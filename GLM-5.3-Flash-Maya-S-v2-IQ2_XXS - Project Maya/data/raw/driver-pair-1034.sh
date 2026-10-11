#!/bin/bash
# Maya on .5: update to v1.0.34, then same-day pair v1.0.9 vs v1.0.34 at 64k (three depths).
# Supersedes the earlier v1.0.33 pair (Eamon: scrap that for now). Mirror of the morning protocol.
set -u
LOG=/home/eamon/maya-pair-1034.log
DONE=/home/eamon/maya-pair-1034.done
exec > "$LOG" 2>&1
rm -f "$DONE"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
PM=/home/eamon/project-maya
V109_SRC="2b852534a0789476"
echo "=== maya update v1.0.34 + pair started $(date -u) ==="

stop_maya() {
  local p V i
  p=$(pgrep -f 'project-maya/[s]erve/server.py' | head -1 || true)
  [ -n "$p" ] && { echo "stopping maya server pid $p"; kill -TERM "$p"; }
  sleep 8
  for i in $(seq 1 45); do pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1 || break; sleep 2; done
  if pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1; then
    p=$(pgrep -f 'project-maya/[s]erve/server.py' | head -1); echo "escalate kill -9 $p"; kill -9 "$p" 2>/dev/null; sleep 5
  fi
  pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1 && fail "server will not die"
  for i in $(seq 1 60); do
    V=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END {print s+0}')
    [ "$V" -lt 1500 ] && break
    sleep 2
  done
  echo "stopped; vram: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
}
start_plain() {  # $1 tag; plain ./setup.sh (soft-recompiles when the source changed, then starts)
  cd "$PM" || fail "cd project-maya"
  setsid -f bash -c "cd $PM && exec ./setup.sh > /home/eamon/maya-pair-1034-start-$1.log 2>&1 < /dev/null"
  local i ok=0
  for i in $(seq 1 140); do
    if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then ok=1; break; fi
    sleep 5
  done
  [ "$ok" = 1 ] || fail "maya not ready ($1)"
  echo "ready after ~$((i*5))s ($1)"
  curl -s --max-time 5 http://127.0.0.1:8080/v1/models | head -c 250; echo
}
stamp() { grep -o '"src": "[0-9a-f]*"' "$PM/build/MAYA-BUILD.json" | head -1 | cut -d'"' -f4; }
bench() {  # $1 label
  cd /home/eamon/model-bench || fail "cd model-bench"
  export MODEL_BENCH_GGUF="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf"
  export MODEL_BENCH_PACK="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs/pack/tokenizer"
  /home/eamon/Strata/.venv/bin/python bench.py --url http://127.0.0.1:8080 --label "$1" --depths 20k,40k,60k
  local rc=$?
  echo "bench $1 rc=$rc $(date -u)"
  [ "$rc" = 0 ] || fail "bench $1 rc=$rc"
}

echo "--- [1] update to v1.0.34 ($(date -u))"
cd "$PM" || fail "cd"
stop_maya
git fetch origin --tags --force || fail "fetch"
git merge --ff-only origin/main || fail "merge ff-only"
git log -1 --format="HEAD: %h %s"
echo "VERSION: $(cat VERSION)"
[ "$(cat VERSION)" = "1.0.34" ] || fail "VERSION is not 1.0.34"
./setup.sh --setup --no-start --yes --context 65536 --host 0.0.0.0 \
  --env STRATA_GLM_TIMING=1 --env STRATA_GLM_POOL_STATS=1 --env STRATA_GLM_RAM_HEADROOM_GB=3
echo "setup rc=$?"
V1034_SRC=$(stamp); echo "v1034 stamp src: $V1034_SRC"
[ -n "$V1034_SRC" ] || fail "no stamp after rebuild"
[ "$V1034_SRC" != "$V109_SRC" ] || fail "stamp equals v109 src?"

echo "--- [2] start v1.0.34, bench ($(date -u))"
start_plain v1034
[ "$(stamp)" = "$V1034_SRC" ] || fail "stamp drift after start ($(stamp))"
bench maya-s-v2-64k-v1034

echo "--- [3] rollback to v1.0.9 (7655730) ($(date -u))"
cd "$PM" || fail "cd"
stop_maya
git checkout 7655730 || fail "checkout 7655730"
git log -1 --format="HEAD: %h %s"
start_plain v109
[ "$(stamp)" = "$V109_SRC" ] || fail "v109 stamp mismatch: $(stamp)"
bench maya-s-v2-64k-v109-rerun2

echo "--- [4] restore v1.0.34 (main) ($(date -u))"
cd "$PM" || fail "cd"
stop_maya
git checkout main || fail "checkout main"
git log -1 --format="HEAD: %h %s"
start_plain v1034b
[ "$(stamp)" = "$V1034_SRC" ] || fail "restore stamp mismatch: $(stamp)"
curl -s --max-time 5 http://127.0.0.1:8080/v1/models | head -c 250; echo
echo "=== update+pair v1.0.34 done $(date -u) ==="
echo 0 > "$DONE"
