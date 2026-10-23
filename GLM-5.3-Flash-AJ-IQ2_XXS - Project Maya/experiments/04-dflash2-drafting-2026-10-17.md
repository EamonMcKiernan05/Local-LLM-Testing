# 04 — DFlash2 drafting on AJ-IQ2_XXS under Maya v1.1.15 (2026-10-17)

**Question.** This quant ships without an MTP block, so every number in this dataset is raw
single-pass decode. Maya v1.1.15 can draft with a DFlash2 drafter instead. Does drafting help
here, and by how much?

**Answer.** No — **DFlash2 is slower than no drafting at all at every depth**. It gives up 29 % of decode throughput on the means;
prefill moves −1.6 %. Full numbers below.

## The drafter

`GLM-5.3-Flash-DFlash2-Q4_K_M.gguf` (697 MB) from the Maya setup's own download, kept at
`/mnt/models/Maya-data/models/GLM-5.3-Flash-DFlash2/` on box .5. The engine loads **717 MB on
CUDA1**, which comes off that card's expert pool (the log's `glm fast: CUDA1 ... expert pool`
line shrinks accordingly). Not copied to the SN730 — the file is read once at load, not per token.

## A trap worth recording: the start-time calibration rewrites the config

Adding `--dflash` to a config whose `installer` block has no `speed_calibration` makes the *start*
run `needs_speed_calibration()` → `speed_calibration()`: it loads the model **twice** (no drafting,
then DFlash2), writes 1,536 tokens on each, and then **rewrites the config** — keeping DFlash2 only
if it wins by `CD.MIN_GAIN`, otherwise stripping `--dflash`. On this box it measured **DFlash2 19.57
against 23.58 tok/s without drafting (8K document)** and removed the flag. That two-load calibration
is also why the first `--dflash` start took 11 minutes instead of 1.

For this experiment the flag was therefore re-applied to the *calibrated* config (which now carries
`installer.speed_calibration`, so the start no longer re-measures) and the three measured arms ran
with `--dflash` present. Config md5 `5324f4280dd57f302ee1f637cd9a053e`, gated on every start.

## Method

- Three fresh-load batteries with `--dflash`, same 262,144-token config otherwise, same six depths
  (20K / 60K / 100K / 150K / 200K / 250K), 400 generated tokens each; the comparison side is the
  three v1.1.15 no-drafting batteries from experiment 03 (same day, same quant, same prompts).
- Gates per arm: engine stamp `707211430e5c3035`; `n_ctx` 262144 read back; `glm dflash:` markers
  present (drafter loaded, `MTP off - the NextN draft block is not loaded, DFlash drafts instead`);
  config md5 unchanged after start; port-in-use and "compiled before" markers absent.
- Comparability: the builder asserts the same `book` and `sliced_tokens` at every depth across all
  six batteries, that the DFlash2 arms offered drafts (`draft_n > 0`) and the plain arms offered
  none.

## Results (mean of three fresh-load runs per depth)

| depth | decode no drafting | decode DFlash2 | Δ | prefill no drafting | prefill DFlash2 | Δ |
|---|---:|---:|---:|---:|---:|---:|
| 20K | 23.97 | 16.77 | -30.0 % | 713.8 | 708.0 | -0.8 % |
| 60K | 24.87 | 18.03 | -27.5 % | 764.7 | 758.2 | -0.8 % |
| 100K | 24.50 | 16.97 | -30.8 % | 828.4 | 815.4 | -1.6 % |
| 150K | 23.60 | 16.80 | -28.8 % | 861.0 | 839.0 | -2.5 % |
| 200K | 23.17 | 16.97 | -26.8 % | 869.6 | 845.6 | -2.8 % |
| 250K | 22.53 | 15.87 | -29.6 % | 850.8 | 841.6 | -1.1 % |
| **mean** | **23.77** | **16.90** | **-28.9 %** | **814.7** | **801.3** | **-1.6 %** |

Drafts were offered on every measured arm (mean 259 per request at 20K, acceptance 65.2 %); the drafting pipeline was running, it just costs more than it returns.

## Why it is slower here (mechanism, from the engine log and release notes)

On a two-GPU split DFlash2 runs the **batched** verify window (the pipelined one needs three or
more GPUs): the drafter's window layer runs on both parts' CPU pools, and each round pays that
layer plus the window's verify passes before any token is committed. The engine log names it:
`glm dflash: a batched window's layer on both parts' CPU pools (CUDA0 + CUDA1)` and
`5 layers ... 717 MB on CUDA1`. Against 23–25 tok/s plain decode, the drafting overhead exceeds
what the accepted drafts return. This matches the 2026-10-12 result on Maya-S, where DFlash2 cost
43–46 % against MTP drafting on the same cards; here the baseline has no drafting at all and the
cost is 29 % (mean).

## Counts

**18 measured arms** (3 batteries × 6 depths). 0 failed; 3 warm-up requests discarded; no measured
arm excluded. The start-time calibration's two sides are diagnostics, not part of this table.
