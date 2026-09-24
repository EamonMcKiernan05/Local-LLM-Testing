# Sampler and draft-confidence flags: everything we measured

Every number here came off the same box as the rest of this repo (2× / 3× RTX 3060, llama.cpp `b11041`, `Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf` unless stated). Sources are named per table. This is the part of the dataset most worth reading before you copy any llama.cpp command line.

## The one rule that explains most of the surprises

**An unset sampler flag is not a default. It is the model's own value.**

llama.cpp reads `--top-k`, `--top-p`, `--min-p` and `--temp` from the GGUF's metadata whenever the user did not pass them. `common/common.cpp:1211 common_init_sampler_from_model()` consults a `user_sampling_config` bitfield (`common/common.h:257`) recording which parameters were actually passed, and for every parameter that was **not** passed it looks the value up in the model metadata and overwrites the CLI default. It will even replace the whole sampler *sequence* from `general.sampling.sequence` if `--samplers` was not passed.

`llama-server --help` still advertises the plain defaults (`--top-k … default: 40`, `--min-p … default: 0.05`). That is what misled us: we ran a 20-arm sweep believing the "no sampler flags" arms were `top_k 40 / min_p 0.05`, and they were not.

| what this model's metadata says | value |
|---|---|
| `general.sampling.top_k` | **20** |
| `general.sampling.top_p` | 0.95 |
| `general.sampling.min_p` | **0.0 (disabled)** |
| `general.sampling.temp` | 1.0 |

Consequence, measured: the "untrimmed" arm and the `top_k 20 / min_p 0.05` arm are the *same sampler*, so they land 0.14% apart (43.07 against 43.01 tok/s, AL 5.310 both). The `top_k 40 / min_p 0.05` arm is a *different* sampler and lands **35%** apart.

**So: if you pass one sampler flag, pass them all.** Otherwise the ones you left out silently inherit from the model, and your experiment is not the experiment you think it is.

## `--top-k`: the single most expensive knob

100k prompt depth, `n-max 7`, tensor split `1,1`, 99,589-token prompt, 256 generated, temp 0.5. AL and accept are in-run. Source: `data/csv/100k-stageB-topk-minp.csv`.

| `top_k` | `min_p` | decode tok/s | AL | accept |
|---|---|---|---|---|
| **20** | 0.05 | **43.01** | 5.310 | 0.616 |
| **20** | 0.08 | **43.05** | 5.310 | 0.616 |
| **20** | 0.10 | **43.03** | 5.310 | 0.616 |
| 30 | 0.08 | 41.24 | 5.100 | 0.594 |
| 50 | 0.05 | 40.59 | 5.000 | 0.573 |
| 30 | 0.10 | 37.80 | 4.640 | 0.522 |
| 30 | 0.05 | 37.70 | 4.640 | 0.519 |
| 50 | 0.10 | 34.11 | 4.180 | 0.460 |
| 50 | 0.08 | 34.84 | 4.250 | 0.469 |
| 40 | 0.10 | 34.07 | 4.180 | 0.460 |
| 40 | 0.08 | 34.06 | 4.180 | 0.460 |
| **40** | **0.05** | **27.97** | 3.450 | 0.356 |

**`top_k` runs backwards from intuition.** A *narrower* pool is faster: 20 → 43.0, 30 → 37.7-41.2, 40 → 28.0-34.1, 50 → 34.1-40.6 tok/s. The mechanism is visible in the acceptance columns: widening the pool makes the target pick less predictable tokens, so the MTP draft head agrees with the target less often. Fewer accepted tokens per round, same round cost, lower throughput. `top_k 40` is 35% below `top_k 20` and the loss is entirely acceptance (AL 5.31 → 3.45).

**Never set `--top-k 40` because the help text calls it the default.** On this model it is the worst value in the range.

## `--min-p` is inert once `top_k` is 20

At `top_k 20`, `min_p` 0.05 / 0.08 / 0.10 give 43.01 / 43.05 / 43.03 tok/s — a 0.1% spread — and **byte-identical output** (all three share `output_sha256 34fd0b3a3fcbd528`). A tight `top_k` has already removed the tokens `min_p >= 0.05` would remove, so `min_p` has nothing left to do.

At `top_k 40`, `min_p 0.08` and `0.10` are also byte-identical to each other (`cc0bb028921b3645`) at 34.06 / 34.07 tok/s.

Practical reading: with this model, `min_p` is not a tuning knob. Set it or leave it, the speed is the same.

## `--top-p` was never varied

Not one arm in any sweep changed `top_p`. It stayed at the GGUF's 0.95 (or unset, which is the same thing here). So there is **no measured answer** to "what does `top_p` cost?" on this box — treat any claim otherwise as unmeasured.

It matters for one reason: `top_p` sits in the same inheritance chain, so if you pass `--min-p` but not `--top-p`, you have silently mixed a CLI choice with a model choice.

## `--temp`: what we know, and the gap

Measured on `UD-Q4_K_XL`, three cards, 19,966-token prompt, 256 generated, n-max 1-8 per family per temperature (`data/csv/dflash2-sweep-temp0.*.csv`, `-temp0.6.csv`, `-temp0.8.csv`, `-temp0.9.csv`):

| temperature | MTP acceptance | best DFlash2 acceptance | DFlash2's best n-max |
|---|---|---|---|
| 0.0 (greedy) | 97.8% | 90.7% | 6 |
| 0.6 | 94.7% | 65.9% | 5 |
| 0.8 | 91.9% | 60.8% | 4 |
| 0.9 | 97.2% | 71.8% | 2 |

- **Temperature is the single biggest threat to a diffusion-style drafter.** DFlash2's acceptance collapses as sampling gets looser (87.6% → 55-66% → ~55%). The MTP head holds 92-98% at every temperature, which is the whole reason it won.
- **The best draft window shrinks as temperature rises** for DFlash2 (6 → 5 → 4 → 2). When blocks start getting rejected, a wider window only proposes more wasted work.
- **At temp 0.0 every configuration emits byte-identical text** (`70da3586571d564f`), whatever the spec family. That is the correctness check: speculative decoding must not change greedy output.
- `--temp` was passed on the command line in every run, so it overrode the metadata's 1.0. **There is no temperature sweep on llama.cpp in this dataset** — the service just moved 0.95 → 0.6 (2026-08-21) → 0.5 (adopted). How much temp 0.5 versus 0.7 costs in acceptance here is an open question.

## `--spec-draft-p-min`: the confidence gate, and the flag that hurt the most

This is the MTP threshold gate: draft tokens are only proposed while the head is confident enough. It is the flag that was costing most of the speed.

| depth | `n-max` | `p-min` | decode tok/s | AL | accept |
|---|---|---|---|---|---|
| 20k | 2 | **0.00 (ungated)** | **43.40** → verified **44.33** | 2.329 | 0.669 |
| 20k | 2 | 0.85 (gated) | **26.01** → verified **25.76** | 2.439 | 0.959 |
| 20k | 4 | 0.00 | 42.73 | 2.983 | 0.496 |
| 20k | 4 | 0.85 | 32.18 | 3.500 | 0.970 |
| 150k | 2 | 0.85 | **9.15** | 1.667 | 0.667 |
| 150k | 2 | 0.00 | 7.78 | 1.667 | 0.353 |
| 150k | 4 | 0.85 | 8.90 | 1.667 | 0.667 |
| 150k | 4 | 0.00 | 6.48 | 2.143 | 0.286 |

Source: `data/csv/two-card-mtp-nmax-20k.csv`, `-150k.csv`, and `two-card-20k-verification-3-repeats.csv` (three repeats per arm with `ignore_eos` forcing exactly 256 tokens: 44.38 / 44.33 / 44.29 against 25.81 / 25.68 / 25.78).

**The gate's sign flips with depth, and that is the important part.**

- **At 20k, the gate costs 1.72×** (44.33 vs 25.76 tok/s). That is the single largest penalty we measured anywhere in this dataset.
- **At 150k, the gate *gains* 18%** (9.15 vs 7.78). Every gated arm reports identical AL 1.667 and acceptance 0.6667, whatever `n-max` you ask for.

The mechanical reason: at shallow depth a decode round costs roughly the same no matter how many positions get verified, so proposing more draft tokens is nearly free and rejecting them costs little. At depth, every verification position attends over the whole KV cache, so a round's cost scales with the positions verified — and rejected draft tokens become pure waste rather than free.

**What we could not explain:** in the 20k pair, acceptance length is nearly the same in both arms (2.381 ungated vs 2.439 gated) and the ungated arm proposes *more* draft tokens per round, yet it finishes a 256-token generation in 5,752 ms against the gated arm's 9,891 ms. Roughly 1.8× the time per round for the same tokens per round. Some cost is attached to the gating path itself, not the draft window. A `p-min` curve at `n-max 2` (0.0 / 0.4 / 0.6 / 0.7 / 0.8 / 0.85 / 0.9 / 0.95) would show whether that cost is a cliff or a gradual slope. **Not run.**

Only two `p-min` values were ever tested, 0.00 and 0.85. The live service ran `0.85` from August until 2026-09-23; **the adopted configuration has no `--spec-draft-p-min` at all**, i.e. it runs ungated.

Also note the acceptance figures are a trap on their own: the gated arms show the *higher* acceptance rate (0.96 vs 0.67) while being far slower. Acceptance rate is not a performance metric — accepted tokens per round, weighed against round cost, is.

## `--spec-draft-n-max` — the other half of the drafting decision

Not a sampler flag, but it is the same trade. Sources: `data/csv/100k-stageA-nmax.csv`, `two-card-mtp-nmax-20k.csv`, `-150k.csv`.

| depth | gate | fastest `n-max` | result |
|---|---|---|---|
| 100k | ungated | **7** | 43.07 tok/s (n-max 8 gives 35.60) |
| 20k | ungated | **2** (2-4 within noise) | 44.33 tok/s |
| 20k | gated 0.85 | 4 | 32.18 tok/s |
| 150k | gated 0.85 | 2 | 9.15 tok/s, and 3-8 are all within 8% |

Wider is not better at any depth. At 100k, `n-max 8` proposes the most tokens per round of any arm (7.9) and converts 42.8% of them, ending 21% slower than 7.

`--spec-draft-n-min` was never swept — every arm ran `n-min 0`.

## Penalty flags

`--presence_penalty 0.0` is in the adopted configuration and was **never varied**. Nothing measured. Any claim about presence/frequency penalties on this box would be invention.

## The settings that survived all of it

```bash
--spec-type draft-mtp --spec-draft-n-max 7 \
--temp 0.5 --presence_penalty 0.0
# and no --top-k / --top-p / --min-p at all
```

At 100k depth that is 43.07 tok/s with the model's own sampler (`top_k 20`, `min_p` off). If you want the setting visible in the process list, `--top-k 20` explicitly is measurably identical (43.01). If you write one sampler flag, write all of them.

## Same lesson, different engine

The retuned ExLlamaV3 stack has a flag for exactly this idea: `--dds`, a draft window that adapts to draft confidence. It is **slower** — AL 5.197 against 5.708, and 67.6 against 72.2 tok/s at n=10 — because at shallow depth the round is flat-cost, so truncating the window only throws away accepted tokens. The engine is different; the shape of the finding is identical to the 20k `p-min` result. Treat "adaptive confidence gating" as a depth-dependent bet, not a free win.

## Open questions

- `--spec-draft-p-min` curve at `n-max 2`: is the 20k penalty a cliff or a slope? (0.0 / 0.4 / 0.6 / 0.7 / 0.8 / 0.85 / 0.9 / 0.95)
- `--top-p` sweep: never touched.
- `--temp` sweep on llama.cpp: never run. The service value was chosen, not measured.
- `--spec-draft-n-min`: never run.
- KV quantisation below q8_0 (`q4_0` / `q5_1`) and its effect on acceptance and deep decode: never run.
