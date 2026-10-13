# Provenance: where every file here came from

Collected 2026-10-13. The rule for this folder: **a number appears here only if it came off a
real run, and every table says which run.** All measurements are of MiniCPM-V 4.7 35B-A3B
(Q8_0) on llama.cpp build b11580, box .5 (2× Tesla V100 32 GB).

## Sources

1. **The raw per-arm record** — written by the benchmark harness itself (model-bench on box .5),
   one JSON object per arm at the moment the arm finished:
   - `model-bench-minicpmv47-q8-results.jsonl` — 7 rows: 1 discarded warm-up + 6 measured depth arms.
   - `model-bench-minicpmv47-q8-meta.json` — the run's endpoint / battery / host record.
   Both are byte-identical copies of the run directory on the box
   (`~/model-bench/runs/2026-10-13T0645Z-minicpmv47-35b-a3b-q8-0-llamacpp/`), sha256 checked
   against the box after the pull.
2. **The engine's own per-request lines** — `llama-server-request-extracts.txt`, extracted from
   `/home/eamon/llama-server-v47-bench.log` on box .5 (the full log stays on the box). Each depth
   arm's final `progress = 1.00`, `prompt eval time` and `eval time` lines, verbatim.
3. **The vision smoke test** — `vision-smoke-v47.json`: one image request against the same server,
   same session, raw response including timings.
4. **The serving command** — `serve-command.txt`: the exact argv and environment the bench server ran.

## sha256

| file | sha256 |
|---|---|
| `model-bench-minicpmv47-q8-results.jsonl` | `6216502217175f6272c8800f39b9f8590b016a2fc762f22554db1e65e7256e7b` |
| `model-bench-minicpmv47-q8-meta.json` | `2e782d1897a8bf40e4e7908d1fe64341d34e15c3a58aff1e693257b525e408f7` |
| `vision-smoke-v47.json` | `65040221e97500cc9432e408b3842ba5e6694e94865c19402fb0204f9def4541` |
| model file `MiniCPM-V-4_7-35B-A3B-Q8_0.gguf` | `8543ee5b0f83152066f2fec58b8d9757d56bb7c4233b4fdd26ae364f0107d16b` (verified vs HF metadata) |
| `mmproj-model-f16.gguf` | `bff3b688e14c300eca273092c37c50a0ddfcc2054e079af1a0480edeed5d20f1` (verified vs HF metadata) |

## Counting the runs

**6 measured runs, 0 failures, plus one discarded warm-up (not counted).** One bench run
(2026-10-13T0645Z), six depths (20k / 60k / 100k / 150k / 200k / 250k), one run per depth,
temp 0.5, seed 12345, 400 generated tokens each, unique tag per request, prompt slicing exact
(the harness sliced with the model's own GGUF tokenizer).

Warm-up requests were discarded by design and stay visible in the raw file as the
`"kind": "warmup"` row. They are not counted.

## Not included, and why

- **No MTP arm** — the official GGUF carries no nextn/MTP tensors (the 733-tensor file was
  checked directly), so there is no in-model drafter to measure. The DSpark drafter is a separate
  model; side-model tests are out of scope for this batch.
- **An earlier run the same morning** — aborted by a harness bug: the backend detector read the
  new llama.cpp `/v1/models` format (which now emits `architecture` on its items) as "Strata" and
  sent the battery through the chat endpoint instead of `/completion`. The harness was fixed, that
  run discarded, and the battery re-run clean. Its directory remains on the box marked
  `-ABORTED-chat-endpoint-misdetect`; none of its numbers are used anywhere here.
