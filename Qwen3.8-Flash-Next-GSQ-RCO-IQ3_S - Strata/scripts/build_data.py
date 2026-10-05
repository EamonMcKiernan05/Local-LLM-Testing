#!/usr/bin/env python3
"""Build data/csv/ from data/raw/ for the Strata dataset.

Mechanical moves unless a column is named `*_derived` (formulas below).
Run from anywhere: `python3 scripts/build_data.py`.

Sources -> outputs
  raw/strata-sampler-sweep-base.jsonl   -> csv/sampler-sweep-base.csv
  raw/strata-mtp-sweep-all-arms.jsonl   -> csv/mtp-sweep-all-arms.csv
                                           csv/mtp-stage-a-gate.csv
                                           csv/mtp-stage-s-suffix.csv
                                           csv/mtp-stage-c-coupled.csv
                                           csv/mtp-stage-b-samplers.csv
                                           csv/mtp-sweep-summary.csv
  raw/model-bench-0-1-32-base-results.jsonl
  raw/model-bench-0-1-39-base-results.jsonl -> csv/release-0-1-32-vs-0-1-39.csv
                                               csv/release-deltas.csv
  raw/depth-decode3.jsonl               -> csv/depth-series-0-1-32.csv
  raw/strata-hero.jsonl                 -> csv/hero-250k.csv
  raw/strata-compare-single3.log         \
  raw/strata-compare-dual4.log           > csv/load-checks.csv
  raw/strata-compare-dual.log           /
  raw/strata-compare-dual2.log          /
  raw/strata-compare-dual3.log          /
  raw/strata-compare-single2.log        /

Derived columns (the only values not read straight off a run):
  draft_accept_pct = 100 * draft_acc / draft_n
  release-deltas.csv: delta_pct = 100 * (v0_1_39 / v0_1_32 - 1); the `mean`
  row is the arithmetic mean of the six per-depth deltas.
  mtp-sweep-summary.csv: per-arm means over the six depths; stage-B bands are
  min/max across that stage's arms (14 per depth); winner_gate is the arbiter
  written by the sweep driver itself (raw/strata-mtp-sweep-winner.txt).

The bring-up observations CSV is not generated here: its rows are exact quotes
from the 2026-09-30/10-01 set-up session records, transcribed one-to-one into
`data/csv/bring-up-observations.csv` (quotes preserved in the `source` column).
"""
import csv
import json
import os
import re

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


def accept_pct(r):
    if r.get("draft_n"):
        return round(100.0 * r["draft_acc"] / r["draft_n"], 1)
    return ""


# ---------------------------------------------------------------- sweeps ----
def sweep_csv(src, out):
    cols = ["label", "spec_min_p", "top_k", "top_p", "min_p", "wall_s", "ptok", "gen",
            "prefill_tps", "decode_tps", "draft_n", "draft_acc", "draft_accept_pct_derived"]
    rows = [[r.get(c) if not c.startswith("draft_accept") else accept_pct(r) for c in cols]
            for r in read_jsonl(src)]
    write_csv(out, cols, rows)
    return rows


def mtp_sweep():
    rows = read_jsonl("strata-mtp-sweep-all-arms.jsonl")
    cols = ["stage", "label", "depth_k", "spec_min_p", "top_k", "top_p", "min_p", "wall_s",
            "ptok", "gen", "prefill_tps", "decode_tps", "draft_n", "draft_acc",
            "draft_accept_pct_derived"]
    write_csv("mtp-sweep-all-arms.csv", cols,
              [[r.get(c) if not c.startswith("draft_accept") else accept_pct(r) for c in cols] for r in rows])

    # Stage A: gate x depth
    a = [r for r in rows if r["stage"] == "A"]
    write_csv("mtp-stage-a-gate.csv",
              ["spec_min_p", "depth_k", "decode_tps", "prefill_tps", "gen", "draft_n", "draft_acc"],
              [[r["spec_min_p"], r["depth_k"], r["decode_tps"], r["prefill_tps"], r["gen"],
                r["draft_n"], r["draft_acc"]] for r in a])

    # Stage S: suffix-draft value from the label (S-sfx0 / S-sfx8)
    s = [r for r in rows if r["stage"] == "S"]
    write_csv("mtp-stage-s-suffix.csv",
              ["suffix_draft", "depth_k", "decode_tps", "prefill_tps", "gen", "draft_n", "draft_acc"],
              [[re.search(r"S-sfx(\d+)", r["label"]).group(1), r["depth_k"], r["decode_tps"],
                r["prefill_tps"], r["gen"], r["draft_n"], r["draft_acc"]] for r in s])

    # Stage C: coupled-draft 'on' runs
    c = [r for r in rows if r["stage"] == "C"]
    write_csv("mtp-stage-c-coupled.csv",
              ["coupled_draft", "depth_k", "decode_tps", "prefill_tps", "gen", "draft_n", "draft_acc"],
              [["on", r["depth_k"], r["decode_tps"], r["prefill_tps"], r["gen"],
                r["draft_n"], r["draft_acc"]] for r in c])

    # Stage B: grid arms + top_p probe
    b = [r for r in rows if r["stage"] == "B"]
    write_csv("mtp-stage-b-samplers.csv",
              ["variant", "top_k", "min_p", "top_p", "depth_k", "decode_tps", "prefill_tps",
               "gen", "draft_n", "draft_acc"],
              [["top_p_probe" if r["label"].startswith("B-tp") else "top_k_min_p_grid",
                r["top_k"], r["min_p"], r["top_p"], r["depth_k"], r["decode_tps"],
                r["prefill_tps"], r["gen"], r["draft_n"], r["draft_acc"]] for r in b])

    # Summary of the statistics the write-ups quote (all derived, see header)
    depths = sorted({r["depth_k"] for r in rows})
    summary = []

    def mean_decode(rs):
        v = [r["decode_tps"] for r in rs if "decode_tps" in r]
        return round(sum(v) / len(v), 1)

    for g in (0.0, 0.5, 0.6, 0.85):
        summary.append(["gate_mean_decode_derived", f"{g:.2f}", mean_decode([r for r in a if r["spec_min_p"] == g]), "", "tok/s"])
    a05 = [r for r in a if r["spec_min_p"] == 0.5]
    for sv, label in (("0", "0 (off)"), ("3", "3 (default, = gate-0.50 stage A data)"), ("8", "8 (aggressive)")):
        rs = a05 if sv == "3" else [r for r in s if r["label"].startswith(f"S-sfx{sv}")]
        summary.append(["suffix_mean_decode_derived", label, mean_decode(rs), "", "tok/s"])
    summary.append(["coupled_mean_decode_derived", "on", mean_decode(c), "", "tok/s"])
    summary.append(["coupled_mean_decode_derived", "off (= gate-0.50 stage A data)", mean_decode(a05), "", "tok/s"])
    for d in depths:
        v = [r["decode_tps"] for r in b if r["depth_k"] == d and "decode_tps" in r]
        summary.append(["stage_b_decode_band_derived", f"{d // 1000}k", round(min(v), 1), round(max(v), 1), "tok/s"])
    pf = [r["prefill_tps"] for r in b if r["depth_k"] == 250000 and "prefill_tps" in r]
    summary.append(["stage_b_prefill_band_derived", "250k", round(min(pf), 1), round(max(pf), 1), "tok/s"])
    for stage, rs in (("a", a), ("c", c), ("s", s)):
        pf = [r["prefill_tps"] for r in rs if r["depth_k"] == 250000]
        v1, v2 = round(min(pf), 1), round(max(pf), 1)
        summary.append([f"stage_{stage}_prefill_250k_range_derived", "250k", v1, "" if v1 == v2 else v2, "tok/s"])
    win = open(os.path.join(RAW, "strata-mtp-sweep-winner.txt")).read().strip()
    summary.append(["winner_gate", "driver arbiter", win, "", "spec_min_p"])
    write_csv("mtp-sweep-summary.csv", ["metric", "key", "value", "value2", "unit"], summary)
    return rows


# ---------------------------------------------------------- model-bench ----
def release():
    rows = []
    for eng, src in (("0.1.32", "model-bench-0-1-32-base-results.jsonl"),
                     ("0.1.39", "model-bench-0-1-39-base-results.jsonl")):
        for r in read_jsonl(src):
            if r.get("kind") != "arm" or r.get("error"):
                continue
            g = r["gpus"]
            rows.append([eng, r["depth_k"], r["ptok"], r["gen"], r["prefill_tps"], r["decode_tps"],
                         r["wall_s"], g[0]["used_mib"], g[1]["used_mib"], g[0]["temp_c"], g[1]["temp_c"], r["ts"]])
    cols = ["engine", "depth_k", "ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
            "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c", "ts"]
    write_csv("release-0-1-32-vs-0-1-39.csv", cols, rows)

    by = {}
    for r in rows:
        by.setdefault(r[0], {})[r[1]] = r
    assert set(by) == {"0.1.32", "0.1.39"}, "need both engines"
    deltas = []
    raw_dd, raw_pd = [], []
    for d in sorted(by["0.1.32"]):
        b = by["0.1.32"][d]
        a = by["0.1.39"][d]
        dd = 100.0 * (a[5] / b[5] - 1)
        pd = 100.0 * (a[4] / b[4] - 1)
        raw_dd.append(dd)
        raw_pd.append(pd)
        deltas.append([d, b[5], a[5], round(dd, 1), b[4], a[4], round(pd, 1)])
    dd_mean = round(sum(raw_dd) / len(raw_dd), 1)
    pd_mean = round(sum(raw_pd) / len(raw_pd), 1)
    deltas.append(["mean", "", "", dd_mean, "", "", pd_mean])
    write_csv("release-deltas.csv",
              ["depth_k", "decode_0_1_32", "decode_0_1_39", "decode_delta_pct_derived",
               "prefill_0_1_32", "prefill_0_1_39", "prefill_delta_pct_derived"], deltas)
    print(f"  release means: decode {dd_mean:+.1f}%  prefill {pd_mean:+.1f}%")
    return rows


# --------------------------------------------------------------- series -----
def depth_series():
    cols = ["depth_k", "book", "ptok", "gen", "prefill_tps", "decode_tps", "draft_n", "draft_acc",
            "wall_s", "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c"]
    rows = []
    for r in read_jsonl("depth-decode3.jsonl"):
        g = r["vram_after"]
        rows.append([r["depth_k_target"], r["book"], r["ptok"], r["gen"], r["prefill_tps"],
                     r["decode_tps"], r["draft_n"], r["draft_acc"], r["wall_s"],
                     g[0]["used_mib"], g[1]["used_mib"], g[0]["temp_c"], g[1]["temp_c"]])
    write_csv("depth-series-0-1-32.csv", cols, rows)
    return rows


def hero():
    cols = ["kind", "depth_label", "ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
            "ingest_s", "decode_s", "stream_events"]
    rows = []
    for r in read_jsonl("strata-hero.jsonl"):
        if r["kind"] == "depth":
            rows.append(["depth", f"{r['depth'] // 1000}k", r["ptok"], r["gen"], r["prefill_tps"],
                         r["decode_tps"], r["wall"], "", "", ""])
        else:
            rows.append(["hero", "250k (hero run)", r["ptok"], r["gen"], "", "", "",
                         r["ingest_s"], r["decode_s"], len(r["events_epoch"])])
    write_csv("hero-250k.csv", cols, rows)
    return rows


# ------------------------------------------------------------- bring-up -----
def bring_up():
    cols = ["group", "label", "ptok", "gen", "prefill_tps", "decode_tps", "wall_s", "note"]
    rows = []
    compares = {
        "strata-compare-dual.log":    ("two cards (pre-NVMe)", ""),
        "strata-compare-dual2.log":   ("two cards (pre-NVMe)", ""),
        "strata-compare-dual3.log":   ("two cards (pre-NVMe)", ""),
        "strata-compare-single2.log": ("single card (pre-NVMe)", "cold server, HDD-streamed"),
        "strata-compare-dual4.log":   ("two cards (post-NVMe)", ""),
        "strata-compare-single3.log": ("single card (post-NVMe)", ""),
    }
    for src, (grp, note) in compares.items():
        txt = open(os.path.join(RAW, src), encoding="utf-8").read()
        for m in re.finditer(r"(?:dual\d?|single\d) (8k|100k): wall (\d+)s \| ptok (\d+) \| prefill ([\d.]+) tok/s \| gen (\d+) at ([\d.]+) tok/s", txt):
            n = note
            if src == "strata-compare-dual.log" and m.group(1) == "8k":
                n = "warm-up contaminated (HDD cold-load)"
            rows.append([grp, m.group(1), int(m.group(3)), int(m.group(5)),
                         float(m.group(4)), float(m.group(6)), int(m.group(2)), n])
    rows.append(["256K context check", "250,592-token prompt", 250592, 62, 1488.2, 51.9, "",
                 "ctx 262144 on both cards; engine log line (extracts in raw/)"])
    write_csv("load-checks.csv", cols, rows)
    return rows


def main():
    print("sweeps:")
    b = sweep_csv("strata-sampler-sweep-base.jsonl", "sampler-sweep-base.csv")
    m = mtp_sweep()
    print("model-bench:")
    r = release()
    print("series:")
    d = depth_series()
    h = hero()
    print("load checks:")
    u = bring_up()

    counts = {"mtp sweep": len(m), "sampler sweep": len(b),
              "release battery 0.1.32": len([x for x in r if x[0] == "0.1.32"]),
              "release battery 0.1.39": len([x for x in r if x[0] == "0.1.39"]),
              "depth series": len(d), "hero series": len(h), "load checks": len(u)}
    total = sum(counts.values())
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"TOTAL recorded runs: {total}")
    assert len(m) == 126 and len(b) == 20
    assert counts["release battery 0.1.32"] == 6 and counts["release battery 0.1.39"] == 6
    assert len(d) == 6 and len(h) == 6 and len(u) == 13


if __name__ == "__main__":
    main()
