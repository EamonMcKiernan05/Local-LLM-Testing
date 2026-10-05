# Hardware, models and flags

> **Era note:** everything in this folder was measured on the 2× Tesla V100 32 GB configuration,
> 2026-09-30 to 2026-10-04. This is the box as it serves today; the earlier two-and-three-card
> RTX 3060 era is a different dataset, in [`../qwen3.8-27b-llama-cpp/`](../qwen3.8-27b-llama-cpp/).

## The box

| item | value |
|---|---|
| Host | single desktop/workstation build (`eamon-ai`), inference only |
| Board | MACHINIST X99-MR9A PRO MAX, single socket |
| CPU | Intel Xeon E5-2680 v4, 14 cores / 28 threads |
| RAM | 32 GB DDR4-2400 (31 GB visible to the OS) |
| Cards | 2× Tesla V100-PCIE-32GB, PCIe 3.0 ×16 each, linked through the PCIe host bridge (no NVLink) |
| OS | Ubuntu 24.04.5 LTS (fresh install 2026-09-26; kernel 6.8.0-146) |
| Driver | NVIDIA 580.178.04 (proprietary, apt-held — the last branch that supports Volta) |
| CUDA | 12.9.86 (`/usr/local/cuda-12.9`) |
| Storage | 2 TB HDD at `/mnt/models` (cold catalogue) + 235 GB NVMe (hot model set, root LV extended 98 → 232 GB on 2026-10-03) |

## Storage policy — the rule that made this box fast

Strata reads its 28.8 GB n-gram table (the "PLE" shard) with **random unbuffered reads per
token**. On the spinning HDD that measured ~80 ms per read and pinned decode at **12.8 tok/s**;
on the NVMe it is ~0.1 ms and decode runs **62–65 tok/s**. That is the 4.9× this box's history
turns on (experiment 01).

The policy: **the actively-used model files live on the NVMe; the HDD is a cold catalogue.**

- Hot set: `/home/eamon/strata-nvme/` (base pack + shard 1), `/home/eamon/strata-ple/` (the
  n-gram shard). Symlinks at the standard `/mnt/models` paths; the HDD originals kept beside as
  `.hdd-original`.
- **Symlink, don't repoint.** The loader discovers shards by exact-path probe from `--native`
  and appends `--ple-gguf` only when the string differs — a config pointing at a new path while
  shard 2 still exists beside shard 1 loads three shards, two of them #2, and dies with
  `native dense: duplicate split shard number`. Swap the file for a symlink; keep config paths
  standard.
- Regression check: decode under ~30 tok/s means the PLE reads are slow again — check the
  storage type of every path the engine reads randomly.

## Strata on this box

Strata is `github.com/Niko1221/Strata` — MIT, runs the model split across GPU VRAM + a large
n-gram table on SSD, serves an OpenAI + Anthropic compatible API and a web app. On Volta
(sm_70) it runs the upstream **experimental** path — not officially supported; this box carries
a locally built engine.

| version | when | notes |
|---|---|---|
| v0.1.30 | installed 2026-09-30 | first install; single card, low-RAM mode |
| v0.1.32 | 2026-10-01 | the sm_70 prompt-attn workaround becomes mandatory (`STRATA_PROMPT_ATTN_OLD=1`, upstream #371) |
| v0.1.39 | 2026-10-04 | +22–31 % decode / +23–26 % prefill (experiment 06); vision enabled same day (experiment 07) |

- Build: local, CUDA 12.9, `archs [70]` only — there is no sm_70 prebuilt (setup compiles it,
  `STRATA_EXPERIMENTAL_SM60=1` admits the V100 and adds `-DSTRATA_EXPERIMENTAL_SM60=ON`).
- Layout under `/home/eamon/Strata/`: `engine-cuda12/strata` + `engine-cuda12/strata-vision`
  (the v0.1.39 CUDA-12 layout the benchmarks ran on); `engine/strata` kept from the first
  install; the JSON config the benchmarks ran on is `strata-iq3_s.json`, with the engine log
  beside it.
- Start/stop: hand-started (no systemd unit). `~/strata-start.sh` sets both sm_70 env flags
  around the launch; wait on `curl http://127.0.0.1:8080/v1/models` — grepping the log for
  "ready" can hit banner text. Stop: `kill -TERM <serve/server.py pid>`; verify VRAM drops.
  Every response carries a `timings` object, and the engine log prints a per-request line —
  that line is the authoritative readout; quote it rather than retyping.

## The model set

| set | quant | files | used for |
|---|---|---|---|
| `Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S ISTA-DASLab/` | IQ3_S | 54.8 + 28.8 GB (2 shards) | everything in this repo; serving on both cards |

Packs (the expert arena, built at install) at `/mnt/models/Strata-data/packs/iq3_s`; the MTP
draft layer at `/mnt/models/Strata-data/mtp/rt`. The n-gram shard (28.8 GB) lives on the NVMe
at `/home/eamon/strata-ple/`.

## Flag sets

### Base — the serving config the benchmarks ran on

```
--pack /mnt/models/Strata-data/packs/iq3_s
--native ".../Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf"
--ple-gguf ".../Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf"
--expert-profile /home/eamon/Strata/data/expert-profile.bin
--expert-cache auto --prefill auto
--spec 4 --spec-min-p 0.5
--mtp /mnt/models/Strata-data/mtp/rt
--max-context 262144 --kv int8 --mmap-experts
--vision --vram-reserve-mib 700 --remote-expert-opt
```

Two-card layer split (`gpus 0,1`), `host 0.0.0.0`, port 8080, ctx 262144.

## Measurement

Newer numbers come from **model-bench** (the `Local-AI-Speed-Test-Harness` —
`github.com/EamonMcKiernan05/Local-AI-Speed-Test-Harness`, web UI on `:8090` on the box): a
fixed six-depth battery, prompts sliced to exact token counts with the pack tokenizer, a unique
tag per request (no prefix-cache reuse), a discarded warm-up, prefill/decode read from the
server's own `timings`. Older numbers come from the drivers in [`data/raw/`](data/raw/), each of
which logs the engine's response verbatim.
