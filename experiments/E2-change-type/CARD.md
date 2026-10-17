# E2: How did this risk change since last year?

**Status: graded 15 October 2026. Verdict: rethink.** Jev's balanced accuracy is 81% against the word rule's 67%, but the 95% interval on the gap (−7 to +25 points) includes zero. Its broadened precision is half the rule's, so the novelty reading doesn't rescue it. Graded on the AI reviewers' key by the owner's override (below). Run by the thread "Alphabet filings first real run".

Card written 15 October from the frozen files. The question, baseline and exclusions below were all committed or recorded on 13 October, before any label or Jev answer was read.

**Example:** in 2024 Alphabet's buyback risk gained a mention of its first dividend. The right answer is "broadened". The test asks whether Jev or a word-counting rule gets answers like that right more often.

## Design (fixed before labels)

| Item | Value |
|---|---|
| Question | Five-way Choice: same, broadened, narrowed, reworked or new. Frozen in `configs/filings/questions_v2.yaml` at commit 3ec507c. Option order shuffled per pair |
| Model | `jev-1.13.0`, one pick per risk |
| Pairs asked | Each of the 363 current risks (FY2014 to FY2025) beside its closest prior-year risk by TF-IDF |
| Baseline | Word overlap, no model: "new" if similarity is under 0.25; otherwise the share of distinct words added and removed, each against 0.20 (both: reworked; added only: broadened; removed only: narrowed; neither: same). Frozen at 3ec507c |
| Sample | 80 risks, stratified by the baseline's answer so rare kinds get rows; design weights undo the oversampling |
| Answer key | Three blind AI labellers on all 80 (majority vote), plus the owner's blind labels on 20 of them. The owner answers same risk? added? dropped?, and code maps that to the five types |
| Excluded | C025, C052, C058, C060: they touch the 2018 heading defect. Recorded 13 Oct 22:50Z, before any label or answer was read (`jev_pilot/change/sealed/excluded_rows.json`). 76 risks are graded |
| Stop rule | Jev must beat the baseline on design-weighted balanced accuracy (the average of each kind's recall), with a 95% bootstrap interval clear of zero |
| Also reported | Recall and precision for each kind, with "new" and "broadened" read first |
| Dataset | v2: `jev_pilot/sec_v2/filings/alphabet_risk_factors.jsonl` (commit 3ec507c). Fixes the fake title risk, the 2017 split heading and the page numbers; the 2018 heading defect is still in it |
| Cost | About 0.5M input tokens, 363 calls. First paid call runs with `--limit 1` |

**Bullet glyphs in v2, checked 15 Oct.** v2 drops list bullets ("•") in FY2013 to FY2019 but keeps them from FY2020 (6 FY2020 risks have them, their FY2019 priors don't). This cannot move the baseline: its word shares count only letter runs, and the TF-IDF pairing ignores punctuation. Comparing v2 with the Data lane's r1, every changed risk outside FY2018 has the same word sequence; the FY2018 changes are the known heading defect, already excluded. Jev and the AI labellers do see the glyphs, a formatting-only difference. No action.

## Rules added by the Lead before the owner's labels exist

Written 15 October, before the owner's 20 labels arrived and before anyone read the AI labels against them.

1. **When the AI key is trusted.** Compare the owner's 20 with the AI majority on the five types. With at least 15 of 20 matching, grade on the AI key, with the owner's label replacing the AI's on those 20, and report the grade on the owner's 20 alone beside it. With fewer than 15, the AI key is not trusted and no verdict is given; the mismatches show which definitions need tightening first. With only 20 rows this check is coarse: 15 of 20 is consistent with true agreement anywhere from about 51% to 91%. The owner answers on a different form from the AI labellers (three yes/no questions mapped to the five types, while the AI picked the five types directly, and its "reworked" also covers "emphasis changed"), so some mismatches may come from the form. Every mismatch counts toward the bar; the form-driven ones are reported separately as description only, since sorting them after the fact could bend the rule.
2. **How novelty is read.** The stop rule decides pass or rethink. If Jev loses on balanced accuracy but beats the baseline on recall for "new" and "broadened" without losing precision, the verdict is "rethink, with a lead": not a pass, but grounds for a novelty-only test on more companies. The card reports how many labelled rows each kind has, since "new" may have only a handful.
3. **Checking the numbers.** The Lead recomputes every number in the verdict from the grading output before it goes on the ledger.

## Open before grading

- [x] The owner's 20 spot-check labels (returned 15 Oct; trust bar not met, see Result)
- [ ] The owner's yes or no on also asking Jev three yes/no questions (same risk? added? dropped?). A yes means writing and committing them before the owner's labels come back. That would be a second Jev arm, E2b, graded on this same key and reported beside E2
- [ ] Grading mechanics: the grader reads labels from the `change` column of `change_sheet.csv` and does not drop the four excluded rows itself. The owning thread will write the merged key, with the exclusion applied, into a copy of the sheet (confirmed 15 Oct)

## Result

### Grade (15 Oct, 76 risks, AI reviewers' key)

| | Jev | Word rule |
|---|---|---|
| Balanced accuracy, design-weighted (the stop rule) | **81.0%** | 66.6% |
| Plain accuracy, design-weighted | 70.6% | 75.4% |
| Right out of the 76 labelled risks | 51 | 54 |
| New: recall / precision | 86% / 100% (6 of 7) | 100% / 100% (7 of 7) |
| Broadened: recall / precision | 94% / 46% | 37% / 90% |

- **Stop rule:** Jev minus the rule is +14.4 points, with a 95% interval of −7.0 to +24.9. It isn't clear of zero, so the verdict is rethink.
- **Novelty reading (rule 2):** not met. Jev catches fewer new risks than the rule, and it buys its broadened recall by flagging many unchanged risks as broadened: precision falls from 90% to 46%. So the verdict is plain "rethink", not "rethink, with a lead".
- **Where Jev goes wrong:** it calls change where the key sees none. 10 of the 22 unchanged risks got broadened, narrowed or reworked. Where it is right, it catches changes that touch few words, all 5 that the rule called "same".
- **On the owner's 20 alone:** Jev 59.5%, the rule 89.5% balanced accuracy (gap −30 points, interval −41 to +1). The owner's stricter line on what counts as material punishes Jev's over-calling harder. That rests on only 20 risks. The owner later said (15 Oct 03:26Z) that the stricter line was "mostly wrong as I was rushing" and that the AI did better, so read this figure as a check on the key, not as a second verdict.
- **Exploratory, chosen after seeing the labels:** Jev's probability for "same" ranks changed against unchanged risks with an AUC of 0.98, against 0.87 for the word shares. Every risk the key calls changed scored 0.17 or less. A cut on that probability might fix the over-calling, but the cut would be picked on these labels, so it needs fresh labels to test.
- **Cost:** 362 Jev calls, about 0.5M input tokens, `jev-1.13.0`, no failures.

**Lead recheck (15 Oct):** recomputed from `e2_graded/grading/graded_risks.csv` independently of the repo code. The key equals the AI majority in `sealed/ai_labels.csv`, and the four excluded risks are absent. Jev's answers equal `sealed/choices.csv`, and the design weights match `label_design.csv`. Balanced and plain accuracy and the per-kind recall and precision match `summary.json` exactly. A separate stratified bootstrap gives the interval as −6.7 to +25.1, the same conclusion.

Write-up: `jev_pilot/change/grading_results.md`.

### Spot check (15 Oct)

**Spot check, 15 Oct: the owner and the AI majority agree on 11 of 20.** The bar was 15, so by rule 1 the AI key is not trusted and Jev is not graded. The Lead recomputed the 11 and the mapping of the owner's answers from `sealed/spot_check_comparison.csv`.

| Kind of mismatch | Rows | What happened |
|---|---|---|
| What counts as material | S07, S08, S16, S17, S20 | The owner answered nothing added and nothing dropped; all three reviewers named a specific change (S16: the first dividend added to the buyback risk) |
| Blank cell read as "no" | S02, S09, S12 | The owner described one direction and left the other blank. Even if all three flipped, agreement would be 14 of 20 |
| New vs broadened | S11 | 2017 Tax Act: the owner called it the same tax risk with a big addition; two of three reviewers called it new |

- **Agreed:** all 3 new risks (S01, S15, S19), both clear broadenings (S10, S18), and 6 unchanged risks.
- **The pattern:** the reviewers call 14 of the 20 changed, the owner 7. They disagree on how big a change has to be, not on which risks are new.
- **One caveat on the 11:** the owner wrote free text in the added and dropped columns rather than yes or no. The owning thread fixed how to read it (blank, "Nothing" or a change called cosmetic = no; a described change = yes) after seeing the owner's answers but before comparing them with the AI labels. Raw text: `sealed/mac_spot_labels.csv`.

**What it means for the test:** for novelty, the owner and the reviewers agree on all three new risks. For "how did it change", the five types depend on a materiality line that isn't yet shared, so neither key can grade Jev yet. Any re-run with a tightened definition and a new key gets its own id and card, written before any relabelling.

Write-up: `jev_pilot/change/spot_check_result.md`.

**The owner's override, 15 Oct 03:16Z.** The owner decided to grade on the AI reviewers' labels despite missing the bar. In the owner's words: "I think the reviewers did a better job, I as a human am trying to read two large paragraphs and compare them perfectly and I do think a language model is good for this the three different reviewers seem to broadly align so I am thinking we go with AI answers." This was decided before any Jev answer existed, so it cannot have been bent toward a Jev result. It replaces rule 1: the key is the AI majority on all 80, the owner's 20 do not replace the AI's labels, and the grade on the owner's 20 alone is still reported beside it.

**How to read the verdict this produces:** it measures whether Jev matches three Claude reviewers, not a person. Model judging model can share blind spots. The reviewers' materiality line is looser than the owner's (14 of 20 changed vs 7), so the key holds more broadened, narrowed and reworked risks than the owner would give.

## Files

- Blind sheet and guide: `jev_pilot/change/change_sheet.csv`, `label_guide.md`, `spot_check_sheet.csv`
- Sealed until grading: `jev_pilot/change/sealed/` (AI majority labels `ai_labels.csv`, design weights, pairs and baseline answers, spot-check key `spot_check_key.csv` mapping S01 to S20 onto C ids)
- Run: `python -m scripts.data.score_risk_changes --risk-factors <v2 jsonl> --output-dir jev_pilot/change [--score | --grade]`
