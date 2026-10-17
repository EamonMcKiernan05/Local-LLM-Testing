#!/usr/bin/env python3
"""Build the engine-comparison tables (Maya v1.1.13 vs v1.1.15 on AJ-IQ2_XXS) from the raw model-bench records.

Reads data/raw/model-bench-aj-v1115-{v1113,v1115}-r{1,2,3}-results.jsonl and writes:
  data/csv/depth-aj-v1115.csv                 - v1.1.15 per-depth means (the chart's source)
  data/csv/version-aj-v1113-v1115.csv         - both engines, per depth, 3-run means
  data/csv/version-deltas-aj-v1113-v1115.csv  - per-depth deltas (computed on unrounded means) + sds

Assertions before writing anything: the same book and sliced_tokens at every depth across all six
batteries, exactly three measured arms per depth per engine, zero draft tokens on every arm.
"""
import csv
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "data", "raw")
OUT = os.path.join(HERE, "data", "csv")

RUNS = {
    "v1.1.13": [f"model-bench-aj-v1115-v1113-r{i}-results.jsonl" for i in (1, 2, 3)],
    "v1.1.15": [f"model-bench-aj-v1115-v1115-r{i}-results.jsonl" for i in (1, 2, 3)],
}

per = {}
for engine, files in RUNS.items():
    for fn in files:
        with open(os.path.join(RAW, fn), encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                if r.get("kind") != "arm":
                    continue
                per.setdefault((engine, r["depth_k"]), []).append(r)

depths = sorted({d for _, d in per})
assert len(depths) == 6, depths
books = {}
for d in depths:
    sets = {(r["book"], r["sliced_tokens"]) for k, v in per.items() if k[1] == d for r in v}
    assert len(sets) == 1, (d, sets)
    books[d] = sets.pop()
    for engine in RUNS:
        rows = per[(engine, d)]
        assert len(rows) == 3, (engine, d, len(rows))
        assert all(r["draft_n"] == 0 for r in rows), (engine, d, "draft tokens on a no-MTP quant")
    assert len(per[("v1.1.13", d)]) == 3 and len(per[("v1.1.15", d)]) == 3


def mean(engine, d, field):
    return st.mean(r[field] for r in per[(engine, d)])


def sd(engine, d, field):
    return st.stdev(r[field] for r in per[(engine, d)])


def ptok(engine, d):
    return min(r["ptok"] for r in per[(engine, d)])


with open(os.path.join(OUT, "depth-aj-v1115.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["depth_k", "ptok", "prefill_tps", "decode_tps"])
    for d in depths:
        w.writerow([d, ptok("v1.1.15", d), f"{mean('v1.1.15', d, 'prefill_tps'):.2f}",
                    f"{mean('v1.1.15', d, 'decode_tps'):.3f}"])

with open(os.path.join(OUT, "version-aj-v1113-v1115.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["engine", "depth_k", "ptok", "prefill_tps", "decode_tps"])
    for engine in ("v1.1.13", "v1.1.15"):
        for d in depths:
            w.writerow([engine, d, ptok(engine, d), f"{mean(engine, d, 'prefill_tps'):.2f}",
                        f"{mean(engine, d, 'decode_tps'):.3f}"])

with open(os.path.join(OUT, "version-deltas-aj-v1113-v1115.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["depth_k", "prefill_v1113", "prefill_v1115", "prefill_pct",
                "prefill_sd_v1113", "prefill_sd_v1115", "decode_v1113", "decode_v1115",
                "decode_pct", "decode_sd_v1113", "decode_sd_v1115"])
    for d in depths:
        pb, pa = mean("v1.1.13", d, "prefill_tps"), mean("v1.1.15", d, "prefill_tps")
        db, da = mean("v1.1.13", d, "decode_tps"), mean("v1.1.15", d, "decode_tps")
        w.writerow([d, f"{pb:.2f}", f"{pa:.2f}", f"{100 * (pa - pb) / pb:+.2f}",
                    f"{sd('v1.1.13', d, 'prefill_tps'):.2f}", f"{sd('v1.1.15', d, 'prefill_tps'):.2f}",
                    f"{db:.3f}", f"{da:.3f}", f"{100 * (da - db) / db:+.2f}",
                    f"{sd('v1.1.13', d, 'decode_tps'):.3f}", f"{sd('v1.1.15', d, 'decode_tps'):.3f}"])

pp = [100 * (mean("v1.1.15", d, "prefill_tps") - mean("v1.1.13", d, "prefill_tps"))
      / mean("v1.1.13", d, "prefill_tps") for d in depths]
dp = [100 * (mean("v1.1.15", d, "decode_tps") - mean("v1.1.13", d, "decode_tps"))
      / mean("v1.1.13", d, "decode_tps") for d in depths]
print("wrote 3 tables")
print("prefill mean {:+.1f}%  decode mean {:+.1f}%".format(st.mean(pp), st.mean(dp)))
