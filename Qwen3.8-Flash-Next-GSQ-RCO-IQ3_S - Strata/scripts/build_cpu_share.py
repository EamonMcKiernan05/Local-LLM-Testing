#!/usr/bin/env python3
"""Build the CPU-share test tables from the raw records.

`STRATA_PREFILL_CPU_SHARE=auto` on box .5, 2026-10-07: short-prompt A/B (512-4,000-token
prompts, 3 reps, two server sessions) + the standard battery as a control on the auto arm.

Sources -> outputs
  raw/cpu-share-short-off.jsonl                    \
  raw/cpu-share-short-auto.jsonl                    > csv/cpu-share-short-prompts.csv
  raw/model-bench-0-1-40-2-base-results.jsonl       \
  raw/model-bench-0-1-40-2-cpu-share-results.jsonl   > csv/cpu-share-battery-control.csv

Mechanical moves; the only derived columns are the battery deltas
(delta_pct = 100 * (cpu_share / default - 1)).
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
    for src in ("cpu-share-short-off.jsonl", "cpu-share-short-auto.jsonl"):
        for r in read_jsonl(src):
            rows.append([r["arm"], r["size"], r["rep"], r["ptok"], r["prompt_ms"],
                         r["prompt_tps"], r["wall_s"], r["decode_tps"], r["ts"]])
    write_csv("cpu-share-short-prompts.csv",
              ["arm", "size", "rep", "ptok", "prompt_ms", "prompt_tps", "wall_s", "decode_tps", "ts"], rows)

    def bat(name):
        out = {}
        for r in read_jsonl(name):
            if r.get("kind") == "arm" and not r.get("error"):
                out[r["depth_k"]] = (r["prefill_tps"], r["decode_tps"])
        return out

    dflt = bat("model-bench-0-1-40-2-base-results.jsonl")
    share = bat("model-bench-0-1-40-2-cpu-share-results.jsonl")
    paired = []
    for d in sorted(dflt):
        pf0, dc0 = dflt[d]
        pf1, dc1 = share[d]
        paired.append([d, pf0, pf1, round(100 * (pf1 / pf0 - 1), 1),
                       dc0, dc1, round(100 * (dc1 / dc0 - 1), 1)])
    write_csv("cpu-share-battery-control.csv",
              ["depth_k", "prefill_default", "prefill_cpu_share", "prefill_delta_pct_derived",
               "decode_default", "decode_cpu_share", "decode_delta_pct_derived"], paired)

    assert len(rows) == 24, "short test must be 24 rows"
    assert len(paired) == 6, "battery pair must be 6 depths"


if __name__ == "__main__":
    main()
