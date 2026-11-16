# Qwen3.8-Flash-Next — UD-Q3_K_XL and UD-IQ3_XXS on Strata, bundled vs BF16 n-gram table

Eight runs, 2026-11-16, box `.5` (2x Tesla V100-PCIE-32GB, 32 GB RAM, NVMe).
Strata **0.2.14.1** (engine 0.1.60.1, local sm_70 CUDA 12.9 build), `--kv int8`, `--max-context 262144`,
MTP on (`--spec 4 --spec-min-p 0.5`), `--resident-budget-gib 8`, `--expert-cache auto`.
Temp 0.5, seed 12345, 256 generated tokens, one rep per arm, `cache_prompt: false`.

The three configs differ **only in the model paths** — same flags, same context, same KV type. Verified by
diffing the argv of `strata-unsloth-ud-q4_k_xl.json`, `…-ud-q3_k_xl.json` and `…-ud-iq3_xxs.json`.

Two questions, one battery: what the two Q3-class quants do, and what the lossless BF16 table costs them.

## Results

Prefill and decode in tok/s, measured prompt tokens in brackets. Books and code are two different
corpora at the same nominal depth, so they do not have identical token counts.

### books

| quant | table | 20K prefill | 20K decode | 100K prefill | 100K decode |
|---|---|---:|---:|---:|---:|
| UD-Q4_K_XL (reference) | IQ4_NL | 248.9 | 38.4 | 695.4 | 54.0 |
| UD-Q4_K_XL (reference) | BF16 | 292.4 | 32.9 | 448.9 | 54.2 |
| UD-Q3_K_XL | IQ4_NL | 1,416.5 | 70.8 | 2,030.6 | 69.5 |
| UD-Q3_K_XL | BF16 | 1,426.4 | 72.8 | 2,034.3 | 66.5 |
| UD-IQ3_XXS | IQ4_NL | 1,430.2 | 79.7 | 2,079.7 | 69.1 |
| UD-IQ3_XXS | BF16 | 1,410.1 | 76.0 | 2,075.0 | 69.4 |

### code

| quant | table | 20K prefill | 20K decode | 100K prefill | 100K decode |
|---|---|---:|---:|---:|---:|
| UD-Q4_K_XL (reference) | IQ4_NL | 440.8 | 34.0 | 567.6 | 55.1 |
| UD-Q4_K_XL (reference) | BF16 | 505.3 | 27.7 | 436.3 | 45.2 |
| UD-Q3_K_XL | IQ4_NL | 1,552.9 | 79.1 | 2,081.8 | 64.3 |
| UD-Q3_K_XL | BF16 | 1,570.3 | 73.8 | 2,131.7 | 76.4 |
| UD-IQ3_XXS | IQ4_NL | 1,601.0 | 77.4 | 2,083.0 | 68.7 |
| UD-IQ3_XXS | BF16 | 1,597.3 | 87.1 | 2,080.2 | 69.3 |

Draft acceptance per arm: Q3_K_XL 61–79 %, IQ3_XXS 64–80 %. Decode differences of ±10 % track draft
acceptance, not the table — code 100K swings 64.3 (61 % acceptance) to 76.4 (73 %) on the same weights.

## Findings

1. **At Q3 sizes the BF16 table is free.** Prefill moves by −1.5 % to +2.4 % across all four
   quant/table comparisons (books 100K: 2,030.6 → 2,034.3; code 100K: 2,081.8 → 2,131.7). On UD-Q4_K_XL
   the same swap cost 23–35 % prefill — the difference is that Q3-class prefill is 3–10x faster overall,
   so the table's extra bytes are not the bottleneck.
2. **The Q4 file is on the wrong side of a residency cliff.** Identical flags, identical engine, identical
   KV: 82.53 GB of weights gives 567–695 tok/s prefill at 100K, 60.66 GB gives ~2,030–2,130. Nothing was
   retuned to get there — the earlier IQ3_S reference on this box (2,148.8 tok/s prefill, 69.1 decode at
   100K) is simply what a Q3-class file does here. Decode lands in the same band: 69.1 then, 64.3–76.4 now.
3. **Q3_K_XL and IQ3_XXS are indistinguishable on speed.** 2,031–2,132 vs 2,075–2,083 at 100K, decode
   64.3–76.4 vs 68.7–69.3. IQ3_XXS is 5.8 GB smaller (54.83 vs 60.66 GB weights) and marginally steadier
   on books; pick on quality grounds, not speed.
4. **Flags do not explain the old gap.** Re-running UD-Q4_K_XL with the IQ3_S-era flag set
   (`--mmap-experts --vram-reserve-mib 700 --remote-expert-opt`) gave 538.3 / 38.2 at 100K — worse than
   the shipped config's 695.4 / 54.0. See the UD-Q4_K_XL folder.

## How the BF16 table is served

Unsloth's `engram/Qwen3.8-Flash-Next-engram-BF16.gguf_file` (102.4 GB) is stamped
`general.architecture = "strata-ple"` (header only, 192 bytes, tensor data untouched — Strata issue #6013),
then the config's `--ple-gguf` points at it while the quant's own IQ4_NL shard stays in place for
`--native`. Every arm above logs the engine's own line, so the table in use is not inferred:

```
Q3_K_XL bundled: PLE on, table 320001536 rows of …/UD-Q3_K_XL/Qwen3.8-Flash-Next-UD-Q3_K_XL-00004-of-00004.gguf
Q3_K_XL bf16:    PLE on, table 320001536 rows of …/engram/Qwen3.8-Flash-Next-engram-BF16.gguf_file
```

Native support for swap-in tables is Strata issue #5248 (open).

## Files

`runs/<cell>/` holds `results.jsonl` (raw per-arm records incl. GPU state and draft acceptance),
`meta.json` and `summary.csv` for the eight cells: `q3kxl-bundled-{books,code}`,
`q3kxl-bf16-{books,code}`, `iq3xxs-bundled-{books,code}`, `iq3xxs-bf16-{books,code}`.

Caveats: one rep per depth; 20K arms are the cold, first-touch ones; the UD-Q4_K_XL reference arms were
measured earlier the same day on the same engine and harness, not back-to-back with these.
