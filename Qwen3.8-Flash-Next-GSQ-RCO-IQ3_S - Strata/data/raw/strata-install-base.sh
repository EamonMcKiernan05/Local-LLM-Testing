#!/bin/bash
# Strata install/re-setup for .5: BASE (non-Coder) Qwen3.8-Flash-Next IQ3_S, low-RAM auto, data on the big
# disk, engine built locally if needed, no start. Reuses the GGUFs already in /mnt/models.
# 2026-10-04: vision ON (GPU encoder, mmproj in the gguf dir); engine now lives in engine-cuda12/
# (the v0.1.39 CUDA-12 layout for Volta). A re-run REGENERATES the config's args - keep every setting here
# in sync with what the model should run, and stop the server first.
export STRATA_EXPERIMENTAL_SM60=1
cd /home/eamon/Strata || exit 1
./setup.sh \
  --setup \
  --family qwen \
  --model IQ3_S \
  --context 262144 \
  --kv int8 \
  --vision gpu \
  --gpus 0,1 \
  --cuda 12 \
  --gguf-dir "/mnt/models/Qwen3.8-Flash-Next/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S ISTA-DASLab" \
  --data-dir /mnt/models/Strata-data \
  --host 0.0.0.0 \
  --port 8080 \
  --build \
  --yes \
  --no-start
rc=$?
echo "INSTALL_EXIT=$rc"
