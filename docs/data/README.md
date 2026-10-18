# Dataset notes

Each file here is the README of one dataset the experiments used, copied from
the original research folder. The datasets themselves (SEC filing texts, risk
factors, 8-K events, daily prices) are **not** in this repository: some are
hundreds of megabytes, and the prices come from a paid vendor. The notes say
what each dataset holds, how it was pulled, which checks it passed, and the
manifest hashes, so a rebuild with the scripts in `scripts/data/` can be checked
against them. The SEC User-Agent shown is a placeholder.

| Note | Dataset | Used by |
|---|---|---|
| [ten_companies_10k.md](ten_companies_10k.md) | 10-K risk factors of 10 large companies, FY2013 to FY2025 | E5, E8 |
| [e9_ten_companies_10k.md](e9_ten_companies_10k.md) | 10-K risk factors of 10 fresh companies | E9 |
| [e10_8k_events.md](e10_8k_events.md) | All 436 qualifying 8-Ks of E5's 10 companies | E10 |
| [e7_sp500_10k.md](e7_sp500_10k.md) | S&P 500 member 10-Ks and their risk factors, 2013 to 2026 | E7 |
| [e7_prep.md](e7_prep.md) | Membership and price-source preparation | E7 |
| [e7_prices.md](e7_prices.md) | EODHD daily adjusted closes, SPY plus 803 symbols | E7, E11 |
| [member_8k_events.md](member_8k_events.md) | S&P 500 members' 8-K events, 2013 to 2026 | E11 |
