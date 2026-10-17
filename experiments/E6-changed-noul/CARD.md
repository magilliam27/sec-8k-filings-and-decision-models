# E6: Does a plain "did it materially change?" question beat word counts?

**Status: graded 15 October 2026. Verdict: stop. The reworded question ranks change no better than word counts on 183 fresh risks (AUC 0.917 vs 0.884, gap interval −0.02 to +0.09), and no better than Jev's original five-way answer (0.925).** The tuning gain did not carry to fresh risks.

**Why:** Jev can't be fine-tuned, but how we ask matters. On E2's and E4's used labels, the tuning thread tried about 30 variants. The best was a single yes/no question in place of E2's five-way pick: AUC 0.946 against 0.887 for word counts on E4's risks. That is best-of-30 on labels already seen, so it is only a lead until tested on fresh risks.

**Example:** the 2025 legal risk added that the Search case reached a final judgment. The five-way question let Jev's "same" probability sit at 32%, a miss. The question here asks directly whether it materially changed.

## Design

| Item | Value |
|---|---|
| Question | One Noul: "Compared with `prior_year_risk_factor`, did `current_risk_factor` materially change?", with criteria. Yes: "Material scope was added or dropped, such as a driver, exposure, product, jurisdiction, event or consequence, or last year's text describes a different risk." No: "The same risk, only lightly reworded or with updated figures or examples; nothing material was added or removed." Frozen by the tuning thread at `jev_tuning/frozen/changed_noul_v1.yaml` (sha256 a6ef0cd9…, written ~03:52Z, before any E6 label), and committed unchanged by the Questions lane before scoring |
| Model and draws | `jev-1.13.0`; three independent draws per risk, averaged, because identical re-asks give slightly different probabilities |
| Risks | All 183 remaining Alphabet risks (v2) outside E2's 80 and E4's 100. Every one is a risk E2's word rule calls "same", which is where word counts are weakest. No sampling, so no weights. Blind sheet: `sample_sheet.csv` |
| Answer key | Three blind AI reviewers, same instructions as E4 (`E4-changed-or-not/labels/reviewers/instructions/`), changed yes/no, majority |
| Baseline | Word counts as in E4: the larger share of words added or removed, cut at 0.04 |
| Main test | Ranking quality (AUC) of the averaged probability against the word score. Jev must win with a 95% bootstrap interval clear of zero |
| Also reported | Balanced accuracy at the fixed cuts (Jev 0.5, words 0.04); calibration; E4's 1 minus "same" probability on the same risks, as a third column |
| Cost | About 550 calls, roughly 0.8M input tokens, one test call first |

## Known limits

- The question's criteria use the same wording as the reviewers' guide, and both are language models, so they may agree for shared reasons.
- Scored as committed in e3d7d2b (`configs/filings/questions_v3.yaml`, id `materially_changed`). Unlike the tuning run, the question is asked alone and under a different name, so its probabilities may shift slightly from the tuning numbers. That doesn't affect the fresh-label test.
- If it passes, it joins E5 as a second Jev question, frozen before E5's labels exist.

## Result

Graded by the Lead on 15 Oct from the Labelling desk's key (`labels/sealed/answer_key.csv`: 43 of 183 changed, 166 unanimous) and the Questions lane's scores (`jev/scores.csv`, commits e3d7d2b and 9abfa3b; 537 calls, 664,896 input tokens). Script: the Lead's own; numbers in `grading/summary.json`, each risk in `grading/graded_risks.csv`.

| 183 fresh risks | Yes/no question (E6) | Five-way answer (E2's question) | Word counts |
|---|---|---|---|
| Ranking quality, AUC (main test) | 0.917 | 0.925 | 0.884 |
| Balanced accuracy at fixed cuts | 81.5% | 83.5% | 79.5% |
| Recall: changed risks caught | 84% | | 95% |
| Precision: flags that were real | 55% | | 45% |
| Right out of 183 | 147 | | 130 |

- **Main test:** the yes/no question minus word counts is +0.032 AUC, with a 95% interval of −0.024 to +0.090. That isn't clear of zero, so it fails.
- **Against Jev's original question:** −0.008 (−0.029 to +0.011). Rewording added nothing on fresh risks. The tuning run's edge (0.946 against 0.906 on E4) came from picking the best of 30 variants on labels it had already seen.
- **Calibration:** the probabilities are roughly calibrated (ECE 0.15) and the three draws barely differ (median spread 0.01).
- **Independence:** 4 pairs repeat another pair's text word for word, so 179 of the 183 asks are distinct.

**Exploratory, all fresh Alphabet risks together.** E4 and E6 between them cover all 283 risks outside E2, so they can be pooled with no weights. Jev's five-way "same" probability against word counts: AUC 0.914 vs 0.893, gap +0.02, interval −0.02 to +0.07. That's a small, consistent edge that never clears noise.
