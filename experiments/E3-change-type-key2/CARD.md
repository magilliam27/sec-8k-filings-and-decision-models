# E3: How did this risk change? (second answer key)

**Status: withdrawn before any work (15 Oct 03:16Z).** The owner chose to grade E2 on the AI labels instead (see the E2 card), so this second key was never built. Nothing below was run. Kept as a record.

Card written 15 October 03:15Z, before the owner's rulings, the AI relabel or the fresh spot check existed.

## What changes from E2

| Item | E2 | E3 |
|---|---|---|
| Definition of "material" | The five option texts only | The owner's rulings on E2's 9 spot-check disagreements, written into the labelling guide (sheet: `jev_pilot/change/adjudication_sheet.csv`) |
| AI labels | 3 reviewers on all 80, five-way guide | 3 reviewers relabel all 80 with the written definition |
| The owner's blind check | 20 risks (S01 to S20) | A fresh 20, none from E2's first 20, since those shaped the definition |

## Kept from E2, unchanged

- Question `configs/filings/questions_v2.yaml` and the word-overlap baseline, both frozen at commit 3ec507c
- Dataset v2, the same 80 sampled risks and design weights, and the same four exclusions (C025, C052, C058, C060)
- The stop rule, the trust bar (at least 15 of the fresh 20 match the AI majority), the novelty reading and the Lead's recheck: rules 1 to 3 on the E2 card
- All 76 non-excluded risks are graded on the new key, as in E2. E2's first 20 shaped the definition, so they can't test the key, but they stay in the graded sample. Jev never saw them, so they are still a fair test of Jev

## Open before grading

- [ ] The owner's rulings on the 9 disagreements, and the written definition, committed to the label guide before the AI relabel starts
- [ ] AI relabel of all 80 (sealed)
- [ ] The owner's fresh blind 20, compared with the AI majority
- [ ] Only then does Jev score the 363 risks (about 0.5M tokens)

## Result

Not graded yet.
