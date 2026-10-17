# 03 — Project Maya v1.1.13 → v1.1.15: a controlled three-run pair on AJ-IQ2_XXS (2026-10-17)

**Question.** Project Maya released v1.1.14 and v1.1.15 the evening of 2026-10-16, hours after the
AJ bench was recorded on v1.1.13. Does either change the speed of this quant on two V100s?

**Answer.** v1.1.15's V100 prompt-attention rework delivers **+9.0 % prefill mean across the six
depths** (+7.6 … +10.3 %, every depth positive). **Decode is unchanged within the box's session
drift.** v1.1.14 contributes nothing measurable here — it is Pascal support and unsloth Q6_K_XL /
Q8_0 pack fixes, and its own release note says GPUs of compute capability 7.0 and newer give
v1.1.13's tokens.

## Release triage (before the box time)

| release item | applies here? |
|---|---|
| v1.1.14 — Pascal (P40/P100/GTX 10) experimental support | no — sm_70 already supported; release: "CC 7.0 and newer give v1.1.13's tokens" |
| v1.1.14 — unsloth Q6_K_XL / Q8_0 GGUFs load | no — this dataset is aj9o9's IQ2_XXS mix |
| v1.1.15 — **two-pass 32-head prompt attention on V100 / RTX 20 (#196)** | **yes — the change under test**; upstream: a 27K prompt's attention 22.5 → 11.8 s on one V100 |
| v1.1.15 — EXL3 + DFlash2 pipelined verify on many GPUs (#225) | no — EXL3 packs and the DFlash2 drafter, not this GGUF |
| v1.1.15 — AVX-512 VBMI CPU-lane rows (#227) | no — this box's CPU is a Xeon E5-2680 v4 (Broadwell, no AVX-512) |
| v1.1.15 — EXL3 on AMD, DFlash2 OOM fix, miss-skip opt-in | no — AMD / not used / off by default and answer-changing |

So the expectation was written down before measuring: **prefill up at long prompts, decode parity.**

## Method

- **Three fresh-load batteries per side, alternated** O N O N O N (v1.1.13, v1.1.15, …), one engine
  load per battery, a discarded warm-up request, mean of the three measured values per depth.
  Alternation cancels the first-position edge a single-ordered pair carries.
- Same quant file, same 262,144-token config on both sides. The config was md5-gated on every
  start and stayed byte-identical (`7e73a42dc4f2e75ac45dab17fb09a300`) — v1.1.14/15 do not migrate
  this config, so **only the engine differs**.
- Engine stamps asserted before every arm: v1.1.13 = `c823b8ca185405dd` (unchanged since
  2026-10-16), v1.1.15 = `707211430e5c3035` (first built 2026-10-17 09:09Z). `n_ctx` read back as
  262144 on every arm; port-in-use and "compiled before" soft-failure markers absent; `glm mtp = 0`
  on every battery (this quant has no draft block).
- Same prompts, provably: the builder asserts `book` and `sliced_tokens` equal at every depth
  across all six batteries. `ptok` jitters ±1 from the per-request tag.

## Results (mean of three fresh-load runs per depth)

| depth | prefill v1.1.13 | prefill v1.1.15 | Δ | decode v1.1.13 | decode v1.1.15 | Δ |
|---|---:|---:|---:|---:|---:|---:|
| 20K | 650.6 | 713.8 | **+9.7 %** | 23.60 | 23.97 | +1.6 % |
| 60K | 704.3 | 764.7 | **+8.6 %** | 23.03 | 24.87 | +8.0 % |
| 100K | 751.2 | 828.4 | **+10.3 %** | 22.97 | 24.50 | +6.7 % |
| 150K | 791.0 | 861.0 | **+8.8 %** | 23.50 | 23.60 | +0.4 % |
| 200K | 799.6 | 869.6 | **+8.8 %** | 23.43 | 23.17 | −1.1 % |
| 250K | 791.0 | 850.8 | **+7.6 %** | 22.30 | 22.53 | +1.0 % |
| **mean** | **747.9** | **814.7** | **+9.0 %** | **23.14** | **23.77** | **+2.8 %** |

Per-depth spreads (sd, three runs): prefill ≤ 12.2 tok/s (one v1.1.15 cellular outlier at 60K; every
other cell ≤ 9.4), decode ≤ 2.54 tok/s. Full table incl. sds: `data/csv/version-deltas-aj-v1113-v1115.csv`.

## Reading it

- **The prefill gain is a version effect, not a day effect.** v1.1.13 re-measured today reproduces
  its 2026-10-16 archive within 1 % at all six depths (650.6/704.3/751.2/791.0/799.6/791.0 against
  651.7/705.2/758.6/791.2/800.8/791.6), and v1.1.15 is +7.6…+10.3 % on top of that, every depth.
  The gain is flat across depth (7.6 % at 250K against 9.7 % at 20K) rather than growing with
  prompt length, so the measured effect here is a roughly constant per-chunk speedup, not something
  that compounds at long context. No mechanism is claimed beyond the release note's own: V100 prompt
  attention now runs in two passes with 32 heads a block.
- **Decode is not claimed.** The +2.8 % mean is inside this box's session drift: one v1.1.13
  session (r3) read 20.1/20.8 tok/s at 60K/100K while its other four cells matched the other
  sessions, and the other two v1.1.13 sessions read 24.4–24.6 at those depths. The prefill and
  decode panels of the comparison chart are drawn from the means as measured; the footer says
  the same thing this paragraph does.
- **Absolute position:** v1.1.15 is the fastest this quant has read on this box — 714 → 870 tok/s
  prefill across 20K–200K, 22.5–24.9 tok/s decode.

## Gates and receipts

- Cycle driver: `data/raw/driver-aj-v1115-cycle.sh`; log `aj-v1115-cycle.log` (on the box:
  `~/maya-aj-v1115-cycle.log`, run 08:45–10:52Z).
- Run dirs (box): `~/model-bench/runs/2026-10-17T{0847Z,0910Z,0929Z,0950Z,1010Z,1032Z}-aj-iq2xxs-256k-v111{3,5}-r{1,2,3}`;
  flattened copies in `data/raw/`.
- Engine `glm stat:` extracts per arm: `data/raw/engine-stats-v111{3,5}-r{1,2,3}.txt`.
- Config the pair ran: `data/raw/config-aj-v1115-pair-served.json` (identical for both sides).
- Box state: Nemotron llama-server was stopped for the cycle and restored after it; the AJ model
  set stayed on the SN730 the whole time (no copy, no burn battery needed — the staging was
  already warm from 2026-10-16).

## Counts

**36 measured arms** in this experiment (6 batteries × 6 depths). 0 failed; 6 warm-up requests
discarded by design; no measured arm excluded. (The dataset README's totals roll these in.)
