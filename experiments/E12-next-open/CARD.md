# E12: Can a retail trader catch Jev's 8-K signal by trading at the next open?

**Status: design frozen 17 Oct 23:45Z, before any opening price was read for these events.** The owner asked (17 Oct 23:34Z): "I'm a retail trader so little trading costs and I would be interested in signal meaning to 2 and 5 days." No new Jev spend: the E11 ratings and events are reused unchanged.

**Why:** E11 found that Jev's rating lines up with the return from the close *before* the filing, and that nothing is left from the first close *after* it. A trader cannot buy at the earlier close. The gap between the two is untested: many 8-Ks arrive after the close or before the open, and the first price a trader can get is the next open. This test asks how much of E11's signal is still there from that open.

**What is already known (not blind):** the Lead has seen all E11 results, including day 0 alone (+0.039) and the drift from the day 0 close (zero). No opening price, and no split of day 0 into overnight and session, has been looked at.

**Example:** Boeing's CEO-exit 8-K on 23 December 2019 was accepted after the close. A trader reading Jev's "bad" that evening can sell at the 24 December open, not at the 23 December close.

## Frozen design

| Item | Value |
|---|---|
| Events | E11's graded events (`E11-8k-returns/grading/graded_events.csv`, 26,962), same Jev rating score, same word-tone baseline, same cells (E11's `cell` column) |
| Entry | The first regular-session open (09:30 US Eastern) after acceptance. Filings accepted when the market is closed (after 16:00, before 09:30, weekends, holidays) enter at the day 0 open. Filings accepted 09:30 to 16:00 enter at the next trading day's open |
| Price | EODHD open, adjusted with the same factor as the close (open × adjusted close ÷ close), from `data/e7_prices/` |
| Bad opens | An event whose stock has no open, or an open of zero, on the entry day is dropped and counted. Gaps of more than 30% between the day −1 close and the entry open are listed for a by-hand check, not dropped |
| Outcome | Stock return from the entry open to the close of the entry day +1 (**2 sessions, main**) and +4 (**5 sessions, second headline**), minus SPY's return over the same open-to-close span. A stock that stops trading inside the window keeps its return to its last close and earns SPY after that (as E11) |
| Groups | **Main: filings accepted when the market is closed** (they enter at day 0's open, so this is E11's day 0 with the overnight gap removed). Also reported: filings accepted during market hours (enter the next day), and all filings together |
| Statistic | As E11: within-cell Spearman, event-weighted average over cells, cells resampled within item group, 10,000 draws, seed 312. Cells with under 10 events in a subset are dropped |
| **Main test** | Jev's rating against the 2-session return, closed-market filings. Pass: positive with the interval clear of zero |
| **Second headline** | The same on 5 sessions |
| Jev against words | Jev's correlation minus word tone's, both windows |
| Also reported | Mean market-adjusted return by Jev answer (month bootstrap, 2,000 draws), for officer changes Jev calls bad, and for deals Jev calls very good; top fifth minus bottom fifth per cell; how much of the E11 2-day move happens between the day −1 close and the entry open (the part a trader cannot get) |
| Cost and trading | No Jev spend. Retail commissions are taken as zero; the bid-ask spread at the open is not modelled and is listed as a limit. Opening auction prices are assumed fillable |
| What a pass leads to | A paper-trading rule for the owner to watch on new filings (no money at stake), and the rating as an event feature for MCI-GRU. A fail is reported as a fail |

## Known limits before running

- Daily data only: a filing at 10:00 enters at the next open, so the intraday reaction that day is not caught or measured.
- The EDGAR acceptance time is taken as the time the filing became public. A filing accepted late in the evening may in practice be seen only the next morning, still before the open.
- Filings accepted 09:00 to 09:30 leave little time to rate them before the open; counted as closed-market anyway and reported by count.
- Jev may remember outcomes (no published cut-off), as in E11.

## Result

**Graded 17 Oct 23:40Z. Verdict: fail.** From the first open a trader can reach, Jev's rating does not rank the next 2 or 5 sessions. Most of what E11 measured happens overnight, before the open.

Graded by the Lead with `grade_e12.py` (in this repository at `grading/scripts/e12/`); numbers in `grading/summary.json` (20b8f5a8…). The per-event file `grading/graded_events.csv` holds the model's per-filing ratings and is not published. 26,928 events with a usable open (34 dropped: no open or zero open). 23,585 were accepted while the market was closed, 3,343 during market hours. 10 events had a gap over 30% (deal announcements such as Abiomed, AMD, Molex, and Fiserv's and Trade Desk's falls); they are real moves and stay in.

| Within-cell rank correlation, closed-market filings | Jev | Word tone | Jev minus words |
|---|---|---|---|
| E11's 2 days on the same events (close before filing) | +0.029 (+0.018 to +0.041) | −0.015 | +0.044 |
| Close before filing to entry open (the part a trader cannot get) | +0.054 (+0.039 to +0.069) | +0.005 | +0.049 |
| **Main: entry open to close of the next session (2 sessions)** | **+0.006 (−0.005 to +0.017)** | −0.019 (−0.028 to −0.010) | +0.025 (+0.012 to +0.038) |
| **Entry open to 5 sessions** | **+0.008 (−0.006 to +0.022)** | −0.017 | +0.025 (+0.008 to +0.040) |

- **Main test: fail.** The interval includes zero at 2 and 5 sessions. Filings accepted during market hours, entered the next morning, show nothing either (+0.003, +0.003).
- **Jev minus words is positive only because word tone runs backwards after the open** (negative-sounding filings do slightly better), not because Jev ranks well. It is not a usable result.
- **Good news overshoots at the open, then gives some back.** Very good: +0.39% from the close to the open, then −0.15% (−0.29 to −0.03) over 2 sessions. Good: +0.36%, then −0.17%.
- **Bad news keeps sliding a little.** Bad: −0.17% to the open, then −0.21% (−0.40 to −0.02) over 2 sessions and −0.33% (−0.67 to +0.00) over 5. Officer changes Jev calls bad (706): −0.33% (−0.60 to −0.08) over 2 sessions, −0.51% (−1.02 to −0.04) over 5. Every filing drifts a little below the market (neutral −0.05% and −0.10%), so against neutral filings the bad-news slide is about −0.2 points. These are descriptive cuts among many, not tested on their own.
- **Fifth-against-fifth:** best-rated fifth minus worst-rated fifth +0.04 points over 2 sessions (−0.07 to +0.14). Nothing a trader could rely on.

**What it leads to:** no trading rule from the open. The one pattern worth a look is the slide after bad officer-change news. It can only be checked fairly on filings that arrive from now on, by paper trading, since these numbers were found by looking.
