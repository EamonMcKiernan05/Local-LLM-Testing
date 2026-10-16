# 01 — AJ-IQ2_XXS bring-up and the 256K bench (2026-10-16)

**Goal.** Stage aj9o9's AJ-IQ2_XXS mix of GLM-5.3-Flash on the SN730 and measure it in Project
Maya v1.1.13 at the full **262,144 context**: a postcopy burn (discarded) plus three fresh-load
batteries over the six standard depths, means shown.

**The file.** GLM-5.3-Flash (321B MoE, ~18B active) hand-mixed by aj9o9 to IQ2_XXS — 2.23 bpw,
87.35 GB across two shards. It carries **no MTP/NextN block** (the uploader pruned it). Checked
four ways before the numbers were trusted:

1. The GGUF header (shard 1): `glm5next.nextn_predict_layers = 0`, `glm5next.block_count = 45`.
2. The tensor lists (both shards, probed 2026-10-16): zero tensors matching `nextn.*`, `eh_proj`
   or `blk.45.*`; the highest layer present is `blk.44.*` (45 layers, 0-indexed).
3. The engine's own loader takes the file cleanly and runs no draft stage (the split planner
   omits it).
4. At runtime: 0 `glm mtp` markers in the engine log across the whole bench, and `draft_n: 0` on
   every measured arm.

So no speculative drafting was possible — the numbers below are **raw single-pass decode**.

## Sequence (all times UTC)

| time | what |
|---|---|
| 12:28–12:30 | engine update v1.1.11 → v1.1.13 (`797819e`, stamp `c823b8ca185405dd`), rebuilt before the bench; the served config byte-identical after |
| ~12:12–13:16 | download from HF (`aj9o9/GLM-5.3-Flash-GGUF`) to the HDD catalogue dir on .5 |
| 13:28–13:42 | staging: HDD → SN730 copy (`~/maya-nvme/glm-5.3-flash-aj-iq2_xxs`), sha256 both shards vs HF, vision files pre-placed, standard path flipped to a symlink |
| 13:44 | pack build (`maya.sh --setup --yes --no-start --context 262144 --gpus 0,1`); config + run script written |
| ~13:46 | first start / load check — `ready … context 262144 tokens, images on` |
| 13:49–15:12 | the bench cycle: burn → r1 → r2 → r3, one engine load per battery; Maya-S restored serving at the end |

## Protocol

- One engine load per battery; on every arm the start gates assert `n_ctx == 262144`, the engine
  stamp `c823b8ca185405dd`, and an unchanged config (md5 `7e73a42dc4f2e75ac45dab17fb09a300`).
- A warm-up request (discarded) precedes the battery; each measured arm is one HTTP call through
  the `model-bench` harness: depths 20K / 60K / 100K / 150K / 200K / 250K, 400 generated tokens
  per arm, temp 0.5, seed 12345, unique per-request tag so the prefix cache cannot flatter a run.
  The engine's own `timings` are the source; wall times include the full prompt.
- The postcopy burn absorbed the first-session-after-copy page-cache effect and is excluded from
  the means by design. It read **0.2–1.2 % under** the measured batteries (below).

## Results — 262,144 ctx, three fresh-load runs per depth, mean (sd)

| depth | prefill tok/s | sd | decode tok/s | sd |
|---|---:|---:|---:|---:|
| 20K | 651.7 | 3.55 | 23.27 | 0.55 |
| 60K | 705.2 | 1.12 | 24.77 | 0.31 |
| 100K | 758.6 | 1.83 | 24.47 | 0.61 |
| 150K | 791.2 | 1.90 | 23.53 | 0.25 |
| 200K | 800.8 | 3.73 | 23.27 | 0.06 |
| 250K | 791.6 | 1.80 | 22.43 | 0.31 |

Burn battery (excluded; single run per depth): 649.0 / 696.9 / 756.8 / 786.7 / 794.6 / 788.9
tok/s prefill and 22.7 / 24.0 / 24.1 / 23.4 / 22.7 / 21.8 decode at the same depths.

Each battery is roughly 19 min of harness time (the 250K arm alone ≈ 5.6 min) plus a ~60–90 s
load and the discarded warm-up.

## Comparability checks

Same corpus document per depth in every run (frankenstein / sherlock / pride / tale2cities /
greatexp / mobydick, sliced exact-token with the pack tokenizer); `sliced_tokens` identical at
every depth; `ptok` (the actual prompt token count including instruction and unique tag) jitters
±1. The data builder (`scripts/build_data_aj.py`) asserts all of this across all seven batteries
before it writes a single CSV.

## Cross-check (observation, not a controlled pair)

Maya-S **with** MTP drafting, same SN730 storage, 2026-10-15 (64K config): 594–647 tok/s prefill /
20.1–23.1 decode at 20K–60K. This file **without** drafting at the same depths (256K config):
652–705 / 23.3–24.8. Different days, configs and depths — worth a controlled no-draft-vs-draft
pair if the headroom question matters.

## Artifacts

- Raw battery records: `data/raw/model-bench-aj-256k-sn730-{postcopy-burn,r1,r2,r3}-*`
- Serving config: `data/raw/config-256k-served.json`; drivers: `driver-aj-prep*.sh`,
  `driver-aj-setup.sh`, `driver-aj-256k-cycle.sh` with their logs
- Engine stat extracts per battery: `data/raw/engine-stats-256k-*.txt`
- The card: `charts/aj-iq2xxs-256k-mean.png` (`scripts/make_chart_256k.py`)
