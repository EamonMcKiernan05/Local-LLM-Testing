# 02 — AJ-IQ2_XXS at 131,072 context: the context comparison (2026-10-16)

**Goal.** Re-run the bench at half the context (131,072) the same day and compare with the 256K
numbers at the shared depths (20K / 60K / 100K) — the question being whether the full 262,144
window costs anything on this box.

## Setup

- The AJ config's `--max-context` was flipped **262144 → 131072** (backup kept as
  `.bak-262144`; the edit asserts the old value before writing).
- Three fresh-load batteries on the shared depths; **no postcopy burn** — there was no new
  staging to absorb (same NVMe copy, five loads into the day); the burn is a
  first-session-after-copy device and stays with experiment 01.
- Start gates on every arm: `n_ctx == 131072`, same engine stamp `c823b8ca185405dd`, config md5
  `4d65f6be873d543244a497d3ba104940`.
- Same harness, same documents, same per-request tags; every battery is one fresh load + a
  discarded warm-up.

## Results

131,072 ctx — three fresh-load runs per depth, mean (sd):

| depth | prefill tok/s | sd | decode tok/s | sd |
|---|---:|---:|---:|---:|
| 20K | 653.1 | 0.44 | 24.10 | 0.36 |
| 60K | 708.0 | 1.78 | 24.87 | 0.76 |
| 100K | 760.7 | 2.22 | 25.37 | 0.15 |

The comparison (per-depth deltas on the unrounded means; 131K vs 256K):

| depth | 256K prefill | 131K prefill | Δ | 256K decode | 131K decode | Δ |
|---|---:|---:|---:|---:|---:|---:|
| 20K | 651.7 | 653.1 | +0.2 % | 23.27 | 24.10 | +3.6 % |
| 60K | 705.2 | 708.0 | +0.4 % | 24.77 | 24.87 | +0.4 % |
| 100K | 758.6 | 760.7 | +0.3 % | 24.47 | 25.37 | +3.7 % |
| **mean** | | | **+0.3 %** | | | **+2.6 %** |

## Reading

- **The finding is parity: context length costs nothing measurable here.** Prefill is flat
  (+0.2 / +0.4 / +0.3 %); decode runs +3.6 / +0.4 / +3.7 % → +2.6 % mean.
- The decode deltas show no depth trend (two cells sit high, the 60K cell is flat) and this is
  one day, three cells, three runs each: treat the mean as "no measurable cost", **not** as a
  2.6 % win. Same house rule as ever — decode claims live on the band, not on single cells.
- The 256K side of the table is experiment 01's three-run means; the 131K side ran hours later
  the same day on the same file and rig, which is what keeps this a clean same-day comparison.

## State at the end

The driver restored Maya-S serving after the cycle. Later that evening the AJ config was
returned to 262144 (stop / config edit / start, byte-verified against `.bak-262144`; no
re-bench — the 131K numbers above are the measurement, the restore is just the box's state).

## Artifacts

- Raw battery records: `data/raw/model-bench-aj-131k-sn730-r{1,2,3}-*`
- Serving config: `data/raw/config-131k-served.json` (the 256K sibling sits beside it)
- The comparison tables: `data/csv/ctx-aj-256k-vs-131k.csv`, `data/csv/ctx-deltas-aj-256k-vs-131k.csv`
- The card: `charts/aj-iq2xxs-131k-mean.png` (`scripts/make_chart_131k.py`) and the comparison
  card `charts/aj-iq2xxs-256k-vs-131k.png` (`scripts/make_chart_compare_aj.py`)
