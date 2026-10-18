# ---- verification pack: configurable paths (statistical logic below is unchanged) ----
import os
F = os.path.join(os.environ.get("FILINGS", "filings"), "")  # frozen inputs, read only
OUT = os.path.join(os.environ.get("VERIFY_OUT", "verify_out/e10"), "")  # everything this script writes goes here
assert "/filings/experiments/" not in os.path.abspath(OUT) + "/", "OUT must not point into filings/experiments"
os.makedirs(OUT, exist_ok=True)
# -------------------------------------------------------------------------------------
import json, sys, numpy as np, pandas as pd
E=F+"experiments/E10-8k-events/"
des=pd.read_csv(E+"grading/design.csv",dtype={"event_id":str}); k=pd.read_csv(E+"labels/sealed/answer_key.csv")
sc=pd.read_csv(E+"jev/scores.csv",dtype={"event_id":str}); bl=pd.read_csv(E+"jev/baselines.csv",dtype={"event_id":str})
assert len(des)==len(k)==len(sc)==len(bl)==436 and set(des.event_id)==set(sc.event_id)==set(bl.event_id) and set(k.label_id)==set(des.label_id)
d=des.merge(k[["label_id","rating","rating_votes","rating_unanimous","size","size_unanimous"]],on="label_id")\
  .merge(sc.drop(columns="company"),on="event_id").merge(bl[["event_id","lean","net_tone","baseline_badness"]],on="event_id")
assert len(d)==436 and d.rating.notna().all()
d["cell"]=d.company+"/"+d.item_group
d["good_score"]=d.rating_p_good+d.rating_p_very_good
d["key_bad"]=d.rating.isin(["bad","very_bad"]); d["key_good"]=d.rating.isin(["good","very_good"])
def wauc(y,s,w):
    y=np.asarray(y,bool); s=np.asarray(s,float); w=np.asarray(w,float)
    sp,sn=s[y],s[~y]; wp,wn=w[y],w[~y]
    cmp=(sp[:,None]>sn[None,:])+0.5*(sp[:,None]==sn[None,:])
    return float((wp[:,None]*wn[None,:]*cmp).sum()/(wp.sum()*wn.sum()))
rng=np.random.default_rng(310); B=10000
def test(sub,ycol,a,b):
    s=d[sub].reset_index(drop=True); y=s[ycol].values; A=s[a].values.astype(float); Bv=b(s).values.astype(float); w=s.weight.values
    cells=[np.where(s.cell.values==c)[0] for c in s.cell.unique()]
    pt=(wauc(y,A,w),wauc(y,Bv,w)); g=[]
    for _ in range(B):
        i=np.concatenate([rng.choice(ix,len(ix)) for ix in cells])
        if y[i].all() or not y[i].any(): continue
        g.append(wauc(y[i],A[i],w[i])-wauc(y[i],Bv[i],w[i]))
    lo,hi=np.percentile(g,[2.5,97.5])
    return {"n":len(s),"positives":int(y.sum()),"auc_jev":pt[0],"auc_base":pt[1],"gap":pt[0]-pt[1],"interval_95":[lo,hi],"clear_of_zero":bool(lo>0),"draws_used":len(g)}
allm=pd.Series(True,index=d.index); off=d.item_group=="officer"
out={"key_rating":d.rating.value_counts().to_dict(),"key_by_group":pd.crosstab(d.item_group,d.rating).to_dict(),
     "jev_rating":d.rating_choice.value_counts().to_dict()}
out["main_bad"]=test(allm,"key_bad","bad_score",lambda s:s.baseline_badness)
out["good"]=test(allm,"key_good","good_score",lambda s:-s.baseline_badness)
out["officer_bad_vs_net_tone"]=test(off,"key_bad","bad_score",lambda s:s.net_tone)
out["main_bad_rating_score"]=test(allm,"key_bad","rating_score",lambda s:-s.baseline_badness) # Jev's -score is badness; flip below
out["main_bad_rating_score"]["note"]="Jev ranked by low rating_score; auc_jev here is for high score so 1-auc is the bad ranking"
nb=d[~d.item_group.eq("negative")]
out["bad_excl_negative_group"]=test(~d.item_group.eq("negative"),"key_bad","bad_score",lambda s:s.baseline_badness)
out["item_lean_only_auc"]=wauc(d.key_bad,d.lean,d.weight)
maj=d.rating.value_counts().idxmax()
out["five_way"]={"jev_acc":float((d.rating_choice==d.rating).mean()),"majority":maj,"majority_acc":float((d.rating==maj).mean()),
  "jev_bal":float(np.mean([(d.rating_choice[d.rating==c]==c).mean() for c in d.rating.unique()]))}
d["jev3"]=d.rating_choice.map({"very_bad":"bad","bad":"bad","neutral":"neutral","good":"good","very_good":"good"})
d["key3"]=d.rating.map({"very_bad":"bad","bad":"bad","neutral":"neutral","good":"good","very_good":"good"})
out["three_way_acc"]=float((d.jev3==d.key3).mean())
out["confusion"]=pd.crosstab(d.rating,d.rating_choice).to_dict()
jb=d.rating_choice.isin(["bad","very_bad"])
out["jev_says_bad"]={"n":int(jb.sum()),"right":int((jb&d.key_bad).sum()),"key_bad":int(d.key_bad.sum())}
out["size"]={"agree":float((d.size_choice==d["size"]).mean()),"majority":d["size"].value_counts().idxmax(),
  "majority_acc":float((d["size"]==d["size"].value_counts().idxmax()).mean()),"confusion":pd.crosstab(d["size"],d.size_choice).to_dict()}
pc={}
for c,g in d.groupby("company"):
    y=g.key_bad.values; r={"n":len(g),"bad":int(y.sum())}
    if 0<y.sum()<len(g): r.update(jev=wauc(y,g.bad_score,g.weight),base=wauc(y,g.baseline_badness,g.weight))
    pc[c]=r
out["per_company"]=pc
pg={}
for c,g in d.groupby("item_group"):
    y=g.key_bad.values; r={"n":len(g),"bad":int(y.sum())}
    if 0<y.sum()<len(g): r.update(jev=wauc(y,g.bad_score,g.weight),base=wauc(y,g.baseline_badness,g.weight))
    pg[c]=r
out["per_group"]=pg
out["bootstrap"]={"draws":B,"seed":310,"resample":"within company x item group"}
print(json.dumps(out,indent=1,default=float))
if len(sys.argv)>1:
    json.dump(out,open(OUT+"summary.json","w"),indent=1,default=float); d.to_csv(OUT+"graded_events.csv",index=False)
