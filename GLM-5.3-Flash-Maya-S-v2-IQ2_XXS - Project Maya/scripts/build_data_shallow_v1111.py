#!/usr/bin/env python3
"""Build the Maya shallow-range CSVs (2026-10-15 second visit): v1.1.1 vs v1.1.11 at
500 / 1K / 5K / 10K prompt depths, three batteries per side, alternated A B A B A B.

Same method as build_data_v1111.py (same-day, same per-side configs, one engine load per
battery, warm-up discarded by the harness). Per-run record + 3-run per-depth means + deltas.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "csv")

COLS = ["depth_k", "ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
        "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c", "ts"]

SIDES = {
    "v1.1.1": ["model-bench-64k-v111-shallow-r1", "model-bench-64k-v111-shallow-r2", "model-bench-64k-v111-shallow-r3"],
    "v1.1.11": ["model-bench-64k-v1111-shallow-r1", "model-bench-64k-v1111-shallow-r2", "model-bench-64k-v1111-shallow-r3"],
}
DEPTHS = (500, 1000, 5000, 10000)
NUM_COLS = ["ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
            "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c"]


def read_run(stem):
    with open(os.path.join(RAW, stem + "-meta.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    assert meta.get("finished_utc") and not meta.get("aborted"), f"{stem}: run not finished"
    assert meta.get("error_count") == 0, f"{stem}: {meta.get('error_count')} errored arms"
    rows = []
    with open(os.path.join(RAW, stem + "-results.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("kind") != "arm" or r.get("error"):
                continue
            g = r["gpus"]
            rows.append([r["depth_k"], r["ptok"], r["gen"], r["prefill_tps"], r["decode_tps"],
                         r["wall_s"], g[0]["used_mib"], g[1]["used_mib"], g[0]["temp_c"],
                         g[1]["temp_c"], r["ts"]])
    assert len(rows) == 4, f"{stem}: expected 4 arms, found {len(rows)}"
    return meta["run_id"], rows


def write_csv(name, cols, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")


def mean_rows(runs):
    out = {}
    for d in DEPTHS:
        at = [r for (_, rows) in runs for r in rows if r[0] == d]
        assert len(at) == len(runs), f"depth {d}: {len(at)} arms for {len(runs)} runs"
        row = list(at[0])
        for i, c in enumerate(COLS):
            if c == "ts":
                continue
            vals = [r[i] for r in at]
            m = sum(vals) / len(vals)
            row[i] = int(round(m)) if c in ("ptok", "gen", "depth_k") else round(m, 3)
        row[COLS.index("ts")] = "2026-10-15 (mean of 3 runs)"
        out[d] = row
    return out


def deltas(name, before, after):
    b = {r[0]: r for r in before}
    a = {r[0]: r for r in after}
    assert set(a) == set(b) == set(DEPTHS)
    rows, raw_d, raw_p = [], [], []
    for d in sorted(b):
        bd, ad = b[d][COLS.index("decode_tps")], a[d][COLS.index("decode_tps")]
        bp, ap = b[d][COLS.index("prefill_tps")], a[d][COLS.index("prefill_tps")]
        dd = 100.0 * (ad / bd - 1)
        pd = 100.0 * (ap / bp - 1)
        raw_d.append(dd); raw_p.append(pd)
        rows.append([d, bd, ad, round(dd, 1), bp, ap, round(pd, 1)])
    rows.append(["mean", "", "", round(sum(raw_d) / len(raw_d), 1), "", "",
                 round(sum(raw_p) / len(raw_p), 1)])
    write_csv(name, ["depth_k", "decode_before", "decode_after", "decode_delta_pct_derived",
                     "prefill_before", "prefill_after", "prefill_delta_pct_derived"], rows)
    print("    decode deltas %s  mean %.1f" % ([round(x, 1) for x in raw_d], sum(raw_d) / len(raw_d)))
    print("    prefill deltas %s  mean %.1f" % ([round(x, 1) for x in raw_p], sum(raw_p) / len(raw_p)))


def main():
    runs = {}
    for side, stems in SIDES.items():
        runs[side] = [read_run(s) for s in stems]
    all_b = runs["v1.1.1"] + runs["v1.1.11"]

    for d in DEPTHS:
        ptoks = [r[1] for (_, rows) in all_b for r in rows if r[0] == d]
        spread = max(ptoks) - min(ptoks)
        assert spread <= 3, f"depth {d}: ptok spread {spread}"
        print(f"  depth {d}: ptok {min(ptoks)}..{max(ptoks)} (spread {spread})")

    per = []
    for side, rs in runs.items():
        for rid, rows in rs:
            for r in rows:
                per.append([side, rid] + r)
    write_csv("depth-64k-shallow-runs.csv", ["side", "run_id"] + COLS, per)

    mb = {side: mean_rows(rs) for side, rs in runs.items()}
    mean_id = "2026-10-15 shallow mean of three runs"
    write_csv("release-64k-shallow-v111-vs-v1111.csv", ["engine", "run_id"] + COLS,
              [["v1.1.1", mean_id] + mb["v1.1.1"][d] for d in DEPTHS] +
              [["v1.1.11", mean_id] + mb["v1.1.11"][d] for d in DEPTHS])
    deltas("release-deltas-64k-shallow.csv",
           [mb["v1.1.1"][d] for d in DEPTHS],
           [mb["v1.1.11"][d] for d in DEPTHS])

    print()
    print("SHALLOW MEANS (3 runs per side):")
    for side in ("v1.1.1", "v1.1.11"):
        for d in DEPTHS:
            r = mb[side][d]
            print("  %s %6d: prefill %7.2f  decode %6.2f" % (side, d, r[COLS.index("prefill_tps")], r[COLS.index("decode_tps")]))


if __name__ == "__main__":
    main()
