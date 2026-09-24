# 08 — the `buun-llama-cpp` fork (spiritbuun)

**2026-09-19/20. Same box, same three cards, same harness as `experiments/02`. Build: llama.cpp fork `github.com/spiritbuun/buun-llama-cpp`, same Sep-2026 vintage as stock `b11041`, built with CUDA 13.3 for sm86 using `-DGGML_CUDA=ON -DGGML_CUDA_FA=ON -DGGML_CUDA_FA_ALL_QUANTS=ON` (all-quants FA is needed for the fork's KV codecs; build time ~65 minutes on this box's Xeon).**

## Verdict

**A net regression on this box.** Twice as slow at prompt processing and 8-10% slower at decode with identical flags, and none of its KV codecs buy that back at 32k context. One exception: its `turbo4` KV codec decodes 25% faster than stock's q8_0 at 100k depth, and only when the prompt is already cached.

## What the fork adds

A research fork whose headline features are KV-cache codecs: dynamic VBR (variable bit-rate cache that degrades layer by layer from f16 down a ladder), TurboQuant scalar codecs (turbo8/4/3/2), TCQ trellis-coded variants, plus vLLM FLA kernels for GDN layers embedded as sm80/sm86/sm120 cubins, native safetensors loading, and an EXL3 quant format. Flash attention is required and force-enabled.

**One source patch was needed to build it:** `ggml/src/ggml-cuda/gated_delta_net_fla_ptx.cu` declares its embedded cubin symbols inside an unnamed namespace, and nvcc 13.3 gives those internal linkage — all 18 declarations fail with "declared with a never-completed type". Moving the `extern "C"` block to global scope fixes the build.

## The sweep

Identical harness to the stock DFlash2 bake-off: llama-server, 19,966-token prompt, 256 generated, temp 0.8, fixed seed, `cache_prompt: false`, ctx 32,768, layer split, `-ts 35,37,28`, `-ub 256`, flash attention on, q8_0 KV unless noted. Stock llama.cpp was re-run the same day for a like-for-like control (the A-arms). Target is the same `Qwen3.8-27B-UD-Q4_K_XL.gguf` for the A/B/C/D/E arms; the F/G arms use the EXL3 safetensors directory.

| config | prefill tok/s | decode tok/s | note |
|---|---|---|---|
| A1 stock + MTP n4 | 868.3 | 27.49 | control |
| A2 stock + DFlash2 Q4_K_M n4 | 810.3 | 31.36 | control |
| A3 stock, no speculation | 1096.8 | 15.72 | control |
| B1 buun + MTP n4 | 439.6 | 25.33 | same flags as A1 |
| B2 buun + DFlash2 n4 | 435.1 | 27.88 | same flags as A2 |
| B3 buun, no speculation | 463.8 | 14.08 | same flags as A3 |
| C1 buun VBR default + MTP | 446.3 | 28.53 | |
| C2 buun VBR default + DFlash2 | 438.5 | 28.35 | |
| C3 buun VBR entry t8 + DFlash2 | 421.7 | 25.12 | |
| D1 buun turbo4 + DFlash2 | 431.4 | 25.34 | |
| D2 buun turbo3_tcq + DFlash2 | 326.6 | 23.45 | TCQ costs prefill, as documented |
| D3 buun turbo2_tcq + DFlash2 | 414.1 | 25.55 | |
| D4 buun turbo4 + MTP | 434.4 | 26.22 | |
| E1 buun turbo4 + DFlash2 n2 | 432.2 | 25.85 | |
| E2 buun turbo4 + DFlash2 n6 | 431.8 | 25.70 | |
| F1 buun EXL3, no speculation | 320.9 | 15.84 | EXL3 safetensors dir |
| F2 buun EXL3 + MTP n4 | 308.8 | 29.82 | |
| F3 buun EXL3 + DFlash2 (GGUF draft) n4 | 307.4 | 28.12 | |
| F4 buun EXL3 + DFlash2 (EXL3 draft dir) n4 | 307.3 | 31.55 | EXL3 draft works too |
| F5 buun EXL3 + VBR + DFlash2 n4 | 308.8 | 31.63 | |
| F6 buun EXL3 + turbo4 + DFlash2 n4 | 302.5 | 28.54 | |
| F7 buun EXL3 + turbo3_tcq + DFlash2 n4 | 247.0 | 26.54 | |
| F8 buun EXL3 + VBR + MTP n4 | 312.9 | 32.58 | |
| G1 buun EXL3 + turbo4 + MTP n2 | 306.8 | 32.88 | |
| G2 buun EXL3 + turbo4 + MTP n6 | 306.4 | **35.12** | best decode of the whole fork sweep |

## Findings

1. **With identical flags the fork is ~2x slower at prompt processing than stock** (GGUF target: 440 against 868 tok/s with MTP) and 8-10% slower at decode. Its KV codecs do not close the gap: VBR, turbo4 and turbo2_tcq land within noise of q8_0; turbo3_tcq loses a further 25% of prefill. **Nothing in the fork sweep beat stock llama.cpp on this box.**
2. **The gap is not the kernels.** A clean llama-bench A/B (same model, same flags, no server) shows the two builds are effectively equal: pp128 496 vs 478, pp512 790 vs 760, pp2048 1046 vs 1057, tg128 18.0 vs 18.5 tok/s. So the fork's CUDA kernels are fine; the regression lives in its server path.
3. **The fork's server processes prompts on essentially one GPU.** Sampling `nvidia-smi` during an identical 2,045-token prefill: stock spreads the work across all three cards (mean utilisation 56/41/51%), while the fork pins GPU0 (48%) and leaves GPU1/GPU2 at 6% and 8%. Reducing the prompt to 2,048 or 8,192 tokens does not change the ratio (485-488 tok/s at both), so it is a constant per-token server-side cost, not a long-prompt or chunking issue.
4. **Ruled out as causes:** context checkpoints (`--ctx-checkpoints 0` does remove them — 0 against 2 created — but prefill is unchanged), the idle-slot/host-cache machinery (`--no-cache-idle-slots`), ubatch size, and KV codec choice. Layer placement is even (24/24/18 across the three cards), KV buffer sizes match q8_0 expectations (408/408/272 MiB at 32k), and VBR is inert with pinned q8_0.
5. **EXL3 in the fork works** — the native safetensors loader takes the EXL3 directory directly, resolves the quantization config, and both drafter paths function: built-in MTP (29.8 tok/s at n4) and DFlash2, whether the draft is the GGUF sidecar (28.1) or the EXL3-format draft directory (31.6). Its prefill, however, is much worse than the GGUF target in the same binary (307 against 435 tok/s), consistent with EXL3 being repacked/dequantised for the prefill GEMMs.
6. **Best fork configuration found: EXL3 target + turbo4 KV + MTP, n-max 6** — 35.12 tok/s decode, the fastest decode measured in the fork sweep, with 306 tok/s prefill. It beats the fork's own GGUF configs on decode but is far behind the stock GGUF + MTP combination on prefill (868).

## Where the fork's prefill time actually goes

Same binary, three harnesses (GGUF target, q8_0 KV, ~2,045-token prompt):

| harness / setting | stock | buun fork |
|---|---|---|
| llama-bench pp2048, `-ub 256` | 1046 | 1056 |
| llama-bench pp2048, `-ub 2048` | not run | 637 |
| llama-server, `-ub 256` | 866 | 488 |
| llama-server, `-b 256 -ub 256` | — | 488 |
| llama-server, `-b 512 -ub 512` | — | 539 |
| llama-server, `-b 2048 -ub 256` | — | 489 |

Three separate effects, in order of size:

1. **The fork's kernels slow down with large chunks.** Same build, same prompt: 1,056 tok/s at `-ub 256` against 637 tok/s at `-ub 2048` (−40%). Its vLLM FLA-GDN kernels (512+ token chunks) and whatever tiling it uses at large ubatch are evidently tuned for small chunks.
2. **The fork's server ignores small ubatches on the prompt path.** Its own verbose log shows a 2,045-token prompt submitted as one giant ubatch — `verify ubatch: 1785 tok, 3035.6 ms (1.70 ms/tok)` — and passing `-b 256 -ub 256` does not change the measured rate (488 tok/s either way). That is the −40% kernel penalty above, applied to every prompt.
3. **The remainder is server-side scheduling.** At the same 2,048-token prompt the fork also runs 2 context checkpoints (~0.5 s each, ~25% of its prompt time), and nvidia-smi sampling shows GPU0 pinned at ~48% while GPU1/GPU2 sit at 6-8%.

## Long context: where a fork codec finally wins

131,072-token cache, 99,708-token prompt:

| config | prefill tok/s | decode tok/s at 100k depth |
|---|---|---|
| stock llama.cpp, q8_0 KV | **840.0** | 10.41 |
| buun fork, q8_0 KV | 337.0 | 7.50 |
| buun fork, turbo4 KV | 314.6 | **13.05** |

The fork is 2.5x slower to prefill a 100k prompt, but its `turbo4` codec (4.125 bpv against q8_0's 8.5) is **25% faster to decode at 100k depth** than stock's q8_0 — the one configuration in this whole exercise where a buun-specific feature wins on this hardware. Within the fork the effect is larger still: 7.50 → 13.05 tok/s (+74%) swapping q8_0 for turbo4 at the same depth. **The catch is that the win only materialises after the prompt is in the cache:** the same 100k-token prompt costs 5.0 minutes to ingest in the fork against 2.0 minutes in stock, so any workload that re-prefills loses more than it gains.

## Drafter quantisation in the fork

All three DFlash2 quants, n=4, temp 0.8, same harness:

| config | prefill tok/s | decode tok/s |
|---|---|---|
| stock + DFlash2 Q8_0 | 822.5 | 29.44 |
| buun + DFlash2 Q8_0 | 442.4 | 32.42 |
| stock + DFlash2 BF16 | 810.7 | 27.92 |
| buun + DFlash2 BF16 | 436.8 | 10.69 |

The prefill picture is identical across every drafter quant (stock 810-822 against fork 437-442, a consistent 1.85x). Decode with a drafter is roughly comparable in the fork and fluctuates around stock (better on Q8_0, worse on Q4_K_M and BF16). Single runs per configuration, so treat those decode deltas as indicative only. BF16 drafting is heavy (3.9 GB per draft pass) and behaves notably worse in the fork.

## Verdict for this box

- Builds and runs (one nvcc-13.3 source patch); supports GGUF + MTP + DFlash2 and the EXL3 safetensors quant with both drafters.
- Default server configurations are 2-2.5x slower at prompt processing than stock and 8-28% slower at decode; its KV codecs do not compensate at 32k context.
- One win: `turbo4` KV at very long context decodes 25% faster than stock's q8_0, at 2.5x the prompt-ingest cost.
- **Keep stock llama.cpp for anything prefill-bound.** The fork is only worth running for long-context, decode-heavy sessions where the prompt stays cached, and even then only with turbo4-class KV.

## Data

`data/csv/buun-fork-sweep-tok_s.csv` (25 arms), `buun-vs-stock-harness.csv` (6), `buun-vs-stock-long-context-100k.csv` (3), `buun-vs-stock-drafter-quants.csv` (4).
