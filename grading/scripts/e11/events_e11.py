"""E11: build the event table (no returns). Writes OUT/events.pkl."""
# ---- verification pack: configurable paths (statistical logic below is unchanged) ----
import os
F = os.path.join(os.environ.get("FILINGS", "filings"), "")  # frozen inputs, read only
OUT = os.path.join(os.environ.get("VERIFY_OUT", "verify_out/e11"), "")  # everything this script writes goes here
assert "/filings/experiments/" not in os.path.abspath(OUT) + "/", "OUT must not point into filings/experiments"
os.makedirs(OUT, exist_ok=True)
# -------------------------------------------------------------------------------------
import json, sys, pandas as pd
from zoneinfo import ZoneInfo
NEG={"1.02","1.03","2.05","2.06","3.01","4.02"}
def group(items):
    s=set(items)
    if s&NEG: return "negative"
    if "4.01" in s: return "auditor"
    if s&{"1.01","2.01"}: return "deals"
    return "officer"
rows=[]
for l in open(F+"data/member_8k_events/member_8k_events.jsonl"):
    d=json.loads(l)
    rows.append(dict(event_id=d["event_id"],company=d["company"],cik=d["cik"],items=";".join(d["items"]),
        event_items=";".join(d["event_items"]),group=group(d["event_items"]),accepted_utc=d["accepted_utc"],
        has_202="2.02" in d["items"],nearby_202=len(d.get("nearby_202_listed_utc") or [])>0,
        press=d.get("press_release") is not None, truncated=d.get("truncated")))
ev=pd.DataFrame(rows)
ET=ZoneInfo("America/New_York")
ev["acc_et"]=pd.to_datetime(ev.accepted_utc,utc=True).dt.tz_convert(ET)
ev.to_pickle(OUT+"events.pkl")
print(len(ev)); print(ev.group.value_counts()); print(ev.has_202.sum(), ev.nearby_202.sum(), ev.press.sum())
