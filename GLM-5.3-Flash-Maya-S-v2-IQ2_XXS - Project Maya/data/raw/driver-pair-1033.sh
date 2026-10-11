#!/bin/bash
# Maya controlled pair on .5: v1.0.33 (current) vs v1.0.9 (7655730), 64K config, three depths.
# Mirrors the 2026-10-08 pair protocol (driver scripts archived in the repo's data/raw/).
set -u
LOG=/home/eamon/maya-pair-1033.log
DONE=/home/eamon/maya-pair-1033.done
exec > "$LOG" 2>&1
rm -f "$DONE"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
PM=/home/eamon/project-maya
V1033_SRC="13c572a2c0c8d2ef"
V109_SRC="2b852534a0789476"
echo "=== maya pair v1.0.33 vs v1.0.9 started $(date -u) ==="

stop_maya() {
  local p V
  p=$(pgrep -f 'project-maya/[s]erve/server.py' | head -1 || true)
  [ -n "$p" ] && { echo "stopping maya server pid $p"; kill -TERM "$p"; }
  sleep 8
  for i in $(seq 1 45); do
    pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1 || break
    sleep 2
  done
  if pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1; then
    p=$(pgrep -f 'project-maya/[s]erve/server.py' | head -1); echo "escalate: kill -9 $p"; kill -9 "$p" 2>/dev/null; sleep 5
  fi
  pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1 && fail "server will not die"
  for i in $(seq 1 60); do
    V=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END {print s+0}')
    [ "$V" -lt 1500 ] && break
    sleep 2
  done
  echo "stopped; vram: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
}
start_maya() {  # $1 tag, $2 expected src
  cd "$PM" || fail "cd project-maya"
  setsid -f bash -c "cd $PM && exec ./setup.sh > /home/eamon/maya-pair-1033-start-$1.log 2>&1 < /dev/null"
  local i ok=0
  for i in $(seq 1 140); do
    if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then ok=1; break; fi
    sleep 5
  done
  [ "$ok" = 1 ] || fail "maya not ready ($1)"
  echo "ready after ~$((i*5))s ($1)"
  curl -s --max-time 5 http://127.0.0.1:8080/v1/models | head -c 300; echo
  grep -o '"src": "[0-9a-f]*"' "$PM/build/MAYA-BUILD.json" | head -1
  grep -q "$2" "$PM/build/MAYA-BUILD.json" || fail "engine stamp is not $1 (want $2)"
}
bench() {  # $1 label
  cd /home/eamon/model-bench || fail "cd model-bench"
  export MODEL_BENCH_GGUF="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf"
  export MODEL_BENCH_PACK="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs/pack/tokenizer"
  /home/eamon/Strata/.venv/bin/python bench.py --url http://127.0.0.1:8080 --label "$1" --depths 20k,40k,60k
  local rc=$?
  echo "bench $1 rc=$rc $(date -u)"
  [ "$rc" = 0 ] || fail "bench $1 rc=$rc"
}

echo "--- [1] restart v1.0.33, then bench ($(date -u))"
stop_maya
start_maya v1033 "$V1033_SRC"
bench maya-s-v2-64k-v1033

echo "--- [2] rollback to v1.0.9 (7655730) ($(date -u))"
cd "$PM" || fail "cd"
stop_maya
git checkout 7655730 || fail "checkout 7655730"
git log -1 --format="HEAD: %h %s"
start_maya v109 "$V109_SRC"
bench maya-s-v2-64k-v109-rerun

echo "--- [3] restore v1.0.33 (main) ($(date -u))"
cd "$PM" || fail "cd"
stop_maya
git checkout main || fail "checkout main"
git log -1 --format="HEAD: %h %s"
start_maya v1033 "$V1033_SRC"

echo "=== pair done $(date -u) ==="
echo 0 > "$DONE"
