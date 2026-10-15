#!/bin/bash
# Maya on .5: prep for the v1.1.1 -> v1.1.11 pair (2026-10-15).
# Stops Strata iq3_s, drops its NVMe working set to HDD names, copies Maya HDD->NVMe, flips.
set -u
LOG=/home/eamon/maya-v1111-prep.log
DONE=/home/eamon/maya-v1111-prep.done
BK=/home/eamon/maya-v1111-cycle-bk
MD="/mnt/models/Maya-data/models/glm-5.3-flash-maya-s-v2-iq2_xxs"
MAYANV=/home/eamon/maya-nvme
MBAY="/mnt/models/Maya-data/models"
NV=/home/eamon/strata-nvme
PACKS=/mnt/models/Strata-data/packs
ISTA="/mnt/models/Qwen3.8-Flash-Next/ISTA DASLab"
IQ3DIR="$ISTA/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S"
B1=Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf
B1SIZE=54817524224
PACKSIZE=50292326400
PM=/home/eamon/project-maya
mkdir -p "$BK"
exec > "$LOG" 2>&1
rm -f "$DONE"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

echo "=== maya v1111 prep started $(date -u) UTC ==="

# ---------- 0. preflight ----------
say "--- [0] preflight"
curl -s -m 5 http://127.0.0.1:8080/v1/models | grep -q 'qwen3.8-flash-next-iq3_s' || fail "iq3_s not serving on 8080"
[ -L "$PACKS/iq3_s" ] || fail "packs/iq3_s not a symlink"
[ "$(readlink -f "$PACKS/iq3_s")" = "$NV/packs/iq3_s" ] || fail "packs/iq3_s target unexpected: $(readlink -f "$PACKS/iq3_s")"
[ -f "$PACKS/iq3_s.hdd-original/experts.bin" ] || fail "packs/iq3_s.hdd-original/experts.bin missing"
[ -L "$IQ3DIR/$B1" ] || fail "iq3_s shard1 not a symlink"
[ "$(readlink -f "$IQ3DIR/$B1")" = "$NV/iq3_s/$B1" ] || fail "shard1 target unexpected: $(readlink -f "$IQ3DIR/$B1")"
[ -f "$IQ3DIR/$B1.hdd-original" ] || fail "shard1 .hdd-original missing"
[ "$(stat -c%s "$IQ3DIR/$B1.hdd-original")" = "$B1SIZE" ] || fail "shard1 origin size"
[ "$(stat -L -c%s "$IQ3DIR/$B1")" = "$B1SIZE" ] || fail "shard1 nvme size"
[ "$(stat -L -c%s "$PACKS/iq3_s/experts.bin")" = "$PACKSIZE" ] || fail "pack nvme experts size"
[ "$(stat -c%s "$PACKS/iq3_s.hdd-original/experts.bin")" = "$PACKSIZE" ] || fail "pack orig experts size"
B2=Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf
[ -L "$IQ3DIR/$B2" ] || fail "shard2 not a symlink"
readlink -f "$IQ3DIR/$B2" | grep -q 'strata-ple' || fail "shard2 not pointing into strata-ple"
[ -d "$MD" ] && [ ! -L "$MD" ] || fail "maya dir not a plain dir"
[ ! -e "$MD.hdd-original" ] || fail "maya .hdd-original already exists"
[ ! -e "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs" ] || fail "maya nvme copy already exists"
cd "$PM" || fail "cd PM"
[ "$(cat VERSION)" = "1.1.1" ] || fail "maya VERSION != 1.1.1"
git describe --tags --exact-match 2>/dev/null | grep -qx 'v1.1.1' || fail "HEAD not at v1.1.1"
STAMP=$(grep -o '"src": "[0-9a-f]*"' "$PM/build/MAYA-BUILD.json" | head -1 | cut -d'"' -f4)
echo "$STAMP" > "$BK/stamp-v111.txt"
echo "v111 stamp: $STAMP"
[ "$STAMP" = "d640b61395691e36" ] || fail "unexpected v1.1.1 stamp: $STAMP"
md5sum "$PM/maya-maya-s-v2-iq2_xxs.json" > "$BK/config-md5.txt"
cat "$BK/config-md5.txt"
cp "$PM/maya-maya-s-v2-iq2_xxs.json" "$BK/config-before-pair.json"
NEED=$(du -sb "$MD" | cut -f1); echo "maya bytes: $NEED"; echo "$NEED" > "$BK/maya-need.txt"
df -h / | tail -1
say "preflight OK"

# ---------- 1. stop strata ----------
say "--- [1] stop strata"
p=$(pgrep -f '[s]erve/server.py' | head -1 || true)
[ -n "$p" ] && { echo "stopping pid $p"; kill -TERM "$p"; }
for i in $(seq 1 60); do pgrep -f '[s]erve/server.py' >/dev/null 2>&1 || break; sleep 2; done
for i in $(seq 1 90); do
  V=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END {print s+0}')
  if ! pgrep -f '[e]ngine-cuda12/strata' >/dev/null 2>&1 && [ "$V" -lt 1000 ]; then break; fi
  sleep 2
done
if pgrep -f '[e]ngine-cuda12/strata' >/dev/null 2>&1; then
  e=$(pgrep -f '[e]ngine-cuda12/strata' | head -1); echo "engine lingers ($e) - TERM"; kill -TERM "$e"; sleep 8
fi
pgrep -f '[e]ngine-cuda12/strata' >/dev/null 2>&1 && fail "strata engine will not die"
pgrep -f '[s]erve/server.py' >/dev/null 2>&1 && fail "server still up"
V=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END {print s+0}')
[ "$V" -lt 2000 ] || fail "VRAM not released: ${V}MiB"
say "strata stopped; vram=${V}MiB"

# ---------- 2. teardown iq3_s nvme set ----------
say "--- [2] teardown iq3_s"
rm "$PACKS/iq3_s" || fail "rm pack symlink"
mv "$PACKS/iq3_s.hdd-original" "$PACKS/iq3_s" || fail "pack restore"
rm "$IQ3DIR/$B1" || fail "rm shard1 symlink"
mv "$IQ3DIR/$B1.hdd-original" "$IQ3DIR/$B1" || fail "shard1 restore"
[ -f "$PACKS/iq3_s/experts.bin" ] || fail "pack restore verify"
[ "$(stat -c%s "$IQ3DIR/$B1")" = "$B1SIZE" ] || fail "shard1 restore verify"
rm -rf "$NV/iq3_s" "$NV/packs/iq3_s" || fail "rm nvme copies"
ls -la "$NV" 2>/dev/null || true
df -h / | tail -1

# ---------- 3. free space gate ----------
FREE=$(df --output=avail -B1 / | tail -1); echo "free: $FREE"
[ "$FREE" -gt $((NEED + 5000000000)) ] || fail "not enough free space ($FREE < $NEED+5G)"

# ---------- 4. copy maya to nvme ----------
say "--- [4] copy maya hdd->nvme $(date -u)"
mkdir -p "$MAYANV" || fail "mkdir maya-nvme"
sync
cp -a "$MD" "$MAYANV/" || fail "cp maya"
sync
say "copy done $(date -u)"; df -h / | tail -1
a=$(du -sb "$MD" | cut -f1); b=$(du -sb "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs" | cut -f1)
echo "du hdd=$a nvme=$b"; [ "$a" = "$b" ] || fail "du mismatch"
for f in GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00002-of-00003.gguf GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00003-of-00003.gguf; do
  x=$(stat -c%s "$MD/$f"); y=$(stat -c%s "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs/$f")
  [ "$x" = "$y" ] || fail "size mismatch $f"
  echo "$f ok ($x)"
done
cmp -s "$MD/vision/GLM-5.3-Flash-vocab.gguf" "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs/vision/GLM-5.3-Flash-vocab.gguf" || fail "vocab cmp"
echo "vocab cmp ok"

# ---------- 5. flip ----------
say "--- [5] flip standard path -> NVMe"
cd "$MBAY" || fail "cd mbay"
mv glm-5.3-flash-maya-s-v2-iq2_xxs glm-5.3-flash-maya-s-v2-iq2_xxs.hdd-original || fail "mv hdd dir"
ln -s "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs" glm-5.3-flash-maya-s-v2-iq2_xxs || fail "ln symlink"
ls -la | head -8
head -3 glm-5.3-flash-maya-s-v2-iq2_xxs/pack/index.txt >/dev/null || fail "index not readable through symlink"
stat -L -c%s "$MD/GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf" >/dev/null || fail "shard1 not readable through symlink"
say "prep done; box ready for cycle"
echo 0 > "$DONE"
