#!/usr/bin/env python3
"""Build data/csv/release-0-1-43-vs-0-1-44.csv (+ deltas) for the 2026-10-13 pair.

Both sides are model-bench standard batteries run on 2026-10-13, box .5, same config as served:
  0.1.43  the pre-update side, benched fresh the same day while still live as served (the pair's "before").
  0.1.44  after updating the engine (v0.1.43.1's layer-split/batch fix folded in; Mac/SYCL/NVFP4
          work lands elsewhere — nothing in this pair's path).

The comparison CSV refuses to write unless the two runs sliced the same documents to the same
token counts at every depth (`book`/`ptok` identical per depth) — same-prompt comparability is
the assertion, not a promise.

Sources -> outputs
  raw/model-bench-0-1-43-base-rerun-results.jsonl  \
                                                > csv/release-0-1-43-vs-0-1-44.csv
  raw/model-bench-0-1-44-base-results.jsonl        /  csv/release-deltas-0144.csv

Derived columns (the only values not read straight off a run):
  release-deltas-0144.csv: delta_pct = 100 * (v0_1_44 / v0_1_43 - 1); the `mean`
  row is the arithmetic mean of the six per-depth deltas.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "csv")


def read_jsonl(name):
    path = os.path.join(RAW, name)
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write_csv(name, cols, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")
    return rows


def main():
    rows = []
    prompts = {}
    for eng, src in (("0.1.43", "model-bench-0-1-43-base-rerun-results.jsonl"),
                     ("0.1.44", "model-bench-0-1-44-base-results.jsonl")):
        prompts[eng] = {}
        n_rows = 0
        for r in read_jsonl(src):
            n_rows += 1
            if r.get("kind") != "arm" or r.get("error"):
                continue
            prompts[eng][r["depth_k"]] = (r.get("book"), r["ptok"])
            g = r["gpus"]
            rows.append([eng, r["depth_k"], r["ptok"], r["gen"], r["prefill_tps"], r["decode_tps"],
                         r["wall_s"], g[0]["used_mib"], g[1]["used_mib"], g[0]["temp_c"], g[1]["temp_c"], r["ts"]])
        print(f"  {eng}: {n_rows} rows read")

    cols = ["engine", "depth_k", "ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
            "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c", "ts"]

    # same-prompt comparability gate: refuse to write on any mismatch
    for eng, d in prompts.items():
        assert len(d) == 6, f"{eng}: need six depths, got {len(d)}"
    for depth in prompts["0.1.43"]:
        assert prompts["0.1.43"][depth] == prompts["0.1.44"][depth], (
            f"depth {depth}: prompt mismatch {prompts['0.1.43'][depth]} vs {prompts['0.1.44'][depth]}")
    print("  same-prompt check: book/ptok identical at all six depths")

    write_csv("release-0-1-43-vs-0-1-44.csv", cols, rows)

    by = {}
    for r in rows:
        by.setdefault(r[0], {})[r[1]] = r
    assert set(by) == {"0.1.43", "0.1.44"}, "need both engines"
    assert len(by["0.1.43"]) == 6 and len(by["0.1.44"]) == 6, "need all six depths per engine"
    deltas = []
    raw_dd, raw_pd = [], []
    for d in sorted(by["0.1.43"]):
        b = by["0.1.43"][d]
        a = by["0.1.44"][d]
        dd = 100.0 * (a[5] / b[5] - 1)
        pd = 100.0 * (a[4] / b[4] - 1)
        raw_dd.append(dd)
        raw_pd.append(pd)
        deltas.append([d, b[5], a[5], round(dd, 1), b[4], a[4], round(pd, 1)])
    dd_mean = round(sum(raw_dd) / len(raw_dd), 1)
    pd_mean = round(sum(raw_pd) / len(raw_pd), 1)
    deltas.append(["mean", "", "", dd_mean, "", "", pd_mean])
    write_csv("release-deltas-0144.csv",
              ["depth_k", "decode_0_1_43", "decode_0_1_44", "decode_delta_pct_derived",
               "prefill_0_1_43", "prefill_0_1_44", "prefill_delta_pct_derived"], deltas)
    print(f"  release means: decode {dd_mean:+.1f}%  prefill {pd_mean:+.1f}%")


if __name__ == "__main__":
    main()
