# E7: Do new, changed and worse risks predict stock returns?

**Status: graded 16 Oct 11:05Z. Verdict: fail. No signal predicts returns.** Design frozen 16 Oct 10:10Z. In preparation since 16 Oct 02:20Z. The owner chose "Confirm, prep returns" (16 Oct 02:13Z): the Data lane starts the S&P 500 10-K pull now, and the design below is settled before any return is looked at. Jev's "worse" signal joins only if E9 confirms E8. Nothing is scored on returns until prices are available.

**Why:** across five tests on 11 companies, free word counts spotted new and changed risks as well as Jev or better. So the open question is no longer whether Jev can read the changes. It is whether the changes matter for prices. Published work suggests they might: Cohen, Malloy and Nguyen ("Lazy Prices", Journal of Finance, 2020) found that firms whose 10-K text changes a lot from the year before go on to underperform, with the risk-factor section among the most informative parts. This test asks whether that holds in our data, using word counts only.

**Example:** in its fiscal 2020 10-K, Delta added pandemic risks with no close match in fiscal 2019. Each filing gets a score, such as the share of its risks that are new or changed. The test asks whether high-score filings are followed by worse returns than low-score ones.

## Proposed design (to settle before any return is looked at)

| Item | Proposal |
|---|---|
| Signal | Per 10-K, from the existing word rules: the share of risks that are new (closest match under 0.25 similarity) and the share that changed (word share 0.04 or more). Also the overall text similarity to last year's Item 1A, as in Lazy Prices. **Added after E8 passed (15 Oct 05:15Z):** Jev's share of risks whose change made things worse (questions_v4 direction), tested against the word-only signals. At E8's cost, every changed risk for about 500 companies is roughly 150,000 calls and 200M input tokens, about $8 |
| Event time | The 10-K's EDGAR acceptance time (true UTC, converted with a real timezone library). Returns start on the next full trading day, so no lookahead |
| Outcome | Return over the next 1, 3 and 6 months, minus the market's return over the same window |
| Test | Rank filings into high and low change groups within each year, and check whether the gap in later returns is clear of zero |
| Breadth | 11 companies give only about 130 filings, too few for a return test. It needs many companies: a point-in-time S&P 500 list, pulled from EDGAR (free) by the Data lane, about 6,000 filings over fiscal 2013 to 2025 (the Data lane's count, 16 Oct: about 8,500 10-Ks from the companies involved, fewer once limited to membership) |
| Membership (decided 16 Oct 03:50Z) | Dated member lists from github.com/fja05680/sp500 (free; 1996-2019 from Andreas Clenow's Norgate-based data, since then from Wikipedia with dates checked by its maintainer), topped up from Wikipedia after its last row (2026-08-18) and spot-checked on about 20 change dates against S&P press releases. About 790 companies were members at some point since 2013. A 10-K counts only if it was filed while its company was a member; the 10-K just before entry is pulled as its pair partner. Rejected: Wikipedia alone (incomplete), EODHD index lists (need a plan we don't have), CRSP/Compustat (paid). Working files: `data/e7_prep/` |
| Pairing | Each 10-K pairs with its company's previous 10-K by filing date, keyed by accession number and period of report, so a change of year-end (GE, ServiceNow and four others) keeps both reports |
| Survivors | Companies later acquired, delisted or renamed (about 180 tickers) are pulled too, matched to EDGAR by name. Every ticker-to-company mapping is checked by name, because tickers get reused (Pepco's POM, Spectra's SE). Grading waits until they are in, since leaving them out would bias returns upward. Every company left out is recorded with its reason |
| Prices | EODHD daily prices, the repo's planned source |
| Cost | No Jev spend. EDGAR pulls are free; prices depend on the EODHD plan |

## Frozen design (16 Oct 10:10Z, before any price is pulled or any return is looked at)

This replaces the proposed design above wherever they differ.

| Item | Value |
|---|---|
| Filings | Every member 10-K in `e7_member_10k_risk_factors` r1 and r2 (752 companies, 6,943 member reports, accepted 2013 to 2026), each with its pair partner, the company's previous report by acceptance time. A filing counts only if its 6-month return window has ended by the price pull |
| Signal 1: whole-section change (the Lazy Prices replication) | 1 minus the cosine similarity of word counts between this Item 1A and the previous one (`member_item_1a.jsonl`; lower-cased words, the same tokeniser as the risk baselines, no stop-word removal). Covers about 97% of filings |
| Signal 2: share of new risks | Share of the filing's risks whose closest prior risk (`closest_prior_pairs`, per company) has similarity under 0.25. Only filings whose risks passed every check (about 93%) |
| Signal 3: share of changed risks | Share whose word score (larger of words-added and words-removed shares) is 0.04 or more, new risks included. Same filings as Signal 2 |
| Signal 4: Jev's "worse" share | Among the risks Signal 3 flags, the sum of Jev's probability of "worse" (questions_v4 direction, `jev-1.13.0`, unchanged), divided by the filing's number of risks. Jev is asked only about flagged risks, because it calls about a third of unchanged risks worse or better (E9). Same filings as Signal 2 |
| Event time | The EDGAR acceptance time, converted to US Eastern time. Returns start at the first market close (16:00) after acceptance: a filing accepted at 09:00 on a Tuesday starts from Tuesday's close, and one at 16:30 starts from Wednesday's. So no return before the filing is public is counted, and the first reaction is left out, which makes the test conservative |
| Outcome | Return over 21, 63 and 126 trading days from that close, using EODHD adjusted closes, minus SPY's adjusted return over the same days. A stock that stops trading inside the window keeps its return to its last close and earns SPY's return after that (EODHD has no delisting payout) |
| Test | Filings are grouped by the calendar quarter of acceptance; quarters with fewer than 30 filings join the next quarter. Within each group, the Spearman rank correlation between the signal and the later adjusted return. The result is the average over groups, with a 95% interval from 10,000 bootstrap draws of whole groups, seed 307 |
| Main test | Signal 1 at 63 days: more change is followed by lower returns, so the average correlation must be negative with its interval clear of zero. Lazy Prices found this; this checks it in our data |
| Jev's test | Does Jev's "worse" share add to word counting? Within each group, the correlation of Signal 4 with the 63-day return minus that of Signal 3, on the same filings. Jev adds something only if the average difference is negative with its interval clear of zero |
| Also reported | Every signal at every window; the top-fifth against bottom-fifth return gap per group; each signal by year; how many filings each signal covers per year and per SIC division |
| What a pass leads to | A signal that holds here is a candidate feature for MCI-GRU or a standalone screen, then gets an out-of-sample check on later filings. A fail is reported as a fail |
| Cost | Jev only on flagged risks: about 90,000 calls at most, roughly $6 at the cost seen so far, inside the $8 the owner set aside on 16 Oct. Prices: one EODHD call per ticker |

**Known limits, accepted now:** SPY adjustment only, with no size, value or industry controls; S&P 500 members only; SIC codes are today's, not dated; delisting payouts are missing.

## Open before this can start

- **Parser findings, decided 16 Oct 06:12Z (before any return is looked at):** the first full read (593 companies, 6,115 member 10-Ks) flagged 802 member reports (13%) in 168 companies, concentrated in banks, utilities and old industrials, so leaving them out would bias the sample by sector. Decision: one bounded fix pass on the common kinds, a rerun from the cache, then whatever is still flagged is left out and recorded per year and sector. The whole Item 1A text is kept for every report where it was found, with a flag for whether its split into risks passed, so the overall similarity signal covers more reports than the per-risk signals. Each signal's test reports how many filings it covers per year.
- **After the fix pass (Data lane, 16 Oct 08:39Z):** 438 of 6,115 member reports (7.2%; 5.8% to 8.9% in every year) have no usable risks. By current SEC industry: finance 12.6%, mining 11.0%, transport and utilities 9.7%, manufacturing 6.3%, services 3.4%, retail 0.9%. The whole Item 1A is kept for 5,963 (97.5%), so the overall similarity signal covers nearly every filing. A new check (`section_text_not_in_risks`) now catches reports whose risks silently hold under 70% of the section's words; E5's, E9's and Alphabet's files reproduce byte for byte with no findings under it.
- **Signals 1 to 3 frozen (16 Oct 10:16Z, Questions lane, commit bcaed08, before any Jev call or return):** `signals/report_signals.csv` sha256 1e699aa7…574a, `signals/risk_pairs.csv` e55a1192…72a5. Signal 1 covers 6,718 member reports, Signals 2 and 3 cover 6,331. 183,233 risk pairs: 8,343 new and 80,597 flagged (new included). Risks pair report to report through the pair partner (the same top-one TF-IDF match), not by fiscal year, as the card intends. Signal 4 on the 80,597 flagged risks costs about 121M input tokens, about $5.
- **Prices published (16 Oct 10:10Z, nothing joined to filings):** `data/e7_prices/`, SPY plus 803 symbols, daily 2012-12-03 to 2026-10-15, EODHD adjusted closes. 812 of 818 ticker runs cover their membership spell, and reused tickers are mapped to the right company (50 runs use a symbol other than the plain ticker). Covidien and the old DuPont have no usable prices, so their filings are left out of the return test and recorded.
- **Joins checked before any return was looked at (16 Oct 10:30Z, Lead's script, counts only):** of 6,943 member reports, 6,871 have all three return windows. Left out: 52 whose 6-month window has not ended, and 20 with no usable price: old DuPont 2013–2017, Covidien 2013–2014, Alcoa/Howmet 2013–2016, Ingersoll-Rand 2013–2017, 21st Century Fox 2016–2018 and Rockwell Collins 2018. Signal 1 covers 6,650 of them and Signals 2 and 3 cover 6,266. Quarters form 43 groups of 30 to several hundred filings. 73 stocks stop trading inside the 6-month window and earn SPY's return after their last close.
- **Signal 4 scored and two rules added (16 Oct 10:58Z, before any return was looked at):** Jev answered all 80,596 flagged risks (116.2M input tokens, about $4.88; `jev/worse_share.csv` sha256 6a560cd3…c98b, commit b5c4b96). Alexion's fiscal 2020 10-K is left out of Signal 4: its section came through as one 200,000-character risk, over Jev's limit. Second, the Questions lane found 70 reports with 3 or fewer risks that passed every check but look like headings or whole sections read as one risk. So Signals 2 to 4 now use only reports where both the report and its pair partner have at least 5 risks. That removes 126 of 6,331 reports. Signal 1 is unaffected.
- **Added 16 Oct 04:38Z, after E10 passed:** Jev's 8-K event rating is a second candidate signal, for returns over the days and weeks after each event, against the item code alone. It needs the S&P 500's 8-Ks pulled too (free) and its own frozen design before any return is looked at; the Lead will card it separately once the 10-K pull is in.

- The owner's choice on the decision card.
- An EODHD key or another daily-price source for about 500 tickers, 2014 to 2026.
- ~~A point-in-time S&P 500 membership list~~: decided 16 Oct 03:50Z (see Membership); the Data lane is pulling.
- ~~Whether EODHD carries delisted US tickers~~: yes (checked 16 Oct 04:16Z, `data/e7_prep/eodhd_check.md`). Delisted CELG and TWX return prices, and the delisted symbol list has 60,432 symbols.

## Result

**Graded 16 Oct 11:05Z. Verdict: fail on both tests.** In the S&P 500 from 2013 to 2026, how much a company's 10-K risk section changed tells us nothing about its stock's next 1, 3 or 6 months, and Jev's "worse" share adds nothing clear over word counting.

Graded by the Lead from the frozen files (`signals/report_signals.csv` 1e699aa7…, `jev/worse_share.csv` 6a560cd3…, `data/e7_prices/`) with the Lead's own script; numbers in `grading/summary.json`, each filing in `grading/graded_filings.csv`. 6,871 filings in 43 quarter groups; 10,000 bootstrap draws of whole groups, seed 307. One return was rechecked by hand (Apple, filed 30 October 2013: −5.7% against SPY over 63 days), and the correlations a second way, pooled over all filings.

| Signal, 63 trading days (about 3 months) | Average rank correlation with later return | 95% interval | Filings |
|---|---|---|---|
| **Main: 1. Whole risk section changed (Lazy Prices)** | +0.004 | −0.034 to +0.044 | 6,650 |
| 2. Share of new risks | +0.010 | −0.025 to +0.045 | 6,141 |
| 3. Share of changed risks | −0.004 | −0.045 to +0.036 | 6,141 |
| 4. Jev's "worse" share | −0.021 | −0.067 to +0.023 | 6,141 |
| **Jev's test:** Signal 4 minus Signal 3 | −0.016 | −0.034 to +0.002 | 6,141 |

- **Main test:** Lazy Prices predicts a negative correlation. Here it is +0.004, with an interval spanning zero. The top fifth of changers did 0.5 points better than the bottom fifth over 3 months, not worse (−1.0 to +2.0).
- **Jev's test:** the difference points the right way (Jev's share is slightly more negative than the changed share), but the interval just reaches zero, so it is not clear. At 1 month the difference is +0.014, and at 6 months −0.005, so there is no steady pattern.
- **1 and 6 months:** every signal at every window has an interval spanning zero. The largest is Jev's share at 6 months, −0.023 (−0.069 to +0.018), with the top fifth 1.3 points behind the bottom fifth (−3.0 to +0.3).
- **By year:** correlations swing between about −0.10 and +0.11 with no sign that holds year after year.

**Why this may differ from Lazy Prices:** they studied all US stocks from 1995 to 2014, held portfolios for months and found the effect strongest in smaller firms and in years before it was published. This test covers only S&P 500 companies from 2013, after publication, which are the most watched stocks. It does not say the effect never existed. It says it is not in this sample.

**Caveats:** SPY adjustment only, with no industry, size or value controls; S&P 500 members only; 13 years of quarters. A small effect, a correlation of about 0.02, could hide inside these intervals.

**What it leads to:** 10-K risk-section changes, read by words or by Jev, do not give a return signal for large US stocks over 1 to 6 months. The better chance for Jev is news that is fresh when filed: the 8-K events of E10, measured over the days just after each filing.

**Two data findings after grading (Data lane, 16 Oct 11:31Z), judged not to change the verdict:**

1. **Acceptance times:** SEC's submissions files list some filers' acceptance times 4 to 5 hours late (JPMorgan's 8-K of 9 January 2013: 16:56 Eastern by its own index page, listed as 02:56 UTC the next day). Listed times are only ever later than the truth, so a return window may start one trading day late but never before the filing was public. A one-day shift in a 63-day window cannot turn a correlation of +0.004 into a clear effect.
2. **Hand-overs in the member table:** 9 reports were counted as members that were not (ACE under CB 2012–14, Tyco under JCI 2013–15, Gardner Denver under IR 2017–19), and 5 member reports were missed (21st Century Fox 2013–15, Walgreen 2013–14). That is 14 of 6,871 filings. The table is now fixed for later pulls; E7 is not rerun.

