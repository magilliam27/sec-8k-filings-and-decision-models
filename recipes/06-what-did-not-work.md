# 06 What did not work

Experiments E1 to E7. Every one was frozen in advance and graded against a free
method. None of them is a win for Jev.

## The first problem: did a 10-K risk change?

A 10-K's risk factors carry over from year to year with edits. The first idea
was that Jev would spot new and changed risks better than counting words. It
did not. Over five graded tests on 11 companies, a simple word rule matched or
beat Jev every time.

The free baselines were:

- **TF-IDF top match**: pair each risk with the most similar prior-year risk.
- **Word rule**: a risk is new if its closest prior risk has similarity under
  0.25; changed if the share of distinct words added or removed is 0.04 or more
  (`sec8k.change.baseline_change`, `word_score`).

## The results

| Id | Question to Jev | Data | Jev | Free method | Gap (95% interval) | Verdict |
|---|---|---|---|---|---|---|
| E1 | Is last year's risk the same risk? (yes/no, `questions_v1`) | Alphabet, 200 hand labels | 92.5% accuracy | TF-IDF top match 94.5% | Jev − TF-IDF −5.1 points (−9.5 to −1.3), weighted | Rethink |
| E2 | How did this risk change? (5 options, `questions_v2`) | Alphabet, 76 risks, AI key | 81.0% balanced accuracy | Word rule 66.6% | +14.4 points (−7.0 to +24.9) | Rethink |
| E3 | Same as E2 with a second key | | | | | Withdrawn before any work |
| E4 | Did it materially change? (E2's "same" probability) | 100 fresh Alphabet risks | AUC 0.906 | Word counts 0.887 | +0.019 (−0.063 to +0.101) | Stop |
| E5 | New risk? Changed? (E2's question) | 10 companies, 300 of 3,228 risks | New 0.987; changed 0.946 | New 0.999; changed 0.962 | New −0.012 (−0.030 to +0.001); changed −0.016 (−0.051 to +0.016) | Stop |
| E6 | Did it materially change? yes/no, 3 draws (`questions_v3`) | 183 fresh Alphabet risks | AUC 0.917 | Word counts 0.884 | +0.032 (−0.024 to +0.090) | Stop |

Notes:

- **E1:** 14 of Jev's 15 errors were false "yes" on related but distinct risks
  ("losing key personnel" against "relying on skilled personnel").
- **E2:** Jev's balanced accuracy looked better, but it over-called change: 10
  of 22 unchanged risks got broadened, narrowed or reworked. Its precision on
  "broadened" was 46% against the rule's 90%.
- **E4:** a lead from E2 (Jev's "same" probability ranked change at AUC 0.98)
  was found on the labels it was judged against. On fresh risks it faded.
- **E5:** the test built to give Jev room, on companies that should rewrite
  their risks more. They did not: only 2.4% of risks had no close word match.
  Words caught 70 of 85 new risks at their fixed cut; Jev caught 54. Averaging
  Jev and words gave +0.012 (−0.003 to +0.030), still not clear.
- **E6:** the tuning run's best wording, chosen from about 30 on seen labels,
  added nothing on fresh risks (−0.008 against Jev's original question).

**Why:** spotting that text changed is what word counts are built for. Jev's
edge, where it has one, is in judging what a change *means*
([recipe 01](01-did-a-risk-get-worse.md)).

## The Lazy Prices replication (E7)

Cohen, Malloy and Nguyen ("Lazy Prices", Journal of Finance, 2020) found that
firms whose 10-K text changes a lot from the year before go on to
underperform. E7 checked this on S&P 500 members, 2013 to 2026, and added
Jev's share of risks that got worse.

- 752 companies, 6,871 member 10-Ks with all three return windows. Point-in-time
  membership; delisted companies included.
- Returns from the first close after acceptance, over 21, 63 and 126 trading
  days, minus SPY.
- Rank correlation within calendar-quarter groups (43 groups), averaged, 95%
  interval from 10,000 draws of whole groups, seed 307.
- Jev scored 80,596 flagged risks.

| Signal, 63 trading days | Rank correlation (95% interval) | Filings |
|---|---|---|
| **Main: whole risk section changed** | **+0.004 (−0.034 to +0.044)** | 6,650 |
| Share of new risks | +0.010 (−0.025 to +0.045) | 6,141 |
| Share of changed risks | −0.004 (−0.045 to +0.036) | 6,141 |
| Jev's "worse" share | −0.021 (−0.067 to +0.023) | 6,141 |
| **Jev minus changed share** | **−0.016 (−0.034 to +0.002)** | 6,141 |

- Lazy Prices predicts a negative correlation. Here it is +0.004. The top
  fifth of changers did 0.5 points *better* than the bottom fifth over 3
  months (−1.0 to +2.0).
- Every signal at every window spans zero. By year, correlations swing between
  about −0.10 and +0.11 with no steady sign.
- Why it may differ from the paper: they studied all US stocks, 1995 to 2014,
  with the effect strongest in small firms and before publication. This sample
  is only S&P 500 stocks, after publication. It does not say the effect never
  existed. It says it is not in this sample.

## What it led to

The failures pointed to the 8-K: news that is fresh when filed, measured over
the days just after. That is where Jev's reading finally showed up in prices
([recipe 03](03-test-a-signal-on-returns.md)).

## Code entry point

- 10-K pulls: `scripts/data/export_sec_risk_factors.py`,
  `scripts/data/export_sec_member_10k.py`, `scripts/data/build_sp500_members.py`
- E1: `scripts/data/score_risk_factor_pairs.py`, graded by
  `scripts/data/grade_risk_factor_pairs.py` (`src/sec8k/grading.py`)
- E2: `scripts/data/score_risk_changes.py`; E4: `score_risk_change_flags.py`;
  E5: `score_company_risk_changes.py`; E6: `score_risk_change_noul.py`
- E7: `scripts/data/score_e7_signals.py` (`src/sec8k/report_signals.py`),
  graded by `grading/scripts/e7/grade_e7.py`
- Cards: `experiments/E1-same-risk/` to `experiments/E7-returns/`
