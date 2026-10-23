# Provenance: where every file here came from

Collected 2026-10-23 from records made on box .5 on 2026-10-22. The rule for this folder:
**a number appears here only if it came off a real run, and every table says which run.** All
measurements are on DeepSeek-V4.1-Flash-1017, Maya-XS IQ1_S, served by Project Maya v1.1.22 (engine
`maya-ds4`) on the two V100s.

## Sources, in order of reliability

1. **The model-bench run records** — written by the harness on box .5 as each arm finished, moved
   here as flattened copies and sha256-checked against the box at collection time (manifest:
   `data/raw/SHA256SUMS`):

   | stem | box run id | what |
   |---|---|---|
   | `model-bench-ds4-maya-xs-128k-burn` | `2026-10-22T1911Z-ds4-maya-xs-128k-burn` | post-load cache warm-up battery, discarded by design |
   | `model-bench-ds4-maya-xs-128k-run1` | `2026-10-22T1921Z-ds4-maya-xs-128k-run1` | measured battery, same load as the burn (warmed) |
   | `model-bench-ds4-maya-xs-128k-run2` | `2026-10-22T1932Z-ds4-maya-xs-128k-run2` | measured battery, fresh load (server restarted at 19:31Z) |

   Each record carries one discarded warm-up row (`"kind": "warmup"`) and three measured arms
   (20K / 60K / 100K prompt depth, 400 generated tokens each). The battery parameters (gen 400,
   temp 0.5, seed 12345, the instruction template), the skipped depths and the per-card VRAM
   sample are in each `-meta.json`.

2. **The setup and bench cycle** — three stage scripts with their complete logs, byte-identical
   copies (`serving/SHA256SUMS`) checked against the box on 2026-10-23:

   | file | what |
   |---|---|
   | `xs-stage1.sh` / `.log` | download of the 276.6 GB Maya-XS set (weights to NVMe, Engram to SATA) at ~23 MB/s: per-file size check, then a sha256 pass — all five shards report OK (the same log's repeat pass on shards 1–3 reports "No such file" against their old staging paths, after the move) |
   | `xs-stage2.sh` / `.log` | update to **v1.1.22**, DSpark download + sha256 check, pack build, speed calibration (drafting vs none) and the config write |
   | `xs-stage3.sh` / `.log` | the bench cycle — readiness gate, engine-facts capture per load, burn + run1 on load 1, server restart, run2 on load 2 |
   | `run-maya-ds4.sh` | the launcher |

   `xs-stage3.log` here is the box's `~/xs-bench.log`, the log stage 3 wrote.

3. **Engine and model identity** — Project Maya **v1.1.22** (`serving/xs-stage2.log`: `tree: v1.1.22`,
   banner line). Model: `peasantsmith/DeepSeek-V4.1-Flash-1017-Maya-GGUF` @ `c273fcb`, `Maya-XS/`,
   5 shards, **276.6 GB**; the pack build in stage 2 lists the quant types it found: BF16 0.1 GB,
   F32 0.5 GB, **IQ1_S 106.2 GB**, IQ2_XXS 3.5 GB, Engram Q6_K 161.3 GB, Q8_0 9.3 GB.

4. **The comparison table** — `data/csv/compare.csv`, built by `scripts/build_data_compare.py` from
   this folder's `averages.csv` and the sibling Maya-S folder's. The builder **refuses to write**
   unless the two sets cover the same depths and sliced the same document at each depth, so the
   comparability proof ships with the data.

5. **The write-up** — `experiments/01-maya-xs-128k-and-the-s-to-xs-gap-2026-10-22.md`, written from
   the records above on the day and re-checked against them at collection time.

## What is derived, not measured

- **`prefill_spread_pct` / `decode_spread_pct`**: `100 × |a − b| / ((a + b) / 2)` across the two
  batteries at that depth.
- **`*_mean`**: arithmetic mean of the two batteries at that depth.
- **`compare.csv`'s `*_delta_pct` and `*_ratio`**: computed from those means, not measured directly.
- **The 13.9 vs 11.7 tok/s calibration** in the write-up is the setup's own measurement (two loads,
  a 1,024-token answer each), not a model-bench battery. It is recorded with the mechanism and does
  not appear in any table or figure.
- **The Maya-S VRAM/expert counts** quoted in the S→XS comparison come from the 21 Oct engine log as
  recorded in that folder's write-up. They are indicative, not re-derived here.

## What is not here, and why

- **The serving JSON the runs used.** The live `~/project-maya/maya-ds4.json` was rewritten on
  2026-10-23 (vision pack enabled, v1.1.25 calibration), so the 22 Oct file no longer exists. Stage 2
  logs the calibration and the config write; the args are recorded in the write-up.
- **The full engine logs from those two loads.** Only the engine-facts lines captured into
  `xs-stage3.log` at each load survive.
- **The vision work of 2026-10-23** is not part of this dataset: it is a capability check on the same
  model file, done after the benches, with no bench record.

## Counting

**2 recorded runs** (batteries). 6 measured arms. 0 failed. 1 burn battery excluded by design
(3 arms) — a mechanical exclusion (it exists to warm the caches after the fresh load), not a
judgement about its numbers.
