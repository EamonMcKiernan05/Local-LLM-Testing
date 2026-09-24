# 02 — DFlash2 drafters against the built-in MTP head: the 107-run bake-off

**2026-09-18. Build `b11041`. `Qwen3.8-27B-UD-Q4_K_XL.gguf`, 3 cards, layer split `35,37,28`, ctx 32768, q8_0 KV, flash attention on.**

## Headline

**The built-in MTP head beat every DFlash2 configuration at every temperature tested.** DFlash2 is rejected for this box.

| temperature | best DFlash2 (gen tok/s) | at n-max | MTP (gen tok/s) | at n-max | margin |
|---|---|---|---|---|---|
| 0.0 (greedy) | 43.28 (Q4_K_M) | 6 | **47.29** | 8 | +9.3% |
| 0.6 | 35.21 (Q4_K_M) | 5 | **35.75** | 6 | +1.5% |
| 0.8 | 31.32 (Q4_K_M) | 4 | **32.63** | 8 | +4.2% |
| 0.9 | 28.08 (Q4_K_M) | 2 | **30.82** | 5 | +9.8% |

Per drafter, per temperature, best measured row only — a straight selection from measured runs, nothing modelled. Full 107 rows in `data/csv/dflash2-sweep-temp0.0.csv`, `-temp0.6.csv`, `-temp0.8.csv`, `-temp0.9.csv`.

## Why DFlash2 loses, mechanically

- **Block-diffusion acceptance collapses as sampling temperature rises**: 87.6% acceptance at greedy, 55-66% at temp 0.6, ~55% at 0.8. The MTP head holds 92-98% at every temperature.
- **DFlash2 costs more per decode step** (164 ms/step at n-max 8 against MTP's 154 ms at greedy) because its 5-layer draft model runs on every step.
- **The best DFlash2 n-max falls as temperature rises** — 6 at temp 0.0, 5 at 0.6, 4 at 0.8, 2 at 0.9. Exactly what you expect when blocks start getting rejected: a wider window just proposes more work that gets thrown away.

## Drafter quantisation is irrelevant here

All three DFlash2 quants (Q4_K_M, Q8_0, BF16) produced **identical accepted/generated counts at every n-max and temperature**. So the smallest quant is never worse, and the BF16 drafter — which carries 3.9 GB per draft pass — buys nothing at all. If DFlash2 is ever revisited, download Q4_K_M only.

## Correctness check

At temp 0.0 **every configuration emitted byte-identical text** (first 16 hex of the output hash: `70da3586571d564f`), which is the property a speculative decoder must have: spec decoding must not alter greedy output. At sampling temperatures the hash differs *between spec families* because the number of RNG draws depends on how many draft tokens were accepted, so the sampler's stream diverges; within a family the hash matches whenever the acceptance pattern matches.

## Prefill cost of drafting

DFlash2 also costs prefill. It has to be filled from the target's states across the whole prompt, which turns into a steady **~26% prefill tax at every depth** — see the depth profile in `experiments/04`: at 19,966 tokens, no speculation runs 1,096.8 tok/s, the MTP head 868.3, DFlash2 Q4_K_M 810.3. MTP also costs prefill against no speculation, but noticeably less than DFlash2, and it gives more back at decode.

## Method

- Server: one throwaway `llama-server` per arm, port 8081, service stopped
- Prompt: one synthetic ~20,000-token prompt (19,966 tokens counted via `/tokenize`), identical for every configuration, `cache_prompt: false` so full prefill is paid every run
- Generation: `n_predict 256`, one measured request per configuration after a discarded warm-up
- Seed 12345 for the temp 0.6/0.8/0.9 passes; greedy at temp 0 needs no RNG
- MTP rows use `--spec-type draft-mtp --spec-draft-p-min 0.85`; DFlash rows use `--spec-type draft-dflash -md <drafter>.gguf`
- `ms/step` is derived: `gen_ms / (gen_tokens / mean_len)`. It separates draft cost per step from how many tokens the draft wins per step. It is the one derived column in the dataset.

32 arms at temp 0.0, 11 at 0.6 (top-band confirmation only, n-max 5-8 for DFlash and 6-8 for MTP), 32 at 0.8, 32 at 0.9 = **107 measured runs**.
