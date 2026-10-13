#!/usr/bin/env python3
"""Build data/csv/ for the MiniCPM-V 4.7 dataset from data/raw/.

Mechanical move: every value is read straight off the runs' results.jsonl
(the abandoned chat-endpoint run is NOT here; only the two clean batteries).
Run from anywhere: `python3 scripts/build_data.py`.

Sources -> outputs
  raw/model-bench-minicpmv47-q8-results.jsonl        -> csv/minicpmv47-q8-v100-depth.csv         (layer split)
  raw/model-bench-minicpmv47-q8-tensor-results.jsonl -> csv/minicpmv47-q8-v100-depth-tensor.csv  (tensor split)
  both                                               -> csv/minicpmv47-q8-split-comparison.csv

No derived columns in the CSVs: nothing here is computed, everything is measured.
The comparison chart derives its own percents; this script prints them for the docs.
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


COLS = ["depth_k", "book", "ptok", "gen", "prefill_tps", "decode_tps", "wall_s",
        "gpu0_used_mib", "gpu1_used_mib", "gpu0_temp_c", "gpu1_temp_c", "ts"]


def load_run(results_name, meta_name, split_mode):
    results = read_jsonl(results_name)
    meta = json.load(open(os.path.join(RAW, meta_name), encoding="utf-8"))
    warmups = [r for r in results if r.get("kind") == "warmup"]
    arms = [r for r in results if r.get("kind") == "arm" and not r.get("error")]
    skipped = [r for r in results if r.get("kind") == "skipped"]
    errors = [r for r in results if r.get("error")]
    assert len(warmups) == 1, f"{results_name} warmups: {len(warmups)}"
    assert len(arms) == 6, f"{results_name} arms: {len(arms)}"
    assert not skipped and not errors, f"{results_name}: unexpected skipped/error rows"
    assert meta.get("finished_utc") and not meta.get("aborted"), f"{results_name}: not finished cleanly"
    assert meta["detected"]["backend"] == "llamacpp"
    rows = []
    for r in sorted(arms, key=lambda r: r["depth_k"]):
        g = r.get("gpus") or []
        rows.append([r["depth_k"], r["book"], r["ptok"], r["gen"], r["prefill_tps"],
                     r["decode_tps"], r["wall_s"],
                     g[0].get("used_mib"), g[1].get("used_mib"),
                     g[0].get("temp_c"), g[1].get("temp_c"), r["ts"]])
    write_csv(f"minicpmv47-q8-v100-depth{'' if split_mode == 'layer' else '-tensor'}.csv", COLS, rows)
    return rows


def main():
    layer = load_run("model-bench-minicpmv47-q8-results.jsonl",
                     "model-bench-minicpmv47-q8-meta.json", "layer")
    tensor = load_run("model-bench-minicpmv47-q8-tensor-results.jsonl",
                      "model-bench-minicpmv47-q8-tensor-meta.json", "tensor")

    # same prompts on both sides is the precondition for comparing them - prove it
    for l, t in zip(layer, tensor):
        assert l[0] == t[0] and l[2] == t[2], f"prompt mismatch at {l[0]}: {l[2]} vs {t[2]}"
    print("  comparability: identical sliced prompts on both sides (ptok equal at all six depths)")

    rows = []
    for mode, data in (("layer", layer), ("tensor", tensor)):
        for r in data:
            rows.append([mode, r[0], r[1], r[2], r[3], r[4], r[5]])
    write_csv("minicpmv47-q8-split-comparison.csv",
              ["split_mode", "depth_k", "book", "ptok", "gen", "prefill_tps", "decode_tps"], rows)

    print("deltas (tensor vs layer):")
    dec_all, pre_all = [], []
    for l, t in zip(layer, tensor):
        dd = 100.0 * (t[5] / l[5] - 1)
        pd = 100.0 * (t[4] / l[4] - 1)
        dec_all.append(dd)
        pre_all.append(pd)
        print(f"  {l[0]//1000:>4}k  decode {l[5]:.1f} -> {t[5]:.1f}  ({dd:+.1f}%)   "
              f"prefill {l[4]:.1f} -> {t[4]:.1f}  ({pd:+.1f}%)")
    print(f"  mean: decode {sum(dec_all)/6:+.1f}%   prefill {sum(pre_all)/6:+.1f}%")

    print("totals: layer 6 + tensor 6 = 12 measured runs, 0 failed (plus 2 discarded warm-ups)")


if __name__ == "__main__":
    main()
