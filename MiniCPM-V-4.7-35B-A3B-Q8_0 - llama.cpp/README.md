# MiniCPM-V 4.7 35B-A3B (Q8_0) on 2× Tesla V100 — first bench on llama.cpp

**6 measured runs (one six-depth battery), 0 failed, 2026-10-13.** The model: MiniCPM-V 4.7
35B-A3B — a 35B-parameter MoE with 3B active (Qwen3.6 backbone + SigLIP2 vision), the first MoE
in the MiniCPM-V line — at Q8_0, on 2× Tesla V100 32 GB, served by llama.cpp **build b11580**
(`4413a1924`, the first master build with MiniCPM-V 4.7 support, PR #29416).

The findings:

- **Decode 87.5 tok/s at 20K prompt depth → 57.3 tok/s at 250K.** A 35B-class MoE with 3B active
  decodes like a small dense model on these cards — the old-VRAM-heavy, cheap-compute shape.
- **Prefill 754 tok/s at 20K → 431 tok/s at 250K** (peak 754). Same order of magnitude as the
  engine that normally serves this box at this depth range.
- **The full 256K window fits on the pair**: a 250,032-token prompt served clean, 22.8 + 20.5 GB
  VRAM in use of 32 GB per card, 43 °C peak package. The Q8_0 file is 36.9 GB — all 256 experts
  resident in combined VRAM, zero expert streaming at run time.
- **Vision works on the V100s**: the f16 mmproj read a test image's text and shapes correctly in
  5.2 s wall (one request, the same server).

![Decode and prefill by depth — MiniCPM-V 4.7 35B-A3B Q8_0 on 2× Tesla V100](charts/minicpmv47-35b-a3b-q8-v100-depth.png)

**The numbers:**

| depth | prompt tok | prefill tok/s | decode tok/s | wall s |
|---|---:|---:|---:|---:|
| 20K | 20,032 | 754.0 | 87.5 | 31.4 |
| 60K | 60,032 | 670.5 | 79.7 | 95.2 |
| 100K | 100,032 | 618.4 | 73.7 | 168.4 |
| 150K | 150,032 | 538.2 | 66.8 | 286.6 |
| 200K | 200,032 | 476.6 | 61.1 | 429.1 |
| 250K | 250,032 | 431.4 | 57.3 | 590.5 |

**Method:** one run per depth, six unique documents (one per depth), 400 generated tokens each,
temperature 0.5, fixed seed; prefill/decode read from llama.cpp's own `timings`. Stock serving
flags (ctx 262144, all layers on both cards, f16 KV, flash-attention auto, mmproj loaded) — no
tuning sweeps yet. Raw record: run `2026-10-13T0645Z-minicpmv47-35b-a3b-q8-0-llamacpp` — see
[`PROVENANCE.md`](PROVENANCE.md).

**What's in the folder:**

```
data/raw/     the raw per-arm record + run meta (sha256-checked copies), the engine's own
              per-request log extracts, the vision smoke-test response, the serving command
data/csv/     the depth table everything above is built from
charts/       the depth card, and the script that draws it (reads the CSV)
experiments/  the setup notes and what the numbers say
scripts/      the data builder and the chart script
```

**Honest limits:** one run per depth — treat single cells at depth as carrying the usual ±5-8%
run-to-run noise class; no MTP arm exists (the official GGUF ships no MTP weights — checked);
the DSpark drafter is a separate model and was not tested (side-model tests are deliberately out
of scope); no serving-flag sweeps yet, everything is at stock defaults.
