#!/usr/bin/env python3
"""Build data/csv/ for the MiniCPM-V 4.7 dataset from data/raw/.

Mechanical move: every value is read straight off the run's results.jsonl
(the abandoned chat-endpoint run is NOT here; only the clean battery).
Run from anywhere: `python3 scripts/build_data.py`.

Sources -> outputs
  raw/model-bench-minicpmv47-q8-results.jsonl -> csv/minicpmv47-q8-v100-depth.csv
  raw/model-bench-minicpmv47-q8-meta.json     -> asserts context only

No derived columns: nothing in this dataset is computed, everything is measured.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "csv")


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
    return rows


def main():
    results = read_jsonl("model-bench-minicpmv47-q8-results.jsonl")
    meta = json.load(open(os.path.join(RAW, "model-bench-minicpmv47-q8-meta.json"), encoding="utf-8"))

    warmups = [r for r in results if r.get("kind") == "warmup"]
    arms = [r for r in results if r.get("kind") == "arm" and not r.get("error")]
    skipped = [r for r in results if r.get("kind") == "skipped"]
    errors = [r for r in results if r.get("error")]
    assert len(warmups) == 1, f"warmups: {len(warmups)}"
    assert len(arms) == 6, f"arms: {len(arms)}"
    assert not skipped and not errors, "unexpected skipped/error rows"
    assert meta.get("finished_utc") and not meta.get("aborted"), "run not finished cleanly"
    assert meta["detected"]["backend"] == "llamacpp"

    cols = ["depth_k", "book", "ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
            "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c", "ts"]
    rows = []
    for r in sorted(arms, key=lambda r: r["depth_k"]):
        g = r.get("gpus") or []
        rows.append([r["depth_k"], r["book"], r["ptok"], r["gen"], r["prefill_tps"],
                     r["decode_tps"], r["wall_s"],
                     g[0].get("used_mib"), g[1].get("used_mib"),
                     g[0].get("temp_c"), g[1].get("temp_c"), r["ts"]])
    write_csv("minicpmv47-q8-v100-depth.csv", cols, rows)

    print("totals: 7 recorded rows (1 warm-up discarded + 6 measured), 0 failed")


if __name__ == "__main__":
    main()
