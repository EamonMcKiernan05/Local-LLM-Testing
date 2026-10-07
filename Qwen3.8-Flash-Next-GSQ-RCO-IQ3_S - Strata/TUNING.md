# Tuning notes: what actually moves the needle on Strata

Every rule below came out of the measurements in this folder — read the linked experiment before
copying a command line. **The short version:**

1. **The drafter gate is the knob that matters.** `--spec-min-p 0.50` ships on the base: across
   126 runs at six depths it won the mean (56.8 tok/s against 53.3–53.7) and 4 of 6 depths. The
   earlier single-run "0.85 is best at 100k" did not generalise; single cells are noise. Do not
   carry a gate value across models or depths without re-measuring — and rank on the mean, not
   on one cell. (Experiments 05, 03.)
2. **Keep `--suffix-draft` 3 (the default).** 0 (off) loses 4.7 tok/s on the mean, 8 (aggressive)
   loses 3.8 — and the sweep's source document was uncommonly repetitive, which flatters
   prompt-lookup drafting. (Experiment 05.)
3. **Keep `--coupled-draft` off.** Turning it on loses ~3.5 tok/s on the mean; only the 100k cell
   gains. (Experiment 05.)
4. **The sampler trims are flat — leave them alone.** On Strata, `top_k` / `min_p` / `top_p` moved
   nothing beyond run noise (54.2–61.6 tok/s across the whole grid; per-depth bands 6.5–12.4 wide
   with the ordering reshuffling). There is no llama.cpp-style trap here: the same `top_k 40`
   that costs 35 % there is indistinguishable from the rest on this engine. (Experiments 03, 05.)
5. **The n-gram shard never goes on a spinning disk.** Decode pins at ~13 tok/s when it does;
   62+ when it doesn't. Move the file and leave a symlink — never repoint the config (duplicate
   shard error). (Experiment 01; mechanics in [`HARDWARE.md`](HARDWARE.md).)
6. **Bench hygiene that cost real time:** give every request a unique prefix (an identical
   prompt is a cache hit, not a measurement), discard the first request after any load, and rank
   on **decode tok/s** — draft acceptance % is a diagnostic, not the goal (the fast-looking
   acceptance number has belonged to the slower arm more than once). (Method notes in 02–05.)
7. **Retire forced workarounds once upstream fixes them — on sm_70 that was ~6 % prefill.** This
   box forced the old prompt-attention kernel (`STRATA_PROMPT_ATTN_OLD=1`, upstream #371) from
   v0.1.32 until v0.1.40.1; the engine's own sm_70 kernel (the fix landed in 0.1.33) is ~6 %
   faster prefill than the forced path, day-matched (experiment 08).
8. **`STRATA_PREFILL_CPU_SHARE` is single-GPU only — expect nothing from it on a layer split.**
   On the 2-card box it measured +0.6 % mean on 512–4,000-token prompts (noise) and ±1 % on the
   battery; the CPU pool is wired to the prefill path only when the run is not split
   (`set_cpu_pool` is guarded by `!multi_gpu`), so the path can never engage here (experiment 10).
   Upstream's −19–35 % (under 1,000-token prompts) comes from single-GPU boxes.

## How to set the gate

- Engine flag (restart to apply): `--spec-min-p 0.5` in the model's config args.
- Per request (no restart): `strata_tune: {"spec_min_p": 0.85}` in the chat-completions body —
  this is how both sweeps were run; an arm is one HTTP call.
