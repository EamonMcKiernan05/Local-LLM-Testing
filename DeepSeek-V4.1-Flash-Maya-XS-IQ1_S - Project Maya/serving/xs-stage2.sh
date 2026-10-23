#!/bin/bash
# stage 2: Maya-XS's own DSpark drafter (4.25 GB), then the v1.1.22 setup:
# compiles the changed engine sources, verifies + packs the model, writes the config, speed-calibrates the drafter.
set -u
LOG=/home/eamon/xs-stage2.log
DONE=/home/eamon/xs-stage2.done
rm -f "$DONE"
exec > "$LOG" 2>&1
say(){ echo "[$(date -u +%FT%TZ)] $*"; }
fail(){ say "FAIL: $*"; echo "FAIL $*" > "$DONE"; exit 1; }

REPO=https://huggingface.co/peasantsmith/DeepSeek-V4.1-Flash-1017-Maya-GGUF/resolve/c273fcbdda76a1db074c2f414cb70edbfca2f2ef
DS=/mnt/nvme/maya-ds4/dspark
mkdir -p "$DS" || fail mkdir

say "=== stage 2 start: drafter + setup ==="

get(){ local f="$1" want="$2" sha="$3" tries=0 have
  while :; do
    have=$(stat -c %s "$DS/$f" 2>/dev/null || echo 0)
    [ "$have" = "$want" ] && break
    tries=$((tries+1)); [ "$tries" -gt 30 ] && fail "drafter $f stuck at $have/$want"
    curl -sS -L --fail --retry 3 --retry-delay 4 -C - --speed-limit 1024 --speed-time 60 \
         --connect-timeout 30 -o "$DS/$f" "$REPO/dspark/$f"
    say "curl $f rc=$? size=$(stat -c %s "$DS/$f" 2>/dev/null || echo 0)/$want"
    sleep 2
  done
  echo "$sha  $DS/$f" | sha256sum -c - || fail "sha256 $f"
  say "OK   $f"
}
get dspark-xs2.bin 4251725568 8dfe21082a6cb320f334fddb454630c241c6d44e0463eef4f8b0b07334511779
get dspark-xs2.json 99146 56d47ad12d6548a8d3d50a79be96451411f18d5b77064de7b8544bb2da22988f

cd /home/eamon/project-maya || fail "cd project-maya"
say "tree: $(git describe --tags)"
say "--- setup ---"
./maya.sh --setup --yes --no-start --model DeepSeek-V4.1-Flash-1017 \
  --model-dir /mnt/nvme/maya-ds4/Maya-XS --ds4-quant maya-xs \
  --context 131072 --gpus 0,1 --host 0.0.0.0 --port 8080 --no-vision
rc=$?
say "setup rc=$rc"
[ "$rc" -eq 0 ] || fail "setup rc=$rc"

say "=== config ==="; cat maya-ds4.json
say "=== build ==="; ls -la build/maya-ds4; cat build/MAYA-BUILD.json 2>/dev/null
say "=== pack ==="; ls -la /mnt/nvme/maya-ds4/Maya-XS/maya-ds4/ 2>/dev/null
say "ALL DONE"; echo OK > "$DONE"
