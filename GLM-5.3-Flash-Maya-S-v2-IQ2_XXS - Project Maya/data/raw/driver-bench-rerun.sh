#!/bin/bash
# Maya controlled pair for the v1.0.9 comparison: re-run the PREVIOUS build (142540b) the same day,
# then restore v1.0.9 and leave it serving. Launch only after the v1.0.9 bench marker exists.
exec > /home/eamon/maya-bench-rerun.log 2>&1
echo "=== maya previous-build re-run + restore $(date -Is) ==="
rm -f /home/eamon/maya-bench-rerun.done
OLD_SRC="326ec0d7adf59f7e"     # build/MAYA-BUILD.json src of the 2026-10-07 build (pre-update)
NEW_SRC="2b852534a0789476"     # v1.0.9 build (2026-10-08)
FAIL=""

stop_maya() {
  P=$(pgrep -f "project-maya/serve/server.py" | head -1)
  if [ -n "${P:-}" ]; then kill -TERM "$P"; fi
  sleep 10
  if pgrep -f "project-maya/serve/server.py" >/dev/null; then kill -9 $(pgrep -f "project-maya/serve/server.py") 2>/dev/null; sleep 4; fi
  if pgrep -f "project-maya/serve/server.py" >/dev/null; then echo "!! server still alive"; return 1; fi
  return 0
}
start_maya() {
  setsid bash -c "cd /home/eamon/project-maya && exec ./setup.sh > /tmp/maya-rerun-setup.log 2>&1 < /dev/null" >/dev/null 2>&1 &
}
wait_ready() {
  for i in $(seq 1 140); do
    if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then echo "ready after ~$((i*5))s"; return 0; fi
    sleep 5
  done
  return 1
}
stamp_src() { grep -o "\"src\": \"[0-9a-f]*\"" /home/eamon/project-maya/build/MAYA-BUILD.json | head -1; }

[ -f /home/eamon/maya-bench-v109.done ] || { echo "v109 bench not done - abort"; echo 1 > /home/eamon/maya-bench-rerun.done; exit 1; }

echo "--- stop maya ---"
if ! stop_maya; then echo "stop failed - abort"; echo 1 > /home/eamon/maya-bench-rerun.done; exit 1; fi

echo "--- checkout 142540b (previous build) ---"
cd /home/eamon/project-maya || { echo 1 > /home/eamon/maya-bench-rerun.done; exit 1; }
if git checkout 142540b; then
  git log -1 --format="HEAD: %h %s"
  echo "--- start (recompiles the previous engine) ---"
  start_maya
  if wait_ready; then
    curl -s --max-time 5 http://127.0.0.1:8080/v1/models | grep -o "\"n_ctx\": [0-9]*" | head -1
    echo "stamp now: $(stamp_src)"
    if grep -q "$OLD_SRC" /home/eamon/project-maya/build/MAYA-BUILD.json; then
      echo "--- rerun bench (previous build) ---"
      cd /home/eamon/model-bench || FAIL="cd model-bench"
      export MODEL_BENCH_GGUF="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf"
      export MODEL_BENCH_PACK="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs/pack/tokenizer"
      /home/eamon/Strata/.venv/bin/python bench.py --url http://127.0.0.1:8080 --label maya-s-v2-64k-tuned-rerun --depths 20k,40k,60k || FAIL="bench rc=$?"
    else
      FAIL="engine stamp is not the previous build"
    fi
  else
    FAIL="previous build did not come up"
  fi
else
  FAIL="checkout 142540b failed"
fi

echo "--- restore: stop ---"
stop_maya || FAIL="$FAIL; stop before restore failed"
echo "--- checkout main (v1.0.9) ---"
cd /home/eamon/project-maya
git checkout main || FAIL="$FAIL; checkout main failed"
git log -1 --format="HEAD: %h %s"
echo "--- start (recompiles v1.0.9) ---"
start_maya
if wait_ready; then
  curl -s --max-time 5 http://127.0.0.1:8080/v1/models | grep -o "\"n_ctx\": [0-9]*" | head -1
  echo "stamp now: $(stamp_src)"
  grep -q "$NEW_SRC" /home/eamon/project-maya/build/MAYA-BUILD.json || FAIL="$FAIL; restore stamp mismatch"
  echo "VERSION: $(cat VERSION 2>/dev/null)"
else
  FAIL="$FAIL; restore did not come up"
fi

if [ -n "$FAIL" ]; then echo "=== DONE WITH FAILURES: $FAIL ($(date -Is)) ==="; echo "1" > /home/eamon/maya-bench-rerun.done
else echo "=== rerun+restore OK done $(date -Is) ==="; echo "0" > /home/eamon/maya-bench-rerun.done; fi
