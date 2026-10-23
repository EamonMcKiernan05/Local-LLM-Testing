#!/bin/bash
set -u
LOG=/home/eamon/ds4-bench.log
DONE=/home/eamon/ds4-bench.done
rm -f "$DONE"
exec > "$LOG" 2>&1
say(){ echo "[$(date -u +%FT%TZ)] $*"; }
say "=== DS4 bench cycle start ==="
cd /home/eamon/model-bench || exit 1
export MODEL_BENCH_GGUF=/mnt/nvme/maya-ds4/Maya-S/DeepSeek-V4.1-Flash-1017-Maya-S-IQ2_XXS-00001-of-00006.gguf
export MODEL_BENCH_PACK=/mnt/nvme/maya-ds4/Maya-S/maya-ds4/tokenizer
PY=/home/eamon/Strata/.venv/bin/python

bench(){
  say "START $1"
  $PY bench.py --url http://127.0.0.1:8080 --label "$1"
  rc=$?
  if [ $rc -ne 0 ]; then say "FAIL $1 rc=$rc"; echo "FAIL $1" > "$DONE"; exit 1; fi
  say "DONE $1"
}

wait_ready(){
  for i in $(seq 1 150); do
    if curl -s -m 3 http://127.0.0.1:8080/v1/models | grep -q 'deepseek-v4.1'; then say "ready after $((i*5))s"; return 0; fi
    sleep 5
  done
  say "NOT READY"; return 1
}

wait_ready || { echo "NOT READY" > "$DONE"; exit 1; }
bench ds4-maya-s-128k-burn
bench ds4-maya-s-128k-run1

say "restart for run2"
PID=$(pgrep -f '[m]aya.py --config .*maya-ds4.json' | head -1)
say "killing maya.py pid=$PID"
kill -TERM "$PID" 2>/dev/null
for i in $(seq 1 60); do pgrep -f '[m]aya.py --config .*maya-ds4.json' >/dev/null || break; sleep 2; done
sleep 6
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader
setsid -f bash -c 'cd /home/eamon/project-maya && exec ./run-maya-ds4.sh > /home/eamon/maya-ds4-start2.log 2>&1 < /dev/null'
wait_ready || { echo "NOT READY 2" > "$DONE"; exit 1; }
bench ds4-maya-s-128k-run2
say "ALL DONE"
echo OK > "$DONE"
