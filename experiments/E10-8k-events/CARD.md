# E10: How good or bad is an 8-K event for shareholders?

**Status: graded 16 Oct 04:35Z. Verdict: pass.** Carded 16 Oct 03:35Z (sample changed 03:58Z, see below), before any 8-K is pulled, any question is frozen, any label exists or any Jev call is made.** The owner chose this idea on 16 Oct 03:29Z ("proceed with 8k idea") from the six sentiment ideas posted at 03:21Z.

**Why:** E8 showed that Jev beats free methods at judging what a change means, not at spotting that text changed. 8-K events are the purest case: the item code says what kind of event happened, but only the wording says how bad it is. Jev's choice probabilities turn its answer into a score, so every event can be ranked, and that ranking is what a later returns test needs.

**Example:** two 8-Ks under Item 5.02. "Jane Smith will retire on June 30 after 22 years; John Lee, our COO, will succeed her" should score neutral. "Jane Smith resigned effective immediately; the board appointed an interim CEO and has engaged a search firm" should score bad. Both share the same item code and similar words.

## Design

| Item | Value |
|---|---|
| Companies | E5's 10 (JPMorgan, Delta, Exxon, Pfizer, Walmart, Boeing, Microsoft, Coca-Cola, UnitedHealth, Caterpillar), filings dated 2013 to 2025 |
| Events | 8-Ks (with 8-K/A amendments left out) carrying any of these items: 1.01 material agreement, 1.02 agreement ended, 1.03 bankruptcy, 2.01 acquisition or sale completed, 2.05 restructuring, 2.06 impairment, 3.01 delisting notice, 4.01 auditor change, 4.02 restatement, 5.02 officer or director change. Earnings releases (2.02) and general news (7.01, 8.01) are left out of this first test |
| Text | The 8-K's item sections, plus press-release exhibit 99.1 when there is one, cut at 20,000 characters, with truncation recorded. The Data lane pulls and checks them, with the EDGAR acceptance time in true UTC |
| Context Jev sees | Computed by code, all known at filing time: company name; the item codes; the company's revenue from its latest 10-K filed before the 8-K; and the item codes of its other 8-Ks in the previous 90 days. Nothing dated after the filing |
| Question 1: rating | One Choice of five, from the shareholder's point of view, with concrete criteria per option (the rubric). **very bad**: an event that threatens the business or the trust in it, such as a restatement, bankruptcy, delisting notice, or a CEO or CFO leaving immediately with no successor or tied to an investigation. **bad**: clearly negative, such as a restructuring with job cuts, an impairment, a lost or ended major contract, or an unplanned senior departure. **neutral**: routine, such as a planned retirement with a named successor, a director change, a compensation plan, or a routine financing agreement. **good**: clearly positive, such as a major new contract or a deal on favourable terms. **very good**: transformative and favourable, such as a large acquisition or sale at a strong price. The Questions lane may tighten the wording and freezes it before any label |
| Question 2: size | One Choice: the amount involved is under 1% of annual revenue, 1% to 5%, over 5%, or no amount stated. Uses the revenue in the context. Reported only |
| Score | Rating score = sum of each option's probability times its weight (−2, −1, 0, +1, +2). "Bad score" = probability of bad plus very bad |
| Sample | 300 events drawn by the Lead after the pull, stratified by item group: officer changes (5.02), deals (1.01, 2.01), negative-leaning items (1.02, 1.03, 2.05, 2.06, 3.01, 4.02) and auditor changes (4.01). Events with several items go to the most negative-leaning group. Rare groups are taken whole; design weights undo the oversampling. Bootstrap cells are company by item group |
| Answer key | Three blind AI reviewers answer both questions from the same text and context, majority vote (the owner accepted AI reviewers on 15 Oct). For the rating, ties of three different answers take the middle one |
| Baseline | A reader who knows the item code and counts words. First the item code's lean, fixed now: negative-leaning items (1.02, 1.03, 2.05, 2.06, 3.01, 4.02) above auditor changes (4.01) above the rest. Then, within a lean, the Loughran-McDonald net tone (negative minus positive words, as a share of all words). It ranks events from worst to best with no labels |
| Main test | Design-weighted AUC for telling "bad or very bad" from the rest: Jev's bad score against the baseline's order. Jev must win with a 95% bootstrap interval clear of zero (10,000 draws within company and item group) |
| Also reported | The same for "good or very good"; officer changes alone (the motivating case), Jev against net tone; Jev's five-way accuracy against always picking the commonest answer; how often a "very bad" from Jev is right; size agreement; per company, descriptive only |
| Cost | Two questions on about 300 events, under 1M input tokens for the test. Scoring every pulled event for the returns work later is a separate, small cost |
| What a pass leads to | Jev's rating score on every event joins the returns test (E7): do events Jev scores as bad see worse returns over the following days and weeks than the item code alone predicts? |

## Sample change (16 Oct 03:58Z, before any 8-K was parsed, any label existed or any Jev call was made)

The Data lane's count from EDGAR's filing index: about 436 qualifying 8-Ks. Officer changes 338, material agreements 81, negative-leaning items about 17 (restructuring 7, agreement ended 5, impairment 4, delisting 1), deals completed 6, and no bankruptcy, auditor change or restatement. A 300-event stratified sample would be nearly the whole set, so:

- **Every qualifying event is used**, with weight 1; no sampling. Groups for the bootstrap stay company by item group: officer changes, deals, negative-leaning. The auditor group is empty and dropped.
- **Minimum for a verdict:** the key must hold at least 20 events rated bad or very bad. With fewer, the main test is reported but carries no verdict, and the next step is the same frozen questions on E9's 10 companies' 8-Ks, under a new id.
- Cost rises to about 870 calls, still about 1.3M input tokens.

## Events as published (16 Oct 04:20Z, before any label or Jev answer)

- **Data:** `e10_8k_events` r1 (manifest `data/e10_8k_events.r1.json`; code bc04cc9, PR magilliam27/MCI-GRU#300, issue magilliam27/MCI-GRU#308; `8k_events.jsonl` sha256 4ef25543…0a581). 436 events, no check findings; 24 texts cut at 20,000 characters (3 inside the item text); 219 with a press release. Events filed in January or February can only use the previous year's 10-K for revenue (58 events).
- **Groups:** officer changes 333 (item 5.02 with no other listed item), deals 86 (1.01 or 2.01), negative-leaning 17. No auditor change, restatement or bankruptcy occurred, so those parts of the rubric and baseline are never used. Bootstrap cells are company by group; the negative cells hold 1 to 4 events.
- **Ids:** K001 to K436 in random order (seed 310), so the order reveals no company or group. Files: `sample_sheet.csv` (blind: company, item codes with titles, prior revenue, prior-90-day items and text, exactly as Jev's state builds them; sha256 fe13b88b…e6a9), `events.csv` (event ids only, for Jev; 4660e48f…da80) and `grading/design.csv` (Lead only; c663706e…6fa).
- **Reviewers' wording:** the option texts frozen in `configs/filings/questions_v5.yaml` (3a1be7f), word for word, so reviewers and Jev read the same rubric.

**Jev scored, 16 Oct 04:20Z, before any label was read:** all 436 events, both questions (872 calls, 1.71M input tokens, commit 5b62432, questions_v5 at 3a1be7f). `jev/scores.csv` sha256 c71e864f…d6ee; `jev/baselines.csv` a122bf9b…3fc0, frozen before any call.

## Order of work

1. Data lane: pull and check the 8-Ks for the 10 companies, with the context fields, and publish a dataset version.
2. Lead: draw the sample and blind sheet, and record the design.
3. In parallel: the Questions lane freezes both questions and the baseline, then scores Jev; the Labelling desk runs the AI reviewers. Neither sees the other's output.
4. Lead: grade, recheck and report.

## Result

**Graded 16 Oct 04:35Z. Verdict: pass. Jev picks out the 8-K events that are bad for shareholders far better than the item code plus a word count.**

Graded by the Lead from `grading/design.csv`, the Labelling desk's key (`labels/sealed/answer_key.csv`, sha256 35023d07…50e3; label set `event_rating_v1.yaml`, eb10700, wording copied from questions_v5; rating unanimous on 414 of 436, every disagreement one step apart, so the middle-answer rule never fired) and the Questions lane's frozen files (above). The key holds 37 bad or very bad events, over the minimum of 20. Script: the Lead's own; numbers in `grading/summary.json`, each event in `grading/graded_events.csv`. Bootstrap 10,000 draws within company and item group, seed 310.

| Test, all 436 events (AUC) | Jev | Free method | Gap | 95% interval |
|---|---|---|---|---|
| **Main:** bad or very bad (37) against the rest; Jev's bad score against item code then net tone | 0.986 | 0.759 | +0.227 | +0.128 to +0.323 |
| Officer changes alone (333 events, 21 bad); Jev against net tone | 0.986 | 0.630 | +0.356 | +0.214 to +0.502 |
| Good or very good (26) against the rest; Jev's good score against the baseline reversed | 0.996 | 0.434 | +0.563 | +0.480 to +0.643 |

**Example (Boeing, 23 December 2019):** the CEO resigned effective immediately, the board saying a change was needed to restore confidence with regulators; an interim CEO was named. The reviewers called it bad, and so did Jev (0.96). The item code (5.02) and its word count put it below 82% of all events.

**A miss (Boeing, 25 March 2024):** the CEO stepping down with no successor named, the chair leaving and a unit head replaced. The reviewers called it bad; Jev called it neutral (bad score 0.27).

**Also reported:**

- **Jev's rating score** (its full five-way average) ranks bad events at 0.944, also well above the baseline.
- **The item code alone** ranks bad events at 0.656: 12 of the 17 negative-leaning items are bad, but most bad events (21 of 37) are officer changes, which the item code cannot separate.
- **Five-way answer:** Jev matches the reviewers on 91%, against 86% for always "neutral"; on bad, neutral or good it matches on 94%. When Jev says bad it is right 24 times of 29; it calls 13 of the 37 bad events neutral. Jev never answers "very bad", and the reviewers used it once (UnitedHealth's CEO leaving immediately with guidance suspended in 2025; Jev said bad). Jev says "very good" for 21 events where the reviewers mostly say "good" (12).
- **Size:** Jev matches the reviewers' size bracket on 96%, against 58% for always "no amount stated".
- **Per company and group:** descriptive only. Jev ranks bad events higher than the baseline in eight companies and ties at Exxon (one bad event); Walmart has none. By group: officer changes 0.99 against 0.63, deals 0.94 against 0.91, negative-leaning 1.00 against 0.83.

**Caveats:**

1. **The key and Jev read the same text with the same rubric**, and the key is three Claude reviewers. This mostly measures whether Jev applies the rubric as a language model would. Word counts cannot see a rubric, so a large gap is expected; it shows Jev reads the events sensibly, not that its score predicts anything.
2. **The good-news test is lopsided:** the baseline was built to find bad events, and reversing it scores below chance.
3. **Hindsight:** the reviewers know how many of these stories ended (Boeing's 2019 crisis, for one). They were told to judge from the sheet alone, but it cannot be ruled out.
4. **Ten large companies, 436 events, 37 bad.** Bankruptcies, restatements and auditor changes never occurred, so the rubric's worst cases are untested.

**What it leads to:** Jev's 8-K rating is ready to be tried in the returns test (E7): do events Jev rates bad see worse returns in the following days and weeks than the item code alone predicts? That test, not this one, says whether the score is worth anything. Scoring every 8-K for the S&P 500 would cost little, as the 10-K scoring does.
