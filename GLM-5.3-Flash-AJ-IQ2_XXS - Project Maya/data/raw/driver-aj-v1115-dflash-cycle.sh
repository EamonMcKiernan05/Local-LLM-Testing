#!/bin/bash
# maya-aj-v1115-dflash-cycle-2026-10-17.sh
# AJ-IQ2_XXS on Maya v1.1.15 with the DFlash2 drafter (--dflash), 262144 ctx,
# three fresh-load batteries, same six standard depths as the v1.1.13/v1.1.15 pair.
# Restores the original AJ config and the Nemotron llama-server at the end.
set -u
LOG=/home/eamon/maya-aj-v1115-dflash-cycle.log
DONE=/home/eamon/maya-aj-v1115-dflash-cycle.done
STOPF=/home/eamon/maya-aj-v1115-dflash-cycle-STOP
BASE=/home/eamon/maya-aj-v1115-dflash
PM=/home/eamon/project-maya
ELOG="$PM/maya-aj-iq2_xxs.log"
CFG="$PM/maya-aj-iq2_xxs.json"
MD="/mnt/models/GLM-5.3-Flash-AJ-IQ2_XXS-GGUF"
RUN_AJ=./run-maya-aj-iq2_xxs.sh
BENCHGGUF="$MD/GLM-5.3-Flash-AJ-IQ2_XXS-00001-of-00002.gguf"
BENCHPACK="$MD/pack/tokenizer"
DRAFTER=/mnt/models/Maya-data/models/GLM-5.3-Flash-DFlash2/GLM-5.3-Flash-DFlash2-Q4_K_M.gguf
EXPECT_STAMP=707211430e5c3035
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

start_arm() {  # $1 rep
  local rep="$1" arm="dflash$rep" i ok=0 before t0 t1 st got ep
  cd "$PM" || fail "cd $PM"
  ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port 8080 busy before start ($arm)"
  cp -f "$BASE/cfg-dflash.json" "$CFG" || fail "restore dflash cfg"
  [ -f "$ELOG" ] || touch "$ELOG"
  before=$(wc -l < "$ELOG")
  t0=$(date +%s)
  echo "--- launching $RUN_AJ ($arm, v1.1.15 + --dflash) at $(date -u)"
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
  [ "$st" = "$EXPECT_STAMP" ] || fail "engine stamp $st != $EXPECT_STAMP ($arm)"
  local dm
  dm=$(tail -n +"$before" "$ELOG" | grep -c 'glm dflash:' || true)
  echo "glm dflash markers since arm start: $dm"
  [ "$dm" -ge 1 ] || fail "no glm dflash marker - drafter not loaded ($arm)"
  tail -n +"$before" "$ELOG" | grep -m4 'glm dflash:' || true
  tail -n +"$before" "$ELOG" | grep -m2 'glm split:' || true
  ep=$(pgrep -f 'project-maya/build/[s]trata --glm-pack' | head -1 || true)
  [ -n "$ep" ] && { echo "engine pid $ep"; tr '\0' '\n' < "/proc/$ep/environ" | grep STRATA || true; }
  md5sum -c "$BASE/cfg-dflash.md5" || fail "config drifted during start ($arm)"
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
  grep -E 'glm stat:|draft' "$ELOG" | tail -20 > "$BASE/stats-$arm.txt" || true
  tail -3 "$BASE/stats-$arm.txt" || true
}

# ---------- 0. preflight ----------
say "--- [0] preflight"
stop_maya
stop_llama
[ -f "$DRAFTER" ] || fail "drafter missing: $DRAFTER"
[ -f "$CFG" ] || fail "AJ config missing"
grep -q '262144' "$CFG" || fail "AJ config is not 262144"
cd "$PM" && git checkout -q v1.1.15 || fail "checkout v1.1.15"
[ "$(cat VERSION)" = "1.1.15" ] || fail "not v1.1.15"
say "--- write the --dflash config (calibration record kept, so it does not re-measure at start)"
cp "$CFG" "$BASE/cfg-plain.json" || fail "snapshot plain config"
grep -q -- '--dflash' "$CFG" && fail "config already has --dflash"
python3 - "$CFG" "$DRAFTER" <<'PY' || fail "add --dflash"
import json, sys
p, drafter = sys.argv[1], sys.argv[2]
c = json.load(open(p))
a = c["args"]
assert "--dflash" not in a, "already present"
assert a[a.index("--max-context") + 1] == "262144"
assert (c.get("installer") or {}).get("speed_calibration"), "calibration record missing - a start would re-measure"
a += ["--dflash", drafter]
json.dump(c, open(p, "w"), indent=1)
print("args:", a)
PY
cp "$CFG" "$BASE/cfg-dflash.json"
md5sum "$CFG" > "$BASE/cfg-dflash.md5"
cat "$BASE/cfg-dflash.md5"
say "preflight OK"

# ---------- 1-3. three dflash arms ----------
for rep in 1 2 3; do
  if [ -f "$STOPF" ]; then say "STOP file present - skipping remaining arms"; break; fi
  say "--- arm dflash$rep"
  start_arm "$rep"
  warmup
  bench "aj-iq2xxs-256k-v1115-dflash-r$rep" "dflash$rep"
  stop_maya
  echo "OK" > "$BASE/stage-dflash$rep.done"
done

# ---------- 4. restore config + Nemotron ----------
say "--- [restore] original AJ config"
cp -f "$BASE/cfg-plain.json" "$CFG" || fail "restore plain config"
grep -q -- '--dflash' "$CFG" && fail "config still has --dflash"
md5sum "$CFG"
say "--- [restore] Nemotron llama-server"
if [ -f /home/eamon/nemotron-restore-argv-2026-10-17.txt ]; then
  NEM=$(cat /home/eamon/nemotron-restore-argv-2026-10-17.txt)
  setsid -f bash -c "cd /home/eamon && exec $NEM > /home/eamon/nemotron-server-restored-2026-10-17b.log 2>&1 < /dev/null"
  ok=0
  for i in $(seq 1 180); do
    if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models 2>/dev/null | grep -q 'owned_by'; then ok=1; break; fi
    sleep 5
  done
  if [ "$ok" = 1 ]; then echo "nemotron API up"; else echo "!!! nemotron restore not answering yet"; fi
else
  echo "no saved argv - leaving the box stopped"
fi
say "--- finish"
echo "=== AJ dflash cycle done $(date -u) ==="
echo 0 > "$DONE"
