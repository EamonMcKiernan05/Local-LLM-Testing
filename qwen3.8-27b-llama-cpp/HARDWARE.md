# Hardware, models and flags

> **Era note:** everything in this folder was measured on the RTX 3060 configuration, 2026-08-14 to 2026-09-23. The box has since been rebuilt around 2× Tesla V100 32GB (2026-09-24), which is a different CUDA generation (Volta, sm_70) and a different dataset.

## The box

| item | value |
|---|---|
| Host | single desktop/workstation build (`eamon-ai`), inference only |
| Board | MACHINIST X99-MR9A PRO MAX |
| CPU | Intel Xeon E5-2680 v4, 14 cores / 28 threads |
| RAM | 32 GB DDR4-2400 (31 GB visible to the OS) |
| OS | Ubuntu 24.04.4 |
| Driver | NVIDIA 580.173.02 |
| Cards | 3x RTX 3060 12 GB (03:00.0 GA104, 04:00.0 GA106 LHR, plus a third on PCIe 2.0 x4) |
| Card count change | from 2026-09-23 20:57 the third card is no longer enumerated — 24 GB total from that point |
| Interconnect | GPU0/GPU1 PCIe 3.0 x16, GPU2 PCIe 2.0 x4. **No NVLink.** |

The PCIe 2.0 x4 link on the third card is why it is excluded from every row-split (tensor) run: a row-split collective is gated by the slowest link, so including it measured 40% slower at prefill and 44% slower at decode (`data/csv/100k-split-mode-matrix.csv`, `mode-tensor3` arms).

## llama.cpp builds

| build | commit | CUDA | built | used for |
|---|---|---|---|---|
| `b10068` | `571d0d540` | 12.0 | 2026-07-18 | live service through the August runs |
| `b11041` | `4fea119de` | 13.3.73 | 2026-09-18 | the DFlash2 bake-off onwards; still the live binary |

The `b11041` build recipe (unchanged from July apart from the version):

```
cmake -B build \
  -DGGML_CUDA=ON -DGGML_CUDA_FA=ON -DGGML_CUDA_FA_ALL_QUANTS=ON -DGGML_CUDA_GRAPHS=ON \
  -DGGML_CUDA_NCCL=ON -DGGML_CUDA_F16=ON -DGGML_CUDA_COMPRESSION_MODE=size \
  -DCMAKE_CUDA_ARCHITECTURES=86 \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda-13.3/bin/nvcc \
  -DCMAKE_INSTALL_RPATH="/usr/local/cuda-13.3/lib64;\$ORIGIN" -DBUILD_WITH_INSTALL_RPATH=ON
```

sm_86 only — the RTX 3060 is Ampere, and the only `sm_*` string in `libggml-cuda.so.0.24.0` is `sm_86`. `nvcc` has to be pinned by absolute path: the `/usr/bin/nvcc` on PATH is a stale CUDA 12.0 from 2023 and builds against the wrong runtime. No `-std=c++20` workaround was needed for this build (unlike the ExLlamaV3 extension, which is a different toolchain story and out of scope for this repo).

## The two GGUFs under test

Both are the same 27B-parameter model, and results are not transferable between them.

### `Qwen3.8-27B-UD-Q4_K_XL.gguf`

- 17.56 GB, unsloth "UD" dynamic quant, `ftype Q4_K - Medium`, 27.3B params
- arch `qwen35`, `/props` reports ctx 262144
- Served by the live systemd unit from 2026-08-14 21:04:36 until 2026-09-23
- Used for: the DFlash2 vs MTP bake-off, the depth profile, the MTP-vs-no-MTP live comparison

### `Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf`

- 12,120,016,960 bytes, IQ3_S with the **built-in MTP head** (3.50 bpw)
- arch `qwen35`
- Used for: the two-card tensor-split sweep, the 100k n-max / sampler / split-mode sweeps, the three-card matrix, and the live service since 2026-09-23 22:37:19

### Drafters (DFlash2, GGUF, `z-lab/Qwen3.8-27B-DFlash2-GGUF`)

| file | size | verdict |
|---|---|---|
| `Qwen3.8-27B-DFlash2-Q4_K_M.gguf` | 1.14 GB | best DFlash2 quant; the only one worth keeping |
| `Qwen3.8-27B-DFlash2-Q8_0.gguf` | 2.06 GB | same accepted/generated counts as Q4_K_M at every n-max |
| `Qwen3.8-27B-DFlash2-BF16.gguf` | 3.86 GB | no better, 3.9 GB per draft pass |
| `Qwen3.8-27B-DFlash2-Q2_K_S-MIX.gguf` | 561 MB | smallest; only usable under layer split |

**All three quants produced identical accepted/generated counts at every n-max and temperature.** Drafter quantisation is irrelevant for this pair, so Q4_K_M is never worse and costs a third of the VRAM.

## Flag sets in use

### Live service since 2026-09-23 22:37:19 (the one that survived the sweeps)

```
/home/eamon/llama.cpp/build/bin/llama-server
  --parallel 1
  -m /home/eamon/models/Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf
  --split-mode tensor --fit off --tensor-split 1,1
  --ctx-size 204800
  --flash-attn on
  --cache-type-k q8_0 --cache-type-v q8_0
  -b 2048 -ub 256
  --host 0.0.0.0 --port 8080
  --jinja --reasoning-preserve --metrics
  --spec-type draft-mtp --spec-draft-n-max 7
  --temp 0.5 --presence_penalty 0.0
```

No `-ts` tuning beyond the even `1,1`, and no `--top-k` / `--top-p` / `--min-p` at all. The GGUF's own metadata (`top_k 20`, `top_p 0.95`, `min_p` off) applies. That is not an oversight — it is the measured fastest configuration (see `experiments/06-100k-nmax-trims.md`).

### Live service until 2026-09-23 (three-card, layer split)

```
--parallel 1 -m /home/eamon/models/Qwen3.8-27B-UD-Q4_K_XL.gguf
--split-mode layer --fit off --tensor-split 35,37,28
--ctx-size 262144 --flash-attn on
--cache-type-k q8_0 --cache-type-v q8_0
-b 2048 -ub 256 --jinja --reasoning-preserve --metrics
--spec-type draft-mtp --spec-draft-n-max 8 --spec-draft-p-min 0.85
--temp 0.6
```

`--chat-template-file /home/eamon/models/chat_template_fixed.jinja` and the `--reasoning-budget*` flags are both present in the unit file **commented out** — the stock in-GGUF template is what serves.

### Sweep harness flags (throwaway server per arm)

```
--parallel 1 --split-mode layer|tensor --fit off
--tensor-split <per-arm> --flash-attn on
--cache-type-k q8_0 --cache-type-v q8_0
--ctx-size 32768 | 131072 | 163840
-b 2048 -ub 256 --jinja --reasoning-preserve --metrics
--spec-type draft-mtp --spec-draft-n-max N --spec-draft-p-min P
[or] --spec-type draft-dflash -md <drafter>.gguf
```

The live `llama-server.service` was stopped for every sweep. The drivers refuse to start if the unit is active or if any card already holds VRAM above ~400 MiB.

## Known memory limit

The unit was OOM-killed once, on 2026-09-22 21:54:06 (`status=9/KILL`, `Failed with result 'oom-kill'`, 29.2 GB memory peak), while its single slot was processing a ~216k-token prompt at ctx 262144 with q8_0 KV plus MTP. It auto-restarted. `MemoryMax` is set to `infinity`, so the kernel decides, not systemd. A single request running near the context ceiling is what tips this host over — the 262k window is not free.
