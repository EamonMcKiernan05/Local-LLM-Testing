#!/bin/bash
# Resume the v1111 pair after the B1 config-migration stop (2026-10-15).
# State assumed: box down; iq3_s on HDD (plain, no .hdd-original); maya on HDD (plain); no servers; NVMe clear.
# Remaining arms: B1r(v1111-r1) A2(v111-r2) B2(v1111-r2) A3(v111-r3) B3(v1111-r3) — alternation preserved.
# Config handling: v111 arms run the ORIGINAL config bytes; v1111 arms run the MIGRATED config
# (+--expert-profile) that v1.1.11's first start writes; each arm is md5-gated before and after start.
set -u
LOG=/home/eamon/maya-v1111-resume.log
DONE=/home/eamon/maya-v1111-resume.done
BK=/home/eamon/maya-v1111-cycle-bk
PM=/home/eamon/project-maya
ELOG="$PM/maya-maya-s-v2-iq2_xxs.log"
MD="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs"
MAYANV=/home/eamon/maya-nvme
NV=/home/eamon/strata-nvme
CFG="$PM/maya-maya-s-v2-iq2_xxs.json"
BENCHGGUF="$MD/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf"
BENCHPACK="$MD/pack/tokenizer"
SRC_V111=d640b61395691e36
exec > "$LOG" 2>&1
rm -f "$DONE"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
echo "=== maya v1111 resume started $(date -u) UTC ==="

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

apply_cfg() {  # $1 v111|v1111
  if [ "$1" = "v111" ]; then
    cp "$BK/config-v111-orig.json" "$CFG" || fail "apply cfg v111"
    md5sum -c "$BK/config-md5-v111.txt" || fail "md5 gate after applying v111 cfg"
  else
    cp "$BK/config-v1111-migrated.json" "$CFG" || fail "apply cfg v1111"
    md5sum -c "$BK/config-md5-v1111.txt" || fail "md5 gate after applying v1111 cfg"
  fi
}

start_arm() {  # $1 tag; $2 expected src; $3 suffix; $4 cfg md5 file
  local tag="$1" exp="$2" sfx="$3" md5f="$4" i ok=0 before t0 t1 st hits ep
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
  grep -q "port 8080 is already in use" "/home/eamon/maya-v1111-start-$sfx.log" && fail "port-in-use marker ($tag/$sfx)"
  [ "$((t1-t0))" -ge 60 ] || fail "suspiciously fast ready ($((t1-t0))s) - stale server? ($tag/$sfx)"
  st=$(stamp); echo "stamp: $st"
  [ "$st" = "$exp" ] || fail "stamp mismatch ($tag/$sfx): $st != $exp"
  hits=$(tail -n +"$before" "$ELOG" | grep -cE 'glm mtp|NextN' || true)
  echo "engine reload marker hits: $hits"
  tail -n +"$before" "$ELOG" | grep -m1 'glm split:' || true
  tail -n +"$before" "$ELOG" | grep -m2 'CPU lane' || true
  ep=$(pgrep -f 'project-maya/build/[s]trata --glm-pack' | head -1 || true)
  if [ -n "$ep" ]; then echo "engine pid $ep env:"; tr '\0' '\n' < "/proc/$ep/environ" | grep STRATA || true; fi
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
  [ "$(cat VERSION)" = "${1#v}" ] || fail "VERSION mismatch after checkout $1"
  echo "checked out $1 at $(date -u)"
}

# ---------- 0. state check ----------
say "--- [0] state check"
pgrep -f '[s]erve/server.py' >/dev/null 2>&1 && fail "a server is running"
ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port busy"
[ -d "$MD" ] && [ ! -L "$MD" ] || fail "maya dir not plain"
[ ! -e "$MD.hdd-original" ] || fail "maya .hdd-original exists"
[ ! -e "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs" ] || fail "maya nvme copy exists"
[ -d /mnt/models/Strata-data/packs/iq3_s ] && [ ! -L /mnt/models/Strata-data/packs/iq3_s ] || fail "iq3_s pack not plain HDD"
rmdir "$NV/packs" 2>/dev/null || true
EXTRA=$(ls "$NV" 2>/dev/null || true); [ -z "$EXTRA" ] || fail "NV not empty: $EXTRA"
say "state OK"

# ---------- 1. snapshot configs ----------
say "--- [1] snapshot configs"
[ -f "$BK/config-before-pair.json" ] || fail "original config snapshot missing"
cp -a "$BK/config-before-pair.json" "$BK/config-v111-orig.json"
cp "$CFG" "$BK/config-v1111-migrated.json" || fail "save migrated config"
grep -q -- '--expert-profile' "$BK/config-v1111-migrated.json" || fail "migrated config has no --expert-profile"
grep -q -- '--expert-profile' "$BK/config-v111-orig.json" && fail "orig snapshot has --expert-profile?!"
V111MD5=$(md5sum < "$BK/config-v111-orig.json" | cut -d' ' -f1)
V1111MD5=$(md5sum < "$BK/config-v1111-migrated.json" | cut -d' ' -f1)
echo "$V111MD5  $CFG" > "$BK/config-md5-v111.txt"
echo "$V1111MD5  $CFG" > "$BK/config-md5-v1111.txt"
cat "$BK/config-md5-v111.txt" "$BK/config-md5-v1111.txt"
[ -f "$PM/data/expert-profile-glm.bin" ] || fail "profile bin missing"
B11=$(cat "$BK/stamp-v1111.txt" 2>/dev/null); [ -n "$B11" ] || fail "no recorded v1111 stamp"
[ "$B11" != "$SRC_V111" ] || fail "v1111 stamp == v111 stamp?!"
echo "v1111 stamp: $B11"
[ -f "/home/eamon/maya-v1111-start-v1111-r1.log" ] && mv "/home/eamon/maya-v1111-start-v1111-r1.log" "/home/eamon/maya-v1111-start-v1111-r1.log.firsttry"
ls -d /home/eamon/model-bench/runs/*maya-s-v2-64k-v111-r1 /home/eamon/model-bench/runs/*maya-s-v2-64k-v111-postcopy-burn 2>/dev/null || true

# ---------- 2. checkout v1.1.1 ----------
say "--- [2] checkout v1.1.1"
checkout_tag v1.1.1
apply_cfg v111

# ---------- 3. copy maya to nvme ----------
say "--- [3] copy maya hdd->nvme $(date -u)"
mkdir -p "$MAYANV" || fail "mkdir mayanv"
NEED=$(du -sb "$MD" | cut -f1); echo "need: $NEED"
FREE=$(df --output=avail -B1 / | tail -1); echo "free: $FREE"
[ "$FREE" -gt $((NEED + 5000000000)) ] || fail "low space $FREE"
sync
cp -a "$MD" "$MAYANV/" || fail "cp maya"
sync
say "copy done $(date -u)"; df -h / | tail -1
a=$(du -sb "$MD" | cut -f1); b=$(du -sb "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs" | cut -f1)
echo "du hdd=$a nvme=$b"; [ "$a" = "$b" ] || fail "du mismatch"
for f in GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00002-of-00003.gguf GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00003-of-00003.gguf; do
  x=$(stat -c%s "$MD/$f"); y=$(stat -c%s "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs/$f")
  [ "$x" = "$y" ] || fail "size mismatch $f"
  echo "$f ok"
done
cmp -s "$MD/vision/GLM-5.3-Flash-vocab.gguf" "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs/vision/GLM-5.3-Flash-vocab.gguf" || fail "vocab cmp"
echo "verify ok"

# ---------- 4. flip ----------
say "--- [4] flip"
cd /mnt/models/Maya-data/models || fail "cd mbay"
mv glm-5.3-flash-maya-s-v2-iq2_xxs glm-5.3-flash-maya-s-v2-iq2_xxs.hdd-original || fail "mv hdd dir"
ln -s "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs" glm-5.3-flash-maya-s-v2-iq2_xxs || fail "ln symlink"
head -3 glm-5.3-flash-maya-s-v2-iq2_xxs/pack/index.txt >/dev/null || fail "index not readable through symlink"
say "flip done"

# ---------- arms ----------
say "--- [B1r] v1.1.11 rep1 (redo)"
checkout_tag v1.1.11
apply_cfg v1111
start_arm v1.1.11 "$B11" "v1111-r1" "$BK/config-md5-v1111.txt"
warmup; bench "maya-s-v2-64k-v1111-r1" "v1111-r1"; stop_maya

say "--- [A2] v1.1.1 rep2"
checkout_tag v1.1.1
apply_cfg v111
start_arm v1.1.1 "$SRC_V111" "v111-r2" "$BK/config-md5-v111.txt"
warmup; bench "maya-s-v2-64k-v111-r2" "v111-r2"; stop_maya

say "--- [B2] v1.1.11 rep2"
checkout_tag v1.1.11
apply_cfg v1111
start_arm v1.1.11 "$B11" "v1111-r2" "$BK/config-md5-v1111.txt"
warmup; bench "maya-s-v2-64k-v1111-r2" "v1111-r2"; stop_maya

say "--- [A3] v1.1.1 rep3"
checkout_tag v1.1.1
apply_cfg v111
start_arm v1.1.1 "$SRC_V111" "v111-r3" "$BK/config-md5-v111.txt"
warmup; bench "maya-s-v2-64k-v111-r3" "v111-r3"; stop_maya

say "--- [B3] v1.1.11 rep3"
checkout_tag v1.1.11
apply_cfg v1111
start_arm v1.1.11 "$B11" "v1111-r3" "$BK/config-md5-v1111.txt"
warmup; bench "maya-s-v2-64k-v1111-r3" "v1111-r3"; stop_maya

say "--- finish"
cd "$PM" || fail "cd pm"
git describe --tags 2>/dev/null || true
stamp
echo "=== maya v1111 resume done $(date -u) ==="
echo 0 > "$DONE"
