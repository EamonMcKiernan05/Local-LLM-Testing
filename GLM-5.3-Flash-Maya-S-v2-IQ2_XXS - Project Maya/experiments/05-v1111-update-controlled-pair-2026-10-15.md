# Experiment 05 — v1.1.11 update: three-run-per-side controlled pair (2026-10-15)

**Pair:** Project Maya **v1.1.1** (`eb9b7ec`, build stamp `d640b61395691e36` — the installed build)
vs **v1.1.11** (`8931339`, stamp `5a23fa1ec92e67aa` — the latest release that morning). Both sides
compiled locally for sm_70 on box .5 the same morning, same battery, **alternated A B A B A B** — one
engine load per battery, **three measured runs per side**, means below. The v1.1.11 side runs the
config the update itself writes: its first start appends `--expert-profile
data/expert-profile-glm.bin` (the shipped routing profile — v1.1.3's "an installed config gets the
profile at its next start"). The v1.1.1 side runs its original config (it predates the flag). All
else identical: 64K context, RAM headroom 3, layer split, MTP drafting.

**Headline: decode +6.7 % mean, up at every depth (+9.1 / +6.8 / +4.3 %); prefill unchanged (−1.7 %
mean, inside this box's wander — no gain claimed).** The decode-side changes the release notes
promise for this hardware (the v1.1.3 expert-profile fill, the v1.1.5 shared CPU rows, the v1.1.2
sampler) show up; between the two versions there was no V100-relevant prefill item.

| depth | v1.1.1 decode | v1.1.11 decode | delta | v1.1.1 prefill | v1.1.11 prefill | delta |
|---|---|---|---:|---|---:|---:|
| 20K | 14.00 | 15.27 | **+9.1 %** | 394.4 | 386.7 | −2.0 % |
| 40K | 17.67 | 18.87 | **+6.8 %** | 461.3 | 461.7 | +0.1 % |
| 60K | 17.93 | 18.70 | **+4.3 %** | 451.2 | 437.2 | −3.1 % |
| **mean** | | | **+6.7 %** | | | **−1.7 %** |

Means of three runs per side (one battery per run; deltas from the unrounded means,
`data/csv/release-deltas-64k-1111.csv`; per-run rows in `data/csv/depth-64k-v1111-runs.csv`).

## Method, and the exclusions

- Six measured batteries (3 per side) plus one discarded **post-copy calibration battery**
  ("burn", v1.1.1). All seven ran the same three documents at 20K/40K/60K (the builder asserts one
  book per depth and a ptok spread of ≤ 2 tokens across all seven); the harness discards a warm-up
  row per battery.
- **The burn battery is excluded by design**: the first session after the HDD→NVMe copy reads high
  (page-cache assist). Its prefill came in at 402.6 / 501.3 / 480.1 — +2 to +9 % above the measured
  v1.1.1 means, exactly the known artifact; it absorbed that state so runs r1–r3 started clean.
- **No measured run was excluded.** Audit: every arm passed its gates (engine stamp match per arm, a
  fresh load per battery, ready-time check against a stale server, configs md5-verified against
  their side's snapshot before and after each start). No cell crossed the exclusion bar — the
  largest single-cell deviation vs the other two runs of its own side is ≈ −15 %, inside this box's
  known wander, and the low cells track a ~0.6 pp lower cache-hit session in the engine's own
  `glm stat:` lines (real session state, not a broken measurement).
- **Per-cell spread** (min–max over each side's three runs), for reading single cells — not the
  means: 20K decode 12.8–14.8 (v1.1.1) / 14.7–16.3 (v1.1.11); 40K decode 16.9–19.0 / 17.8–20.2;
  60K decode 16.1–19.0 / 18.0–19.6; prefill within ±1.5 % per cell except v1.1.1 60K (444.5–457.3).
- The load re-plans the layer split each start (v1.1.1: `[0, 23)/[23, 45)`, "routes from the usage
  counts"; v1.1.11: `[0, 25)/[25, 45)`, "routes from the default coverage curve") — the alternation
  is what keeps that per-load lottery out of the between-side read.

## Agreement check (v1.1.1 vs its own records)

The v1.1.1 side re-reads within ~1–2 % of its 2026-10-12 archive on **prefill** at every depth
(today's means 394.4 / 461.3 / 451.2 vs the 10-12 midday runs' 392.4–404.0 / 460.7–474.7 /
444.7–445.1); decode sits inside the archive's own cell band. Prefill is the metric that reproduces
on this box; decode wanders — read the means, not cells.

## Context

- The config migration above is part of the update as shipped: every installed config gets the
  shipped expert profile at its first start on v1.1.3+.
- Not engaged here (gated for this hardware or opt-in): EXL3 paths (RTX 30+; this GGUF is unaffected),
  the Strix/Gorgon Halo work, Windows/NVLink/CPU-share items, the INT8-KV prompt work (`--kv int8` is
  not in this config), `STRATA_GLM_DISK_SKIP_W` (changes answers — off).
- These are storage-capped numbers: the box streams expert tiers from a DRAM-less SK hynix BC501
  boot SSD, and `glm stat:` shows a disk component in every steady-state request. An NVMe upgrade is
  pending on delivery.

## Artifacts

- Runs on .5 under `~/model-bench/runs/`: `2026-10-15T0919Z-…-v111-postcopy-burn`, `…T0928Z-…-v111-r1`,
  `…T0958Z-…-v1111-r1`, `…T1008Z-…-v111-r2`, `…T1018Z-…-v1111-r2`, `…T1028Z-…-v111-r3`,
  `…T1038Z-…-v1111-r3`.
- Flattened records `data/raw/model-bench-64k-v111-*` / `…-v1111-*` (sha256-checked); drivers
  `driver-pair-1111-*.sh`; logs `pair-1111-*.log`; both sides' configs.
- The cycle ran as prep → bench (+calibration) → restore, with a resume after the first v1.1.11
  start was stopped by the config-drift gate exactly as designed (the update rewrites the config on
  its first start; the gate caught it before any bench data was taken) — the full sequence is in
  `pair-1111.log` / `pair-1111-resume.log`.
