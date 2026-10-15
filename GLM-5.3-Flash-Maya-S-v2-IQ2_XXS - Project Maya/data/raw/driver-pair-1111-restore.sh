#!/bin/bash
# Maya on .5: restore after the v1111 pair — Maya out (HDD), Strata iq3_s back on NVMe + serving.
set -u
LOG=/home/eamon/maya-v1111-restore.log
DONE=/home/eamon/maya-v1111-restore.done
MD="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs"
MAYANV=/home/eamon/maya-nvme
NV=/home/eamon/strata-nvme
PACKS=/mnt/models/Strata-data/packs
ISTA="/mnt/models/Qwen3.8-Flash-Next/ISTA DASLab"
IQ3DIR="$ISTA/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S"
B1=Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf
B1SIZE=54817524224
PACKSIZE=50292326400
STRATA=/home/eamon/Strata
exec > "$LOG" 2>&1
rm -f "$DONE"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
echo "=== maya v1111 restore started $(date -u) UTC ==="

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

say "--- [0] stop maya"
stop_maya

# ---------- 1. fast paths ----------
say "--- [1] state check"
if [ -L "$PACKS/iq3_s" ] && [ ! -L "$MD" ]; then
  if curl -s -m 5 http://127.0.0.1:8080/v1/models | grep -q 'qwen3.8-flash-next-iq3_s'; then
    say "box already in as-found state (iq3_s flipped + serving)"; echo 0 > "$DONE"; exit 0
  fi
  say "iq3_s is still flipped but not serving -> just start it"
  cd "$STRATA" || fail "cd strata"
  STRATA_EXPERIMENTAL_SM60=1 setsid -f bash -c "cd $STRATA && exec ./run-iq3_s.sh > /home/eamon/strata-iq3_s-run.log 2>&1 < /dev/null"
  for i in $(seq 1 180); do
    curl -s --max-time 5 http://127.0.0.1:8080/v1/models 2>/dev/null | grep -q 'qwen3.8-flash-next-iq3_s' && { say "iq3_s up after ~$((i*5))s"; echo 0 > "$DONE"; exit 0; }
    sleep 5
  done
  fail "iq3_s did not come up"
fi

# ---------- 2. maya teardown ----------
say "--- [2] maya teardown"
if [ -L "$MD" ]; then rm "$MD" || fail "rm maya symlink"; fi
if [ -e "$MD.hdd-original" ]; then
  [ -e "$MD" ] && { echo "WARN: plain dir at MD while .hdd-original exists - removing plain dir"; rm -rf "$MD" || fail "rm stray MD"; }
  mv "$MD.hdd-original" "$MD" || fail "restore maya dir"
fi
[ -d "$MD" ] && [ ! -L "$MD" ] || fail "maya dir not a restored plain dir"
[ -f "$MD/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf" ] || fail "maya shard1 missing after restore"
rm -rf "$MAYANV"/glm-5.3-flash-maya-s-v2-iq2_xxs || fail "rm maya nvme copy"
stat -L -c%s "$MD/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf" >/dev/null || fail "maya shard1 not readable"
df -h / | tail -1

# ---------- 3. iq3_s masters present ----------
say "--- [3] iq3_s HDD masters"
[ -d "$PACKS/iq3_s" ] && [ ! -L "$PACKS/iq3_s" ] || fail "iq3_s pack not a plain HDD dir"
[ -f "$PACKS/iq3_s/experts.bin" ] || fail "iq3_s experts.bin missing"
[ -f "$IQ3DIR/$B1" ] && [ ! -L "$IQ3DIR/$B1" ] || fail "iq3_s shard1 not a plain HDD file"
[ ! -e "$NV/packs/iq3_s" ] && [ ! -e "$NV/iq3_s" ] || fail "nvme target dirs already exist"
FREE=$(df --output=avail -B1 / | tail -1); echo "free: $FREE"
[ "$FREE" -gt 112000000000 ] || fail "low space $FREE"

# ---------- 4. copy iq3_s to nvme ----------
say "--- [4] copy iq3_s hdd->nvme $(date -u)"
mkdir -p "$NV/iq3_s" "$NV/packs"
cp -a "$PACKS/iq3_s" "$NV/packs/iq3_s" || fail "pack copy"
echo "pack copied $(date -u)"
cp -a "$IQ3DIR/$B1" "$NV/iq3_s/$B1" || fail "shard1 copy"
echo "shard1 copied $(date -u)"; sync; df -h / | tail -1

# ---------- 5. verify + flip ----------
say "--- [5] verify + flip"
a=$(du -sb "$PACKS/iq3_s" | cut -f1); b=$(du -sb "$NV/packs/iq3_s" | cut -f1); echo "pack du $a/$b"; [ "$a" = "$b" ] || fail "pack du mismatch"
[ "$(stat -c%s "$NV/packs/iq3_s/experts.bin")" = "$PACKSIZE" ] || fail "experts.bin size"
[ "$(stat -c%s "$NV/iq3_s/$B1")" = "$B1SIZE" ] || fail "shard1 size"
cmp -n 1048576 "$IQ3DIR/$B1" "$NV/iq3_s/$B1" || fail "shard1 head cmp"
mv "$PACKS/iq3_s" "$PACKS/iq3_s.hdd-original" && ln -s "$NV/packs/iq3_s" "$PACKS/iq3_s" || fail "pack flip"
mv "$IQ3DIR/$B1" "$IQ3DIR/$B1.hdd-original" && ln -s "$NV/iq3_s/$B1" "$IQ3DIR/$B1" || fail "shard1 flip"
stat -L -c%s "$PACKS/iq3_s/experts.bin" >/dev/null || fail "pack not readable through symlink"
stat -L -c%s "$IQ3DIR/$B1" >/dev/null || fail "shard1 not readable through symlink"
B2=Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf
stat -L -c%s "$IQ3DIR/$B2" >/dev/null || fail "shard2 not readable through symlink"
ls -la "$IQ3DIR" | head -10

# ---------- 6. config sanity ----------
say "--- [6] strata config sanity"
cd "$STRATA" || fail "cd strata"
cp strata-iq3_s.json strata-iq3_s.json.bak-maya1111-20261015 || fail "config snapshot"
/home/eamon/Strata/.venv/bin/python - <<'PY' || fail "config check"
import json, os
p = "/home/eamon/Strata/strata-iq3_s.json"
d = json.load(open(p))
a = d["args"]
assert "--vision" in a, "--vision missing"
assert "--vram-reserve-mib" in a, "vram reserve missing"
for k in ("--pack", "--native", "--ple-gguf"):
    assert os.path.exists(a[a.index(k) + 1]), f"missing {k}: {a[a.index(k) + 1]}"
v = d.get("vision", {})
for k in ("exe", "mmproj", "model"):
    assert os.path.exists(v[k]), f"missing {k}: {v[k]}"
print("config OK; mmproj:", v["mmproj"])
PY

# ---------- 7. start strata ----------
say "--- [7] start iq3_s"
STRATA_EXPERIMENTAL_SM60=1 setsid -f bash -c "cd $STRATA && exec ./run-iq3_s.sh > /home/eamon/strata-iq3_s-run.log 2>&1 < /dev/null"
ok=0
for i in $(seq 1 180); do
  out=$(curl -s --max-time 5 http://127.0.0.1:8080/v1/models 2>/dev/null || true)
  if printf '%s' "$out" | grep -q 'qwen3.8-flash-next-iq3_s'; then ok=1; echo "model up after ~$((i*5))s"; break; fi
  sleep 5
done
[ "$ok" = 1 ] || { tail -40 /home/eamon/strata-iq3_s-run.log; fail "iq3_s not ready"; }
for i in $(seq 1 60); do
  out=$(curl -s --max-time 5 http://127.0.0.1:8080/v1/models 2>/dev/null || true)
  printf '%s' "$out" | grep -q '"image"' && { echo "vision modality advertised"; break; }
  sleep 5
done
curl -s --max-time 5 http://127.0.0.1:8080/v1/models | head -c 400; echo
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader
say "=== maya v1111 restore done $(date -u) ==="
echo 0 > "$DONE"
