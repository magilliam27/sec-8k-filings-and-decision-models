# E7 preparation: S&P 500 membership sizing (Data lane, 2026-10-16)

Working files for the membership-source proposal sent to the research lead. Not a
published dataset; nothing here has been checked company by company.

- `sp500_historical_components_fja05680_2026-08-18.csv`: dated S&P 500 member
  lists from github.com/fja05680/sp500 (`S&P 500 Historical Components &
  Changes (Updated).csv`), downloaded 2026-10-16, last row 2026-08-18. One row
  per change date: `date`, comma-separated tickers.
- `sec_ticker_mapped_10k_counts.csv`: for each CIK that SEC's current
  `company_tickers.json` gives for a member ticker since 2012-12-28: CIK,
  tickers, SEC name, fiscal 2013-2025 10-K count, most 10-Ks in one fiscal
  year. No header.
- `unmapped_tickers.txt`: the 183 member tickers SEC's current file does not
  list (acquired, delisted or renamed companies).

Known mapping errors from ticker reuse (to fix by name): POM (Pepco Holdings,
now another company's ticker), SE (Spectra Energy, now Sea Ltd), XOM (needs
both Exxon CIKs, as in E5).
