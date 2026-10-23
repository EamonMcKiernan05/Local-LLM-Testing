#!/usr/bin/env python3
"""Build the DeepSeek-V4.1-Flash-1017 / Maya-XS (IQ1_S) 128k dataset from the measured model-bench runs in data/raw.

Rules:
 - Only the run1 and run2 records count. The burn battery is excluded by
   design: it exists to warm the expert caches after the fresh load.
 - An arm is an ANOMALY and is excluded only if it did not complete
   (gen != 400), if the two runs sliced a different document at that depth
   (book mismatch = not comparable), or if its run is missing.
 - Every value comes from the raw results.jsonl. Nothing is typed in by hand.
"""
import json, csv, pathlib, sys

BASE = pathlib.Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
RUNS = ["model-bench-ds4-maya-xs-128k-run1", "model-bench-ds4-maya-xs-128k-run2"]
GEN = 400


def load(stem):
    out = {}
    for line in (RAW / ("%s-results.jsonl" % stem)).read_text().splitlines():
        r = json.loads(line)
        if r.get("kind") != "arm":
            continue
        out[int(r["sliced_tokens"])] = r
    return out

runs = {run: load(run) for run in RUNS}
depths = sorted(set.intersection(*[set(v) for v in runs.values()]))
rows, excluded = [], []

for depth in depths:
    a, b = runs[RUNS[0]][depth], runs[RUNS[1]][depth]
    if a["gen"] != GEN or b["gen"] != GEN:
        excluded.append((depth, "gen %s/%s != %s" % (a["gen"], b["gen"], GEN)))
        continue
    if a["book"] != b["book"] or a["sliced_tokens"] != b["sliced_tokens"]:
        excluded.append((depth, "book/slice mismatch %s vs %s" % (a["book"], b["book"])))
        continue
    pa, pb = float(a["prefill_tps"]), float(b["prefill_tps"])
    da, db = float(a["decode_tps"]), float(b["decode_tps"])
    rows.append(dict(
        depth=int(depth), ptok=int(a["ptok"]), book=a["book"],
        prefill_run1=round(pa, 2), prefill_run2=round(pb, 2), prefill_mean=round((pa + pb) / 2, 2),
        prefill_peak=round(max(pa, pb), 2), prefill_spread_pct=round(100 * abs(pa - pb) / ((pa + pb) / 2), 1),
        decode_run1=round(da, 2), decode_run2=round(db, 2), decode_mean=round((da + db) / 2, 2),
        decode_peak=round(max(da, db), 2), decode_spread_pct=round(100 * abs(da - db) / ((da + db) / 2), 1),
        gpu0_used_mib=int(({e["idx"]: e for e in (a.get("gpus") or [])}.get(0) or {}).get("used_mib") or 0),
        gpu1_used_mib=int(({e["idx"]: e for e in (a.get("gpus") or [])}.get(1) or {}).get("used_mib") or 0),
        method=a.get("method"),
    ))

if not rows:
    sys.exit("no comparable arms")

with open(BASE / "data" / "csv" / "averages.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

for depth, why in excluded:
    print("EXCLUDED depth %d: %s" % (depth, why))
print("rows:", len(rows), "| books:", [r["book"] for r in rows])
print("prefill peak overall: %.2f tok/s" % max(r["prefill_peak"] for r in rows))
print("decode peak overall:  %.2f tok/s" % max(r["decode_peak"] for r in rows))
print("mean of depth means: prefill %.2f, decode %.2f" % (
    sum(r["prefill_mean"] for r in rows) / len(rows), sum(r["decode_mean"] for r in rows) / len(rows)))
