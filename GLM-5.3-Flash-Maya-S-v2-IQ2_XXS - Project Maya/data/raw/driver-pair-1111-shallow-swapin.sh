#!/bin/bash
# Maya shallow range prep (2026-10-15, second visit): Strata iq3_s out, Maya HDD->NVMe, flip.
set -u
LOG=/home/eamon/maya-shallow-swapin.log
DONE=/home/eamon/maya-shallow-swapin.done
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
exec > "$LOG" 2>&1
rm -f "$DONE"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
echo "=== maya shallow swap-in started $(date -u) UTC ==="

say "--- [0] preflight"
curl -s -m 5 http://127.0.0.1:8080/v1/models | grep -q 'qwen3.8-flash-next-iq3_s' || fail "iq3_s not serving"
[ -L "$PACKS/iq3_s" ] || fail "packs/iq3_s not a symlink"
[ "$(readlink -f "$PACKS/iq3_s")" = "$NV/packs/iq3_s" ] || fail "iq3_s pack target unexpected"
[ -f "$PACKS/iq3_s.hdd-original/experts.bin" ] || fail "pack hdd-original missing"
[ -L "$IQ3DIR/$B1" ] || fail "iq3_s shard1 not a symlink"
[ "$(readlink -f "$IQ3DIR/$B1")" = "$NV/iq3_s/$B1" ] || fail "shard1 target unexpected"
[ -f "$IQ3DIR/$B1.hdd-original" ] || fail "shard1 hdd-original missing"
[ -d "$MD" ] && [ ! -L "$MD" ] || fail "maya dir not plain"
[ ! -e "$MD.hdd-original" ] || fail "maya .hdd-original exists"
[ ! -e "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs" ] || fail "maya nvme copy exists"
NEED=$(du -sb "$MD" | cut -f1); echo "need: $NEED"
say "preflight OK"

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

say "--- [2] teardown iq3_s"
rm "$PACKS/iq3_s" || fail "rm pack symlink"
mv "$PACKS/iq3_s.hdd-original" "$PACKS/iq3_s" || fail "pack restore"
rm "$IQ3DIR/$B1" || fail "rm shard1 symlink"
mv "$IQ3DIR/$B1.hdd-original" "$IQ3DIR/$B1" || fail "shard1 restore"
[ -f "$PACKS/iq3_s/experts.bin" ] || fail "pack restore verify"
[ "$(stat -c%s "$IQ3DIR/$B1")" = "$B1SIZE" ] || fail "shard1 restore verify"
rm -rf "$NV/iq3_s" "$NV/packs/iq3_s" || fail "rm nvme copies"
rmdir "$NV/packs" 2>/dev/null || true
df -h / | tail -1

say "--- [3] space gate"
FREE=$(df --output=avail -B1 / | tail -1); echo "free: $FREE"
[ "$FREE" -gt $((NEED + 5000000000)) ] || fail "not enough free space"

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
done
cmp -s "$MD/vision/GLM-5.3-Flash-vocab.gguf" "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs/vision/GLM-5.3-Flash-vocab.gguf" || fail "vocab cmp"
echo "verify ok"

say "--- [5] flip"
cd "$MBAY" || fail "cd mbay"
mv glm-5.3-flash-maya-s-v2-iq2_xxs glm-5.3-flash-maya-s-v2-iq2_xxs.hdd-original || fail "mv hdd dir"
ln -s "$MAYANV/glm-5.3-flash-maya-s-v2-iq2_xxs" glm-5.3-flash-maya-s-v2-iq2_xxs || fail "ln symlink"
head -3 glm-5.3-flash-maya-s-v2-iq2_xxs/pack/index.txt >/dev/null || fail "index not readable"
say "swap-in done; box ready for shallow cycle"
echo 0 > "$DONE"
