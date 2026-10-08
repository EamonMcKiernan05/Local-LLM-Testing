#!/bin/bash
# Maya v1.0.9 re-bench, same protocol as the last run (2026-10-07T2042Z-maya-s-v2-64k-tuned): restart, then the identical bench.
exec > /home/eamon/maya-bench-v109.log 2>&1
echo "=== maya v1.0.9 bench $(date -Is) ==="
rm -f /home/eamon/maya-bench-v109.done
fail() { echo "!!! FAILED: $1"; echo 1 > /home/eamon/maya-bench-v109.done; exit 1; }

echo "--- vram/temps before stop:"; nvidia-smi --query-gpu=index,memory.used,temperature.gpu --format=csv,noheader

echo "--- stop maya ---"
P=$(pgrep -f "project-maya/serve/server.py" | head -1)
if [ -n "${P:-}" ]; then kill -TERM "$P"; fi
sleep 10
if pgrep -f "project-maya/serve/server.py" >/dev/null; then kill -9 $(pgrep -f "project-maya/serve/server.py") 2>/dev/null; sleep 4; fi
pgrep -f "project-maya/serve/server.py" >/dev/null && fail "server will not die"

echo "--- start maya ---"
cd /home/eamon/project-maya || fail "cd project-maya"
setsid ./run-maya-maya-s-v2-iq2_xxs.sh </dev/null > /home/eamon/maya-start-bench109.log 2>&1 &
ok=0
for i in $(seq 1 120); do
  if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then ok=1; echo "ready after ~$((i*5))s"; break; fi
  sleep 5
done
[ "$ok" = 1 ] || fail "maya not ready"
curl -s --max-time 5 http://127.0.0.1:8080/v1/models | grep -o "\"n_ctx\": [0-9]*" | head -1

echo "--- bench ---"
cd /home/eamon/model-bench || fail "cd model-bench"
export MODEL_BENCH_GGUF="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf"
export MODEL_BENCH_PACK="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs/pack/tokenizer"
/home/eamon/Strata/.venv/bin/python bench.py --url http://127.0.0.1:8080 --label maya-s-v2-64k-v109 --depths 20k,40k,60k
rc=$?
echo "=== bench rc=$rc $(date -Is) ==="
echo "$rc" > /home/eamon/maya-bench-v109.done
