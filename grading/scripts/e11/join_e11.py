"""E11 joins: event -> price symbol, day 0, day -1, window check. Counts only unless 'returns' is passed."""
# ---- verification pack: configurable paths (statistical logic below is unchanged) ----
import os
F = os.path.join(os.environ.get("FILINGS", "filings"), "")  # frozen inputs, read only
OUT = os.path.join(os.environ.get("VERIFY_OUT", "verify_out/e11"), "")  # everything this script writes goes here
assert "/filings/experiments/" not in os.path.abspath(OUT) + "/", "OUT must not point into filings/experiments"
os.makedirs(OUT, exist_ok=True)
# -------------------------------------------------------------------------------------
import sys, numpy as np, pandas as pd
ev=pd.read_pickle(OUT+"events.pkl")
runs=pd.read_csv(F+"data/member_8k_events/membership/sp500_ticker_runs.csv",dtype={"ciks":str})
pr=pd.read_csv(F+"data/e7_prices/price_runs.csv")
px=pd.read_csv(F+"data/e7_prices/daily_prices.csv.gz",usecols=["symbol","date","adjusted_close"],parse_dates=["date"])
runs=runs.merge(pr[["ticker","start","symbol"]],on=["ticker","start"],how="left")
rows=[]
for _,r in runs.iterrows():
    st=pd.Timestamp(r.start); en=pd.Timestamp(r.end) if isinstance(r.end,str) else pd.Timestamp("2100-01-01")
    for c in str(r.ciks).split(";"): rows.append((c.strip().zfill(10),st,en,r.ticker,r.symbol,"main"))
    if isinstance(r.handed_over,str):
        for part in r.handed_over.split(";"):
            t=part.split()
            if len(t)>=4: rows.append((t[0].zfill(10),pd.Timestamp(t[1]),pd.Timestamp(t[3]),r.ticker,r.symbol,"handed_over"))
cmap=pd.DataFrame(rows,columns=["cik","st","en","ticker","symbol","kind"])
spy=px[px.symbol=="SPY.US"].set_index("date").adjusted_close.sort_index(); cal=spy.index
P={s:g.set_index("date").adjusted_close.sort_index() for s,g in px.groupby("symbol")}
def day0(ts):
    d=ts.tz_localize(None).normalize()
    if d in cal and ts.hour<16: return cal.get_loc(d)
    i=cal.searchsorted(d,side="right"); return i if i<len(cal) else None
ev["acc_date"]=ev.acc_et.dt.tz_localize(None).dt.normalize()
out=[]
by_cik={k:g for k,g in cmap.groupby("cik")}
for f in ev.itertuples():
    o={"event_id":f.event_id,"why":None,"symbol":None,"i0":None}
    m=by_cik.get(f.cik.zfill(10))
    if m is not None: m=m[(m.st<=f.acc_date)&(m.en>=f.acc_date)&m.symbol.notna()]
    if m is None or m.empty: o["why"]="no run with a price symbol"; out.append(o); continue
    i0=day0(f.acc_et)
    if i0 is None or i0+9>=len(cal): o["why"]="window not ended"; out.append(o); continue
    dm1=cal[i0-1]; best=None
    for mm in m.sort_values(["kind","ticker"]).itertuples():
        s=P.get(mm.symbol)
        if s is not None and dm1 in s.index: best=mm; break
    if best is None: o["why"]="no price at day -1"; out.append(o); continue
    o.update(symbol=best.symbol,i0=i0); out.append(o)
J=ev.merge(pd.DataFrame(out),on="event_id")
J.to_pickle(OUT+"joined.pkl")
print(J.why.fillna("joined").value_counts())
ok=J[J.why.isna()]
print("joined, also lists 2.02:",ok.has_202.sum())
ok=ok[~ok.has_202]
# same company, same day 0: keep most negative-leaning group, then earliest
rank={"negative":0,"auditor":1,"deals":2,"officer":3}
ok=ok.assign(r=ok.group.map(rank)).sort_values(["company","i0","r","acc_et"])
dup=ok.duplicated(["company","i0"])
print("same-day duplicates dropped:",dup.sum())
ok=ok[~dup]
print("test events:",len(ok)); print(ok.group.value_counts())
print(ok.groupby(ok.acc_et.dt.year).size().to_dict())
noprice=J[J.why=="no price at day -1"]; print(noprice.company.value_counts().head(25).to_dict())
norun=J[J.why=="no run with a price symbol"]; print(norun.company.value_counts().head(25).to_dict())
