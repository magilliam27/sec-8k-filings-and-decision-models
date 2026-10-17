# E5: Does Jev spot new and changed risks better on other companies' 10-Ks?

**Status: graded 15 Oct 04:55Z. Verdict: stop.** Sample drawn 04:40Z. Carded 03:45Z. The owner chose this over the 8-K route on 15 Oct 03:37Z, which lifts the Alphabet-only rule for 10-Ks. The design was fixed before the pulls, except the sample, which was redrawn after them (marked). No label or Jev answer exists yet.

**Why:** on Alphabet, Jev tied word counting three times (E1, E2, E4). But Alphabet adds only about one new risk a year and edits its risks lightly, so it may be an easy case where word counts are already enough. Other companies, such as an airline through COVID or a bank through rate shocks, should add and rewrite risks more often. That gives Jev more room to show an edge, especially on new risks, which the owner weighs most.

**Example:** in its 2020 10-K, Delta would be expected to add pandemic risks it never had before. The question is whether Jev flags those as new more reliably than "no close word match last year".

## Design

| Item | Value |
|---|---|
| Companies | Default: the plan's 10 (JPMorgan, Delta, Exxon, Pfizer, Walmart, Boeing, Microsoft, Coca-Cola, UnitedHealth, Caterpillar). The owner can swap any before the pulls start |
| Years | 10-Ks for fiscal 2013 to 2025, so fiscal 2014 to 2025 each have a prior year, as for Alphabet |
| Data | Data lane pulls and splits each company's Item 1A and runs the five automatic checks on every year. Any company with a check finding is fixed or left out before sampling, and the decision is recorded. One risk file per company, so risks pair only within a company. Walmart (January year end) and Microsoft (June) use a fiscal-year mapping where each 10-K's prior year is the previous filing |
| Question | Unchanged: the frozen five-way question `configs/filings/questions_v2.yaml` (commit 3ec507c), `jev-1.13.0`, each current risk against its closest prior-year risk. Jev is used as is, with no tuning, so the result stays comparable with E2 and E4 |
| Main test: new risks | Ranking quality (AUC) of Jev's "new" probability against the word baseline's 1 minus TF-IDF similarity, for telling new risks from carried-over ones. Jev must win with a 95% bootstrap interval clear of zero, resampling within company and stratum |
| Second test: changed or not | E4 repeated: AUC of 1 minus Jev's "same" probability against the larger word share added or removed. Cuts stay at E4's 0.05 and 0.04 |
| Second Jev question (conditional) | Not used: E6 failed on 15 Oct. The rule was: if E6 passes, `jev_tuning/frozen/changed_noul_v1.yaml` (one yes/no "materially changed?" question, 3 draws, cut 0.5) is also scored on E5 and graded on the changed-or-not test. Decided before E5's labels exist; adds roughly 3 times the calls of the main question |
| Third test: Jev plus words (added 15 Oct 04:20Z) | The tuning thread's frozen rule `jev_tuning/frozen/combo_rank_v1.yaml` (sha256 21fa4a97…48f9, checked by the Lead): average Jev's 1 − "same" rank with the word-share rank, each ranked over every pair E5 scores. Graded on the changed-or-not key: AUC against words alone, 95% interval resampling within company and stratum, must be clear of zero; its gap against Jev alone is reported too. No new Jev calls. Added before any E5 label, pull or Jev answer exists. Prior evidence is exploratory: on the 283 fresh Alphabet risks it scored 0.941 against 0.893 for words (Lead recomputed: interval +0.024 to +0.073), but it was picked from 4 combinations tried on those labels, so that figure is flattered. Because the changed-or-not key now carries two tests, a pass on only one of them is reported as such, not as a general Jev win |
| Also reported | Each test per company; recall and precision for "new" at fixed cuts (Jev: "new" probability 0.5 or more; words: similarity under 0.25, E2's rule) |
| Sample | Drawn by the Lead after the pulls: 30 risks per company (300 in all), oversampling low-similarity risks so new ones get enough rows, with design weights undoing it. **Replaced 15 Oct 04:40Z, after the pulls and before any label or Jev answer, see "Sample as drawn" below** |
| Answer key | Three blind AI reviewers per risk, two questions each: is this a new risk not covered by last year's closest match, and if not, did it materially change? Majority vote. The owner accepted AI reviewers as the key on 15 Oct |
| Cost | Jev on every risk-year pair: roughly 10 times Alphabet's 363 calls, so about 5M input tokens (estimate). Scoring starts with a one-call test per run |

## Sample as drawn (15 Oct 04:40Z, before any label or Jev answer)

**What the pulls showed.** Dataset `ten_companies_10k_risk_factors` r1 (repo commit 2ef33e5, 130 10-Ks, all six checks pass) gives 3,228 current risks in fiscal 2014 to 2025, each paired with its closest prior-year risk by the repo's own pairing (`closest_prior_pairs` at main d5a43e2). These companies carry their risks over almost as steadily as Alphabet: only 76 risks (2.4%) fall under the 0.25 similarity of E2's "new" rule and 144 (4.5%) under 0.5. They are spread unevenly: JPMorgan has 46, Caterpillar 2. A quota of 30 per company would either drop new-risk candidates or waste rows, so the design is:

| Stratum | Risks in population | Drawn | Weight |
|---|---|---|---|
| `near_miss`: similarity under 0.5 | 144 | all 144 | 1 |
| `carried`: similarity 0.5 or more, per company | 3,084 | 156, split across companies in proportion to their size (largest remainder) | each company's count over its draw, about 19.8 |

- **Why 0.5:** almost every new risk should sit below it, and every pair below it is changed by the word score, so the near-miss stratum holds the rows that decide both tests. Pairs above 0.5 carry the risk of missed changes, which the carried stratum measures.
- **Bootstrap cells** are company by stratum, as carded. Caterpillar has no pairs between 0.25 and 0.5, so its near-miss cell has 2 rows.
- **Draw:** seed 297, rows shuffled into a random label order (ids H001 to H300) so the order reveals no stratum. Files: `grading/design.csv` (sealed from the Labelling desk and the Questions lane), `sample_sheet.csv` (blind: company, years, headings and bodies only).
- **Per company** the sample runs from 16 risks (UnitedHealth) to 68 (JPMorgan), so per-company results are descriptive only.
- **Scoring:** the Questions lane scores all 3,228 pairs (the combined rule ranks over every pair), from `population_pairs.csv`, which lists pair ids only (sha256 c91aaf2c…8918).
- **Drawn:** carried rows per company: BA 13, CAT 16, DAL 13, JPM 22, KO 26, MSFT 14, PFE 17, UNH 12, WMT 11, XOM 12. Weights sum to 3,228. 30 of the 300 have identical current and prior text, and one pair of rows shares the same texts. `sample_sheet.csv` sha256 d5aa8a8b…9e45; `grading/design.csv` sha256 6e493e77…0f980.

## Order of work

1. Data lane: pull and check the 10 companies, then publish a dataset version.
2. Lead: draw the 300-risk sample and blind sheet; record the design.
3. In parallel: the Labelling desk runs the AI reviewers; the Questions lane scores Jev. Neither sees the other's output.
4. Lead: grade, recheck and post the verdict.

## Result

**Graded 15 Oct 04:55Z. Verdict: stop on all three tests.** On 10 other companies, Jev does not beat word counting at spotting new risks or changed risks, and adding Jev to word counts does not clear noise either.

Graded by the Lead from `grading/design.csv`, the Labelling desk's key (`labels/sealed/answer_key.csv`: 85 new and 180 changed of 300; 294 and 291 unanimous) and the Questions lane's frozen files (`jev/scores.csv` sha256 7a282cd6…def7, `jev/baselines.csv` ad0db6d4…cbf7, commit f3533b5; 3,223 calls, 4.24M input tokens). The baselines match the Lead's own design values on all 300. Script: the Lead's own; numbers in `grading/summary.json`, each risk in `grading/graded_risks.csv`. Bootstrap: 10,000 draws within company by stratum, seed 300. The AUCs were rechecked with a second method.

| Test (design-weighted AUC) | Jev | Words | Gap | 95% interval | Verdict |
|---|---|---|---|---|---|
| Main: new risk | 0.987 (p_new) | 0.999 (1 − similarity) | −0.012 | −0.030 to +0.001 | Stop |
| Second: changed or not | 0.946 (1 − p_same) | 0.962 (word share) | −0.016 | −0.051 to +0.016 | Stop |
| Third: Jev and words averaged | 0.974 | 0.962 | +0.012 | −0.003 to +0.030 | Stop (it does beat Jev alone: +0.029, +0.009 to +0.052) |

- **New-risk recall at the fixed cuts (what the owner weighs most):** Jev ("new" 0.5 or more) catches 54 of 85 new risks with no false flags; words (similarity under 0.25) catch 70 of 85, with 6 false flags. Jev labels most of the new risks it misses "reworked" (16 of 31) or "broadened" (7), so it reads a replaced risk as a heavily rewritten one. Pfizer has 10 of Jev's 31 misses.
- **Where every new risk sits:** all 85 are among the 144 pairs under 0.5 similarity. None of the 156 carried pairs drawn is new. So in the population, word similarity alone puts every new risk above the 3,084 carried pairs, and that is why words score almost perfectly.
- **Changed or not at the fixed cuts:** balanced accuracy is 89.3% for Jev and 86.2% for words. Jev's precision is 69%, against 57% for words; its recall is 95%, against 100%.

Exploratory, chosen after seeing the labels:

- **Among the 144 hard pairs only (unweighted):** Jev ranks new risks above other low-match risks better than words do (AUC 0.971 vs 0.929). But Jev also scores some of the thousands of carried pairs above new risks it under-calls, and the population-weighted test counts that.
- **Either method says new:** that flags 79 and catches 73 of 85 new risks, 3 more than words alone at no extra false flags.
- **Per company** (descriptive, 16 to 68 risks each): on new risks both are near perfect at most companies, and Jev is clearly worse only at Pfizer (0.93 vs 1.00). Changed or not is mixed: Jev better at Walmart, Pfizer and Boeing; words better at Caterpillar, Coca-Cola and Exxon.

**What it means:** this was the test built to give Jev room, on companies that should change their risks more. They turned out to change almost as little as Alphabet: 2.4% of risks have no close word match. Across five tests and 11 companies, Jev has never beaten word counting with an interval clear of zero.
