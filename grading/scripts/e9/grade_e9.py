# ---- verification pack: configurable paths (statistical logic below is unchanged) ----
import os
F = os.path.join(os.environ.get("FILINGS", "filings"), "")  # frozen inputs, read only
OUT = os.path.join(os.environ.get("VERIFY_OUT", "verify_out/e9"), "")  # everything this script writes goes here
assert "/filings/experiments/" not in os.path.abspath(OUT) + "/", "OUT must not point into filings/experiments"
os.makedirs(OUT, exist_ok=True)
# -------------------------------------------------------------------------------------
import json, sys, numpy as np, pandas as pd
E=F+"experiments/E9-direction-confirm/"
des=pd.read_csv(E+"grading/design.csv"); k=pd.read_csv(E+"labels/sealed/answer_key.csv")
sc=pd.read_csv(E+"jev/scores.csv"); bl=pd.read_csv(E+"jev/baselines.csv")
assert len(sc)==len(bl)==len(des)==len(k)==300 and set(sc.pair_id)==set(des.pair_id)==set(bl.pair_id) and set(k.label_id)==set(des.label_id)
yn={"yes":True,"no":False,True:True,False:False,"True":True,"False":False}
for c in ["new_risk","changed"]: k[c]=k[c].map(yn)
d=des[["label_id","company","pair_id","stratum","weight"]].merge(k[["label_id","new_risk","changed","direction","finer","direction_votes","direction_unanimous","finer_unanimous"]],on="label_id")\
  .merge(sc.drop(columns="company"),on="pair_id").merge(bl[["pair_id","neg_change","neg_count_change","word_balance"]],on="pair_id")
assert len(d)==300
d["cell"]=d.company+"/"+d.stratum
nomaj=~d.direction.isin(["worse","better","neutral"])
print("no-majority direction rows:",d.loc[nomaj,["label_id","direction","direction_votes"]].to_dict("records"))
d=d[d.label_id!="J227"].reset_index(drop=True)
assert d.direction.isin(["worse","better","neutral"]).all()
def wauc(y,s,w):
    y=np.asarray(y,bool); s=np.asarray(s,float); w=np.asarray(w,float)
    sp,sn=s[y],s[~y]; wp,wn=w[y],w[~y]
    cmp=(sp[:,None]>sn[None,:])+0.5*(sp[:,None]==sn[None,:])
    return float((wp[:,None]*wn[None,:]*cmp).sum()/(wp.sum()*wn.sum()))
rng=np.random.default_rng(309); B=10000
def test(sub,y,a,b):
    s=d[sub].reset_index(drop=True); y=y(s).values
    A=a(s).values.astype(float); Bv=b(s).values.astype(float); w=s.weight.values
    cells=[np.where(s.cell.values==c)[0] for c in s.cell.unique()]
    pt=(wauc(y,A,w),wauc(y,Bv,w)); g=[]
    for _ in range(B):
        i=np.concatenate([rng.choice(ix,len(ix)) for ix in cells])
        if y[i].all() or not y[i].any(): continue
        g.append(wauc(y[i],A[i],w[i])-wauc(y[i],Bv[i],w[i]))
    lo,hi=np.percentile(g,[2.5,97.5])
    return {"n":len(s),"positives":int(y.sum()),"auc_jev":pt[0],"auc_base":pt[1],"gap":pt[0]-pt[1],"interval_95":[lo,hi],"clear_of_zero":bool(lo>0),"draws_used":len(g)}
chg=(d.changed&~d.new_risk)
def wacc(sub,pred,true):
    s=d[sub]; return float((s.weight*(s[pred]==s[true])).sum()/s.weight.sum())
def bacc(sub,pred,true):
    s=d[sub]; r=[]
    for c in s[true].unique():
        m=s[true]==c; r.append((s.weight[m]*(s[pred][m]==c)).sum()/s.weight[m].sum())
    return float(np.mean(r))
d["finer_as_dir"]=d.change_kind_choice.map({"materialized":"worse","new_exposure":"worse","escalated":"worse","eased":"better","neutral":"neutral"})
W=lambda s:s.direction=="worse"
out={"excluded":["J227"],"key_counts_all":d.direction.value_counts().to_dict(),"key_counts_main":d[chg].direction.value_counts().to_dict(),
 "finer_counts_main":d[chg].finer.value_counts().to_dict(),"new_risks":int(d.new_risk.sum()),"changed":int(d.changed.sum())}
out["main_worse_vs_word_balance"]=test(chg,W,lambda s:s.direction_p_worse,lambda s:s.word_balance)
out["worse_vs_lm_count_change"]=test(chg,W,lambda s:s.direction_p_worse,lambda s:s.neg_count_change)
out["worse_vs_lm_share_change"]=test(chg,W,lambda s:s.direction_p_worse,lambda s:s.neg_change)
nb=int((d[chg].direction=="better").sum())
out["better_main_vs_minus_word_balance"]=test(chg,lambda s:s.direction=="better",lambda s:s.direction_p_better,lambda s:-s.word_balance) if nb>=10 else {"skipped":nb}
allm=pd.Series(True,index=d.index)
out["worse_all_vs_word_balance"]=test(allm,W,lambda s:s.direction_p_worse,lambda s:s.word_balance)
for nm,sub in [("main",chg),("all",allm)]:
    s=d[sub]; maj=s.groupby("direction").weight.sum().idxmax(); fmaj=s.groupby("finer").weight.sum().idxmax()
    jw=s.direction_choice=="worse"
    out[f"three_way_{nm}"]={"jev_acc":wacc(sub,"direction_choice","direction"),"jev_bal":bacc(sub,"direction_choice","direction"),
      "majority_class":maj,"majority_acc":float(s.weight[s.direction==maj].sum()/s.weight.sum()),
      "jev_says_worse":int(jw.sum()),"jev_worse_right":int((jw&(s.direction=="worse")).sum()),
      "key_worse":int((s.direction=="worse").sum()),
      "finer_jev_acc":wacc(sub,"change_kind_choice","finer"),"finer_jev_bal":bacc(sub,"change_kind_choice","finer"),
      "finer_majority":fmaj,"finer_majority_acc":float(s.weight[s.finer==fmaj].sum()/s.weight.sum())}
out["confusion_main"]=pd.crosstab(d[chg].direction,d[chg].direction_choice).to_dict()
out["confusion_all"]=pd.crosstab(d.direction,d.direction_choice).to_dict()
out["confusion_finer_all"]=pd.crosstab(d.finer,d.change_kind_choice).to_dict()
out["jev_self_consistency"]=int((d.finer_as_dir==d.direction_choice).sum())
nr=d[d.new_risk]; out["new_risks_dir"]={"n":len(nr),"key_worse":int((nr.direction=="worse").sum()),"jev_worse":int((nr.direction_choice=="worse").sum())}
un=d[~d.changed]; out["unchanged"]={"n":len(un),"key":un.direction.value_counts().to_dict(),"jev":un.direction_choice.value_counts().to_dict()}
pc={}
for c,g in d[chg].groupby("company"):
    y=(g.direction=="worse").values; r={"n":len(g),"worse":int(y.sum())}
    if 0<y.sum()<len(g): r.update(jev=wauc(y,g.direction_p_worse,g.weight),word_balance=wauc(y,g.word_balance,g.weight),lm_count=wauc(y,g.neg_count_change,g.weight))
    pc[c]=r
out["per_company_main"]=pc
out["bootstrap"]={"draws":B,"seed":309,"resample":"within company x stratum"}
print(json.dumps(out,indent=1,default=float))
if len(sys.argv)>1:
    json.dump(out,open(OUT+"summary.json","w"),indent=1,default=float); d.to_csv(OUT+"graded_risks.csv",index=False)
