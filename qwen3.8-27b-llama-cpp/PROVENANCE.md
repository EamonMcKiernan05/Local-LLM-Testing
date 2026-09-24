# Provenance: where every file here came from

Collected 2026-09-24. The rule for this repo is simple: **a number appears here only if it came off a real run, and every table says which run.**

## Sources, in order of reliability

1. **Raw per-arm records** (`data/raw/*.jsonl`, `data/raw/100k-arm-summary.json`). Written by the sweep drivers themselves, one JSON object per arm, at the moment the arm finished. These are the strongest evidence in the repo. 58 arms.
2. **The written reports**, produced immediately after each sweep from those records and from llama-server's own logs, and reviewed by hand at the time:
   - `llama-dflash2-sweep-2026-09-18.md` (107 arms)
   - `two-card-tensor-split-gsq-iq3s-2026-09-22.md` (70 arms)
   - `two-card-100k-nmax-trims-2026-09-23.md` (58 arms, including the three-card work)
   - the working copy of `qwen38-exl3-dflash2-on-.5.md`, whose section 13 holds the depth profile
3. **Server journal text preserved in the agent session records**, for the live-service numbers where no sweep ran: the August MTP comparison, and the September production request. Extracted mechanically by `scripts/build_session_evidence.py` — every row carries its original log timestamp and PID.

## What was reachable, and what was not

- **The inference box was unreachable at collection time.** It answered nothing on ping or SSH (`No route to host`), so the raw artifact directories that live on it could not be re-read or re-verified. The files below were pulled off it *during* the sweeps and are complete copies.
- **Raw per-arm JSONL we hold:** the 100k trim sweep (20 arms), the 100k confirmation (12), the split-mode matrix (8), the three-card matrix (7), the three-card DFlash2 sweep (11). Total 58 arms, in `data/raw/`.
- **Raw per-arm JSONL we do not hold:** the 2026-09-18 DFlash2 bake-off (107 arms) and the 2026-09-22 two-card sweep (70 arms). Their drivers' output stayed on the box (`~/dflash-sweep*-results.jsonl`, `~/two-card-sweep-results.jsonl`) and could not be copied. For those two experiments the tables in `data/csv/` are transcribed from the reports, which were in turn written from those files row by row on the day. The per-arm logs and the JSONL are still on the box.
- **A copy of one report exists in two versions.** The working copy of the EXL3 report carries a section 13 (the depth profile) that the vault copy does not; the vault copy carries a later status paragraph that the working copy does not. Both were read; the depth table is reproduced in `experiments/04`.

## The CSV files, and what each column means

| file | rows | contents |
|---|---|---|
| `100k-and-three-card-arms-normalised.csv` | 58 | every raw arm record we hold, one tidy schema |
| `dflash2-sweep-temp0.0.csv` / `-temp0.6.csv` / `-temp0.8.csv` / `-temp0.9.csv` | 32 / 11 / 32 / 32 | the full DFlash2 vs MTP bake-off, per temperature |
| `dflash2-best-per-drafter-per-temp.csv` | 15 | selection of the best row per drafter per temperature (a summary, not new runs) |
| `live-service-build11041-20k.csv` | 2 | live service straight after the rebuild |
| `prefill-by-depth.csv` | 9 | prefill rate against prompt depth |
| `two-card-160k-load-vram.csv` | 5 | VRAM at 160k context, layer vs tensor |
| `two-card-mtp-nmax-20k.csv` / `-150k.csv` | 14 / 14 | the two-card n-max sweeps |
| `two-card-20k-verification-3-repeats.csv` | 2 | the `ignore_eos` verification, three repeats per arm |
| `two-card-bub-grid-20k.csv` / `-150k.csv` | 21 / 21 | the `-b`/`-ub` grids, including the 3 failed arms |
| `two-card-fastest-configs.csv` | 7 | summary of the fastest configurations (not new runs) |
| `100k-stageA-nmax.csv` / `100k-stageB-topk-minp.csv` | 8 / 12 | the 100k n-max and sampler trim sweeps |
| `100k-confirm-nmax5-8-3-repeats.csv` | 4 | arm means and spreads from 12 runs (a summary) |
| `100k-split-mode-matrix.csv` | 8 | tensor/layer, 2 and 3 cards |
| `three-card-matrix.csv` | 7 | three cards: `-ts` balances, DFlash2, one aborted arm |
| `three-card-dflash2-nmax.csv` | 8 | DFlash2 n-max 1-8 on three cards |
| `100k-selftest-gguf-metadata.csv` | 5 | the comparison that exposed the GGUF-metadata inheritance (not new runs) |
| `live-service-summary.csv` | 5 | the live-service configurations, with provenance per row |
| `live-traffic-draft-acceptance-aug14-15.csv` | 28 | per-request journal lines from real fleet traffic |
| `live-service-2026-09-23-prefill-progress.csv` | 10 | the production cold prefill, sample by sample |
| `live-service-2026-09-23-decode-series.csv` | 21 | the production decode rate, sample by sample |
| `buun-fork-sweep-tok_s.csv` etc. | 25 / 6 / 3 / 4 | the fork: main sweep, harness comparison, long context, drafter quants |

### Counting the runs

**284 recorded runs** on Qwen3.8-27B: 107 (DFlash2 bake-off) + 70 (two-card) + 58 (100k and three-card) + 38 (fork) + 9 (depth profile) + 2 (post-rebuild reference). **277 produced a measurement; 7 failed at load** (3 in the two-card `-b`/`-ub` grid, 4 in the three-card sweeps: one tensor+DFlash2 arm and three `--spec-draft-device` pinning arms) and are marked in the data with an `error` field. That excludes the summary tables listed above, which select from runs already counted, and excludes the live-service journal series, which is one production request sampled repeatedly rather than a series of arms.

### The one derived column

`ms/step` in the DFlash2 bake-off tables is computed: `gen_ms / (gen_tokens / mean_len)`. It is the only figure anywhere in this repo that is not read straight off a run. Its formula is stated in the tables' source report.

### Counter sources

Draft-acceptance figures come from one of two places and **they do not agree**, because they divide by different denominators:

- **in-run** — the per-request `slot print_timing: draft acceptance = ... mean len = ...` journal line, covering the measured request only. Used in the published tables.
- **cumulative** — llama.cpp's `/metrics` counters (`spec_decode_*_total`), which include the discarded warm-up request. Slower arms barely differ; winners do (`mtp7-untrimmed` reads AL 5.000 against 5.31 in-run). Columns in `100k-and-three-card-arms-normalised.csv` carrying this source say `_metrics_cumulative` in the name.

`prefill_tok_s` and `gen_tok_s` always come from the response's own `timings` block and are unaffected by that distinction.

## Scripts

- `scripts/build_data.py` — extracts the tables from the source reports into `data/csv/`. Moves cells; never recalculates.
- `scripts/build_raw.py` — normalises the raw per-arm JSONL into one schema.
- `scripts/build_session_evidence.py` — extracts the live-service journal series from the session records.
- `data/raw/harness-depth_test.py`, `data/raw/driver-100k-trims.py` — the actual harness and driver for the 100k sweeps, unmodified.

## Housekeeping

- No credentials, hostnames of private services or personal data are in this repo. The host is referred to as "the box"; the path `/home/eamon/` appears only where it is part of a command that someone would need in order to reproduce a result.
- Source reports also live in a private Obsidian knowledge vault and were used with their author's consent; they are quoted freely here because the runs, the box and the data are all his.
