"""E7 grading: frozen design on experiments/E7-returns/CARD.md (16 Oct 10:10Z).
Usage: grade_e7.py counts   -> joins and coverage only, no correlations
       grade_e7.py grade    -> full result
       grade_e7.py save     -> full result written to OUT (originally grading/)"""
# ---- verification pack: configurable paths (statistical logic below is unchanged) ----
import os
F = os.path.join(os.environ.get("FILINGS", "filings"), "")  # frozen inputs, read only
OUT = os.path.join(os.environ.get("VERIFY_OUT", "verify_out/e7"), "")  # everything this script writes goes here
assert "/filings/experiments/" not in os.path.abspath(OUT) + "/", "OUT must not point into filings/experiments"
os.makedirs(OUT, exist_ok=True)
# -------------------------------------------------------------------------------------
import sys, json, os, numpy as np, pandas as pd
from zoneinfo import ZoneInfo
E=F+"experiments/E7-returns/"
mode=sys.argv[1]
sig=pd.read_csv(E+"signals/report_signals.csv",dtype={"accession_number":str,"cik":str,"prior_accession":str})
runs=pd.read_csv(F+"data/e7_sp500_10k/membership/sp500_ticker_runs.csv",dtype={"ciks":str})
pr=pd.read_csv(F+"data/e7_prices/price_runs.csv")
px=pd.read_csv(F+"data/e7_prices/daily_prices.csv.gz",usecols=["symbol","date","adjusted_close"],parse_dates=["date"])
# Signal 4, if scored
j4=None
for cand in ["jev/worse_share.csv"]:
    if os.path.exists(E+cand): j4=cand
# ---- filing -> price symbol
runs=runs.merge(pr[["ticker","start","symbol","name_check"]],on=["ticker","start"],how="left")
rows=[]
for _,r in runs.iterrows():
    st=pd.Timestamp(r.start); en=pd.Timestamp(r.end) if isinstance(r.end,str) else pd.Timestamp("2100-01-01")
    for c in str(r.ciks).split(";"):
        rows.append((c.strip().zfill(10),st,en,r.ticker,r.symbol,r.name_check,"main"))
    if isinstance(r.handed_over,str):
        for part in r.handed_over.split(";"):
            t=part.split()
            if len(t)>=4: rows.append((t[0].zfill(10),pd.Timestamp(t[1]),pd.Timestamp(t[3]),r.ticker,r.symbol,r.name_check,"handed_over"))
cmap=pd.DataFrame(rows,columns=["cik","st","en","ticker","symbol","name_check","kind"])
ET=ZoneInfo("America/New_York")
sig["acc_et"]=pd.to_datetime(sig.accepted_utc,utc=True).dt.tz_convert(ET)
sig["acc_date"]=sig.acc_et.dt.tz_localize(None).dt.normalize()
spy=px[px.symbol=="SPY.US"].set_index("date").adjusted_close.sort_index()
cal=spy.index
P={s:g.set_index("date").adjusted_close.sort_index() for s,g in px.groupby("symbol")}
LAST=cal[-1]; H=[21,63,126]
def start_day(ts):
    d=ts.tz_localize(None).normalize()
    if d in cal and ts.hour<16: return d
    i=cal.searchsorted(d,side="right"); return cal[i] if i<len(cal) else None
recs=[]
for _,f in sig.iterrows():
    m=cmap[(cmap.cik==f.cik.zfill(10))&(cmap.st<=f.acc_date)&(cmap.en>=f.acc_date)&cmap.symbol.notna()]
    out={"accession_number":f.accession_number,"symbol":None,"why":None}
    if m.empty: out["why"]="no run"; recs.append(out); continue
    d0=start_day(f.acc_et)
    best=None
    for _,mm in m.sort_values(["kind","ticker"]).iterrows():
        s=P.get(mm.symbol)
        if s is None: continue
        k=s.index.searchsorted(d0)
        if k<len(s) and (s.index[k]-d0).days<=7: best=(mm,s,s.index[k]); break
    if best is None: out["why"]="no price at start"; recs.append(out); continue
    mm,s,t0=best; i0=cal.searchsorted(t0)
    out.update(symbol=mm.symbol,ticker=mm.ticker,start=t0)
    if i0+126>=len(cal): out["why"]="window not ended"; recs.append(out); continue
    p0=s.loc[t0]; q0=spy.loc[t0]
    for h in H:
        te=cal[i0+h]; last=s.index[s.index<=te][-1]
        r_stock=s.loc[last]/p0-1
        if last<te: r_stock=(1+r_stock)*(spy.loc[te]/spy.loc[last])-1   # after it stops trading: earns SPY
        out[f"r{h}"]=r_stock-(spy.loc[te]/q0-1); out[f"stopped{h}"]=bool(last<te)
    recs.append(out)
R=pd.DataFrame(recs); d=sig.merge(R,on="accession_number")
ok=d.r126.notna() if "r126" in d else pd.Series(False,index=d.index)
# ---- groups: calendar quarter of acceptance (ET), quarters under 30 filings join the next
g=d[ok].copy(); g["q"]=g.acc_et.dt.year.astype(str)+"Q"+g.acc_et.dt.quarter.astype(str)
qs=sorted(g.q.unique()); cnt=g.q.value_counts(); grp={}; cur=[]; n=0; gid=0
for q in qs:
    cur.append(q); n+=cnt[q]
    if n>=30:
        for x in cur: grp[x]=gid
        gid+=1; cur=[]; n=0
if cur:
    for x in cur: grp[x]=gid-1 if gid>0 else 0
g["group"]=g.q.map(grp)
few=(g.n_risks<5)|(g.n_prior_risks<5)
for c in ["new_share","changed_share"]: g.loc[few,c]=np.nan
counts={"few_risks_blanked":int((few&sig.set_index("accession_number").loc[g.accession_number,"new_share"].notna().values).sum()),"member_reports":len(d),"why_dropped":d.why.value_counts().to_dict(),"with_returns":int(ok.sum()),
  "groups":int(g.group.nunique()),"group_size_min":int(g.group.value_counts().min()),"group_size_median":float(g.group.value_counts().median()),
  "signal1":int(g.section_change.notna().sum()),"signal2_3":int(g.new_share.notna().sum()),
  "stopped_trading_in_126":int(g.stopped126.sum()),"by_year":g.acc_et.dt.year.value_counts().sort_index().to_dict()}
if j4:
    J=pd.read_csv(E+j4,dtype={"accession_number":str})[["accession_number","worse_share"]]; g=g.merge(J,on="accession_number",how="left")
    g["signal4"]=g["worse_share"]
    g.loc[(g.n_risks<5)|(g.n_prior_risks<5),"signal4"]=np.nan
    counts["signal4"]=int(g.signal4.notna().sum()); counts["signal4_file"]=j4
print(json.dumps(counts,indent=1,default=str))
if mode=="counts": sys.exit()
SIG={"signal1_section_change":"section_change","signal2_new_share":"new_share","signal3_changed_share":"changed_share"}
if j4: SIG["signal4_jev_worse_share"]="signal4"
rng=np.random.default_rng(307); B=10000
def per_group(col,h,min_n=10):
    ic={}; spread={}
    for k,x in g[[col,f"r{h}","group"]].dropna().groupby("group"):
        if len(x)<min_n: continue
        ic[k]=x[col].rank().corr(x[f"r{h}"].rank())
        lo,hi=x[col].quantile([.2,.8]); spread[k]=x.loc[x[col]>=hi,f"r{h}"].mean()-x.loc[x[col]<=lo,f"r{h}"].mean()
    return pd.Series(ic),pd.Series(spread)
def boot(v):
    v=np.asarray(v); m=[v[rng.integers(0,len(v),len(v))].mean() for _ in range(B)]
    return [float(np.percentile(m,2.5)),float(np.percentile(m,97.5))]
res={"counts":counts,"signals":{}}
for name,col in SIG.items():
    for h in H:
        ic,sp=per_group(col,h)
        res["signals"][f"{name}@{h}"]={"groups":len(ic),"mean_rank_corr":float(ic.mean()),"interval_95":boot(ic.values),
          "share_groups_negative":float((ic<0).mean()),"top_minus_bottom_fifth":float(sp.mean()),"spread_interval_95":boot(sp.values)}
m=res["signals"]["signal1_section_change@63"]; res["main_test"]={**m,"pass":bool(m["interval_95"][1]<0)}
if j4:
    for h in H:
        both=g.dropna(subset=["signal4","changed_share",f"r{h}"]); diff={}
        for k,x in both.groupby("group"):
            if len(x)<10: continue
            diff[k]=x.signal4.rank().corr(x[f"r{h}"].rank())-x.changed_share.rank().corr(x[f"r{h}"].rank())
        diff=pd.Series(diff); res[f"jev_test@{h}"]={"groups":len(diff),"mean_diff":float(diff.mean()),"interval_95":boot(diff.values),"pass":bool(boot(diff.values)[1]<0) if h==63 else None}
yr={}
for name,col in SIG.items():
    yr[name]={int(y):float(x[col].rank().corr(x["r63"].rank())) for y,x in g[[col,"r63"]].assign(y=g.acc_et.dt.year).dropna().groupby("y") if len(x)>=30}
res["by_year_rank_corr_63"]=yr
res["bootstrap"]={"draws":B,"seed":307,"unit":"whole groups (quarters, joined to reach 30 filings)"}
print(json.dumps(res,indent=1,default=float))
if mode=="save":
    json.dump(res,open(OUT+"summary.json","w"),indent=1,default=float)
    g.drop(columns=["acc_et"]).to_csv(OUT+"graded_filings.csv",index=False)
