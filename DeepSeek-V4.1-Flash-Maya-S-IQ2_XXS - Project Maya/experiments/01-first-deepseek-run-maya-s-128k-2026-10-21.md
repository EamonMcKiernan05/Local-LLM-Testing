# 01 — First DeepSeek run on the V100s: Maya-S IQ2_XXS at 128K (2026-10-21)

Compared against: the Maya-XS run of 22 Oct, in the sibling folder
(`DeepSeek-V4.1-Flash-Maya-XS-IQ1_S - Project Maya/`) — same harness, **2.20× prefill / 2.49×
decode**.

First DeepSeek run on this box. Project Maya **v1.1.19** (engine `maya-ds4`) serving **Maya-S
IQ2_XXS**, 131,072 context, two-card layer split, no speculation (Maya's own calibration rejected
the DSpark drafter here: 4.6 vs 6.8 tok/s at short context).

## Result

Mean of two full bench runs (run 1 on the load the burn battery warmed, run 2 a fresh load;
gen 400; temp 0.5; seed 12345; exact tokenizer):

| depth | prefill run1 | run2 | mean | decode run1 | run2 | mean |
|---|---:|---:|---:|---:|---:|---:|
| 20K | 140.3 | 147.1 | **143.7** | 6.2 | 4.7 | **5.5** |
| 60K | 147.0 | 147.3 | **147.2** | 7.8 | 4.8 | **6.3** |
| 100K | 149.8 | 155.3 | **152.6** | 8.7 | 6.0 | **7.3** |

- **Peak prefill 155.3 tok/s** (100K prompt, run 2). **Peak decode 8.7 tok/s** (100K, run 1).
- Prefill is tight across runs (spread 0.2–4.7%); decode swings 27–48% between loads — `maya-ds4`
  re-times and re-plans its CPU/stream lanes on every load (the engine log shows the planned
  6.738 ms expert lane re-timed to 2.4–3.5 ms on the second load), so the two-run mean is the
  honest figure, not either run alone.
- Nothing excluded as an anomaly: all six measured arms completed 400 tokens, and both runs sliced
  the same document at each depth (`book`: frankenstein / sherlock / pride). The 14:09Z burn
  battery is excluded by design (post-load cache warm-up).

## Model and layout on the box

- `peasantsmith/DeepSeek-V4.1-Flash-1017-Maya-GGUF`, `Maya-S/` — 6 shards, 339.5 GB total
  (experts IQ2_XXS/IQ2_S/IQ3_XXS/IQ3_S, 178.2 GB; Engram Q6_K 161.3 GB), plus an 8 GB DSpark
  drafter (downloaded, not used).
- Experts shards 1–4 on the SN730 NVMe (`/mnt/nvme/maya-ds4/Maya-S/`), Engram shards 5–6 on the
  boot SATA SSD (`/home/eamon/maya-ds4/engram/`, symlinked into the model dir). The whole set does
  not fit the 234 GiB NVMe; splitting keeps the per-token reads on NVMe and the engram rows on SATA.
- Pack is an index only (`tensors.txt` 3.7 MB, `engram.bin` 518 KB) — no weight copies.
- Engine: 10,709 of 15,360 routed experts on the CPU lane (117.8 GB read in place); VRAM
  31.9 / 32 GB per card; the CPU lane carried 0.1–0.6% of experts per request.
- Unsloth's UD-IQ1_S set was downloaded and verified first, then deleted: the engine has no IQ1_S
  (ggml type 19) kernels — the packer refuses it. IQ2_XXS is the smallest quant Maya can read here.

## Records

- Run dirs (box .5 `~/model-bench/runs/`): `2026-10-21T1433Z-ds4-maya-s-128k-run1`,
  `2026-10-21T1458Z-ds4-maya-s-128k-run2`; burn `2026-10-21T1409Z-...-burn`.
- In this folder: `data/raw/` (the three records), `data/csv/averages.csv`,
  `charts/ds4-maya-s-128k-v100.png`, `scripts/`, `serving/` (driver + log + setup log + launcher).
- Setup: `./maya.sh --setup --yes --no-start --model DeepSeek-V4.1-Flash-1017 --model-dir
  /mnt/nvme/maya-ds4/Maya-S --ds4-quant maya-s --context 131072 --gpus 0,1 --no-vision`.
- Config `maya-ds4.json`, launcher `run-maya-ds4.sh`, engine log `maya-ds4.log`.

Strata's Qwen3.8-Flash-Next service was stopped to free the cards and is not running.
