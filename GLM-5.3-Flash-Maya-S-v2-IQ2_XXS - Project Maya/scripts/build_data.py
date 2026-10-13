#!/usr/bin/env python3
"""Build the Maya CSVs from the raw model-bench run records.

Every value is read mechanically from raw/*.jsonl (flattened copies of the run dirs on box .5,
sha256-checked both sides). The only derived columns are the deltas at the bottom of this file
(formula stated at the `deltas()` call).

Runs (raw/):
  64k-tuned         2026-10-07T2042Z-maya-s-v2-64k-tuned        previous build, 64K config (archived baseline)
  64k-tuned-rerun   2026-10-08T....Z-maya-s-v2-64k-tuned-rerun  previous build re-run the same day as the update
  64k-v109          2026-10-08T1000Z-maya-s-v2-64k-v109         v1.0.9 after the update
  64k-v109-rerun    2026-10-11T....Z-maya-s-v2-64k-v109-rerun   v1.0.9 re-run on the v1.0.33 update day
  64k-v1033         2026-10-11T....Z-maya-s-v2-64k-v1033        v1.0.33 after the update
  64k-v109-rerun2   2026-10-11T....Z-maya-s-v2-64k-v109-rerun2  v1.0.9 re-run again for the v1.0.34 pair
  64k-v1034         2026-10-11T....Z-maya-s-v2-64k-v1034        v1.0.34 after the update
  128k / 128k-warm2 2026-10-07T1917Z / T2005Z                   bring-up, stock 128K config (record only)

Outputs (csv/):
  depth-64k-previous.csv / depth-64k-v109.csv / depth-64k-before-rerun.csv
  release-64k-before-rerun-vs-v109.csv     + release-deltas-64k-109.csv
  release-deltas-64k-rerun-vs-archived.csv (agreement check: the same-day re-run vs the archive)
  depth-64k-v109-rerun.csv / depth-64k-v1033.csv
  release-64k-v109-vs-v1033.csv            + release-deltas-64k-1033.csv
  release-deltas-64k-v109-rerun-vs-archived.csv (agreement check for the 2026-10-11 pair)
  depth-64k-v109-rerun2.csv / depth-64k-v1034.csv
  release-64k-v109-vs-v1034.csv            + release-deltas-64k-1034.csv
  release-deltas-64k-v109-rerun2-vs-archived.csv (agreement check for the v1.0.34 pair)
  bringup-128k-stock.csv
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "csv")

COLS = ["depth_k", "ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
        "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c", "ts"]


def read_run(stem):
    """One completed model-bench run: returns (run_id, rows). Asserts it finished with 3 error-free arms."""
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
    assert len(rows) == 3, f"{stem}: expected 3 arms, found {len(rows)}"
    return meta["run_id"], rows


def write_csv(name, cols, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")
    return rows


def deltas(name, before, after):
    """delta_pct_derived = 100 * (after / before - 1) per depth, on the unrounded values;
    the `mean` row is the mean of the three unrounded deltas, then rounded. The only derived
    columns in the dataset."""
    b = {r[0]: dict(zip(COLS, r)) for r in before}
    a = {r[0]: dict(zip(COLS, r)) for r in after}
    assert set(a) == set(b) == {20000, 40000, 60000}, "need 20K/40K/60K on both sides"
    rows, raw_d, raw_p = [], [], []
    for d in sorted(b):
        dd = 100.0 * (a[d]["decode_tps"] / b[d]["decode_tps"] - 1)
        pd = 100.0 * (a[d]["prefill_tps"] / b[d]["prefill_tps"] - 1)
        raw_d.append(dd)
        raw_p.append(pd)
        rows.append([d, b[d]["decode_tps"], a[d]["decode_tps"], round(dd, 1),
                     b[d]["prefill_tps"], a[d]["prefill_tps"], round(pd, 1)])
    rows.append(["mean", "", "", round(sum(raw_d) / len(raw_d), 1), "", "",
                 round(sum(raw_p) / len(raw_p), 1)])
    write_csv(name, ["depth_k", "decode_before", "decode_after", "decode_delta_pct_derived",
                     "prefill_before", "prefill_after", "prefill_delta_pct_derived"], rows)


def main():
    prev_id, prev = read_run("model-bench-64k-tuned")
    rerun_id, rerun = read_run("model-bench-64k-tuned-rerun")
    v109_id, v109 = read_run("model-bench-64k-v109")
    v109r_id, v109r = read_run("model-bench-64k-v109-rerun")
    v1033_id, v1033 = read_run("model-bench-64k-v1033")
    v109r2_id, v109r2 = read_run("model-bench-64k-v109-rerun2")
    v1034_id, v1034 = read_run("model-bench-64k-v1034")
    b128_id, b128 = read_run("model-bench-128k")
    b128w_id, b128w = read_run("model-bench-128k-warm2")

    write_csv("depth-64k-previous.csv", ["run_id"] + COLS, [[prev_id] + r for r in prev])
    write_csv("depth-64k-v109.csv", ["run_id"] + COLS, [[v109_id] + r for r in v109])
    write_csv("depth-64k-before-rerun.csv", ["run_id"] + COLS, [[rerun_id] + r for r in rerun])

    write_csv("release-64k-before-rerun-vs-v109.csv", ["engine", "run_id"] + COLS,
              [["previous", rerun_id] + r for r in rerun] +
              [["v1.0.9", v109_id] + r for r in v109])
    deltas("release-deltas-64k-109.csv", rerun, v109)
    deltas("release-deltas-64k-rerun-vs-archived.csv", prev, rerun)

    write_csv("depth-64k-v109-rerun.csv", ["run_id"] + COLS, [[v109r_id] + r for r in v109r])
    write_csv("depth-64k-v1033.csv", ["run_id"] + COLS, [[v1033_id] + r for r in v1033])
    write_csv("release-64k-v109-vs-v1033.csv", ["engine", "run_id"] + COLS,
              [["v1.0.9", v109r_id] + r for r in v109r] +
              [["v1.0.33", v1033_id] + r for r in v1033])
    deltas("release-deltas-64k-1033.csv", v109r, v1033)
    deltas("release-deltas-64k-v109-rerun-vs-archived.csv", v109, v109r)

    write_csv("depth-64k-v109-rerun2.csv", ["run_id"] + COLS, [[v109r2_id] + r for r in v109r2])
    write_csv("depth-64k-v1034.csv", ["run_id"] + COLS, [[v1034_id] + r for r in v1034])
    write_csv("release-64k-v109-vs-v1034.csv", ["engine", "run_id"] + COLS,
              [["v1.0.9", v109r2_id] + r for r in v109r2] +
              [["v1.0.34", v1034_id] + r for r in v1034])
    deltas("release-deltas-64k-1034.csv", v109r2, v1034)
    deltas("release-deltas-64k-v109-rerun2-vs-archived.csv", v109, v109r2)

    write_csv("bringup-128k-stock.csv", ["run", "run_id"] + COLS,
              [["128k", b128_id] + r for r in b128] +
              [["128k-warm2", b128w_id] + r for r in b128w])


if __name__ == "__main__":
    main()
