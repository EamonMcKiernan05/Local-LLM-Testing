# 04 — v1.0.34: prefill +97.5 %, decode +46.4 % on a same-day pair (2026-10-11)

v1.0.34 (commit `e728e52`) landed at 14:13 UTC, ~40 minutes after the v1.0.33 pair was
measured; by Eamon's call that pair was set aside unpublished (kept as experiment 03) and this
pair re-run fresh against v1.0.9 the same afternoon. The jump is mostly a Windows RAM-tier
pinning fix and CUDA 12.0–12.2 builds, plus two opt-in settings (all off by default; upstream's
checks say identical tokens to v1.0.33 with defaults). The model was moved onto the NVMe that
morning, and this pair ran on it.

Measured the house way: **a controlled same-day pair**. v1.0.9 (`7655730`) was rebuilt from its
commit and re-run the same afternoon, on the same config as served (64K context, RAM headroom
3), same three documents, one run per depth — then the same run on v1.0.34. Only the engine
differs.

## Results

| depth | decode v1.0.9 | decode v1.0.34 | Δ | prefill v1.0.9 | prefill v1.0.34 | Δ |
|---|---|---|---|---|---|---|
| 20K | 10.5 | 16.8 | +60.0 % | 221.7 | 471.7 | **+112.8 %** |
| 40K | 14.3 | 20.3 | +42.0 % | 259.5 | 525.6 | **+102.5 %** |
| 60K | 14.2 | 19.5 | +37.3 % | 268.8 | 476.1 | **+77.1 %** |
| mean | | | +46.4 % | | | **+97.5 %** |

Reading: prefill goes ×2.13 / ×2.03 / ×1.77 — above a clean doubling at the shallow depths,
and +97.5 % on the mean. Decode is up across all three cells; the mean is the claim (one run per
cell).

## The agreement check

The fresh re-run of v1.0.9 landed on its 2026-10-08 archive on prefill: −2.1 / −1.7 / −0.7 %
(mean −1.5 %). Its decode sat under its archive (−22.2 / −5.3 / −1.4 %, mean −9.6 %) — cells
inside the wander band, but it means part of the pair's decode gain may be day drift; the
prefill claim is unaffected. Table: `data/csv/release-deltas-64k-v109-rerun2-vs-archived.csv`.

## Update and pair procedure (as run)

1. Stop the server, verify VRAM drops.
2. Update: `git fetch origin --tags --force` → fast-forward to `e728e52` → `./setup.sh --setup
   --no-start` (engine rebuilt, vision unchanged) — then start via `./run-maya-maya-s-v2-iq2_xxs.sh`.
3. Pair: restart v1.0.34 fresh → run; then checkout `7655730`, start (the plain start recompiles
   the previous engine), run; then checkout `main` and start again — engine stamps log-verified
   (`2b852534a0789476` v1.0.9, `f15b35e76c6513ef` v1.0.34), box left serving v1.0.34. Script:
   `data/raw/driver-pair-1034.sh`; log `data/raw/pair-1034.log`.

## Note on experiment 03

The v1.0.33 pair (measured 14:44–15:04 UTC against the same v1.0.9 baseline) remains in the
record as experiment 03 — superseded the same day, never published.

## Figures and raw

Figures: [`charts/maya-v100-64k-depth-v1034.png`](../charts/maya-v100-64k-depth-v1034.png) (the
depth card) and
[`charts/maya-v100-64k-v109-vs-v1034.png`](../charts/maya-v100-64k-v109-vs-v1034.png) (the pair,
per depth). Raw: `model-bench-64k-v1034-*` and `model-bench-64k-v109-rerun2-*` in `data/raw/`;
pair table `data/csv/release-64k-v109-vs-v1034.csv`, deltas `data/csv/release-deltas-64k-1034.csv`.
