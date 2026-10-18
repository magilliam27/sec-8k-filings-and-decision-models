# E13: Does Jev's 8-K signal survive when the company's name is hidden?

**Status: graded 18 Oct 03:10Z. Verdict: unclear. Jev's rating keeps exactly its E11 link with returns when the name is hidden (+0.025, against +0.025 with the name), but Jev can still tell which company filed from the masked text (72% name mask, 64% deep mask, out of five; chance 20%), so memory is not ruled out.** Design frozen 18 Oct 02:41Z, before any masked Jev score or leak-check answer existed. The owner asked (18 Oct 01:45Z) to test "the masking of names idea discussed in our report". The report (docs/REPORT.md, section 4) lists it as the first test for model memory: "re-rates the filings with the company name masked, as Glasserman and Lin do."

**Why:** E11's caveat is that Jev sees the company name and may remember how a story ended: if Jev was trained on later news about Boeing's December 2019 CEO exit, its "bad" may be memory rather than reading. Glasserman and Lin (2023, [arXiv 2309.17322](https://arxiv.org/abs/2309.17322)) test this for GPT news sentiment by removing company identifiers from the text. Removing them takes away two things at once: look-ahead (knowing what followed) and distraction (general views about the company getting in the way of the reading). In their headlines, anonymised versions did better in-sample, which they read as distraction outweighing look-ahead, most of all for large firms.

**What is already known (not blind):** the session that ran this test had read every E11 and E12 result. No masked score exists yet. The returns, cells and original ratings are E11's frozen files; only the masked ratings are new.

**Example:** Boeing's 8-K of 23 December 2019 (CEO exit, Jev's E11 answer "bad") opens "On December 23, 2019, The Boeing Company (“Boeing”) announced that its Board of Directors ... elected David L. Calhoun". Under the name mask Jev reads "On December 23, 2019, The Company announced that its Board of Directors ... elected David L. Calhoun", with "withheld" in the company field. Under the deep mask the people, other company names and places are also replaced ("elected [person]"), and the revenue line reads "$100.0 billion" instead of "$101.1 billion". The question, answer options and option order are E11's, unchanged. If the rating still lines up with the 2-day return without the name, memory through the name is not what E11 measured.

## Frozen design

| Item | Value |
|---|---|
| Events | E11's 26,962 test events (`E11-8k-returns/events.csv`, sha256 f885c806…0b3b), from `member_8k_events` r1 (`member_8k_events.jsonl` 04172c9b…931f) |
| Question | E11's rating question, `configs/filings/questions_v5.yaml` unchanged, `jev-1.13.0`, options shuffled per event from the event id exactly as in E11. Asked once per event per mask level with `scripts/data/score_8k_events.py --question rating` |
| **Name mask** (the report's test) | Code: `src/sec8k/masking.py`, `scripts/data/mask_8k_events.py`. The state's company field becomes `withheld`. In the text: the filer's legal names (member table, its 8-Ks, SEC's current and former names) and their cores without suffixes, a distinctive first word of a current name and its initials (capitalised or in capitals only), its tickers, become "the Company" or "[ticker]"; every web and e-mail address becomes "[website]" or "[email]". A word that many other filers write in lower case ("target", "general") is masked only in its capitalised spellings. A **residual check** stops the run if any event still holds its filer's multi-word name core, a one-word core capitalised, or a ticker after an exchange name |
| **Deep mask** (stronger, secondary) | The name-masked text with named people, other organisations, places and products (spaCy `en_core_web_sm` 3.8.0) replaced by "[person]", "[organization]", "[place]", "[product]", phone numbers by "[phone]", and prior revenue rounded to one significant figure. Kept: 8-K item titles, job titles ("Group President"), defined terms in quotes, and regulators, exchanges, boards and committees |
| Not masked | Dates, amounts, item codes, the prior-90-day 8-K list, and business descriptions ("an integrated global biopharmaceutical company") |
| **Leak check** | Can Jev still tell who filed? A fixed sample of 1,000 events (seed 313, `jev/identify/identify_sample.csv`, sha256 324d1a5a…). For each, five companies: the filer and four other filers drawn from the same SIC code, widening to two digits, one digit, then any (`identify_options.csv`). Jev picks the filer, on the original, name-masked and deep-masked text, same options in the same order (`scripts/data/identify_8k_company.py`). Chance is 20%. Interval: 10,000 draws of whole companies. A mask level **hides the filer** if the upper end of its interval is below 50% |
| Redraw control | The original, unmasked rating asked again on the same 1,000 events with an empty cache (`jev/redraw/`), to show how much Jev's answers move between identical calls. A masked answer differing from E11's only as often as a redraw does means the mask changed little |
| Returns and cells | E11's frozen `grading/graded_events.csv`: market-adjusted returns from the day −1 close, cells of item group by year |
| Statistic | As E11: within-cell Spearman, event-weighted average over cells, 10,000 draws of whole cells within item group, seed 313. Every signal and difference uses the same draws (paired) |
| **Main test** | Name-masked rating against the 2-day return. **Survives** if positive with its interval clear of zero |
| **Name against original** | Name-masked minus E11's rating, paired. Below zero with its interval clear: the name carried part of the signal (memory, or knowledge about the company). Above zero and clear: masking helped (Glasserman and Lin's distraction). Otherwise: no detectable difference |
| Deep mask | The same two tests on the deep mask, reported beside the main test |
| **Memory verdict** | **Name memory unlikely to explain E11** if at least one mask level both hides the filer (leak check) and survives (main test on that level). **Unclear** if a level survives but no surviving level hides the filer. **E11 may rest on knowing the company** if no level survives |
| Also reported | Every E11 window (day 0, 5 and 10 days, drift after the day 0 close); each mask against word tone; by period (2013–2017, 2018–2021, 2022–2026: memory should matter most for older events); by company size (thirds of prior revenue: Glasserman and Lin found distraction largest in large firms); officer changes alone; events after 10 Sep 2026; answer counts; mean 2-day return by masked answer; officer changes the masked rating calls bad |
| Grading script | `grading/grade_e13.py` (here `grading/scripts/e13/grade_e13.py`), frozen with this card. `check` mode joins scores and prints agreement and the leak check without reading any return |
| Cost | Rating question on 26,962 events at each of two mask levels, about 55M input tokens each ($2.32 each at E11's rate); leak check 3,000 calls and redraw 1,000 calls, about 8M tokens ($0.35). About **$5 in all**, within the agreed budget. If the measured estimate for either mask level passes $3, stop and ask the owner |
| What a result leads to | If name memory is unlikely, E11's caveat narrows to memory through dates and event details, and the forward hold-out (the report's second test) is the remaining check. If E11 rests on knowing the company, the write-up downgrades E11 to unclear. Either way the masked rating is a candidate input for MCI-GRU in place of the original |

## Known limits before running

- **A name mask cannot remove everything that identifies a company.** People, places, products and the business description remain under the name mask; the deep mask removes most of the first three, not the description. The leak check measures what remains rather than assuming it away.
- **Masking also removes honest information.** The deep mask hides counterparties ("acquire [organization] for $2.1 billion"), so a deep-mask drop is not all memory. The name mask removes little a careful reader would need.
- **Dates stay.** A model that knows the event type and date could still recall a story for a well-known event even without the name, so a survival result rules out memory through the name, not all memory.
- **The tagger is imperfect.** `en_core_web_sm` misses some names and tags some phrases wrongly; the counts below show how much it replaced.
- **Leak-check distractors** are drawn from all filers in the data, including some that had stopped filing by the event's date; Jev could rule those out from the date, which makes the leak look larger, not smaller.
- **One draw per event.** Jev's answers vary slightly between identical calls (an earlier tuning finding); the redraw control sizes that.
- Texts lengthened by placeholders are cut at 20,000 characters, as E11's were.

## Masked data (counts only, before any score)

Built 18 Oct 02:24Z to 02:38Z by `scripts/data/mask_8k_events.py` at MCI-GRU commit 44f708d (PR magilliam27/MCI-GRU#314, ported here to `src/sec8k/` and `scripts/data/`), into `masked/` (manifest `masked/masked.meta.json`).

| | Name mask | Deep mask |
|---|---|---|
| Events | 26,962 | 26,962 |
| Replaced | 243,434 names, 32,487 tickers, 27,202 web and e-mail addresses | on top: 1,011,990 tagged entities, 17,334 phone numbers |
| Events where the text never names the filer | 1,562 (only the company field changes) | |
| Residual check | 0 events keep a filer name or exchange ticker | |
| Cut at 20,000 characters after masking | 605 (placeholders lengthened them; only the tail is lost) | 259 |
| `events.jsonl` sha256 | 3547f97d…19f | d22f92c7…fd6 |
| Estimated input tokens (characters ÷ 4) | 48.0M, about 55.7M after E10's 16% under-count, about $2.34 | 47.5M, about 55.1M, about $2.31 |

`identities.csv` (c5d0ffcb…849b) lists the names, former names, tickers and patterns each of the 750 filers is masked by. Both estimates are under the card's $3 stop line, so no question to the owner is needed.

## Freeze (18 Oct 02:41Z)

Frozen before any masked score, leak-check answer or redraw existed: this card and `grading/grade_e13.py` (hashes in `freeze.sha256` beside this card), the masked events above, and the leak-check sample and options (`jev/identify/identify_sample.csv` 324d1a5a…, `identify_options.csv`). Code: MCI-GRU 44f708d.

## Scoring log

- 02:41Z to 02:47Z: leak check, 3,000 calls (5.77M input tokens), and redraw control, 1,000 calls (2.08M), no failed call. Two one-event SDK test calls before that (about 7,000 tokens).
- 02:41Z to 02:53Z: name mask, 26,962 rating calls (54.62M input tokens), no failed call. `jev/name/scores.csv` a1dd3cf2…, answers `jev/name/answers/rating.jsonl`.
- 02:53Z to 03:06Z: deep mask, 26,962 rating calls (54.07M), no failed call. `jev/deep/scores.csv` ae4b0e30….
- **Total: 116.5M input tokens, about $4.89** at $0.042 per million.

## Result

**Graded 18 Oct 03:10Z with `grade_e13.py save` (frozen, hash in `freeze.sha256`; in this repository at `grading/scripts/e13/`); numbers in `grading/summary.json` (710d2e34…). The per-event file `grading/graded_events.csv`, the masked texts and the model's masked answers hold SEC filing text or per-filing ratings and are not published. Verdict by the card's rule: unclear.** Both mask levels survive the main test, but neither hides the filer.

**1. Leak check: the masks do not hide the company.** Jev picks the right filer out of five same-industry companies:

| Text Jev reads | Right filer | 95% interval (whole companies resampled) | Hides the filer (upper end under 50%)? |
|---|---|---|---|
| Original | 100% | 100 to 100 | no |
| Name mask | 72.1% | 69.0 to 75.1 | no |
| Deep mask | 63.7% | 60.4 to 66.9 | no |
| Chance | 20% | | |

**2. Main test: the signal is unchanged.** Rank correlation with the 2-day market-adjusted return, within item group and year, 26,962 events, 44 cells, paired draws:

| Signal | 2 days (main) | Minus E11's rating | Minus word tone |
|---|---|---|---|
| E11's rating (name shown) | +0.025 (+0.015 to +0.034) | | +0.040 |
| **Name mask** | **+0.025 (+0.014 to +0.036)** | **+0.001 (−0.003 to +0.005)** | +0.041 (+0.025 to +0.056) |
| Deep mask | +0.024 (+0.014 to +0.034) | −0.001 (−0.006 to +0.005) | +0.039 (+0.024 to +0.055) |

- **Main test: survives** at both levels. **Name against original: no detectable difference** at either level, so no sign of look-ahead (a drop) or of Glasserman and Lin's distraction (a gain).
- **Why so little moves:** masking changed Jev's answer on 1.9% of events (name) and 2.6% (deep); asking the identical unmasked question again changed 0.5% (redraw control, 1,000 events). Rank correlation of scores with E11's: 0.95 (name), 0.93 (deep), 0.98 for a redraw. Answer counts barely move (bad 1,456 → 1,566 → 1,609; very good 2,141 → 2,189 → 2,185).
- **Windows:** day 0 +0.036 (name) and +0.036 (deep) against +0.039; 5 days +0.023 and +0.022 against +0.022; 10 days +0.013 and +0.011 against +0.010. Drift from the day 0 close is still nil at both levels. No window differs from E11 by more than its interval.
- **By period** (memory should matter most for older events): 2013–2017 name +0.034, deep +0.028, original +0.035 (deep minus original −0.007, −0.014 to −0.000, the one cut that clears zero, barely); 2018–2021 +0.033, +0.033, +0.028; 2022–2026 +0.008, +0.011, +0.009. The masked rating is weaker in recent years exactly as the original is, so that decline is not explained by the name.
- **By company size:** large firms +0.038 (name), +0.036 (deep), +0.040 (original); small +0.018, +0.016, +0.012 (name minus original +0.006, +0.001 to +0.012). Unlike Glasserman and Lin, no gain from masking in large firms.
- **Officer changes alone:** +0.031 (name), +0.030 (deep), +0.032 (original). Officer changes rated bad: −0.53% over 2 days (name, 848 events), −0.39% (deep, 887), −0.68% (original, 774).
- **After 10 Sep 2026** (107 events): +0.087 (name), +0.079 (deep), +0.034 (original); too few to test.

**Rechecks:** the name-masked main correlation recomputed by a separate script straight from `jev/name/scores.csv` and E11's returns: +0.0254 over 44 cells, matching. E11's own rating through this script: +0.0247, matching E11's card. Boeing's CEO-exit 8-K (the example): Jev says bad with the name (score −1.24), bad under the name mask (−1.38) and bad under the deep mask (−1.34); its 2-day return was −2.80%.

**What the verdict means.** Hiding the name changes almost nothing Jev says, and nothing about how its ratings line up with returns. Either Jev reads the event and not the name, or it recognises the company from what is left and could still recall the story. The leak check shows the second is possible: in a five-way choice it recognises most filers. Recognition when asked is easier than spontaneous recall when not asked, so the leak check overstates the risk, but this test cannot measure by how much. So E13 does not support "memory through the name drives E11", and it does not rule memory out.

**Found by looking, not part of the frozen design:** most of the leak comes from attached press releases, which end with an "About the company" paragraph. On the 629 sampled filings with no press release attached, Jev picks the filer 60.1% of the time under the name mask and 49.3% under the deep mask (near the 50% line); with one attached, 92.5% and 88.1%. On all 17,101 filings without a press release, the deep-masked rating's 2-day correlation is +0.026 (+0.015 to +0.038), against +0.027 (+0.015 to +0.040) for E11's rating. This points the same way as the main result in the place where the company is hardest to spot, but it was chosen after seeing the leak check, so it is a lead, not a test.

**What it leads to:** the forward hold-out (the report's second memory test) is the only clean check left: rate 8-Ks filed after the model's release, publish the hashed ratings, then grade. A stronger mask (dropping the press-release "About" paragraph, or the exhibit) would be a new experiment id. The masked rating can stand in for the original as an MCI-GRU input: it carries the same signal.


## The owner's reading, added after the result (18 Oct 03:45Z, post-hoc, not part of the frozen verdict)

The owner's point: the masks did make Jev lose track of many filers, yet the signal did not fall with them. If the 2-day signal came from Jev recalling each company's story, it should have dropped roughly in proportion to the filers Jev could no longer identify. It did not:

| Mask | Filers Jev no longer identifies (leak check, corrected for guessing) | Expected change if name memory drove the signal | Observed change against E11 (95% interval) |
|---|---|---|---|
| Name mask | 35% | about −0.009 | +0.001 (−0.003 to +0.005) |
| Deep mask | 45% | about −0.011 | −0.001 (−0.006 to +0.005) |
| Deep mask, filings without a press release | 63% | about −0.017 | −0.001 (−0.009 to +0.008) |

Revised 18 Oct 04:00Z at the launch review's suggestion (first version: 28%, 36% and 51% lost, from 1 − accuracy, with every row against +0.025). A five-way pick is right 20% of the time by guessing, so the share still identified is (accuracy − 0.2) ÷ 0.8 and the rest is lost. The expected change is the share lost times the same filings' E11 correlation: +0.025 overall, +0.027 without a press release. Figures in `grading/posthoc.json` (aggregates only, post-hoc). A proportional drop lies outside the observed interval in all three rows. This is not a perfect result, but it adds support to E11's finding that Jev reads the event rather than the name.

The weakness of the argument: memory need not be spread evenly. It may sit mostly in famous events (Boeing's CEO exit, say), which Jev still identifies under both masks. The filings that became unrecognisable are mostly ones without a press release, where memory would matter least anyway. So this counts against name memory being the main driver, without ruling it out. The frozen verdict stays **unclear**, and the forward hold-out is still the clean test.
