# 06 — 100k depth: n-max, sampler trims, split modes, and three cards

**2026-09-23, 11:30 to 17:48. Build `b11041`. `Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf`, q8_0 K/V, flash attention on, ctx 131072, `-b 2048 -ub 256`, prompt 99,589 tokens, 256 generated, seed 12345, temp 0.5. One measured run per arm after a discarded warm-up.**

**58 measured arms: 20 (stages A+B) + 12 (confirmation) + 8 (split-mode matrix) + 7 (three-card matrix) + 11 (DFlash2 on three cards). 54 produced numbers, 4 aborted at load.**

## Headline

- **Fastest decode at 100k depth: 43.07 tok/s** — MTP `--spec-draft-n-max 7`, ungated, tensor split `1,1`. Prefill 513.55 tok/s.
- **The sampler trim grid cannot beat it.** `top_k 20` with `min_p` anywhere in 0.05-0.10 gives 43.01 / 43.05 / 43.03 — a 0.1% spread. `min_p` is inert once `top_k` is 20.
- **Forcing `top_k 40` is the worst thing you can do: 27.97 tok/s, 35% below the winner.**
- **The n-max curve peaks sharply at 7**, not at the widest window: 26.92 (n1), 32.98 (n2), 35.04 (n3), 33.40 (n4), 31.36 (n5), 33.85 (n6), **43.07 (n7)**, 35.60 (n8).
- **Prefill is flat and configuration-independent**: 506.81-518.27 tok/s across all 20 arms, a 2.2% spread. Samplers act after prompt processing, so prefill carries no configuration signal here.
- **Layer split restores GPU-side sampling; tensor split refuses it. It buys nothing.** Tensor split was 1.64x faster at decode while keeping its sampler on the CPU.
- **Tensor split works on three cards** — the odd-card-count concern is disproven — but is 40% slower at prefill and 44% slower at decode, because the third card's PCIe 2.0 x4 link gates the row-split collective.
- **Layer split on three cards is the best prefill configuration measured at this depth: 599 tok/s**, 18% above tensor-2 — and it loses decode, 1.72x behind tensor-2.

## Stage A — MTP n-max, "untrimmed"

`--spec-draft-n-max` 1-8, `--spec-draft-p-min 0.00`, and **no** `--top-k` / `--top-p` / `--min-p` on the command line.

| arm | prefill tok/s | **gen tok/s** | AL (in-run) | accept (in-run) | proposals/round | VRAM after load (G0/G1 MiB) |
|---|---|---|---|---|---|---|
| `mtp1-untrimmed` | 516.51 | 26.92 | 1.850 | 0.848 | 1.003 | 9,161 / 9,153 |
| `mtp2-untrimmed` | 512.42 | 32.98 | 2.550 | 0.775 | 2.000 | 9,237 / 9,229 |
| `mtp3-untrimmed` | 518.27 | 35.04 | 3.060 | 0.687 | 3.000 | 9,311 / 9,303 |
| `mtp4-untrimmed` | 513.94 | 33.40 | 3.190 | 0.552 | 3.967 | 9,387 / 9,379 |
| `mtp5-untrimmed` | 512.60 | 31.36 | 3.310 | 0.465 | 4.970 | 9,461 / 9,453 |
| `mtp6-untrimmed` | 515.78 | 33.85 | 3.850 | 0.475 | 6.003 | 9,535 / 9,527 |
| **`mtp7-untrimmed`** | 513.55 | **43.07** | 5.310 | 0.618 | 6.975 | 9,611 / 9,603 |
| `mtp8-untrimmed` | 510.16 | 35.60 | 4.400 | 0.428 | 7.939 | 9,685 / 9,677 |

VRAM after load rises monotonically with n-max, 9,161 → 9,685 MiB per card, because the draft context grows with the proposal window. Peak during generation adds about 165 MiB.

n-max 8 is the only arm where the window is clearly over-wide: it proposes the most tokens per round of any arm in either stage (7.9) and converts 42.8% of them.

## Stage B — `top_k` x `min_p` at n-max 7

| arm | top_k | min_p | prefill tok/s | gen tok/s | AL | accept |
|---|---|---|---|---|---|---|
| `mtp7-topk20-minp005` | 20 | 0.05 | 512.55 | 43.01 | 5.310 | 0.616 |
| `mtp7-topk20-minp008` | 20 | 0.08 | 513.65 | **43.05** | 5.310 | 0.616 |
| `mtp7-topk20-minp01` | 20 | 0.10 | 513.78 | 43.03 | 5.310 | 0.616 |
| `mtp7-topk30-minp008` | 30 | 0.08 | 513.95 | 41.24 | 5.100 | 0.594 |
| `mtp7-topk50-minp005` | 50 | 0.05 | 515.64 | 40.59 | 5.000 | 0.573 |
| `mtp7-topk50-minp008` | 50 | 0.08 | 514.48 | 34.84 | 4.250 | 0.469 |
| `mtp7-topk50-minp01` | 50 | 0.10 | 516.24 | 34.11 | 4.180 | 0.460 |
| `mtp7-topk40-minp01` | 40 | 0.10 | 513.10 | 34.07 | 4.180 | 0.460 |
| `mtp7-topk40-minp008` | 40 | 0.08 | 506.81 | 34.06 | 4.180 | 0.460 |
| `mtp7-topk30-minp01` | 30 | 0.10 | 513.31 | 37.80 | 4.640 | 0.522 |
| `mtp7-topk30-minp005` | 30 | 0.05 | 512.27 | 37.70 | 4.640 | 0.519 |
| `mtp7-topk40-minp005` | 40 | 0.05 | 513.16 | **27.97** | 3.450 | 0.356 |

`top_k` is the only lever that matters, and it runs **backwards from intuition**: 20 → 43.0, 30 → 37.7-41.2, 40 → 28.0-34.1, 50 → 34.1-40.6 tok/s. Widening the pool makes the target pick less predictable tokens, so fewer drafts survive verification.

Three arms are byte-identical in output despite different `min_p`: all three `top_k 20` arms share `output_sha256 34fd0b3a3fcbd528`, and `topk40-minp008`, `topk40-minp01`, `topk50-minp01` share `cc0bb028921b3645`. A tight `top_k` already removes the tokens `min_p >= 0.05` would remove.

## The trap: "untrimmed" is not llama.cpp's stock sampler

Stage A was documented at the time as running llama.cpp's stock defaults (`--top-k 40`, `--top-p 0.95`, `--min-p 0.05`). It does not. **With no sampler flags on the command line, llama.cpp `b11041` reads the sampler settings embedded in the GGUF and uses those instead.**

This model's metadata:

| GGUF key | value |
|---|---|
| `general.sampling.top_k` | **20** |
| `general.sampling.top_p` | 0.95 |
| `general.sampling.min_p` | **0.0 (disabled)** |
| `general.sampling.temp` | 1.0 (overridden by the CLI `--temp 0.5`, which *was* passed) |

The mechanism, from the source: `common/common.cpp:1211 common_init_sampler_from_model()` reads a `user_sampling_config` bitfield (`common/common.h:257`) recording which sampler parameters the user actually passed, and for any parameter the user did not pass, looks the value up in the model's GGUF metadata and overwrites the CLI default. It will even replace the whole sampler *sequence* from `general.sampling.sequence` if `--samplers` was not passed. The binary's own `--help` still advertises the plain defaults, which is why the assumption looked safe.

**So the comparison is not like-for-like, and no result is in doubt.** Read correctly, the intended reproduction check passes: `topk20-minp005` — the same `top_k` the untrimmed arms silently inherited — lands **0.14%** off stage A's winner (43.01 against 43.07, AL 5.310 both). The `min_p` difference changes the output hash but not the speed.

You have two coherent options and one trap:

1. Pass no sampler flags at all — you get the model's own recommendation (`top_k 20`, `min_p` off) and the fastest numbers in this sweep.
2. Pass `--top-k 20` explicitly (optionally `--min-p 0.05-0.10`) if you want the setting visible in the process list — measurably the same.
3. **Trap:** passing `--top-k 40` (or any single sampler flag) thinking you are "setting the defaults" actually *changes* behaviour, and costs 35% of generation speed. If you pass one sampler flag, pass them all, so nothing silently inherits from the model metadata.

## Confirmation run — was n-max 7 lucky?

12 arms: n-max 5, 6, 7, 8, three repeats each, everything else identical to stage A.

| n-max | gen tok/s (3 repeats) | mean | range | sd | prefill mean | prefill range |
|---|---|---|---|---|---|---|
| 5 | 31.41 / 31.34 / 31.30 | 31.35 | 0.11 | 0.056 | 508.32 | 4.03 |
| 6 | 33.86 / 33.83 / 33.81 | 33.83 | 0.05 | 0.025 | 505.19 | 4.18 |
| **7** | 43.05 / 43.02 / 43.04 | **43.04** | **0.03** | 0.015 | 507.39 | 4.81 |
| 8 | 35.59 / 35.57 / 35.62 | 35.59 | 0.05 | 0.025 | 505.81 | 2.28 |

**n-max 7 is reproducibly the fastest. The 43.07 tok/s was not a lucky draw.** The three n7 repeats span 0.03 tok/s (0.07% of the mean) against a 7.45 tok/s (21%) gap to the next-best n-max. n7 is now five measurements of this configuration on this prompt: 43.07, 43.05, 43.02, 43.04, 43.10 — mean **43.06**, total range **0.08 tok/s**.

**The limitation, stated plainly:** the three repeats are **byte-identical** — same output hash, same rounds / draft / accepted counters. They are three re-runs of one deterministic trajectory, so they prove the measurement is stable (no thermal, scheduling or counter-order luck), not that three independent samples agree. Every number in this experiment comes from the same single 99,589-token prompt, so the correct claim is "n-max 7 is reproducibly fastest **for this prompt**". Ruling out prompt-specific luck would need more prompts or seeds, not more repeats of this one.

On prefill, arm means span only 505.19-508.32 tok/s (0.6%), which is *narrower* than one arm's own three repeats (n7's 4.81 range). Whichever arm "wins" prefill here is repeat order, not configuration.

## Split-mode matrix at n-max 7

Two repeats each. `sampler on GPU` is inferred by scanning each arm's log for the string `backend sampling not supported`: its absence means `llama_context::set_sampler()` took the install path (`src/llama-context.cpp:1227-1243`).

| arm | devices | split | ts | prefill tok/s | gen tok/s | AL | sampler on GPU | VRAM after load (MiB) |
|---|---|---|---|---|---|---|---|---|
| `mode-tensor2-nmax7` rep1 | CUDA0,1 | tensor | 1,1 | 507.92 | **43.10** | 5.000 | no | 9,611 / 9,603 |
| `mode-tensor2-nmax7` rep2 | CUDA0,1 | tensor | 1,1 | 506.12 | 43.06 | 5.000 | no | 9,611 / 9,603 |
| `mode-layer2-nmax7` rep1 | CUDA0,1 | layer | 1,1 | 489.83 | 26.26 | 4.909 | **yes** | 8,529 / 11,009 |
| `mode-layer2-nmax7` rep2 | CUDA0,1 | layer | 1,1 | 489.99 | 26.26 | 4.909 | **yes** | 8,529 / 11,009 |
| `mode-layer3-nmax7` rep1 | CUDA0,1,2 | layer | 1,1,1 | **599.19** | 24.99 | 4.909 | **yes** | 5,795 / 6,607 / 8,113 |
| `mode-layer3-nmax7` rep2 | CUDA0,1,2 | layer | 1,1,1 | 599.12 | 24.97 | 4.909 | **yes** | 5,795 / 6,607 / 8,113 |
| `mode-tensor3-nmax7` rep1 | CUDA0,1,2 | tensor | 1,1,1 | 302.38 | 24.14 | 3.333 | no | 6,819 / 6,667 / 6,749 |
| `mode-tensor3-nmax7` rep2 | CUDA0,1,2 | tensor | 1,1,1 | 302.09 | 24.17 | 3.333 | no | 6,819 / 6,667 / 6,749 |

- **Layer split restores GPU-side sampling and it is the only thing that does.** All four layer arms report `yes`, both tensor arms `no`. Repeat pairs agree exactly, so the flag is deterministic in this build.
- **GPU-side sampling buys nothing measurable.** Tensor split is 1.64x *faster* at decode (43.10 / 43.06 against 26.26) while keeping its sampler on the CPU. Acceptance is effectively identical (AL 5.000 vs 4.909), so the entire 64% gap is per-round compute time. The sampler-on-CPU warning tensor split prints is cosmetic in throughput terms — trading tensor for layer split to silence it costs 39% of decode speed.
- **Tensor split works on three cards — the odd-count concern is disproven.** `mode-tensor3` loaded cleanly, balanced across all three (6,819 / 6,667 / 6,749 MiB) with no error, no `cudaMalloc` fallback and no abort. It is simply slow: prefill −40%, decode −44% against two cards, and AL drops to 3.333. The third card's PCIe 2.0 x4 link gates the per-layer all-reduce that row split requires.
- **Layer split on three cards is the best prefill configuration measured at this depth** — 599 tok/s, +22% on layer-2 and +18% on tensor-2 — but it loses decode (24.98 against 26.26) and is 1.72x behind tensor-2. VRAM distributes 5,795 / 6,607 / 8,113 MiB, with the heaviest share on the slowest link.
- **Layer-2 is the most lopsided fit of the four**: 8,529 / 11,009 MiB, leaving GPU1 about 1.3 GB from its 12,288 ceiling, where tensor-2 balances to 8 MiB.

Prefill ranking at n-max 7: layer-3 599 > tensor-2 507 > layer-2 490 > tensor-3 302. Decode ranking: tensor-2 43.1 > layer-2 26.3 > layer-3 25.0 > tensor-3 24.2.

## Three-card matrix — does the `-ts` balance matter?

All arms MTP `n-max 7` unless stated, layer split.

| arm | split | `-ts` | prefill tok/s | gen tok/s | AL | VRAM after load G0/G1/G2 (MiB) |
|---|---|---|---|---|---|---|
| `g3-layer-ts111-mtp7` | layer | 1,1,1 | 602.76 | **24.96** | 5.20 | 5,795 / 6,607 / **8,113** |
| `g3-layer-ts353728-mtp7` | layer | 35,37,28 | **611.29** | 24.93 | 5.20 | 6,397 / 7,021 / 7,095 |
| `g3-layer-ts13-13-04-mtp7` | layer | 1.3,1.3,0.4 | 514.31 | 24.78 | 5.20 | 7,585 / 8,349 / 4,577 |
| `g3-layer-ts111-dflash4` | layer | 1,1,1 | 606.56 | 23.06 | 3.31 | 5,941 / 6,761 / 7,261 |
| `g3-layer-ts111-dflash8` | layer | 1,1,1 | 598.12 | 19.47 | 3.63 | 6,153 / 6,961 / 7,449 |
| `g2-layer-ts11-dflash4` | layer (2 cards) | 1,1 | 494.55 | 23.56 | 3.31 | 8,695 / 10,179 / 4 |
| `g3-tensor-ts111-dflash4` | tensor | 1,1,1 | — | — | — | **aborted at load** |

- **No `-ts` balance wins on decode.** 24.96 / 24.93 / 24.78 tok/s is a 0.18 tok/s (0.7%) spread, and all three are byte-identical in output (`0194852ba7ad2825`) with identical counters. The balance only moves **prefill**: the skewed `1.3,1.3,0.4` costs 88 tok/s of prefill against `1,1,1` (−14.7%) and buys nothing. On prefill alone `35,37,28` leads by 1.4%, inside this depth's jitter, so treat the top two as a tie.
- **DFlash2 loses to MTP at the same split: MTP +7.3%.** DFlash2 n-max 4 gives 23.06 against MTP n-max 7's 24.96; DFlash2's best n-max in the sweep below (7, at 23.27) still trails by 7.3%. Prefill is a wash. DFlash2's acceptance is the reason: AL 3.31 / accept 0.578 against MTP's 5.20 / 0.604 — MTP proposes almost as many tokens per round (6.75 against 3.95) *and* lands a higher share of them.
- **The third card does not help the drafter.** DFlash2 n-max 4 on **two** cards in layer split is faster at decode than the same arm on three — 23.56 against 23.06 (+2.2%), identical acceptance and output hash — and the third card buys prefill (494.55 → 606.56, +23%). Total VRAM is lower on two cards (18,878 against 19,963 MiB across the cards in use).
- **DFlash2 n-max 8 never ran an 8-token window.** Its log prints `requested draft size (n_max=8, n_min=0) exceeds the trained block size 8 -- clamping to 7`. n-max 8 is n-max 7 wearing a wider output window, and it costs 16% of decode.

## DFlash2 n-max 1-8 on three cards (layer, `-ts 1,1,1`)

| n-max | prefill tok/s | gen tok/s | AL (in-run) | accept (in-run) | accepted / generated |
|---|---|---|---|---|---|
| 1 | **624.06** | 16.10 | 1.88 | 0.881 | 119 / 135 |
| 2 | 618.39 | 18.45 | 2.32 | 0.662 | 145 / 219 |
| 3 | 614.58 | 19.40 | 2.63 | 0.547 | 158 / 289 |
| 4 | 606.19 | 23.05 | 3.31 | 0.578 | 178 / 308 |
| 5 | 603.32 | 22.11 | 3.45 | 0.495 | 181 / 366 |
| 6 | 602.74 | 22.97 | 3.86 | 0.482 | 189 / 392 |
| 7 | 600.29 | **23.27** | **4.32** | 0.477 | 196 / 411 |
| 8 | 597.76 | 19.48 | 3.63 | 0.376 | 184 / 490 |

- **The peak is n-max 7 at 23.27 tok/s — but it is a shelf, not a spike like MTP's.** n-max 4, 6 and 7 sit within 1.3% of each other (23.05 / 22.97 / 23.27) — one number, not three, against the noise band. The honest reading is a flat n-max 4-7 shelf at roughly 22-23 tok/s. **The shape against MTP is the finding:** MTP climbs 29% from n-max 4 to its n-max 7 peak, while DFlash2 gains nothing beyond n-max 4.
- **Acceptance keeps climbing while throughput does not.** AL rises monotonically 1.88 → 4.32 as the accept rate falls 0.881 → 0.477. Each extra drafted token is worth less than it costs.
- **Prefill falls monotonically with n-max** — 624.06 → 597.76 (−4.2%) across the eight arms, a more orderly drift than MTP showed (whose prefill was flat). Likely cause: the growing output window (`n_outputs_max` scales with `n_max + 1` for DFlash) means bigger buffers per prefill batch. Flagged as an observation, not a measured mechanism.
- **Nothing here is close to the recommendation.** The best DFlash2 number measured anywhere is 23.56 tok/s; the recommended two-card tensor MTP config is **43.06 tok/s** — **1.83x** DFlash2's best.

## What killed the two failing configurations

**Tensor split + DFlash2 (three cards)** aborted during load, before serving:

```
ggml/src/ggml-backend-meta.cpp:543: GGML_ASSERT(src_ss[0].axis != GGML_BACKEND_SPLIT_AXIS_0) failed
  ggml_backend_sched_alloc_graph -> llama_context::process_ubatch -> llama_context::decode
  -> llama_decode -> common_context_can_seq_rm -> server_context_impl::load_model
```

The abort is in the meta backend's `handle_per_row` handler, which asserts the op's source is *not* split on axis 0. A meta wrapper over an axis-0 split exists because `--split-mode tensor` splits the model row-wise. The draft model **inherits** the target's device list and split mode when `--spec-draft-device` is not given, and `common/speculative.cpp:2480-2483` says so explicitly: *"a draft pinned to a single device doesn't need the meta wrapper an inherited `-sm tensor` would give it"*. It died at load, not under generation.

**`--spec-draft-device` (all three pinning arms)** died with a different error, also at load:

```
ggml/src/ggml-backend.cpp:941: pre-allocated tensor (output.weight)
  in a buffer (CUDA2) that cannot run the operation (NONE)
  ggml_backend_sched_split_graph -> llama_context::graph_reserve -> sched_reserve
  -> llama_init_from_model -> common_speculative_init_result -> server_context_impl::load_model
```

The flag is real and was parsed (`--spec-draft-device, -devd, --device-draft` is listed by `--help` in this build, and the arms carried `devd=CUDA0`/`CUDA1` in their records). The abort happens while the **draft** context is being built. The pin did not move `output.weight`: all three arms name a **CUDA2** buffer even though they asked for CUDA0 or CUDA1. CUDA2 is the card the *target's* output layer occupies under a 3-way layer split (`src/llama-model.cpp:1546`), so the placement of that tensor followed the split's last share, leaving a tensor in a buffer the draft's single-device scheduler will not run. **Pinning is not "slower here" — it does not start.**

## Where the drafter actually lands, and why pinning had little to win

| interval | d GPU0 | d GPU1 | d GPU2 |
|---|---|---|---|
| every +1 n-max (7 intervals) | 52-54 MiB | 50 MiB exactly, every interval | 46-48 MiB |
| n1 → n8 total | +372 | +350 | +328 |

**Every card grows by roughly 50 MiB for each extra drafted token.** That is the signature of the draft model *and its context* being spread across all three cards, which is what "draft device inherited" means. There is no single card to bias `-ts` away from. Stated as inference from the VRAM deltas, not from a printed device-assignment line.

The same numbers bound the prize: the entire draft model plus a 131,072-token draft context, across n-max 1→8, moves the cards by 372 / 350 / 328 MiB — a few hundred MiB per card, against 12,288. VRAM was never the binding constraint in the DFlash2 configuration, so moving the drafter between cards has very little room to help even when it works.

## Open question worth one arm

**Does DFlash2 work under tensor split at all?** It aborted on three cards for a reason (the axis-0 meta wrapper) that is not three-card-specific. If it aborts on two cards too, DFlash2 is unusable in the recommended split mode and the whole drafter line is closed. If it loads, that is the only configuration in which DFlash2 was ever given the split mode that produces 43 tok/s with MTP. Cost: one or two arms, about 12 minutes. **Not run.**

## A caveat on the `backend_sampling_on_gpu` field

All 18 rows in the three-card sweeps report `backend_sampling_on_gpu: true`. That is correct for the 14 arms that ran (all layer-split), but it is a **false positive for the 4 arms that aborted at load**: a server that dies before the sampler is installed never prints the warning, and the absence-of-a-string heuristic cannot tell "sampling worked" from "the process aborted". Those 4 rows must not be read as evidence about sampling.

## Data

| file | contents |
|---|---|
| `data/raw/100k-arm-results.jsonl` | 20 arms, stages A+B, raw per-arm records |
| `data/raw/100k-nmax-confirm.jsonl` | 12 arms, three repeats per n-max |
| `data/raw/100k-split-mode-matrix.jsonl` | 8 arms |
| `data/raw/three-card-matrix.jsonl` | 7 arms |
| `data/raw/three-card-dflash2.jsonl` | 11 arms |
| `data/raw/100k-arm-summary.json` | parsed summary of the 20 stage A/B arms |
| `data/csv/100k-and-three-card-arms-normalised.csv` | all 58 arms, one tidy schema |
| `data/csv/100k-stageA-nmax.csv`, `100k-stageB-topk-minp.csv`, `100k-confirm-nmax5-8-3-repeats.csv`, `100k-split-mode-matrix.csv`, `three-card-matrix.csv`, `three-card-dflash2-nmax.csv` | per-experiment tables |

**Counter source.** `acceptance_length`, `proposed_per_round` and `token_accept_rate` in the raw JSONL come from llama.cpp's **cumulative** `/metrics` counters, which include the discarded warm-up request, so they read slightly low — `mtp7-untrimmed` reads 5.000 / 0.5918 there against 5.31 / 0.618 in-run. The tables above use the in-run values from each arm's `draft acceptance = ... mean len = ...` log line, which cover the measured request only. Both are arithmetically self-consistent; they divide by different denominators. `gen_tok_s` and `prefill_tok_s` come from the response timings and are unaffected.
