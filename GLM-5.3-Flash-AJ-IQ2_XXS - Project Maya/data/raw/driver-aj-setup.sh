#!/bin/bash
# maya-aj-setup-2026-10-16.sh - stop Maya, run the Maya setup for aj9o9's AJ-IQ2_XXS as a local --gguf-dir model
# at 262144 context, build its pack, write maya-aj-iq2_xxs.json + run script, snapshot the config for the md5 gates.
# No start (--no-start); no tuning (--yes + --no-start skip the offer); vision files are pre-placed by the prep script.
set -u
LOG=/home/eamon/maya-aj-setup.log
DONE=/home/eamon/maya-aj-setup.done
PM=/home/eamon/project-maya
BASE=/home/eamon/maya-aj-iq2xxs
CFG="$PM/maya-aj-iq2_xxs.json"
exec > "$LOG" 2>&1
rm -f "$DONE"
fail(){ echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say(){ echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
mkdir -p "$BASE"
echo "=== AJ setup started $(date -u) UTC ==="

say "--- stop Maya"
p=$(pgrep -f 'project-maya/[s]erve/server.py' | head -1 || true)
if [ -n "$p" ]; then
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
else
  echo "no maya server running"
fi
ss -ltn 2>/dev/null | grep -q ':8080 ' && fail "port 8080 still listening"

say "--- setup (pack build; no start)"
cd "$PM" || fail "cd $PM"
./maya.sh --setup --yes --no-start \
  --gguf-dir /mnt/models/GLM-5.3-Flash-AJ-IQ2_XXS-GGUF \
  --gpus 0,1 --context 262144 --host 0.0.0.0 \
  --env STRATA_GLM_TIMING=1 --env STRATA_GLM_POOL_STATS=1 --env STRATA_GLM_RAM_HEADROOM_GB=3
rc=$?; echo "setup rc=$rc"
[ "$rc" = 0 ] || fail "setup rc=$rc"

say "--- verify config"
[ -f "$CFG" ] || fail "config not written"
python3 - "$CFG" <<'PY' || fail "config check"
import json, sys
c = json.load(open(sys.argv[1]))
a = c["args"]
assert a[a.index("--max-context") + 1] == "262144", "max-context not 262144"
assert c.get("gpu") == [0, 1], f"gpu {c.get('gpu')}"
assert c.get("host") == "0.0.0.0", f"host {c.get('host')}"
p = a[a.index("--glm-pack") + 1]
assert p.endswith("/maya-nvme/glm-5.3-flash-aj-iq2_xxs/pack"), p
assert c.get("vision"), "vision block missing"
print("config OK:", json.dumps(c, indent=1))
PY
cat "$CFG"
cp -a "$CFG" "$BASE/config-aj-snapshot.json"
md5sum "$CFG" > "$BASE/config-md5-aj.txt"
say "--- setup OK; config: $CFG; run script: $PM/run-$(basename "$CFG" .json).sh"
echo "=== AJ setup done $(date -u) ==="
echo 0 > "$DONE"
