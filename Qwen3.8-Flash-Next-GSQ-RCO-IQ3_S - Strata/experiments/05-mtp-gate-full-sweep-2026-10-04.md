# 05 — The full drafter sweep: 126 runs across six depths (2026-10-04)

The proper confirmation of the 0.5-vs-0.85 drafter-gate question, plus the two untested engine
flags, measured at all six depths on the base IQ3_S (both cards, 262K context, pack + shard 1 +
n-gram on NVMe). **126 runs, zero errors.**

Method: a chained master driver on the box. Gate and sampler arms are per-request (one HTTP
call each); suffix-draft and coupled-draft are engine flags, so they cost one restart per value
(~2.5 min each). Sampling baseline: temperature 0.5, seed 12345, top_k 20 / top_p 0.95 /
min_p 0.0; 400-token generations; prompts are slices of one document, unique tag per run.

## Stage A — drafter gate `spec_min_p` × depth — decode tok/s

| gate | 20k | 60k | 100k | 150k | 200k | 250k | mean |
|---|---|---|---|---|---|---|---|
| 0.00 | 58.3 | 52.1 | 52.9 | 47.2 | 44.2 | 47.3 | 50.3 |
| 0.50 | 67.2 | 60.1 | 53.9 | 56.6 | 53.0 | 50.2 | **56.8** |
| 0.60 | 56.3 | 56.1 | 54.4 | 53.7 | 52.2 | 49.5 | 53.7 |
| 0.85 | 63.1 | 51.9 | 55.8 | 48.3 | 55.3 | 45.4 | 53.3 |

**Winner: gate 0.50** — best at 4 of 6 depths, and the 0.5-vs-0.85 question is settled. The
earlier single-run "0.85 best at 100k" did not generalise: 0.85 only edges 0.50 at 100k and
200k, both by ~2 tok/s, inside single-cell noise. The driver wrote 0.50 to the model config as
its default at the end of the sweep.

## Stage S — suffix-draft — decode tok/s (gate 0.50)

| `--suffix-draft` | 20k | 60k | 100k | 150k | 200k | 250k | mean |
|---|---|---|---|---|---|---|---|
| 0 (off) | 57.0 | 57.8 | 53.1 | 52.1 | 48.4 | 44.4 | 52.1 |
| 3 (default) | 67.2 | 60.1 | 53.9 | 56.6 | 53.0 | 50.2 | **56.8** |
| 8 (aggressive) | 54.4 | 60.0 | 52.3 | 52.1 | 50.8 | 48.3 | 53.0 |

Keep the default (3): both alternatives lose on the mean and neither beats it at any depth
(8 ties at 60k). Caveat: the source document is highly repetitive, which flatters prompt-lookup
drafting vs ordinary text.

## Stage C — coupled-draft — decode tok/s (gate 0.50)

| `--coupled-draft` | 20k | 60k | 100k | 150k | 200k | 250k | mean |
|---|---|---|---|---|---|---|---|
| off (default) | 67.2 | 60.1 | 53.9 | 56.6 | 53.0 | 50.2 | **56.8** |
| on | 51.1 | 59.3 | 55.0 | 56.0 | 48.6 | 49.7 | 53.3 |

Keep coupled off: it loses 3.5 tok/s on the mean; only 100k gains (+1.1), 20k drops 16.1.

## Stage B — sampler trims (gate 0.50) — decode tok/s bands across the 14 arms

| depth | min–max (tok/s) |
|---|---|
| 20k | 55.1–66.6 |
| 60k | 54.0–66.4 |
| 100k | 52.7–59.2 |
| 150k | 47.9–57.1 |
| 200k | 46.2–55.2 |
| 250k | 45.5–55.3 |

Flat, exactly as experiment 03 found: no sampler setting separates cleanly — the pre-depth
bands are 6.5–12.4 tok/s wide, the ordering reshuffles at every depth, and near-identical
`top_p` repeats differ by up to ~7 tok/s on their own. Best cell by depth-mean:
`top_k 50 / min_p 0.10` (57.6), with the next three cells 56.0–56.3 — treat as tied.

## Prefill

Flat across everything, as it always is on this box: every stage's 250K-token prefill sits
within **1,493.6–1,498.3 tok/s** (stage means 1,495–1,498).

## Verdict

Gate **0.50** confirmed and set as the config default. Keep `--suffix-draft` at its default 3
and `--coupled-draft` off — both alternatives measurably lose. Sampler grid flat; no changes.
At 250K: ~50 tok/s decode / ~1,498 tok/s prefill on this configuration.

Raw: [`strata-mtp-sweep-all-arms.jsonl`](../data/raw/strata-mtp-sweep-all-arms.jsonl) +
[driver](../data/raw/strata-mtp-sweep.py) + [master
driver](../data/raw/strata-mtp-sweep-master.sh) + [winner
file](../data/raw/strata-mtp-sweep-winner.txt) + [stdout log](../data/raw/strata-mtp-sweep.out).
Tables: [`mtp-sweep-all-arms.csv`](../data/csv/mtp-sweep-all-arms.csv), the per-stage files in
[`data/csv/`](../data/csv/), and [`mtp-sweep-summary.csv`](../data/csv/mtp-sweep-summary.csv)
for the means and bands quoted above.
