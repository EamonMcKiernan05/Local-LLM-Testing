#!/bin/bash
# stage 1: stop served Maya-S, delete it (NVMe weights + SATA engram), update to v1.1.22,
# download the Maya-XS set with the 120.6 GB weights on the NVMe and the two 161 GB Engram shards on the SATA SSD.
set -u
LOG=/home/eamon/xs-stage1.log
DONE=/home/eamon/xs-stage1.done
rm -f "$DONE"
exec > "$LOG" 2>&1
say(){ echo "[$(date -u +%FT%TZ)] $*"; }
fail(){ say "FAIL: $*"; echo "FAIL $*" > "$DONE"; exit 1; }

REPO="https://huggingface.co/peasantsmith/DeepSeek-V4.1-Flash-1017-Maya-GGUF/resolve/c273fcbdda76a1db074c2f414cb70edbfca2f2ef/Maya-XS"
NV=/mnt/nvme/maya-ds4/Maya-XS
EN=/home/eamon/maya-ds4/engram-xs

say "=== stage 1 start ==="

# ---------------- 1. stop the served Maya-S
PID=$(pgrep -f '[m]aya.py --config .*maya-ds4.json' | head -1)
say "maya.py pid=${PID:-none}"
if [ -n "${PID:-}" ]; then kill -TERM "$PID"; fi
for i in $(seq 1 90); do pgrep -f '[m]aya.py --config .*maya-ds4.json' >/dev/null || break; sleep 2; done
sleep 5
VR=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}')
say "VRAM used after stop: ${VR} MiB"
[ "$VR" -lt 2000 ] || fail "VRAM still ${VR} MiB"

# ---------------- 2. delete the outgoing quant
say "--- before delete:"; du -sh /mnt/nvme/maya-ds4/Maya-S /home/eamon/maya-ds4/engram 2>/dev/null
rm -rf /mnt/nvme/maya-ds4/Maya-S || fail "rm Maya-S"
rm -rf /home/eamon/maya-ds4/engram || fail "rm engram"
say "deleted"; df -h / /mnt/nvme | tail -2

# ---------------- 3. update the tree
cd /home/eamon/project-maya || fail "cd project-maya"
git fetch origin --tags --force -q || fail "git fetch"
git checkout -f v1.1.22 || fail "git checkout v1.1.22"
say "tree now: $(git describe --tags) ($(git rev-parse --short HEAD))"

# ---------------- 4. layout: 3 weight shards on NVMe, 2 Engram shards on the SATA SSD (symlinked in)
mkdir -p "$NV" "$EN" || fail "mkdir model dirs"
for n in 4 5; do
  f="DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-0000${n}-of-00005.gguf"
  ln -sfn "$EN/$f" "$NV/$f"
done
ls -la "$NV" "$EN"

# ---------------- 5. download, 5 files at once, each resumable
dl(){
  local f="$1" want="$2" dest="$3" tries=0 have rc
  while :; do
    have=$(stat -c %s "$dest" 2>/dev/null || echo 0)
    if [ "$have" = "$want" ]; then say "OK   $f ($want bytes)"; return 0; fi
    tries=$((tries+1))
    if [ "$tries" -gt 60 ]; then say "GIVE UP $f after $tries runs"; return 1; fi
    curl -sS -L --fail --retry 3 --retry-delay 5 -C - --speed-limit 1024 --speed-time 60 \
         --connect-timeout 30 -o "$dest" "$REPO/$f"
    rc=$?
    say "curl $f rc=$rc size=$(stat -c %s "$dest" 2>/dev/null || echo 0)/$want"
    sleep 3
  done
}

say "--- download start (276.6 GB total)"
dl DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00001-of-00005.gguf 47781530400 "$NV/DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00001-of-00005.gguf" &
P1=$!
dl DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00002-of-00005.gguf 47775748128 "$NV/DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00002-of-00005.gguf" &
P2=$!
dl DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00003-of-00005.gguf 19784230848 "$NV/DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00003-of-00005.gguf" &
P3=$!
dl DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00004-of-00005.gguf 80641295472 "$EN/DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00004-of-00005.gguf" &
P4=$!
dl DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00005-of-00005.gguf 80643503412 "$EN/DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00005-of-00005.gguf" &
P5=$!

# progress line every 2 minutes
( while :; do sleep 120
  a=$(du -sb "$NV" 2>/dev/null | cut -f1); b=$(du -sb "$EN" 2>/dev/null | cut -f1)
  say "progress: $(numfmt --to=iec ${a:-0}) nvme + $(numfmt --to=iec ${b:-0}) sata of 276.6 GB"
done ) & PROG=$!

wait $P1; R1=$?; wait $P2; R2=$?; wait $P3; R3=$?; wait $P4; R4=$?; wait $P5; R5=$?
kill $PROG 2>/dev/null
say "download results: $R1 $R2 $R3 $R4 $R5"
[ $R1$R2$R3$R4$R5 = 00000 ] || fail "a download did not finish"

# ---------------- 6. sha256 against the published hashes
say "--- sha256 check"
cat > /tmp/maya-xs.sha <<'EOF'
a0cb7966afd68bc35c46f78018d1fa1d2e4bcbe3c3baf39f60cd1733ed9ad7e5  DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00001-of-00005.gguf
ba5afb43adfc667436ebcfbd82d25411fa2843ee7e1d877290611cd60f93cca1  DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00002-of-00005.gguf
1482443bb4957c8d2f005ded365445f98558ff05c50674f9ee9a96ddabc122a4  DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00003-of-00005.gguf
0d93315942c523d82f6dbc0a6e0e1751548e309f3963f96b82f92e8f9bc52e36  DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00004-of-00005.gguf
39bbc8cde8b17604fed9a7ba7fc6bc9c5e72e34733657943ac049b4b9ca2d340  DeepSeek-V4.1-Flash-1017-Maya-XS-IQ1_S-00005-of-00005.gguf
EOF
( cd "$NV" && sha256sum -c /tmp/maya-xs.sha 2>&1 | grep -E '0000[1-3]' ) || fail "sha256 weights"
( cd "$EN" && sha256sum -c /tmp/maya-xs.sha 2>&1 | grep -E '0000[4-5]' ) || fail "sha256 engram"

say "--- final sizes"; du -sh "$NV" "$EN"; df -h / /mnt/nvme | tail -2
say "ALL DONE"
echo OK > "$DONE"
