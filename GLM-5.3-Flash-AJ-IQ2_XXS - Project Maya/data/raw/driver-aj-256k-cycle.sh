#!/bin/bash
# maya-aj-iq2xxs-cycle-2026-10-16.sh
# Maya serves aj9o9's AJ-IQ2_XXS (87.35 GB, no MTP block) from the SN730 at 262144 ctx.
# Sequence: postcopy BURN battery (discarded by design) then 3 fresh-load measured batteries (standard six depths
# 20k..250k, default gen 400), then Maya-S restored serving. Adapted from maya-sn730-cycle.sh (proven pattern).
# STOP file /home/eamon/maya-aj-iq2xxs-cycle-STOP skips remaining arms and goes straight to the restore.
set -u
LOG=/home/eamon/maya-aj-iq2xxs-cycle.log
DONE=/home/eamon/maya-aj-iq2xxs-cycle.done
STOPF=/home/eamon/maya-aj-iq2xxs-cycle-STOP
BASE=/home/eamon/maya-aj-iq2xxs
PM=/home/eamon/project-maya
ELOG="$PM/maya-aj-iq2_xxs.log"
MLOG="$PM/maya-maya-s-v2-iq2_xxs.log"
CFG="$PM/maya-aj-iq2_xxs.json"
MSCFG="$PM/maya-maya-s-v2-iq2_xxs.json"
MD="/mnt/models/GLM-5.3-Flash-AJ-IQ2_XXS-GGUF"
RUN_AJ=./run-maya-aj-iq2_xxs.sh
RUN_MS=./run-maya-maya-s-v2-iq2_xxs.sh
EXPECT_STAMP=c823b8ca185405dd
BENCHGGUF="$MD/GLM-5.3-Flash-AJ-IQ2_XXS-00001-of-00002.gguf"
BENCHPACK="$MD/pack/tokenizer"
mkdir -p "$BASE"
exec > "$LOG" 2>&1
rm -f "$DONE"
fail(){ echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say(){ echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
echo "=== maya AJ-IQ2_XXS cycle started $(date -u) UTC ==="

stamp() { grep -o '"src": "[0-9a-f]*"' "$PM/build/MAYA-BUILD.json" | head -1 | cut -d'"' -f4; }

stop_maya() {
  local p i V
  p=$(pgrep -f 'project-maya/[s]erve/server.py' | head -1 || true)
  [ -z "$p" ] && { echo "no maya server running"; return 0; }
  echo "stopping maya server pid $p"; kill -TERM "$p"
  sleep 8
  for i in $(seq 1 45); do pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1 || break; sleep 2; done
  if pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1; then
    p=$(pgrep -f 'project-maya/[s]erve/server.py' | head -1); echo "escalate kill -9 $p"; kill -9 "$p" 2>/dev/null; sleep 5
  fi
  pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1 && fail "maya server will not die"
  for i in $(seq 1 90); do
    V=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END {print s+0}')
    [ "$V" -lt 1500 ] && break
    sleep 2
  done
  echo "stopped; vram: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
  ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port 8080 still listening"
}

start_arm() {  # $1 sfx  $2 run script  $3 want n_ctx  $4 engine log
  local sfx="$1" script="$2" want="$3" elog="$4" i ok=0 before t0 t1 st ep got
  cd "$PM" || fail "cd $PM"
  ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port 8080 busy before start ($sfx)"
  [ -f "$elog" ] || touch "$elog"
  before=$(wc -l < "$elog")
  t0=$(date +%s)
  echo "--- launching $script ($sfx) at $(date -u)"
  setsid -f bash -c "cd $PM && exec $script > $BASE/start-$sfx.log 2>&1 < /dev/null"
  for i in $(seq 1 900); do
    if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then ok=1; break; fi
    sleep 4
  done
  [ "$ok" = 1 ] || fail "maya not ready ($sfx)"
  t1=$(date +%s)
  echo "api up after ~$((t1-t0))s ($sfx)"
  grep -q "port 8080 is already in use" "$BASE/start-$sfx.log" && fail "port-in-use marker ($sfx)"
  [ "$((t1-t0))" -ge 60 ] || fail "suspiciously fast ready ($((t1-t0))s) - stale server? ($sfx)"
  got=$(curl -s --max-time 8 http://127.0.0.1:8080/v1/models | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"][0]["meta"]["n_ctx"])' 2>/dev/null)
  echo "n_ctx: $got (want $want)"; [ "$got" = "$want" ] || fail "n_ctx $got != $want ($sfx)"
  st=$(stamp); echo "engine src stamp: $st"
  [ "$st" = "$EXPECT_STAMP" ] || fail "unexpected engine stamp ($sfx): $st"
  echo "markers since arm start: glm mtp=$(tail -n +"$before" "$elog" | grep -cE 'glm mtp' || true) glm dflash=$(tail -n +"$before" "$elog" | grep -cE 'glm dflash' || true)"
  tail -n +"$before" "$elog" | grep -m2 'glm split:' || true
  tail -n +"$before" "$elog" | grep -m1 'glm pack: CUDA0 dense weights' || true
  ep=$(pgrep -f 'project-maya/build/[s]trata --glm-pack' | head -1 || true)
  [ -n "$ep" ] && { echo "engine pid $ep"; tr '\0' '\n' < "/proc/$ep/environ" | grep STRATA || true; }
  md5sum -c "$BASE/config-md5.txt" || fail "config drifted during start ($sfx)"
  echo "start gates done ($sfx)"
}

warmup() {
  echo "--- warm-up $(date -u)"
  python3 - <<'PY'
import json, urllib.request
try:
    text = open('/home/eamon/project-maya/CHANGELOG.md', encoding='utf-8', errors='ignore').read()
except Exception:
    text = "reference material " * 4000
text = (text * 3)[:80000]
req = json.dumps({"model": "x", "messages": [{"role": "user", "content": "Read.\n\n" + text}], "max_tokens": 4, "temperature": 0}).encode()
try:
    r = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8080/v1/chat/completions", data=req, headers={"Content-Type": "application/json"}), timeout=1800)
    d = json.load(r)
    print("warmup ok: prompt_tokens", d.get("usage", {}).get("prompt_tokens"), "| timings:", d.get("timings"))
except Exception as e:
    print("warmup failed:", e)
PY
}

bench() {  # $1 label  $2 sfx
  local label="$1" sfx="$2" rc RD
  cd /home/eamon/model-bench || fail "cd model-bench"
  export MODEL_BENCH_GGUF="$BENCHGGUF"
  export MODEL_BENCH_PACK="$BENCHPACK"
  /home/eamon/Strata/.venv/bin/python bench.py --url http://127.0.0.1:8080 --label "$label"
  rc=$?
  echo "bench $label rc=$rc $(date -u)"
  [ "$rc" = 0 ] || fail "bench $label rc=$rc"
  RD=$(ls -1dt /home/eamon/model-bench/runs/*"$label" | head -1)
  echo "run dir: $RD"
  grep -m1 'prompts:' "$RD/summary.md" || true
  grep -q 'local tokenizer (exact' "$RD/summary.md" || fail "prompt slicing not exact ($label)"
  echo "$(date -u) $sfx rundir=$RD" >> "$BASE/timeline.txt"
  cp -a "$RD" "$BASE"/ || true
  grep -E 'glm stat:' "$ELOG" | tail -20 > "$BASE/stats-$sfx.txt" || true
  tail -3 "$BASE/stats-$sfx.txt" || true
}

# ---------- 0. preflight ----------
say "--- [0] preflight"
pgrep -f '[s]erve/server.py' >/dev/null 2>&1 && fail "a server is running"
ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port busy"
[ -f "$CFG" ] || fail "AJ config missing"
[ -d "$MD" ] && [ -L "$MD" ] || fail "AJ model dir is not the NVMe symlink"
grep -q '262144' "$CFG" || fail "AJ config is not 262144"
mountpoint -q /home/eamon/maya-nvme || fail "maya-nvme bind missing"
cp -a "$CFG" "$BASE/config-aj-snapshot.json" 2>/dev/null || true
md5sum "$CFG" "$MSCFG" > "$BASE/config-md5.txt"
cat "$BASE/config-md5.txt"
say "preflight OK"

# ---------- 1-4. burn + three measured runs ----------
for stage in burn r1 r2 r3; do
  if [ -f "$STOPF" ]; then say "STOP file present - skipping remaining arms"; break; fi
  case "$stage" in
    burn) label="aj-iq2xxs-256k-sn730-postcopy-burn"; say "--- [burn] postcopy burn battery (discarded by design)";;
    *)    label="aj-iq2xxs-256k-sn730-$stage"; say "--- [run ${stage#r}] $label";;
  esac
  start_arm "$stage" "$RUN_AJ" 262144 "$ELOG"
  warmup
  bench "$label" "$stage"
  stop_maya
  echo "OK" > "$BASE/stage-$stage.done"
done

# ---------- 5. restore Maya-S serving ----------
say "--- [restore] Maya-S serving"
start_arm "restore" "$RUN_MS" 65536 "$MLOG"
curl -s -m 5 http://127.0.0.1:8080/v1/models | head -c 400; echo
say "--- finish"
echo "=== maya AJ cycle done $(date -u) ==="
echo 0 > "$DONE"
