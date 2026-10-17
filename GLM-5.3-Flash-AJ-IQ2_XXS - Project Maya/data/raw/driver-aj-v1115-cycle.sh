#!/bin/bash
# maya-aj-v1115-cycle-2026-10-17.sh
# Controlled 3+3 alternated pair on aj9o9's AJ-IQ2_XXS (no MTP block), 262144 ctx,
# v1.1.13 (last version tested) vs v1.1.15 (current release). Six standard depths,
# one battery per fresh load, order O N O N O N. Then restore the Nemotron llama-server.
# STOP file /home/eamon/maya-aj-v1115-cycle-STOP skips remaining arms, still restores.
set -u
LOG=/home/eamon/maya-aj-v1115-cycle.log
DONE=/home/eamon/maya-aj-v1115-cycle.done
STOPF=/home/eamon/maya-aj-v1115-cycle-STOP
BASE=/home/eamon/maya-aj-v1115
PM=/home/eamon/project-maya
ELOG="$PM/maya-aj-iq2_xxs.log"
CFG="$PM/maya-aj-iq2_xxs.json"
MD="/mnt/models/GLM-5.3-Flash-AJ-IQ2_XXS-GGUF"
RUN_AJ=./run-maya-aj-iq2_xxs.sh
BENCHGGUF="$MD/GLM-5.3-Flash-AJ-IQ2_XXS-00001-of-00002.gguf"
BENCHPACK="$MD/pack/tokenizer"
STAMP_OLD=c823b8ca185405dd
mkdir -p "$BASE"
exec > "$LOG" 2>&1
rm -f "$DONE"
fail(){ echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say(){ echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
stamp(){ grep -o '"src": "[0-9a-f]*"' "$PM/build/MAYA-BUILD.json" | head -1 | cut -d'"' -f4; }

wait_vram_free() { local i V; for i in $(seq 1 90); do V=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END {print s+0}'); [ "$V" -lt 1500 ] && return 0; sleep 2; done; return 1; }

stop_maya() {
  local p i
  p=$(pgrep -f 'project-maya/[s]erve/server.py' | head -1 || true)
  if [ -n "$p" ]; then
    echo "stopping maya server pid $p"; kill -TERM "$p"; sleep 8
    for i in $(seq 1 45); do pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1 || break; sleep 2; done
    if pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1; then
      p=$(pgrep -f 'project-maya/[s]erve/server.py' | head -1); echo "escalate kill -9 $p"; kill -9 "$p" 2>/dev/null; sleep 5
    fi
    pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1 && fail "maya server will not die"
  else
    echo "no maya server running"
  fi
  wait_vram_free || fail "vram not released after maya stop"
  echo "vram: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
  ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port 8080 still listening"
}

stop_llama() {
  local p i
  p=$(pgrep -f 'llama.cpp/build/bin/[l]lama-server' | head -1 || true)
  [ -z "$p" ] && { echo "no llama-server running"; return 0; }
  echo "stopping llama-server pid $p (Nemotron; argv saved for restore)"
  kill -TERM "$p"; sleep 5
  for i in $(seq 1 60); do pgrep -f 'llama.cpp/build/bin/[l]lama-server' >/dev/null 2>&1 || break; sleep 2; done
  if pgrep -f 'llama.cpp/build/bin/[l]lama-server' >/dev/null 2>&1; then
    p=$(pgrep -f 'llama.cpp/build/bin/[l]lama-server' | head -1); echo "escalate kill -9 $p"; kill -9 "$p" 2>/dev/null; sleep 5
  fi
  pgrep -f 'llama.cpp/build/bin/[l]lama-server' >/dev/null 2>&1 && fail "llama-server will not die"
  wait_vram_free || fail "vram not released after llama-server stop"
  ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port 8080 still listening after llama stop"
  echo "llama-server stopped; vram: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
}

start_arm() {  # $1 side (old|new)  $2 tag  $3 rep
  local side="$1" tag="$2" rep="$3" i ok=0 before t0 t1 st ep got v arm file_cfg
  arm="$side$rep"
  cd "$PM" || fail "cd $PM"
  git checkout -q "$tag" || fail "checkout $tag"
  v=$(cat VERSION)
  echo "checked out $tag (VERSION $v)"
  [ "$v" = "${tag#v}" ] || fail "VERSION $v != $tag"
  file_cfg="$BASE/cfg-$side.json"
  if [ -f "$file_cfg" ]; then cp -f "$file_cfg" "$CFG" || fail "restore cfg-$side"; echo "config restored to the $side snapshot"; fi
  grep -q '262144' "$CFG" || fail "config not 262144"
  ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port 8080 busy before start ($arm)"
  [ -f "$ELOG" ] || touch "$ELOG"
  before=$(wc -l < "$ELOG")
  t0=$(date +%s)
  echo "--- launching $RUN_AJ ($arm, $tag) at $(date -u)"
  setsid -f bash -c "cd $PM && exec $RUN_AJ > $BASE/start-$arm.log 2>&1 < /dev/null"
  for i in $(seq 1 900); do
    if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then ok=1; break; fi
    sleep 4
  done
  [ "$ok" = 1 ] || fail "maya not ready ($arm)"
  t1=$(date +%s); echo "api up after ~$((t1-t0))s ($arm)"
  grep -q "port 8080 is already in use" "$BASE/start-$arm.log" && fail "port-in-use marker ($arm)"
  grep -q "compiled before" "$BASE/start-$arm.log" && fail "soft compile-failure marker ($arm)"
  [ "$((t1-t0))" -ge 60 ] || fail "suspiciously fast ready ($((t1-t0))s) ($arm)"
  got=$(curl -s --max-time 8 http://127.0.0.1:8080/v1/models | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"][0]["meta"]["n_ctx"])' 2>/dev/null)
  echo "n_ctx: $got (want 262144)"; [ "$got" = "262144" ] || fail "n_ctx $got ($arm)"
  st=$(stamp); echo "engine src stamp: $st"
  if [ "$side" = new ]; then
    if [ -f "$BASE/stamp-new.txt" ]; then
      [ "$st" = "$(cat "$BASE/stamp-new.txt")" ] || fail "new-side stamp drifted ($arm): $st"
    else
      echo "$st" > "$BASE/stamp-new.txt"
    fi
    [ "$st" = "$STAMP_OLD" ] && fail "new side is running the OLD engine ($arm)"
  else
    [ "$st" = "$STAMP_OLD" ] || fail "old-side stamp not $STAMP_OLD ($arm): $st"
  fi
  echo "markers since arm start: glm mtp=$(tail -n +"$before" "$ELOG" | grep -cE 'glm mtp' || true) dflash=$(tail -n +"$before" "$ELOG" | grep -cE 'glm dflash' || true)"
  tail -n +"$before" "$ELOG" | grep -m2 'glm split:' || true
  tail -n +"$before" "$ELOG" | grep -m2 'prompt attention on the' || true
  tail -n +"$before" "$ELOG" | grep -m1 'glm pack: CUDA0 dense weights' || true
  ep=$(pgrep -f 'project-maya/build/[s]trata --glm-pack' | head -1 || true)
  [ -n "$ep" ] && { echo "engine pid $ep"; tr '\0' '\n' < "/proc/$ep/environ" | grep STRATA || true; }
  if [ ! -f "$file_cfg" ]; then
    cp "$CFG" "$file_cfg"; md5sum "$CFG" > "$BASE/cfg-$side.md5"
    echo "config snapshot taken for $side: $(cat "$BASE/cfg-$side.md5")"
  fi
  md5sum -c "$BASE/cfg-$side.md5" || fail "config drifted during start ($arm)"
  echo "start gates done ($arm)"
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

bench() {  # $1 label  $2 arm
  local label="$1" arm="$2" rc RD
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
  echo "$(date -u) $arm rundir=$RD" >> "$BASE/timeline.txt"
  cp -a "$RD" "$BASE"/ || true
  grep -E 'glm stat:' "$ELOG" | tail -20 > "$BASE/stats-$arm.txt" || true
  tail -3 "$BASE/stats-$arm.txt" || true
}

# ---------- 0. preflight ----------
say "--- [0] preflight"
pgrep -f 'project-maya/[s]erve/server.py' >/dev/null 2>&1 && fail "a maya server is running"
stop_llama
[ -f "$CFG" ] || fail "AJ config missing"
[ -d "$MD" ] && [ -L "$MD" ] || fail "AJ model dir is not the NVMe symlink"
grep -q '262144' "$CFG" || fail "AJ config is not 262144"
mountpoint -q /home/eamon/maya-nvme || fail "maya-nvme bind missing"
say "--- update checkout v1.1.15"
cd "$PM" && git checkout -q v1.1.15 || fail "checkout v1.1.15"
cat VERSION
say "preflight OK"

# ---------- 1-6. alternated arms ----------
ARMS=("old v1.1.13 1" "new v1.1.15 1" "old v1.1.13 2" "new v1.1.15 2" "old v1.1.13 3" "new v1.1.15 3")
for a in "${ARMS[@]}"; do
  set -- $a; side=$1; tag=$2; rep=$3
  arm="$side$rep"
  if [ -f "$STOPF" ]; then say "STOP file present - skipping remaining arms"; break; fi
  say "--- arm $arm ($tag rep $rep)"
  start_arm "$side" "$tag" "$rep"
  warmup
  label="aj-iq2xxs-256k-v$(echo "${tag#v}" | tr -d '.')-r$rep"
  bench "$label" "$arm"
  stop_maya
  echo "OK" > "$BASE/stage-$arm.done"
done

# ---------- 7. restore the Nemotron llama-server ----------
say "--- [restore] Nemotron llama-server"
if [ -f /home/eamon/nemotron-restore-argv-2026-10-17.txt ]; then
  NEM=$(cat /home/eamon/nemotron-restore-argv-2026-10-17.txt)
  setsid -f bash -c "cd /home/eamon && exec $NEM > /home/eamon/nemotron-server-restored-2026-10-17.log 2>&1 < /dev/null"
  ok=0
  for i in $(seq 1 180); do
    if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models 2>/dev/null | grep -q 'owned_by'; then ok=1; break; fi
    sleep 5
  done
  if [ "$ok" = 1 ]; then echo "nemotron API up"; curl -s -m 5 http://127.0.0.1:8080/v1/models | head -c 300; echo; else echo "!!! nemotron restore not answering yet"; fi
else
  echo "no saved argv - leaving the box stopped"
fi
say "--- finish"
cd "$PM" && git checkout -q v1.1.15
echo "=== aj v1.1.13 vs v1.1.15 cycle done $(date -u) ==="
echo 0 > "$DONE"
