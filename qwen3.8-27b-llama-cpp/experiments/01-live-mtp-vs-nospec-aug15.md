# 01 — MTP against no MTP, measured on live fleet traffic

**2026-08-14 / 15. Build `b10068`. `Qwen3.8-27B-UD-Q4_K_XL.gguf`, 3 cards, layer split `35,37,28`, ctx 262144, q8_0 KV. Live systemd service, no sweep.**

## Why this one is different

Every other experiment in this repo used a throwaway server and one fixed prompt. This one measured the **service that was already serving**, under real agent traffic: 23.4 million generated tokens of it. That makes the numbers representative of the box's actual workload, and it is also why they are lower than the benchmark figures elsewhere in this repo — real traffic is long-prompt, mixed-temperature and mostly cache-hostile.

## Headline

| config | decode | acceptance | note |
|---|---|---|---|
| no MTP (PID 215819) | **17.3 tok/s** | — | weighted over 126,000 tokens |
| llama-bench, single request | 17.57 tok/s | — | `n_decoded = 100, tg = 17.57` |
| MTP `n-max 8 --spec-draft-p-min 0.85`, first test (PID 228363) | 38.8 tok/s | 0.83792, mean len 5.37 | short burst, not sustained |
| MTP `n-max 8 --spec-draft-p-min 0.85`, sustained (PID 230701) | **24.5 tok/s** | **0.8708** (176,446 / 202,620) | weighted over 23.4M tokens |

On this traffic the MTP head is worth **+42%** on sustained decode (17.3 → 24.5 tok/s). Short bursts reach 28-39 tok/s; long-context requests fall to 14-16 tok/s.

Per-task acceptance has a median of 0.884 and a range of 0.70 to 1.00. Mean draft length is only **4.46 of the 8 allowed** — because the `p-min 0.85` gate stops drafting early whenever the head is unsure.

## What was asked, and what the logs actually said

The starting assumption was "18 tok/s baseline, 32 tok/s with MTP n-max 8, acceptance about 0.6". Two of the three were off, and in opposite directions:

- **Acceptance is 0.87, not 0.6.** The 0.85 gate raises acceptance and shortens drafts. 0.6 is roughly what you would see *ungated* at n-max 8.
- **Sustained speed is 24.5, not 32.** 32 tok/s was reachable in bursts only.
- **n-max 8 was past the sweet spot.** The 100k sweeps run a month later (`experiments/06`) put the peak at `n-max 7`, and subsequent 20k work showed the peak moving down to `n-max 2` at shallow depth. n-max 8 proposes the most tokens per round and converts the smallest share of them.

## Data

- `data/csv/live-service-summary.csv` — the four configurations above, with provenance
- `data/csv/live-traffic-draft-acceptance-aug14-15.csv` — 28 per-request journal lines captured in the same window (timestamp, PID, acceptance rate, accepted/generated, mean draft length)
