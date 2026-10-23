# Provenance: where every file here came from

Collected 2026-10-16. The rule for this folder: **a number appears here only if it came off a real
run, and every table says which run.** All measurements are on aj9o9's AJ-IQ2_XXS mix
(GLM-5.3-Flash) served by Project Maya on box .5.

## Sources, in order of reliability

1. **The model-bench run records** — written by the harness on box .5 as each arm finishes, and
   moved here as flattened copies (`<stem>-results.jsonl` / `-meta.json` / `-summary.csv`); every
   file is a byte-identical copy, sha256-checked against the box at collection time (the manifest
   is `raw/SHA256SUMS`):

   | stem | box run id | what |
   |---|---|---|
   | `model-bench-aj-256k-sn730-postcopy-burn` | `2026-10-16T1350Z-aj-iq2xxs-256k-sn730-postcopy-burn` | post-copy calibration battery, discarded by design |
   | `model-bench-aj-256k-sn730-r1..r3` | `2026-10-16T1411Z / T1432Z / T1453Z-aj-iq2xxs-256k-sn730-r1..r3` | the 256K measured batteries, three fresh loads |
   | `model-bench-aj-131k-sn730-r1..r3` | `2026-10-16T1516Z / T1524Z / T1531Z-aj-iq2xxs-131k-sn730-r1..r3` | the 131K measured batteries, three fresh loads |
   | `model-bench-aj-v1115-v1113-r1..r3` | `2026-10-17T0847Z / T0929Z / T1010Z-aj-iq2xxs-256k-v1113-r1..r3` | the v1.1.13 side of the engine pair, three fresh loads |
   | `model-bench-aj-v1115-v1115-r1..r3` | `2026-10-17T0910Z / T0950Z / T1032Z-aj-iq2xxs-256k-v1115-r1..r3` | the v1.1.15 side of the engine pair, three fresh loads |
   | `model-bench-aj-v1115-dflash-r1..r3` | `2026-10-17T1104Z / T1124Z / T1145Z-aj-iq2xxs-256k-v1115-dflash-r1..r3` | DFlash2 drafting batteries, three fresh loads |

   Each record carries one discarded warm-up row (`"kind": "warmup"`) and its measured arms — six
   at 256K, three at 131K. Each battery is one engine load, driven by the two cycle scripts below.
   The 2026-10-17 files are listed in their own manifest, `raw/SHA256SUMS-v1115` (the 2026-10-16
   set keeps the original `raw/SHA256SUMS`).

2. **The serving configs, the drivers and the logs** — `config-256k-served.json` and
   `config-131k-served.json` are the configs the two cycles ran on (on the box:
   `~/project-maya/maya-aj-iq2_xxs.json`, the two differing only in `--max-context`; the 256K
   config's md5 in the gates was `7e73a42dc4f2e75ac45dab17fb09a300`, the 131K one
   `4d65f6be873d543244a497d3ba104940`).
   The 2026-10-17 pair and DFlash2 test ran on `config-aj-v1115-pair-served.json` (byte-identical
   for both engine sides, md5 `7e73a42dc4f2e75ac45dab17fb09a300`), `config-aj-v1115-dflash.json`
   (`--dflash` added on top of the calibrated config, md5 `5324f4280dd57f302ee1f637cd9a053e`) and
   `config-aj-v1115-plain-calibrated.json` (the state after Maya's one-time draft calibration —
   `installer.speed_calibration`, `kept: mtp`; md5 `d98e1d5599f1f3ddd69f4297787de03a`). Their
   drivers are `driver-aj-v1115-cycle.sh` and `driver-aj-v1115-dflash-cycle.sh`, logs
   `aj-v1115-cycle.log` and `aj-v1115-dflash-cycle.log`, plus
   `dflash-calibration-2026-10-17.log` (the calibration's own two-load transcript).
   Drivers: `driver-aj-prep.sh` / `driver-aj-prep-resume.sh` (HDD → SN730 copy, sha256 vs HF,
   symlink flip, vision pre-place), `driver-aj-setup.sh` (the pack build + config write, run as
   `maya.sh --setup --yes --no-start --gguf-dir … --gpus 0,1 --context 262144`), and
   `driver-aj-256k-cycle.sh` / `driver-aj-131k-cycle.sh` (the bench cycles — start gates, warm-up,
   bench, stop, stat extract, restore). Their logs: `aj-prep.log`, `aj-prep-resume.log`,
   `aj-setup.log`, `aj-256k-cycle.log`, `aj-131k-cycle.log`, plus `aj-firststart.log` (the first
   load, before the cycle) and `update-v1113.log` (the engine update the same morning).
   Note: the first `aj-prep.log` ended in its own `du` check refusing on a path-name mismatch; the
   resume script renamed and completed the staging — both scripts and both logs are here so the
   whole sequence is auditable.
3. **Engine identity**: v1.1.13 = commit `797819e` (the update's `git describe`), engine build
   stamp `c823b8ca185405dd`; **v1.1.15 build stamp `707211430e5c3035`** (first built 2026-10-17
   09:09Z, plain-path rebuild over v1.1.13; `third_party/llama.cpp` unchanged, vision source
   changed but deliberately not rebuilt — text-only bench, encoder stays at `3a8570cc5f1f1686`).
   Both stamps were asserted before **every arm of every battery** by the cycle scripts
   (`engine src stamp:` lines). The update replaced v1.1.11 (`8931339`, stamp `5a23fa1ec92e67aa`)
   the same morning; the config the update was started on is byte-identical after (the update log
   shows the `md5sum -c` pass).
4. **Model identity**: HF repo `aj9o9/GLM-5.3-Flash-GGUF`, quant `AJ-IQ2_XXS`, two shards —
   shard 1 `1fa0535ecddaee4ff127eb8ffd47d3855ca7efa1cc29c996c24da699c5fbe3f7`
   (44,665,098,240 B), shard 2 `ab8abbde061254a7f6b1a16b3627c4b77e3084f52e3d9739ebaa515b9365945c`
   (42,680,908,320 B). Both sha256-verified **on the SN730 copy** against the HF metadata (the
   prep logs hold both checks); the HDD master stayed as
   `/mnt/models/GLM-5.3-Flash-AJ-IQ2_XXS-GGUF.hdd-original` with the standard path flipped to a
   symlink. Vision files were pre-placed from the Maya-S copy and sha256-checked against their
   published hashes (`3627575d…` mmproj, `8f53cb1b…` vocab) — same files in every GLM-5.3-Flash
   quant on this box. The quant carries **no MTP block** (no NextN tensors; 0 `glm mtp` markers
   across the whole bench; `draft_n: 0` on every measured arm) — that is the build that was
   tested, not an inference about it.

## Counting the runs

**33 recorded runs, every one with measurements; no failures:**

- 256K cycle: 4 batteries × 6 depths = **24 arms** (20K / 60K / 100K / 150K / 200K / 250K).
- 131K cycle: 3 batteries × 3 depths = **9 arms** (20K / 60K / 100K).
- Engine pair (2026-10-17): 6 batteries × 6 depths = **36 arms** (v1.1.13 ×3 and v1.1.15 ×3,
  alternated), plus 6 warm-ups discarded.
- DFlash2 test (2026-10-17): 3 batteries × 6 depths = **18 arms**, plus 3 warm-ups discarded.
- The 2026-10-16 post-copy burn battery's 6 arms are excluded from the means by design (they
  read 0.2–1.2 % under the measured batteries); they stay visible in the raw records and in
  `depth-aj-runs.csv` (`side` = "256K ctx (burn, excluded)").
- The 7 warm-up requests (one per battery) were discarded by design — they stay visible in the
  raw files (`"kind": "warmup"`) and are not counted.

## Derived values (the only numbers not read straight off a run)

| file | column | formula |
|---|---|---|
| `depth-aj-256k.csv`, `depth-aj-131k.csv`, `ctx-aj-256k-vs-131k.csv` | all columns | mean of the three per-run measured values per depth; prefill rounded to 2 dp and decode to 3 dp — the working precision the cards were drawn from (they display prefill whole and decode to 1 dp); `ptok` is the smallest per-run prompt token count at that depth |
| `ctx-deltas-aj-256k-vs-131k.csv` | `*_delta_pct_derived` | 100 × (131K value / 256K value − 1) on the **unrounded** means; the `mean` row averages the three unrounded deltas, then rounds |
| `version-aj-v1113-v1115.csv`, `version-deltas-aj-v1113-v1115.csv` | all columns | 3-run means per engine per depth (2 dp prefill / 3 dp decode), deltas on the unrounded means; `scripts/build_data_v1115.py` |
| `dflash-aj-v1115.csv`, `dflash-deltas-aj-v1115.csv` | all columns | the same shape for the DFlash2 test against the v1.1.15 no-drafting side; `scripts/build_data_dflash.py` asserts `draft_n > 0` on the drafter arms and `draft_n = 0` on the plain ones |

The charts read their values from `data/csv/` at draw time — nothing is retyped into a chart
script. The data builder asserts the same book and `sliced_tokens` per depth across all seven
batteries and both contexts before writing anything, so the same-prompt proof ships with the data.

## What is not here, and why

- **The full engine log stays on the box** (`~/project-maya/maya-aj-iq2_xxs.log`). What is here:
  per-battery `glm stat:` extracts (`engine-stats-*.txt`) — `grep 'glm stat:' | tail -20` taken at
  each battery's end; they overlap across arms because the engine log is shared, and are a
  starting point, not a substitute for the log.
- **The start-arm logs stay on the box** (one per battery, ~18 KB each; the milestones are
  inlined in the cycle logs here).
- **The HF download logs stay on the box** (`~/hf-dl-aj-iq2xxs/`).
- **The model files themselves** (87.35 GB) are not in git — the sha256s above are the identity.
- **The X draft associated with these runs** is not part of this dataset; it lives in the account
  pipeline.
