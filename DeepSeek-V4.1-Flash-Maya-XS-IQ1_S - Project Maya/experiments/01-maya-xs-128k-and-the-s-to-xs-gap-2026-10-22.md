# 01 — Maya-XS IQ1_S at 128K, and the 2.2× gap to Maya-S (2026-10-22)

Maya **v1.1.22** (released 22 Oct), engine `maya-ds4`, serving **Maya-XS** (IQ1_S experts, 120.6 GB
of weights), 131,072 context, both V100s, no speculation. The previous DeepSeek run on this box was
Maya-S IQ2_XXS on v1.1.19 (21 Oct) — that is the comparison below.

## Result

Mean of two full bench runs (run 1 follows the burn battery on the same load, run 2 is a fresh load;
gen 400; temp 0.5; seed 12345; exact tokenizer):

| depth | prefill run1 | run2 | mean | decode run1 | run2 | mean |
|---|---:|---:|---:|---:|---:|---:|
| 20K | 226.8 | 283.4 | **255.1** | 20.9 | 7.2 | **14.1** |
| 60K | 365.7 | 314.4 | **340.1** | 20.8 | 11.8 | **16.3** |
| 100K | 383.7 | 372.9 | **378.3** | 19.9 | 14.6 | **17.3** |

- **Peak prefill 383.7 tok/s** (100K), **peak decode 20.9 tok/s** (20K, the warmed load).
- Prefill spread 2.9–22.2% between runs; decode 30.7–97.5%. The decode spread is the fresh-load
  penalty: run 2 starts at 7.2 tok/s on its first arm and climbs to 14.6 by 100K, while run 1
  (warmed by the burn battery) holds 19.9–20.9 across all three depths. The burn battery reads
  7.6 / 15.4 / 17.7 — same shape. The two-run mean is the published figure; the warm-only figure is
  the top of the range.
- Nothing excluded: all six arms completed 400 tokens and both runs sliced the same document at each
  depth (frankenstein / sherlock / pride). The burn battery is excluded by design.

## Tensor parallel: asked for, refused by the engine's block arithmetic

The config carries `--tp 2` and both cards are used, but the engine logs at every start:

```
ds4: tensor parallel 2 -> 1: the experts' 256-value blocks split n_ff 2304 no other way (each GPU its own layers)
```

Source (`src/ds4/ds4_model.cu` L2317-2336, v1.1.22): a TP group takes `n_ff / tp` of each expert,
and for a GGUF whose expert blocks are 256 values wide the width is reduced while
`(g.ff / tp) % blk != 0` (blk = 256 for IQ1_S). 2304 / 2 = 1152, and 1152 % 256 = 128, so tp drops
to 1. Only 1, 3 or 9 parts divide 2304 into whole 256-value blocks — **on two GPUs this quant cannot
run tensor parallel**, and neither could Maya-S (IQ2_XXS, also 256-value blocks; its log carried the
same line). The engine falls back to one layer group per GPU: CUDA0 layers 0–19, CUDA1 layers 20–39
+ head.

## Speedup vs the 21 Oct Maya-S run

| depth | prefill S → XS | ratio | decode S → XS | ratio |
|---|---|---:|---|---:|
| 20K | 143.7 → 255.1 | 1.78× | 5.45 → 14.05 | 2.58× |
| 60K | 147.2 → 340.1 | 2.31× | 6.30 → 16.30 | 2.59× |
| 100K | 152.6 → 378.3 | 2.48× | 7.35 → 17.25 | 2.35× |
| **mean** | 147.8 → 324.5 | **2.20×** | 6.37 → 15.87 | **2.49×** |

The delta spans two changes: the quant (IQ2_XXS → IQ1_S) and the engine (v1.1.19 → v1.1.22). It is
**not** a tensor-parallel win — TP was refused on both sides. The mechanism that pays is residency:
XS puts 7,432 of 15,360 routed experts in VRAM (48%) against 4,651 (30%) for Maya-S, and the CPU
lane carries 54.8 GB read in place instead of 117.8 GB.

Maya-S was not re-run today: its quant was deleted before the update, so this pair is today's XS
against the archived 21 Oct runs (same harness, same battery, same box).

## Model and layout on the box

- `peasantsmith/DeepSeek-V4.1-Flash-1017-Maya-GGUF` @ `c273fcb`, `Maya-XS/` — 5 shards,
  **276.6 GB** (weights 115.3 GB in shards 1–3; Engram Q6_K 161.3 GB in shards 4–5), plus Maya-XS's
  own 2-bit DSpark drafter `dspark-xs2` (4.25 GB) — downloaded, not used.
- Weights on the SN730 NVMe (`/mnt/nvme/maya-ds4/Maya-XS/`), Engram shards on the boot SATA SSD
  (`/home/eamon/maya-ds4/engram-xs/`, symlinked into the model dir). Pack is an index only
  (`tensors.txt` 3.6 MB, `engram.bin` 518 KB) plus the engine's `expert-profile.bin`.
- Engine: 7,928 routed experts on the CPU lane (54.8 GB, read in place), 14 threads; CUDA0 3,729 of
  7,680 + CUDA1 3,703 of 7,680 in VRAM; ~580 MiB free per card. Load ~45 s.
- Speed calibration (setup, 2 loads): **13.9 tok/s without drafting vs 11.7 tok/s with the XS
  drafter** (68% of drafts accepted) → the config keeps `--dspark none`, the same call Maya's own
  calibration made for the shared drafter on 21 Oct (4.6 vs 6.8).

## Records

- Run dirs (box .5 `~/model-bench/runs/`): `2026-10-22T1921Z-ds4-maya-xs-128k-run1`,
  `2026-10-22T1932Z-ds4-maya-xs-128k-run2`; burn `2026-10-22T1911Z-...-burn`.
- In this folder: `data/raw/` (the three records), `data/csv/averages.csv`, `compare.csv`,
  `charts/` (two cards), `scripts/`, `serving/` (three stages with logs + launcher).
- Download: 276.6 GB from Hugging Face at ~23 MB/s (3 h 20 min), every shard size-checked.
- Setup: `./maya.sh --setup --yes --no-start --model DeepSeek-V4.1-Flash-1017 --model-dir
  /mnt/nvme/maya-ds4/Maya-XS --ds4-quant maya-xs --context 131072 --gpus 0,1 --host 0.0.0.0
  --port 8080 --no-vision`. Note the setup's download prompt defaults to "no" under `--yes`, so the
  shards were fetched by hand before it ran (with the Engram pair pre-linked to the SATA SSD; a
  whole-set download into the model dir would not fit the NVMe).
- The server was left running as served (`deepseek-v4.1-flash`, 131072).
