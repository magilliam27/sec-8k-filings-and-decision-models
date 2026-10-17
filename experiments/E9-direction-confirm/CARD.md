# E9: Does Jev's edge at spotting changes for the worse hold on 10 fresh companies?

**Status: graded 16 Oct 03:55Z. Verdict: pass, E8 confirmed.** Carded 02:20Z. The owner chose "Confirm, prep returns" on 16 Oct 02:13Z. No pull, label or Jev answer exists yet, so everything below is fixed before any of them, except the sample's exact draw (see Sample).

**Why:** E8 passed on 95 changed risks from 10 companies. Its edge over the fairest free score ("the text got longer") was +0.053, with an interval of +0.003 to +0.132, just clear of zero. A fresh sample, frozen in advance, shows whether that edge is real before Jev's "worse" score feeds the returns test (E7).

**Example:** if Chevron's 2020 commodity-price risk adds the pandemic's collapse in oil demand, the right answer is "worse". The test asks whether Jev ranks changes like that above the rest better than "the text got longer" does.

## Design

| Item | Value |
|---|---|
| Companies | 10 not used before, one per sector where possible: Apple, Home Depot, Johnson & Johnson, Bank of America, American Airlines, Chevron, Procter & Gamble, Honeywell, Verizon and NextEra Energy. 10-Ks for fiscal 2013 to 2025. The owner can swap any before the pulls |
| Data | The Data lane pulls them with all six automatic checks, as for E5. A company with a check finding is fixed or left out before sampling, and the decision is recorded |
| Pairs | Each current risk (fiscal 2014 to 2025) beside its closest prior-year risk, the repo's `closest_prior_pairs`, per company |
| Sample | 300 pairs, drawn by the Lead after the pulls, seed 309. Per company: 25 from the "candidate" stratum (word score 0.04 or more, which holds every low-similarity pair) and 5 from the rest, with design weights undoing it. If a company has fewer than 25 candidates, the spare rows go to other companies' candidates in proportion to size. Bootstrap cells are company by stratum |
| Question | Unchanged: the direction question in `configs/filings/questions_v4.yaml` (frozen at d7dac91), `jev-1.13.0`, one answer per pair, option order shuffled per pair. The finer list is asked too, as in E8, and reported only |
| Answer key | Three fresh blind AI reviewers per item, majority vote, answering four questions: E5's `new_risk` and `changed` (label set `new_changed_v1.yaml`) and E8's `direction` and `finer` (`change_direction_v1.yaml`), word for word |
| Main test | Among the risks the key calls changed but not new: design-weighted AUC for telling "worse" from "better or neutral", Jev's probability of worse against the word balance (share of words added minus share removed). Jev must win with a 95% bootstrap interval clear of zero (10,000 draws, within company and stratum) |
| Also reported | Against the change in the count of Loughran-McDonald negative words (E8's exploratory score, now fixed in advance) and the registered share version; Jev's three-way accuracy against always picking the commonest answer; when Jev says "worse", how often it is right; the finer list; per company, descriptive only |
| Cost | Two questions on 300 pairs: about 600 calls, 0.8M input tokens. EDGAR pulls are free |

## Sample as drawn (16 Oct 03:40Z, before any label or Jev answer)

- **Data:** `e9_ten_companies_10k_risk_factors` r1 (PR magilliam27/MCI-GRU#300, issue magilliam27/MCI-GRU#304), 127 10-Ks and 3,164 risks, all six checks pass. Johnson & Johnson starts at fiscal 2016 (its 2013–2015 Item 1A points to an exhibit), so its pairs run from 2017. That makes 2,927 pairs, 1,352 of them candidates.
- **Draw** as carded: 25 candidates and 5 others per company, seed 309, ids J001 to J300 in random order. Every company had at least 25 candidates, so nothing was reallocated. Weights run from 2.5 (Chevron candidates) to 103 (NextEra others) and sum to 2,927. 24 items have identical texts; 15 have similarity under 0.25.
- **Files:** `sample_sheet.csv` (blind, sha256 367e5d6a…), `pairs.csv` (pair ids only, for Jev, 3c64aa87…), `population_pairs.csv` (73bea54a…), and `grading/design.csv` (Lead only, d97f39e0…).

**Key arrived, recorded before any Jev answer (16 Oct 03:40Z).** The Labelling desk asked all four questions together (label set `new_changed_direction_v1.yaml`, 19de6d4, the two frozen sets copied unchanged). J227 has no majority on direction (one reviewer each for worse, better and neutral), so it is left out of every direction result. The Lead decided this before any Jev answer existed. The main set is the remaining 167 changed-not-new risks. Unlike E8, almost none of them is neutral: asked "changed?" in the same sitting, the reviewers called every unchanged risk neutral. So the main test here mostly separates worse from better.

## Order of work

1. Data lane: pull and check the 10 companies, then publish a dataset version.
2. Lead: draw the sample and blind sheet, and record the design.
3. In parallel: the Labelling desk runs the AI reviewers, and the Questions lane scores Jev and freezes the baselines. Neither sees the other's output.
4. Lead: grade, recheck and report.

## Result

**Graded 16 Oct 03:55Z. Verdict: pass. Jev's edge at spotting changes for the worse holds on 10 fresh companies, and it is wider than in E8.**

Graded by the Lead from `grading/design.csv`, the Labelling desk's key (`labels/sealed/answer_key.csv`; J227 left out as recorded above) and the Questions lane's frozen files (`questions_v4` unchanged; `jev/scores.csv` sha256 8e392214…36e4; `jev/baselines.csv` e3f58f6c…a801, written from commit 07e842c before any Jev call; 600 calls, 0.81M input tokens). The pairing reproduces `population_pairs.csv`. Script: the Lead's own; numbers in `grading/summary.json`, each risk in `grading/graded_risks.csv`. Bootstrap 10,000 draws within company and stratum, seed 309. AUCs rechecked with a second method (scikit-learn, weighted).

| Telling "worse" from the rest, 167 changed risks (132 worse, 34 better, 1 neutral), design-weighted AUC | Jev | Free method | Gap | 95% interval |
|---|---|---|---|---|
| **Main test:** against the word balance (text added minus text removed) | 0.947 | 0.838 | +0.109 | +0.024 to +0.199 |
| Against the change in the count of negative words (Loughran-McDonald) | 0.947 | 0.810 | +0.138 | +0.059 to +0.218 |
| Against the change in the share of negative words (E8's registered score) | 0.947 | 0.433 | +0.515 | +0.386 to +0.640 |

The share score runs backwards again (under 0.5), as in E8, so the word balance is the fair comparison, and Jev clears it.

**Example (Bank of America, fiscal 2016, Brexit):** last year's broad non-US risk mentioned a possible Brexit vote; this year the vote had happened and the pound had fallen, and the risk became a shorter stand-alone item. All three reviewers called it worse ("materialized"), and so did Jev (0.98). The text shrank (word balance −0.28) and lost 27 negative words, so both free scores read it as easing.

**Also reported:**

- **"Better":** 34 in the main set, enough for its own test this time. Jev 0.977 against 0.843 for "the text shrank", gap +0.134 (+0.051 to +0.228).
- **All 299 risks:** "worse" against the rest, Jev 0.961 against 0.810 for the word balance (+0.151, +0.089 to +0.213).
- **Three-way answer, 167 changed risks:** Jev is right on 90% (weighted), against 79% for always saying "worse". When Jev says "worse" it is right 121 times out of 124. It misses 11 of the 132 worse risks (5 called better, 6 neutral). On all 299 it is right on 88% (balanced 88%), against 62% for always "neutral".
- **Jev still over-calls change on unchanged risks:** of the 115 risks the reviewers call unchanged (all neutral), Jev calls 28 worse and 10 better. Across all 299, 137 of Jev's 168 "worse" calls are right. In the returns test this matters: Jev's "worse" share should be counted only over risks the word rule flags as changed.
- **Finer list, all 299:** Jev matches the reviewers on 83% (weighted; balanced 77%), against 62% for always "neutral". Its answers map onto its direction answers for 258 of 300.
- **New risks:** all 17 are worse to the reviewers; Jev says worse for 16.
- **Per company:** descriptive only (12 to 21 risks each, most nearly all worse). Jev beats or ties the word balance in 7 of 10; it trails slightly at Honeywell (0.84 vs 0.87), Johnson & Johnson and Verizon (0.98–0.99 vs 1.00). Exploratory, after seeing the result: comparing only risks within the same company, Jev still leads, 0.936 against 0.807.

**Caveats:**

1. The key is three Claude reviewers, so this measures Jev against a language model's judgement of meaning.
2. Unlike E8, the main set is almost all worse against better (one neutral), because the reviewers called every unchanged risk neutral when asked "changed?" in the same sitting. So E9 confirms Jev on worse-versus-better; E8 is the evidence for worse-versus-neutral.

**What it leads to:** Jev's "worse" share, counted over risks the word rule flags as changed, joins the returns test (E7) as a candidate signal beside the word-only ones. That is the spend the owner set aside on 16 Oct 02:13Z (about $8), once the S&P 500 10-Ks are pulled.
