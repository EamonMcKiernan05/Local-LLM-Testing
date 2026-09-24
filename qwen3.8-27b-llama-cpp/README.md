# Qwen3.8-27B on 2x / 3x RTX 3060 — every llama.cpp measurement we took

**284 recorded llama.cpp runs on Qwen3.8-27B between 2026-08-14 and 2026-09-23, 277 of which produced a measurement** (7 died at load: 3 in the two-card sweep, 4 in the three-card sweeps), on one desktop-class box with 12 GB consumer cards. Every number here came off a real run on real hardware. Nothing is estimated from a datasheet, and nothing is extrapolated from someone else's rig.

The findings that matter:

- **The built-in MTP head is the fastest speculative decoder for this model on this box.** It beat three DFlash2 drafter quants at every temperature tested (107 runs), and it beat DFlash2 again on two cards and on three cards.
- **`--spec-draft-n-max 7`, ungated, is the peak at 100k prompt depth: 43.07 tok/s decode.** Reproduced five times on the same prompt, spread 0.08 tok/s.
- **The optimum inverts with depth.** At 20k the fastest config is `n-max 2` *ungated* at 44.33 tok/s; at 150k the fastest is `n-max 2` *gated* at 9.15 tok/s. Ungated is 1.72x faster at 20k and 15% slower at 150k.
- **Two-card tensor (row) split beats layer split for decode, and cannot carry DFlash2.** DFlash2 aborts at load under row split (`GGML_ASSERT(src_ss[0].axis != GGML_BACKEND_SPLIT_AXIS_0)`). On two cards you pick tensor+MTP or layer+DFlash2, never both.
- **Prefill degrades gracefully with depth: 1,096.8 tok/s at 20k down to 717.4 at 150k.** Decode follows the opposite curve.
- **On three cards, the extra card buys prefill and costs decode.** `-ts` balance moves prefill only (611 vs 603 vs 514 tok/s); decode is identical to within 0.7%.

The last of those is why the live service now runs what it runs: two cards, tensor split `1,1`, `--spec-draft-n-max 7`, `--temp 0.5`, no sampler flags (the GGUF's own `top_k 20` / `min_p` off apply), at ctx 204800, serving `Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf`.

## The hardware

One box, unchanged through every run except where noted:

| | |
|---|---|
| Board / CPU | MACHINIST X99-MR9A PRO MAX, Xeon E5-2680 v4 (28 threads) |
| RAM | 31 GB DDR4 |
| Cards | 3x RTX 3060 12 GB for the August and Sep-18 work; **2x** from 2026-09-23 20:57, when the third card (PCIe 2.0 x4) dropped off the bus |
| Card links | GPU0/GPU1 PCIe 3.0 x16, GPU2 PCIe 2.0 x4 — no NVLink |
| OS / driver | Ubuntu 24.04.4, NVIDIA 580.173.02 |
| llama.cpp | `b10068` (`571d0d540`) for the August runs, `b11041` (`4fea119de`) from 2026-09-18 |
| Build | CUDA 13.3.73, `CMAKE_CUDA_ARCHITECTURES=86` (sm_86 only) |

Two GGUF files were tested. They are different quants of the same model and they are not interchangeable across the results:

| file | size | quant | used for |
|---|---|---|---|
| `Qwen3.8-27B-UD-Q4_K_XL.gguf` | 17.56 GB | Q4_K_XL (unsloth) | live service until 2026-09-23; the DFlash2 bake-off; the depth profile |
| `Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf` | 12,120,016,960 B | IQ3_S + built-in MTP head | the two-card and three-card sweeps; the live service since 2026-09-23 22:37:19 |

## Method, and what is deliberately not claimed

- **Measurement source is stated per table.** Prompt-processing and token-generation figures come from llama.cpp's own `/completion` `timings` block. Draft acceptance comes either from the per-request `slot print_timing` journal line (in-run, the measured request only) or from the cumulative `/metrics` counters (which include the discarded warm-up). The two disagree for the same arm — `mtp7-untrimmed` reads AL 5.31 in-run and 5.000 cumulative — because they divide by different denominators. Where a table uses cumulative counters, the column name says so.
- **One measured run per arm** in the sweeps, after one discarded warm-up, unless a table says otherwise. Treat spreads under ~3% as noise.
- **A fixed seed makes repeats byte-identical.** Where three repeats are quoted, they prove the measurement is stable, not that three independent samples agree. Every number in the 100k sweeps comes from one 99,589-token prompt, so the honest claim is "fastest for this prompt".
- **Nothing here is a vendor number.** The only third-party figure quoted anywhere is the r0b0tlab RTX 3090 reference in `experiments/04-dflash2-vs-mtp.md`, and it is labelled as theirs, used once to show that our acceptance rates match theirs while our raw speed is a hardware ratio away.

## Repo layout

```
data/csv/     every table from the source reports, one CSV per table, plus a
              normalised file of all 58 raw per-arm records we still hold
data/raw/     the raw per-arm JSONL, harnesses and drivers, unmodified
experiments/  one write-up per experiment, in the order they were run
charts/       the two figures prepared for posting, and the scripts that draw them
scripts/      the parsers that build data/ from the reports and the raw files
HARDWARE.md   the box, the binaries, the exact flag sets
PROVENANCE.md where every file came from, and what could not be reached
```

## The experiments

| # | date | what | arms | headline |
|---|---|---|---|---|
| 01 | 2026-08-14/15 | MTP vs no MTP on live fleet traffic | 2 configs, 23.4M tokens | 17.3 → 24.5 tok/s weighted, acceptance 0.8708 |
| 02 | 2026-09-18 | DFlash2 (3 quants) vs MTP, 4 temperatures, n-max 1-8 | 107 | MTP wins at every temperature |
| 03 | 2026-09-18 | build `b11041` live-service reference at 20k | 2 | 850 / 854 tok/s prefill, 32.95 / 28.30 tok/s decode |
| 04 | 2026-09-20 | prefill rate against prompt depth, q8_0 KV | 9 | 1,096.8 → 717.4 tok/s from 20k to 150k |
| 05 | 2026-09-22/23 | two cards, tensor split, n-max and `-b`/`-ub` grid | 70 | 44.33 tok/s at 20k; the `p-min` gate flips sign with depth |
| 06 | 2026-09-23 | 100k depth: n-max, sampler trims, split modes, three cards | 58 | 43.07 tok/s at n-max 7; `top_k 40` costs 35% |
| 07 | 2026-09-23 | the adopted config, in production | 1 request, 31 samples | 511 tok/s cold prefill, 27.7-32.0 tok/s decode |

Two figures are drawn from this data: `charts/qwen38-27b-llama-cpp-2x3060.png` (the two-card story) and `charts/qwen38-27b-llama-cpp-3x3060.png` (the three-card story, which is where the third card earns its keep on prefill and loses on decode). Both are regenerated by the scripts in `scripts/`.

Plus a separate pass over the **`buun-llama-cpp` fork** (spiritbuun), which is a llama.cpp fork rather than stock: 38 arms, documented in `experiments/08-buun-fork.md`. It is a net regression on this box — twice as slow at prompt processing — with one win: its `turbo4` KV codec decodes 13.05 tok/s at 100k depth against stock's 10.41.

## Reproducing

The full flag set for the winning config:

```bash
/home/eamon/llama.cpp/build/bin/llama-server \
  --parallel 1 -m /home/eamon/models/Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf \
  --split-mode tensor --fit off --tensor-split 1,1 \
  --ctx-size 204800 --flash-attn on \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  -b 2048 -ub 256 --host 0.0.0.0 --port 8080 --jinja \
  --reasoning-preserve --metrics \
  --spec-type draft-mtp --spec-draft-n-max 7 --temp 0.5 --presence_penalty 0.0
```

Two traps worth knowing before you copy any of it:

1. **Do not pass a single sampler flag unless you pass them all.** llama.cpp reads unset sampler parameters from the GGUF's own metadata. This model's metadata says `top_k 20`, `min_p` off. Passing `--top-k 40` thinking you are restating the default costs 35% of generation speed.
2. **`-ub 256` is the prefill sweet spot at every `-b`.** `-ub 128` costs about 4%; `-ub 512` and above cost 1.5-3% and add VRAM, and at 160k context `-ub 2048` kills the server during a long prompt.

## Peaks observed live (not harness runs)

Three figures in this project's history are **not** sweep measurements and are kept out of every table above. They are recorded in `data/csv/live-peak-observations.csv` with their source on each row.

| date | config | workload | figure |
|---|---|---|---|
| 2026-09-23 | two cards, tensor split, MTP `n-max 7` | basic pong coding task, shallow context | **81 tok/s peak decode** — Eamon's own live measurement |
| 2026-09-23 | same config | the production request below | **41.77 tok/s** in llama-server's 3-second window, against 27.73-27.80 sustained |
| 2026-09-24 | three cards, layer split | not recorded | **35 tok/s peak decode** — reported by Eamon |

Read them as bursts, not rates. The distinction matters: llama-server reports both a cumulative `tg` and a `tg_3s` three-second window, and the short window spikes well above the real rate — the second row is proof, at 1.5x its own sustained figure. The controlled two-card arms top out at 44.33 tok/s (20k depth, ungated `n-max 2`) and 43.10 (100k depth, `n-max 7`); a shallow-context coding task has far less KV cache to re-read per step, so a peak above those numbers is mechanically expected, not surprising.

**Rule for using them:** quote a live peak only with its context and only as a peak. Never put one in the same column as a fixed-prompt harness run.

## What we still cannot answer

Stated honestly, because someone will ask:

- **Why the `p-min` gate costs 1.72x at 20k is unexplained.** Both arms have nearly the same acceptance length, but the gated arm takes about 1.8x longer per round. Some cost sits in the gating path itself. A `p-min` curve at `n-max 2` would show whether it is a cliff or gradual — not run.
- **The 100k `-b`/`-ub` grid's generation column is trajectory noise**, not a batch effect: identical flags re-sample slightly differently at temp 0.5 and accept different numbers of draft tokens. Only prefill is trustworthy in that table.
- **Only two `p-min` values were ever tested** (0.85 and 0.00). The mechanical story predicts a shallow-context optimum near the top of the range and a deep-context optimum near 1.0.
- **`n-max 1` was never tested** on the two-card sweeps (range started at 2, by instruction).
- **KV quantisation below q8_0 was never tested on llama.cpp.** It would buy VRAM at 160k and may lift deep decode, at a quality cost.
- **Whether DFlash2 works under tensor split at all** — it aborts on three cards for a reason that is not three-card-specific. One or two arms would settle it.
