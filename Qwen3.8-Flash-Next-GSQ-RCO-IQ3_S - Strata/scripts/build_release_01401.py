#!/usr/bin/env python3
"""Build data/csv/release-0-1-39-vs-0-1-40-1.csv (+ deltas) for the 2026-10-07 pair.

Both sides are model-bench standard batteries run on 2026-10-07, box .5:
  0.1.39    re-run with the box's then-serving start config (STRATA_PROMPT_ATTN_OLD=1,
            the old prompt-attention kernel it had been forcing) — day-matched to the run below.
  0.1.40.1  the update-run, its default V100 prompt kernel (the workaround retired).

Mechanical moves; the only derived column is the delta (formula below). Extraction is the
same as scripts/build_data.py `release()`.

Sources -> outputs
  raw/model-bench-0-1-39-base-rerun-results.jsonl  \
                                                    > csv/release-0-1-39-vs-0-1-40-1.csv
  raw/model-bench-0-1-40-1-base-results.jsonl      /  csv/release-deltas-01401.csv

Derived columns (the only values not read straight off a run):
  release-deltas-01401.csv: delta_pct = 100 * (v0_1_40_1 / v0_1_39 - 1); the `mean`
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
    for eng, src in (("0.1.39", "model-bench-0-1-39-base-rerun-results.jsonl"),
                     ("0.1.40.1", "model-bench-0-1-40-1-base-results.jsonl")):
        for r in read_jsonl(src):
            if r.get("kind") != "arm" or r.get("error"):
                continue
            g = r["gpus"]
            rows.append([eng, r["depth_k"], r["ptok"], r["gen"], r["prefill_tps"], r["decode_tps"],
                         r["wall_s"], g[0]["used_mib"], g[1]["used_mib"], g[0]["temp_c"], g[1]["temp_c"], r["ts"]])
    cols = ["engine", "depth_k", "ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
            "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c", "ts"]
    write_csv("release-0-1-39-vs-0-1-40-1.csv", cols, rows)

    by = {}
    for r in rows:
        by.setdefault(r[0], {})[r[1]] = r
    assert set(by) == {"0.1.39", "0.1.40.1"}, "need both engines"
    assert len(by["0.1.39"]) == 6 and len(by["0.1.40.1"]) == 6, "need all six depths per engine"
    deltas = []
    raw_dd, raw_pd = [], []
    for d in sorted(by["0.1.39"]):
        b = by["0.1.39"][d]
        a = by["0.1.40.1"][d]
        dd = 100.0 * (a[5] / b[5] - 1)
        pd = 100.0 * (a[4] / b[4] - 1)
        raw_dd.append(dd)
        raw_pd.append(pd)
        deltas.append([d, b[5], a[5], round(dd, 1), b[4], a[4], round(pd, 1)])
    dd_mean = round(sum(raw_dd) / len(raw_dd), 1)
    pd_mean = round(sum(raw_pd) / len(raw_pd), 1)
    deltas.append(["mean", "", "", dd_mean, "", "", pd_mean])
    write_csv("release-deltas-01401.csv",
              ["depth_k", "decode_0_1_39", "decode_0_1_40_1", "decode_delta_pct_derived",
               "prefill_0_1_39", "prefill_0_1_40_1", "prefill_delta_pct_derived"], deltas)
    print(f"  release means: decode {dd_mean:+.1f}%  prefill {pd_mean:+.1f}%")


if __name__ == "__main__":
    main()
