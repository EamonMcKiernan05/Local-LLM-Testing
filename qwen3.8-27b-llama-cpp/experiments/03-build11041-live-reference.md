# 03 — live-service reference straight after the `b11041` rebuild

**2026-09-18 ~20:35. Build `b11041`. `Qwen3.8-27B-UD-Q4_K_XL.gguf`, 3 cards, layer split `35,37,28`, ctx 262144, q8_0 KV, MTP `n-max 8`, temp 0.6. Live service (pid 206666), not a throwaway server.**

## Result

| run | prompt tokens | prefill tok/s | prefill ms | gen tok/s | gen ms | draft acceptance | mean len |
|---|---|---|---|---|---|---|---|
| 1 | 19,966 | 850.22 | 23,483 | 32.95 | 7,739 | 98.2% (160/163) | 3.08 |
| 2 | 19,966 | 853.63 | 23,389 | 28.30 | 9,012 | 94.8% (181/191) | 3.59 |

Prompt was 62,235 characters, counted at 19,966 tokens via `/tokenize`. `cache_prompt: false` and a unique random prompt each run, so every run paid full prefill. One warm-up request discarded.

**Time to first token at 20k depth: about 23.4-23.5 seconds.** `-ub 256` means roughly 78 micro-batches.

## The interesting bit: the generation spread is MTP, not the build

32.95 against 28.30 tok/s looks like a 16% variance problem. It is not. Divide each run's generation time by the number of decode steps implied by its mean accepted length and you get **108.5 ms and 108.4 ms per decode step** — identical. The whole difference is how often the draft lands:

- run 1: acceptance 3.08 tokens per round → 32.95 tok/s
- run 2: acceptance 3.59 tokens per round → 28.30 tok/s
- ratio 3.59 / 3.08 = 1.166 against a speed ratio of 32.95 / 28.30 = 1.164

So the number to plan around for this model and this box at this context length is **about 30 tok/s generation and 850 tok/s prefill at 20k depth**.

## What this is not

There is **no before/after comparison against the previous build** (`b10068`). The old binary was never benchmarked with this harness, so nothing here is a regression claim. To get one, build the July commit into a separate directory and re-run the same script.

## Data

`data/csv/live-service-build11041-20k.csv`
