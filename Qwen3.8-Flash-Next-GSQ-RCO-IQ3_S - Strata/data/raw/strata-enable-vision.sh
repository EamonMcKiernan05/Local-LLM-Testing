#!/bin/bash
# Enable vision (image encoder) on the base Qwen3.8-Flash-Next IQ3_S model in Strata on box .5.
# Also moves the engine to the v0.1.39 CUDA-12 layout (engine-cuda12/) required for Volta (sm_70):
# setup builds the full engine there plus the strata-vision helper, writes both into the config.
export STRATA_EXPERIMENTAL_SM60=1
cd /home/eamon/Strata || exit 1
./setup.sh \
  --setup \
  --family qwen --model IQ3_S \
  --context 262144 --kv int8 \
  --vision gpu \
  --gpus 0,1 \
  --cuda 12 \
  --gguf-dir "/mnt/models/Qwen3.8-Flash-Next/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S ISTA-DASLab" \
  --data-dir /mnt/models/Strata-data \
  --host 0.0.0.0 \
  --port 8080 \
  --build --yes --no-start
rc=$?
echo "SETUP_EXIT=$rc"
touch /home/eamon/strata-vision-setup.done
exit $rc
