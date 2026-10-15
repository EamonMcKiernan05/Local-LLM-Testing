#!/bin/bash
# maya-sn730-cycle.sh — 2026-10-15 night
# Move Maya's model set onto the new SN730 NVMe (~/maya-nvme is a bind of /mnt/nvme/maya-nvme),
# flip the standard paths, then burn + 3 fresh-load bench batteries at 20k/40k/60k.
# Adapted from maya-v1111-resume-2026-10-15.sh (proven stop/start/bench pattern).
set -u
LOG=/home/eamon/maya-sn730-cycle.log
DONE=/home/eamon/maya-sn730-cycle.done
BASE=/home/eamon/maya-sn730
PM=/home/eamon/project-maya
ELOG="$PM/maya-maya-s-v2-iq2_xxs.log"
CFG="$PM/maya-maya-s-v2-iq2_xxs.json"
MD="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs"
MBAY="/mnt/models/Maya-data/models"
MAYANV=/home/eamon/maya-nvme
NAME=glm-5.3-flash-maya-s-v2-iq2_xxs
EXPECT_STAMP=5a23fa1ec92e67aa
BENCHGGUF="$MD/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf"
BENCHPACK="$MD/pack/tokenizer"
mkdir -p "$BASE"
exec > "$LOG" 2>&1
rm -f "$DONE"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
echo "=== maya SN730 cycle started $(date -u) UTC ==="

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

start_arm() {  # $1 sfx
  local sfx="$1" i ok=0 before t0 t1 st ep
  cd "$PM" || fail "cd $PM"
  ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port 8080 busy before start ($sfx)"
  before=$(wc -l < "$ELOG" 2>/dev/null || echo 0)
  t0=$(date +%s)
  echo "--- launching ./setup.sh ($sfx) at $(date -u)"
  setsid -f bash -c "cd $PM && exec ./setup.sh > /home/eamon/maya-sn730-start-$sfx.log 2>&1 < /dev/null"
  for i in $(seq 1 720); do
    if curl -sf --max-time 5 http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then ok=1; break; fi
    sleep 5
  done
  [ "$ok" = 1 ] || fail "maya not ready ($sfx)"
  t1=$(date +%s)
  echo "api up after ~$((t1-t0))s ($sfx)"
  grep -q "port 8080 is already in use" "/home/eamon/maya-sn730-start-$sfx.log" && fail "port-in-use marker ($sfx)"
  [ "$((t1-t0))" -ge 60 ] || fail "suspiciously fast ready ($((t1-t0))s) - stale server? ($sfx)"
  st=$(stamp); echo "engine src stamp: $st"
  [ "$st" = "$EXPECT_STAMP" ] || fail "unexpected engine stamp ($sfx): $st"
  echo "engine reload marker hits: $(tail -n +"$before" "$ELOG" | grep -cE 'glm mtp|NextN' || true)"
  tail -n +"$before" "$ELOG" | grep -m1 'glm split:' || true
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
  echo "$(date -u) $sfx rundir=$RD" >> "$BASE/timeline.txt"
  cp -a "$RD" "$BASE"/ || true
  grep -E 'glm stat:' "$ELOG" | tail -5 > "$BASE/stats-$sfx.txt" || true
  cat "$BASE/stats-$sfx.txt" || true
}

# ---------- 0. preflight ----------
say "--- [0] preflight"
pgrep -f '[s]erve/server.py' >/dev/null 2>&1 && fail "a server is running"
ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port busy"
[ -d "$MD" ] && [ ! -L "$MD" ] || fail "maya dir not plain HDD"
[ ! -e "$MD.hdd-original" ] || fail "maya .hdd-original already exists"
[ ! -e "$MAYANV/$NAME" ] || fail "maya nvme copy exists already"
mountpoint -q "$MAYANV" || fail "~/maya-nvme is not the NVMe bind"
NEED=$(du -sb "$MD" | cut -f1); echo "need: $NEED bytes"
FREE=$(df --output=avail -B1 /mnt/nvme | tail -1); echo "free on /mnt/nvme: $FREE"
[ "$FREE" -gt $((NEED + 8000000000)) ] || fail "not enough space on new NVMe ($FREE)"
cp -a "$CFG" "$BASE/config-snapshot.json"
V=$(md5sum < "$CFG" | cut -d' ' -f1); echo "$V  $CFG" > "$BASE/config-md5.txt"
cat "$BASE/config-md5.txt"
say "preflight OK"

# ---------- 1. copy hdd -> nvme ----------
say "--- [1] copy maya HDD -> SN730 $(date -u)"
sync
cp -a "$MD" "$MAYANV/" || fail "cp maya"
sync
say "copy done $(date -u)"
a=$(du -sb "$MD" | cut -f1); b=$(du -sb "$MAYANV/$NAME" | cut -f1)
echo "du hdd=$a nvme=$b"; [ "$a" = "$b" ] || fail "du mismatch"
for f in GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00002-of-00003.gguf GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00003-of-00003.gguf; do
  x=$(stat -c%s "$MD/$f"); y=$(stat -c%s "$MAYANV/$NAME/$f")
  [ "$x" = "$y" ] || fail "size mismatch $f"
  echo "$f ok"
done
cmp -s "$MD/vision/GLM-5.3-Flash-vocab.gguf" "$MAYANV/$NAME/vision/GLM-5.3-Flash-vocab.gguf" || fail "vocab cmp"
echo "verify ok"; echo "OK" > "$BASE/stage-copy.done"

# ---------- 2. flip ----------
say "--- [2] flip"
cd "$MBAY" || fail "cd mbay"
mv "$NAME" "$NAME.hdd-original" || fail "mv hdd dir"
ln -s "$MAYANV/$NAME" "$NAME" || fail "ln symlink"
head -3 "$NAME/pack/index.txt" >/dev/null || fail "index not readable through symlink"
[ "$(readlink "$MBAY/$NAME")" = "$MAYANV/$NAME" ] || fail "symlink target unexpected"
say "flip done"; echo "OK" > "$BASE/stage-flip.done"

# ---------- 3. burn battery (discarded by design) ----------
say "--- [3] burn battery (post-copy, discarded)"
start_arm "burn"
warmup; bench "maya-s-v2-64k-sn730-postcopy-burn" "burn"; stop_maya
echo "OK" > "$BASE/stage-burn.done"

# ---------- 4-6. three measured runs ----------
for n in 1 2 3; do
  say "--- [run $n] sn730-r$n"
  start_arm "r$n"
  warmup; bench "maya-s-v2-64k-sn730-r$n" "r$n"; stop_maya
  echo "OK" > "$BASE/stage-r$n.done"
done

# ---------- 7. leave Maya serving ----------
say "--- [7] final start (leave serving)"
start_arm "serving"
curl -s -m 5 http://127.0.0.1:8080/v1/models | head -c 400; echo
say "--- finish"
echo "=== maya SN730 cycle done $(date -u) ==="
echo 0 > "$DONE"
