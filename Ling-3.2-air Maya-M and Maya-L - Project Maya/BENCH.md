# Ling-3.2-air · Maya-M and Maya-L — Project Maya v1.1.83 on 2× V100 32 GB

First run of inclusionAI's Ling-3.2-air on box .5 through Maya's own engine (`maya-ling`), with
Maya's own quants, at the maximum context the machine will hold.

## Result

| quant | file size | depth | prompt tokens | prefill tok/s | decode tok/s |
|---|---:|---:|---:|---:|---:|
| Maya-M (IQ2_S) | 46.0 GB | 8K | 8,899 | **2,730.8** | **103.2** |
| Maya-M | | 64K | 61,846 | 2,154.3 | 61.9 |
| Maya-M | | 200K | 254,743 | 905.6 | 25.7 |
| Maya-L (IQ3_S) | 59.2 GB | 8K | 8,899 | **2,567.4** | **103.1** |
| Maya-L | | 64K | 61,846 | 2,083.8 | 58.9 |
| Maya-L | | 200K | 254,743 | 923.3 | 24.7 |

Chart: `ling32air-code-speed.png`.

The 200K point is a 254,743-token prompt — 97% of the 262,144-token maximum — and it completed, so
the full context fits on this box. Between the two quants the difference is inside run-to-run noise:
the larger file buys quality, not speed, because at 256K the planner keeps ~98% of the experts in
VRAM for both (Maya-M: 23.2 + 25.9 GB across the two cards; Maya-L: 50.2 GiB VRAM + 23.1 GiB RAM,
0.2 GiB streamed from the SSD).

## How it was measured

- Maya v1.1.83, `--gpus 0,1 --max-context 262144 --kv fp16 --drafting auto`, pictures on.
- `~/model-bench/bench.py --backend openai --corpus code --depths 8k,64k,200k --reps 1 --gen 128`
  against Maya's OpenAI endpoint at `127.0.0.1:8080`. Code corpus = real source trees; temperature
  0.5 (the harness default), so decode carries sampling.
- Prefill is the prompt read (Maya reports it separately from decode), decode is the answer written
  over 128 generated tokens. One rep per depth: these are single measurements, not medians.
- Both quants: `--max-context 262144` set by `./maya.sh --setup --context 262144`. Maya's planner
  warns that Maya-L at 256K "will run slowly" (it keeps 23.1 GiB in system RAM); the box has 32 GB
  and is inference-only, so that was accepted.
- Maya-M lives on `/mnt/nvme2` (46 GB), Maya-L on `/mnt/nvme` (59.2 GB).

## Notes

- Download came from Maya's own pinned manifest (`tools/ling/download.json`, sha256 checked).
- Inkling 2 Mini was idle for 5 minutes before the switch, per instruction; it is stopped while
  Ling-3.2-air holds both cards (the model needs both V100s).
- Not measured: drafting on/off A/B, concurrency above 1, and Maya's own `--bench` (it wants Maya
  stopped and uses docs prompts, not code).
