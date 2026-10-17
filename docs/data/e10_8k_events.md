# 8-K events with filing-time context, r1 (E10)

Every original 8-K (8-K/A amendments left out) filed 1 January 2013 to 31
December 2025 by E5's ten companies that carries any of items 1.01, 1.02, 1.03,
2.01, 2.05, 2.06, 3.01, 4.01, 4.02 or 5.02: 436 events, 0 check findings.

| key | events | 1.01 | 1.02 | 2.01 | 2.05 | 2.06 | 3.01 | 5.02 | text cut | with press release |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| jpm | 40 | 0 | 0 | 0 | 0 | 0 | 0 | 40 | 3 | 16 |
| dal | 54 | 23 | 1 | 0 | 0 | 2 | 0 | 30 | 3 | 28 |
| xom | 33 | 1 | 2 | 1 | 0 | 1 | 0 | 29 | 1 | 7 |
| pfe | 43 | 7 | 1 | 2 | 3 | 0 | 0 | 32 | 8 | 30 |
| wmt | 25 | 1 | 0 | 0 | 0 | 0 | 1 | 23 | 1 | 17 |
| ba | 72 | 29 | 0 | 0 | 0 | 0 | 0 | 43 | 1 | 37 |
| msft | 31 | 1 | 0 | 2 | 1 | 0 | 0 | 27 | 0 | 13 |
| ko | 47 | 0 | 0 | 0 | 1 | 0 | 0 | 47 | 0 | 32 |
| unh | 40 | 4 | 0 | 1 | 0 | 0 | 0 | 35 | 1 | 18 |
| cat | 51 | 15 | 1 | 0 | 2 | 1 | 0 | 32 | 6 | 21 |
| **all** | **436** | **81** | **5** | **6** | **7** | **4** | **1** | **338** | **24** | **219** |

Item columns count events carrying that item; 6 events carry two of the ten, so
they sum to 442. No 8-K in range carries 1.03 (bankruptcy), 4.01 (auditor
change) or 4.02 (restatement).

- Manifest: `../e10_8k_events.r1.json` (3 files, SHA-256 each).
- `8k_events.jsonl`: one event per line, in the Questions lane's format:
  `event_id` (the accession number), `company` (key), `company_name`, `items`
  (every item EDGAR lists, never empty), `text` (at most 20,000 characters),
  `prior_revenue_usd`, `prior_revenue_fiscal_year`, `prior_90d_items` (a list
  of lists, oldest first). Extra fields: `truncated`, `accepted_utc`,
  `filing_date`, `event_items` (the listed items among the ten),
  `prior_revenue_concept`, `prior_revenue_period_end`, `prior_10k_accession`,
  `sections` (item codes of the sections read, in order), `press_release` (its
  file name, or null), `cik`, `document_url`, `document_sha256`.
- `8k_events_checks.csv`: check findings (empty). `8k_events.meta.json`: pull
  provenance and the counts above.
- Produced by `scripts/data/export_sec_8k_events.py` in the MCI-GRU repository at commit bc04cc9 (issue magilliam27/MCI-GRU#308, pull request
  magilliam27/MCI-GRU#300), User-Agent "Your Name you@example.com".

## What the checks cover

Every event: each item EDGAR lists (other than 9.01) has a section in the
document; no section is empty; a press release found is not empty; the
acceptance time parses (true UTC, from EDGAR's submissions file); no event id
repeats. A finding blocks the manifest. Separately, a second reading of every
primary document with a different HTML library matched the item text to within
3 words for all 436.

## What is left out, and why

- **8-K/A amendments.** As asked; they restate an earlier event.
- **Item 9.01 text.** It only lists exhibits. Its code stays in `items`.
- **Exhibits other than the press release.** The text adds exhibit 99.1, or
  the only exhibit 99 when a filing numbers none (12 events, labelled
  "Exhibit 99"). Exhibits 99.2 and later, agreements (10.x) and other exhibits
  are not read. 217 events have no press release.
- **Text past 20,000 characters.** 24 events are cut, `truncated` true. Item
  sections come first, so 21 cuts shorten only the press release. In 3 the
  item text alone passes 20,000 characters, so the text ends inside the items
  and the press release (present in 2 of them) is lost.
- **Items 2.02, 7.01 and 8.01 as events.** Out of this test, but an event that
  also lists them keeps them in `items`, and they count in `prior_90d_items`,
  which lists every original 8-K's items. That is why every event has at least
  one prior 8-K: earnings releases come quarterly.

## What to know when reading it

- **Revenue** is total revenue as tagged in XBRL by the latest 10-K accepted
  before the 8-K, for that 10-K's own fiscal year, with the concept named
  (Revenues 310, RevenueFromContractWithCustomerExcludingAssessedTax 61,
  SalesRevenueGoodsNet 39, SalesRevenueNet 26). JPMorgan's Revenues tag is its
  total net revenue. Fiscal year follows the 10-K rule: the year the period
  ends, except that a year ending in the first week of January is the year
  before (Walmart's year ending 31 January 2024 is fiscal 2024). An 8-K filed in January or February, before that year's 10-K, uses the
  10-K from more than a year earlier (58 events).
- **Sections EDGAR does not list are kept.** A document's item heading that
  EDGAR's list omits is still read (one Caterpillar 2.03; 9.01 is dropped as
  above).
- **Headings vary.** Sections start at an "Item N.NN" line, or at an
  emphasised bare "N.NN Title" line (Caterpillar), and end at the next item or
  the signature. JPMorgan splits one item into several sections ("Item
  5.02(b)", "Item 5.02(d)"); all are kept.
- **Tables** come out as one cell per line, so compensation tables read as
  short lines.
- Text length: median 4,170 characters, shortest 252.
