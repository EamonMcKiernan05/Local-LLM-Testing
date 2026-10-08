# 01 — bring-up and the tuned 64K config (2026-10-07)

Project Maya (the Strata-derived engine) was installed on box .5 on 2026-10-07: Maya-S-v2 IQ2_XXS
(96.5 GB, 3 shards + pack) served from the NVMe working copy, layer-split `[0, 24) / [24, 45)`
across the two V100s with a RAM tier and SSD streaming. Two benches were run the same day:
the stock 128K-context config, then the tuned 64K config the box has served since.

## Results

Stock 128K config (two runs — the second after a usage-warm restart, which does not move the
numbers):

| depth | prefill (run 1 / run 2) | decode (run 1 / run 2) |
|---|---|---|
| 20K | 93.8 / 112.5 | 9.4 / 8.5 |
| 60K | 96.5 / 96.4 | 11.2 / 12.1 |
| 100K | 99.1 / 100.6 | 12.5 / 10.6 |

Tuned config — 64K context and a bigger pinned RAM tier (`STRATA_GLM_RAM_HEADROOM_GB=3`), which
grows the expert caches from ~10.7k to ~11.5k slots of the 12,096 experts and roughly halves the
per-token disk reads:

| depth | prefill | decode |
|---|---|---|
| 20K | 160.9 | 12.4 |
| 40K | 146.9 | 14.8 |
| 60K | 141.6 | 15.9 |

## The boot-drive diagnosis

A direct-read sampler ran during the tuned bench (the drive's own speed, `dd iflag=direct` every
~100 s while the model served): healthy reads ~1.1 GB/s idle, collapsing to 90–330 MB/s within
minutes of sustained load. With ~600 experts always streamed off the disk, disk waits measured
29–127 ms/token — about half of each token's cost. Remove the disk component and the arithmetic
lands at the authors' ~29 tok/s reference; a proper NVMe is the fix, never applied here.

## Raw

`data/raw/model-bench-128k-*`, `model-bench-128k-warm2-*`, `model-bench-64k-tuned-*` (each
`results.jsonl` + `meta.json` + `summary.csv`, sha256-checked). Tables:
`data/csv/bringup-128k-stock.csv` and `depth-64k-previous.csv`.
