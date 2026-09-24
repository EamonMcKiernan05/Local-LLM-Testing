#!/usr/bin/env python3
"""
Normalise the raw per-arm JSONL captured from the benchmark box into one tidy CSV.

Input : data/raw/*.jsonl  (copied verbatim from /home/eamon/*.jsonl on the
        inference box at the end of the 2026-09-23 sweeps)
Output: data/csv/100k-and-three-card-arms-normalised.csv

Fields are renamed but never recalculated. Note on counters:
`acceptance_length`, `proposed_per_round` and `token_accept_rate` in these files
come from llama.cpp's cumulative /metrics counters, which include the discarded
warm-up request, so they read slightly low. The in-run values (measured request
only) are the ones quoted in the published tables under experiments/.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "csv", "100k-and-three-card-arms-normalised.csv")

SOURCES = {
    "100k-arm-results.jsonl": "100k n-max + sampler trim sweep (stage A+B)",
    "100k-nmax-confirm.jsonl": "100k n-max 5-8 confirmation, 3 repeats",
    "100k-split-mode-matrix.jsonl": "100k split-mode matrix, n-max 7, 2 repeats",
    "three-card-matrix.jsonl": "3-card matrix (layer/tensor, -ts balances)",
    "three-card-dflash2.jsonl": "3-card DFlash2 n-max sweep + drafter pinning",
}

COLS = [
    ("experiment", lambda r, s: s),
    ("label", lambda r, s: r.get("label")),
    ("target_model", lambda r, s: (r.get("target") or "").split("/")[-1]),
    ("split_mode", lambda r, s: r.get("split")),
    ("tensor_split", lambda r, s: r.get("ts")),
    ("spec_family", lambda r, s: (r.get("spec") or [None])[0]),
    ("spec_n_max", lambda r, s: (r.get("spec") or [None, None])[1]),
    ("spec_p_min", lambda r, s: (r.get("spec") or [None, None, None])[2]),
    ("top_k", lambda r, s: r.get("top_k")),
    ("min_p", lambda r, s: r.get("min_p")),
    ("temp", lambda r, s: r.get("temp")),
    ("ctx_total", lambda r, s: r.get("ctx")),
    ("batch_b", lambda r, s: r.get("b")),
    ("ubatch_ub", lambda r, s: r.get("ub")),
    ("n_predict", lambda r, s: r.get("n_predict")),
    ("prompt_tokens", lambda r, s: r.get("prompt_tokens")),
    ("prefill_tok_s", lambda r, s: r.get("prefill_tok_s")),
    ("prefill_ms", lambda r, s: r.get("prefill_ms")),
    ("gen_tokens", lambda r, s: r.get("gen_tokens")),
    ("gen_tok_s", lambda r, s: r.get("gen_tok_s")),
    ("gen_ms", lambda r, s: r.get("gen_ms")),
    ("acceptance_length_metrics_cumulative", lambda r, s: r.get("acceptance_length")),
    ("proposed_per_round_metrics_cumulative", lambda r, s: r.get("proposed_per_round")),
    ("token_accept_rate_metrics_cumulative", lambda r, s: r.get("token_accept_rate")),
    ("output_sha256_16hex", lambda r, s: r.get("output_sha256")),
    ("vram_after_load_mib", lambda r, s: r.get("vram_after_load_mib")),
    ("peak_vram_mib", lambda r, s: r.get("peak_vram_mib")),
    ("repeat", lambda r, s: r.get("repeat")),
    ("backend_sampling_on_gpu", lambda r, s: r.get("backend_sampling_on_gpu")),
    ("wall_s", lambda r, s: r.get("wall_s")),
    ("error", lambda r, s: r.get("error")),
]


def main():
    rows = []
    for fname, desc in SOURCES.items():
        path = os.path.join(RAW, fname)
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                rows.append([fn(r, desc) for _, fn in COLS])

    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([c for c, _ in COLS])
        w.writerows(rows)

    ok = sum(1 for r in rows if r[19] is not None)
    print(f"{len(rows)} arms normalised ({ok} with a decode measurement, "
          f"{len(rows) - ok} aborted at load) -> {OUT}")


if __name__ == "__main__":
    main()
