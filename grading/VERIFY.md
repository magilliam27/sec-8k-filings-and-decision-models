# Verification pack: E7, E9, E10, E11

> **Note for this repository.** This pack was written for the original research folder ("this share" below), which holds the bulk data, the sealed answer keys and Jev's per-filing answers. None of those are published here: the filings can be rebuilt from SEC EDGAR, the prices need an EODHD subscription, and Jev's per-filing ratings (`jev/scores.csv` and `jev/answers/`) are not published. Their sha256 hashes are listed below, so a rebuilt copy can be checked against them. The scripts are in `grading/scripts/`; point `FILINGS` at a folder laid out like that original tree (`data/`, `experiments/<id>/jev/`, `experiments/<id>/grading/`, `experiments/<id>/labels/sealed/`). The frozen E10 and E11 baseline and join files are copied in `results/`; run without the research tree, `python3 grading/scripts/check_hashes.py` checks those copies against the stated hashes and lists the rest as not available. The only edits to the pack for publication are its default paths (now `./filings` and `./verify_out`) and the source-repository link. Code paths that name `mci_gru/filings/` refer to the module now at `src/sec8k/`; the frozen YAML question files keep the old name, since editing them would change their hashes.

Checked 17 Oct 2026, 03:30–03:50Z. Everything here reads the frozen files under the research tree `$FILINGS` (the original shared `filings/` folder; its bulk data is not in this repository) and writes only to a scratch folder (`VERIFY_OUT`, default `verify_out/<exp>/`). Each script asserts that its output folder is not inside `filings/experiments/`, so a rerun cannot overwrite a published `grading/` file.

## Scripts (`scripts/`)

The Lead's grading scripts, copied with their statistical logic unchanged. The only edits are a path header (`F` = filings root from `$FILINGS`, `OUT` = output folder from `$VERIFY_OUT`). `save` mode writes to `OUT` and no longer to `grading/`. In E11, the chain's `events.pkl` and `joined.pkl` also go to `OUT`, not to the Lead's scratchpad.

| Script | What it does |
|---|---|
| `e11/events_e11.py` | Reads `data/member_8k_events/member_8k_events.jsonl` (28,253 events), assigns item groups and flags (2.02, nearby earnings, press release), and converts acceptance times to US Eastern. Writes `OUT/events.pkl` |
| `e11/join_e11.py` | Maps each event to a price symbol through the member table and `data/e7_prices/price_runs.csv`, finds day 0 (the first close after acceptance), and checks the day −1 price and the 10-day window. Writes `OUT/joined.pkl` and prints the join counts and the test set (26,962) |
| `e11/grade_e11.py` | Grading as frozen on the E11 card: SPY-adjusted returns, item-group-by-year cells, cell-bootstrap Spearman (10,000 draws, seed 311), robustness checks, month-bootstrap means and patterns. Modes: `check`, `grade`, `save` |
| `e11/grade_e11_v1.py` | The first version, which produced the original `summary.json` (now `grading/summary_v1.json`, 4d84b3de; in this repository `results/E11-8k-returns/summary_v1.json`). It is kept so that file can be reproduced |
| `e12/grade_e12.py` | E12 (next open): reads E11's `grading/graded_events.csv` and `data/e7_prices/daily_prices.csv.gz`, enters at the first open after acceptance, and grades the 2- and 5-session returns as frozen on the E12 card (seed 312). Modes: `check`, `grade`, `save`. Its `summary.json` (20b8f5a8…) is in `experiments/E12-next-open/grading/` |
| `e7/grade_e7.py` | Grading as frozen on the E7 card: filing-to-price joins, quarter groups, rank correlations at 21, 63 and 126 days, Jev against the changed share (10,000 draws, seed 307). Modes: `counts`, `grade`, `save` |
| `e10/grade_e10.py` | E10: design-weighted AUC of Jev against the baseline on the sealed AI key (10,000 draws within company × group, seed 310). It does not import `lib/e10_events.py`, so that file is not copied |
| `e9/grade_e9.py` | E9: the same AUC test on direction of change (seed 309) |
| `check_hashes.py` | Recomputes sha256 for every hash a card states, and every full hash in the data manifests, the Jev `meta.json` files and `data/e7_prices/SHA256SUMS`. Read only |
| `compare_json.py` | Compares a rerun against a published `summary.json`: byte hash, then field by field. It also accepts a `grade` stdout log |

## Commands

```bash
P=grading/scripts; export FILINGS=/path/to/filings; G=$FILINGS/experiments
export VERIFY_OUT=verify_out/e11      # E11 end to end, about 5 min
python3 $P/e11/events_e11.py && python3 $P/e11/join_e11.py && python3 $P/e11/grade_e11.py save
python3 $P/compare_json.py $G/E11-8k-returns/grading/summary.json $VERIFY_OUT/summary.json
VERIFY_OUT=verify_out/e7 python3 $P/e7/grade_e7.py grade > verify_out/e7.log   # under 1 min
python3 $P/compare_json.py $G/E7-returns/grading/summary.json verify_out/e7.log
VERIFY_OUT=verify_out/e10 python3 $P/e10/grade_e10.py save   # any argument means save
VERIFY_OUT=verify_out/e9  python3 $P/e9/grade_e9.py save
python3 $P/check_hashes.py                 # about 4 min, hashes about 1.2 GB
```

## Rerun results

| Experiment | Rerun | Result |
|---|---|---|
| **E11** v2 (current) | events → join → `grade_e11.py save` | `summary.json` **byte-identical** to the published file: sha256 6f8455ce…afd5 (mtime 03:41:55Z, the Lead's corrected save; unchanged at 03:47Z). `graded_events.csv` also identical (2c446e6d…028b) |
| E11 v1 | the same chain with `grade_e11_v1.py` | Byte-identical to the original `summary.json` (4d84b3de…84d2, now `summary_v1.json`) and `graded_events.csv` (a50e5527…c1a6). `events.pkl` and `joined.pkl` equal the Lead's (joined byte-identical) |
| E11 join counts | `join_e11.py` stdout | As on the card: 28,063 joined; 93 with no day −1 price, 63 with the window not ended, 34 with no series; 848 listing 2.02; 253 duplicates; **26,962** test events (officer 16,263, deals 8,953, negative 1,678, auditor 68) |
| **E7** | `grade` mode (not `save`) | All 207 numeric fields equal `grading/summary.json`. Main test +0.004 (−0.034 to +0.044); Jev minus changed share −0.016 (−0.034 to +0.002); 6,871 filings in 43 groups, as on the card |
| E10 | `save` to scratch | `summary.json` byte-identical (bfbd9102…0d41); `graded_events.csv` identical |
| E9 | `save` to scratch | `summary.json` byte-identical (aed0f0eb…4917); `graded_risks.csv` identical |

**E11 correction (Lead, 17 Oct 03:38Z, after an independent recheck).** `grade_e11.py` changed in two lines. (1) In `ret()`, a stock whose last price is on or before the window start now earns SPY for the whole window (`if last<=ta: return 0.0`); before, it used its stale price. (2) The patterns' "10-day" interval (`d10_ci`) now ends at day +9 (`p9`) like the headline, not at day +10. Effect, v1 against v2: the main test, the 10-day headline, every robustness test and the top-minus-bottom-fifth gap are unchanged to 4 decimals. `window_drift_5` and `window_drift_10` move by at most 0.0001. Only the `pattern_*` `d10_ci` entries change materially, for example officer change with Jev bad, −0.95% → −0.89% (−1.40 to −0.36). The verdict is unaffected. Any 10-day pattern figure quoted from v1 should be read from the new `summary.json`.

## Hashes (stated on the cards against computed)

| File (under `filings/`) | Stated | Computed | Match |
|---|---|---|---|
| E7 `signals/report_signals.csv` | 1e699aa7…574a | 1e699aa7…574a | yes |
| E7 `signals/risk_pairs.csv` | e55a1192…72a5 | e55a1192…72a5 | yes |
| E7 `jev/worse_share.csv` | 6a560cd3…c98 | 6a560cd3…c98b | prefix yes. The card's suffix drops the last character; the full hash in `jev/jev.meta.json` matches exactly |
| E10 `data/e10_8k_events/8k_events.jsonl` | 4ef25543…0a581 | 4ef25543…0a581 | yes |
| E10 `sample_sheet.csv` | fe13b88b…e6a9 | fe13b88b…e6a9 | yes |
| E10 `events.csv` | 4660e48f…da80 | 4660e48f…da80 | yes |
| E10 `grading/design.csv` | c663706e…6fa | c663706e…66fa | yes |
| E10 `jev/scores.csv` | c71e864f…d6ee | c71e864f…d6ee | yes |
| E10 `jev/baselines.csv` | a122bf9b…3fc0 | a122bf9b…3fc0 | yes |
| E10 `labels/sealed/answer_key.csv` | 35023d07…50e3 | 35023d07…50e3 | yes |
| E11 `data/member_8k_events.r1.json` | f4029460…3bb2 | f4029460…3bb2 | yes |
| E11 `data/member_8k_events/member_8k_events.jsonl` | 04172c9b…931f | 04172c9b…931f | yes |
| E11 `events.csv` | f885c806…0b3b | f885c806…0b3b | yes |
| E11 `grading/joins.csv` | 685fd126…b02 | 685fd126…3b02 | yes |
| E11 `jev/baselines.csv` | 9a6296a9…1bdda | 9a6296a9…1bdda | yes |
| E11 `jev/scores.csv` | eb56f1c8…d05b | eb56f1c8…d05b | yes |
| E11 `jev/answers/rating.jsonl` | 8b3456b9…3bfc | 8b3456b9…3bfc | yes |
| E11 `grading/summary.json` (Lead's save log) | 6f8455ce | 6f8455ce…afd5 | yes |

**Full hashes:** 1,585 of 1,585 match, with no failure. That covers the data manifests (`member_8k_events.r1`, `e10_8k_events.r1`, `e7_member_10k_risk_factors.r1`/`r2`: 21 files including the 428 MB Item 1A file), the Jev `meta.json` files (E11, E10, E7: scores, baselines, the answer caches and all 719 per-company E7 answer files) and `e7_prices/SHA256SUMS` (815 files). One input is not on this share: `lm_dictionary` (147cb24a…), the Loughran-McDonald list in the repo. The cards state no hash for the grading outputs. For E7, E10 and E11, `check_hashes.py` prints them.

## Software

Python 3.13.16, pandas 3.0.5, numpy 2.5.3 (standard library: `json`, `hashlib`, `zoneinfo`). No other packages. Pandas prints a harmless `Pandas4Warning` about `sum(1)` in `grade_e11.py`.

## What an outsider also needs

- **This share's frozen files:** `data/` (events, member tables, `e7_prices/`) and `experiments/E*/` (events, `jev/`, `labels/sealed/`, `grading/design.csv`). Grading needs nothing else and **no new Jev calls**: Jev's answers are cached in `jev/answers/` (E11 `rating.jsonl`, E10 `rating`/`size.jsonl`, E7 one file per company), and `jev/scores.csv` is computed from them.
- **To rebuild the inputs from scratch:** the MCI-GRU source repository, whose filings code this cookbook carries as `src/sec8k/` and `scripts/data/`.
  - Data pulls: `scripts/data/export_sec_member_8k.py` at e502416 and `nearby_202` at 18e9bfb (PR magilliam27/MCI-GRU#300, issue magilliam27/MCI-GRU#311); `export_sec_8k_events` at bc04cc9 (PR magilliam27/MCI-GRU#300, issue magilliam27/MCI-GRU#308); `export_sec_member_10k` at 1f868f3 (issue magilliam27/MCI-GRU#309).
  - Questions lane: `configs/filings/questions_v5.yaml` at 3a1be7f; scoring commits 631301f (E11), 5b62432 (E10), bcaed08 and b5c4b96 (E7).
  - These commits are in the MCI-GRU repository, on the pull requests named above.
- **To repull prices:** an EODHD subscription (`scripts/data/pull_eodhd_prices.py` in this repository, which also writes `price_runs.csv` and `daily_prices.csv.gz`; the raw vendor responses and their hashes are kept in `raw/` and `vendor_body_sha256.csv`). Prices change little, but adjusted closes can be restated, so the frozen `daily_prices.csv.gz` is what the results use.
- **To re-ask Jev:** a TypeSafe API key and `jev-1.13.0`. Repeated calls return slightly different probabilities (see the ledger), so new answers will not reproduce the cached ones exactly.
- **E9 and E10 labels:** the sealed AI keys are on this share. Regenerating them needs the Labelling desk's reviewer runs (`labels/reviewers/`).
