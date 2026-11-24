# Capability run — gBench evals against MiniCPM5-15B-A2.5B

**19 suites scored, 5 impossible on this endpoint, 3 still to provision.** gBench 0.5.0.post1,
thinking off, temperature 0.0, `--max-output-tokens 16384`, 4–8 concurrent requests, run against the
hosted OpenAI-compatible endpoint on 2026-11-24. Sample counts are deliberately small (10–200 per
suite): this is a first honest reading, not a leaderboard entry.

## Scored

| suite | score | counts | notes |
|---|---:|---|---|
| MMLU-Pro | **90.0%** | 9 / 10 | needed the auth-injecting proxy |
| AMC / AIME | **80.0%\*** | 16 / 20 correct | \* harness prints 100% — it scores only the 16 that answered |
| IFEval | **80.0%** | 8 / 10 | |
| Seal-Tools | **76.3%** | 7 / 20 tasks | composite check score |
| GSM8K | **75.0%** | 15 / 20 | clean |
| BFCL-Live (tools) | **71.4%** | 7 / 10 | ran inside its Docker image |
| GPQA-Diamond | **70.0%** | 140 / 200 attempts | 41 replies hit GPQA's own 2,048-token budget |
| CyberSecEval | **70.0%** | 7 / 10 | semgrep scorer image |
| GPQA | **64.0%** | 128 / 200 attempts | 41 truncated, same cause |
| NexusRaven (tools) | **60.4%** | 13 / 20 | tool-calling |
| CRUXEval | **55.0%** | 110 / 200 | 30 truncated at the 16K cap |
| Multilingual MMLU | **55.0%** | 11 / 20 | 14 languages |
| LoFT (SciFact) | **50.0%** | 10 / 20 | long-context retrieval |
| LiveCodeBench | **48.6%** | 34 / 70 scored | 200 generations, 10 attempts each; 50 truncated |
| AgentDojo | **45.0%** | 9 / 20 | agentic tool use + prompt injection |
| i18n Translate | **20.5%** | 10 samples | chrF-style translation score |
| ARC-AGI | **18.8%** | 3 / 20 | 12 of 42 generations never returned |
| CausalBench | **0.0%** | 0 / 20 | clean zero |
| SciCode | **0.0%** | 0 / 10 | ran, solved nothing |
| T-Eval | **no score** | 0 / 10 correct | suite reports success but yields no aggregate metric |

Charts: `charts/minicpm5-eval-scores.png`, `charts/minicpm5-eval-uncertainty.png`,
`charts/minicpm5-eval-losses.png`.

Confidence intervals matter more than the point estimates: a 10-sample suite carries ±14 to ±25
points and a 20-sample suite ±17 to ±20. Only the 200-attempt GPQA runs (±6) and CRUXEval's 200
items (±7) are pinned down. Where a run lost 20–30% of its generations to truncation, the score is a
floor.

## Not scored

| blocker | suites | detail |
|---|---|---|
| Endpoint has no `/v1/completions` | 3 | MMLU, MMLU-Redux and WMDP read answer letters from top-100 log-probabilities on that route, which this provider does not serve. The 15B weights are not public (`openbmb/MiniCPM5-15B-A2.5B` returns 401), so self-hosting is not an option either |
| Model is text-only | 2 | bundled_detection and lab_bench send images; the endpoint answers `该模型不支持图片输入` |
| Needs a large mirror | 1 | Codeforces needs `GBENCH_CODEFORCES_GENERATED_TESTS` (official tests alone are 9.7% coverage) |
| Needs a checkout | 1 | NESTFUL needs `GBENCH_NESTFUL_FUNC_DIR` + `GBENCH_PREREQS_DIR` |
| Needs data generation | 1 | RULER is cloned at `c3f5e3b` but its per-tokenizer synthetic data has not been built |

LongBench-v2-code was blocked on a missing context window in `/v1/models`;
`GBENCH_LONGBENCH_V2_CODE_WINDOW=131072` supplies it and that run is in progress.

## Method notes (the traps)

- `--max-output-tokens` is mandatory for gBench evals — truncation reads as a failure, so the cap is
  part of the measurement. It was 16384 here.
- `--eval-concurrency` defaults to **1**. Every early run was single-stream at ~180 tok/s; at 8 the
  same suites finish in minutes.
- `--eval-limit` counts samples, but suites repeat attempts: GPQA 20 samples × 10 attempts = 200
  generations, CRUXEval 400, LiveCodeBench 200, ARC-AGI 84.
- gBench's vendored MMLU-Pro deletes the `Authorization` header (fine for local vLLM, fatal for a
  keyed API). A local proxy on `127.0.0.1:8099` re-adds it; point gbench at
  `--remote-endpoint http://127.0.0.1:8099/v1`.
- Docker suites need the docker group **and** a process started with it:
  `sg docker -c '<gbench …>'`. The gbench wheel does not ship `gbench/docker/*.Dockerfile`, so images
  are built from a clone of `google-deepmind/gbench`; the BFCL build needed its `bfcl-eval` wheel
  pre-downloaded on the host (SHA pinned to `3bb6dfa5…`).
- GPQA needs the dataset licence accepted **and** `HF_TOKEN` exported into gbench's environment.
- The endpoint reports `context_window: 512000` in `/v1/models` — the 512K figure is confirmed, not
  assumed.
- Thinking is **off** for every figure here; the endpoint defaults it **on** (a plain "Hello" returns
  27 reasoning tokens), so `--eval-thinking` runs would move these numbers and have not been done.

Raw logs: `~/evals_<suite>.log` on the Hermes host; result JSONs under
`~/results/<timestamp>/eval_<suite>_*.json`.
