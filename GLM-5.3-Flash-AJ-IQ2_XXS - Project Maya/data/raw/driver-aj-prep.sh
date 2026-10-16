#!/bin/bash
# maya-aj-prep-2026-10-16.sh - stage aj9o9's AJ-IQ2_XXS (GLM-5.3-Flash, 87.35 GB, 2 shards) for Maya:
# HDD master -> SN730 working copy (~/maya-nvme), verify sha256 against HF, flip the standard path to a symlink,
# pre-place the (shared, sha-checked) vision files so the setup does not re-download them.
# Runs with Maya still serving (touches only the AJ folder + symlink). Adapted from maya-sn730-cycle.sh steps 1-2.
set -u
LOG=/home/eamon/maya-aj-prep.log
DONE=/home/eamon/maya-aj-prep.done
HDD=/mnt/models/GLM-5.3-Flash-AJ-IQ2_XXS-GGUF
NAME=glm-5.3-flash-aj-iq2_xxs
NV=/home/eamon/maya-nvme
MS="$NV/glm-5.3-flash-maya-s-v2-iq2_xxs"
S1=GLM-5.3-Flash-AJ-IQ2_XXS-00001-of-00002.gguf
S2=GLM-5.3-Flash-AJ-IQ2_XXS-00002-of-00002.gguf
SHA1=1fa0535ecddaee4ff127eb8ffd47d3855ca7efa1cc29c996c24da699c5fbe3f7
SHA2=ab8abbde061254a7f6b1a16b3627c4b77e3084f52e3d9739ebaa515b9365945c
VMM=3627575df16bd152db0f3fd7e488d270b33f3a9e6c7fa3b1b8ac381faafde882
VVOC=8f53cb1bd2e631c14ef413e3284735d9e53f3c508d07a6f609e705b487105912
exec > "$LOG" 2>&1
rm -f "$DONE"
fail(){ echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
say(){ echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
echo "=== AJ prep started $(date -u) UTC ==="

say "--- preflight"
[ -d "$HDD" ] && [ ! -L "$HDD" ] || fail "$HDD missing or already a symlink"
[ -f "$HDD/$S1.done" ] || fail "$S1.done missing"
[ -f "$HDD/$S2.done" ] || fail "$S2.done missing"
[ ! -e "$NV/$NAME" ] || fail "$NV/$NAME already exists"
mountpoint -q "$NV" || fail "~/maya-nvme is not the NVMe bind"
[ -d "$MS" ] || fail "Maya-S nvme copy missing (vision source)"
NEED=$(du -sb "$HDD" | cut -f1); FREE=$(df --output=avail -B1 /mnt/nvme | tail -1)
echo "need=$NEED free=$FREE"
[ "$FREE" -gt $((NEED + 8000000000)) ] || fail "not enough space on /mnt/nvme"

say "--- copy HDD -> NVMe $(date -u)"
sync
cp -a "$HDD" "$NV/" || fail "cp"
sync
say "copy done $(date -u)"
a=$(du -sb "$HDD" | cut -f1); b=$(du -sb "$NV/$NAME" | cut -f1)
echo "du src=$a dst=$b"; [ "$a" = "$b" ] || fail "du mismatch"

say "--- sha256 the NVMe copies (against HF metadata)"
h1=$(sha256sum "$NV/$NAME/$S1" | cut -d' ' -f1); h2=$(sha256sum "$NV/$NAME/$S2" | cut -d' ' -f1)
echo "$S1 $h1"; echo "$S2 $h2"
[ "$h1" = "$SHA1" ] || fail "sha256 mismatch $S1"
[ "$h2" = "$SHA2" ] || fail "sha256 mismatch $S2"

say "--- vision files from the Maya-S copy (same files in every GLM-5.3-Flash quant)"
mkdir -p "$NV/$NAME/vision" || fail "mkdir vision"
cp -a "$MS/vision/mmproj-GLM-5.3-Flash-F16.gguf" "$NV/$NAME/vision/" || fail "cp mmproj"
cp -a "$MS/vision/GLM-5.3-Flash-vocab.gguf" "$NV/$NAME/vision/" || fail "cp vocab"
vm=$(sha256sum "$NV/$NAME/vision/mmproj-GLM-5.3-Flash-F16.gguf" | cut -d' ' -f1)
vv=$(sha256sum "$NV/$NAME/vision/GLM-5.3-Flash-vocab.gguf" | cut -d' ' -f1)
echo "mmproj $vm"; echo "vocab $vv"
[ "$vm" = "$VMM" ] || fail "mmproj sha256 mismatch vs the published one"
[ "$vv" = "$VVOC" ] || fail "vocab sha256 mismatch vs the published one"

say "--- flip the standard path"
cd /mnt/models || fail "cd /mnt/models"
mv "$HDD" "$HDD.hdd-original" || fail "mv hdd dir"
ln -s "$NV/$NAME" "$HDD" || fail "ln symlink"
[ "$(readlink "$HDD")" = "$NV/$NAME" ] || fail "symlink target unexpected"
[ "$(dd if=$HDD/$S1 bs=4 count=1 2>/dev/null)" = "GGUF" ] || fail "GGUF magic not readable through symlink"
head -2 "$HDD/pack/index.txt" >/dev/null 2>&1 || true   # pack not built yet is fine
say "flip done: $HDD -> $NV/$NAME"
echo "=== AJ prep OK $(date -u) ==="
echo 0 > "$DONE"
