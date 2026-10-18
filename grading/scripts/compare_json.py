"""Compare a rerun's result with the published grading/summary.json, field by field.

Usage: python3 compare_json.py PUBLISHED.json RERUN [--tol 0]
RERUN is either a .json file or a script's stdout log; for a log, the last top-level
JSON object in it is used (so `grade` mode output can be compared without `save`).
Prints the sha256 of both files when RERUN is a .json, then every differing field.
Exit code 0 when identical (within --tol for numbers), 1 otherwise.
"""
import hashlib, json, math, sys

pub, rer = sys.argv[1], sys.argv[2]
tol = float(sys.argv[sys.argv.index("--tol") + 1]) if "--tol" in sys.argv else 0.0


def last_json(text):
    dec, i, last = json.JSONDecoder(), 0, None
    while True:
        j = text.find("{", i)
        if j < 0: return last
        if j == 0 or text[j - 1] == "\n":
            try:
                obj, end = dec.raw_decode(text, j); last = obj; i = end; continue
            except ValueError:
                pass
        i = j + 1


A = json.load(open(pub))
if rer.endswith(".json"):
    B = json.load(open(rer))
    ha, hb = (hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (pub, rer))
    print("sha256 published", ha); print("sha256 rerun    ", hb); print("byte-identical:", ha == hb)
else:
    B = last_json(open(rer).read())
diffs, n = [], [0]


def walk(a, b, path):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(map(str, a)) | set(map(str, b))):
            ka = {str(x): x for x in a}.get(k); kb = {str(x): x for x in b}.get(k)
            if ka is None or kb is None: diffs.append((path + "/" + k, a.get(ka), b.get(kb), "missing")); continue
            walk(a[ka], b[kb], path + "/" + k)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)): walk(x, y, f"{path}[{i}]")
    else:
        n[0] += 1
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
            same = (math.isnan(a) and math.isnan(b)) or abs(a - b) <= tol
        else:
            same = a == b
        if not same: diffs.append((path, a, b, ""))


walk(A, B, "")
print(f"leaf fields compared: {n[0]}; differing: {len(diffs)}")
for d in diffs[:50]: print("DIFF", *d)
sys.exit(1 if diffs else 0)
