# E1: Is last year's risk the same risk?

**Status: graded 13 October 2026. Verdict: stop rule triggered, rethink.** Jev got 92.5% of the owner's 200 labels right; the TF-IDF top match got 94.5%.

Card written after the fact (15 October) from the frozen files and the grading output, so it records what was fixed in advance rather than being the advance record itself. Tracker: issue magilliam27/MCI-GRU#289, merged in PR magilliam27/MCI-GRU#290.

## Design (fixed before labels)

| Item | Value |
|---|---|
| Question | Yes/no "Noul": is the prior-year risk factor the same underlying risk as the current one? Changed details still count as the same risk. Frozen in `configs/filings/questions_v1.yaml` |
| Model | `jev-1.13.0`, answer is a probability; yes at 0.5 or above |
| Pairs asked | Every current risk against every prior-year risk: 11,026 pairs, 363 current risks, fiscal 2014 to 2025 |
| Baselines | Heading match (identical headings = same); TF-IDF top match (the most similar prior risk = same) |
| Answer key | The owner, 200 blind labels (89 yes, 111 no), stratified sample of each risk's TF-IDF top-5 shortlist |
| Stop rule | Pilot plan (11 Oct): rethink if Jev can't beat a plain heading match. Grading read it on the whole shortlist (design-weighted) against both baselines, a win needing a 95% bootstrap interval clear of zero |
| Code | Scored at commit 9502de7; grading at 4be0e25 and 6477743 |
| Dataset | v1: `jev_pilot/sec/alphabet_risk_factors.jsonl` (13 10-Ks, FY2013 to FY2025, 392 risks) |
| Cost | About 13.06M input tokens, no failures |

## Result

| Method | 200 labelled pairs | Whole shortlist (weighted) |
|---|---|---|
| Jev | 92.5% | 92.7% |
| TF-IDF top match | 94.5% | 97.8% |
| Heading match | 88.0% | 95.2% |

- **Jev minus heading match, whole shortlist:** −2.5 points (−7.1 to +1.7). Not a win, so the plan's stop rule triggers.
- **Jev minus TF-IDF, whole shortlist:** −5.1 points (−9.5 to −1.3). A clear loss.
- **Ranking:** ROC AUC 0.991 for Jev, 0.994 for TF-IDF similarity.
- **Calibration:** reliable above 0.9 and below 0.4; overconfident from 0.5 to 0.7. Brier score 0.048.
- **Errors:** 14 of Jev's 15 are false "yes" on related but distinct risks (for example "losing key personnel" vs "relying on skilled personnel").

## Data defects in v1

The first was caught before scoring; the other three were found after it. All are fixed with tests in PR magilliam27/MCI-GRU#290. Leaving out the affected labelled pairs does not change the verdict (Jev 92.9%, TF-IDF 95.4% without the 2018 pairs).

| Defect | Years | Labelled pairs touched |
|---|---|---|
| Fake "RISK FACTORS" risk | 2014 to 2019 | 0 (fixed before scoring, 9502de7) |
| Heading split across a page | 2017 | 3 |
| Stray page numbers ("11.") | 2023 to 2025 | 24, cosmetic |
| 808-character heading merged into the previous risk | 2018 | 3 (L007, L161, L174) |

## Follow-ups (exploratory, not pre-registered)

- **E1a, AI reviewers re-judge (13 Oct):** three blind Claude reviewers judged 44 pairs and agreed on all of them. On the owner's 15 disagreements with Jev they sided with Jev on 7 (the owner's "no" meant "it changed") and with the owner on 8. With their labels: TF-IDF 98.0%, Jev 96.0%. Caveat: AI judging AI.
- **E1b, novel risks (13 Oct):** with a "new if even the best match is poor" cut-off, word overlap and Jev flag the same 8 new risks in 12 years. Jev adds 7 flags on risks that kept their name but gained content, some real (2024 first dividend), some false alarms.
- **Not graded:** answer stability (asking twice).

## What it led to

The disputes were mostly about whether a risk had changed, not whether it was the same risk, so the next test (E2) asks how each risk changed.

## Files

- Write-up: `jev_pilot/grading_results.md`
- Numbers: `jev_pilot/risk_pairs/grading/summary.json`, `calibration.csv`, `graded_pairs.csv`
- Reviewer re-judge: `jev_pilot/risk_pairs/grading/judge_1.csv` to `judge_3.csv`, `judges_combined.csv`
- Jev's answers: `jev_pilot/risk_pairs/sealed/scores.csv`, `risk_verdicts.csv`, `answers.jsonl`
