#!/bin/bash
# maya-aj-prep-resume-2026-10-16.sh - resume after the original prep script (maya-aj-prep-2026-10-16.sh) failed
# its du check because cp landed the copy under the source basename (GLM-5.3-Flash-AJ-IQ2_XXS-GGUF) instead of
# the intended NVMe name glm-5.3-flash-aj-iq2_xxs. Covers the remaining steps: rename -> du verify -> sha256 both
# files vs HF -> vision pre-copy + sha -> flip the standard path -> done.
set -u
LOG=/home/eamon/maya-aj-prep-resume.log
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
echo "=== AJ prep resume started $(date -u) UTC ==="

say "--- preflight"
pgrep -f '[c]p -a /mnt/models' >/dev/null 2>&1 && fail "a cp is still running"
[ -d "$HDD" ] && [ ! -L "$HDD" ] || fail "HDD source not a plain dir"
[ ! -e "$HDD.hdd-original" ] || fail ".hdd-original already exists"
A=$(du -sb "$HDD" | cut -f1)
if [ -d "$NV/GLM-5.3-Flash-AJ-IQ2_XXS-GGUF" ] && [ ! -e "$NV/$NAME" ]; then
  say "--- rename copied dir to $NAME"
  B1=$(du -sb "$NV/GLM-5.3-Flash-AJ-IQ2_XXS-GGUF" | cut -f1)
  echo "du before rename: src=$A dst=$B1"
  [ "$A" = "$B1" ] || fail "du mismatch before rename ($A vs $B1)"
  mv "$NV/GLM-5.3-Flash-AJ-IQ2_XXS-GGUF" "$NV/$NAME" || fail "rename"
else
  say "--- no rename needed (already named or already renamed)"
fi
[ -d "$NV/$NAME" ] || fail "$NV/$NAME missing"
B=$(du -sb "$NV/$NAME" | cut -f1)
echo "du src=$A dst=$B"; [ "$A" = "$B" ] || fail "du mismatch"
[ "$(stat -c%s "$HDD/$S1")" = "$(stat -c%s "$NV/$NAME/$S1")" ] || fail "size mismatch $S1"
[ "$(stat -c%s "$HDD/$S2")" = "$(stat -c%s "$NV/$NAME/$S2")" ] || fail "size mismatch $S2"

say "--- sha256 the NVMe copies (vs HF metadata)"
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
say "flip done: $HDD -> $NV/$NAME"
echo "=== AJ prep resume OK $(date -u) ==="
echo 0 > "$DONE"
