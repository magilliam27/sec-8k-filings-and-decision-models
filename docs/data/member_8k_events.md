# S&P 500 members' 8-K events, r1 (for E11)

Every original 8-K (8-K/A amendments left out) carrying any of items 1.01, 1.02,
1.03, 2.01, 2.05, 2.06, 3.01, 4.01, 4.02 or 5.02, accepted from 1 January 2013
to 15 October 2026 on a day the company was an S&P 500 member: **28,253 events
from 752 companies**, with **232 more left out** because a check failed (0.8%).
E10's contract throughout: same items, same text rules, same context fields.
No prices and no Jev scores are in this folder (E11's blind wall).

| year | events | 1.01 | 1.02 | 1.03 | 2.01 | 2.05 | 2.06 | 3.01 | 4.01 | 4.02 | 5.02 | left out | share left out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2013 | 2,069 | 657 | 76 | 0 | 74 | 50 | 35 | 5 | 6 | 2 | 1,308 | 37 | 1.8% |
| 2014 | 2,098 | 685 | 72 | 0 | 82 | 34 | 22 | 4 | 14 | 2 | 1,317 | 19 | 0.9% |
| 2015 | 2,267 | 874 | 105 | 0 | 109 | 53 | 26 | 15 | 1 | 0 | 1,305 | 36 | 1.6% |
| 2016 | 2,132 | 743 | 94 | 0 | 95 | 48 | 23 | 10 | 7 | 3 | 1,298 | 22 | 1.0% |
| 2017 | 2,115 | 741 | 71 | 2 | 86 | 33 | 19 | 9 | 8 | 2 | 1,288 | 19 | 0.9% |
| 2018 | 2,130 | 672 | 101 | 1 | 85 | 35 | 16 | 20 | 5 | 3 | 1,359 | 10 | 0.5% |
| 2019 | 2,063 | 705 | 85 | 0 | 74 | 30 | 15 | 18 | 3 | 2 | 1,288 | 26 | 1.2% |
| 2020 | 2,242 | 846 | 82 | 0 | 58 | 44 | 22 | 8 | 6 | 2 | 1,317 | 24 | 1.1% |
| 2021 | 2,124 | 789 | 103 | 0 | 72 | 17 | 11 | 9 | 1 | 1 | 1,285 | 7 | 0.3% |
| 2022 | 1,868 | 573 | 75 | 0 | 46 | 13 | 11 | 14 | 2 | 2 | 1,259 | 6 | 0.3% |
| 2023 | 1,841 | 581 | 66 | 1 | 33 | 30 | 10 | 12 | 3 | 1 | 1,207 | 7 | 0.4% |
| 2024 | 1,840 | 594 | 63 | 0 | 36 | 31 | 11 | 16 | 6 | 3 | 1,185 | 5 | 0.3% |
| 2025 | 1,977 | 638 | 90 | 0 | 39 | 34 | 17 | 10 | 5 | 2 | 1,286 | 10 | 0.5% |
| 2026 | 1,487 | 499 | 65 | 0 | 41 | 25 | 6 | 10 | 5 | 1 | 963 | 4 | 0.3% |
| **all** | **28,253** | **9,597** | **1,148** | **4** | **930** | **477** | **244** | **160** | **72** | **26** | **17,665** | **232** | **0.8%** |

Year is the year of `accepted_utc`. Item columns count events carrying that
item; 1,758 events carry two or more of the ten, so they sum to 30,323. 2026
runs to 15 October. Members by release: r1 24,467 events, r2 3,786 (the E7
split; `release` on each event).

## Files

- Manifest: `../member_8k_events.r1.json` (4 files, SHA-256 each).
- `member_8k_events.jsonl` (203 MB): one event per line, keyed by `event_id`
  (the accession number). E10's fields in E10's order: `event_id`, `company`
  (member key), `company_name`, `items`, `event_items`, `text` (at most 20,000
  characters), `truncated`, `prior_revenue_usd`, `prior_revenue_fiscal_year`,
  `prior_revenue_concept`, `prior_revenue_period_end`, `prior_10k_accession`,
  `prior_90d_items`, `accepted_utc`, `filing_date`, `cik`, `sections`,
  `press_release`, `document_url`, `document_sha256`. Added for E11:
  - `listed_accepted_utc`: the time SEC's submissions file lists.
  - `accepted_from_index_page`: true when `accepted_utc` came from the
    filing's index page (true for all 28,253).
  - `nearby_202_listed_utc`: listed times of the same company's other 8-Ks
    carrying item 2.02 (earnings) within 5 Eastern calendar days either side
    of the event's own Eastern day; empty when none (3,431 events have one).
  - `release` (r1 or r2) and `sic` (SEC's current SIC code, not dated; 31
    events have none).
- `member_8k_left_out.csv`: the 232 left-out events, with `event_id`,
  `company`, `cik`, `accepted_utc`, `year`, `items` and `reason`.
- `member_8k_checks.csv`: every check finding (254 findings on the 232).
- `member_8k_events.meta.json`: provenance and counts, including events by
  item, by year, by year and item, and the share left out per year.
- `membership/`: the member table the pull read (v2, 753 companies), its
  ticker runs, the manual name rows and its build record. This is a corrected
  version of `../e7_sp500_10k/membership/`; see "Member table" below.
- Produced by `scripts/data/export_sec_member_8k.py` in the MCI-GRU repository at commit e502416 (issue magilliam27/MCI-GRU#311, pull request
  magilliam27/MCI-GRU#300), User-Agent "Your Name you@example.com". Documents were downloaded on
  16 October 12:36Z to 14:00Z (37,860 requests) and the final run re-read them
  from that cache at 14:10Z.

## Acceptance time: read this before computing day 0

`accepted_utc` is the "Accepted" time on the filing's own index page (EDGAR's
Eastern clock, converted to UTC). SEC's submissions files, which E10 used,
list some filers' times 4 to 5 hours late: JPMorgan's 8-K accepted 16:56
Eastern on 9 January 2013 is listed at 02:56 UTC on 10 January, which would be
after the 17:30 cut-off its filing date shows it beat. The two times differ for
**12,594 of the 28,253 events** (JPMorgan, Delta, Pfizer, Walmart, Microsoft,
UnitedHealth, Apple, Caterpillar and many more). Both are kept:
`listed_accepted_utc` is SEC's listed time. No event fell back to the listed
time (`acceptance_from_listing_only` 0 in the meta).

Membership is judged on the Eastern day of the index-page time. 66 8-Ks
inside a spell by their listed time fall outside by their index-page time and
are not events (`outside_membership_by_index_page` in the meta).

## What the checks cover, and what was left out

Every event: each listed item other than 9.01 has a section in the document;
no section is empty; a press release found is not empty; the document and
index page read; no event id repeats. An event with any finding is left out
(`--leave-out-flagged`), not repaired. The 232 left out, by reason:

| reason | events |
| --- | --- |
| a listed item has no section in the document | 167 |
| an item section is empty | 57 |
| the press release reads empty | 6 |
| both of the first two | 2 |

By year (in the table above) the share left out is 1.8% at most (2013) and
0.3% from 2021. The left-out events were not inspected one by one. The
companies with most left out: MetLife 15, Cincinnati Financial 12, Humana 10, Cencora 8,
Weyerhaeuser 8.

Two heading layouts were found in a first run and fixed before this one
(commit e502416), which recovered 339 events: an item heading followed straight
by another item's heading over one shared text (Fifth Third heads "Item 1.01"
and "Item 2.03" over one account of a deal), and an item number run into its
title with no space (Agilent's "Item 5.02Departure of Directors"). The text
rules are unchanged; E10's ten companies export byte for byte as before.

## Member table

The pull reads member table v2, built after a fix to how a ticker passes
between two companies:

- A company that took over a ticker now holds only its own part of the run.
  Before, ACE, Tyco and GDI counted as members for years before they held
  their tickers.
- Twenty-First Century Fox (FOXA before 2019) and Walgreen Co. (before
  Walgreens Boots Alliance) are now in, through name-only manual rows.

**Apache is left out for 2013 to early 2021.** APA's ticker run is matched to
APA Corp (CIK 0001841666), the holding company formed in March 2021; Apache
Corporation (CIK 0000006769) held the ticker before that and kept filing
afterwards as APA Corp's subsidiary, so the hand-over rule cannot date the
change from its filings. A more general rule that would have caught it gave
wrong spans for Marathon Petroleum and O-I Glass, so it was not used. APA's events here start in January 2022
(25 events). The research lead agreed to leave Apache's earlier years out.

## What to know when reading it

- **Same text rules as E10.** Item sections run from an "Item N.NN" heading
  (or an emphasised bare "N.NN Title") to the next item or the signature; item
  9.01 text is dropped; the press release is exhibit 99.1, or a lone
  unnumbered 99. Exhibits 99.2 and later and agreements are not read.
- **Text past 20,000 characters is cut** (2,031 events, `truncated` true).
  Item sections come first, so most cuts shorten only the press release.
  10,855 events carry a press release.
- **Revenue** is total revenue as tagged in XBRL by the latest 10-K accepted
  before the 8-K, for that 10-K's own fiscal year. 1,516 events have none
  (no earlier 10-K, or none of E10's six revenue concepts tagged).
- **Items 2.02, 7.01 and 8.01 are not events**, but an event listing them
  keeps them in `items`. 854 events also list 2.02 (E11 leaves these out of
  its test).
- **One company, several CIKs.** An event's `cik` is the filer that made it;
  `prior_90d_items` and `nearby_202_listed_utc` look across all the
  company's CIKs in the member table.
- **Companies with no events:** Interactive Brokers (ibkr), a member only
  since 28 August 2025, filed no 8-K with any of the ten items since.
- Text length: median 4,322 characters, shortest 150.
