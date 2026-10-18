"""Independent recheck of E11 (8-K rating vs market-adjusted returns).

Written from CARD.md's frozen design and the raw files only; it does not read
or import the Lead's grading scripts, and reads grading/joins.csv only to
compare symbol mappings (and graded_events.csv not at all).
Prints all numbers used in independent_recheck.md.
"""
import gzip
import json
import sys
from datetime import time
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = "filings"  # a folder laid out like the original research tree
EXP = f"{ROOT}/experiments/E11-8k-returns"
ET = ZoneInfo("America/New_York")
NEG = {"1.02", "1.03", "2.05", "2.06", "3.01", "4.02"}

# ---------------------------------------------------------------- events
ids = set(pd.read_csv(f"{EXP}/events.csv", dtype=str).event_id)
rows = []
with open(f"{ROOT}/data/member_8k_events/member_8k_events.jsonl", encoding="utf-8") as fh:
    for line in fh:
        d = json.loads(line)
        if d["event_id"] not in ids:
            continue
        rows.append(dict(event_id=d["event_id"], company=d["company"], cik=d["cik"],
                         items=d["items"], event_items=d["event_items"],
                         accepted_utc=d["accepted_utc"],
                         press_release=d.get("press_release")))
ev = pd.DataFrame(rows)
print("events in csv", len(ids), "found in jsonl", len(ev), "dup ids", ev.event_id.duplicated().sum())


def group_of(items):
    s = set(items)
    if s & NEG:
        return "negative"
    if "4.01" in s:
        return "auditor"
    if s & {"1.01", "2.01"}:
        return "deals"
    return "officer"


ev["group"] = ev.event_items.map(group_of)
acc = pd.to_datetime(ev.accepted_utc, utc=True).dt.tz_convert(ET)
ev["acc_et"] = acc
ev["acc_date"] = acc.dt.date.astype(str)
ev["year"] = acc.dt.year
ev["has_202"] = ev["items"].map(lambda x: "2.02" in x)
print("events listing 2.02 in test set:", int(ev.has_202.sum()))
print(ev.group.value_counts().to_dict())

# ---------------------------------------------------------------- symbol map
runs = pd.read_csv(f"{ROOT}/data/member_8k_events/membership/sp500_ticker_runs.csv", dtype=str)
pr = pd.read_csv(f"{ROOT}/data/e7_prices/price_runs.csv", dtype=str)
runs = runs.merge(pr[["ticker", "start", "symbol"]], on=["ticker", "start"], how="left")
spans = []  # (cik, start, end, ticker, symbol)
for r in runs.itertuples():
    end = r.end if isinstance(r.end, str) else "9999-12-31"
    for c in str(r.ciks).split(";"):
        spans.append((c.strip(), r.start, end, r.ticker, r.symbol, "run"))
    if isinstance(r.handed_over, str):
        for part in r.handed_over.split(";"):
            tok = part.split()
            # 'cik start to end'
            spans.append((tok[0], tok[1], tok[3] if len(tok) > 3 else "9999-12-31", r.ticker, r.symbol, "handed"))
sp = pd.DataFrame(spans, columns=["cik", "s", "e", "ticker", "symbol", "kind"])
m = ev[["event_id", "cik", "acc_date"]].merge(sp, on="cik", how="left")
m = m[(m.s <= m.acc_date) & (m.acc_date <= m.e) & m.symbol.notna()]
cand = m.groupby("event_id").symbol.agg(lambda x: sorted(set(x)))
ev["cands"] = ev.event_id.map(cand)
joins = pd.read_csv(f"{EXP}/grading/joins.csv", dtype=str).set_index("event_id")
ev["sym_joins"] = ev.event_id.map(joins.symbol)
nc = ev.cands.map(lambda x: len(x) if isinstance(x, list) else 0)
print("candidate-count distribution", nc.value_counts().to_dict())
one = nc == 1
ev["sym_mine"] = np.where(one, ev.cands.map(lambda x: x[0] if isinstance(x, list) else None), None)
agree1 = (ev.sym_mine[one] == ev.sym_joins[one]).mean()
multi_ok = ev[nc > 1].apply(lambda r: r.sym_joins in r.cands, axis=1).mean() if (nc > 1).any() else float("nan")
print(f"unique-candidate events agreeing with joins.csv: {agree1:.4%} of {one.sum()}; "
      f"multi-candidate events whose joins symbol is among mine: {multi_ok:.4%} of {(nc>1).sum()}")
print("multi-candidate examples:", ev[nc > 1][["company", "cands", "sym_joins"]].drop_duplicates("company").head(10).to_string())
bad1 = ev[one & (ev.sym_mine != ev.sym_joins)]
print("unique-candidate disagreements:", len(bad1), bad1[["company", "acc_date", "sym_mine", "sym_joins"]].head(10).to_string())
# Final symbol: mine when unique, else the joins.csv choice (it is among my candidates; checked above).
ev["symbol"] = np.where(one, ev.sym_mine, ev.sym_joins)

# ---------------------------------------------------------------- prices
need = set(ev.symbol.dropna()) | {"SPY.US"}
px = {}
with gzip.open(f"{ROOT}/data/e7_prices/daily_prices.csv.gz", "rt") as fh:
    for chunk in pd.read_csv(fh, usecols=["symbol", "date", "adjusted_close"], chunksize=2_000_000, dtype={"symbol": str, "date": str}):
        chunk = chunk[chunk.symbol.isin(need)]
        for s, g in chunk.groupby("symbol"):
            px.setdefault(s, []).append(g)
px = {s: pd.concat(g).drop_duplicates("date").set_index("date").adjusted_close.sort_index() for s, g in px.items()}
spy = px["SPY.US"]
cal = list(spy.index)
cal_idx = {d: i for i, d in enumerate(cal)}
cal_arr = np.array(cal)
print("calendar", cal[0], cal[-1], len(cal), "symbols missing from price file:", sorted(need - set(px)))

# ---------------------------------------------------------------- event time
close_t = time(16, 0)


def day0_index(ts):
    d = ts.date().isoformat()
    i = int(np.searchsorted(cal_arr, d, side="left"))  # first trading day >= d
    if i < len(cal) and cal[i] == d and ts.time() < close_t:
        return i
    if i < len(cal) and cal[i] == d:
        return i + 1
    return i


ev["i0"] = ev.acc_et.map(day0_index)


def price_on_or_before(s, d):
    """Last stock close on or before date d: (date, price) or (None, nan)."""
    ser = px.get(s)
    if ser is None:
        return None, np.nan
    j = ser.index.searchsorted(d, side="right") - 1
    if j < 0:
        return None, np.nan
    return ser.index[j], ser.iloc[j]


def excess(sym, i_start, i_end):
    """Stock return from close cal[i_start] to cal[i_end] minus SPY's; stock must have
    an exact close on cal[i_start]; after its last close it earns SPY."""
    ser = px.get(sym)
    if ser is None or i_end >= len(cal):
        return np.nan
    ds, de = cal[i_start], cal[i_end]
    if ds not in ser.index:
        return np.nan
    p0 = ser[ds]
    dl, pl = price_on_or_before(sym, de)
    stock = pl / p0 * (spy[de] / spy[dl]) - 1
    return stock - (spy[de] / spy[ds] - 1)


ev["r2"] = [excess(s, i - 1, i + 1) for s, i in zip(ev.symbol, ev.i0)]
ev["r10"] = [excess(s, i - 1, i + 9) for s, i in zip(ev.symbol, ev.i0)]
ev["drift10"] = [excess(s, i, i + 10) for s, i in zip(ev.symbol, ev.i0)]
ev["r1"] = [excess(s, i - 1, i) for s, i in zip(ev.symbol, ev.i0)]
ev["r_m1_p10"] = [excess(s, i - 1, i + 10) for s, i in zip(ev.symbol, ev.i0)]
ev["drift10_alt"] = ev.r_m1_p10 - ev.r1  # alternative drift: difference of excess returns
ev["drift9"] = [excess(s, i, i + 9) for s, i in zip(ev.symbol, ev.i0)]
for c in ["r1", "r2", "r10", "drift10"]:
    print(c, "missing", int(ev[c].isna().sum()))

# ---------------------------------------------------------------- scores
sc = pd.read_csv(f"{EXP}/jev/scores.csv", dtype={"event_id": str})
bl = pd.read_csv(f"{EXP}/jev/baselines.csv", dtype={"event_id": str})
ev = ev.merge(sc[["event_id", "rating_choice", "rating_score", "bad_score"]], on="event_id", how="left")
ev = ev.merge(bl[["event_id", "net_tone"]], on="event_id", how="left")
ev["words"] = -ev.net_tone
print("missing scores", int(ev.rating_score.isna().sum()), "missing baseline", int(ev.net_tone.isna().sum()))

# ---------------------------------------------------------------- cells
cell_of = {}
for g, sub in ev.groupby("group"):
    counts = sub.year.value_counts().sort_index()
    cells, cur, n = [], [], 0
    for y, c in counts.items():
        cur.append(y)
        n += c
        if n >= 30:
            cells.append(cur)
            cur, n = [], 0
    if cur:
        if cells:
            cells[-1] += cur
        else:
            cells.append(cur)
    for k, ys in enumerate(cells):
        for y in ys:
            cell_of[(g, y)] = f"{g}:{ys[0]}-{ys[-1]}"
ev["cell"] = [cell_of[(g, y)] for g, y in zip(ev.group, ev.year)]
print("cells", ev.cell.nunique(), ev.groupby("group").cell.nunique().to_dict())


def spearman(a, b):
    ok = ~(pd.isna(np.asarray(a, dtype=float)) | pd.isna(np.asarray(b, dtype=float)))
    a, b = np.asarray(a, dtype=float)[ok], np.asarray(b, dtype=float)[ok]
    ra, rb = pd.Series(a).rank(method="average"), pd.Series(b).rank(method="average")
    if ra.std() == 0 or rb.std() == 0:
        return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


def cell_table(score, ret):
    t = ev.groupby("cell").apply(lambda d: pd.Series(dict(rho=spearman(d[score], d[ret]), n=int(d[ret].notna().sum()), group=d.group.iloc[0])),
                                 include_groups=False)
    return t


def wavg(t):
    return float((t.rho * t.n).sum() / t.n.sum())


rng = np.random.default_rng(311)
cells = cell_table("rating_score", "r2")
groups = {g: np.where(cells.group.values == g)[0] for g in cells.group.unique()}
B = 10_000
draws = np.empty((B, len(cells)), dtype=int)  # multiplicity of each cell in each draw
for b in range(B):
    cnt = np.zeros(len(cells), dtype=int)
    for g, idx in groups.items():
        np.add.at(cnt, rng.choice(idx, size=len(idx), replace=True), 1)
    draws[b] = cnt


def boot(t):
    w = draws * t.n.values
    return (w * t.rho.values).sum(1) / w.sum(1)


def ci(x):
    return np.percentile(x, [2.5, 97.5])


res = {}
for name, ret in [("2d", "r2"), ("10d", "r10"), ("drift10", "drift10"), ("1d", "r1"),
                  ("drift10_alt(diff of excess)", "drift10_alt"), ("drift day0->+9", "drift9")]:
    tj, tw = cell_table("rating_score", ret), cell_table("words", ret)
    assert (tj.index == cells.index).all()
    bj, bw = boot(tj), boot(tw)
    res[name] = (wavg(tj), ci(bj), wavg(tw), ci(bw), wavg(tj) - wavg(tw), ci(bj - bw))
    print(f"{name}: jev {wavg(tj):+.4f} {ci(bj).round(4)} words {wavg(tw):+.4f} {ci(bw).round(4)} "
          f"diff {wavg(tj)-wavg(tw):+.4f} {ci(bj-bw).round(4)}")

ob = ev[(ev.group == "officer") & (ev.rating_choice == "bad")]
print(f"officer x bad: n={len(ob)} mean 2d {100*ob.r2.mean():+.3f}%  mean 10d {100*ob.r10.mean():+.3f}%")
for ch, d in ev.groupby("rating_choice"):
    print(f"  choice {ch}: n={len(d)} mean2d {100*d.r2.mean():+.3f}%")
print("per-group pooled-within-years 2d jev rho:",
      {g: round(wavg(cells[cells.group == g]), 4) for g in groups})

# ---------------------------------------------------------------- hand checks
print("\nHAND CHECKS")
for ch in ["very_bad", "very_good", "neutral"]:
    r = ev[ev.rating_choice == ch].sort_values("event_id").iloc[len(ev[ev.rating_choice == ch]) // 2]
    i = r.i0
    s = px[r.symbol]
    print(f"{ch}: {r.event_id} {r.company} {r.symbol} group={r.group} accepted ET {r.acc_et}")
    for k, lab in [(-1, "day-1"), (0, "day0"), (1, "day+1")]:
        d = cal[i + k]
        print(f"   {lab} {d} stock {s.get(d, float('nan'))} SPY {spy[d]}")
    st = s[cal[i + 1]] / s[cal[i - 1]] - 1
    sr = spy[cal[i + 1]] / spy[cal[i - 1]] - 1
    print(f"   stock {100*st:+.3f}% SPY {100*sr:+.3f}% excess {100*(st-sr):+.3f}%  (pipeline r2 {100*r.r2:+.3f}%) score {r.rating_score}")

# ---------------------------------------------------------------- sanity checks
print("\nSANITY (a): shuffle scores within cell, 200 times")
srng = np.random.default_rng(7)
vals = []
for _ in range(200):
    sh = ev.groupby("cell").rating_score.transform(lambda x: x.sample(frac=1, random_state=int(srng.integers(1 << 31))).values)
    tmp = ev.assign(sh=sh.values)
    t = tmp.groupby("cell").apply(lambda d: pd.Series(dict(rho=spearman(d.sh, d.r2), n=len(d))), include_groups=False)
    vals.append(wavg(t))
vals = np.array(vals)
print(f"shuffled mean {vals.mean():+.4f} sd {vals.std():.4f} 2.5/97.5% {np.percentile(vals,[2.5,97.5]).round(4)} "
      f"max {vals.max():+.4f}; share >= observed {np.mean(vals >= res['2d'][0]):.3f}")

print("SANITY (b): day -1 close strictly before acceptance")
dm1 = pd.to_datetime([cal[i - 1] + " 16:00" for i in ev.i0]).tz_localize(ET)
d0 = pd.to_datetime([cal[i] + " 16:00" for i in ev.i0]).tz_localize(ET)
print("violations day-1 close >= acceptance:", int((dm1 >= pd.DatetimeIndex(ev.acc_et)).sum()),
      "| day0 close <= acceptance:", int((d0 <= pd.DatetimeIndex(ev.acc_et)).sum()),
      "| accepted exactly 16:00:00 ET:", int((ev.acc_et.dt.time == close_t).sum()),
      "| accepted on non-trading day:", int((~ev.acc_date.isin(cal_idx)).sum()))
hd = ev.acc_et.dt.time
print("acceptance before 09:30 ET:", int((hd < time(9, 30)).sum()), " 09:30-16:00:", int(((hd >= time(9, 30)) & (hd < close_t)).sum()),
      " after 16:00:", int((hd >= close_t).sum()))
# half-day sessions (13:00 close): events accepted 13:00-16:00 on a day whose close was 13:00 would get day0 = that day
# even though that close preceded acceptance. Flag candidates: day before July 4, Black Friday, Christmas Eve.
ev["md"] = ev.acc_et.dt.strftime("%m-%d")
half = ev[((ev.md.isin(["07-03", "12-24", "12-31"])) | ((ev.acc_et.dt.month == 11) & (ev.acc_et.dt.weekday == 4) & (ev.acc_et.dt.day.between(23, 29))))
          & (hd >= time(13, 0)) & (hd < close_t) & ev.acc_date.isin(cal_idx)]
print("possible half-day-session events accepted 13:00-16:00 ET:", len(half))
dup = ev.groupby(["company", "i0"]).size()
print("same company same day0 pairs remaining:", int((dup > 1).sum()))
ev[["event_id", "company", "symbol", "group", "cell", "rating_choice", "rating_score", "words", "r1", "r2", "r10", "drift10"]].to_csv(
    sys.argv[1] if len(sys.argv) > 1 else "/dev/null", index=False)
