# 03 — Per-request sweeps: the drafter gate and the sampler trims (2026-10-03)

**20 arms on the base in ~22 minutes — no server restarts.** Strata takes `temperature` /
`top_p` / `top_k` / `min_p` / `seed` and `strata_tune.spec_min_p` *per request*, so every arm
here is one HTTP call against the live server. (The llama.cpp driver for the same value grids
needed a throwaway server per arm at ~3.5 min each.)

The grids replay the 27B/3060 sweep values so the two engines can be compared directly:
`spec_min_p` {0.00, 0.60, 0.85} × depth {20k, 100k}, then `top_k` {20, 30, 40, 50} × `min_p`
{0.05, 0.08, 0.10} at the gate winner, then a `top_p` probe. 256-token generations,
temperature 0.5, seed 12345, a unique tag per arm so nothing is served from cache.

> **Superseded on the gate question.** The full six-depth sweep the next day (experiment 05,
> 126 runs) settled the drafter gate at **0.50** on repeated evidence. This sweep's
> "best gate per depth" cells are single runs; read them as the shape of the curve, not the
> final pick.

## Base IQ3_S — stage A: the drafter gate × depth

Sampler baseline in every arm: top_k 20, top_p 0.95, min_p 0.00, temp 0.5, seed 12345.

| gate | depth | prefill (tok/s) | decode (tok/s) | gen | accepted/proposed | accept |
|---|---|---|---|---|---|---|
| 0.00 | 20k | 1254.4 | 64.2 | 62 | 42/63 | 67 % |
| 0.00 | 100k | 1645.2 | 53.1 | 67 | 41/79 | 52 % |
| 0.60 | 20k | 1271.0 | **73.7** | 62 | 39/46 | 85 % |
| 0.60 | 100k | 1650.7 | 55.7 | 67 | 36/52 | 69 % |
| 0.85 | 20k | 1266.0 | 63.0 | 31 | 16/19 | 84 % |
| 0.85 | 100k | 1649.1 | **59.1** | 83 | 41/45 | 91 % |

At 100k the tighter gate led (0.85 > 0.60 > 0.00, an 11 % span); at 20k it inverted (0.60
best). The ungated arm proposed the most drafts and converted the fewest at depth (79
proposals, 52 % accepted) — which is why it lands last there.

## Base — stage B: `top_k` × `min_p` at gate 0.85, 100k depth

Decode tok/s (accept rate in brackets), top_p fixed at 0.95:

| top_k \ min_p | 0.05 | 0.08 | 0.10 |
|---|---|---|---|
| 20 | 55.6 (79 %) | 58.6 (88 %) | 55.9 (88 %) |
| 30 | 56.5 (87 %) | 55.4 (73 %) | 54.2 (74 %) |
| 40 | 59.2 (95 %) | 57.9 (86 %) | 58.8 (93 %) |
| 50 | 57.1 (89 %) | **61.6 (88 %)** | 58.0 (92 %) |

**Flat grid**: 54.2–61.6 tok/s, no collapsing cell — the llama.cpp `top_k 40` penalty (−35 %)
does not reproduce on Strata. Best cell `top_k 50 / min_p 0.08` = 61.6; runner-up cells are
inside the single-run noise band (±5 % at this depth).

## Base — stage C: `top_p` probe at the winner

| top_p | decode (tok/s) | accept | gen |
|---|---|---|---|
| 0.90 | 56.9 | 82 % | 63 |
| 0.95 | 61.6 | 88 % | 68 |
| 1.00 | 58.5 | 85 % | 62 |

All three inside the noise band.

## Verdict

- The **drafter gate is the only knob that clearly moves decode**, and it needs a full sweep to
  pin down — single runs mislead (the confirmation is experiment 05).
- **The sampler trims are flat on Strata.** Unlike llama.cpp, there is no trap: 54.2–61.6 tok/s
  across the whole base grid. The absence of a trap is itself the finding.
- Sampled arms sit ~5–8 % under the greedy runs (drafts are argmax proposals verified against a
  sampled target) — `--coupled-draft` is the lever for that gap (tested in experiment 05).

## Caveats

- **One measured run per arm.** Differences under ~5 % are noise at this depth; the stage A 100k
  ordering spans 11 % and is the only pattern claimed as real here.
- Generation lengths vary (31–83 tokens, early stop) — part of the spread.
- All numbers are temperature 0.5, sampling on.

Raw: [`strata-sampler-sweep-base.jsonl`](../data/raw/strata-sampler-sweep-base.jsonl) +
[`.out`](../data/raw/strata-sampler-sweep-base.out) +
[driver](../data/raw/strata-sampler-sweep-base.py). Table:
[`data/csv/sampler-sweep-base.csv`](../data/csv/sampler-sweep-base.csv).
