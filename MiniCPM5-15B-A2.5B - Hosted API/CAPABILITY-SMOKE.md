# Capability smoke run — gBench evals against MiniCPM5-15B-A2.5B

**7 suites scored, 21 blocked, 2026-11-24.** A first pass at the 28 suites gBench's preflight
considered runnable, at smoke scale (3–20 samples per suite, `--max-output-tokens 2048–8192`,
temperature 0.0, thinking off). These are **not** leaderboard numbers: the sample counts are far
below each suite's own, and several suites could not run at all against this endpoint.

## Scored

| suite | score | correct / scored | notes |
|---|---:|---:|---|
| gsm8k | **75.00%** | 15 / 20 | 8-shot CoT, no truncation, no empty replies |
| ifeval | **80.00%** | 8 / 10 | prompt-level strict accuracy |
| nexusraven_api_eval | **75.00%** | 3 / 4 | tool-calling |
| seal_tools | **93.33%** | 2 / 4 | composite check score, not sample accuracy |
| multilingual_mmlu | **55.00%** | 11 / 20 | 14-language MMMLU |
| causalbench | **0.00%** | 0 / 20 | Corr2Cause F1 of the valid class; 20 replies, none truncated, none empty, all scored invalid |
| arc_agi | **0.00%** | 0 / 4 | four public ARC-AGI-1 tasks — **6 replies were truncated at the 2,048-token cap**, so this zero is contaminated and needs a re-run with a bigger budget |

## Blocked, and why

**Blocked by the endpoint itself** (nothing to install):

| suite | reason |
|---|---|
| mmlu, mmlu_redux, wmdp | these read answer letters from `/v1/completions` log-probabilities; the endpoint does not serve `/v1/completions` at all (404) |
| mmlu_pro | the endpoint rejected the request its own client sends (HTTP 400) |
| longbench_v2_code | the served `/v1/models` reports no context window, and the suite sizes prompts from it |
| bundled_detection | sends document images — this model has no image input ("该模型不支持图片输入") |

**Blocked by gated data or missing checkouts** (fixable with accounts and clones):

| suite | what it needs |
|---|---|
| gpqa, gpqa_diamond | `Idavidrein/gpqa` is gated: an HF token with the licence accepted on the dataset page |
| codeforces | the `generated_tests` mirror (official tests alone are ~9.7% coverage) |
| bfcl_live | BFCL's own harness image |
| i18n_translate | WMT19 test sets + sacrebleu |
| nestful | IBM/NESTFUL checkout |
| scicode | SciCode's data reader |
| t_eval | sentence-transformers + networkx (pulls torch) |
| cyberseceval | Docker (semgrep scorer image) |
| ruler | now has the pinned NVIDIA/RULER checkout; its per-tokenizer data generation had not run yet |

**Not finished at smoke scale** — these generate long code/maths per sample and exceeded a
3-minute-per-suite budget at 4 samples: `amc_aime`, `cruxeval`, `lcb`, `loft_scifact`.
**Excluded up front**: `lab_bench` (FigQA/TableQA are image inputs).

## What this says about the model

Not much yet, and that is the honest answer. The two suites with 20 samples put it at 75% (GSM8K)
and 55% (multilingual MMLU); IFEval at 10 samples is 80%. Its tool-calling suites score 75% and
93% on four samples each, which is far too few to conclude anything. Corr2Cause and ARC-AGI at
Corr2Cause at zero is a clean zero (nothing truncated or empty). ARC-AGI's zero is not: six of its replies were
cut off at the token cap, so it must be re-run before it means anything.

To make these publishable numbers rather than a smoke test: accept the gated licences, clone the
three checkouts, add Docker access, and run each suite at its own full sample count. On this
endpoint the log-probability suites (MMLU, WMDP) will still be impossible — that needs a provider
that serves `/v1/completions`, or a served copy of the model you control.

Raw logs: `~/evals_<suite>.log` on the Hermes host; gBench result JSONs under
`~/results/<timestamp>/eval_<suite>_*.json`.
