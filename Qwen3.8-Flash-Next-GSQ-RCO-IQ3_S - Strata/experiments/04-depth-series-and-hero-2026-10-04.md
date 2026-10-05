# 04 — The depth series and the 250K hero run (2026-10-03/04)

The two data-collection passes behind the first figures, both on the base IQ3_S (v0.1.32 era,
both cards, 262K context).

## Hero series — five depth points and one full-depth streaming generation

Five short prompts (8k–150k depth, 16-token replies) plus one hero run: the full document at
~250K depth with a 6,000-token essay streamed back, per-token timestamps recorded.

| depth | prompt read (tok/s) | decode (tok/s) |
|---|---|---|
| 8k | 786.3 | 53.1 |
| 20k | 1,262.4 | 58.4 |
| 50k | 1,549.9 | 56.1 |
| 100k | 1,641.3 | 55.6 |
| 150k | 1,610.3 | 57.6 |

The hero run itself, from the engine's own line (the authoritative readout):

> `strata serve: prompt 250632 tokens = 0 reused + 250632 read in 167602 ms (1495.4 tok/s),
> 6000 generated in 122856 ms (48.8 tok/s), drafts accepted 3020 of 4845`

One counting nuance, stated because someone will ask: the raw JSONL is the *client's* view of
the same run — it logs the document length (250,592 tokens, hardcoded from the token count used
to slice the prompt), a 168.88 s ingest, 122.83 s of stream, and 5,899 stream events. The
engine's line counts the request's own prompt (250,632 — instruction included) and the full
6,000-token generation. Both are recorded;
[`data/csv/hero-250k.csv`](../data/csv/hero-250k.csv) carries the client fields and
[`engine-log-extracts.txt`](../data/raw/engine-log-extracts.txt) carries the engine line. The
card's tiles use the engine's numbers.

Figure: [`charts/strata-v100-250k-hero.png`](../charts/strata-v100-250k-hero.png) — built from
this run in a reference card layout (stat tiles → prompt curve → decode curve → sidebar),
delivered 2026-10-03; the next day's six-document card is the one that went to X.

Raw: [`strata-hero.jsonl`](../data/raw/strata-hero.jsonl) +
[driver](../data/raw/strata-hero.py).

## Six-document depth series — the posted card's data

Six **unique documents**, one per depth (frankenstein → mobydick), one 400-token generation
each — no shared prefix anywhere, so every run pays full prefill:

| depth | book | prompt read (tok/s) | decode (tok/s) |
|---|---|---|---|
| 20k | frankenstein | 1,169.6 | 58.1 |
| 60k | sherlock | 1,533.4 | 59.2 |
| 100k | pride | 1,575.0 | 53.3 |
| 150k | tale2cities | 1,550.4 | 48.0 |
| 200k | greatexp | 1,504.1 | 53.4 |
| 250k | mobydick | 1,448.8 | 46.4 |

Decode eases from 58.1 to 46.4 tok/s across the full window; prefill peaks at 1,575 tok/s
(100k) and holds 1,449 at 250K. This is the data behind
[`charts/strata-v100-decode-depth.png`](../charts/strata-v100-decode-depth.png), posted
2026-10-04.

Raw: [`depth-decode3.jsonl`](../data/raw/depth-decode3.jsonl) +
[driver](../data/raw/strata-depth-decode3.py); table:
[`data/csv/depth-series-0-1-32.csv`](../data/csv/depth-series-0-1-32.csv).

> Both series here are 0.1.32 numbers. The engine comparison in experiment 06 re-measured the
> same battery on 0.1.39 — read that one for the current speeds.
