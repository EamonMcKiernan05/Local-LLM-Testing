#!/usr/bin/env python3
"""Build the 0.2.0-beta release CSVs from the raw model-bench run records.

Sources (all in data/raw/, sha256-checked copies of ~/model-bench/runs on box .5):
  model-bench-0-2-0-beta-nvme-results.jsonl      0.2.0-beta, PLE shard on /mnt/nvme (the comparison arm)
  model-bench-0-2-0-beta-sata-pass1-results.jsonl 0.2.0-beta, PLE shard on the SATA boot SSD (as served)
  model-bench-0-2-0-beta-sata-pass2-results.jsonl the same, second pass
  model-bench-0-2-0-beta-sata-warm20k-results.jsonl  20K re-run after the cold first arm
  data/csv/release-0-1-43-vs-0-1-44-mean3.csv    the last tested version (0.1.44, 3-pass means)

Outputs:
  data/csv/release-0-1-44-vs-0-2-0-beta.csv
  data/csv/release-deltas-020-beta.csv
  data/csv/ple-location-020-beta.csv
  data/csv/ple-location-deltas-020-beta.csv

Every number is parsed from a record, never retyped. The comparison refuses to build
unless the six depths, their corpus books and their sliced token counts match the
0.1.44 record exactly (ptok may drift +/-2 with the per-request unique tag).
"""
import csv
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RAW = os.path.join(ROOT, "data", "raw")
CSV = os.path.join(ROOT, "data", "csv")

OLD42 = os.path.join(CSV, "release-0-1-43-vs-0-1-44-mean3.csv")
OLD_RAW = os.path.join(RAW, "model-bench-0-1-44-base-rep2-results.jsonl")

NVME = os.path.join(RAW, "model-bench-0-2-0-beta-nvme-results.jsonl")
SATA1 = os.path.join(RAW, "model-bench-0-2-0-beta-sata-pass1-results.jsonl")
SATA2 = os.path.join(RAW, "model-bench-0-2-0-beta-sata-pass2-results.jsonl")
SATA20 = os.path.join(RAW, "model-bench-0-2-0-beta-sata-warm20k-results.jsonl")

DEPTHS = [20000, 60000, 100000, 150000, 200000, 250000]


def arms(path):
    out = []
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r.get("kind") == "arm":
            out.append(r)
    return out


def by_depth(rows):
    got = {int(r["depth_k"]): r for r in rows}
    assert sorted(got) == DEPTHS, sorted(got)
    return got


def check_comparable(reference, other, name, depths=None):
    """Same corpus book + same sliced tokens at every depth; ptok within 2."""
    for d in (depths or DEPTHS):
        a, b = reference[d], other[d]
        assert a["book"] == b["book"], (name, d, a["book"], b["book"])
        assert a["sliced_tokens"] == b["sliced_tokens"], (name, d)
        assert abs(int(a["ptok"]) - int(b["ptok"])) <= 2, (name, d, a["ptok"], b["ptok"])


# --- the last tested version: 0.1.44 three-pass means -----------------------
old = {}
with open(OLD42, encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if r["engine"] == "0.1.44":
            old[int(r["depth_k"])] = {
                "ptok": int(r["ptok"]),
                "prefill_tps": float(r["prefill_tps"]),
                "decode_tps": float(r["decode_tps"]),
            }
assert sorted(old) == DEPTHS

old_raw = by_depth(arms(OLD_RAW))

# --- 0.2.0-beta, comparison arm (PLE on NVMe) ------------------------------
nv = arms(NVME)
nv_d = by_depth(nv)
check_comparable(old_raw, nv_d, "nvme-vs-0.1.44")

# --- 0.2.0-beta, as served (PLE on the SATA boot SSD) ----------------------
s1 = by_depth(arms(SATA1))
s2 = by_depth(arms(SATA2))
s20_rows = arms(SATA20)
assert len(s20_rows) == 1 and int(s20_rows[0]["depth_k"]) == 20000
s20 = {20000: s20_rows[0]}
check_comparable(old_raw, s1, "sata-pass1-vs-0.1.44")
check_comparable(old_raw, s2, "sata-pass2-vs-0.1.44")
check_comparable(old_raw, s20, "sata-warm20k-vs-0.1.44", depths=[20000])


def mean_prefill(d):
    if d == 20000:
        # pass 1 and 2's 20K arms ran on a cold box (577.0 / 982.3); the warm re-run is the usable one
        return s20[d]["prefill_tps"], 1
    return statistics.mean([s1[d]["prefill_tps"], s2[d]["prefill_tps"]]), 2


sata = {}
for d in DEPTHS:
    p, n = mean_prefill(d)
    sata[d] = {"ptok": s20[d]["ptok"] if d == 20000 else s1[d]["ptok"], "prefill_tps": p, "n_runs": n}

# ---------------------------------------------------------------- CSV 1 -----
p1 = os.path.join(CSV, "release-0-1-44-vs-0-2-0-beta.csv")
with open(p1, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["engine", "depth_k", "ptok", "gen", "prefill_tps", "decode_tps", "n_runs"])
    for d in DEPTHS:
        w.writerow(["0.1.44", d, old[d]["ptok"], 400, f"{old[d]['prefill_tps']:.1f}", f"{old[d]['decode_tps']:.1f}", 3])
    for d in DEPTHS:
        w.writerow(["0.2.0-beta", d, nv_d[d]["ptok"], int(nv_d[d]["gen"]),
                    f"{nv_d[d]['prefill_tps']:.1f}", f"{nv_d[d]['decode_tps']:.1f}", 1])

p2 = os.path.join(CSV, "release-deltas-020-beta.csv")
with open(p2, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["depth_k", "prefill_0_1_44", "prefill_0_2_0", "prefill_delta_pct",
                "decode_0_1_44", "decode_0_2_0", "decode_delta_pct"])
    pre_pcts, dec_pcts = [], []
    for d in DEPTHS:
        pp = 100.0 * (nv_d[d]["prefill_tps"] - old[d]["prefill_tps"]) / old[d]["prefill_tps"]
        dp = 100.0 * (nv_d[d]["decode_tps"] - old[d]["decode_tps"]) / old[d]["decode_tps"]
        pre_pcts.append(pp)
        dec_pcts.append(dp)
        w.writerow([d, f"{old[d]['prefill_tps']:.1f}", f"{nv_d[d]['prefill_tps']:.1f}", f"{pp:.2f}",
                    f"{old[d]['decode_tps']:.1f}", f"{nv_d[d]['decode_tps']:.1f}", f"{dp:.2f}"])
    w.writerow(["mean", "", "", f"{statistics.mean(pre_pcts):.2f}", "", "", f"{statistics.mean(dec_pcts):.2f}"])

# ---------------------------------------------------------------- CSV 2 -----
p3 = os.path.join(CSV, "ple-location-020-beta.csv")
with open(p3, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["config", "depth_k", "ptok", "prefill_tps", "n_runs"])
    for d in DEPTHS:
        w.writerow(["PLE on SATA SSD", d, sata[d]["ptok"], f"{sata[d]['prefill_tps']:.1f}", sata[d]["n_runs"]])
    for d in DEPTHS:
        w.writerow(["PLE on NVMe", d, nv_d[d]["ptok"], f"{nv_d[d]['prefill_tps']:.1f}", 1])

p4 = os.path.join(CSV, "ple-location-deltas-020-beta.csv")
with open(p4, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["depth_k", "sata_prefill", "nvme_prefill", "delta_pct"])
    pcts = []
    for d in DEPTHS:
        pct = 100.0 * (nv_d[d]["prefill_tps"] - sata[d]["prefill_tps"]) / sata[d]["prefill_tps"]
        pcts.append(pct)
        w.writerow([d, f"{sata[d]['prefill_tps']:.1f}", f"{nv_d[d]['prefill_tps']:.1f}", f"{pct:.2f}"])
    w.writerow(["mean", "", "", f"{statistics.mean(pcts):.2f}"])

print("wrote", p1)
print("wrote", p2)
print("wrote", p3)
print("wrote", p4)
print("0.1.44 -> 0.2.0-beta mean prefill %+.2f%%, decode %+.2f%%"
      % (statistics.mean(pre_pcts), statistics.mean(dec_pcts)))
print("PLE SATA -> NVMe mean prefill %+.2f%%" % statistics.mean(pcts))
