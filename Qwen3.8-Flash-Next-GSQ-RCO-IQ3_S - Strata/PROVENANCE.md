# Provenance: where every file here came from

Collected 2026-10-05. The rule for this folder: **a number appears here only if it came off a
real run, and every table says which run.** All measurements are on the base IQ3_S.

## Sources, in order of reliability

1. **Raw per-arm records** — written by the drivers themselves, one JSON object per arm, at the
   moment the arm finished. The strongest evidence in the repo:

   | file | rows | what |
   |---|---|---|
   | `strata-mtp-sweep-all-arms.jsonl` | 126 | the drafter-gate / flags / sampler sweep |
   | `strata-sampler-sweep-base.jsonl` | 20 | the first per-request sweep |
   | `model-bench-0-1-32-base-results.jsonl` | 7 | 0.1.32 battery (1 discarded warm-up + 6 arms) |
   | `model-bench-0-1-39-base-results.jsonl` | 7 | 0.1.39 battery (same shape) |
   | `depth-decode3.jsonl` | 6 | the six-document depth series |
   | `strata-hero.jsonl` | 6 | five depth points + the hero run |

2. **Driver logs** — the chained master driver's stdout (`strata-mtp-sweep.out`), the sweep
   drivers' prints (`*.out`), the per-config comparison logs (`strata-compare-*.log`), and the
   engine's own per-request lines for the two 250K runs (`engine-log-extracts.txt`). Captured
   verbatim; not retyped.
3. **The model-bench run directories on the box** (`~/model-bench/runs/2026-10-04T1320Z-…` and
   `T1335Z-…`) — the two `results.jsonl` files here are byte-identical copies (sha256 checked
   against the box).

## Counting the runs

**183 recorded runs, every one with measurements; no failures:**

126 (MTP sweep) + 20 (sampler sweep) + 12 (release batteries, 6 per engine) + 6 (depth series)
+ 6 (hero series) + 13 (load checks: 12 single/dual iterations + the 256K check).

- **Warm-up requests were discarded by design** — one per battery and per final compare run.
  They stay visible in their raw files, and they are not counted. (The batteries' warm-ups are
  the `"kind": "warmup"` rows.)
- Rows carrying a `note` in `load-checks.csv` are annotated, not excluded: `dual`'s 8k cell is
  warm-up-contaminated and `single2` was a cold HDD-bound server — both kept because they are
  what the runs actually produced.
- `release-deltas.csv` and `mtp-sweep-summary.csv` rows are **summaries of runs already
  counted** (deltas, means, bands) — they select from the counted set; they are not new runs.

## Derived values (the only numbers not read straight off a run)

| file | column | formula |
|---|---|---|
| sweep tables | `draft_accept_pct_derived` | 100 × draft_acc / draft_n |
| `release-deltas.csv` | `*_delta_pct_derived` | 100 × (0.1.39 value / 0.1.32 value − 1); the `mean` row averages the six **unrounded** deltas, then rounds |
| `mtp-sweep-summary.csv` | means and bands | per-arm mean over the six depths; bands are min/max across that stage's arms |

Everything else is copied cell-for-cell from the raw records or the logs.

## What is not here, and why

- **One single-card attempt is missing from the logs.** An 8k run before `single2` (recorded in
  the set-up session at 26.8 tok/s) was not captured to a log file; its repeat is `single2` and
  that is what the tables use.
- **The hero card was a one-off render.** Its plotting script was not retained; the other three
  figures regenerate from `data/csv/` via `scripts/`.
- **The full engine log stays on the box.** Only the per-request lines for the two 250K runs and
  sampled cache-hit lines are extracted, in `engine-log-extracts.txt`, with the grep documented
  by the experiment that cites them.
- **Bring-up context has no per-run file.** The storage work behind experiment 01 happened
  through ad-hoc requests; the rules it produced are documented there and in `HARDWARE.md`.

## Housekeeping

- No credentials, private hostnames or personal data are in this repo. The box is referred to as
  "box .5"; absolute paths appear only where needed to reproduce a result.
- The source write-ups for these experiments also live in a private knowledge vault and are used
  with their author's consent — the runs, the box and the data are all his.
