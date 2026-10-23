#!/bin/bash
# stage 3: start Maya-XS, burn battery (discarded, warms caches), full run 1, restart, full run 2.
set -u
LOG=/home/eamon/xs-bench.log
DONE=/home/eamon/xs-bench.done
rm -f "$DONE"
exec > "$LOG" 2>&1
say(){ echo "[$(date -u +%FT%TZ)] $*"; }
fail(){ say "FAIL: $*"; echo "FAIL $*" > "$DONE"; exit 1; }

export MODEL_BENCH_GGUF=/mnt/nvme/maya-ds4/Maya-XS/DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00001-of-00005.gguf
export MODEL_BENCH_PACK=/mnt/nvme/maya-ds4/Maya-XS/maya-ds4/tokenizer
PY=/home/eamon/Strata/.venv/bin/python

say "=== stage 3 start: Maya-XS bench ==="
[ -f "$MODEL_BENCH_PACK/chat_template.jinja" ] || fail "pack tokenizer missing"
[ -f /home/eamon/project-maya/maya-ds4.json ] || fail "config missing"

wait_ready(){
  for i in $(seq 1 180); do
    if curl -s -m 3 http://127.0.0.1:8080/v1/models | grep -q 'deepseek-v4.1'; then
      say "ready after $((i*5))s"; return 0
    fi
    sleep 5
  done
  say "NOT READY"; return 1
}
bench(){
  say "START $1"
  ( cd /home/eamon/model-bench && $PY bench.py --url http://127.0.0.1:8080 --label "$1" )
  rc=$?
  [ "$rc" -eq 0 ] || fail "bench $1 rc=$rc"
  say "DONE $1"
}
restart(){
  local pid
  pid=$(pgrep -f '[m]aya.py --config .*maya-ds4.json' | head -1)
  say "killing maya.py pid=${pid:-none}"
  [ -n "${pid:-}" ] && kill -TERM "$pid"
  for i in $(seq 1 90); do pgrep -f '[m]aya.py --config .*maya-ds4.json' >/dev/null || break; sleep 2; done
  sleep 8
  nvidia-smi --query-gpu=index,memory.used --format=csv,noheader
  setsid -f bash -c 'cd /home/eamon/project-maya && exec ./run-maya-ds4.sh > /home/eamon/maya-ds4-start.log 2>&1 < /dev/null'
}

# fresh load #1
say "--- starting server"
setsid -f bash -c 'cd /home/eamon/project-maya && exec ./run-maya-ds4.sh > /home/eamon/maya-ds4-start.log 2>&1 < /dev/null'
wait_ready || fail "not ready (load 1)"
say "=== engine facts (load 1) ==="
grep -E 'tensor parallel|routed experts on the CPU lane|CUDA[01] layers' /home/eamon/project-maya/maya-ds4.log | tail -6

bench ds4-maya-xs-128k-burn
bench ds4-maya-xs-128k-run1

say "--- restart for run2"
restart
wait_ready || fail "not ready (load 2)"
say "=== engine facts (load 2) ==="
grep -E 'tensor parallel|routed experts on the CPU lane|CUDA[01] layers' /home/eamon/project-maya/maya-ds4.log | tail -4

bench ds4-maya-xs-128k-run2

say "=== final: server left running as served ==="
curl -s http://127.0.0.1:8080/v1/models
say "ALL DONE"
echo OK > "$DONE"
