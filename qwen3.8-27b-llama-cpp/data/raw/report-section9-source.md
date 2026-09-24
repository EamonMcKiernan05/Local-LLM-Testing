
## 9. Three-card matrix and the DFlash2 drafter on three cards — plus an attempt to pin the drafter (7 + 11 arms)

**Status: measurements COMPLETE, stage 2 VOID.** 18 arms recorded (7 in the three-GPU matrix, 11 in the DFlash2-on-three-cards sweep), **14 produced usable numbers and 4 aborted at model load** (1 tensor-split arm, 3 drafter-pinning arms). Both drivers printed their end markers (`GPU3_SWEEP_DONE` 16:54:49, `DFLASH3_SWEEP_DONE` 17:30:24). Engine unchanged: stock llama.cpp **b11041 (4fea119de)**, CUDA 13.3, sm_86. Measured prompt 99,589 tokens in every arm, 256 generated, seed 12345, temp 0.5, q8_0 KV, ctx 131072, `-b 2048 -ub 256`, `--spec-draft-p-min 0.00`, no `--top-k` / `--top-p` / `--min-p` (so the GGUF metadata's `top_k 20` / `min_p` off apply — §4). One run per arm.

**State of `.5` at time of writing (17:47 BST):** idle — no `llama-server` process, no sweep driver, GPUs at **9 / 1 / 1 MiB** of 12,288 MiB. Nothing was started, stopped or reconfigured on `.5` to produce this section. **Observation only.**

Raw evidence: `~/gpu3-sweep.jsonl` (7 rows), `~/dflash3-sweep.jsonl` (11 rows), `~/gpu3-sweep-logs/` and `~/dflash3-sweep-logs/` (one server log per arm), `~/gpu3-sweep.out`, `~/dflash3-sweep.out`, drivers `~/gpu3_sweep.py` and `~/dflash3_sweep.py`.

### 9.1 Three-GPU matrix — MTP and DFlash2 across three cards

All arms MTP `--spec-draft-n-max 7` or DFlash2 n-max 4 / 8, layer split unless stated. Acceptance columns are **in-run** values from each arm's `draft acceptance = … mean len = …` log line (see the §5 caveat — the JSONL's `acceptance_length` / `token_accept_rate` fields are cumulative `/metrics` counters and include the discarded warm-up, e.g. MTP n-max 7 reads 4.909 / 0.5795 there against 5.20 / 0.604 in-run).

| arm | split | `-ts` | prefill tok/s | gen tok/s | AL (in-run) | accept (in-run) | VRAM after load G0/G1/G2 (MiB) |
|---|---|---|---|---|---|---|---|
| `g3-layer-ts111-mtp7` | layer | 1,1,1 | 602.76 | **24.96** | 5.20 | 0.604 | 5795 / 6607 / **8113** |
| `g3-layer-ts353728-mtp7` | layer | 35,37,28 | **611.29** | 24.93 | 5.20 | 0.604 | 6397 / 7021 / 7095 |
| `g3-layer-ts13-13-04-mtp7` | layer | 1.3,1.3,0.4 | 514.31 | 24.78 | 5.20 | 0.604 | 7585 / 8349 / 4577 |
| `g3-layer-ts111-dflash4` | layer | 1,1,1 | 606.56 | 23.06 | 3.31 | 0.578 | 5941 / 6761 / 7261 |
| `g3-layer-ts111-dflash8` | layer | 1,1,1 | 598.12 | 19.47 | 3.63 | 0.376 | 6153 / 6961 / 7449 |
| `g2-layer-ts11-dflash4` | layer (2 cards) | 1,1 | 494.55 | **23.56** | 3.31 | 0.578 | 8695 / 10179 / 4 |
| `g3-tensor-ts111-dflash4` | tensor | 1,1,1 | — | — | — | — | — **aborted at load (§9.3)** |

**Which `-ts` balance wins: none of them, on decode.** 24.96 / 24.93 / 24.78 tok/s is a 0.18 tok/s spread (0.7%), and all three arms are byte-identical in output (`0194852ba7ad2825`) with identical counters (206 accepted / 341 generated). The balance only moves **prefill**: 602.76 / **611.29** / 514.31 — the skewed `1.3,1.3,0.4` balance costs **87 tok/s of prefill (−14%) and buys nothing**. On prefill alone `35,37,28` leads by 1.4%, which is inside this depth's prefill jitter (§5), so treat the top two as a tie and `1.3,1.3,0.4` as strictly worse. The sweep inherited `-ts 1,1,1` for stage 2 of §9.2 — that is not a confound, since the three balances are decode-identical.

**DFlash2 vs MTP at the same split (three cards, layer, `-ts 1,1,1`): MTP wins by 8.2%.** DFlash2 n-max 4 gives 23.06 tok/s against MTP n-max 7's 24.96, and DFlash2's best n-max in §9.2 (7, at 23.27) still trails by **7.3%**. Prefill is a wash (606.56 vs 602.76, +0.6%). DFlash2's acceptance is the reason: AL 3.31 / accept 0.578 against MTP's 5.20 / 0.604 — MTP proposes almost as many tokens per round (6.75 vs 3.95) *and* lands a higher share of them.

**The third card is not helping the drafter.** DFlash2 n-max 4 on **two** cards in layer split is *faster* at decode than the same arm on three — 23.56 vs 23.06 (+2.2%) — and identical in acceptance and output hash. The third card buys prefill (494.55 → 606.56, +23%), exactly the §8 pattern, and costs decode. Total VRAM is lower on two cards (18,878 MiB vs 19,963 MiB across the cards in use).

**DFlash2 n-max 8 never ran an 8-token window.** Its log prints `requested draft size (n_max=8, n_min=0) exceeds the trained block size 8 -- clamping to 7` — the DFlash2 drafter's trained block size is 8, so n-max 8 is n-max 7 wearing a wider output window, and it costs **16% of decode** (19.47 vs 23.27 at n-max 7 in §9.2). The same clamping line appears in the layer-8 arm from both sweeps.

**Nothing here is close to the recommendation.** The best DFlash2 number measured anywhere so far is 23.56 tok/s; the recommended two-card tensor-split MTP n-max 7 config is **43.06 tok/s** — **1.83×** DFlash2's best and **1.85×** its three-card peak.

### 9.2 DFlash2 n-max 1–8 on three cards (layer split, `-ts 1,1,1`, draft device inherited)

| n-max | prefill tok/s | gen tok/s | AL (in-run) | accept (in-run) | accepted / generated | VRAM after load G0/G1/G2 (MiB) |
|---|---|---|---|---|---|---|
| 1 | **624.06** | 16.10 | 1.88 | 0.881 | 119 / 135 | 5781 / 6611 / 7121 |
| 2 | 618.39 | 18.45 | 2.32 | 0.662 | 145 / 219 | 5835 / 6661 / 7169 |
| 3 | 614.58 | 19.40 | 2.63 | 0.547 | 158 / 289 | 5887 / 6711 / 7215 |
| 4 | 606.19 | 23.05 | 3.31 | 0.578 | 178 / 308 | 5941 / 6761 / 7261 |
| 5 | 603.32 | 22.11 | 3.45 | 0.495 | 181 / 366 | 5993 / 6811 / 7309 |
| 6 | 602.74 | 22.97 | 3.86 | 0.482 | 189 / 392 | 6047 / 6861 / 7355 |
| 7 | 600.29 | **23.27** | **4.32** | 0.477 | 196 / 411 | 6099 / 6911 / 7403 |
| 8 | 597.76 | 19.48 | 3.63 | 0.376 | 184 / 490 | 6153 / 6961 / 7449 |

- **The peak is n-max 7 at 23.27 tok/s — but it is a plateau, not a spike.** n-max 4 through 7 read 23.05 / 22.11 / 22.97 / 23.27, a **1.0% spread**. Against the §5 noise band (±3%) that is one number, not four: DFlash2's decode is flat from n-max 4 upward. This is the opposite shape to MTP's curve, which peaks sharply at 7 (43.07 against 33.40 at n-max 4 in §2).
- **Acceptance keeps climbing while throughput does not.** AL rises monotonically 1.88 → 4.32 (accept rate falls 0.881 → 0.477 as proposals per round rise from 1.0 to 6.8): each extra drafted token is worth less than it costs. At n-max 8 the window is over-wide, AL collapses to 3.63 and decode drops 16%.
- **Prefill falls monotonically with n-max** — 624.06 → 597.76 (−4.2%) across the eight arms, which is a larger and more orderly drift than MTP showed (MTP's prefill was flat and config-independent, §2/§7). The likely cause is the growing output window (`n_outputs_max` scales with `n_max + 1` for DFlash), so the graph carries bigger buffers per prefill batch. Flagged as an observation, not a measurement of a mechanism.
- **The two arms that repeat across sweeps agree exactly.** `dflash3-nmax4` reproduces `g3-layer-ts111-dflash4` to 0.01 tok/s (23.05 vs 23.06) and `dflash3-nmax8` reproduces the n-max 8 layer arm (19.48 vs 19.47), with identical acceptance counters and output hashes in both pairs.
- **Against the MTP n-max 7 baseline on the same split:** 23.27 vs **24.96** tok/s — MTP **+7.3%** — with equal prefill (600.29 vs 602.76). On this build and this model, the built-in MTP head is the better drafter on three cards, and neither is close to the two-card tensor-split MTP result.

### 9.3 What killed the two failing configurations

**Tensor split + DFlash2 (three cards) — a split-axis assert inside the meta backend.** The server aborted during load, before it ever served:

```
/home/eamon/llama.cpp/ggml/src/ggml-backend-meta.cpp:543: GGML_ASSERT(src_ss[0].axis != GGML_BACKEND_SPLIT_AXIS_0) failed
  ggml_backend_sched_alloc_graph -> llama_context::process_ubatch -> llama_context::decode
  -> llama_decode -> common_context_can_seq_rm -> server_context_impl::load_model
```

Two things this establishes:

1. **It is the drafter that breaks it, not the target — and the split mode is why.** The abort is in the meta backend's `handle_per_row` handler, which asserts that the op's source is *not* split on axis 0 (`ggml/src/ggml-backend-meta.cpp:543`). A meta wrapper over a split on axis 0 exists because `--split-mode tensor` splits the model row-wise. The draft model **inherits** the target's device list and split mode when `--spec-draft-device` is not given (`common/speculative.cpp:2476–2479` only overrides `result.devices` when the draft device list is non-empty) — and the source says so explicitly at `common/speculative.cpp:2480–2483`: *"a draft pinned to a single device doesn't need the meta wrapper an inherited `-sm tensor` would give it"*. So the DFlash2 drafter's graph, run through that wrapper, hits a per-row op over an axis-0-split tensor and aborts. The target alone under tensor split is fine — §8 ran `mode-tensor3-nmax7` cleanly with MTP.
2. **It died at load, not under generation.** The stack runs through `common_context_can_seq_rm` — llama.cpp's load-time probe of whether a context can drop a sequence, which does one small decode. Nothing was generated, no VRAM peak was recorded, and the arm has no `vram_after_load_mib`.

**`--spec-draft-device` (all three pinning arms) — a different abort, also at load.** All three arms died with the identical error, at the same point, regardless of `-ts`:

```
/home/eamon/llama.cpp/ggml/src/ggml-backend.cpp:941: pre-allocated tensor (output.weight)
  in a buffer (CUDA2) that cannot run the operation (NONE)
  ggml_backend_sched_split_graph -> llama_context::graph_reserve -> sched_reserve
  -> llama_init_from_model -> common_speculative_init_result -> server_context_impl::load_model
```

- The flag itself is real and was parsed: `--spec-draft-device, -devd, --device-draft` is listed by `llama-server --help` in this build (`common/arg.cpp:4200`), and the arms carried `devd=CUDA0` / `CUDA1` in their JSONL rows. This is a failure, not a typo.
- **The abort happens while the draft context is being built**, from `common_speculative_init_result` → `llama_init_from_model(model_dft, cparams)` → `sched_reserve` → `ggml_backend_sched_split_graph`. The scheduler that cannot place the tensor is the draft's.
- **The pin did not move `output.weight`.** All three arms name a **CUDA2** buffer even though they asked for CUDA0 (or CUDA1). CUDA2 is the card the *target's* output layer occupies under a 3-way layer split — `get_layer_buft_list(n_layer_all)` is the last share of the split (`src/llama-model.cpp:1546`). So the pinned device list moved the draft's device list but the placement of this tensor followed the split's last share, leaving a tensor in a buffer the draft's single-device scheduler will not run — hence the abort. Reading the failure mode: pinning is not "slower here", it **does not start**.
- Because all three arms aborted before the health check passed, there are **no `vram_after_load_mib` rows for the pinned configurations** — the question "did the `-ts` bias free the room it was meant to" cannot be answered from this sweep. What the JSONL shows for those three rows is `vram_after_load_mib: null`, `gen_tok_s: null`, `peak_vram_mib: null`.

### 9.4 Where the drafter actually lands (inherited case) — and why pinning had little to win

The stage-2 design assumed the drafter is resident on one card, so biasing `-ts` away from that card would make room for it. The inherited-case VRAM in §9.2 does not support that assumption:

| interval | Δ GPU0 | Δ GPU1 | Δ GPU2 |
|---|---|---|---|
| every +1 n-max (n1→n2 … n7→n8, 7 intervals) | 52–54 MiB | 50 MiB (exactly, every interval) | 46–48 MiB |
| n1 → n8 total | +372 | +350 | +328 |

**Every card grows by roughly 50 MiB for each extra drafted token.** That is the signature of the draft model *and its context* being spread across all three cards, which is what "draft device inherited" means in the source: with no `--spec-draft-device`, the draft takes the target's three-device list and the same layer split (`common/speculative.cpp:2476–2479`). There is no single card to bias `-ts` away from. **Stated as inference from the VRAM deltas, not from a printed device-assignment line** — these logs capture the server's own output plus model-loader warnings, and do not contain llama.cpp's `load_tensors:` / `model buffer size` lines.

The same numbers also bound the prize. The **entire** draft model plus a 131,072-token draft context, across n-max 1→8, moves the cards by 372 / 350 / 328 MiB — a few hundred MiB per card. Stage 1's tightest card peaked at 7,449 MiB of 12,288 MiB. VRAM was never the binding constraint in the DFlash2 configuration, so moving the drafter between cards has very little room to help even when it works.

### 9.5 Verdict — pinning the drafter

**It cannot be measured on this build, and it is not worth testing on the two-card config.**

- **Untestable as written:** 0 of 3 pinning arms loaded. `--spec-draft-device` aborts at draft-context init in `ggml_backend_sched_split_graph` (output.weight stranded in a CUDA2 buffer). The `-ts` bias made no difference — the arm with no bias died identically to the two with it. The question "pinned vs unpinned decode and prefill" has no answer in this data, and nothing should be read into the absence.
- **Not worth chasing on two cards:** the recommendation is two-card **tensor** split, and there the pin is a different proposition — with a single draft device the source forces the draft to **layer** split (`common/speculative.cpp:2480–2483`), so pinning changes what the drafter does rather than just where it lives. Add the §9.4 bound (a few hundred MiB of draft footprint against ~4.8 GB of headroom on the tightest two-card arm, 9,611 / 9,603 vs 12,288 MiB in §8) and there is no room for a win. The fastest configuration measured anywhere on this model uses **MTP**, which has no separate drafter to pin at all.
- **The open question worth one arm instead:** does DFlash2 work under tensor split **at all**? It aborted on three cards for a reason (the axis-0 meta wrapper) that is not three-card-specific. If it aborts on two cards too, DFlash2 is unusable in the recommended split mode and the whole drafter line is closed. If it loads, that is the only configuration in which DFlash2 was ever given the split mode that produces 43 tok/s with MTP. **Cost: one or two arms, ~12 minutes** — 2-card tensor + DFlash2 n-max 7, then the same with `-devd CUDA0` if the first aborts. Not run in this sweep (out of scope), and not run since.

### 9.6 `backend_sampling_on_gpu` in these two sweeps — true everywhere, including the four arms that never ran

All 18 rows report `backend_sampling_on_gpu: true`, and this field is set by the same absence-of-a-warning heuristic used in §8: the string `backend sampling not supported` appears in **none of the 18 logs** (checked with `grep -l` across both log directories).

That is correct for the 14 arms that ran — every one of them was layer-split, and layer split restores GPU-side sampling (§8). It is a **false positive for the 4 arms that aborted at load** (`g3-tensor-ts111-dflash4` and all three `-pin` arms, each of which also carries `asserted: true` / `dflash_assert: true`): a server that dies before the sampler is installed never prints the warning, and the heuristic cannot tell "warning absent because sampling worked" from "warning absent because the process aborted". **The 4 aborted rows' `backend_sampling_on_gpu: true` must not be read as evidence about sampling, and they say nothing about tensor split's sampler behaviour.** Read §8's tensor-split arms (`no`) for that.

### 9.7 Raw evidence for this section

| path | contents |
|---|---|
| `~/gpu3-sweep.jsonl` | 7 rows, three-GPU matrix (1 aborted) |
| `~/gpu3-sweep-logs/<arm>-100k.log` | per-arm server log; aborted arms carry the GGML abort and backtrace |
| `~/gpu3-sweep.out` | driver stdout, ends `GPU3_SWEEP_DONE` at 16:54:49 |
| `~/dflash3-sweep.jsonl` | 11 rows, DFlash2 on three cards (8 stage-1 + 3 aborted stage-2) |
| `~/dflash3-sweep-logs/<arm>-100k.log` | per-arm server log, including the in-run `draft acceptance … mean len` line |
| `~/dflash3-sweep.out` | driver stdout, ends `DFLASH3_SWEEP_DONE` at 17:30:24 |
| `~/gpu3_sweep.py`, `~/dflash3_sweep.py` | drivers (`dflash3_sweep.py` imports `~/two-card-nmax-trims-sweep.py` for `run_one`) |
| `~/llama.cpp/ggml/src/ggml-backend-meta.cpp:543`, `~/llama.cpp/ggml/src/ggml-backend.cpp:941` | the two abort sites |
| `~/llama.cpp/common/speculative.cpp:2476–2486`, `~/llama.cpp/src/llama-model.cpp:1546` | draft-device / output-layer placement logic quoted in §9.3 and §9.4 |
