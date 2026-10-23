# Serving and bench drivers — Maya-S run, 2026-10-21

Byte-identical copies from box .5, collected 2026-10-23. Hashes in `SHA256SUMS`.

| file | what it is |
|---|---|
| `run-maya-ds4.sh` | the launcher Maya wrote: starts the dashboard + API on `:8080` from `maya-ds4.json` |
| `ds4-bench-cycle.sh` | the cycle driver — waits for readiness, runs the burn battery, run1, restarts the server, runs run2. Sets `MODEL_BENCH_GGUF` to the Maya-S shard 1 so the harness tokenizes in the model's own vocab |
| `ds4-bench.log` | the driver's full log: readiness, every arm's tok/s as the harness printed it, the restart, the run dirs |
| `maya-ds4-setup.log` | the pack build and first start (`maya.sh --setup …`): GPU check, model registration, pack contents, expert profile |

## The serving config is not archived

The live `~/project-maya/maya-ds4.json` on the box was rewritten on **2026-10-23** for the vision
pack and the v1.1.25 speed calibration, so the JSON these runs used no longer exists on disk.

What the runs were served with is recorded in the write-up and in the model setup log:

- engine **v1.1.19**, `maya-ds4` backend, 131,072 context, `--gpus 0,1`, `--no-vision` at setup
- `--tp 2` in the config — the engine logs `tensor parallel 2 -> 1 … (each GPU its own layers)` and
  runs one layer group per card; see the Maya-XS folder for the block-arithmetic reason
- `--dspark none` (Maya's calibration rejected the drafter: 4.6 vs 6.8 tok/s at short context)
- config sampling `temperature 1.0, top_p 1.0`; the harness pins **temp 0.5 / seed 12345** per
  request, so the measured arms do not use the config's sampling values

The engine log for this load (`~/project-maya/maya-ds4.log`) has since been overwritten by later
loads. The engine-facts lines quoted in the write-up were read from it at the time.
