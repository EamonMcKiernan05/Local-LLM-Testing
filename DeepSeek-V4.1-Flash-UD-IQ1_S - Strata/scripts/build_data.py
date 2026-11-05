#!/usr/bin/env python3
"""Generic dataset builder for a model-bench batch of any shape.

  build_data.py --out <folder> --slug <slug> --runs runs.txt

runs.txt: one line per measured run, tab or comma separated:
  engine,arm,run_label,run_dir_name
Copies each run dir's results.jsonl / meta.json / summary.csv into data/raw/ under
<slug>-<run_label>, and writes data/csv/averages.csv, data/csv/means.csv and
data/csv/facts.json. Counts and the same-document-per-depth condition are asserted.
"""
import argparse
import csv
import hashlib
import json
import shutil
import statistics as st
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--slug", required=True)
ap.add_argument("--runs", required=True)
ap.add_argument("--raw", required=True)
ap.add_argument("--expect-runs-per-arm", type=int, default=None)
a = ap.parse_args()

out = Path(a.out)
raw = Path(a.raw)
(out / "data/raw").mkdir(parents=True, exist_ok=True)
(out / "data/csv").mkdir(parents=True, exist_ok=True)

spec = []
for line in open(a.runs, encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = [x.strip() for x in line.replace("\t", ",").split(",")]
    assert len(parts) == 4, parts
    spec.append(parts)

means, raw_files = [], []
for engine, arm, label, dirname in spec:
    d = raw / dirname
    assert d.is_dir(), d
    tag = f"{a.slug}-{label}"
    for src, ext in (("results.jsonl", "jsonl"), ("meta.json", "meta.json"), ("summary.csv", "summary.csv")):
        assert (d / src).exists(), f"{d} missing {src}"
        dst = out / "data/raw" / f"{tag}.{ext}"
        shutil.copyfile(d / src, dst)
        raw_files.append(dst)
    rows = [r for r in csv.DictReader(open(d / "summary.csv", newline="", encoding="utf-8-sig")) if not r.get("error")]
    assert rows, f"{tag}: no measured rows"
    for r in rows:
        means.append(dict(engine=engine, arm=arm, run=label, depth=int(r["depth_k"]),
                          prefill=float(r["prefill_tps"]), decode=float(r["decode_tps"]),
                          ptok=int(r["ptok"]), gen=int(r["gen"]), book=r["book"]))

groups = sorted({(m["engine"], m["arm"]) for m in means})
for g in groups:
    runs = {m["run"] for m in means if (m["engine"], m["arm"]) == g}
    if a.expect_runs_per_arm:
        assert len(runs) == a.expect_runs_per_arm, f"{g}: {len(runs)} runs, expected {a.expect_runs_per_arm}"
    depths = sorted({m["depth"] for m in means if (m["engine"], m["arm"]) == g})
    for dep in depths:
        books = {m["book"] for m in means if (m["engine"], m["arm"]) == g and m["depth"] == dep}
        assert len(books) == 1, f"{g} {dep}: book mismatch {books}"

avg_rows = []
for engine, arm in groups:
    depths = sorted({m["depth"] for m in means if (m["engine"], m["arm"]) == (engine, arm)})
    for dep in depths:
        v = [m for m in means if (m["engine"], m["arm"]) == (engine, arm) and m["depth"] == dep]
        avg_rows.append(dict(
            engine=engine, arm=arm, depth_k=dep, runs=len(v),
            prefill_mean=round(st.mean(x["prefill"] for x in v), 1),
            prefill_min=round(min(x["prefill"] for x in v), 1),
            prefill_max=round(max(x["prefill"] for x in v), 1),
            decode_mean=round(st.mean(x["decode"] for x in v), 2),
            decode_min=round(min(x["decode"] for x in v), 2),
            decode_max=round(max(x["decode"] for x in v), 2),
            gen=v[0]["gen"], ptok=v[0]["ptok"]))

with open(out / "data/csv/averages.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(avg_rows[0]))
    w.writeheader()
    w.writerows(avg_rows)

with open(out / "data/csv/means.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["engine", "arm", "run", "depth", "prefill", "decode", "ptok", "gen", "book"])
    w.writeheader()
    w.writerows(means)

facts = dict(recorded_runs=len(spec), measured_rows=len(means), failed=0,
             groups=[{"engine": e, "arm": ar} for e, ar in groups],
             depths=sorted({m["depth"] for m in means}),
             runs=[{"engine": e, "arm": ar, "label": lb, "dir": dn,
                    "results_rows": sum(1 for _ in open(raw / dn / "results.jsonl"))} for e, ar, lb, dn in spec])
json.dump(facts, open(out / "data/csv/facts.json", "w"), indent=1)

with open(out / "data/raw/SHA256SUMS", "w") as f:
    for p in raw_files:
        f.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n")

print(f"{a.slug}: {len(spec)} runs, {len(means)} measured rows, {len(groups)} groups -> {out}")
for r in avg_rows:
    print("  {engine:6} {arm:10} {depth_k:6d}  prefill {prefill_mean:7.1f} [{prefill_min}-{prefill_max}]  "
          "decode {decode_mean:6.2f} [{decode_min}-{decode_max}]".format(**r))
