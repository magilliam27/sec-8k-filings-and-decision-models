"""Pull EODHD daily prices for SPY and every S&P 500 ticker run, then assemble them.

Usage, from the repository root:

    EODHD_API_KEY=... python scripts/data/pull_eodhd_prices.py \\
        RUNS_CSV OUT_DIR

``RUNS_CSV`` is ``membership/sp500_ticker_runs.csv`` as written by
``build_sp500_members.py``. Read-only GETs; the key is read from the
``EODHD_API_KEY`` environment variable and never written to disk. Raw responses
are saved byte for byte under ``OUT_DIR/raw/``. The script writes
``price_runs.csv`` (the symbol chosen for each run) and ``daily_prices.csv.gz``
(every chosen symbol plus SPY, long form). Nothing is joined to any filing or
signal. A rerun reuses the raw files already on disk.
"""

import csv
import datetime as dt
import gzip
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RUNS = Path(sys.argv[1]) if len(sys.argv) > 2 else None
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else None
RAW = OUT / "raw" if OUT else None
API = "https://eodhd.com/api"
FROM = "2012-12-01"
PRICE_COLUMNS = ["date", "open", "high", "low", "close", "adjusted_close", "volume"]

GENERIC = set(
    "inc incorporated corp corporation co company companies ltd limited plc the holdings holding "
    "group class a b c common stock new de llc lp l p sa nv ag n v s international intl and of "
    "ordinary shares share trust de del md nj ny the cl".split()
)

# Runs checked by hand (2026-10-16). (ticker, start) -> (symbol or "", name_check, note)
OVERRIDES = {
    ("BBT", "1997-12-04"): ("BBT_old", "reviewed", "BBT.US is now Beacon Financial, a different company; BB&T is BBT_old.US (TFC.US carries the same history)"),
    ("FOX", "2015-09-21"): ("FOX", "reviewed", "Run CIK is Fox Corp, listed 2019-03-13; 21st Century Fox class B (2015-2019) is FOX1.US, a different company"),
    ("FOXA", "2004-12-20"): ("FOXA", "reviewed", "Run CIK is Fox Corp, listed 2019-03-12; 21st Century Fox class A (to 2019-03-12) is FOXA1.US, a different company"),
    ("IR", "2010-11-17"): ("IR", "reviewed", "Run CIK is Ingersoll Rand Inc (ex-Gardner Denver), listed 2017-05-12; the older Ingersoll-Rand plc is TT.US, a different CIK"),
    ("ARNC", "1996-01-02"): ("ARNC_old", "reviewed", "Arconic Inc from 2016-11-01 only; no pre-2016 Alcoa Inc prices in EODHD. Same company continues as HWM.US from 2020-04-01 (raw prices differ: spin-off and reverse split)"),
    ("MNK", "2014-08-19"): ("MNK_old", "reviewed", "EODHD's list names MNK_old a Muniholdings fund, but the prices are Mallinckrodt's (43.50 at the June 2013 spin-off, 0.75 at the 2020 bankruptcy)"),
    ("PSKY", "2025-08-08"): ("SKYD", "reviewed", "EODHD carries Paramount Skydance under SKYD.US to the latest day; PSKY.US is the same series ending 2026-10-05"),
    ("COV", "2011-03-01"): ("", "missing", "No Covidien prices in EODHD (COV.US returns no rows)"),
    ("DD", "1996-01-02"): ("", "missing", "No clean E. I. du Pont series: DD.US before 2017-09-01 is Dow Chemical's prices; DWDP.US pre-merger values match neither company and were not used"),
    ("AOS", "2017-07-26"): ("AOS", "reviewed", "A. O. Smith; initials split the name"),
    ("DHI", "2005-07-05"): ("DHI", "reviewed", "D. R. Horton; initials split the name"),
    ("GWW", "1996-01-02"): ("GWW", "reviewed", "W. W. Grainger; initials split the name"),
    ("CHRW", "2007-03-02"): ("CHRW", "reviewed", "C. H. Robinson; initials split the name"),
    ("JBHT", "2015-07-01"): ("JBHT", "reviewed", "J. B. Hunt; initials split the name"),
    ("GMCR", "2014-03-24"): ("GMCR", "reviewed", "Keurig Green Mountain, formerly Green Mountain Coffee Roasters"),
    ("FII", "2003-04-16"): ("FII", "reviewed", "Federated Investors, renamed Federated Hermes in 2020"),
    ("LH", "2004-11-01"): ("LH", "reviewed", "Labcorp is Laboratory Corporation of America"),
    ("MYL", "2004-04-23"): ("MYL", "reviewed", "Mylan; EODHD's list shows the successor name Viatris, prices end 2020-11-18"),
    ("PCG", "1996-01-02"): ("PCG", "reviewed", "Run names the utility subsidiary; PCG is PG&E Corp's stock"),
    ("BHGE", "1996-01-02"): ("BKR", "reviewed", "BKR.US carries Baker Hughes Inc to 2017-07-03, then Baker Hughes a GE company (special dividend on 2017-07-05)"),
}


def get(path, dest):
    if dest.exists():
        return dest.read_bytes()
    sep = "&" if "?" in path else "?"
    url = f"{API}/{path}{sep}api_token={os.environ['EODHD_API_KEY']}"
    for delay in (0, 2, 4, 8, 16):
        time.sleep(delay)
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                body = r.read()
            dest.write_bytes(body)
            return body
        except urllib.error.HTTPError as e:
            if e.code == 404:
                dest.write_bytes(b"[]")
                return b"[]"
            if e.code not in (429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError):
            pass
    raise RuntimeError(f"gave up on {path}")


def tokens(name):
    s = name.lower().replace("&", "")
    s = re.sub(r"\(.*?\)", " ", s)
    return [w for w in re.findall(r"[a-z0-9]+", s) if w not in GENERIC]


def run_names(r):
    out = [p.split(": ", 1)[-1] for p in r["names"].split(" | ") if p.strip()]
    out += [p for p in r["sec_names"].split(" | ") if p.strip()]
    return out


def name_match(eod_name, names):
    a = set(tokens(eod_name))
    if not a:
        return 0.0
    best = 0.0
    for n in names:
        b = set(tokens(n))
        if b:
            best = max(best, len(a & b) / min(len(a), len(b)))
    return best


def series(code):
    body = get(f"eod/{code}.US?from={FROM}&fmt=json", RAW / f"{code}.US.json")
    rows = json.loads(body)
    return [r["date"] for r in rows]


def coverage(dates, start, end, latest):
    s = max(start, FROM)
    e = end or latest
    inside = [d for d in dates if s <= d <= e]
    if not dates:
        return dict(first="", last="", starts_ok=False, ends_ok=False, max_gap=0, gaps=0, rows=0)
    d0 = dt.date.fromisoformat
    starts_ok = dates[0] <= (d0(s) + dt.timedelta(days=7)).isoformat()
    ends_ok = dates[-1] >= (d0(e) - dt.timedelta(days=7)).isoformat()
    gaps = [(d0(b) - d0(a)).days for a, b in zip(inside, inside[1:])]
    big = [g for g in gaps if g > 6]
    return dict(first=dates[0], last=dates[-1], starts_ok=starts_ok, ends_ok=ends_ok,
                max_gap=max(gaps) if gaps else 0, gaps=len(big), rows=len(inside))


def assemble(symbols):
    """Write every chosen symbol's raw series to one long, gzipped CSV."""
    with gzip.open(OUT / "daily_prices.csv.gz", "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["symbol"] + PRICE_COLUMNS)
        for symbol in sorted(symbols):
            for row in json.loads((RAW / f"{symbol}.json").read_bytes()):
                w.writerow([symbol] + [row[c] for c in PRICE_COLUMNS])


def main():
    if RUNS is None:
        sys.exit("usage: pull_eodhd_prices.py RUNS_CSV OUT_DIR (with EODHD_API_KEY set)")
    if not os.environ.get("EODHD_API_KEY"):
        sys.exit("set EODHD_API_KEY")
    RAW.mkdir(parents=True, exist_ok=True)
    lists = {}
    for key, q in (("active", ""), ("delisted", "&delisted=1")):
        body = get(f"exchange-symbol-list/US?fmt=json{q}", OUT / f"symbol_list_US_{key}.json")
        lists[key] = json.loads(body)
    by_code = {}
    for key, rows in lists.items():
        for x in rows:
            if x.get("Type") == "Common Stock":
                by_code.setdefault(x["Code"], []).append((key, x["Name"] or "", x["Exchange"]))

    runs = list(csv.DictReader(RUNS.open()))
    spy = series("SPY")
    latest = spy[-1]

    US = {"NYSE", "NASDAQ", "NYSE MKT", "NYSE ARCA", "BATS", "AMEX"}
    by_first = {}
    for code, entries in by_code.items():
        for _, nm, exch in entries:
            tk = tokens(nm)
            if tk and exch in US:
                by_first.setdefault(tk[0], set()).add(code)

    def candidates(r):
        t = r["ticker"].replace(".", "-")
        variants = [t, f"{t}_old"] + [f"{t}_old{i}" for i in range(1, 5)] + [f"{t}{i}" for i in range(1, 4)]
        names = run_names(r)
        found = {c: by_code.get(c, [("none", "(not in symbol lists)", "")]) for c in variants if c in by_code}
        found.setdefault(t, by_code.get(t, [("none", "(not in symbol lists)", "")]))
        named = []
        for first in {tokens(n)[0] for n in names if tokens(n)}:
            for code in by_first.get(first, ()):
                if code not in found:
                    score = max(name_match(e[1], names) for e in by_code[code])
                    if score >= 1.0:
                        named.append(code)
        for code in sorted(named)[:8]:
            found[code] = by_code[code]
        return found

    plans = [(r, candidates(r)) for r in runs]
    codes = sorted({c for _, f in plans for c in f})
    print("runs", len(plans), "codes to fetch", len(codes), file=sys.stderr)
    t0 = time.time()
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(series, codes))
    print("fetched", round(time.time() - t0), "s", file=sys.stderr)

    table = []
    for r, found in plans:
        names = run_names(r)
        t = r["ticker"].replace(".", "-")
        scored = []
        for code, entries in found.items():
            nm = max((e[1] for e in entries), key=lambda n: name_match(n, names))
            score = name_match(nm, names)
            variant = code == t or code.startswith(t + "_old") or bool(re.fullmatch(re.escape(t) + r"\d", code))
            cov = coverage(series(code), r["start"], r["end"], latest)
            scored.append((score >= 0.5, cov["starts_ok"] and cov["ends_ok"], score, variant, cov["rows"], code, nm, cov))
        scored.sort(reverse=True)
        key = (r["ticker"], r["start"])
        if key in OVERRIDES:
            want, check, note = OVERRIDES[key]
            pick = [x for x in scored if x[5] == want] if want else []
            if want and not pick:
                cov = coverage(series(want), r["start"], r["end"], latest)
                nm = next((e[1] for e in by_code.get(want, [])), "(not in symbol lists)")
                pick = [(True, True, name_match(nm, names), True, cov["rows"], want, nm, cov)]
            if pick:
                _, _, score, _, _, code, nm, cov = pick[0]
            else:
                score, code, nm, cov = 0.0, "", "", coverage([], r["start"], r["end"], latest)
            name_check = check
        else:
            ok_name, _, score, _, _, code, nm, cov = scored[0]
            name_check = "pass" if score >= 1.0 else ("fail" if not ok_name else "review")
            note = ""
        table.append(dict(
            ticker=r["ticker"], start=r["start"], end=r["end"], run_status=r["status"],
            symbol=f"{code}.US" if code else "", eodhd_name=nm, name_score=round(score, 2), name_check=name_check,
            first_price=cov["first"], last_price=cov["last"], rows_in_spell=cov["rows"],
            covers_start=cov["starts_ok"], covers_end=cov["ends_ok"], gaps_over_6_days=cov["gaps"],
            max_gap_days=cov["max_gap"], other_candidates=";".join(x[5] for x in scored if x[5] != code)[:120], note=note,
        ))
    with (OUT / "price_runs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    assemble({row["symbol"] for row in table if row["symbol"]} | {"SPY.US"})
    print("latest", latest, file=sys.stderr)


if __name__ == "__main__":
    main()
