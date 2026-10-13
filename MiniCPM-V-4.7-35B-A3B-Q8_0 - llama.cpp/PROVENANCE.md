# Provenance: where every file here came from

Collected 2026-10-13. The rule for this folder: **a number appears here only if it came off a
real run, and every table says which run.** All measurements are of MiniCPM-V 4.7 35B-A3B
(Q8_0) on llama.cpp build b11580, box .5 (2× Tesla V100 32 GB).

## Sources

1. **The raw per-arm records** — written by the benchmark harness itself (model-bench on box .5),
   one JSON object per arm at the moment the arm finished:
   - `model-bench-minicpmv47-q8-results.jsonl` — layer-split run, 7 rows: 1 discarded warm-up + 6 measured depth arms.
   - `model-bench-minicpmv47-q8-meta.json` — that run's endpoint / battery / host record.
   - `model-bench-minicpmv47-q8-tensor-results.jsonl` — tensor-split run, same shape (7 rows).
   - `model-bench-minicpmv47-q8-tensor-meta.json` — that run's record.
   All four are byte-identical copies of the run directories on the box
   (`~/model-bench/runs/2026-10-13T0645Z-minicpmv47-35b-a3b-q8-0-llamacpp/` and
   `…2026-10-13T0920Z-minicpmv47-35b-a3b-q8-0-llamacpp-tensor/`), sha256 checked against the box
   after the pull.
2. **The engine's own per-request lines** — `llama-server-request-extracts.txt` and
   `llama-server-tensor-request-extracts.txt`, extracted from the two server logs on box .5 (the
   full logs stay on the box). Each depth arm's final `progress = 1.00`, `prompt eval time` and
   `eval time` lines, verbatim.
3. **The vision smoke test** — `vision-smoke-v47.json`: one image request against the layer-split
   server, same session, raw response including timings.
4. **The serving commands** — `serve-command.txt` (layer split, the default) and
   `serve-command-tensor.txt` (tensor split): exact argv and environment per run.

## sha256

| file | sha256 |
|---|---|
| `model-bench-minicpmv47-q8-results.jsonl` | `6216502217175f6272c8800f39b9f8590b016a2fc762f22554db1e65e7256e7b` |
| `model-bench-minicpmv47-q8-meta.json` | `2e782d1897a8bf40e4e7908d1fe64341d34e15c3a58aff1e693257b525e408f7` |
| `model-bench-minicpmv47-q8-tensor-results.jsonl` | `f2701aa787ac7a002ff3c6f4652d6d80bf34f257795727cbe5bf1d7bed544498` |
| `model-bench-minicpmv47-q8-tensor-meta.json` | `6d4632569e80093e30fb30d2b560aae64780871a5f748d8ee4ac3941d4799599` |
| `vision-smoke-v47.json` | `65040221e97500cc9432e408b3842ba5e6694e94865c19402fb0204f9def4541` |
| model file `MiniCPM-V-4_7-35B-A3B-Q8_0.gguf` | `8543ee5b0f83152066f2fec58b8d9757d56bb7c4233b4fdd26ae364f0107d16b` (verified vs HF metadata) |
| `mmproj-model-f16.gguf` | `bff3b688e14c300eca273092c37c50a0ddfcc2054e079af1a0480edeed5d20f1` (verified vs HF metadata) |

## Counting the runs

**12 measured runs, 0 failures, plus two discarded warm-ups (not counted).** Two bench runs
(2026-10-13T0645Z layer split; 2026-10-13T0920Z tensor split), six depths each
(20k / 60k / 100k / 150k / 200k / 250k), one run per depth, temp 0.5, seed 12345, 400 generated
tokens each, unique tag per request, prompt slicing exact (the harness sliced with the model's
own GGUF tokenizer). The two runs' prompts are identical at every depth — the data builder
asserts the prompt-token counts match before it will write the comparison CSV.

Warm-up requests were discarded by design and stay visible in the raw files as the
`"kind": "warmup"` rows. They are not counted.

## Not included, and why

- **No MTP arm** — the official GGUF carries no nextn/MTP tensors (the 733-tensor file was
  checked directly), and the source checkpoint's safetensors index has 0 of 1,152 MTP keys. There
  is no in-model drafter for this model to measure. The DSpark drafter is a separate release;
  side-model tests are out of scope for this batch.
- **The removed row-split mode** — `-sm row` was tried first and aborts at load on this build
  (`device CUDA0 does not support split buffers`); upstream removed CUDA row split in
  `74976e1ae`. That attempt produced no data; the tensor-mode run above is the working
  tensor-split implementation. (A `-sm tensor` attempt at this level of detail is in
  `experiments/02-split-mode-2026-10-13.md`.)
- **An earlier run the same morning** — aborted by a harness bug: the backend detector read the
  new llama.cpp `/v1/models` format (which now emits `architecture` on its items) as "Strata" and
  sent the battery through the chat endpoint instead of `/completion`. The harness was fixed, that
  run discarded, and the battery re-run clean. Its directory remains on the box marked
  `-ABORTED-chat-endpoint-misdetect`; none of its numbers are used anywhere here.
