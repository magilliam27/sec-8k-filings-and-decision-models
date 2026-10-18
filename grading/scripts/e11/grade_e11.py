"""E11 grading, frozen design on experiments/E11-8k-returns/CARD.md (16 Oct 12:45Z).
Usage: grade_e11.py check  -> inputs and hashes only, no returns
       grade_e11.py grade  -> full result printed
       grade_e11.py save   -> also written to OUT (originally grading/)"""
# ---- verification pack: configurable paths (statistical logic below is unchanged) ----
import os
F = os.path.join(os.environ.get("FILINGS", "filings"), "")  # frozen inputs, read only
OUT = os.path.join(os.environ.get("VERIFY_OUT", "verify_out/e11"), "")  # everything this script writes goes here
assert "/filings/experiments/" not in os.path.abspath(OUT) + "/", "OUT must not point into filings/experiments"
os.makedirs(OUT, exist_ok=True)
# -------------------------------------------------------------------------------------
import sys, json, hashlib, numpy as np, pandas as pd
E=F+"experiments/E11-8k-returns/"
S=OUT  # was the Lead's scratchpad e11/ folder
mode=sys.argv[1]
sha=lambda p: hashlib.sha256(open(p,"rb").read()).hexdigest()
ids=pd.read_csv(E+"events.csv",dtype=str).event_id
J=pd.read_pickle(S+"joined.pkl"); J=J[J.event_id.isin(ids)].copy()
sc=pd.read_csv(E+"jev/scores.csv",dtype={"event_id":str})
bl=pd.read_csv(E+"jev/baselines.csv",dtype={"event_id":str})
d=J.merge(sc[["event_id","rating_choice","rating_score","bad_score"]],on="event_id",how="left") \
   .merge(bl[["event_id","lean","net_tone"]],on="event_id",how="left")
print("events",len(d),"| no Jev score",d.rating_score.isna().sum(),"| no baseline",d.net_tone.isna().sum())
print("hashes: events",sha(E+"events.csv")[:8],"scores",sha(E+"jev/scores.csv")[:8],"baselines",sha(E+"jev/baselines.csv")[:8])
if mode=="check": sys.exit()
d=d[d.rating_score.notna()&d.net_tone.notna()].copy()
d["year"]=d.acc_et.dt.year
d["base_good"]=-d.net_tone; d["jev_good_bad"]=-d.bad_score
d["good_score"]=sc.set_index("event_id").loc[d.event_id,["rating_p_good","rating_p_very_good"]].sum(1).values
# ---- prices and returns
px=pd.read_csv(F+"data/e7_prices/daily_prices.csv.gz",usecols=["symbol","date","adjusted_close"],parse_dates=["date"])
spy=px[px.symbol=="SPY.US"].set_index("date").adjusted_close.sort_index(); cal=spy.index
P={s:g.set_index("date").adjusted_close.sort_index() for s,g in px.groupby("symbol")}
def ret(s,ia,ib):
    ta,tb=cal[ia],cal[ib]
    a=s.index[s.index<=ta]; 
    if len(a)==0: return np.nan
    pa=s.loc[a[-1]]; last=s.index[s.index<=tb][-1]
    if last<=ta: return 0.0   # stopped trading by the window start: earns SPY for the whole window
    r=s.loc[last]/pa-1
    if last<tb: r=(1+r)*(spy.loc[tb]/spy.loc[last])-1
    return r-(spy.loc[tb]/spy.loc[ta]-1)
W={"d0":(-1,0),"d0_1":(-1,1),"d0_4":(-1,4),"d0_9":(-1,9),"drift_5":(0,5),"drift_10":(0,10)}
for w,(a,b) in W.items():
    d[w]=[ret(P[r.symbol],int(r.i0)+a,int(r.i0)+b) if int(r.i0)+b<len(cal) else np.nan for r in d.itertuples()]
print("missing returns:",{w:int(d[w].isna().sum()) for w in W})
# ---- cells: group x year, under 30 joins next year (last joins previous)
def cells(df):
    lab=pd.Series(index=df.index,dtype=object)
    for g,gg in df.groupby("group"):
        yrs=sorted(gg.year.unique()); cur=[]; done=[]
        for y in yrs:
            cur.append(y)
            if (gg.year.isin(cur)).sum()>=30: done.append(cur); cur=[]
        if cur:
            if done: done[-1]+=cur
            else: done.append(cur)
        for c in done: lab[gg.index[gg.year.isin(c)]]=f"{g}:{c[0]}-{c[-1]}"
    return lab
d["cell"]=cells(d)
rng_seed=311; B=10000
def cell_rhos(df,sig,out,min_n=10):
    r=[]
    for c,g in df.groupby("cell"):
        g=g[[sig,out,"group"]].dropna()
        if len(g)<min_n or g[sig].nunique()<2: continue
        r.append((c,g.group.iloc[0],len(g),g[sig].rank().corr(g[out].rank())))
    return pd.DataFrame(r,columns=["cell","group","n","rho"])
def boot_stat(df,sigs,out,min_n=10):
    """event-weighted mean of within-cell Spearman for each signal, plus difference sigs[0]-sigs[1]; cells resampled within group"""
    tabs=[cell_rhos(df,s,out,min_n).set_index("cell") for s in sigs]
    common=tabs[0].index
    for t in tabs[1:]: common=common.intersection(t.index)
    tabs=[t.loc[common] for t in tabs]
    n=tabs[0].n.values; grp=tabs[0].group.values
    R=np.vstack([t.rho.values for t in tabs])
    est=(R*n).sum(1)/n.sum()
    rng=np.random.default_rng(rng_seed); bs=[]
    gi=[np.where(grp==g)[0] for g in np.unique(grp)]
    for _ in range(B):
        idx=np.concatenate([rng.choice(ix,len(ix),replace=True) for ix in gi])
        bs.append((R[:,idx]*n[idx]).sum(1)/n[idx].sum())
    bs=np.array(bs)
    res={"cells":int(len(common)),"events":int(n.sum())}
    for k,s in enumerate(sigs):
        res[s]=[round(float(est[k]),4),round(float(np.percentile(bs[:,k],2.5)),4),round(float(np.percentile(bs[:,k],97.5)),4)]
    if len(sigs)==2:
        dd=bs[:,0]-bs[:,1]; res["diff"]=[round(float(est[0]-est[1]),4),round(float(np.percentile(dd,2.5)),4),round(float(np.percentile(dd,97.5)),4)]
    return res
O={"n_events":int(len(d)),"cells":int(d.cell.nunique())}
O["main"]=boot_stat(d,["rating_score","base_good"],"d0_1")
for w in W: O[f"window_{w}"]=boot_stat(d,["rating_score","base_good"],w)
O["headline_10d"]=O["window_d0_9"]
O["good_score_main"]=boot_stat(d,["good_score","base_good"],"d0_1")
O["good_score_10d"]=boot_stat(d,["good_score","base_good"],"d0_9")
O["bad_score_main"]=boot_stat(d,["jev_good_bad","base_good"],"d0_1")
O["officer_only"]=boot_stat(d[d.group=="officer"],["rating_score","base_good"],"d0_1")
O["with_press_release"]=boot_stat(d[d.press],["rating_score","base_good"],"d0_1")
O["without_press_release"]=boot_stat(d[~d.press],["rating_score","base_good"],"d0_1")
O["no_nearby_earnings"]=boot_stat(d[~d.nearby_202],["rating_score","base_good"],"d0_1")
# month-cluster bootstrap for means
d["month"]=d.acc_et.dt.strftime("%Y-%m")
def mean_ci(df,out="d0_1"):
    m=df.groupby("month")[out].agg(["sum","count"]); s=m["sum"].values; c=m["count"].values
    rng=np.random.default_rng(rng_seed); bs=[]
    for _ in range(2000):
        i=rng.integers(0,len(s),len(s)); bs.append(s[i].sum()/c[i].sum())
    return [round(float(s.sum()/c.sum()*100),3),round(float(np.percentile(bs,2.5)*100),3),round(float(np.percentile(bs,97.5)*100),3),int(c.sum())]
O["mean_2d_pct_by_group"]={g:mean_ci(gg) for g,gg in d.groupby("group")}
O["mean_2d_pct_by_jev_answer"]={g:mean_ci(gg) for g,gg in d.groupby("rating_choice")}
O["mean_2d_pct_by_jev_answer_officer"]={g:mean_ci(gg) for g,gg in d[d.group=="officer"].groupby("rating_choice")}
# item lean alone, pooled within years
dy=d.assign(cell=d.year.astype(str),group="all",lean_good=-d.lean)
O["item_lean_within_year"]=boot_stat(dy,["lean_good"],"d0_1")
# top fifth minus bottom fifth per cell, by rating score
gaps=[]
for c,g in d.groupby("cell"):
    q=pd.qcut(g.rating_score.rank(method="first"),5,labels=False)
    gaps.append((c,g.group.iloc[0],len(g),g.d0_1[q==4].mean()-g.d0_1[q==0].mean()))
G=pd.DataFrame(gaps,columns=["cell","group","n","gap"])
rng=np.random.default_rng(rng_seed); bs=[]
gi=[np.where(G.group.values==x)[0] for x in G.group.unique()]
for _ in range(B):
    i=np.concatenate([rng.choice(ix,len(ix)) for ix in gi]); bs.append((G.gap.values[i]*G.n.values[i]).sum()/G.n.values[i].sum())
O["top_minus_bottom_fifth_2d_pct"]=[round(float((G.gap*G.n).sum()/G.n.sum()*100),3),round(float(np.percentile(bs,2.5)*100),3),round(float(np.percentile(bs,97.5)*100),3)]
# patterns: average return path day 0..+10 by item code, Jev answer, group x answer
for k in range(0,11): d[f"p{k}"]=[ret(P[r.symbol],int(r.i0)-1,int(r.i0)+k) if int(r.i0)+k<len(cal) else np.nan for r in d.itertuples()]
def path(df): return {"n":int(len(df)),"path_pct":[round(float(df[f"p{k}"].mean()*100),3) for k in range(11)],"d1_ci":mean_ci(df,"p1"),"d10_ci":mean_ci(df,"p9")}   # 10 trading days: day -1 close to day +9, as the headline
ex=d.assign(item=d.event_items.str.split(";")).explode("item")
O["pattern_by_item"]={i:path(g) for i,g in ex.groupby("item")}
O["pattern_by_jev_answer"]={a:path(g) for a,g in d.groupby("rating_choice")}
O["pattern_by_group_and_answer"]={f"{x}|{a}":path(g) for (x,a),g in d.groupby(["group","rating_choice"]) if len(g)>=20}
# by year
O["by_year"]={int(y):(lambda t:(round(float((t.rho*t.n).sum()/t.n.sum()),4) if len(t) else None))(cell_rhos(g,"rating_score","d0_1")) for y,g in d.groupby("year")}
late=d[d.acc_et>=pd.Timestamp("2026-09-10",tz="America/New_York")]
O["after_2026_09_10"]={"n":int(len(late)),"spearman":(round(float(late.rating_score.rank().corr(late.d0_1.rank())),4) if len(late)>2 else None)}
print(json.dumps(O,indent=1))
if mode=="save":
    json.dump(O,open(OUT+"summary.json","w"),indent=1)
    d.drop(columns=["acc_et"]).assign(accepted_et=d.acc_et.astype(str)).to_csv(OUT+"graded_events.csv",index=False)
    print("saved", sha(OUT+"summary.json")[:8])
