#!/usr/bin/env python3
"""Build the DFlash2 drafting comparison on AJ-IQ2_XXS (Project Maya v1.1.15) from the raw records.

Reads data/raw/model-bench-aj-v1115-dflash-r{1,2,3}-results.jsonl plus the v1.1.15 side of
model-bench-aj-v1115-v1115-r{1,2,3}-results.jsonl (no drafting) and writes:
  data/csv/dflash-aj-v1115.csv         - both series, per depth, 3-run means
  data/csv/dflash-deltas-aj-v1115.csv  - per-depth deltas on unrounded means + sds

Assertions before writing: same book + sliced_tokens at every depth across all six batteries
(the drafting arm must see the identical prompts), three measured arms per depth per side, and an
accepted-draft count above zero in the DFlash2 arms (drafting actually engaged).
"""
import csv
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "data", "raw")
OUT = os.path.join(HERE, "data", "csv")

RUNS = {
    "no drafting": [f"model-bench-aj-v1115-v1115-r{i}-results.jsonl" for i in (1, 2, 3)],
    "DFlash2": [f"model-bench-aj-v1115-dflash-r{i}-results.jsonl" for i in (1, 2, 3)],
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
for d in depths:
    sets = {(r["book"], r["sliced_tokens"]) for k, v in per.items() if k[1] == d for r in v}
    assert len(sets) == 1, (d, sets)
    for engine in RUNS:
        rows = per[(engine, d)]
        assert len(rows) == 3, (engine, d, len(rows))
assert all(r["draft_n"] > 0 for r in per[("DFlash2", depths[0])]), "no drafts offered"
assert all(r["draft_n"] == 0 for r in per[("no drafting", depths[0])]), "unexpected drafts"


def mean(engine, d, field):
    return st.mean(r[field] for r in per[(engine, d)])


def sd(engine, d, field):
    return st.stdev(r[field] for r in per[(engine, d)])


def ptok(engine, d):
    return min(r["ptok"] for r in per[(engine, d)])


with open(os.path.join(OUT, "dflash-aj-v1115.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["engine", "depth_k", "ptok", "prefill_tps", "decode_tps"])
    for engine in ("no drafting", "DFlash2"):
        for d in depths:
            w.writerow([engine, d, ptok(engine, d), f"{mean(engine, d, 'prefill_tps'):.2f}",
                        f"{mean(engine, d, 'decode_tps'):.3f}"])

with open(os.path.join(OUT, "dflash-deltas-aj-v1115.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["depth_k", "decode_plain", "decode_dflash", "decode_pct", "decode_sd_plain",
                "decode_sd_dflash", "prefill_plain", "prefill_dflash", "prefill_pct",
                "draft_n_mean", "draft_acc_mean"])
    for d in depths:
        db, da = mean("no drafting", d, "decode_tps"), mean("DFlash2", d, "decode_tps")
        pb, pa = mean("no drafting", d, "prefill_tps"), mean("DFlash2", d, "prefill_tps")
        w.writerow([d, f"{db:.3f}", f"{da:.3f}", f"{100 * (da - db) / db:+.2f}",
                    f"{sd('no drafting', d, 'decode_tps'):.3f}", f"{sd('DFlash2', d, 'decode_tps'):.3f}",
                    f"{pb:.2f}", f"{pa:.2f}", f"{100 * (pa - pb) / pb:+.2f}",
                    f"{mean('DFlash2', d, 'draft_n'):.1f}", f"{mean('DFlash2', d, 'draft_acc'):.1f}"])

dp = [100 * (mean("DFlash2", d, "decode_tps") - mean("no drafting", d, "decode_tps"))
      / mean("no drafting", d, "decode_tps") for d in depths]
pp = [100 * (mean("DFlash2", d, "prefill_tps") - mean("no drafting", d, "prefill_tps"))
      / mean("no drafting", d, "prefill_tps") for d in depths]
print("wrote 2 tables")
print("decode mean {:+.1f}%  prefill mean {:+.1f}%".format(st.mean(dp), st.mean(pp)))
