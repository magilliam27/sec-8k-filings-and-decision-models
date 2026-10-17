"""Verification pack: recompute sha256 of the frozen inputs and outputs of E7, E10 and E11.

Part 1 checks every shortened hash a CARD.md states (prefix...suffix) against the file.
Part 2 checks every full hash recorded in the data manifests, the Questions lane's
meta.json files and data/e7_prices/SHA256SUMS. Read only: writes nothing but stdout.
Usage: python3 check_hashes.py [FILINGS_ROOT]      (default ./filings)
"""
import hashlib, json, os, sys

F = os.path.join(sys.argv[1] if len(sys.argv) > 1 else "filings", "")
X = F + "experiments/"
_cache = {}


def sha(path):
    if path not in _cache:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 22), b""):
                h.update(block)
        _cache[path] = h.hexdigest()
    return _cache[path]


# (experiment, path under filings/, hash as the card states it: prefix and suffix around the ellipsis)
CARD = [
    ("E7", "experiments/E7-returns/signals/report_signals.csv", "1e699aa7", "574a"),
    ("E7", "experiments/E7-returns/signals/risk_pairs.csv", "e55a1192", "72a5"),
    ("E7", "experiments/E7-returns/jev/worse_share.csv", "6a560cd3", "c98"),
    ("E10", "data/e10_8k_events/8k_events.jsonl", "4ef25543", "0a581"),
    ("E10", "experiments/E10-8k-events/sample_sheet.csv", "fe13b88b", "e6a9"),
    ("E10", "experiments/E10-8k-events/events.csv", "4660e48f", "da80"),
    ("E10", "experiments/E10-8k-events/grading/design.csv", "c663706e", "6fa"),
    ("E10", "experiments/E10-8k-events/jev/scores.csv", "c71e864f", "d6ee"),
    ("E10", "experiments/E10-8k-events/jev/baselines.csv", "a122bf9b", "3fc0"),
    ("E10", "experiments/E10-8k-events/labels/sealed/answer_key.csv", "35023d07", "50e3"),
    ("E11", "data/member_8k_events.r1.json", "f4029460", "3bb2"),
    ("E11", "data/member_8k_events/member_8k_events.jsonl", "04172c9b", "931f"),
    ("E11", "experiments/E11-8k-returns/events.csv", "f885c806", "0b3b"),
    ("E11", "experiments/E11-8k-returns/grading/joins.csv", "685fd126", "b02"),
    ("E11", "experiments/E11-8k-returns/jev/baselines.csv", "9a6296a9", "1bdda"),
    ("E11", "experiments/E11-8k-returns/jev/scores.csv", "eb56f1c8", "d05b"),
    ("E11", "experiments/E11-8k-returns/jev/answers/rating.jsonl", "8b3456b9", "3bfc"),
    # not on the card: the 8-char prefixes the Lead's `grade_e11.py save` printed
    # ("saved 6f8455ce" for the corrected run of 17 Oct 03:41Z, "saved 4d84b3de" for v1, kept as summary_v1.json)
    ("E11", "experiments/E11-8k-returns/grading/summary.json", "6f8455ce", ""),
    ("E11", "experiments/E11-8k-returns/grading/summary_v1.json", "4d84b3de", ""),
]

print("## Part 1: hashes stated on the cards")
print("| exp | file | stated | computed | match |")
print("|---|---|---|---|---|")
bad1 = 0
for exp, rel, pre, suf in CARD:
    p = F + rel
    if not os.path.exists(p):
        print(f"| {exp} | {rel} | {pre}…{suf} | MISSING | no |"); bad1 += 1; continue
    h = sha(p)
    ok = h.startswith(pre) and h.endswith(suf)
    note = "yes" if ok else "NO"
    if not ok and h.startswith(pre) and suf and suf in h[-len(suf) - 2:]:
        note = f"prefix yes; card's suffix is digits {suf!r} one place early (typo), full hash ends {h[-6:]}"
    bad1 += not ok
    print(f"| {exp} | `{rel}` | {pre}…{suf} | {h[:8]}…{h[-max(len(suf), 4):]} | {note} |")

print("\n## Part 2: full hashes in manifests and meta files")
checks = []  # (source, path, expected)


def manifest(mpath, root):
    m = json.load(open(mpath))
    for f in m["files"]:
        checks.append((os.path.relpath(mpath, F), root + f["path"], f["sha256"]))


manifest(F + "data/member_8k_events.r1.json", F + "data/member_8k_events/")
manifest(F + "data/e10_8k_events.r1.json", F + "data/e10_8k_events/")
manifest(F + "data/e7_member_10k_risk_factors.r1.json", F + "data/e7_sp500_10k/r1/")
manifest(F + "data/e7_member_10k_risk_factors.r2.json", F + "data/e7_sp500_10k/r2/")


def meta(mpath, resolve):
    m = json.load(open(mpath))
    for k, v in m.get("sha256", {}).items():
        p = resolve(k)
        if p is None:
            checks.append((os.path.relpath(mpath, F), "(" + k + ": no file named)", v)); continue
        checks.append((os.path.relpath(mpath, F), p, v))


def jev_resolver(exp, data_jsonl):
    def r(k):
        if k == "events": return data_jsonl
        if k == "sample": return X + exp + "/events.csv"
        if k in ("lm_dictionary", "leave_out"): return None
        for base in (X + exp + "/jev/", X + exp + "/"):
            if os.path.exists(base + k): return base + k
        return X + exp + "/jev/" + k
    return r


meta(X + "E11-8k-returns/jev/scores.meta.json", jev_resolver("E11-8k-returns", F + "data/member_8k_events/member_8k_events.jsonl"))
meta(X + "E11-8k-returns/jev/baselines.meta.json", jev_resolver("E11-8k-returns", F + "data/member_8k_events/member_8k_events.jsonl"))
meta(X + "E10-8k-events/jev/scores.meta.json", jev_resolver("E10-8k-events", F + "data/e10_8k_events/8k_events.jsonl"))
meta(X + "E10-8k-events/jev/baselines.meta.json", jev_resolver("E10-8k-events", F + "data/e10_8k_events/8k_events.jsonl"))
meta(X + "E7-returns/jev/jev.meta.json", jev_resolver("E7-returns", None))


def sig_resolver(k):
    if k.endswith(".json"): return F + "data/" + k
    if k.startswith(("r1/", "r2/")): return F + "data/e7_sp500_10k/" + k
    return X + "E7-returns/" + k


meta(X + "E7-returns/signals/signals.meta.json", sig_resolver)
for line in open(F + "data/e7_prices/SHA256SUMS"):
    h, p = line.split(None, 1)
    checks.append(("data/e7_prices/SHA256SUMS", F + "data/e7_prices/" + p.strip().lstrip("./").lstrip("*"), h))

summary = {}
fails = []
for src, p, h in checks:
    s = summary.setdefault(src, [0, 0, 0])
    if p.startswith("("):
        s[2] += 1; continue
    if not os.path.exists(p):
        s[1] += 1; fails.append((src, p, h, "MISSING")); continue
    got = sha(p)
    if got == h: s[0] += 1
    else: s[1] += 1; fails.append((src, p, h, got))
print("| source | match | fail | not a file |")
print("|---|---|---|---|")
for src, (a, b, c) in summary.items():
    print(f"| `{src}` | {a} | {b} | {c} |")
for src, p, h, got in fails:
    print(f"FAIL {src}: {os.path.relpath(p, F)} expected {h} got {got}")
print(f"\nPart 1: {len(CARD) - bad1}/{len(CARD)} match. Part 2: {sum(v[0] for v in summary.values())} match, {len(fails)} fail.")
print("\n## Computed hashes of grading outputs (no stated hash on the cards)")
for rel in ["E7-returns/grading/summary.json", "E7-returns/grading/graded_filings.csv",
            "E10-8k-events/grading/summary.json", "E10-8k-events/grading/graded_events.csv",
            "E11-8k-returns/grading/summary.json", "E11-8k-returns/grading/graded_events.csv",
            "E11-8k-returns/grading/summary_v1.json"]:
    print(f"{sha(X + rel)}  experiments/{rel}")
