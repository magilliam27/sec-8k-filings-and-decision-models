# 10-K research ledger

Every experiment, its verdict and the decisions behind it, newest first. Kept by the grading role (the Lead). One line per experiment; the card holds the detail. Last updated 18 October 2026. "Words" and "word counts" below mean the free word baselines; for E11 and E12 that is the word-tone score, positive minus negative Loughran-McDonald words.

## Where things stand

**Next open (E12, 17 Oct): nothing usable is left from the first open a trader can reach.** On the 23,585 E11 filings accepted while the market was closed, the rating's correlation with the return from the next open is +0.006 (−0.005 to +0.017) over 2 sessions and +0.008 (−0.006 to +0.022) over 5. The move E11 measured happens mostly overnight, before the open.

**8-K returns (E11, 17 Oct): Jev's rating of an 8-K lines up with the next 2 days' return, beyond the item code and better than word counts.** Across 26,962 S&P 500 8-Ks from 2013 to 2026, rank correlation +0.025 (+0.015 to +0.034) within item group and year; Jev minus words +0.040. Small, mostly on day 0, gone by 10 days, and nothing after the first close following the filing, so not a trade at the close. Officer changes Jev calls bad fall 0.7% over 2 days.

**Returns test (E7, 16 Oct): no 10-K risk signal predicts S&P 500 returns.** Across 6,871 filings from 2013 to 2026, neither how much the risk section changed (the Lazy Prices idea) nor Jev's share of changes for the worse is related to the next 1, 3 or 6 months' return; every interval spans zero. Jev's share edges word counting by −0.016 at 3 months, interval −0.034 to +0.002: not clear.

**Jev's first win, now confirmed: telling whether a change makes a risk worse (E8 15 Oct, E9 16 Oct).** Jev can't beat word counting at spotting that a risk changed. Across E1 to E6, on 11 companies, it never cleared noise; on 10 other companies words even beat it on new risks (E5). But at judging what the change means, it beats every free method. E8: AUC 0.979 against 0.926 for "the text grew" (interval +0.003 to +0.132). E9, 10 fresh companies frozen in advance: 0.947 against 0.838 (+0.024 to +0.199), and 0.810 for the change in negative words. The finance dictionary's share score runs backwards both times. The keys are AI reviewers. Jev still calls about a quarter of unchanged risks worse or better, so its signal should be counted only on risks words flag as changed. **8-K events (E10, 16 Oct):** rating 436 events from very bad to very good, Jev picks out the bad ones at 0.986 against 0.759 for the item code plus a word count, but the AI key reads the same rubric, so this shows sensible reading, not value.

## Experiments

| Id | Question | Data | Answer key | Jev | Baseline | Verdict | Card |
|---|---|---|---|---|---|---|---|
| E12 | From the first open a trader can reach, does Jev's 8-K rating rank the next 2 and 5 sessions? | E11's 26,962 events; EODHD opens | stock returns, entry open to close of session +1 and +4 | E11's ratings, no new spend | word-tone score | **Fail** (17 Oct): 2 sessions +0.006 (−0.005 to +0.017), 5 sessions +0.008 (−0.006 to +0.022); most of E11's move is overnight, before the open | [card](E12-next-open/CARD.md) |
| E11 | Does Jev's 8-K rating predict returns over 1 to 10 days, beyond the item code? | member_8k_events r1: 26,962 S&P 500 8-Ks, 2013–2026 | stock returns (EODHD), day −1 close to day +1 | questions_v5 rating on 26,962 events (55.2M tokens, $2.32) | item code, then dictionary net tone | **Pass** (17 Oct): 2-day corr +0.025 (+0.015 to +0.034); Jev minus words +0.040 (+0.026 to +0.055); gone by 10 days, no drift after day 0 | [card](E11-8k-returns/CARD.md) |
| E10 | How good or bad is an 8-K event for shareholders? Five-way rating | e10_8k_events r1: all 436 8-Ks of E5's 10 companies, 2013–2025 | AI ×3 on all 436 | questions_v5 (1.71M tokens) | item code, then dictionary net tone | **Pass** (16 Oct): bad events 0.986 vs 0.759, +0.128 to +0.323; key and Jev share a rubric | [card](E10-8k-events/CARD.md) |
| E9 | E8 repeated on 10 fresh companies: is the change worse? | 10 new companies (e9 r1) | AI ×3 on 300 | questions_v4 (0.81M tokens) | text-grew score | **Pass** (16 Oct): 0.947 vs 0.838, +0.024 to +0.199 | [card](E9-direction-confirm/CARD.md) |
| E7 | Do new, changed and worse risks predict returns? | e7_member_10k r1+r2: 752 S&P 500 companies, 6,943 member 10-Ks, 2013–2026 | stock returns (EODHD) | questions_v4 on 80,596 flagged risks | whole-section change (Lazy Prices), word shares | **Fail** (16 Oct): whole-section change +0.004 (−0.034 to +0.044); Jev's extra −0.016 (−0.034 to +0.002) | [card](E7-returns/CARD.md) |
| E8 | Is the change bad, good or neutral for the company? Three-way, plus a finer five-way list | E5's 300 risks | AI ×3 on 300 (95 changed: 61 worse) | AUC 0.979 for worse | dictionary 0.194 (runs backwards); text-grew 0.926 | **Pass**: +0.785 (+0.649 to +0.885) on the registered dictionary, and +0.053 (+0.003 to +0.132) on the fairer text-grew score. First Jev win (15 Oct) | [card](E8-change-direction/CARD.md) |
| E6 | Did this risk materially change? One yes/no question, 3 draws | Alphabet v2, 183 remaining risks | AI ×3 on all 183 (43 changed) | AUC 0.917 | word counts AUC 0.884 | **Stop**: gap +0.03, interval −0.02 to +0.09; no better than the original five-way answer (0.925) (15 Oct) | [card](E6-changed-noul/CARD.md) |
| E5 | New and changed risks on 10 other companies' 10-Ks; also Jev and words averaged | 10 companies r1, 3,228 risks | AI ×3 on 300 risks (85 new, 180 changed) | new AUC 0.987; changed 0.946 | words: new 0.999; changed 0.962 | **Stop** on all three tests: new −0.012 (−0.030 to +0.001); changed −0.016 (−0.05 to +0.02); averaged +0.012 (−0.003 to +0.030). New-risk recall at fixed cuts: Jev 54 of 85, words 70 (15 Oct) | [card](E5-ten-companies/CARD.md) |
| E4 | Did this risk materially change? (Jev's E2 "same" probability on fresh risks) | Alphabet v2 | AI ×3 on 100 fresh risks (35 changed) | AUC 0.906 | word counts AUC 0.887 | **Stop**: gap +0.02, interval −0.06 to +0.10; balanced accuracy tied at 78.8% (15 Oct) | [card](E4-changed-or-not/CARD.md) |
| E3 | How did this risk change? Same as E2, new answer key | Alphabet v2 | The owner's rulings define "material" | none | none | **Withdrawn** before any work: the owner kept E2's AI key instead (15 Oct) | [card](E3-change-type-key2/CARD.md) |
| E2 | How did this risk change? (5 options) | Alphabet v2 | AI ×3 majority on 76 (the owner's override; spot check 11 of 20 vs 15 needed) | 81% balanced | word rule 67% balanced | **Rethink**: gap +14 points, interval −7 to +25 includes zero; broadened precision 46% vs 90% (15 Oct) | [card](E2-change-type/CARD.md) |
| E1 | Is last year's risk the same risk? (yes/no) | Alphabet v1 | The owner, 200 blind | 92.5% | TF-IDF top match 94.5% | **Rethink**: Jev beats neither baseline (13 Oct) | [card](E1-same-risk/CARD.md) |

Exploratory follow-ups to E1, not pre-registered: AI reviewers re-judged 44 pairs (TF-IDF 98.0%, Jev 96.0% on their labels), and both methods flag the same 8 clearly new risks in 12 years. Details on the E1 card.

**Label reuse (15 Oct):** the thread "Tuning Jev for our work" uses E2's 76 and E4's 100 graded risks as its exploration set (outputs in `jev_tuning/` (a separate tuning folder, not in this repository)). Those 176 risks, and since E6's grading its 183 too (all 283 fresh Alphabet risks), can no longer test anything that thread proposes; any tuning idea gets graded on fresh labels, such as E5's. It also found that repeated identical Jev calls return slightly different probabilities (0.80, 0.78, 0.78 on one test), so each cached answer is one draw, and that `jev-1.14.0` went live on 14 Oct. All experiments here stay pinned to `jev-1.13.0`.

## Datasets

| Version | Where | Built at | Known defects |
|---|---|---|---|
| ten r1 | `data/ten_companies_10k/` (Data lane) | 2ef33e5, 15 Oct, issue magilliam27/MCI-GRU#297 | None known. 130 10-Ks (JPM, DAL, XOM, PFE, WMT, BA, MSFT, KO, UNH, CAT; FY2013 to FY2025), 3,455 risks, all six checks pass. Only 2.4% of risks have a closest prior match under 0.25 similarity, so these companies carry risks over almost as steadily as Alphabet. Used by E5 |
| r1 | `data/alphabet_10k/` (Data lane) | c5934e1, 15 Oct, draft PR magilliam27/MCI-GRU#294 | None known. Five automatic checks pass on all 13 years; 393 risks (the 2018 heading fix splits one); bullets kept in every year. Not used by any experiment yet |
| v2 | `jev_pilot/sec_v2/filings/` | 3ec507c, 13 Oct | 2018 heading over the 600-character limit merges two risks (handled in E2 by excluding 4 rows) |
| v1 | `jev_pilot/sec/` | 9502de7, 13 Oct | 2017 split heading, page numbers 2023 to 2025, the 2018 heading |

The Alphabet versions hold its 13 10-Ks, FY2013 to FY2025. The Data lane publishes new versions under `data/`; r1 is its first.

## Decisions

| Date | Decision | By |
|---|---|---|
| 16 Oct | E11 design frozen before any member 8-K, Jev score or return: within item group and year, rank correlation of Jev's rating with the 2-day SPY-adjusted return; Jev against net tone; pass downgraded to unclear if it fails after Jev's training cut-off | Lead |
| 17 Oct | E11: rate all 26,962 test events with Jev, about $2.40 instead of $1 | Owner |
| 16 Oct | Test Jev's 8-K rating on returns in the days after filing (E11), about $1 of Jev | Owner |
| 16 Oct | E7 design frozen before any price: quarterly rank correlations at 63 days; main test whole-section change; Jev's test is its 'worse' share against the changed share | Lead |
| 16 Oct | E7 parser findings (13% of member reports flagged, sector-concentrated): one fix pass, then leave out the rest by year and sector; keep whole Item 1A text where splitting fails | Lead |
| 16 Oct | E10: use all 436 events instead of a 300 sample; verdict needs at least 20 bad or very bad in the key | Lead |
| 16 Oct | E7 membership: fja05680 S&P 500 history topped up from Wikipedia; only 10-Ks filed during membership; delisted companies included before grading | Lead |
| 16 Oct | Test Jev rating 8-K events from very bad to very good (E10), chosen from six sentiment ideas | Owner |
| 16 Oct | Confirm E8 on 10 fresh companies (E9) and start the S&P 500 10-K pull for the returns test (E7) | Owner |
| 15 Oct | Test whether Jev can tell if a change is bad, good or neutral, which word counts can't (E8) | Owner |
| 15 Oct | E5 sample: all 144 risks under 0.5 similarity plus 156 above it in proportion to company size, instead of 30 per company (new-risk candidates are too uneven across companies), before any label | Lead |
| 15 Oct | Add the tuning thread's free Jev-plus-words rank average to E5 as a third test, before any E5 label exists | Lead |
| 15 Oct | Test the tuning thread's best question (one yes/no "materially changed?") on Alphabet's 183 unlabelled risks before E5 (E6) | Lead |
| 15 Oct | Not 8-Ks. Explore other companies' 10-Ks next (lifts the Alphabet-only rule), and look separately at tuning Jev's parameters | Owner |
| 15 Oct | Next test is E4: check Jev's "same" probability on 100 fresh risks, no new Jev spend | Owner |
| 15 Oct | Grade E2 on the AI reviewers' labels despite the 11-of-20 spot check (an override of the 15 bar), decided before any Jev answer existed | Owner |
| 15 Oct | Settle E2's 9 spot-check disagreements personally (replaced the same hour by the override above); the rulings define "material" for a new key (E3) | Owner |
| 15 Oct | Trust bar for E2's AI answer key: the owner's 20 must match it on at least 15 (set by the Lead before the labels came back; the owner did not object) | Lead |
| 15 Oct | Four lanes; the Data lane improves the parser only, no other companies yet; merge PR magilliam27/MCI-GRU#290 | Owner |
| 14 Oct | The owner's labels must be their own blind call: both texts in full, nothing highlighted, no AI answers | Owner |
| 13 Oct | E2 answer key: AI labels on all 80 plus the owner's blind spot-check of 20 | Owner |
| 13 Oct | After E1, test how a risk changed rather than stop | Owner |
| 13 Oct | Novel-risk recall matters more than a slight edge in overall accuracy | Owner |
| 12 Oct | Jev judges every current risk against every prior-year risk | Owner |
| 11 Oct | Start with one question on Alphabet 10-K risk factors, FY2014 to FY2025 | Owner |

## Open questions for the owner

- Which companies for E5? Default is the plan's 10: JPM, DAL, XOM, PFE, WMT, BA, MSFT, KO, UNH and CAT.
