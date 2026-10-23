# Serving, setup and bench drivers — Maya-XS run, 2026-10-22

Byte-identical copies from box .5, collected 2026-10-23. Hashes in `SHA256SUMS`.

| file | what it is |
|---|---|
| `xs-stage1.sh` / `xs-stage1.log` | download of the 276.6 GB Maya-XS set — weights to the NVMe, the Engram pair to the SATA SSD, with per-file checks |
| `xs-stage2.sh` / `xs-stage2.log` | update to **v1.1.22**, DSpark download + sha256 check, pack build, and the speed calibration that chose `--dspark none` (13.9 vs 11.7 tok/s) |
| `xs-stage3.sh` / `xs-stage3.log` | the bench cycle — readiness gate, engine-facts capture at each load, burn + run1 on load 1, kill + relaunch, run2 on load 2. This file is the box's `~/xs-bench.log` |
| `run-maya-ds4.sh` | the launcher: starts the dashboard + API on `:8080` from `maya-ds4.json` |

The stage-3 log is the most useful record here: it holds the engine's own start lines for both
loads — the tensor-parallel reduction, the per-card VRAM split, and the CPU-lane expert count
(7,928 experts / 54.8 GB) — next to every arm's tok/s as the harness printed it.

## The serving config is not archived

The live `~/project-maya/maya-ds4.json` on the box was rewritten on **2026-10-23** for the vision
pack and the v1.1.25 speed calibration, so the JSON these runs used no longer exists on disk. What
the runs were served with:

- engine **v1.1.22**, `maya-ds4` backend, 131,072 context, `--gpus 0,1`, `--no-vision` at setup
- `--tp 2` in the config — reduced to 1 by the engine at every start (`tensor parallel 2 -> 1`), one
  layer group per card; the write-up carries the source line and the block-arithmetic reason
- `--dspark none` — the XS drafter was downloaded, checked and measured slower (11.7 vs 13.9 tok/s)
- config sampling `temperature 1.0, top_p 1.0`; the harness pins **temp 0.5 / seed 12345** per
  request, so the measured arms do not use the config's sampling values
