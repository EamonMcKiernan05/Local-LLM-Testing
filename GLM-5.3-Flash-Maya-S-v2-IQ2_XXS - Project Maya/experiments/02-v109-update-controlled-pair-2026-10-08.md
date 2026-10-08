# 02 — v1.0.9: +69.1 % prefill on a same-day pair (2026-10-08)

The box's install was updated to the upstream v1.0.9 (commit `7655730`) the morning of 2026-10-08
(stop → `git pull` fast-forward → `./setup.sh`, which recompiles only what changed and starts;
config byte-identical, engine rebuilt for sm_70). The update jump included the project's prefill
work — the SSD read-ahead and the tensor-core prompt attention — plus `--bench`/`--report`, the
Turing fix, and conversation slots.

Measured the house way: **a controlled same-day pair**. The previous build (tree `142540b`) was
rebuilt from its commit and re-run the same morning, on the same config as served (64K context,
RAM headroom 3), same documents, one run per depth — then the same bench on v1.0.9. Only the
engine differs.

## Results

| depth | decode before | decode after | Δ | prefill before | prefill after | Δ |
|---|---|---|---|---|---|---|
| 20K | 11.9 | 13.5 | +13.4 % | 161.7 | 226.4 | **+40.0 %** |
| 40K | 16.3 | 15.1 | −7.4 % | 149.1 | 263.9 | **+77.0 %** |
| 60K | 14.9 | 14.4 | −3.4 % | 142.3 | 270.8 | **+90.3 %** |
| mean | | | +0.9 % | | | **+69.1 %** |

Reading: the prefill gain grows with depth (the read-ahead scales with the prompt) and is the
largest measured change on this box since the storage fix — 142 → 271 tok/s at 60K. Decode is flat:
+13.4 / −7.4 / −3.4 % is single-rep noise on three cells (mean +0.9 %).

## The agreement check

The fresh re-run of the previous build landed on its archived 2026-10-07 numbers: prefill +0.5 /
+1.5 / +0.5 % (mean +0.8 %), decode −4.0 / +10.1 / −6.3 % (mean −0.1 %) — prefill reproduces
tightly, decode wanders per cell inside its band. The pair therefore measures the engine, not the
day. Table: `data/csv/release-deltas-64k-rerun-vs-archived.csv`.

## Update and pair procedure (as run)

1. Stop the server (`kill -TERM <serve/server.py pid>`), verify VRAM drops.
2. `git fetch origin --tags --force` → fast-forward to `7655730` → detached `./setup.sh` (its
   `refresh_engine` rebuilds only when the source hash changed, then starts; ~2 min with ccache).
3. For the pair: checkout `142540b`, start (`./setup.sh` recompiles the previous engine), run the
   bench, then checkout `main` and start again — engine stamps log-verified on both sides
   (`326ec0d7adf59f7e` old, `2b852534a0789476` new), box left serving v1.0.9.

## Figures and raw

Figures: [`charts/maya-v100-64k-depth.png`](../charts/maya-v100-64k-depth.png) (the re-issued card,
v1.0.9 numbers) and
[`charts/maya-v100-64k-v109-vs-previous.png`](../charts/maya-v100-64k-v109-vs-previous.png)
(the pair, per depth). Raw: `model-bench-64k-v109-*` and `model-bench-64k-tuned-rerun-*` in
`data/raw/`; pair table `data/csv/release-64k-before-rerun-vs-v109.csv`, deltas
`data/csv/release-deltas-64k-109.csv`.
