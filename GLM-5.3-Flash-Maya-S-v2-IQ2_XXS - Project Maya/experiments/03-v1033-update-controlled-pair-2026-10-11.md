# 03 — v1.0.33: +86.9 % prefill, +20.2 % decode on a same-day pair (2026-10-11)

The install was updated to upstream v1.0.33 (commit `6083122`) the morning of 2026-10-11 — a jump
of ~24 releases since v1.0.9 (tool-call parsing fixed end-to-end, the long-prompt number
tokenizer fix, the expert-tier crash fixes, better MTP drafts, the smaller KV indexer at depth,
CPU-lane timing kept across starts, conversation slots, `--calibrate` for disk reads, the new
dashboard and the setup screen). The same morning the model was moved onto the NVMe (a 98.6 GB
copy at ~198 MB/s, ~8 min; Strata's working set swapped out), and this pair was run on it.

Measured the house way: **a controlled same-day pair**. v1.0.9 (tree `7655730`) was rebuilt from
its commit and re-run the same morning, on the same config as served (64K context, RAM headroom
3), same three documents, one run per depth — then the same run on v1.0.33. Only the engine
differs.

## Results

| depth | decode v1.0.9 | decode v1.0.33 | Δ | prefill v1.0.9 | prefill v1.0.33 | Δ |
|---|---|---|---|---|---|---|
| 20K | 11.8 | 14.5 | +22.9 % | 223.0 | 412.6 | **+85.0 %** |
| 40K | 14.2 | 17.4 | +22.5 % | 254.0 | 501.5 | **+97.4 %** |
| 60K | 14.6 | 16.8 | +15.1 % | 267.6 | 476.9 | **+78.2 %** |
| mean | | | +20.2 % | | | **+86.9 %** |

Reading: prefill nearly doubles at every depth (254 → 502 tok/s at 40K) — the project's prompt
work. Decode is up across all three cells (+15.1 to +22.9 %), outside the ±10 % per-cell band, so
the mean (+20.2 %) is the claim; the candidates in the jump are the better MTP drafting, the
"experts leaving VRAM are no longer re-read from the SSD" fix, and the CPU-lane timing fix. One
run per cell; quote the mean.

## The agreement check

The fresh re-run of v1.0.9 landed close to its 2026-10-08 archive on prefill: −1.5 / −3.8 / −1.2 %
(mean −2.1 %). Its decode sat ~6 % under its archive (−12.6 / −6.0 / +1.4 %, mean −5.7 %) — inside
the per-cell wander band, but it means a sliver of the pair's decode gain may be day drift; the
prefill claim is unaffected. Table: `data/csv/release-deltas-64k-v109-rerun-vs-archived.csv`.

## Update and pair procedure (as run)

1. Stop the server (`kill -TERM <serve/server.py pid>`), verify VRAM drops.
2. Update: `git fetch origin --tags --force` → fast-forward to `6083122` → `./setup.sh --setup
   --no-start` (rebuilds engine + vision; the plain start path alone does not refresh the vision
   encoder) — then start via `./run-maya-maya-s-v2-iq2_xxs.sh`.
3. For the pair: restart v1.0.33 fresh → run; then checkout `7655730`, start (`./setup.sh`
   recompiles the previous engine), run; then checkout `main` and start again — engine stamps
   log-verified on both sides (`2b852534a0789476` v1.0.9, `13c572a2c0c8d2ef` v1.0.33), box left
   serving v1.0.33. Script: `data/raw/driver-pair-1033.sh`; log `data/raw/pair-1033.log`.

## Figures and raw

Figures: [`charts/maya-v100-64k-depth-v1033.png`](../charts/maya-v100-64k-depth-v1033.png) (the
depth card, v1.0.33 numbers) and
[`charts/maya-v100-64k-v109-vs-v1033.png`](../charts/maya-v100-64k-v109-vs-v1033.png) (the pair,
per depth). Raw: `model-bench-64k-v1033-*` and `model-bench-64k-v109-rerun-*` in `data/raw/`;
pair table `data/csv/release-64k-v109-vs-v1033.csv`, deltas `data/csv/release-deltas-64k-1033.csv`.
