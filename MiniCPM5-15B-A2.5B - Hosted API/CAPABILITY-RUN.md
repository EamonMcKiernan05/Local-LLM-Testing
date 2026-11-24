# Capability run — gBench evals against MiniCPM5-15B-A2.5B

**11 suites scored, 17 blocked, 1 still running.** gBench 0.5.0.post1, thinking off, temperature
0.0, `--max-output-tokens 16384`, 8 concurrent requests, run against the hosted
OpenAI-compatible endpoint on 2026-11-24. Sample counts are small by design (10–200 per suite) —
this is a first honest reading, not a leaderboard entry.

## Scored

| suite | score | counts | notes |
|---|---:|---|---|
| IFEval | **80.0%** | 8 / 10 prompts | |
| AMC / AIME | **80.0%\*** | 16 / 20 correct | \* the harness prints 100% — it scores only the 16 that answered; 4 requests never returned |
| Seal-Tools | **76.3%** | 7 / 20 tasks | composite check score |
| GSM8K | **75.0%** | 15 / 20 | clean: no truncation, no empty replies |
| NexusRaven (tools) | **60.4%** | 13 / 20 | tool-calling |
| CRUXEval | **55.0%** | 110 / 200 | 30 replies cut off at the 16K cap |
| Multilingual MMLU | **55.0%** | 11 / 20 | 14 languages |
| LoFT (SciFact) | **50.0%** | 10 / 20 | long-context retrieval |
| LiveCodeBench | **48.6%** | 34 / 70 scored | 200 generations, 10 attempts each; 50 truncated |
| ARC-AGI | **18.8%** | 3 / 20 | 42 tasks × 2 attempts; 12 requests never returned |
| CausalBench | **0.0%** | 0 / 20 | clean zero — nothing truncated, nothing empty |

Charts: `charts/minicpm5-eval-scores.png`, `charts/minicpm5-eval-uncertainty.png`,
`charts/minicpm5-eval-blockers.png`.

The confidence intervals matter more than the point estimates: a 20-sample suite at 55% has a 95%
interval of 32–76%. Only CRUXEval (n=200) is pinned down to ±7 points.

## Blocked, and why

| blocker | suites | detail |
|---|---|---|
| Gated data or missing checkout | 9 | GPQA ×2 (`Idavidrein/gpqa` is gated on the Hub), Codeforces (`generated_tests` mirror), BFCL (own harness), i18n (WMT19 + sacrebleu), NESTFUL, SciCode, T-Eval (sentence-transformers + networkx), RULER (per-tokenizer data generation) |
| The endpoint cannot serve it | 5 | MMLU, MMLU-Redux and WMDP read answer letters from `/v1/completions` log-probabilities — that route 404s on this provider; MMLU-Pro's request is rejected with HTTP 400; LongBench-v2 needs a context window that `/v1/models` does not report |
| Model is text-only | 2 | bundled_detection and lab_bench send images; the endpoint answers `该模型不支持图片输入` |
| Needs Docker | 1 | CyberSecEval (semgrep scorer image); the host user lacks Docker access |

`agent_dojo` needed the `agentdojo` package (now installed) and is running past a 20-minute budget
at the time of writing; its score will follow.

## Method

- `gbench --evals-only --evals <suite> --eval-limit 20 --max-output-tokens 16384
  --max-model-len 32768 --eval-concurrency 8`, remote endpoint, tokenizer `openbmb/MiniCPM5-2B`.
- Thinking is **off** for every figure here. The endpoint defaults thinking **on** (a plain
  "Hello" returns 27 reasoning tokens), so `--eval-thinking` runs would move these numbers and have
  not been done.
- `--eval-limit 20` sets samples per suite, but suites that repeat attempts multiply it: CRUXEval
  did 400 generations over 200 scored items, LiveCodeBench 200 generations over 70 scored items,
  ARC-AGI 84 generations over 42 tasks.
- Truncation is counted as failure by gBench; the 16K cap is what CRUXEval's and LiveCodeBench's
  truncated replies hit.
- Log-probability suites (MMLU family, WMDP) can never run against this provider. They need a
  served copy of the model you control, or a provider that exposes `/v1/completions`.

Raw logs: `~/evals_<suite>.log` on the Hermes host; result JSONs under
`~/results/<timestamp>/eval_<suite>_*.json`.
