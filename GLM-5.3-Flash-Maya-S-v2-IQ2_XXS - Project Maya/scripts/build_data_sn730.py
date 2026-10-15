#!/usr/bin/env python3
"""Build the Maya storage-upgrade CSVs from the raw model-bench run records (2026-10-15).

Six measured batteries - three per side (before = the morning runs with the model set on the old
BC501 boot NVMe, after = the night runs with the set moved to the new SN730 data NVMe) - plus one
discarded post-copy burn battery (SN730). All seven ran the same battery on box .5 the same day,
one engine load per battery; every arm is a
single measured request through the model-bench harness (warm-up row discarded by the harness).

The pair CSVs hold the 3-run per-depth means - the analysis basis (mean of three runs per side;
the burn battery is excluded by design - its first-session-after-copy prefill reads high
from the known page-cache assist (experiments/05).

Every value is read mechanically from raw/*.jsonl. The only derived columns are the deltas
(formula at deltas()); the mean CSVs are averages of the per-run measured values.
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
    "before (BC501 NVMe)": ["model-bench-64k-v1111-r1", "model-bench-64k-v1111-r2", "model-bench-64k-v1111-r3"],
    "after (SN730 NVMe)": ["model-bench-64k-sn730-r1", "model-bench-64k-sn730-r2", "model-bench-64k-sn730-r3"],
}
BURN_STEM = "model-bench-64k-sn730-postcopy-burn"
BURN_SIDE = "after (SN730 NVMe) (burn, excluded)"
DEPTHS = (20000, 40000, 60000)
NUM_COLS = ["ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
            "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c"]


def read_run(stem):
    """One completed battery: returns (run_id, rows) with rows as flat COLS-order lists."""
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


def mean_rows(runs):
    """Per-depth mean over the runs; returns {depth: row-list} in COLS order."""
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
    """delta_pct_derived = 100 * (after / before - 1) per depth on the unrounded means;
    the `mean` row averages the three unrounded deltas, then rounds."""
    b = {r[0]: r for r in before}
    a = {r[0]: r for r in after}
    assert set(a) == set(b) == set(DEPTHS), "need 20K/40K/60K on both sides"
    rows, raw_d, raw_p = [], [], []
    for d in sorted(b):
        bd, ad = b[d][COLS.index("decode_tps")], a[d][COLS.index("decode_tps")]
        bp, ap = b[d][COLS.index("prefill_tps")], a[d][COLS.index("prefill_tps")]
        dd = 100.0 * (ad / bd - 1)
        pd = 100.0 * (ap / bp - 1)
        raw_d.append(dd)
        raw_p.append(pd)
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
    burn = read_run(BURN_STEM)
    all_batteries = runs["before (BC501 NVMe)"] + runs["after (SN730 NVMe)"] + [burn]

    # same-prompt proof: one book per depth across all seven batteries, ptok within a few tokens
    for d in DEPTHS:
        ptoks = [r[1] for (_, rows) in all_batteries for r in rows if r[0] == d]
        spread = max(ptoks) - min(ptoks)
        assert spread <= 3, f"depth {d}: ptok spread {spread} ({min(ptoks)}..{max(ptoks)})"
        print(f"  depth {d}: ptok {min(ptoks)}..{max(ptoks)} (spread {spread})")

    per = []
    for side, rs in runs.items():
        for rid, rows in rs:
            for r in rows:
                per.append([side, rid] + r)
    for r in burn[1]:
        per.append([BURN_SIDE, burn[0]] + r)
    write_csv("depth-64k-sn730-runs.csv", ["side", "run_id"] + COLS, per)

    mb = {side: mean_rows(rs) for side, rs in runs.items()}
    mean_id = "2026-10-15 night, mean of three runs"

    write_csv("depth-64k-sn730.csv", ["run_id"] + COLS,
              [[mean_id] + mb["after (SN730 NVMe)"][d] for d in DEPTHS])
    write_csv("release-64k-bc501-vs-sn730.csv", ["engine", "run_id"] + COLS,
              [["before (BC501 NVMe)", mean_id] + mb["before (BC501 NVMe)"][d] for d in DEPTHS] +
              [["after (SN730 NVMe)", mean_id] + mb["after (SN730 NVMe)"][d] for d in DEPTHS])
    deltas("release-deltas-64k-sn730.csv",
           [mb["before (BC501 NVMe)"][d] for d in DEPTHS],
           [mb["after (SN730 NVMe)"][d] for d in DEPTHS])

    print()
    print("MEANS (3 runs per side):")
    for side in ("before (BC501 NVMe)", "after (SN730 NVMe)"):
        for d in DEPTHS:
            r = mb[side][d]
            print("  %s %5dK: prefill %7.2f  decode %6.2f" % (side, d // 1000,
                  r[COLS.index("prefill_tps")], r[COLS.index("decode_tps")]))
    print()
    print("BURN (excluded, per depth prefill/decode):")
    for d in DEPTHS:
        r = [r for r in burn[1] if r[0] == d][0]
        print("  %5dK: %7.1f / %5.1f" % (d // 1000, r[COLS.index("prefill_tps")], r[COLS.index("decode_tps")]))


if __name__ == "__main__":
    main()
