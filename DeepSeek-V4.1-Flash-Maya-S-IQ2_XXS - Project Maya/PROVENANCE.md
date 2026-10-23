# Provenance: where every file here came from

Collected 2026-10-23 from records made on box .5 on 2026-10-21. The rule for this folder:
**a number appears here only if it came off a real run, and every table says which run.** All
measurements are on DeepSeek-V4.1-Flash-1017, Maya-S IQ2_XXS, served by Project Maya v1.1.19 on the
two V100s.

## Sources, in order of reliability

1. **The model-bench run records** — written by the harness on box .5 as each arm finished, and
   moved here as flattened copies (`model-bench-<label>-results.jsonl` / `-meta.json` /
   `-summary.csv`). Every file is a byte-identical copy, sha256-checked against the box at
   collection time (manifest: `data/raw/SHA256SUMS`):

   | stem | box run id | what |
   |---|---|---|
   | `model-bench-ds4-maya-s-128k-burn` | `2026-10-21T1409Z-ds4-maya-s-128k-burn` | post-load cache warm-up battery, discarded by design |
   | `model-bench-ds4-maya-s-128k-run1` | `2026-10-21T1433Z-ds4-maya-s-128k-run1` | measured battery, same load as the burn |
   | `model-bench-ds4-maya-s-128k-run2` | `2026-10-21T1458Z-ds4-maya-s-128k-run2` | measured battery, fresh load (server restarted at 14:57Z) |

   Each record carries one discarded warm-up row (`"kind": "warmup"`) and three measured arms
   (20K / 60K / 100K prompt depth, 400 generated tokens each). The run metadata in each
   `-meta.json` holds the battery parameters (gen 400, temp 0.5, seed 12345, the instruction
   template), the skipped depths and their reasons, and the per-card VRAM/temperature sample.

2. **The serving and bench cycle** — `serving/ds4-bench-cycle.sh` is the driver that ran all three
   batteries (`MODEL_BENCH_GGUF` set to the Maya-S shard 1, so the slicer tokenizes in the model's
   own vocab), `serving/ds4-bench.log` is its full log with every arm's numbers as the harness
   printed them, `serving/maya-ds4-setup.log` is the pack build and first start, and
   `serving/run-maya-ds4.sh` is the launcher. All four are byte-identical copies
   (`serving/SHA256SUMS`) checked against the box on 2026-10-23.

3. **Engine and model identity** — Project Maya **v1.1.19**, engine `maya-ds4` (the setup log's
   banner and the update record). Model: `peasantsmith/DeepSeek-V4.1-Flash-1017-Maya-GGUF`
   `Maya-S/`, 6 shards, **339.5 GB**, as reported by the setup step that registered the files
   (`serving/maya-ds4-setup.log`, "Step 5"). The pack build lists the quant types it found:
   BF16 0.1 GB, F32 0.5 GB, IQ2_S 23.2 GB, IQ2_XXS 74.7 GB, IQ3_S 15.6 GB, IQ3_XXS 55.5 GB,
   MXFP4 7.2 GB, Q6_K 161.3 GB, Q8_0 9.3 GB.

4. **The write-up** — `experiments/01-first-deepseek-run-maya-s-128k-2026-10-21.md`, written from
   the records above on the day and re-checked against them at collection time.

## What is derived, not measured

- **`prefill_spread_pct` / `decode_spread_pct`** in `data/csv/averages.csv` are the run-to-run gap
  between the two batteries as a percentage of their mean: `100 × |a − b| / ((a + b) / 2)`.
- **`*_mean`** columns are the arithmetic mean of the two batteries' values at that depth.
- Everything else in the CSV is a value the harness wrote into `results.jsonl`.

## What is not here, and why

- **The serving JSON the runs used.** The live `~/project-maya/maya-ds4.json` was rewritten on
  2026-10-23 (vision pack enabled, v1.1.25 calibration), so the exact file from 21 Oct no longer
  exists. The launcher, the args it takes and the engine's own start banner are here instead; the
  write-up records the config as served.
- **The engine log for this load** (`~/project-maya/maya-ds4.log` on the box was overwritten by
  later loads). The engine-facts lines quoted in the write-up were read from it at the time.
- **The DSpark drafter test** was a calibration, not a bench: its numbers (4.6 vs 6.8 tok/s at short
  context) appear in the write-up only, with no harness record. They are not in any table or figure.
- **No raw per-request log extract** beyond the harness rows: this batch's headline numbers are all
  client-side timings from `bench.py`, which is the same method as every earlier batch in this repo.

## Counting

**2 recorded runs** (batteries). 6 measured arms. 0 failed. 1 burn battery excluded by design
(3 arms), for the mechanical reason that it exists to warm the caches after the fresh load — not
because any of its numbers looked wrong.
