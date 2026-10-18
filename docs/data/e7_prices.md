# E7 daily prices (EODHD), pulled 2026-10-16

Daily prices from 2012-12-01 to 2026-10-15 for SPY and every ticker run in
`../e7_sp500_10k/membership/sp500_ticker_runs.csv` (818 runs, 802 tickers),
delisted names included. The pull used read-only GET calls, about 1,420 for prices
and 2 for symbol lists. Nothing here is joined to a filing or a signal. Returns are computed only at
grading, per `../../experiments/E7-returns/CARD.md`.

## Files

| File | What it is |
|---|---|
| `price_runs.csv` | One row per run: the EODHD symbol used, its name in EODHD's symbol list, a name check, the first and last price date, whether the series covers the run's membership spell, gaps, other candidates and a note. |
| `daily_prices.csv.gz` | All 803 symbols used plus SPY, in long form: `symbol,date,open,high,low,close,adjusted_close,volume` (2,370,243 rows). Open, high, low and close are raw. `adjusted_close` covers splits and dividends. |
| `raw/<SYMBOL>.US.json.gz` | EODHD's `/api/eod` response, byte for byte (gzipped), for each symbol used, plus 5 reference-only series named in the notes. |
| `symbol_list_US_active.json.gz`, `symbol_list_US_delisted.json.gz` | EODHD `/api/exchange-symbol-list/US`, with and without `delisted=1`, as returned. |
| `vendor_body_sha256.csv` | SHA-256 of each vendor response before gzip. |
| `SHA256SUMS` | SHA-256 of every file in this folder. |
| `pull_prices.py` | The script that made it, published here as `scripts/data/pull_eodhd_prices.py` (key from `EODHD_API_KEY`). |

## How a symbol was chosen

Tickers get reused, so a run's ticker is not trusted on its own. For each run the
candidates were the ticker itself, EODHD's renamed delisted codes (`T_old`,
`T_old1`.., `T1`..) and any common stock whose listed name matches the run's
names. Each candidate's series was fetched. The pick favours, in order, a name
match, coverage of the membership spell (from the later of the run start and
2012-12-01, to the run end or the latest day, with 7 days' slack each side), and
then the closeness of the name. Of the 50 runs that needed a symbol other than the
plain ticker, examples are `POM_old` (Pepco), `SE1` (Spectra Energy), `DOW_old`
(Dow Chemical), `FB_old` (Facebook) and `CSC` (Computer Sciences for the old DXC
run).

`name_check` takes four values:
- `pass` (798 runs): every word of the shorter name appears in the other, after
  dropping words like Inc, Corp and Holdings.
- `reviewed` (18): checked by hand, with the reason in `note`. These cover initials
  (A. O. Smith, D. R. Horton), renames (Mylan, Federated Hermes, Labcorp) and
  reused or mislabelled symbols:
  - BB&T is `BBT_old`, because `BBT.US` is now Beacon Financial.
  - Mallinckrodt is `MNK_old`. EODHD's list labels it a Muniholdings fund, but
    its prices are Mallinckrodt's.
  - Paramount Skydance is `SKYD`. `PSKY.US` is the same series but stops on
    2026-10-05.
  - Baker Hughes is `BKR`, which carries Baker Hughes Inc's prices to 2017-07-03.
- `missing` (2): no usable series.
  - Covidien (COV, 2011-2015): EODHD has no rows for it.
  - E. I. du Pont (DD, 1996-2017): `DD.US` before 2017-09-01 holds Dow Chemical's
    prices. The pre-merger values in `DWDP.US` match neither company, so neither
    series was used.

## Spell coverage

812 of 818 runs are covered from start to end. The 6 that are not:
- **The two `missing` runs** (COV, DD 1996-2017).
- **FOX, FOXA and IR.** The run's SEC company was listed later than the run's
  start (Fox Corp on 2019-03-12/13, Ingersoll Rand Inc on 2017-05-12). The ticker
  earlier belonged to a different company: 21st Century Fox is `FOX1`/`FOXA1`, and
  Ingersoll-Rand plc is `TT`. Only the run's own CIK's prices are used, so 10-Ks
  from before those dates should have no price here.
- **ARNC (CIK 4281, Alcoa Inc → Arconic Inc → Howmet).** EODHD has no Alcoa Inc
  prices before 2016-11-01. `ARNC_old` runs from 2016-11-01 to 2020-03-31, and the
  same company continues as `HWM.US` from 2020-04-01. Raw prices step across that
  date because of the Arconic Corp spin-off.

Gaps: only DO and NE have a gap over 6 calendar days inside their spell (10 days
each). Delisted series end on their last trade. Some end on a stale row
(open = high = low = close, small volume), for example TWX on 2018-06-15.

## Caveats for grading

- `adjusted_close` is EODHD's own and was not cross-checked here. BKR steps on
  2017-07-05 because of the Baker Hughes / GE special dividend.
- A few symbols carry a predecessor's history under the successor's name, for
  example `VIAC` (CBS), `CCE` (Coca-Cola Enterprises, then CCEP) and `BKR`. The
  name check passes them because the run names the same company.
- The 26 runs marked "no 10-K while a member" were pulled too.
