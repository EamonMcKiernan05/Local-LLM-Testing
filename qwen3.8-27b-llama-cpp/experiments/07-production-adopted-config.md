# 07 — the adopted configuration, measured in production

**2026-09-23 22:40-22:46. Build `b11041`. `Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf`, 2 cards, tensor split `1,1`, ctx 204800, q8_0 KV, MTP `n-max 7`, temp 0.5, no sampler flags. Live systemd service (pid 10028), one real agent request.**

## What happened

The service was restarted with the winning sweep configuration at 22:37:19. Three minutes later a real agent request arrived carrying **103,726 tokens of prompt** and the box had to prefill all of it cold: the restarts had thrown away the slot KV cache, so nothing was reused.

This is the most useful measurement in the repo because it is the configuration doing its actual job — a huge prompt, a warm-but-empty cache, and a long generation — with no harness and no fixed prompt.

## Cold prefill: 511-536 tok/s

| logged at | prompt tokens processed | progress | elapsed | prefill tok/s |
|---|---|---|---|---|
| 22:40:24 | 87,500 | 0.84 | 163.20 s | 536.14 |
| 22:40:28 | 89,548 | 0.86 | 167.97 s | 533.10 |
| 22:40:33 | 91,596 | 0.88 | 172.79 s | 530.10 |
| 22:40:38 | 93,644 | 0.90 | 177.66 s | 527.09 |
| 22:40:43 | 95,692 | 0.92 | 182.57 s | 524.15 |
| 22:40:48 | 97,740 | 0.94 | 187.51 s | 521.24 |
| 22:40:53 | 99,788 | 0.96 | 192.51 s | 518.36 |
| 22:40:58 | 101,836 | 0.98 | 197.54 s | 515.52 |
| 22:41:02 | 103,466 | 1.00 | 202.17 s | 511.79 |
| 22:41:03 | 103,722 | 1.00 | 202.93 s | 511.12 |

**103,726 tokens in 202.93 seconds — about 3 minutes 23 seconds to first token.** The rate decays smoothly from 536 to 511 tok/s as the prompt gets longer, exactly the shape the depth profile predicts (`experiments/04`) and with no cliff. It also lines up with the sweep's 100k arms, which measured 507-518 tok/s prefill at 99,589 tokens on the same configuration.

This is why the client waiting on the response logged `waiting for stream response (180s, first_chunk)` and then an `APIConnectionError` / HTTP 503 loop with five retries: **the request was not slow, it was bigger than the client's 180-second stream-timeout.** The next call on the same session, with the prompt now cached, was fine.

## Decode: 27.7-32.0 tok/s, settling at 27.7

| tokens generated | decode tok/s |
|---|---|
| 100 | 28.51 |
| 211 | 32.04 |
| 305 | 31.70 |
| 373 | 29.50 |
| 450 | 28.72 |
| 527 | 28.11 |
| 636 | 29.18 |
| 744 | 29.90 |
| 804 | 28.81 |
| 898 | 29.02 |
| 982 | 28.86 |
| 1,092 | 29.45 |
| 1,200 | 29.91 |
| 1,293 | 29.93 |
| 1,381 | 29.86 |
| 8,432 | 27.73 |
| 8,513 | 27.71 |
| 8,602 | 27.72 |
| 8,694 | 27.75 |
| 8,785 | 27.76 |
| 8,883 | 27.80 |

Mean over the series **29.05 tok/s**, range 27.71-32.04. The early samples (28.5-32.0) are the warm-up; from 8,400 tokens onward the rate sits in a very tight 27.71-27.80 band, and that plateau — **about 27.8 tok/s** — is the honest sustained figure for this configuration on a request this deep.

Note this is *below* the 43 tok/s the sweeps measured at 100k depth, and the difference is workload, not configuration: the sweep measured a 256-token generation after a prompt that was already in the cache, on a single fixed prompt. Here the request generated 8,883 tokens in one go, at temp 0.5 with real content, with all 103,726 prompt tokens in the KV cache being re-read on every step.

## Data

- `data/csv/live-service-2026-09-23-prefill-progress.csv` — the ten prefill samples above
- `data/csv/live-service-2026-09-23-decode-series.csv` — 21 decode samples from the same request

Both files are extracted directly from the journal text preserved in the session that diagnosed the incident; the extraction script is `scripts/build_session_evidence.py`.
