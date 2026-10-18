# 01 Did a risk get worse?

Experiments: [E8](../experiments/E8-change-direction/CARD.md) (graded 15 Oct
2026) and [E9](../experiments/E9-direction-confirm/CARD.md) (graded 16 Oct
2026, 10 fresh companies, frozen in advance). Verdict: **pass, twice.**

## The problem

A company's 10-K lists its risk factors every year. Most carry over with small
edits. Word counts can tell you that a risk's text changed. They cannot tell
you what the change means. A risk that now reports the pandemic's collapse in
demand got worse. A risk that drops a settled lawsuit got better. A risk with
new dates and figures stayed the same. All three look "changed" to a counter.

This recipe asks Jev the question a reader asks: did the change make the risk
worse, better, or neither?

## The question

Frozen in [configs/filings/questions_v4.yaml](../configs/filings/questions_v4.yaml)
before any E8 label existed. Jev sees a state built in code
(`sec8k.jev.pair_state`): the current-year risk factor and its closest
prior-year risk factor by TF-IDF, each as heading and text. The options are
shuffled per pair, so their order cannot steer the answer.

```yaml
version: 4
model: jev-1.13.0
questions:
  direction:
    kind: choice
    instructions: >-
      Compare the current-year risk factor with the prior-year risk factor,
      which is its closest match in last year's filing. From the company's
      point of view, did the risk get worse, get better, or stay as serious as
      it was?
    options:
      worse: >-
        The risk became more serious or more likely for the company: a new
        exposure or a wider scope, an event that actually happened, or a
        stronger warning.
      better: >-
        The risk eased for the company: an exposure was removed or shrank, a
        matter was resolved, or the warning softened.
      neutral: >-
        No change in how serious or likely the risk is: only rewording, updated
        figures or dates, or reorganised text.
```

The same file holds a finer five-way question (`change_kind`: materialized,
new_exposure, escalated, eased, neutral). It was asked too and reported only.

Jev's score for a risk is its probability of "worse".

## The free baseline it must beat

Two free scores, both frozen before any label:

- **Word balance** (the fair one): the share of distinct words added minus the
  share removed. A risk that grew probably got worse. E8 0.926, E9 0.838.
- **Loughran-McDonald negative-word share** (E8's registered main baseline):
  the change in the share of words on the standard finance negative list. It
  runs backwards (E8 0.194, E9 0.433): a risk that gets worse usually gains
  plain explanatory text, which dilutes the share of negative words. So the
  word balance is the comparison to read.
- E9 also fixed in advance the change in the *count* of negative words (0.810).

## How it was graded

- E8: the 300 risk pairs of E5's sample (10 large companies, FY2013 to FY2025),
  with design weights. E9: 300 pairs from 10 companies never used before
  (Apple, Home Depot, Johnson & Johnson, Bank of America, American Airlines,
  Chevron, Procter & Gamble, Honeywell, Verizon, NextEra Energy), drawn with a
  fixed seed after the pulls and before any label.
- Answer key: three blind AI reviewers per item, majority vote, reading the
  same option texts ([recipe 04](04-blind-ai-answer-keys.md)). Label sets:
  `configs/filings/labels/change_direction_v1.yaml` and
  `new_changed_direction_v1.yaml`.
- Main test: among risks the key calls changed but not new, design-weighted
  AUC for telling "worse" from the rest. Jev must win with a 95% bootstrap
  interval clear of zero (10,000 draws within company and stratum).

## Result

| Test | Jev | Free method | Gap (95% interval) |
|---|---|---|---|
| E8, 95 changed risks (61 worse), against word balance | 0.979 | 0.926 | +0.053 (+0.003 to +0.132) |
| E8, against the registered negative-word share | 0.979 | 0.194 | +0.785 (+0.649 to +0.885) |
| **E9, 167 changed risks (132 worse), against word balance (main)** | **0.947** | **0.838** | **+0.109 (+0.024 to +0.199)** |
| E9, against the change in negative-word count | 0.947 | 0.810 | +0.138 (+0.059 to +0.218) |
| E9, "better" against "the text shrank" | 0.977 | 0.843 | +0.134 (+0.051 to +0.228) |

When Jev says "worse" on a changed risk it is right 49 of 51 times (E8) and
121 of 124 times (E9).

**Read with care:**

- The key is three Claude reviewers. This measures agreement with a language
  model's reading of meaning, not with a person, and not with money.
- Jev over-calls change on unchanged risks: in E9 it called 28 of 115
  unchanged risks worse and 10 better. Count its "worse" signal only on risks a
  word rule already flags as changed.
- When this signal was taken to stock returns (E7), it predicted nothing. See
  [recipe 06](06-what-did-not-work.md).

## Code entry point

```bash
# 1. Pair the risks and freeze both baselines. No Jev call.
python -m scripts.data.score_change_direction \
    --data-dir <10-K risk-factor package>/filings \
    --pairs <pairs.csv with a pair_id column> \
    --lm-dictionary Loughran-McDonald_MasterDictionary_1993-2025.csv \
    --output-dir runs/direction/jev

# 2. One test call, then every pair; 3. collect scores.csv.
python -m scripts.data.score_change_direction ... --score --question direction --limit 1
python -m scripts.data.score_change_direction ... --score
python -m scripts.data.score_change_direction ... --collect
```

- Script: [scripts/data/score_change_direction.py](../scripts/data/score_change_direction.py)
- Pairing and baselines: `src/sec8k/change.py` (`closest_prior_pairs`,
  `word_change`, `negative_share`, `option_order`, `score_states`)
- Jev state and answer cache: `src/sec8k/jev.py` (`pair_state`,
  `AnswerCache`, `load_question_set`)
- 10-K parsing: `src/sec8k/risk_factors.py`, checks in `checks.py`
- Pulling the 10-Ks: `scripts/data/export_sec_risk_factors.py`
- E9's grading script: `grading/scripts/e9/grade_e9.py`
- Tests: `tests/test_filings_change.py`
