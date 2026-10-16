#!/usr/bin/env python3
"""Build the AJ-IQ2_XXS CSVs from the raw model-bench run records (2026-10-16).

Seven measured batteries on box .5, one engine load per battery, every arm a single
measured request through the model-bench harness (the per-battery warm-up request is
discarded by the harness and stays visible as a `warmup` row in the records):

  256K context (262,144): postcopy burn (discarded by design) + three measured batteries
  131K context (131,072): three measured batteries at the shared depths

The 256K means are the analysis basis for the 256K card; the 131K means (three shared
depths) vs them are the context comparison. The burn battery is excluded from the means
by design (first-session-after-copy page-cache assist, per house method).

Every value is read mechanically from ../data/raw/*.jsonl. The only derived columns are
the ctx deltas (formula in deltas()); the mean rows are averages of the per-run measured
values. `ptok` in the mean files is the smallest per-run prompt token count at that depth
(the per-request unique tag tokenizes with variable width, so runs drift by +-1-2).
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "csv")

COLS = ["depth_k", "ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
        "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c", "ts"]

DEPTHS_256 = (20000, 60000, 100000, 150000, 200000, 250000)
DEPTHS_131 = (20000, 60000, 100000)

RUNS_256 = ["model-bench-aj-256k-sn730-r1", "model-bench-aj-256k-sn730-r2",
            "model-bench-aj-256k-sn730-r3"]
BURN = "model-bench-aj-256k-sn730-postcopy-burn"
RUNS_131 = ["model-bench-aj-131k-sn730-r1", "model-bench-aj-131k-sn730-r2",
            "model-bench-aj-131k-sn730-r3"]


def read_run(stem, want_depths):
    """One completed battery: returns (run_id, rows) with rows as flat COLS-order lists."""
    with open(os.path.join(RAW, stem + "-meta.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    assert meta.get("finished_utc") and not meta.get("aborted"), f"{stem}: run not finished"
    assert meta.get("error_count") == 0, f"{stem}: {meta.get('error_count')} errored arms"
    assert tuple(meta["battery"]["depths_k"]) == want_depths, f"{stem}: unexpected depths"
    rows, books = [], {}
    with open(os.path.join(RAW, stem + "-results.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("kind") != "arm" or r.get("error"):
                continue
            g = r["gpus"]
            assert r["gen"] == 400, f"{stem}: gen {r['gen']}"
            assert r["sliced_tokens"] == r["depth_k"], f"{stem}: slice != depth at {r['depth_k']}"
            assert r["draft_n"] == 0, f"{stem}: drafting appeared at {r['depth_k']}"
            books.setdefault(r["depth_k"], r["book"])
            assert books[r["depth_k"]] == r["book"], f"{stem}: book drift at {r['depth_k']}"
            rows.append([r["depth_k"], r["ptok"], r["gen"], r["prefill_tps"], r["decode_tps"],
                         r["wall_s"], g[0]["used_mib"], g[1]["used_mib"], g[0]["temp_c"],
                         g[1]["temp_c"], r["ts"]])
    n_arm = sum(1 for line in open(os.path.join(RAW, stem + "-results.jsonl"), encoding="utf-8")
                if line.strip() and json.loads(line).get("kind") == "arm")
    assert len(rows) == n_arm, f"{stem}: dropped arms ({n_arm} recorded vs {len(rows)} kept)"
    assert len(rows) == len(want_depths), f"{stem}: expected {len(want_depths)} arms, found {len(rows)}"
    return meta["run_id"], rows, books


def mean_rows(runs, depths):
    """Per-depth mean over the runs; returns {depth: (write_row, ptoks, sds, raw_means)}.

    write_row rounds to the working precision the cards were drawn from: prefill to 2 dp,
    decode to 3 dp (the cards display prefill whole and decode to 1 dp); raw_means keeps
    full precision for the deltas.
    """
    out = {}
    for d in depths:
        at = [r for (_, rows, _) in runs for r in rows if r[0] == d]
        assert len(at) == len(runs), f"depth {d}: {len(at)} arms for {len(runs)} runs"
        row = list(at[0])
        raw = {}
        for i, c in enumerate(COLS):
            if c == "ts":
                continue
            vals = [r[i] for r in at]
            m = sum(vals) / len(vals)
            raw[c] = m
            if c in ("ptok", "gen", "depth_k"):
                row[i] = int(round(m))
            elif c == "prefill_tps":
                row[i] = round(m, 2)
            else:
                row[i] = round(m, 3)
        ptoks = [r[1] for r in at]
        sds = {c: stdev([r[COLS.index(c)] for r in at]) for c in ("prefill_tps", "decode_tps")}
        row[COLS.index("ptok")] = min(ptoks)  # the value the cards were drawn with
        row[COLS.index("ts")] = "2026-10-16 (mean of %d runs)" % len(at)
        out[d] = (row, ptoks, sds, raw)
    return out


def stdev(vals):
    m = sum(vals) / len(vals)
    return (sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5


def write_csv(name, cols, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")


def deltas(name, before, after, depths):
    """delta_pct_derived = 100 * (after / before - 1) per depth on the unrounded means;
    the `mean` row averages the three unrounded deltas, then rounds (house convention)."""
    rows, raw_d, raw_p = [], [], []
    for d in depths:
        bd, ad = before[d][3]["decode_tps"], after[d][3]["decode_tps"]
        bp, ap = before[d][3]["prefill_tps"], after[d][3]["prefill_tps"]
        dd = 100.0 * (ad / bd - 1)
        pd = 100.0 * (ap / bp - 1)
        raw_d.append(dd)
        raw_p.append(pd)
        rows.append([d, bd, ad, round(dd, 1), bp, ap, round(pd, 1)])
    rows.append(["mean", "", "", round(sum(raw_d) / len(raw_d), 1), "", "",
                 round(sum(raw_p) / len(raw_p), 1)])
    write_csv(name, ["depth_k", "decode_256k", "decode_131k", "decode_delta_pct_derived",
                     "prefill_256k", "prefill_131k", "prefill_delta_pct_derived"], rows)
    print("    decode deltas %s  mean %.1f" % ([round(x, 1) for x in raw_d], sum(raw_d) / len(raw_d)))
    print("    prefill deltas %s  mean %.1f" % ([round(x, 1) for x in raw_p], sum(raw_p) / len(raw_p)))


def main():
    r256 = [read_run(s, DEPTHS_256) for s in RUNS_256]
    burn = read_run(BURN, DEPTHS_256)
    r131 = [read_run(s, DEPTHS_131) for s in RUNS_131]

    # same-prompt proof: one book per depth, ptok spread small, across all batteries
    for depths, batteries in ((DEPTHS_256, r256 + [burn]), (DEPTHS_131, r131)):
        for d in depths:
            books = {b[d] for (_, _, b) in batteries}
            assert len(books) == 1, f"depth {d}: books {books}"
            ptoks = [r[1] for (_, rows, _) in batteries for r in rows if r[0] == d]
            spread = max(ptoks) - min(ptoks)
            assert spread <= 3, f"depth {d}: ptok spread {spread} ({min(ptoks)}..{max(ptoks)})"
            print(f"  depth {d}: book {books.pop()}  ptok {min(ptoks)}..{max(ptoks)} (spread {spread})")
    # cross-cycle: same book + same slice at the shared depths
    for d in DEPTHS_131:
        assert r256[0][2][d] == r131[0][2][d], f"book differs across ctx at {d}"
        ptoks = [r[1] for (_, rows, _) in r256 + r131 for r in rows if r[0] == d]
        assert max(ptoks) - min(ptoks) <= 3, f"cross-ctx ptok spread at {d}"

    # per-run rows
    per = []
    for side, rs in (("256K ctx", r256), ("131K ctx", r131)):
        for rid, rows, _ in rs:
            for row in rows:
                per.append([side, rid] + row)
    for row in burn[1]:
        per.append(["256K ctx (burn, excluded)", burn[0]] + row)
    write_csv("depth-aj-runs.csv", ["side", "run_id"] + COLS, per)

    m256 = mean_rows(r256, DEPTHS_256)
    m131 = mean_rows(r131, DEPTHS_131)
    mean_id = "2026-10-16, mean of three runs"

    write_csv("depth-aj-256k.csv", ["run_id"] + COLS, [[mean_id] + m256[d][0] for d in DEPTHS_256])
    write_csv("depth-aj-131k.csv", ["run_id"] + COLS, [[mean_id] + m131[d][0] for d in DEPTHS_131])

    write_csv("ctx-aj-256k-vs-131k.csv", ["ctx", "run_id"] + COLS,
              [["262144 ctx", mean_id] + m256[d][0] for d in DEPTHS_131] +
              [["131072 ctx", mean_id] + m131[d][0] for d in DEPTHS_131])
    deltas("ctx-deltas-aj-256k-vs-131k.csv", m256, m131, list(DEPTHS_131))

    print()
    print("MEANS (3 runs per side):")
    for tag, m, depths in (("256K", m256, DEPTHS_256), ("131K", m131, DEPTHS_131)):
        for d in depths:
            row, ptoks, sds, _ = m[d]
            print("  %s %5dK: prefill %8.3f (sd %.3f)  decode %7.3f (sd %.3f)  ptok %d"
                  % (tag, d // 1000, row[COLS.index("prefill_tps")], sds["prefill_tps"],
                     row[COLS.index("decode_tps")], sds["decode_tps"], min(ptoks)))
    print()
    print("BURN (excluded, per depth prefill/decode):")
    for d in DEPTHS_256:
        r = [r for r in burn[1] if r[0] == d][0]
        print("  %5dK: %7.1f / %5.1f" % (d // 1000, r[COLS.index("prefill_tps")],
                                         r[COLS.index("decode_tps")]))


if __name__ == "__main__":
    main()
