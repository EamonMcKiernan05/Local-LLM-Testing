#!/bin/bash
# Maya shallow-range batteries (2026-10-15): v1.1.1 vs v1.1.11 at 0.5K/1K/5K/10K, 3 reps per side, alternated.
set -u
LOG=/home/eamon/maya-shallow-cycle.log
DONE=/home/eamon/maya-shallow-cycle.done
BK=/home/eamon/maya-v1111-cycle-bk
PM=/home/eamon/project-maya
ELOG="$PM/maya-maya-s-v2-iq2_xxs.log"
MD="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs"
BENCHGGUF="$MD/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf"
BENCHPACK="$MD/pack/tokenizer"
SRC_V111=d640b61395691e36
DEPTHS="500,1k,5k,10k"
exec > "$LOG" 2>&1
rm -f "$DONE"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
echo "=== maya shallow cycle started $(date -u) UTC ==="

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

apply_cfg() {
  if [ "$1" = "v111" ]; then
    cp "$BK/config-v111-orig.json" "$PM/maya-maya-s-v2-iq2_xxs.json" || fail "apply cfg v111"
    md5sum -c "$BK/config-md5-v111.txt" || fail "md5 gate after applying v111 cfg"
  else
    cp "$BK/config-v1111-migrated.json" "$PM/maya-maya-s-v2-iq2_xxs.json" || fail "apply cfg v1111"
    md5sum -c "$BK/config-md5-v1111.txt" || fail "md5 gate after applying v1111 cfg"
  fi
}

start_arm() {
  local tag="$1" exp="$2" sfx="$3" md5f="$4" i ok=0 before t0 t1 st hits ep
  cd "$PM" || fail "cd $PM"
  before=$(wc -l < "$ELOG" 2>/dev/null || echo 0)
  t0=$(date +%s)
  echo "--- launching ./setup.sh ($tag / $sfx) at $(date -u)"
  setsid -f bash -c "cd $PM && exec ./setup.sh > /home/eamon/maya-shallow-start-$sfx.log 2>&1 < /dev/null"
  for i in $(seq 1 720); do
    if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then ok=1; break; fi
    sleep 5
  done
  [ "$ok" = 1 ] || fail "maya not ready ($tag/$sfx)"
  t1=$(date +%s)
  echo "api up after ~$((t1-t0))s ($tag/$sfx)"
  grep -q "port 8080 is already in use" "/home/eamon/maya-shallow-start-$sfx.log" && fail "port-in-use marker ($tag/$sfx)"
  [ "$((t1-t0))" -ge 60 ] || fail "suspiciously fast ready ($tag/$sfx)"
  st=$(stamp); echo "stamp: $st"
  [ "$st" = "$exp" ] || fail "stamp mismatch ($tag/$sfx): $st != $exp"
  hits=$(tail -n +"$before" "$ELOG" | grep -cE 'glm mtp|NextN' || true)
  echo "engine reload marker hits: $hits"
  tail -n +"$before" "$ELOG" | grep -m1 'glm split:' || true
  md5sum -c "$md5f" || fail "config drifted during start ($tag/$sfx)"
  echo "start gates done ($tag/$sfx)"
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
    print("warmup ok: prompt_tokens", d.get("usage", {}).get("prompt_tokens"))
except Exception as e:
    print("warmup failed:", e)
PY
}

bench() {
  local label="$1" sfx="$2" rc RD
  cd /home/eamon/model-bench || fail "cd model-bench"
  export MODEL_BENCH_GGUF="$BENCHGGUF"
  export MODEL_BENCH_PACK="$BENCHPACK"
  /home/eamon/Strata/.venv/bin/python bench.py --url http://127.0.0.1:8080 --label "$label" --depths "$DEPTHS"
  rc=$?
  echo "bench $label rc=$rc $(date -u)"
  [ "$rc" = 0 ] || fail "bench $label rc=$rc"
  RD=$(ls -1dt /home/eamon/model-bench/runs/*"$label" | head -1)
  echo "run dir: $RD"
  echo "$(date -u) $sfx rundir=$RD" >> "$BK/timeline-shallow.txt"
  cp -a "$RD" "$BK"/ || true
}

checkout_tag() {
  cd "$PM" || fail "cd $PM"
  git checkout "$1" || fail "checkout $1"
  [ "$(cat VERSION)" = "${1#v}" ] || fail "VERSION mismatch after checkout $1"
  echo "checked out $1 at $(date -u)"
}

# ---------- preflight ----------
say "--- [0] preflight"
[ -L "$MD" ] || fail "maya model path not flipped"
[ -f "$BK/config-v111-orig.json" ] || fail "v111 config snapshot missing"
[ -f "$BK/config-v1111-migrated.json" ] || fail "v1111 config snapshot missing"
B11=$(cat "$BK/stamp-v1111.txt" 2>/dev/null); [ -n "$B11" ] || fail "no recorded v1111 stamp"
[ "$B11" != "$SRC_V111" ] || fail "stamps collided"
pgrep -f '[s]erve/server.py' >/dev/null 2>&1 && fail "a server is running already"
ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port 8080 busy"
say "preflight OK (v111=$SRC_V111 v1111=$B11)"

say "--- [A1] v1.1.1 shallow r1"
checkout_tag v1.1.1
apply_cfg v111
start_arm v1.1.1 "$SRC_V111" "v111-sh-r1" "$BK/config-md5-v111.txt"
warmup; bench "maya-s-v2-64k-v111-shallow-r1" "v111-sh-r1"; stop_maya

say "--- [B1] v1.1.11 shallow r1"
checkout_tag v1.1.11
apply_cfg v1111
start_arm v1.1.11 "$B11" "v1111-sh-r1" "$BK/config-md5-v1111.txt"
warmup; bench "maya-s-v2-64k-v1111-shallow-r1" "v1111-sh-r1"; stop_maya

say "--- [A2] v1.1.1 shallow r2"
checkout_tag v1.1.1
apply_cfg v111
start_arm v1.1.1 "$SRC_V111" "v111-sh-r2" "$BK/config-md5-v111.txt"
warmup; bench "maya-s-v2-64k-v111-shallow-r2" "v111-sh-r2"; stop_maya

say "--- [B2] v1.1.11 shallow r2"
checkout_tag v1.1.11
apply_cfg v1111
start_arm v1.1.11 "$B11" "v1111-sh-r2" "$BK/config-md5-v1111.txt"
warmup; bench "maya-s-v2-64k-v1111-shallow-r2" "v1111-sh-r2"; stop_maya

say "--- [A3] v1.1.1 shallow r3"
checkout_tag v1.1.1
apply_cfg v111
start_arm v1.1.1 "$SRC_V111" "v111-sh-r3" "$BK/config-md5-v111.txt"
warmup; bench "maya-s-v2-64k-v111-shallow-r3" "v111-sh-r3"; stop_maya

say "--- [B3] v1.1.11 shallow r3"
checkout_tag v1.1.11
apply_cfg v1111
start_arm v1.1.11 "$B11" "v1111-sh-r3" "$BK/config-md5-v1111.txt"
warmup; bench "maya-s-v2-64k-v1111-shallow-r3" "v1111-sh-r3"; stop_maya

say "--- finish"
cd "$PM" || fail "cd pm"
git describe --tags 2>/dev/null || true
stamp
echo "=== maya shallow cycle done $(date -u) ==="
echo 0 > "$DONE"
