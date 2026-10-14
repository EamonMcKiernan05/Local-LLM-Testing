#!/usr/bin/env python3
"""Build data/csv/release-0-1-43-vs-0-1-44-mean3.csv (+ deltas) — the three-pass means.

One row per depth per engine: the arithmetic mean of the three same-night passes
(0.1.43: the T1956Z re-run + T2139Z rep2 + T2146Z rep3; 0.1.44: T2007Z + T2122Z rep2 + T2129Z rep3),
plus per-metric min/max spans for provenance. Refuses to write unless every source run sliced
the same documents to the same token counts at every depth.

Sources -> outputs
  raw/model-bench-0-1-43-base-{rerun,rep2,rep3}-results.jsonl  > csv/release-0-1-43-vs-0-1-44-mean3.csv
  raw/model-bench-0-1-44-base-{base..,rep2,rep3}-results.jsonl > csv/release-deltas-0144-mean3.csv

Derived columns (the only values not read straight off a run):
  release-deltas-0144-mean3.csv: delta_pct = 100 * (mean_0_1_44 / mean_0_1_43 - 1); the `mean`
  row is the arithmetic mean of the six per-depth deltas.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "csv")

SOURCES = {
    "0.1.43": ["model-bench-0-1-43-base-rerun-results.jsonl",
               "model-bench-0-1-43-base-rep2-results.jsonl",
               "model-bench-0-1-43-base-rep3-results.jsonl"],
    "0.1.44": ["model-bench-0-1-44-base-results.jsonl",
               "model-bench-0-1-44-base-rep2-results.jsonl",
               "model-bench-0-1-44-base-rep3-results.jsonl"],
}


def read_jsonl(name):
    with open(os.path.join(RAW, name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write_csv(name, cols, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")


def main():
    per_run = {}          # (engine, name) -> {depth: row}
    prompts = {}          # depth -> set of (book, ptok)
    for eng, names in SOURCES.items():
        for name in names:
            by = {}
            for r in read_jsonl(name):
                if r.get("kind") != "arm" or r.get("error"):
                    continue
                by[r["depth_k"]] = r
                prompts.setdefault(r["depth_k"], set()).add((r.get("book"), r["ptok"]))
            assert len(by) == 6, f"{name}: {len(by)} arms"
            per_run[(eng, name)] = by
            print(f"  {name}: 6 arms")

    for depth, keys in prompts.items():
        assert len(keys) == 1, f"depth {depth}: prompt mismatch {sorted(keys)}"
    print("  same-prompt check: book/ptok identical across all six runs, all six depths")

    rows = []
    for eng, names in SOURCES.items():
        for depth in sorted(per_run[(eng, names[0])]):
            rs = [per_run[(eng, n)][depth] for n in names]
            pf = [r["prefill_tps"] for r in rs]
            dc = [r["decode_tps"] for r in rs]
            g0 = round(sum(r["gpus"][0]["used_mib"] for r in rs) / 3)
            g1 = round(sum(r["gpus"][1]["used_mib"] for r in rs) / 3)
            wl = round(sum(r["wall_s"] for r in rs) / 3, 1)
            rows.append([eng, depth, rs[0]["ptok"], rs[0]["gen"],
                         round(sum(pf) / 3, 1), round(sum(dc) / 3, 1),
                         min(pf), max(pf), min(dc), max(dc),
                         wl, g0, g1, 3])
    cols = ["engine", "depth_k", "ptok", "gen", "prefill_tps", "decode_tps",
            "prefill_min", "prefill_max", "decode_min", "decode_max",
            "wall_s", "gpu0_used_mib", "gpu1_used_mib", "n_runs"]
    write_csv("release-0-1-43-vs-0-1-44-mean3.csv", cols, rows)

    by = {}
    for r in rows:
        by.setdefault(r[0], {})[r[1]] = r
    assert set(by) == {"0.1.43", "0.1.44"}, "need both engines"
    deltas = []
    raw_dd, raw_pd = [], []
    for depth in sorted(by["0.1.43"]):
        b = by["0.1.43"][depth]
        a = by["0.1.44"][depth]
        dd = 100.0 * (a[5] / b[5] - 1)
        pd = 100.0 * (a[4] / b[4] - 1)
        raw_dd.append(dd)
        raw_pd.append(pd)
        deltas.append([depth, b[5], a[5], round(dd, 1), b[4], a[4], round(pd, 1)])
    dd_mean = round(sum(raw_dd) / len(raw_dd), 1)
    pd_mean = round(sum(raw_pd) / len(raw_pd), 1)
    deltas.append(["mean", "", "", dd_mean, "", "", pd_mean])
    write_csv("release-deltas-0144-mean3.csv",
              ["depth_k", "decode_0_1_43", "decode_0_1_44", "decode_delta_pct_derived",
               "prefill_0_1_43", "prefill_0_1_44", "prefill_delta_pct_derived"], deltas)
    print(f"  mean3 means: decode {dd_mean:+.1f}%  prefill {pd_mean:+.1f}%")


if __name__ == "__main__":
    main()
