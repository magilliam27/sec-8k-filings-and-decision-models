# E8: Is a risk's change bad, good or neutral for the company?

**Status: graded 15 Oct 05:15Z. Verdict: pass.** Carded 05:05Z, before any question was frozen, any label existed or any Jev call was made. The owner asked for it at 04:49Z: "I haven't seen any research from you where we use jev for sentiment on if the change is bad, good or neutral or an even more refined list. I know for a fact word count cannot do that so I'd like us to look into it."

**Why:** E1 to E6 asked whether a risk changed. Word counts can answer that, and they matched Jev every time. Whether a change makes things worse or better for the company is about meaning, which counting changed words cannot see. If Jev has an edge anywhere, it should be here.

**Example:** in fiscal 2020 Delta's fuel-price risk might add a paragraph on the pandemic collapse in demand. That is "worse": the risk got more serious. A Pfizer risk that drops a patent lawsuit because it settled is "better". A risk that only updates dates and figures is "neutral". Word counts would score all three as "changed".

## Design

| Item | Value |
|---|---|
| Risks | The 300 risk pairs of E5's sample (H001 to H300, 10 companies, each current risk beside its closest prior-year risk), with E5's design weights. They are reused because their texts are already pulled and checked, and E5's "changed" and "new" labels let the grade focus on real changes |
| Question 1: direction | One Choice of three. **worse**: the risk became more serious or more likely for the company (a new exposure, a wider scope, an event that actually happened, or a stronger warning). **better**: the risk eased (an exposure removed or shrunk, a matter resolved, or a softer warning). **neutral**: no change in how serious the risk is (rewording, updated figures or dates, reorganised text) |
| Question 2: the finer list | One Choice of five. **materialized**: it now reports that the risk actually happened (an incident, ruling, fine, loss or disruption). **new_exposure**: it adds a new driver, product, market, rule or counterparty. **escalated**: same exposure, but it warns of larger or likelier harm. **eased**: an exposure shrank or was removed, a matter was resolved, or the warning softened. **neutral**: wording, figures, dates or layout only. The first three map to "worse" in Question 1, eased to "better", neutral to "neutral" |
| Wording | The Questions lane may tighten the wording above, and freezes both questions in a committed config before any label is read. `jev-1.13.0`, one answer per pair, option order shuffled per pair, no tuning |
| Answer key | Three blind AI reviewers answer both questions on all 300 items from the texts alone (majority vote; the owner accepted AI reviewers on 15 Oct). Same caveat as before: this measures agreement with Claude reviewers, not with a person |
| Baseline | A finance sentiment dictionary, Loughran-McDonald (the standard one for 10-Ks): the change in the share of its negative words from the prior text to the current one. Also reported: the word balance, the share of words added minus the share removed (a risk that grew). If the Questions lane cannot get the dictionary, the word balance becomes the baseline. That is decided now, before anything is scored |
| Main test | Among risks E5's key calls changed but not new (95 of the 300), design-weighted AUC for telling "worse" from "better or neutral": Jev's probability of worse against the baseline's increase in negative words. Jev must win with a 95% bootstrap interval clear of zero, resampling within company and stratum |
| Also reported | The same for "better" (if the key has at least 10); Jev's and the baseline's weighted accuracy on the three-way question; Jev's agreement with the reviewers on the finer list, against always picking the reviewers' most common answer; whether Jev's two answers agree with each other; results on new risks, which should almost all be "worse"; per company, descriptive only |
| Cost | Two questions on 300 pairs, about 600 calls and 0.8M input tokens. One test call first |
| What a pass leads to | Jev's "worse" score becomes a candidate signal for the returns test (draft E7), next to the free word counts |

## Order of work

1. Questions lane: write and freeze both questions and the baseline, then score the 300 pairs. It never sees labels.
2. Labelling desk: the AI reviewers answer both questions on the 300. It never sees Jev's answers or the baseline.
3. Lead: grade, recheck and report.

## Result

**Graded 15 Oct 05:15Z. Verdict: pass, the first time Jev has beaten a free method.** Among the 95 risks that really changed (E5's key, new risks left out), Jev picks out the changes that made things worse far better than the finance dictionary does, and also better than the fairest free stand-in, "the risk text grew".

Graded by the Lead from E5's `grading/design.csv` and key, this experiment's key (`labels/sealed/answer_key.csv`: direction unanimous on 279 of 300, finer on 266; label set `change_direction_v1.yaml`, a33a7c8) and the Questions lane's frozen files (`configs/filings/questions_v4.yaml` at d7dac91; `jev/scores.csv` sha256 cd3f9f96…fc2; `jev/baselines.csv` b6a15552…bf33; 599 calls, 0.82M input tokens). Script: the Lead's own; numbers in `grading/summary.json`, each risk in `grading/graded_risks.csv`. Bootstrap 10,000 draws within company and stratum, seed 308.

| Telling "worse" from "better or neutral", 95 changed risks (61 worse), design-weighted AUC | Jev | Free method | Gap | 95% interval |
|---|---|---|---|---|
| **Main test:** against the dictionary (rise in the share of negative words) | 0.979 | 0.194 | +0.785 | +0.649 to +0.885 |
| Against the word balance (text added minus text removed) | 0.979 | 0.926 | +0.053 | +0.003 to +0.132 |

**Read the main gap with care.** The registered dictionary score runs backwards: below 0.5, worse than chance. A change that makes a risk worse usually adds plain explanatory text, which dilutes the share of negative words. So the +0.785 gap overstates Jev's edge. The fair comparison is the word balance, also registered, which Jev beats by +0.05 with an interval just clear of zero. Two exploratory checks, chosen after seeing the result, point the same way: the dictionary score flipped scores 0.806, and the change in the count of negative words scores 0.903. Jev beats every free score tried.

**Example (Exxon, fiscal 2020, "Economic conditions"):** the risk now reports the COVID-19 collapse in demand and prices. The reviewers called it worse ("materialized"), and so did Jev (probability 0.9 or more). Its share of negative words fell, so the dictionary scored it as improving.

**Also reported:**

- **Three-way answer, 95 changed risks:** Jev is right on 93% (weighted; balanced accuracy 95%), against 79% for always saying "worse". When Jev says "worse" it is right 49 times out of 51. It misses 12 of the 61 worse risks, calling 6 "better" and 6 "neutral".
- **"Better" is thin:** 9 in the main set, under the card's 10, so it has no separate test. On all 300, Jev's AUC for "better" is 0.962. Jev calls "better" more than the reviewers do (29 against 17 on all 300).
- **Finer list, all 300:** Jev matches the reviewers on 82% (weighted; balanced 65%), against 55% for always saying "neutral". On the 95 changed risks it is 78%, against 53% for always saying "new exposure". Its weak spot is "eased": only 12 of its 45 "eased" calls match, and 20 of those the reviewers call neutral.
- **Jev agrees with itself:** its finer answer maps onto its direction answer for 253 of 300 pairs.
- **New risks:** the reviewers call 81 of 85 worse, and Jev 66.
- **Risks E5 called unchanged (120):** the reviewers still see 28 as worse and 6 as better, and Jev's answers spread almost the same (31 and 5). So "did it change materially?" and "did it get worse?" are different questions.
- **Per company:** the main set is uneven (JPMorgan 38 risks, Caterpillar 1), so these are descriptive only. Jev beats the dictionary in each company with both kinds present, except UnitedHealth, which has 3 risks.

**Caveats:**

1. The key is three Claude reviewers, so this measures Jev against a language model's judgement of meaning. On such a key, word methods start at a disadvantage.
2. The main set is 95 risks.
3. Jev saw the Questions lane's slightly tightened wording of the questions; the reviewers saw the card's. The option sets and definitions are the same.

**What it leads to:** this is the first task where Jev beats every free method. Its "worse" score is a candidate signal for the returns test (draft E7).
