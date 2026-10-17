# E11: Does Jev's 8-K event rating predict stock returns in the days after filing?

**Status: graded 17 Oct 03:40Z. Verdict: pass. Jev's rating lines up with the 2-day return beyond the item code, and beats word counting; the effect is small and is over by the first close after filing.** Design frozen 16 Oct 12:45Z, before any member 8-K was published, any Jev score existed or any return was looked at. The owner chose "8-K returns test" on the Lead's decision card (16 Oct 12:30Z): pull S&P 500 8-Ks (free), score them with E10's frozen question (about $1 approved), and test returns over 1 to 10 days against the item code alone.

**Why:** E7 found that 10-K risk sections, read by words or by Jev, say nothing about the next 1 to 6 months. 10-Ks change slowly and are heavily read. 8-Ks are fresh news: E10 showed Jev tells a bad 8-K from a routine one far better than the item code plus a word count (0.986 against 0.759). This test asks whether that reading shows up in prices.

**Example:** two officer-change 8-Ks (item 5.02). Boeing, 23 December 2019: the CEO resigned effective immediately and an interim CEO was named; Jev rated it bad. A planned retirement with a named successor gets neutral. The item code is the same for both. If Jev's rating carries price information, the first should be followed by a worse return than the second, more often than chance.

## Frozen design

| Item | Value |
|---|---|
| Events | Every event in the Data lane's member 8-K dataset (issue #311, `scripts/data/export_sec_member_8k.py`, E10's contract): original 8-Ks carrying items 1.01, 1.02, 1.03, 2.01, 2.05, 2.06, 3.01, 4.01, 4.02 or 5.02, accepted on a day the company was an S&P 500 member (member table v2, 753 companies), from 2013. Events the Data lane leaves out for a failed check are recorded with their reason, per year |
| Left out of the test | 8-Ks that also list item 2.02 (earnings), since the earnings news would swamp the event. Events whose 10-day window has not ended by the last price date. Events with no usable price at day −1 (recorded by company and year) |
| Same company, same day 0 | Several qualifying 8-Ks from one company with the same day 0 share one return, so only one is kept: the one in the most negative-leaning item group, then the earliest acceptance. The rule does not look at any Jev score |
| Jev's score | The rating question of `configs/filings/questions_v5.yaml` at 3a1be7f, unchanged, `jev-1.13.0`, the same state E10 used (text plus code-added company name, item codes, prior 10-K revenue, prior-90-day item codes). **Rating score** = probability-weighted −2 to +2. Bad score = P(bad) + P(very bad), reported. The size question is not asked |
| Baseline | E10's, frozen: item lean (negative-leaning items above auditor change above the rest), then within a lean the Loughran-McDonald net tone (negative minus positive words, share of all words). For correlation with returns its "good" score is minus net tone |
| Item groups | As E10: negative-leaning (1.02, 1.03, 2.05, 2.06, 3.01, 4.02), auditor (4.01), deals (1.01, 2.01), officer (5.02 only). An 8-K with several items goes to its most negative-leaning group |
| Event time | `accepted_utc` from the filing's index page, converted to US Eastern. **Day 0** is the first trading day whose 16:00 close comes after acceptance. **Day −1 close** is the last close before acceptance, so it is never after the news was public. Events whose index-page time could not be read use the listed time and are flagged |
| Outcome | Return from the day −1 close to the day +k close, using EODHD adjusted closes, minus SPY's return over the same days. A stock that stops trading inside the window keeps its return to its last close and earns SPY after that (as E7) |
| Windows | Day 0 alone (1 day); **day 0 to +1 (2 days, main)**; day 0 to +4 (5 days); day 0 to +9 (10 days). Drift a buyer could capture, from the day 0 close: to day +5 and to day +10 |
| Cells | Item group by calendar year of acceptance. A cell with under 30 events joins the next year of the same group (the last year joins the one before) |
| Statistic | Within each cell, the Spearman rank correlation between the score and the return. The result is the average over cells, weighted by events per cell. 95% interval from 10,000 bootstrap draws of whole cells, drawn within item group, seed 311 |
| **Main test** | Jev's rating score against the 2-day return. Because each cell holds one item group, this is the information Jev adds **beyond the item code**. Pass: the average correlation is positive with its interval clear of zero |
| **Jev against words** | On the same events and cells, Jev's correlation minus the baseline's (minus net tone). Jev beats word counting only if the difference is positive with its interval clear of zero |
| Model memory check | Jev may have read later news about these companies. The Questions lane finds jev-1.13.0's training cut-off in TypeSafe's docs before scoring. Events accepted after it are reported separately. If the cut-off is found and the after-cut-off main correlation is zero or negative, a pass is downgraded to **unclear** |
| Also reported | Every window; bad score as the signal; the item code alone (mean 2-day return by item group, and the item lean's pooled correlation within years), to show what the code itself carries; mean 2-day return by Jev's most likely answer, with intervals; top-fifth against bottom-fifth gap per cell; officer changes alone; events with a press release attached against those without (an 8-K often follows the news by up to four business days, so the price may already have moved); by year; events by item and by year; if the Data lane supplies it, the main test leaving out events with a separate earnings 8-K within 5 calendar days |
| What a pass leads to | A drift check on later events and a candidate event feature for MCI-GRU or a standalone screen. A fail is reported as a fail |
| Cost | Rating question only, one call per event. The owner approved about $1. Before any call, the Questions lane estimates input tokens from the published events; if the estimate passes $1.50, the Lead asks the owner first. Prices: the existing `data/e7_prices/` (to 2026-10-15), plus any symbol the 8-K events need that it lacks |

**Known limits, accepted now:** SPY adjustment only, with no industry, size or value controls; S&P 500 members only; 8-Ks often follow a press release, so some news is priced before day −1; Jev sees the company name and may remember how a story ended.

## Added at the owner's ask (17 Oct 03:15Z, before any Jev score or return exists)

The owner asked for good news and general patterns as well as bad news, and for the 10-day return as a second headline beside the 2-day one. None of this changes the main test or the verdict rule; it is reported alongside.

- **10-day result as a second headline:** the same test on the return from day −1 to day +9, Jev against words, reported next to the 2-day result.
- **Good news:** the same test with Jev's good score (P(good) + P(very good)), so a high score should be followed by a better return.
- **Patterns after similar events (descriptive):** the average market-adjusted return path, day 0 to day +10, (a) for each item code, (b) for each of Jev's five answers, and (c) for each item group split by Jev's answer, each with its number of events and a 95% interval from resampling whole months. These describe what typically happens after each kind of event; they are not tests.

## Facts found before any score or return (16 Oct 12:36Z)

- **Event count:** the Data lane's pull holds 28,551 events before checks and left-outs. At E10's rate of about 2,000 input tokens per rating call, scoring all of them is about 57M tokens, roughly $2.40, over the $1.50 line, so the Lead asks the owner before any call.
- **Jev's training cut-off is not published.** The Questions lane searched TypeSafe's full docs export, the Models page and the Jev 1.13 page: none gives a cut-off. The only bound is that `jev-latest` (which points at jev-1.13.0) was released on 10 Sep 2026, so the cut-off is on or before that date. By the card's rule the cut-off is "not found", so no downgrade applies. Events accepted after 10 Sep 2026 are still reported separately, but few will have a complete 10-day window, so the model-memory risk stays a known limit rather than a tested one.
- **Earnings overlap field supplied:** each event carries `nearby_202_listed_utc` (Data lane, PR #300, 18e9bfb), so the earnings robustness check in "Also reported" will run.

## Events as published and joined (16 Oct 14:26Z, counts only, no return computed)

- **Data:** `member_8k_events` r1 (manifest `data/member_8k_events.r1.json` sha256 f4029460…3bb2; `member_8k_events.jsonl` 04172c9b…931f; code e502416, PR #300, issue #311). 28,253 events from 752 companies, accepted 1 Jan 2013 to 15 Oct 2026; 232 left out by checks (0.8%), listed in `member_8k_left_out.csv`. Every event's acceptance time comes from its index page. Apache 2013 to early 2021 is missing (it filed as a subsidiary).
- **Joins (Lead's script, counts only):** 28,063 events join to a price series with a close on day −1 and a complete 10-day window. Left out: 93 with no price at day −1 (Fox 33, Howmet/Alcoa 31, Ingersoll-Rand/Trane 21, 8 others), 63 whose window has not ended, 34 with no price series (old DuPont 18, Covidien 15, Baker Hughes 1). These are the same companies E7 could not price.
- **Rules applied:** 848 joined events also list 2.02 and are left out; 253 same-company, same-day-0 duplicates are dropped by the group rule.
- **Test set: 26,962 events.** Officer changes 16,263, deals 8,953, negative-leaning 1,678, auditor changes 68. From 1,371 (2026, part year) to 2,153 (2015) a year. Ids only in `events.csv` (sha256 f885c806…0b3b), for the Questions lane; joins per event in `grading/joins.csv` (685fd126…b02).
- **Cost at E10's rate:** 26,962 rating calls at about 2,000 input tokens is about 54M tokens, roughly $2.30. Waiting on the owner's answer (decision card, 12:36Z) before any call.
- **Baseline frozen (16 Oct 14:29Z, Questions lane, commit 631301f, before any Jev call):** `jev/baselines.csv` sha256 9a6296a9…1bdda, E10's rule unchanged. Exact estimate for the rating question: 48.2M input tokens by characters, about 56M after E10's 16% under-count, roughly $2.35.
- **The owner approved about $2.40** on the Lead's decision card (17 Oct 03:05Z); the Questions lane was told to score.
- **Jev scored, 17 Oct 03:17Z, before any return was computed:** all 26,962 events, rating question only, no failed call (55.2M input tokens, about $2.32; commit 631301f, questions_v5 rating unchanged from 3a1be7f). `jev/scores.csv` sha256 eb56f1c8…d05b; `jev/answers/rating.jsonl` 8b3456b9…3bfc. Jev's answers: neutral 22,463, very good 2,141, bad 1,456, good 823, very bad 79.

## Blind wall for this test

The Questions lane scores Jev without seeing any price or return. The Data lane publishes events without prices. The Lead joins prices to events and computes returns only at grading, after Jev's scores and the baseline are frozen with their hashes recorded here. No labels are needed.

## Order of work

1. Data lane: publish the member 8-K dataset (#311) with its manifest.
2. Lead: record the event counts and joins to prices (counts only), and note the hashes here.
3. Questions lane: estimate cost, then score the rating question and compute the baseline on every event; send hashes.
4. Lead: grade, recheck one return by hand, and report.

## Result

**Graded 17 Oct 03:40Z. Verdict: pass on the main test and on Jev against words.** Among 8-Ks of the same kind, the ones Jev rates worse are followed by worse 2-day returns, and Jev's rating does this where a negative-word count does not. The effect is small, it is mostly in the first day, and nothing is left after the first close following the filing.

Graded by the Lead from the frozen files (`events.csv` f885c806…, `jev/scores.csv` eb56f1c8…, `jev/baselines.csv` 9a6296a9…, `data/e7_prices/`) with the Lead's own script; numbers in `grading/summary.json`, each event in `grading/graded_events.csv`. 26,962 events in 44 cells (item group by year); 10,000 bootstrap draws of whole cells within item group, seed 311.

| Average rank correlation with the later return, within item group and year | Jev's rating | Word count (minus net tone) | Jev minus words |
|---|---|---|---|
| **Main: 2 days (day −1 close to day +1)** | **+0.025 (+0.015 to +0.034)** | −0.015 (−0.028 to −0.004) | **+0.040 (+0.026 to +0.055)** |
| Day 0 alone | +0.039 (+0.028 to +0.049) | −0.012 | +0.051 (+0.036 to +0.068) |
| 5 days | +0.022 (+0.009 to +0.034) | −0.010 | +0.032 (+0.015 to +0.047) |
| **10 days (second headline)** | +0.010 (−0.000 to +0.021) | +0.001 | +0.009 (−0.008 to +0.025) |
| Drift from the day 0 close to day +5 | −0.002 (−0.014 to +0.009) | −0.002 | −0.000 |
| Drift from the day 0 close to day +10 | −0.007 (−0.018 to +0.005) | +0.004 | −0.010 |

- **Main test:** +0.025, interval clear of zero: pass. **Jev against words:** +0.040, clear of zero: pass. The word count runs slightly the wrong way.
- **10 days:** the correlation halves and its interval just reaches zero, so it is not clear on its own.
- **No drift:** from the first close after the filing onward, neither Jev nor words predicts anything. The price moves on day 0 and stops. So this is not a trade at the closing price after filing.
- **In money terms:** within each cell, the fifth of events Jev rates best beat the fifth it rates worst by 0.29 points over 2 days (+0.16 to +0.42).
- **Every year:** positive in 13 of 14 years (2022 −0.017). After 10 Sep 2026, the only events Jev cannot have read about: 107 events, correlation +0.034, same direction, too few to test. Jev's training cut-off is not published, so the downgrade rule does not apply.
- **Robust:** officer changes alone +0.032 against words −0.027 (gap +0.059, +0.044 to +0.074); leaving out events with an earnings 8-K within 5 days +0.027; with a press release attached +0.042, without +0.027; Jev's bad score alone +0.023; good score alone +0.012 (−0.001 to +0.024).
- **The item code alone** says nothing across groups: item lean within years −0.005 (−0.017 to +0.006).

**Patterns after similar events (descriptive; market-adjusted, 2 days and 10 days, 95% intervals from resampling months):**

| Events | Count | 2 days | 10 days |
|---|---|---|---|
| Jev: very bad | 79 | −1.19% (−3.12 to +0.62) | −1.05% |
| Jev: bad | 1,456 | −0.34% (−0.55 to −0.13) | −0.38% (−0.77 to +0.08) |
| Jev: neutral | 22,463 | −0.05% (−0.10 to −0.01) | −0.13% |
| Jev: good | 823 | +0.16% (−0.05 to +0.38) | +0.14% |
| Jev: very good | 2,141 | +0.27% (+0.08 to +0.46) | +0.07% |
| Officer change, Jev very bad | 25 | −2.16% (−4.26 to −0.17) | −2.45% (−5.61 to +0.40) |
| Officer change, Jev bad | 774 | −0.68% (−1.02 to −0.37) | −0.89% (−1.40 to −0.36) |
| Deal, Jev very good | 1,941 | +0.32% (+0.12 to +0.53) | +0.11% |
| Restatement (4.02) | 15 | −2.00% (−4.86 to +0.17) | −1.07% |
| Delisting notice (3.01) | 146 | −0.69% (−1.93 to +0.30) | −0.99% |
| Restructuring (2.05) | 299 | −0.29% (−0.68 to +0.10) | −0.22% |
| Officer change (5.02), all | 16,860 | −0.07% (−0.13 to −0.01) | −0.16% |
| Material agreement (1.01), all | 9,303 | +0.05% (−0.02 to +0.12) | −0.05% |

**Correction (17 Oct 03:55Z, after an independent recheck):** the first version of this table's 10-day column ran from day −1 to day +10 (11 trading days) instead of day +9 like the 10-day headline; it now matches the headline. In the same pass, a stock with no price after day −1 now earns SPY for the whole drift window, as the design says (30 events; drift moves by under 0.0001). No correlation, interval or verdict changed. The first run's summary is kept as `grading/summary_v1.json`.

The full day-by-day paths for every item code, Jev answer and group-by-answer pair are in `grading/summary.json`.

**Rechecks:** Boeing's 8-K of 23 December 2019 (CEO resignation, accepted 16:58 Eastern, Jev: bad) recomputed by hand from the price file: Boeing −2.26%, SPY +0.54%, so −2.80% over 2 days and −2.84% over 10 days, matching the script. Pooled over all years within each group, Jev's rank correlation is +0.030 for officer changes, +0.050 for negative-leaning items and +0.014 for deals, matching the cell averages.

**Caveats:**

1. **Small effect:** a correlation of 0.025 explains well under 1% of the variation in 2-day returns. It is real across 27,000 events and 13 of 14 years, but small per event.
2. **Not a trade at the close:** most of the move is on day 0, and nothing follows the first close after the filing. Whether some of it can be caught at the next open was not tested.
3. **The news often comes first:** Boeing announced the CEO's exit on the morning of 23 December 2019; the 8-K came after the close. Some events are priced before day −1, which can only weaken this test.
4. **Model memory:** Jev sees company names and may know how some stories ended. The cut-off is unpublished; the 107 later events point the same way but are too few.
5. **SPY adjustment only,** S&P 500 members only.

**What it leads to:** Jev's 8-K rating carries real, if small, information about the immediate price reaction that word counts and item codes do not. As a standalone screen it has nothing left once the filing is a day old. Its natural use is as a fast event feature (for MCI-GRU, or for timing around filings), and a natural next test is the return from the next open after an after-hours filing.
