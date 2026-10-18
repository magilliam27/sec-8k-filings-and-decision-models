"""E13 grading, frozen with experiments/E13-name-masking/CARD.md before any masked Jev score exists.
Usage: grade_e13.py check -> scores joined, counts and agreement only, no returns read
       grade_e13.py grade -> full result printed
       grade_e13.py save  -> also written to OUT (originally E13 grading/)
Returns, cells and the original rating are E11's frozen graded_events.csv; only the masked
ratings are new."""
# ---- verification pack: configurable paths (statistical logic below is unchanged) ----
import os
F = os.path.join(os.environ.get("FILINGS", "filings"), "")  # frozen inputs, read only
OUT = os.path.join(os.environ.get("VERIFY_OUT", "verify_out/e13"), "")  # everything this script writes goes here
assert "/filings/experiments/" not in os.path.abspath(OUT) + "/", "OUT must not point into filings/experiments"
# -------------------------------------------------------------------------------------
import sys, json, hashlib, numpy as np, pandas as pd
E11 = F + "experiments/E11-8k-returns/"; E = F + "experiments/E13-name-masking/"
mode = sys.argv[1]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
B = 10000; SEED = 313
ARMS = ["name", "deep"]
WINDOWS = {"d0": "day 0", "d0_1": "2 days (main)", "d0_4": "5 days", "d0_9": "10 days", "drift_5": "drift day 0 close to +5", "drift_10": "drift day 0 close to +10"}

# ---- join (no returns used in check mode)
key = ["event_id", "group", "cell", "year", "rating_choice", "rating_score", "base_good", "accepted_utc"]
d = pd.read_csv(E11 + "grading/graded_events.csv", dtype={"event_id": str})
assert len(d) == 26962
for arm in ARMS:
    s = pd.read_csv(E + f"jev/{arm}/scores.csv", dtype={"event_id": str})[["event_id", "rating_choice", "rating_score", "bad_score"]]
    s.columns = ["event_id", f"{arm}_choice", f"{arm}_score", f"{arm}_bad"]
    assert len(s) == 26962 and s.event_id.is_unique
    d = d.merge(s, on="event_id", how="left", validate="1:1")
    assert d[f"{arm}_score"].notna().all(), arm
O = {"n_events": int(len(d)), "inputs": {
    "E11 graded_events.csv": sha(E11 + "grading/graded_events.csv"),
    **{f"jev/{a}/scores.csv": sha(E + f"jev/{a}/scores.csv") for a in ARMS}}}
O["answers"] = {c: d[c].value_counts().to_dict() for c in ["rating_choice"] + [f"{a}_choice" for a in ARMS]}
O["agreement_with_original"] = {a: {"same_answer": round(float((d[f"{a}_choice"] == d.rating_choice).mean()), 4),
                                    "score_rank_corr": round(float(d[f"{a}_score"].rank().corr(d.rating_score.rank())), 4)} for a in ARMS}
rd = E + "jev/redraw/scores.csv"
try:
    r = pd.read_csv(rd, dtype={"event_id": str})[["event_id", "rating_choice", "rating_score"]].rename(columns={"rating_choice": "re_choice", "rating_score": "re_score"})
    x = d.merge(r, on="event_id")
    O["redraw_control"] = {"events": int(len(x)),
        "same_answer_original_vs_redraw": round(float((x.re_choice == x.rating_choice).mean()), 4),
        "score_rank_corr_original_vs_redraw": round(float(x.re_score.rank().corr(x.rating_score.rank())), 4),
        **{f"same_answer_original_vs_{a}_on_these": round(float((x[f"{a}_choice"] == x.rating_choice).mean()), 4) for a in ARMS},
        **{f"score_rank_corr_original_vs_{a}_on_these": round(float(x[f"{a}_score"].rank().corr(x.rating_score.rank())), 4) for a in ARMS}}
except FileNotFoundError:
    O["redraw_control"] = "missing"
idf = E + "jev/identify/identify.csv"
try:
    idt = pd.read_csv(idf, dtype={"event_id": str})
    leak = {}
    for v, g in idt.groupby("version"):
        comp = g.groupby("company")["correct"].agg(["sum", "count"]); s_, c_ = comp["sum"].values, comp["count"].values
        rng = np.random.default_rng(SEED); bs = []
        for _ in range(B):
            i = rng.integers(0, len(s_), len(s_)); bs.append(s_[i].sum() / c_[i].sum())
        leak[v] = {"events": int(len(g)), "accuracy": round(float(g.correct.mean()), 4),
                   "interval": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)],
                   "mean_p_truth": round(float(g.p_truth.mean()), 4),
                   "hides_filer": bool(np.percentile(bs, 97.5) < 0.5)}
    O["leak_check"] = {"chance": 0.2, **leak}
except FileNotFoundError:
    O["leak_check"] = "missing"
if mode == "check":
    print(json.dumps(O, indent=1)); sys.exit()

# ---- grading (E11's statistic: Spearman within item group x year cell, weighted by events,
# 10,000 bootstrap draws of whole cells within item group; paired, so differences share draws)
def cell_rhos(df, sig, out, min_n=10):
    r = []
    for c, g in df.groupby("cell"):
        g = g[[sig, out, "group"]].dropna()
        if len(g) < min_n or g[sig].nunique() < 2: continue
        r.append((c, g.group.iloc[0], len(g), g[sig].rank().corr(g[out].rank())))
    return pd.DataFrame(r, columns=["cell", "group", "n", "rho"])
def boot(df, sigs, out, pairs):
    tabs = [cell_rhos(df, s, out).set_index("cell") for s in sigs]
    common = tabs[0].index
    for t in tabs[1:]: common = common.intersection(t.index)
    tabs = [t.loc[common] for t in tabs]; n = tabs[0].n.values; grp = tabs[0].group.values
    R = np.vstack([t.rho.values for t in tabs]); est = (R * n).sum(1) / n.sum()
    rng = np.random.default_rng(SEED); gi = [np.where(grp == g)[0] for g in np.unique(grp)]; bs = []
    for _ in range(B):
        idx = np.concatenate([rng.choice(ix, len(ix), replace=True) for ix in gi]); bs.append((R[:, idx] * n[idx]).sum(1) / n[idx].sum())
    bs = np.array(bs); res = {"cells": int(len(common)), "events": int(n.sum())}
    ci = lambda v, e: [round(float(e), 4), round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]
    for k, s in enumerate(sigs): res[s] = ci(bs[:, k], est[k])
    for a, b in pairs:
        i, j = sigs.index(a), sigs.index(b); res[f"{a}_minus_{b}"] = ci(bs[:, i] - bs[:, j], est[i] - est[j])
    return res
SIGS = ["name_score", "deep_score", "rating_score", "base_good"]
PAIRS = [("name_score", "rating_score"), ("deep_score", "rating_score"), ("name_score", "base_good"), ("deep_score", "base_good")]
O["main_2day"] = boot(d, SIGS, "d0_1", PAIRS)
O["windows"] = {w: boot(d, SIGS, w, PAIRS[:2]) for w in WINDOWS}
O["by_period"] = {p: boot(d[(d.year >= lo) & (d.year <= hi)], SIGS[:3], "d0_1", PAIRS[:2])
                  for p, (lo, hi) in {"2013-2017": (2013, 2017), "2018-2021": (2018, 2021), "2022-2026": (2022, 2026)}.items()}
raw = {}
with open(F + "data/member_8k_events/member_8k_events.jsonl", encoding="utf-8") as h:
    for line in h:
        j = json.loads(line); raw[j["event_id"]] = j["prior_revenue_usd"]
d["revenue"] = d.event_id.map(raw)
d["size_third"] = pd.qcut(d.revenue.rank(method="first"), 3, labels=["small", "middle", "large"])
O["by_size_third"] = {str(t): boot(g, SIGS[:3], "d0_1", PAIRS[:2]) for t, g in d[d.revenue.notna()].groupby("size_third", observed=True)}
O["officer_only"] = boot(d[d.group == "officer"], SIGS, "d0_1", PAIRS)
late = d[pd.to_datetime(d.accepted_utc) >= pd.Timestamp("2026-09-10", tz="UTC")]
O["after_2026_09_10"] = {"events": int(len(late)), **{s: round(float(late[s].rank().corr(late.d0_1.rank())), 4) for s in SIGS[:3]}}
def mean_ci(df, out):
    m = df.groupby("month")[out].agg(["sum", "count"]); s_ = m["sum"].values; c_ = m["count"].values
    rng = np.random.default_rng(SEED); bs = []
    for _ in range(2000):
        i = rng.integers(0, len(s_), len(s_)); bs.append(s_[i].sum() / c_[i].sum())
    return [round(float(s_.sum() / c_.sum() * 100), 3), round(float(np.percentile(bs, 2.5) * 100), 3), round(float(np.percentile(bs, 97.5) * 100), 3), int(c_.sum())]
O["mean_2d_pct_by_answer"] = {a: {k: mean_ci(g, "d0_1") for k, g in d.groupby(f"{a}_choice" if a != "original" else "rating_choice")} for a in ["original"] + ARMS}
O["officer_bad_2d_pct"] = {a: mean_ci(d[(d.group == "officer") & (d[f"{a}_choice" if a != "original" else "rating_choice"] == "bad")], "d0_1") for a in ["original"] + ARMS}
print(json.dumps(O, indent=1))
if mode == "save":
    os.makedirs(OUT, exist_ok=True)
    json.dump(O, open(OUT + "summary.json", "w"), indent=1)
    d.drop(columns=[c for c in d.columns if c.startswith("p") and c[1:].isdigit()]).to_csv(OUT + "graded_events.csv", index=False)
    print("saved", sha(OUT + "summary.json")[:8])
