# 03 Test a signal on returns

Experiments: [E11](../experiments/E11-8k-returns/CARD.md) (8-K rating, graded
17 Oct 2026, **pass**) and [E7](../experiments/E7-returns/CARD.md) (10-K risk
changes, graded 16 Oct 2026, **fail**).

## The problem

An AI answer key can show that Jev reads a filing sensibly. It cannot show
that the reading is worth anything. For that you need an outcome nobody can
argue with: what the stock did next. This recipe fixes the whole test before
any score or return exists, then joins prices only at grading.

## The question

E11 reuses E10's rating question unchanged:
[configs/filings/questions_v5.yaml](../configs/filings/questions_v5.yaml),
`rating` only, `jev-1.13.0`. The full text is in
[recipe 02](02-rate-an-8k-event.md). The signal is the **rating score**
(probability-weighted −2 to +2).

E7 used E8's `direction` question from
[questions_v4.yaml](../configs/filings/questions_v4.yaml) (see
[recipe 01](01-did-a-risk-get-worse.md)), summed into each 10-K's share of
risks that got worse.

## The free baseline it must beat

- **E11:** E10's baseline. For returns, its "good" score is minus the
  Loughran-McDonald net tone. Because every comparison is made inside one item
  group, the item code itself is already controlled for.
- **E7:** the Lazy Prices signal (1 minus the cosine similarity of the whole
  risk section to last year's) as the main test, and the share of risks a word
  rule flags as changed as Jev's comparison.

## How it was graded (E11)

Frozen on the card on 16 Oct 12:45Z, before any member 8-K was published, any
Jev score existed or any return was looked at.

| Item | Rule |
|---|---|
| Events | Every original 8-K of an S&P 500 member (point-in-time membership, 753 companies) carrying items 1.01, 1.02, 1.03, 2.01, 2.05, 2.06, 3.01, 4.01, 4.02 or 5.02, from 2013 |
| Left out | 8-Ks that also list 2.02 (earnings); events with no price at day −1; events whose 10-day window had not ended; same-company same-day duplicates (rule does not look at Jev) |
| Event time | Acceptance time from the filing's index page, in US Eastern. **Day 0** is the first trading day whose 16:00 close comes after acceptance. The **day −1 close** is the last close before acceptance, so it is never after the news was public |
| Outcome | Return from the day −1 close to the day +k close (EODHD adjusted closes) minus SPY's. A stock that stops trading keeps its return to its last close and earns SPY after that |
| Cells | Item group (negative-leaning, auditor, deals, officer) by calendar year; a cell under 30 events joins the next year |
| Statistic | Spearman rank correlation inside each cell, averaged with weights by events per cell. 95% interval from 10,000 bootstrap draws of whole cells within item group, seed 311 |
| Pass | Main: Jev's rating against the 2-day return, interval clear of zero. Jev against words: the difference in correlations, interval clear of zero |
| Model memory | Jev's training cut-off is not published. Events after 10 Sep 2026 (the model's release) are reported apart |

Blind wall: the scoring lane never saw a price. The data lane published events
without prices. Prices were joined only at grading, after the Jev scores and
baselines were frozen with their hashes on the card.

## Result (E11)

26,962 events in 44 cells. Officer changes 16,263, deals 8,953,
negative-leaning 1,678, auditor changes 68. Jev cost 55.2M input tokens,
about $2.32.

| Average rank correlation, within item group and year | Jev's rating | Word tone | Jev minus word tone |
|---|---|---|---|
| **Main: 2 days (day −1 close to day +1)** | **+0.025 (+0.015 to +0.034)** | −0.015 (−0.028 to −0.004) | **+0.040 (+0.026 to +0.055)** |
| Day 0 alone | +0.039 (+0.028 to +0.049) | −0.012 | +0.051 (+0.036 to +0.068) |
| 5 days | +0.022 (+0.009 to +0.034) | −0.010 | +0.032 (+0.015 to +0.047) |
| 10 days (second headline) | +0.010 (−0.000 to +0.021) | +0.001 | +0.009 (−0.008 to +0.025) |
| Drift, day 0 close to day +10 | −0.007 (−0.018 to +0.005) | +0.004 | −0.010 |

- Within each cell, the fifth Jev rates best beat the fifth it rates worst by
  0.29 points over 2 days (+0.16 to +0.42).
- Positive in 13 of 14 years (2022: −0.017).
- Officer changes Jev calls bad: −0.68% over 2 days (−1.02 to −0.37), 774
  events.
- The 107 events after 10 Sep 2026: +0.034, same direction, too few to test.
- The item code alone, across groups within years: −0.005 (−0.017 to +0.006).

**What it means:** Jev's rating carries real, small information about the
immediate price reaction that item codes and word counts miss. A correlation
of 0.025 explains well under 1% of 2-day returns. It is over by the first
close after the filing, so it is not a trade at the close. Its natural use is
as a fast event feature.

## The failed version (E7)

Same idea on 10-K risk sections: 6,871 S&P 500 10-Ks, 2013 to 2026, returns
over 21, 63 and 126 trading days from the first close after filing, quarter
groups, seed 307.

| Signal, 63 trading days | Rank correlation (95% interval) |
|---|---|
| Main: whole risk section changed (Lazy Prices) | +0.004 (−0.034 to +0.044) |
| Share of new risks | +0.010 (−0.025 to +0.045) |
| Share of changed risks | −0.004 (−0.045 to +0.036) |
| Jev's "worse" share | −0.021 (−0.067 to +0.023) |
| Jev minus changed share | −0.016 (−0.034 to +0.002) |

Every signal at every window spans zero. Lazy Prices predicts a negative
correlation; here it is +0.004. 10-Ks change slowly and are heavily read;
8-Ks are fresh news. That is the difference between E7 and E11.

## Code entry point

- E11 grading chain (the Lead's scripts, statistics unchanged):
  `grading/scripts/e11/events_e11.py` → `join_e11.py` → `grade_e11.py save`.
  Set `FILINGS` to a folder laid out like the research tree (`data/`,
  `experiments/`) and `VERIFY_OUT` to a scratch folder. See
  [grading/VERIFY.md](../grading/VERIFY.md).
- E11's frozen inputs and outputs: [results/E11-8k-returns/](../results/E11-8k-returns/)
  (`events.csv`, `baselines.csv`, `joins.csv`, `summary.json`; Jev's
  per-filing `scores.csv` is not published;
  `summary_v1.json` is the first run before a correction to a descriptive
  table, see the card)
- Pulling members' 8-Ks: `scripts/data/build_sp500_members.py`, then
  `scripts/data/export_sec_member_8k.py`
- Prices: `scripts/data/pull_eodhd_prices.py` (needs `EODHD_API_KEY`)
- E7 signals and Jev scoring: `scripts/data/score_e7_signals.py`,
  `src/jev_filings/report_signals.py`; grading `grading/scripts/e7/grade_e7.py`
- An independent recheck of E11 with separately written code:
  [docs/independent_recheck.md](../docs/independent_recheck.md)
