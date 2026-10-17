# E4: Did this risk materially change? (proposed)

**Status: graded 15 October 2026. Verdict: stop. On fresh risks, Jev's "same" probability ranks change no better than word counts (AUC 0.91 vs 0.89, gap interval −0.06 to +0.10).** The E2 hint (0.995 vs 0.947) did not hold up once tested on risks the tuning never saw.

**Why this test:** E2's one promising lead was exploratory. Jev's probability for "same" separated changed from unchanged risks far better than its top answer: AUC 0.98 against 0.87 for word counts. But that was found on the labels it is judged against. E4 tests it on risks nobody has labelled yet. With E4's exact scores on E2's 76 risks, the ranking scores are 0.995 for Jev and 0.947 for word counts, and with both cuts tuned, balanced accuracy is 0.99 against 0.90. So the edge is smaller than the first hint, and all of it was measured on labels the tuning saw.

**Example from E2:** the 2024 buyback risk added the first dividend, and Jev gave "same" a 0% probability, so it counts as changed (right). The 2022 intellectual property risk only added "financial condition and". Jev's top pick was "broadened", a miss, but it still gave "same" 46%, so under a cut at 20% it counts as unchanged (right).

## Design

| Item | Value |
|---|---|
| Question | None new. Uses Jev's E2 answers, already paid for all 363 Alphabet risks: the probability it gave "same" (`jev_pilot/change/sealed/answers.jsonl`, `jev-1.13.0`, question frozen at 3ec507c) |
| Risks | 100 of the 283 Alphabet risks outside E2's 80, drawn by the Lead on 15 Oct (seed 289): all 7 the word rule calls changed, plus 93 of the 276 it calls the same (weight 2.97 each). So the test is mostly about whether Jev finds changes the word rule misses. These strata use E2's five-way word rule (0.20 shares), not E4's 0.04 cut, which calls 209 of 363 changed. Blind sheet: `sample_sheet.csv`; design: `grading/design.csv` (Lead only). None of the four 2018 defect pairs is in it |
| Answer key | Three blind AI reviewers answer one question: did this risk materially change from last year's closest match? Same guide wording as E2 ("same" = lightly reworded or updated figures). Majority vote. The owner accepted AI reviewers as the key on 15 Oct |
| Baseline | Word counts from E2, frozen at 3ec507c: score = the larger of the share of words added and the share removed |
| Main test | Ranking quality (AUC, design-weighted) of 1 minus Jev's "same" probability against the baseline score. Jev must win with a 95% bootstrap interval clear of zero |
| Also reported | Balanced accuracy at fixed cuts, each picked the same way: the cut with the best balanced accuracy on E2's 76 labels (15 Oct). Jev: changed when its "same" probability is under 0.05. Word counts: changed when the larger share is 0.04 or more. Tuning only Jev's cut would favour it (a point the Questions lane raised) |
| Cost | No Jev spend. Labelling desk time for the AI reviewers |

**The owner's framing (15 Oct 03:26Z):** "calibrating Jev's confidence may be key to performance". E4 tests one form of that: whether Jev's "same" probability, rather than its top pick, is the useful signal.

## Known limits

- The key is three Claude reviewers, and Jev is also a language model, so they may share a view of what counts as material. The owner's spot-check line was stricter (7 of 20 changed vs the reviewers' 14), though the owner later judged it rushed and the AI's line better.
- Alphabet only. A pass means the signal is worth testing on more companies, not that it predicts anything about returns.

## Result

Graded by the Lead on 15 Oct from `grading/design.csv`, the Labelling desk's key (`labels/sealed/answer_key.csv`: 35 changed, 65 not; 92 of 100 unanimous) and the Questions lane's frozen scores (`jev/scores.csv`, commit dc586f7, cuts 0.05 and 0.04). Script: the Lead's own, independent of the repo code; numbers in `grading/summary.json`, each risk in `grading/graded_risks.csv`.

| Design-weighted | Jev | Word counts |
|---|---|---|
| Ranking quality, AUC (the main test) | 0.906 | 0.887 |
| Balanced accuracy at the fixed cuts | 78.8% | 78.8% |
| Recall: changed risks caught | 64% | 87% |
| Precision: flags that were real changes | 83% | 58% |
| Right out of 100 | 83 | 77 |

- **Main test:** Jev minus word counts is +0.019 AUC, with a 95% interval of −0.063 to +0.101 (10,000 draws resampled within strata). Not clear of zero, so it fails.
- **Different styles, same score:** Jev flags fewer risks and is right more often when it does. Word counts catch more changes but raise more false alarms. On balanced accuracy they tie to the third decimal.
- **A miss by Jev:** the 2025 legal risk now says the Search case reached a final judgment with data-sharing remedies. The reviewers called that changed; Jev gave "same" 32%, above the cut, so it stayed unchanged.
- **Why the hint faded:** the E2 numbers were measured on the same labels used to spot the lead. This is the usual gap between a pattern found after looking and one tested fresh.

**Verdict:** across three tests (E1, E2, E4), Jev does not beat word counting at reading how Alphabet's risk factors change. The plan's Stage A gate is not met.
