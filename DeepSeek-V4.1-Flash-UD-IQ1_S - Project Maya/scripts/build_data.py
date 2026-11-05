#!/usr/bin/env python3
"""Build the published CSV/JSON record for one model file of the Stage E batch.

  build_data.py --side gguf --raw <dir of model-bench run dirs> --out <repo folder>

Reads the harness run dirs (results.jsonl, meta.json, summary.csv), copies them into
data/raw/ with stable names, and writes data/csv/averages.csv, data/csv/means.csv and
data/csv/facts.json. Counts are asserted, not assumed.
"""
import argparse
import csv
import hashlib
import json
import os
import shutil
import statistics as st
from pathlib import Path

DEPTHS = [20000, 60000, 100000]
ARMS = {"suf3": "prompt-lookup drafting on (--suffix-draft 3)",
        "suf0": "prompt-lookup drafting off (--suffix-draft 0)"}

ap = argparse.ArgumentParser()
ap.add_argument("--side", required=True, choices=["gguf", "exl3"])
ap.add_argument("--raw", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--slug", required=True)
a = ap.parse_args()

runs = sorted([p for p in Path(a.raw).iterdir()
               if p.is_dir() and {"gguf": "udiq1s", "exl3": "exl3mia"}[a.side] in p.name.lower()])
assert runs, f"no run dirs for side {a.side} in {a.raw}"

out = Path(a.out)
(out / "data/raw").mkdir(parents=True, exist_ok=True)
(out / "data/csv").mkdir(parents=True, exist_ok=True)

by_arm = {}
for r in runs:
    arm = "suf3" if "suf3" in r.name else "suf0"
    by_arm.setdefault(arm, []).append(r)

raw_files = []
means = []
for arm, dirs in sorted(by_arm.items()):
    for i, d in enumerate(sorted(dirs), 1):
        tag = f"{a.slug}-{arm}-run{i}"
        for src_name, ext in (("results.jsonl", "jsonl"), ("meta.json", "meta.json"), ("summary.csv", "summary.csv")):
            src = d / src_name
            assert src.exists(), f"{d} missing {src_name}"
            dst = out / "data/raw" / f"{tag}.{ext}"
            shutil.copyfile(src, dst)
            raw_files.append(dst)
        rows = [r for r in csv.DictReader(open(d / "summary.csv", newline="", encoding="utf-8-sig"))]
        rows = [r for r in rows if not r.get("error")]
        assert len(rows) == 3, f"{tag}: {len(rows)} depth rows"
        for r in rows:
            means.append(dict(side=a.side, arm=arm, run=i, depth=int(r["depth_k"]),
                              prefill=float(r["prefill_tps"]), decode=float(r["decode_tps"]),
                              ptok=int(r["ptok"]), gen=int(r["gen"]), book=r["book"]))

# same document sliced at each depth in every run: the comparability proof
for arm in ARMS:
    for dep in DEPTHS:
        books = {m["book"] for m in means if m["arm"] == arm and m["depth"] == dep}
        assert len(books) == 1, f"book mismatch {arm} {dep}: {books}"

avg_rows = []
for arm in sorted(ARMS):
    for dep in DEPTHS:
        v = [m for m in means if m["arm"] == arm and m["depth"] == dep]
        assert len(v) == 2, f"{arm} {dep}: {len(v)} runs"
        avg_rows.append(dict(
            arm=arm, depth_k=dep, runs=len(v),
            prefill_mean=round(st.mean(x["prefill"] for x in v), 1),
            prefill_min=round(min(x["prefill"] for x in v), 1),
            prefill_max=round(max(x["prefill"] for x in v), 1),
            decode_mean=round(st.mean(x["decode"] for x in v), 2),
            decode_min=round(min(x["decode"] for x in v), 2),
            decode_max=round(max(x["decode"] for x in v), 2),
            ptok=v[0]["ptok"], gen=v[0]["gen"]))

with open(out / "data/csv/averages.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(avg_rows[0]))
    w.writeheader()
    w.writerows(avg_rows)

with open(out / "data/csv/means.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["side", "arm", "run", "depth", "prefill", "decode", "ptok", "gen", "book"])
    w.writeheader()
    w.writerows(means)

meta = json.load(open(sorted(runs)[0] / "meta.json"))
facts = dict(
    side=a.side,
    recorded_runs=len(runs),
    measured_arms=len(means),
    failed=0,
    depths=DEPTHS,
    arms=ARMS,
    gen=means[0]["gen"],
    harness_meta=meta,
    runs=[{"arm": "suf3" if "suf3" in r.name else "suf0", "dir": r.name,
           "results_rows": sum(1 for _ in open(r / "results.jsonl"))} for r in runs],
)
json.dump(facts, open(out / "data/csv/facts.json", "w"), indent=1)

with open(out / "data/raw/SHA256SUMS", "w") as f:
    for p in raw_files:
        f.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n")

print(f"{a.side}: {len(runs)} runs, {len(means)} measured arms -> {out}")
for r in avg_rows:
    print("  {arm} {depth_k:6d}  prefill {prefill_mean:7.1f} [{prefill_min}-{prefill_max}]  "
          "decode {decode_mean:6.2f} [{decode_min}-{decode_max}]".format(**r))
