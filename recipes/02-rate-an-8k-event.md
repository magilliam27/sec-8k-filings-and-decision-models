# 02 Rate an 8-K event

Experiment: [E10](../experiments/E10-8k-events/CARD.md), graded 16 Oct 2026.
Verdict: **pass**, with a large caveat about the answer key.

## The problem

An 8-K is a company's report of a material event: a deal, a restructuring, an
officer leaving, an auditor change. The item code says what kind of event it
is. It does not say how bad or good it is. A planned retirement with a named
successor and a CEO resigning effective immediately share item 5.02 and use
similar words. A shareholder would rate them very differently.

This recipe asks Jev to rate each event on a five-point scale, with a written
rubric for each point, and turns its probabilities into a score.

## The question

Frozen in [configs/filings/questions_v5.yaml](../configs/filings/questions_v5.yaml)
(commit 3a1be7f in the source repository) before any E10 label existed. Jev
reads a state built in code (`sec8k.events.event_state`) from facts known
at filing time only: the company name, the item codes with their titles, the
company's revenue from its latest 10-K filed before the 8-K, the item codes of
its other 8-Ks in the previous 90 days, and the event text (item sections plus
press-release exhibit 99.1, cut at 20,000 characters). Options are shuffled per
event.

```yaml
version: 5
model: jev-1.13.0
questions:
  rating:
    kind: choice
    instructions: >-
      This 8-K reports an event at the company. From a shareholder's point of
      view, how good or bad is the event for the company? Judge the event the
      text describes, using the context: the item codes, the company's prior
      annual revenue for scale, and its other 8-Ks in the previous 90 days.
    options:
      very_bad: >-
        An event that threatens the business or the trust in it, such as a
        restatement, a bankruptcy, a delisting notice, or a CEO or CFO leaving
        immediately with no successor or in connection with an investigation.
      bad: >-
        A clearly negative event, such as a restructuring with job cuts, an
        impairment, a lost or ended major contract, or an unplanned senior
        departure.
      neutral: >-
        A routine event, such as a planned retirement with a named successor, a
        director change, a compensation plan, or a routine financing agreement.
      good: >-
        A clearly positive event, such as a major new contract or a deal on
        favourable terms.
      very_good: >-
        A transformative and favourable event, such as a large acquisition or
        sale at a strong price.
```

The file also holds a `size` question (the amount against prior revenue). E10
asked it and reported it only. E11 did not ask it.

Two scores come from the probabilities (`sec8k.events`):

- **Rating score** = sum of each option's probability times its weight, −2
  (very bad) to +2 (very good).
- **Bad score** = P(bad) + P(very bad).

## The free baseline it must beat

A reader who knows the item code and counts words, frozen before any label:

1. The item code's lean: negative-leaning items (1.02, 1.03, 2.05, 2.06, 3.01,
   4.02) above auditor changes (4.01) above the rest.
2. Within a lean, the Loughran-McDonald net tone: negative minus positive
   words, as a share of all words.

`baseline_badness = lean + (1 + net_tone) / 3`, so tone can never lift an
event past a stronger lean.

## How it was graded

- Events: every qualifying original 8-K of E5's 10 companies (JPMorgan, Delta,
  Exxon, Pfizer, Walmart, Boeing, Microsoft, Coca-Cola, UnitedHealth,
  Caterpillar), 2013 to 2025: 436 events, 37 of them bad or very bad in the
  key. Earnings releases (2.02) and general news (7.01, 8.01) were left out.
- Answer key: three blind AI reviewers on all 436, reading the same rubric word
  for word (label set `configs/filings/labels/event_rating_v1.yaml`, prompt
  `reviewer_events_v1.md`). Unanimous on 414 of 436.
- Main test: AUC for telling "bad or very bad" from the rest, Jev's bad score
  against the baseline's order. Jev must win with a 95% interval clear of zero
  (10,000 bootstrap draws within company and item group, seed 310).

## Result

| Test, all 436 events (AUC) | Jev | Free method | Gap (95% interval) |
|---|---|---|---|
| **Main: bad or very bad (37) against the rest** | **0.986** | **0.759** | **+0.227 (+0.128 to +0.323)** |
| Officer changes alone (333 events, 21 bad), against net tone | 0.986 | 0.630 | +0.356 (+0.214 to +0.502) |
| Good or very good (26), against the baseline reversed | 0.996 | 0.434 | +0.563 (+0.480 to +0.643) |

Jev's five-way answer matches the key on 91%, against 86% for always
"neutral". When Jev says "bad" it is right 24 times of 29; it calls 13 of the
37 bad events neutral. It never answered "very bad" in E10.

**Read with care:** the key and Jev read the same text with the same rubric,
and the key is three Claude reviewers. A word count cannot see a rubric, so a
large gap is expected. This shows Jev reads events sensibly. It does not show
the score is worth anything. That is the job of
[recipe 03](03-test-a-signal-on-returns.md), where the same question was put
to 26,962 8-Ks and checked against stock prices.

## Code entry point

```bash
# Pull the 8-Ks (free; SEC wants a real User-Agent)
python -m scripts.data.export_sec_8k_events --user-agent "Your Name you@example.com" \
    --package-root data/8k_events --cache-dir data/sec_cache --filer jpm \
    --manifest-output data/8k_events.r1.json

# Freeze the baseline (no Jev), then score and collect
python -m scripts.data.score_8k_events --events data/8k_events/8k_events.jsonl \
    --lm-dictionary Loughran-McDonald_MasterDictionary_1993-2025.csv \
    --output-dir runs/e10/jev
python -m scripts.data.score_8k_events ... --score --question rating --limit 1
python -m scripts.data.score_8k_events ... --score
python -m scripts.data.score_8k_events ... --collect
```

- Scoring script: [scripts/data/score_8k_events.py](../scripts/data/score_8k_events.py)
  (`--workers` for calls in flight, `--sample` for a listed subset)
- Event state, scores and baseline: `src/sec8k/events.py`
- 8-K parsing (item sections, press release, revenue context):
  `src/sec8k/eight_k.py`; companies in `filers.py`
- E10's frozen baselines: [results/E10-8k-events/](../results/E10-8k-events/)
  (Jev's per-filing ratings are not published)
- E10's grading script: `grading/scripts/e10/grade_e10.py` (needs the sealed
  answer key, which is not published here)
- Tests: `tests/test_filings_events.py`, `tests/test_filings_eight_k.py`
