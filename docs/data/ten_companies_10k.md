# Ten companies' 10-K risk factors, r1 (E5)

Item 1A risk factors from every 10-K for fiscal 2013 to 2025 of JPMorgan Chase
(`jpm`), Delta Air Lines (`dal`), Exxon Mobil (`xom`), Pfizer (`pfe`), Walmart
(`wmt`), Boeing (`ba`), Microsoft (`msft`), Coca-Cola (`ko`), UnitedHealth
(`unh`) and Caterpillar (`cat`): 13 filings each, 130 in all, 3,455 risks.

- Manifest: `../ten_companies_10k_risk_factors.r1.json` (60 files, SHA-256 each).
- Files per company under `filings/`, named by its key, in the same shape as
  Alphabet's r1: `<key>_risk_factors.jsonl` (one risk per line: `risk_id`,
  `accession_number`, `fiscal_year`, `index`, `category`, `heading`, `body`),
  `<key>_10k_index.csv`, `<key>_10k_duplicates.csv`, `<key>_extraction_report.csv`,
  `<key>_extraction_checks.csv` (all empty) and `<key>_risk_factors.meta.json`.
- `risk_id` is `<accession number>#<position>`, unique across all companies and
  fixed for a given filing and parser.
- Produced by `scripts/data/export_sec_risk_factors.py` on branch
  `claude/project-thread-abwj2s` at commit e7ea527 (issue #297), User-Agent
  "Your Name you@example.com".

## What to know when reading it

- Fiscal year is the year of the period of report (the rule is in the manifest's
  metadata, and each company's meta file maps fiscal year to period end). Each
  company has exactly one 10-K per fiscal year 2013-2025, so a filing's prior
  year is always its previous filing. Walmart's year ends in
  January, so its fiscal 2025 report covers February 2024 to January 2025.
  Microsoft's ends in June.
- Exxon Mobil heads each risk with a short italic lead ("Economic conditions."),
  so its headings are short topics, not sentences. Each category's own
  introductory paragraph is not part of any risk. Its 2025 report was filed by
  the new holding company (a second CIK); one copy per report is kept.
- Microsoft puts titled sub-headings inside each risk; they stay in the risk's
  body. Its categories are the capitals lines ("GENERAL RISKS").
- Boeing's umbrella risks hold run-in sub-points; those stay in the umbrella
  risk's body rather than becoming risks of their own.
- JPMorgan restructured Item 1A in its fiscal 2017 report (about 20 risks
  before, 41 to 52 after). That is the filing, not the parser.
- Pfizer heads some risks with topic titles ("Outsourcing") rather than
  sentences.
- Risk summaries, cautionary statements and forward-looking-statement
  preambles are left out.

Every filing passes the six extraction checks in `mci_gru/filings/checks.py`.
An independent reading with lxml matched each company's text word for word
except page furniture (page numbers, running headers and footers, "Table of
Contents", "Part I") and Exxon's category introductions.
