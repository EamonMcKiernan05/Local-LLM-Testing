# Provenance: where every file here came from

Collected 2026-10-08. The rule for this folder: **a number appears here only if it came off a real
run, and every table says which run.** All measurements are on Maya-S-v2 IQ2_XXS (GLM-5.3-Flash).

## Sources, in order of reliability

1. **The model-bench run records** — written by the harness on box .5 as each arm finishes, and
   moved here as flattened copies (`<stem>-results.jsonl` / `-meta.json` / `-summary.csv`); every
   file is a byte-identical copy, sha256-checked against the box at pull time (the manifest is
   `raw/SHA256SUMS`):

   | stem | box run id | what |
   |---|---|---|
   | `model-bench-128k` | `2026-10-07T1917Z-maya-s-v2-128k` | bring-up, stock 128K config |
   | `model-bench-128k-warm2` | `2026-10-07T2005Z-maya-s-v2-128k-warm2` | bring-up repeat after a usage-warm restart |
   | `model-bench-64k-tuned` | `2026-10-07T2042Z-maya-s-v2-64k-tuned` | the tuned 64K config — the archived baseline |
   | `model-bench-64k-tuned-rerun` | `2026-10-08T1014Z-maya-s-v2-64k-tuned-rerun` | previous build re-run on the update day (the controlled pair's "before") |
   | `model-bench-64k-v109` | `2026-10-08T1000Z-maya-s-v2-64k-v109` | v1.0.9 after the update (the pair's "after") |

   Each record carries one discarded warm-up row and three measured arms (20K / 40K / 60K).
2. **The serving config and the drivers** — verbatim copies: `config-64k-served.json` (both sides of
   the pair ran on exactly this config; byte-identical to the pre-update snapshot, checked
   2026-10-08), `driver-bench-v109.sh` / `driver-bench-rerun.sh` (the two bench drivers, including
   the checkout/re-build/restore steps of the controlled pair), and `update-v109.log` (the update
   run's own output).
3. **Engine identity for the pair**: "previous build" = the tree at commit `142540b` (2026-10-07,
   pre-version-numbering); "v1.0.9" = `7655730` (2026-10-08). Both sides compiled locally for
   sm_70 (CUDA 12.9); the engine build stamps (`build/MAYA-BUILD.json` src hashes
   `326ec0d7adf59f7e` and `2b852534a0789476` respectively) were verified before each side was
   benchmarked.

## Counting the runs

**15 recorded runs, every one with measurements; no failures:** 5 benches × 3 depth arms
(20K / 40K / 60K). The five warm-up requests were discarded by design — they stay visible in the
raw files (`"kind": "warmup"`) and are not counted.

## Derived values (the only numbers not read straight off a run)

| file | column | formula |
|---|---|---|
| `release-deltas-64k-109.csv` | `*_delta_pct_derived` | 100 × (v1.0.9 value / re-run value − 1); the `mean` row averages the three **unrounded** deltas, then rounds |
| `release-deltas-64k-rerun-vs-archived.csv` | `*_delta_pct_derived` | same formula, re-run vs the archived 2026-10-07 run — the agreement check |

The charts read their values from `data/csv/` at draw time (percentages included) — nothing is
retyped into a chart script.

## What is not here, and why

- **The full engine logs stay on the box** (the `glm stat:` per-request lines, tier warm-up lines,
  and the bring-up drive-sampler loop's raw output). The drive numbers quoted in experiment 01 are
  from that sampler log.
- **Install-day smoke tests** (a vision image test and a short chat) are not part of this dataset.
- **Upstream's published V100 numbers** (the project's own README speeds) are the authors' and are
  referenced as such only where a comparison is explicitly made; they are not in any table here.

## Housekeeping

- No credentials, private hostnames or personal data are in this repo. The box is referred to as
  "box .5"; absolute paths appear only where needed to reproduce a result.
