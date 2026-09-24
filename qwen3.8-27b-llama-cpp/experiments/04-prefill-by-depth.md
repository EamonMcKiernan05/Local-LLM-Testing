# 04 — prefill rate against prompt depth

**2026-09-20. Build `b11041`. `Qwen3.8-27B-UD-Q4_K_XL.gguf`, 3 cards, layer split `35,37,28`, q8_0 KV, flash attention on, `-ub 256`, temp 0.8, one harness throughout. Cache 32,768 for the 20k run, 262,144 for the deeper runs.**

## Result

| prompt tokens | cache | speculation | prefill tok/s | prefill time | decode at depth |
|---|---|---|---|---|---|
| 19,966 | 32k | none | **1,096.8** | 18.2 s | 15.72 |
| 19,966 | 32k | MTP head, n=4 | 868.3 | 23.0 s | 27.49 |
| 19,966 | 32k | DFlash2 Q4_K_M, n=4 | 810.3 | 24.6 s | 31.36 |
| 19,966 | 32k | DFlash2 Q8_0, n=4 | 822.5 | 24.3 s | 29.44 |
| 99,708 | 131k | none | 840.0 | 118.7 s | 10.41 |
| 127,018 | 262k | none | 775.9 | 163.7 s | 9.22 |
| 127,018 | 262k | DFlash2 Q4_K_M, n=4 | 576.7 | 220.3 s | 13.97 |
| 149,462 | 262k | none | **717.4** | 208.3 s | 8.44 |
| 149,462 | 262k | DFlash2 Q4_K_M, n=4 | 540.4 | 276.6 s | 12.63 |

## What it shows

- **Prefill degrades gracefully with depth, with no cliff**: 1,096.8 → 840.0 → 775.9 → 717.4 tok/s from 20k to 150k, i.e. −35% at the deepest prompt. There is no point in the curve where it falls off a wall.
- **Turning on speculation costs prefill at every depth**, and consistently: roughly 21% for the MTP head and roughly 26% for DFlash2, because the draft model has to be filled from the target's states across the entire prompt.
- **Decode swaps the ranking at depth.** No-spec is the fastest to prefill and the slowest to generate; DFlash2 flips from losing at shallow depth to winning at 150k (12.63 against no-spec's 8.44) — but still losing to MTP, which the later two-card work measured far higher on this same depth.
- **This is the table that sets the storage and prompt-length expectations for the box.** At 150k tokens you pay 208 seconds before the first token is generated at all, with no speculation.

## Note on the source

This table exists in one copy of the experiment write-up and not the other: it was added to the working copy after the vault copy was last synced. It is reproduced here and the rows are in `data/csv/prefill-by-depth.csv`; the arithmetic behind the "1,097 → 717, no cliff" line quoted elsewhere in the project history comes from these nine runs.
