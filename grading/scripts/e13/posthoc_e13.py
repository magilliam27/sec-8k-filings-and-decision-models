"""E13 post-hoc figures, computed after grading (not part of the frozen design).
Writes OUT/posthoc.json with aggregates only: the leak check split by whether a press
release is attached, the 2-day correlations on filings without a press release, and the
proportional reading (expected change if name memory drove the signal).
Uses the same within-cell Spearman and cell bootstrap as grade_e13.py (10,000 draws, seed 313)."""
# ---- verification pack: configurable paths ----
import os
F = os.path.join(os.environ.get("FILINGS", "filings"), "")  # frozen inputs, read only
OUT = os.path.join(os.environ.get("VERIFY_OUT", "verify_out/e13"), "")
assert "/filings/experiments/" not in os.path.abspath(OUT) + "/", "OUT must not point into filings/experiments"
# -----------------------------------------------
import json, numpy as np, pandas as pd
E = F + "experiments/E13-name-masking/"
B = 10000; SEED = 313; CHANCE = 0.2
d = pd.read_csv(E + "grading/graded_events.csv", dtype={"event_id": str})
idt = pd.read_csv(E + "jev/identify/identify.csv", dtype={"event_id": str}).merge(d[["event_id", "press"]], on="event_id", how="left")

def cell_rhos(df, sig, out, min_n=10):
    r = []
    for c, g in df.groupby("cell"):
        g = g[[sig, out, "group"]].dropna()
        if len(g) < min_n or g[sig].nunique() < 2: continue
        r.append((c, g.group.iloc[0], len(g), g[sig].rank().corr(g[out].rank())))
    return pd.DataFrame(r, columns=["cell", "group", "n", "rho"])
def boot(df, sigs, out):
    tabs = [cell_rhos(df, s, out).set_index("cell") for s in sigs]
    common = tabs[0].index
    for t in tabs[1:]: common = common.intersection(t.index)
    tabs = [t.loc[common] for t in tabs]; n = tabs[0].n.values; grp = tabs[0].group.values
    R = np.vstack([t.rho.values for t in tabs]); est = (R * n).sum(1) / n.sum()
    rng = np.random.default_rng(SEED); gi = [np.where(grp == g)[0] for g in np.unique(grp)]; bs = []
    for _ in range(B):
        idx = np.concatenate([rng.choice(ix, len(ix), replace=True) for ix in gi]); bs.append((R[:, idx] * n[idx]).sum(1) / n[idx].sum())
    bs = np.array(bs); ci = lambda v, e: [round(float(e), 4), round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]
    res = {"cells": int(len(common)), "events": int(n.sum())}
    for k, s in enumerate(sigs): res[s] = ci(bs[:, k], est[k])
    for k, s in enumerate(sigs[:-1]): res[f"{s}_minus_{sigs[-1]}"] = ci(bs[:, k] - bs[:, -1], est[k] - est[-1])
    return res

O = {"note": "post-hoc, computed after grading; not part of the frozen design"}
O["leak_check_by_press_release"] = {f"{v}_{'with' if p else 'without'}_press_release": {"events": int(len(g)), "accuracy": round(float(g.correct.mean()), 4)}
                                    for (v, p), g in idt.groupby(["version", "press"])}
nopress = d[~d.press.astype(bool)]
O["no_press_release_2day"] = boot(nopress, ["name_score", "deep_score", "rating_score"], "d0_1")
acc = {v: float(g.correct.mean()) for v, g in idt.groupby("version")}
acc_np = {v: float(g.correct.mean()) for v, g in idt[~idt.press.astype(bool)].groupby("version")}
S = json.load(open(E + "grading/summary.json"))["main_2day"]
rows = [("name_mask", acc["name"], S["rating_score"][0], S["name_score_minus_rating_score"]),
        ("deep_mask", acc["deep"], S["rating_score"][0], S["deep_score_minus_rating_score"]),
        ("deep_mask_no_press_release", acc_np["deep"], O["no_press_release_2day"]["rating_score"][0], O["no_press_release_2day"]["deep_score_minus_rating_score"])]
O["proportional_reading"] = {"method": "share lost = 1 - (accuracy - 0.2) / 0.8, correcting for guessing among five; expected change = -(share lost) x the same filings' E11 correlation",
    **{k: {"identification_accuracy": round(a, 4), "share_lost": round(1 - (a - CHANCE) / (1 - CHANCE), 4), "e11_base": round(b, 4),
           "expected_change": round(-(1 - (a - CHANCE) / (1 - CHANCE)) * b, 4), "observed_change": obs} for k, a, b, obs in rows}}
os.makedirs(OUT, exist_ok=True)
json.dump(O, open(OUT + "posthoc.json", "w"), indent=1)
print(json.dumps(O, indent=1))
