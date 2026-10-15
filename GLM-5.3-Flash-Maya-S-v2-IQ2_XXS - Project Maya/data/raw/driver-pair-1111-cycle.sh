#!/bin/bash
# Maya on .5: v1.1.1 <-> v1.1.11 repeated same-day pair, 2026-10-15.
# One discarded post-copy burn battery, then 3 measured batteries per side, alternated:
#   [B burn v111] [A1 v111 r1] [B1 v1111 r1] [A2 v111 r2] [B2 v1111 r2] [A3 v111 r3] [B3 v1111 r3]
# Each arm: stop -> checkout tag -> plain ./setup.sh (rebuild-if-changed + start) -> gates -> warmup -> bench -> stop.
set -u
LOG=/home/eamon/maya-v1111-cycle.log
DONE=/home/eamon/maya-v1111-cycle.done
BK=/home/eamon/maya-v1111-cycle-bk
PM=/home/eamon/project-maya
ELOG="$PM/maya-maya-s-v2-iq2_xxs.log"
MD="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs"
BENCHGGUF="$MD/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf"
BENCHPACK="$MD/pack/tokenizer"
SRC_V111=d640b61395691e36
exec > "$LOG" 2>&1
rm -f "$DONE"
mkdir -p "$BK"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
echo "=== maya v1111 cycle started $(date -u) UTC ==="

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

start_arm() {  # $1 tag; $2 expected src or "new"; $3 short suffix
  local tag="$1" exp="$2" sfx="$3" i ok=0 before t0 t1 st hits ep
  cd "$PM" || fail "cd $PM"
  before=$(wc -l < "$ELOG" 2>/dev/null || echo 0)
  t0=$(date +%s)
  echo "--- launching ./setup.sh ($tag / $sfx) at $(date -u)"
  setsid -f bash -c "cd $PM && exec ./setup.sh > /home/eamon/maya-v1111-start-$sfx.log 2>&1 < /dev/null"
  for i in $(seq 1 720); do
    if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then ok=1; break; fi
    sleep 5
  done
  [ "$ok" = 1 ] || fail "maya not ready ($tag/$sfx)"
  t1=$(date +%s)
  echo "api up after ~$((t1-t0))s ($tag/$sfx)"
  grep -q "port 8080 is already in use" "/home/eamon/maya-v1111-start-$sfx.log" && fail "port-in-use marker in start log ($tag/$sfx)"
  [ "$((t1-t0))" -ge 60 ] || fail "suspiciously fast ready ($((t1-t0))s) - stale server? ($tag/$sfx)"
  st=$(stamp); echo "stamp: $st"
  if [ "$exp" = "new" ]; then
    [ "$st" != "$SRC_V111" ] || fail "v1111 stamp identical to v111 - soft compile failure?"
    echo "$st" > "$BK/stamp-v1111.txt"
  else
    [ "$st" = "$exp" ] || fail "stamp mismatch ($tag/$sfx): $st != $exp"
  fi
  hits=$(tail -n +"$before" "$ELOG" | grep -cE 'glm mtp|NextN' || true)
  echo "engine reload marker hits: $hits"
  tail -n +"$before" "$ELOG" | grep -m1 'glm split:' || true
  tail -n +"$before" "$ELOG" | grep -m2 'CPU lane' || true
  ep=$(pgrep -f 'project-maya/build/[s]trata --glm-pack' | head -1 || true)
  if [ -n "$ep" ]; then echo "engine pid $ep env:"; tr '\0' '\n' < "/proc/$ep/environ" | grep STRATA || true; fi
  md5sum -c "$BK/config-md5.txt" || fail "config drifted ($tag/$sfx)"
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
    print("warmup ok: prompt_tokens", d.get("usage", {}).get("prompt_tokens"), "| timings:", d.get("timings"))
except Exception as e:
    print("warmup failed:", e)
PY
}

bench() {  # $1 label; $2 sfx
  local label="$1" sfx="$2" rc RD
  cd /home/eamon/model-bench || fail "cd model-bench"
  export MODEL_BENCH_GGUF="$BENCHGGUF"
  export MODEL_BENCH_PACK="$BENCHPACK"
  /home/eamon/Strata/.venv/bin/python bench.py --url http://127.0.0.1:8080 --label "$label" --depths 20k,40k,60k
  rc=$?
  echo "bench $label rc=$rc $(date -u)"
  [ "$rc" = 0 ] || fail "bench $label rc=$rc"
  RD=$(ls -1dt /home/eamon/model-bench/runs/*"$label" | head -1)
  echo "run dir: $RD"
  echo "$(date -u) $sfx rundir=$RD" >> "$BK/timeline.txt"
  cp -a "$RD" "$BK"/ || true
  grep -E 'glm stat:' "$ELOG" | tail -5 > "$BK/stats-$sfx.txt" || true
  echo "--- last glm stat lines:"
  cat "$BK/stats-$sfx.txt" || true
}

checkout_tag() {  # $1 tag
  cd "$PM" || fail "cd $PM"
  git checkout "$1" || fail "checkout $1"
  [ "$(cat VERSION)" = "${1#v}" ] || fail "VERSION mismatch after checkout $1: $(cat VERSION)"
  md5sum -c "$BK/config-md5.txt" || fail "config drifted after checkout $1"
  echo "checked out $1 at $(date -u)"
}

# ---------- preflight ----------
say "--- [0] preflight"
EXP=$(cat "$BK/stamp-v111.txt" 2>/dev/null); [ -n "$EXP" ] || fail "no prep stamp"
[ "$EXP" = "$SRC_V111" ] || fail "unexpected stored v111 stamp $EXP"
[ -L "$MD" ] || fail "maya model path not flipped"
head -1 "$MD/pack/index.txt" >/dev/null || fail "maya pack not readable through symlink"
[ ! -L /mnt/models/Strata-data/packs/iq3_s ] || fail "iq3_s still flipped"
[ -f /mnt/models/Strata-data/packs/iq3_s/experts.bin ] || fail "iq3_s pack not on HDD"
pgrep -f '[s]erve/server.py' >/dev/null 2>&1 && fail "a server is running already"
ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port 8080 busy"
cd "$PM" || fail "cd $PM"
git fetch origin --tags --force || fail "fetch"
checkout_tag v1.1.1
say "preflight OK"

# ---------- burn ----------
say "--- [B] post-copy burn (discarded)"
start_arm v1.1.1 "$SRC_V111" "v111-burn"
warmup
bench "maya-s-v2-64k-v111-postcopy-burn" "v111-burn"
stop_maya

# ---------- arms ----------
say "--- [A1] v1.1.1 rep1"
checkout_tag v1.1.1
start_arm v1.1.1 "$SRC_V111" "v111-r1"
warmup; bench "maya-s-v2-64k-v111-r1" "v111-r1"; stop_maya

say "--- [B1] v1.1.11 rep1"
checkout_tag v1.1.11
start_arm v1.1.11 "new" "v1111-r1"
warmup; bench "maya-s-v2-64k-v1111-r1" "v1111-r1"; stop_maya

say "--- [A2] v1.1.1 rep2"
checkout_tag v1.1.1
start_arm v1.1.1 "$SRC_V111" "v111-r2"
warmup; bench "maya-s-v2-64k-v111-r2" "v111-r2"; stop_maya

say "--- [B2] v1.1.11 rep2"
checkout_tag v1.1.11
start_arm v1.1.11 "new" "v1111-r2"
warmup; bench "maya-s-v2-64k-v1111-r2" "v1111-r2"; stop_maya

say "--- [A3] v1.1.1 rep3"
checkout_tag v1.1.1
start_arm v1.1.1 "$SRC_V111" "v111-r3"
warmup; bench "maya-s-v2-64k-v111-r3" "v111-r3"; stop_maya

say "--- [B3] v1.1.11 rep3"
checkout_tag v1.1.11
start_arm v1.1.11 "new" "v1111-r3"
warmup; bench "maya-s-v2-64k-v1111-r3" "v1111-r3"; stop_maya

# ---------- finish ----------
say "--- finish"
cd "$PM" || fail "cd PM"
git describe --tags 2>/dev/null || true
stamp
curl -s --max-time 5 http://127.0.0.1:8080/v1/models | head -c 200 || true; echo
echo "=== maya v1111 cycle done $(date -u) ==="
echo 0 > "$DONE"
