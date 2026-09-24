# 05 — two cards, tensor split: n-max, depth and the `-b`/`-ub` grid

**2026-09-22 22:09 to 2026-09-23 02:16. Build `b11041`. `Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf`, 2x RTX 3060, tensor (row) split `1,1`, q8_0 K/V, flash attention on.**

**70 measured arms, 67 successful, 3 failed.**

## Headline

- **Fastest decode at 20k depth: 44.33 tok/s** — MTP `--spec-draft-n-max 2`, **ungated** (`--spec-draft-p-min 0.00`), `-b 2048 -ub 256`. Verified over three repeats: 44.38 / 44.33 / 44.29, spread 0.09.
- **Fastest decode at 150k depth: 9.15 tok/s** — MTP `n-max 2`, **gated** (`p-min 0.85`). Prefill 452.8 tok/s.
- **The `p-min` gate flips sign with depth.** Ungated is 1.72x faster at 20k and about 15% *slower* at 150k.
- **Tensor split balances the two cards to within 8 MiB** where layer split left GPU1 about 2.4 GB heavier — and it removes the OOM fallback layer split needed.
- **DFlash2 cannot run under row split at all.** It aborts at load. On two cards you choose tensor+MTP or layer+DFlash2, never both.

## Scope

- Tensor (row) split only, two cards. CUDA2 (the PCIe 2.0 x4 card) deliberately excluded — a row-split collective is gated by the slowest link.
- MTP speculation only, `--spec-draft-n-max` 2 through 8, gated (`0.85`) and ungated (`0.00`).
- Two depths: 20,000 and 150,000 prompt tokens.
- Then every `-b`/`-ub` pair from {128, 256, 512, 1024, 2048, 4096} at the fastest MTP config, both depths. Pairs with `ub > b` were skipped: llama.cpp clamps `n_ubatch = min(n_batch, n_ubatch)` (`src/llama-context.cpp:247`), so they are the same configuration twice.
- Everything at temp 0.6, `--top_p 0.95 --top_k 20`, seed 12345, 256 tokens generated.

## What fits at 160k context (load tests, no prompt)

| split | spec | GPU0 MiB | GPU1 MiB | free on GPU1 | notes |
|---|---|---|---|---|---|
| layer `1,1` | none | 8,729 | 10,049 | 2,239 | clean |
| layer `1,1` | MTP n8 | 9,343 | **11,703** | **585** | `cudaMalloc failed` for a 421 MiB compute buffer, then `retrying without pipeline parallelism` — fitted only via a fallback |
| layer `1,1` | DFlash2 n4 | 9,525 | 10,821 | 1,467 | clean |
| **tensor `1,1`** | none | 9,241 | 9,233 | 3,055 | clean, balanced to 8 MiB |
| **tensor `1,1`** | **MTP n8** | **10,453** | **10,445** | **1,843** | **clean, no OOM, no fallback** |

Two conclusions. First, **tensor split fixes the layer split's imbalance**: under layer split the KV cache rides the 16 full-attention layers, so GPU1 carried ~2.4 GB more than GPU0 and MTP only loaded through a retry path. Second, **160k on two cards with q8_0 KV plus MTP is essentially the ceiling** — there is no room left to also carry a drafter's own cache at this context.

Through the sweep at 150k depth, VRAM after load ranged 9,887-10,709 MiB per card and peaked at 10,935, against 12,288.

## DFlash2 aborts under tensor split

Two variants, both abort at load:

- `-sm tensor -ts 1,1 -md <drafter> --spec-type draft-dflash` (drafter on both cards):
  `ggml/src/ggml-backend-meta.cpp:543: GGML_ASSERT(src_ss[0].axis != GGML_BACKEND_SPLIT_AXIS_0) failed` — `ggml_abort` inside `ggml_gallocr_alloc_graph`, reached from the load-time decode probe.
- Same with the drafter pinned to one card, `--spec-draft-device CUDA0`: also aborts, but earlier — `llama_init_from_model` → `sched_reserve` → `ggml_backend_sched_split_graph`.

One root cause: the draft context inherits the target's device list and split mode when `--spec-draft-device` is not given (`common/speculative.cpp:2476-2479`), and the DFlash2 graph cannot be split across backends in row mode. DFlash2 loads and runs normally under **layer** split, so the drafter itself is fine. This matches the independent ExLlamaV3 finding for the same drafter: *"DFlash2 does not support tensor-parallel targets because the selector needs top-k logits."*

**Consequence: on two cards you pick one — tensor split + MTP, or layer split + DFlash2.** Since DFlash2's advantage is concentrated at shallow context and its acceptance collapses with depth, tensor + MTP is the better default.

## MTP n-max sweep — 20,000-token depth

Prompt 19,953 tokens, ctx 32,768, 256 generated, temp 0.6, `-b 2048 -ub 256`. AL and accept are in-run values.

| n-max | p-min | prefill tok/s | **gen tok/s** | AL | accept |
|---|---|---|---|---|---|
| 2 | 0.00 | 649.80 | **43.40** | 2.329 | 0.6689 |
| 4 | 0.00 | 646.43 | 42.73 | 2.983 | 0.4958 |
| 3 | 0.00 | 650.12 | 42.08 | 2.565 | 0.5268 |
| 6 | 0.00 | 646.97 | 37.92 | 3.143 | 0.3647 |
| 8 | 0.00 | 640.63 | 37.26 | 3.243 | 0.2912 |
| 5 | 0.00 | 641.55 | 36.83 | 2.928 | 0.3855 |
| 7 | 0.00 | 648.51 | 35.16 | 3.200 | 0.3218 |
| 4 | 0.85 | 648.13 | 32.18 | 3.500 | 0.9697 |
| 3 | 0.85 | 649.99 | 30.71 | 3.114 | 0.9610 |
| 5 | 0.85 | 639.91 | 30.57 | 3.581 | 0.9756 |
| 6 | 0.85 | 639.72 | 30.06 | 3.860 | 0.9760 |
| 7 | 0.85 | 644.29 | 29.91 | 3.828 | 0.9647 |
| 8 | 0.85 | 644.12 | 29.87 | 3.982 | 0.9653 |
| 2 | 0.85 | 643.74 | 26.01 | 2.439 | 0.9593 |

- **Prefill is flat across every arm** (640-650 tok/s): the draft window costs prompt processing essentially nothing.
- **The gate is the single biggest lever at shallow depth: ungated beats gated at every window** (43.40 vs 26.01 at n-max 2; 42.73 vs 32.18 at n-max 4).
- **Ungated peaks at n-max 2-4.** Past 4 the extra drafts stop paying: n-max 8 falls to 37.26 despite the longest acceptance (AL 3.243) because only 29% of proposed tokens are accepted.
- **Gated peaks at n-max 4** (32.18) and falls to 29.87 at n-max 8 even as AL climbs 3.50 → 3.98 — accepting more per round stops meaning more throughput once the round gets expensive.

### Verification of the ungated result

The first 43.40 tok/s run stopped early: the model emitted EOS after 164 of the 256 requested tokens, so the two arms were not doing equal work. Re-measured with `ignore_eos: true` forcing exactly 256 tokens, three runs per arm:

| arm | run 1 | run 2 | run 3 | mean | spread |
|---|---|---|---|---|---|
| `n-max 2`, `p-min 0.00` | 44.38 | 44.33 | 44.29 | **44.33** | 0.09 |
| `n-max 2`, `p-min 0.85` | 25.81 | 25.68 | 25.78 | **25.76** | 0.13 |

Both arms produced byte-identical output across their three repeats, so these are stable measurements, not lucky draws. **The ungated advantage is real: 44.33 against 25.76 tok/s, a 1.72x difference.**

What it is *not* is explained. Acceptance length is nearly the same in both arms (2.381 ungated vs 2.439 gated) and the ungated arm proposes *more* draft tokens per round, yet it finishes a 256-token generation in 5,752 ms against the gated arm's 9,891 ms — about 1.8x the time per round for the same tokens per round. Some cost is attached to the gating path itself. Mapping `p-min` (0.0 / 0.4 / 0.6 / 0.7 / 0.8 / 0.85 / 0.9 / 0.95 at n-max 2) would show whether that cost is a cliff or gradual. **Not run.**

## MTP n-max sweep — 150,000-token depth

Ctx 163,840, prompt ~149.5k tokens. Same flags otherwise.

| n-max | p-min | prefill tok/s | **gen tok/s** | AL | accept |
|---|---|---|---|---|---|
| 2 | 0.85 | 452.76 | **9.15** | 1.667 | 0.6667 |
| 4 | 0.85 | 448.20 | 8.90 | 1.667 | 0.6667 |
| 3 | 0.85 | 452.85 | 8.87 | 1.667 | 0.6667 |
| 5 | 0.85 | 453.68 | 8.80 | 1.667 | 0.6667 |
| 6 | 0.85 | 452.63 | 8.72 | 1.667 | 0.6667 |
| 7 | 0.85 | 449.57 | 8.50 | 1.667 | 0.6667 |
| 8 | 0.85 | 453.42 | 8.43 | 1.667 | 0.6667 |
| 2 | 0.00 | 455.99 | 7.78 | 1.667 | 0.3529 |
| 3 | 0.00 | 453.36 | 7.23 | 1.667 | 0.2400 |
| 4 | 0.00 | 452.92 | 6.48 | 2.143 | 0.2857 |
| 5 | 0.00 | 451.77 | 5.98 | 2.143 | 0.2286 |
| 6 | 0.00 | 452.10 | 5.76 | 1.875 | 0.1707 |
| 7 | 0.00 | 451.98 | 5.36 | 1.875 | 0.1489 |
| 8 | 0.00 | 449.25 | 5.21 | 1.875 | 0.1321 |

**The ranking inverts at depth, and the reason is mechanical.** At 150k tokens every verification position attends over the whole KV cache, so the round is no longer flat-cost: cost scales with the number of verified positions. Rejected draft tokens are then pure waste rather than nearly free.

- **Gated beats ungated at every window** (9.15 vs 7.78 at n-max 2; 8.43 vs 5.21 at n-max 8) — the exact opposite of the 20k result.
- **Every gated arm reports identical AL 1.667 and acceptance 0.6667.** The gate truncates the draft chain at the same point however wide the window is, because at depth the MTP head is not confident enough to run a long chain. `n-max` therefore barely binds; what the gate buys is a *shorter round*.
- **Ungated acceptance collapses with depth**: 0.353 at n-max 2 down to 0.132 at n-max 8, while AL only creeps from 1.667 to 1.875. Wide drafts at depth are mostly rejected work.
- **Prefill is flat again** (449-456 tok/s) and about 30% below the 20k figure (645) — the inherent cost of attention over a long KV.

## `-b`/`-ub` grid

Full grids: `data/csv/two-card-bub-grid-150k.csv` and `two-card-bub-grid-20k.csv` (21 pairs each, base config `mtp2-tensor-q8`).

**At 150k depth**, the batch setting moves **prefill by up to 8.7%** and **generation by nothing at all**: every successful combination lands in 8.97-9.24 tok/s, a 3% spread, with identical AL (1.667) and acceptance (0.6667). Best prefill `-b 4096 -ub 256` at 455.46 tok/s; `-ub 256` wins at every `-b` value, `-ub 128` costs ~4%, `-ub 512+` costs 1.5-3% and adds VRAM. Three arms failed outright: `-b 2048 -ub 2048` and `-b 4096 -ub 2048` died mid-request, `-b 4096 -ub 4096` never became healthy.

**At 20k depth**, the same prefill story applies (`-b 2048 -ub 256` best at 652.77 tok/s). The generation column spreads 23.4-32.8 tok/s, but that spread tracks **acceptance length** (AL 2.11-2.70), not the batch setting. With one run per configuration, **treat the 20k generation column as trajectory noise and the prefill column as the real effect.**

## Fastest configurations measured

| requirement | config | result |
|---|---|---|
| **Fastest decode, 20k** | MTP `n-max 2`, `p-min 0.00`, `-b 2048 -ub 256` | **44.33 tok/s** (mean of 3, spread 0.09), ~650 tok/s prefill |
| Runner-up, 20k | MTP `n-max 4`, `p-min 0.00` | 42.73 tok/s, 646.4 tok/s prefill |
| Best gated (live-style), 20k | MTP `n-max 4`, `p-min 0.85` | 32.18 tok/s, 648.1 tok/s prefill |
| **Fastest decode, 150k** | MTP `n-max 2`, `p-min 0.85`, `-b 2048 -ub 256` | **9.15 tok/s**, 452.8 tok/s prefill |
| **Best prefill, 150k** | same, `-b 4096 -ub 256` | **455.46 tok/s**, 9.04 tok/s decode |
| **Best prefill, 20k** | same, `-b 2048 -ub 256` | **652.77 tok/s** prefill |
| Cleanest 160k load | tensor `1,1`, MTP `n-max 8` | 10,453 / 10,445 MiB, no OOM, no fallback |

**If you pick one setting:** `--split-mode tensor --tensor-split 1,1 --spec-type draft-mtp --spec-draft-n-max 2 --spec-draft-p-min 0.85 -b 2048 -ub 256`. Fastest at 150k depth, near-best prefill, lowest VRAM. For shallow-context work, dropping `--spec-draft-p-min` to 0 and raising `n-max` to 4 measured 30-60% faster — but it costs you at depth, so it is a per-workload choice, not a new default.

## Method

| item | value |
|---|---|
| Target | `Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf` — 12,120,016,960 B, arch `qwen35` |
| Drafter | `Qwen3.8-27B-DFlash2-Q2_K_S-MIX.gguf` — 561,241,824 B (layer split only) |
| Harness | `~/dflash_test_big.py` — one deterministic seeded prompt, `cache_prompt:false`, one measured `/completion` per config after a discarded warm-up; `timings` from the response, speculative counters from `/metrics` |
| Driver | `~/two-card-gsq-sweep.py` — resumable, refuses to start while the live service is active or if either GGUF is the wrong size |

**One measured run per configuration**, after a discarded warm-up, so treat spreads under ~3% as noise. At 20k, generation differences across the grid track acceptance length rather than the batch setting — at temp 0.6, batching changes the numerics just enough to move the sampled trajectory. **Prefill is the trustworthy signal in the grid.**
