# Ten more companies' 10-K risk factors, r1 (E9)

Item 1A risk factors from every 10-K for fiscal 2013 to 2025 of Apple (`aapl`),
Home Depot (`hd`), Johnson & Johnson (`jnj`), Bank of America (`bac`), American
Airlines (`aal`), Chevron (`cvx`), Procter & Gamble (`pg`), Honeywell (`hon`),
Verizon (`vz`) and NextEra Energy (`nee`): 127 filings, 3,164 risks.

| key | filings | risks | risks per year |
| --- | --- | --- | --- |
| aapl | 13 | 355 | 26-29 |
| hd | 13 | 291 | 18-25 |
| jnj | 10 (fiscal 2016-2025) | 176 | 12-23 |
| bac | 13 | 386 | 28-31 |
| aal | 13 | 528 | 38-44 |
| cvx | 13 | 152 | 9-15 |
| pg | 13 | 211 | 14-18 |
| hon | 13 | 229 | 13-21 |
| vz | 13 | 175 | 12-18 |
| nee | 13 | 661 | 49-55 |

- Manifest: `../e9_ten_companies_10k_risk_factors.r1.json` (60 files, SHA-256 each).
- Files per company under `filings/`, in the same shape as E5's
  `ten_companies_10k`: `<key>_risk_factors.jsonl` (one risk per line:
  `risk_id`, `accession_number`, `fiscal_year`, `index`, `category`, `heading`,
  `body`), `<key>_10k_index.csv`, `<key>_10k_duplicates.csv`,
  `<key>_extraction_report.csv`, `<key>_extraction_checks.csv` (all empty) and
  `<key>_risk_factors.meta.json`.
- `risk_id` is `<accession number>#<position>`, unique across all companies and
  fixed for a given filing and parser.
- Produced by `scripts/data/export_sec_risk_factors.py` on branch
  `claude/project-thread-abwj2s` at commit 219d9c0 (issue #304, pull request
  #300), User-Agent "Your Name you@example.com". The same code reproduces
  Alphabet's and E5's published risk files unchanged.

## What to know when reading it

- **Johnson & Johnson starts at fiscal 2016.** Its fiscal 2013-2015 reports'
  Item 1A only points to Exhibit 99, which holds the risk factors; those years
  are left out rather than read from a different document. Its meta file
  records this as `note`.
- **Fiscal year** is the year of the period of report, except that a 52- or
  53-week year ending in the first week of January belongs to the year before
  (Johnson & Johnson's fiscal 2015 ended 3 January 2016). Each company has
  exactly one 10-K per fiscal year, so a filing's prior year is always its
  previous filing. Each meta file maps fiscal year to period end.
- **Home Depot's fiscal year here is one more than its own name for it.** Its
  year ends around 1 February, so the report for the year ending 2 February
  2014 (which Home Depot calls fiscal 2013) is fiscal 2014 here, as Walmart's
  are in E5. Apple's year ends in September and Procter & Gamble's in June.
- **American Airlines** is American Airlines Group, which filed as AMR
  Corporation until the December 2013 merger under the same CIK, so one CIK
  covers every year including fiscal 2013.
- **Chevron** heads most risks with an emphasised lead running into the
  paragraph (no punctuation from fiscal 2015), so its headings are short
  claims; it has few risks a year (9-15).
- **Honeywell** from fiscal 2020 lays out its 10-K by topic, with "Item 1A"
  only in an index at the back. Its risks are read from the section titled
  "Risk Factors". Before fiscal 2014 it uses no categories.
- **Bank of America** categories are sometimes a long title-case line ("Market
  Risk is the Risk that Values of Assets and Liabilities ..."), which replaces
  the short title above it ("Market Risk"). Its fiscal 2021 risk summary is
  left out; in that year the first risk's heading begins "Coronavirus Disease"
  because the filing sets the category and heading in one paragraph, so that
  one risk has no category.
- **NextEra** puts an introductory paragraph under each "Risks Relating to ..."
  title; it is not part of any risk.
- Risk summaries, cautionary statements and forward-looking-statement
  preambles are left out.

Every filing passes the six extraction checks in `mci_gru/filings/checks.py`.
An independent reading with lxml matched each company's text word for word
except page furniture (page numbers, running headers and footers, "Table of
Contents") and the category text noted above. That reading caught three
Chevron fiscal 2020 risks (COVID-19 and two on the Noble acquisition) that no
check flagged; the parser was fixed and they are in this release.
