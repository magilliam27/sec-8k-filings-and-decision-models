"""E12 grading, frozen design on experiments/E12-next-open/CARD.md (17 Oct 23:45Z).
Usage: grade_e12.py check -> entry split and bad-open counts only, no returns
       grade_e12.py grade -> full result printed
       grade_e12.py save  -> also written to OUT (originally grading/)"""
# ---- verification pack: configurable paths (statistical logic below is unchanged) ----
import os
F = os.path.join(os.environ.get("FILINGS", "filings"), "")  # frozen inputs, read only
OUT = os.path.join(os.environ.get("VERIFY_OUT", "verify_out/e12"), "")  # everything this script writes goes here
assert "/filings/experiments/" not in os.path.abspath(OUT) + "/", "OUT must not point into filings/experiments"
# -------------------------------------------------------------------------------------
import sys, json, hashlib, numpy as np, pandas as pd
E11=F+"experiments/E11-8k-returns/"
mode=sys.argv[1]
sha=lambda p: hashlib.sha256(open(p,"rb").read()).hexdigest()
d=pd.read_csv(E11+"grading/graded_events.csv",dtype={"event_id":str,"cik":str},
              usecols=["event_id","symbol","group","cell","year","i0","rating_choice","rating_score","base_good","d0_1","accepted_et"])
d["acc"]=pd.to_datetime(d.accepted_et.str.slice(0,19))   # naive US Eastern wall time
px=pd.read_csv(F+"data/e7_prices/daily_prices.csv.gz",usecols=["symbol","date","open","close","adjusted_close"],parse_dates=["date"])
px["adj_open"]=px.open*px.adjusted_close/px.close
spy=px[px.symbol=="SPY.US"].set_index("date").sort_index(); cal=spy.index
P={s:g.set_index("date").sort_index() for s,g in px.groupby("symbol")}
# entry: first 09:30 open after acceptance
day0=cal[d.i0.astype(int).values]
intraday=(d.acc.dt.normalize().values==day0.values)&(d.acc.dt.hour*60+d.acc.dt.minute>=570).values
d["closed_mkt"]=~intraday
d["i0"]=d.i0.astype(int); d["ie"]=d.i0+intraday.astype(int)
entry_open=cal[d.ie.values]+pd.Timedelta(hours=9,minutes=30)
assert (entry_open>d.acc.values).all(), "entry before acceptance"
d["late_premarket"]=d.closed_mkt&(d.acc.dt.normalize().values==day0.values)&((d.acc.dt.hour*60+d.acc.dt.minute)>=540).values
def entry_ok(r):
    s=P[r.symbol]; t=cal[r.ie]
    return t in s.index and s.at[t,"open"]>0 and np.isfinite(s.at[t,"adj_open"])
d["open_ok"]=[entry_ok(r) for r in d.itertuples()]
print("events",len(d),"| closed-market",int(d.closed_mkt.sum()),"| intraday",int((~d.closed_mkt).sum()),
      "| 09:00-09:30 premarket",int(d.late_premarket.sum()),"| bad/missing open",int((~d.open_ok).sum()))
print("bad opens by group:",d[~d.open_ok].groupby("closed_mkt").size().to_dict())
if mode=="check": sys.exit()
d=d[d.open_ok].copy()
def ret(sym,ie,k):
    s=P[sym]; ta,tb=cal[ie],cal[ie+k]
    pa=s.at[ta,"adj_open"]; last=s.index[s.index<=tb][-1]
    r=s.at[last,"adjusted_close"]/pa-1
    if last<tb: r=(1+r)*(spy.at[tb,"adjusted_close"]/spy.at[last,"adjusted_close"])-1
    return r-(spy.at[tb,"adjusted_close"]/spy.at[ta,"adj_open"]-1)
for k,w in [(1,"s2"),(4,"s5")]:
    d[w]=[ret(r.symbol,r.ie,k) if r.ie+k<len(cal) else np.nan for r in d.itertuples()]
# part a trader cannot get: day -1 close to entry open, market-adjusted (closed-market only; ie=i0)
def gap(r):
    s=P[r.symbol]; ta,tb=cal[r.i0-1],cal[r.ie]
    a=s.index[s.index<=ta]
    if len(a)==0: return np.nan
    return s.at[tb,"adj_open"]/s.at[a[-1],"adjusted_close"]-1-(spy.at[tb,"adj_open"]/spy.at[ta,"adjusted_close"]-1)
d["gap"]=[gap(r) for r in d.itertuples()]
big=d[d.gap.abs()>0.30]
print("missing returns",{w:int(d[w].isna().sum()) for w in ["s2","s5"]},"| gaps over 30%:",len(big))
print(big[["event_id","symbol","accepted_et","gap"]].to_string())
B=10000; SEED=312
def cell_rhos(df,sig,out,min_n=10):
    r=[]
    for c,g in df.groupby("cell"):
        g=g[[sig,out,"group"]].dropna()
        if len(g)<min_n or g[sig].nunique()<2: continue
        r.append((c,g.group.iloc[0],len(g),g[sig].rank().corr(g[out].rank())))
    return pd.DataFrame(r,columns=["cell","group","n","rho"])
def boot_stat(df,sigs,out):
    tabs=[cell_rhos(df,s,out).set_index("cell") for s in sigs]
    common=tabs[0].index
    for t in tabs[1:]: common=common.intersection(t.index)
    tabs=[t.loc[common] for t in tabs]; n=tabs[0].n.values; grp=tabs[0].group.values
    R=np.vstack([t.rho.values for t in tabs]); est=(R*n).sum(1)/n.sum()
    rng=np.random.default_rng(SEED); gi=[np.where(grp==g)[0] for g in np.unique(grp)]; bs=[]
    for _ in range(B):
        idx=np.concatenate([rng.choice(ix,len(ix),replace=True) for ix in gi]); bs.append((R[:,idx]*n[idx]).sum(1)/n[idx].sum())
    bs=np.array(bs); res={"cells":int(len(common)),"events":int(n.sum())}
    for k,s in enumerate(sigs): res[s]=[round(float(est[k]),4),round(float(np.percentile(bs[:,k],2.5)),4),round(float(np.percentile(bs[:,k],97.5)),4)]
    dd=bs[:,0]-bs[:,1]; res["diff"]=[round(float(est[0]-est[1]),4),round(float(np.percentile(dd,2.5)),4),round(float(np.percentile(dd,97.5)),4)]
    return res
d["month"]=d.acc.dt.strftime("%Y-%m")
def mean_ci(df,out):
    m=df.groupby("month")[out].agg(["sum","count"]); s=m["sum"].values; c=m["count"].values
    rng=np.random.default_rng(SEED); bs=[]
    for _ in range(2000):
        i=rng.integers(0,len(s),len(s)); bs.append(s[i].sum()/c[i].sum())
    return [round(float(s.sum()/c.sum()*100),3),round(float(np.percentile(bs,2.5)*100),3),round(float(np.percentile(bs,97.5)*100),3),int(c.sum())]
def fifth_gap(df,out):
    gaps=[]
    for c,g in df.groupby("cell"):
        g=g.dropna(subset=[out])
        if len(g)<10: continue
        q=pd.qcut(g.rating_score.rank(method="first"),5,labels=False)
        gaps.append((g.group.iloc[0],len(g),g[out][q==4].mean()-g[out][q==0].mean()))
    G=pd.DataFrame(gaps,columns=["group","n","gap"]); rng=np.random.default_rng(SEED); bs=[]
    gi=[np.where(G.group.values==x)[0] for x in G.group.unique()]
    for _ in range(B):
        i=np.concatenate([rng.choice(ix,len(ix)) for ix in gi]); bs.append((G.gap.values[i]*G.n.values[i]).sum()/G.n.values[i].sum())
    return [round(float((G.gap*G.n).sum()/G.n.sum()*100),3),round(float(np.percentile(bs,2.5)*100),3),round(float(np.percentile(bs,97.5)*100),3)]
O={"counts":{"events_with_open":int(len(d)),"closed_market":int(d.closed_mkt.sum()),"intraday":int((~d.closed_mkt).sum()),"premarket_0900_0930":int(d.late_premarket.sum())}}
subsets={"closed_market":d[d.closed_mkt],"intraday_next_open":d[~d.closed_mkt],"all":d}
for name,x in subsets.items():
    O[name]={w:boot_stat(x,["rating_score","base_good"],w) for w in ["s2","s5"]}
    O[name]["fifth_gap_pct"]={w:fifth_gap(x,w) for w in ["s2","s5"]}
    O[name]["mean_pct_by_answer"]={a:{w:mean_ci(g,w) for w in ["s2","s5"]} for a,g in x.groupby("rating_choice")}
    O[name]["officer_bad"]={w:mean_ci(x[(x.group=="officer")&(x.rating_choice=="bad")],w) for w in ["s2","s5"]}
    O[name]["deals_very_good"]={w:mean_ci(x[(x.group=="deals")&(x.rating_choice=="very_good")],w) for w in ["s2","s5"]}
cm=d[d.closed_mkt]
O["closed_market"]["e11_2day_same_events"]=boot_stat(cm,["rating_score","base_good"],"d0_1")
O["closed_market"]["gap_before_entry"]=boot_stat(cm,["rating_score","base_good"],"gap")
O["closed_market"]["mean_gap_pct_by_answer"]={a:mean_ci(g,"gap") for a,g in cm.groupby("rating_choice")}
O["closed_market"]["mean_e11_2day_pct_by_answer"]={a:mean_ci(g,"d0_1") for a,g in cm.groupby("rating_choice")}
print(json.dumps(O,indent=1))
if mode=="save":
    os.makedirs(OUT,exist_ok=True)
    json.dump(O,open(OUT+"summary.json","w"),indent=1)
    d.drop(columns=["acc"]).to_csv(OUT+"graded_events.csv",index=False)
    print("saved",sha(OUT+"summary.json")[:8])
