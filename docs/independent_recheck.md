# E11 independent recheck (17 Oct 2026)

Recomputed from `CARD.md`'s frozen design and the raw files, with my own code (`grading/independent_recheck/independent_recheck_code.py`). I did not read or import any grading script. Symbols: my own mapping (ticker runs + `handed_over` spans joined to `price_runs.csv`) gives one candidate for 26,796 events, all identical to `grading/joins.csv`. The other 166 have two candidates (FOX/FOXA, GOOG/GOOGL, NWS/NWSA, renamed tickers). For those I took the `joins.csv` symbol, which is always one of my two. Every return is computed from `daily_prices.csv.gz`. Only after my numbers were final did I open `grading/graded_events.csv`, to find the cause of the two differences below.

## Claimed vs recomputed

| Figure | Claimed | Recomputed |
|---|---|---|
| Events (officer / deals / negative / auditor) | 26,962 (16,263 / 8,953 / 1,678 / 68) | 26,962 (16,263 / 8,953 / 1,678 / 68) |
| Cells | 44 | 44 (14 / 14 / 14 / 2); partition identical to the Lead's |
| 2-day, Jev | +0.025 (+0.015 to +0.034) | +0.0247 (+0.0151 to +0.0340) |
| 2-day, words (−net tone) | −0.015 (−0.028 to −0.004) | −0.0154 (−0.0277 to −0.0044) |
| 2-day, Jev − words | +0.040 (+0.026 to +0.055) | +0.0401 (+0.0260 to +0.0545) |
| Day 0 alone, Jev / diff | +0.039 / +0.051 | +0.0387 / +0.0510 |
| 10-day (day −1 to +9), Jev | +0.010 (−0.000 to +0.021) | +0.0103 (−0.0001 to +0.0207) |
| 10-day words / diff | +0.001 / +0.009 (−0.008 to +0.025) | +0.0014 / +0.0090 (−0.0075 to +0.0247) |
| Drift day 0 close to +10, Jev | −0.007 (−0.018 to +0.005) | −0.0064 (−0.0177 to +0.0047), see note 1 |
| Drift words / diff | +0.004 / −0.010 | +0.0040 / −0.0104 |
| Officer × Jev 'bad': n, mean 2-day | 774, −0.68% | 774, −0.684% |
| Mean 2-day by Jev answer (vb / b / n / g / vg) | −1.19 / −0.34 / −0.05 / +0.16 / +0.27% | −1.189 / −0.339 / −0.054 / +0.164 / +0.267% |

Bootstrap: 10,000 draws of whole cells within item group, seed 311 (numpy default_rng). Spearman uses average-tie ranks. Every per-event 1-, 2- and 10-day return matches `graded_events.csv` exactly (largest difference 0).

## Hand checks (from adjusted closes; 2-day = day +1 / day −1 − 1, minus SPY's)

1. **very_bad**, SRCL (Stericycle) 0001193125-16-662174, negative group, accepted 2016-07-28 16:01:55 ET (after the close). Day −1 2016-07-28, day 0 2016-07-29, day +1 2016-08-01. Stock −15.633%, SPY +0.078%, **excess −15.711%**. Rating score −1.99.
2. **very_good**, ANDV (Andeavor) 0001193125-14-436515, deals group, accepted 2014-12-08 17:14:04 ET. Day −1 2014-12-08, day 0 2014-12-09, day +1 2014-12-10. Stock +1.266%, SPY −1.670%, **excess +2.936%**. Score +1.48.
3. **neutral**, TPR (Tapestry) 0001157523-19-001415, officer group, accepted 2019-06-19 06:45:35 ET (before the open, so day 0 is the same day). Day −1 2019-06-18, day 0 2019-06-19, day +1 2019-06-20. Stock +1.881%, SPY +1.183%, **excess +0.697%**. Score +0.08.

All three match my pipeline value and the Lead's per-event value.

## Sanity checks

- **(a) Shuffle test.** I shuffled Jev's scores within each cell 200 times. The weighted 2-day correlation then averages +0.0006 (sd 0.0056; 2.5 to 97.5% −0.0108 to +0.0096; largest +0.0140). The real +0.0247 beat all 200 shuffles. The null centres on zero and the observed value is well outside it.
- **(b) Window start vs acceptance.** In 26,961 of 26,962 events the day −1 close is strictly before acceptance, and in all 26,962 the day 0 close is after acceptance. The one exception is EL (Estée Lauder) 0001001250-22-000105, accepted at exactly 16:00:00 ET: its day −1 close is the same instant, so it is not before acceptance and not after it. Acceptance times: 5,353 before 09:30 ET, 3,367 during the session, 18,242 after 16:00. 66 were accepted on a non-trading day. No company has two events left with the same day 0.

## Disagreements and things that look wrong

1. **Drift +10 for stocks that stopped trading (tiny).** 30 events are mergers or delistings where the stock's last close is day −1 (AET, CELG, RHT and others). By the design these earn SPY, so their excess drift should be exactly 0. The Lead's file gives them SPY(+10)/SPY(−1) − SPY(+10)/SPY(0) instead, roughly SPY's day-0 return. The drift is measured from day 0, but the stand-in SPY leg starts at day −1. Effect on the headline: −0.00650 (Lead's values) vs −0.00645 (excluded) vs −0.00645 (set to 0). That rounds to −0.007 vs −0.006, so the conclusion does not change.
2. **The "10 days" column of the patterns table is not the 10-day window of the headline.** It is the path value p10 (day −1 to day +10, 11 sessions), not day −1 to day +9. For example, Jev very bad is −0.41% in the table but −1.05% on the defined 10-day window. Officer bad is −0.95% vs −0.89%, officer very bad −2.22% vs −2.45%, Jev good +0.10% vs +0.14%. The 2-day column and every correlation are correct. The 10-day column should be relabelled "to day +10" or recomputed to day +9.
3. **Half-day sessions are not handled (negligible).** The design assumes a 16:00 close every day. About 21 events were accepted between 13:00 and 16:00 ET on early-close days (day after Thanksgiving, July 3, Dec 24). For those, "day 0" closed before acceptance, so their day-0 return is pre-news. Day −1 is still before acceptance, so nothing leaks from the future.
4. **The auditor group is noisy.** 68 events in 2 cells, within-cell correlation −0.093. It carries 0.3% of the weight. Not an error.
5. 45 events stop trading before day +1, and 30 of them have a 2-day excess of exactly 0. This is as designed, and it is consistent between my code and the Lead's.

**Bottom line:** all headline numbers reproduce to the third decimal, and the intervals agree within bootstrap noise. The pass verdicts on the main test (+0.025) and on Jev against words (+0.040) stand. The only real defect is the 10-day label in the descriptive patterns table.
