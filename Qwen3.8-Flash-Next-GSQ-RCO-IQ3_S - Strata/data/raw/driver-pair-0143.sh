#!/bin/bash
# Strata on .5: update to v0.1.43, swap the NVMe working set back to iq3_s (Maya out), then
# the same-day pair v0.1.42 vs v0.1.43 (six depths, model-bench standard). Deployed 2026-10-11.
set -u
LOG=/home/eamon/strata-update-0143.log
DONE=/home/eamon/strata-update-0143.done
BK=/home/eamon/strata-backup-2026-10-11-0143
exec > "$LOG" 2>&1
rm -f "$DONE"
mkdir -p "$BK"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
echo "=== strata update v0.1.43 + pair started $(date -u) ==="

PACKS=/mnt/models/Strata-data/packs
IQDIR="/mnt/models/Qwen3.8-Flash-Next/ISTA DASLab/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S"
I1=Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf
NV=/home/eamon/strata-nvme
MD_H="/mnt/models/Maya-data/models"
MAYANV=/home/eamon/maya-nvme
MDR=glm-5.3-flash-maya-s-v2-iq2_xxs
STRATA=/home/eamon/Strata

stop_servers() {
  local p e V i
  p=$(pgrep -f 'project-maya/[s]erve/server.py' | head -1 || true)
  [ -n "$p" ] && { echo "stopping maya server pid $p"; kill -TERM "$p"; }
  p=$(pgrep -f '[s]erve/server.py' | head -1 || true)
  [ -n "$p" ] && { echo "stopping server pid $p"; kill -TERM "$p"; }
  sleep 8
  for i in $(seq 1 60); do
    if ! pgrep -f '[s]erve/server.py' >/dev/null 2>&1 && ! pgrep -f '[e]ngine-cuda12/strata' >/dev/null 2>&1; then break; fi
    sleep 2
  done
  if pgrep -f '[e]ngine-cuda12/strata' >/dev/null 2>&1; then
    e=$(pgrep -f '[e]ngine-cuda12/strata' | head -1); echo "engine lingers ($e) - TERM"; kill -TERM "$e"; sleep 6
  fi
  pgrep -f '[s]erve/server.py' >/dev/null 2>&1 && fail "a server will not stop"
  for i in $(seq 1 60); do
    V=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END {print s+0}')
    [ "$V" -lt 1500 ] && break
    sleep 2
  done
  echo "stopped; vram: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
}
stop_strata_only() {
  local p e V i
  p=$(pgrep -f '[s]erve/server.py' | head -1 || true)
  [ -n "$p" ] && { echo "stopping strata server pid $p"; kill -TERM "$p"; }
  for i in $(seq 1 60); do pgrep -f '[s]erve/server.py' >/dev/null 2>&1 || break; sleep 2; done
  for i in $(seq 1 90); do
    V=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END {print s+0}')
    if ! pgrep -f '[e]ngine-cuda12/strata' >/dev/null 2>&1 && [ "$V" -lt 1000 ]; then break; fi
    sleep 2
  done
  if pgrep -f '[e]ngine-cuda12/strata' >/dev/null 2>&1; then
    e=$(pgrep -f '[e]ngine-cuda12/strata' | head -1); kill -TERM "$e"; sleep 8
  fi
  pgrep -f '[e]ngine-cuda12/strata' >/dev/null 2>&1 && fail "strata engine will not stop"
  echo "strata stopped"
}
start_iq3s() {  # $1 tag
  cd "$STRATA" || fail "cd strata"
  STRATA_EXPERIMENTAL_SM60=1 setsid -f bash -c "cd $STRATA && exec ./run-iq3_s.sh > $BK/iq3_s-run-$1.log 2>&1 < /dev/null"
  local i ok=0
  for i in $(seq 1 168); do
    if curl -s --max-time 3 http://127.0.0.1:8080/v1/models 2>/dev/null | grep -q '"loaded"'; then ok=1; break; fi
    sleep 5
  done
  [ "$ok" = 1 ] || fail "strata not ready ($1)"
  echo "ready after ~$((i*5))s ($1)"
  curl -s --max-time 5 http://127.0.0.1:8080/v1/models | head -c 250; echo
}
warmup() {
python3 - <<'PY'
import json, urllib.request, glob
text = ""
for f in ['/home/eamon/Strata/docs/DETAILS.md'] + sorted(glob.glob('/home/eamon/Strata/docs/*.md')):
    try: text += open(f, encoding='utf-8', errors='ignore').read() + "\n"
    except Exception: pass
    if len(text) >= 90000: break
req = json.dumps({"model": "x", "messages": [{"role": "user", "content": "Read.\n\n" + text[:90000]}], "max_tokens": 4, "temperature": 0}).encode()
try:
    r = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8080/v1/chat/completions", data=req, headers={"Content-Type": "application/json"}), timeout=900)
    print("warmup ok:", json.load(r).get("usage", {}).get("prompt_tokens"))
except Exception as e:
    print("warmup failed:", e)
PY
}
bench() {  # $1 label (six depths)
  cd /home/eamon/model-bench || fail "cd model-bench"
  /home/eamon/Strata/.venv/bin/python bench.py --url http://127.0.0.1:8080 --label "$1"
  local rc=$?
  echo "bench $1 rc=$rc $(date -u)"
  [ "$rc" = 0 ] || fail "bench $1 rc=$rc"
}

echo "--- [0] pre-state snapshots"
cd "$STRATA" || fail "cd strata"
git describe --tags
cp -a strata-*.json "$BK"/ 2>/dev/null
md5sum strata-*.json > "$BK/configs-pre.md5"
cat engine-cuda12/BUILD.json engine/BUILD.json > "$BK/BUILD-pre.txt" 2>/dev/null

echo "--- [1] stop maya + teardown maya nvme set ($(date -u))"
stop_servers
[ -L "$MD_H/$MDR" ] || fail "maya standard path is not a flipped symlink"
[ -d "$MD_H/$MDR.hdd-original" ] || fail "maya .hdd-original missing"
S1=GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00001-of-00003.gguf
S2=GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00002-of-00003.gguf
S3=GLM-5.3-Flash-Maya-S-v2-IQ2_XXS-00003-of-00003.gguf
for f in "$S1" "$S2" "$S3"; do
  x=$(stat -L -c%s "$MD_H/$MDR/$f"); y=$(stat -c%s "$MD_H/$MDR.hdd-original/$f")
  echo "maya $f: nvme=$x hdd=$y"; [ "$x" = "$y" ] || fail "maya shard size mismatch: $f"
done
(cd "$MD_H/$MDR" && find . -type f -printf '%P\t%s\n' | sort) > /tmp/maya-nvme-list.txt
(cd "$MD_H/$MDR.hdd-original" && find . -type f -printf '%P\t%s\n' | sort) > /tmp/maya-hdd-list.txt
DIFFLINES=$(diff /tmp/maya-nvme-list.txt /tmp/maya-hdd-list.txt || true)
echo "--- tree diff (only pack/expert_usage.txt is expected):"; printf '%s\n' "$DIFFLINES"
UNEXPECTED=$(printf '%s\n' "$DIFFLINES" | grep -E '^[<>] ' | grep -v 'expert_usage.txt' || true)
[ -z "$UNEXPECTED" ] || fail "unexpected nvme/hdd differences (see log)"
mkdir -p /mnt/models/maya-nvme-archive/pack
cp -a "$MD_H/$MDR/pack/expert_usage.txt" /mnt/models/maya-nvme-archive/pack/expert_usage.txt && echo "archived pack/expert_usage.txt (runtime usage file)" || echo "warn: no expert_usage.txt to archive"
rm "$MD_H/$MDR" && mv "$MD_H/$MDR.hdd-original" "$MD_H/$MDR" || fail "maya restore to hdd"
rm -rf "$MAYANV" || fail "rm maya-nvme"
echo "maya back on hdd; df:"; df -h / | tail -1

echo "--- [2] copy iq3_s hdd->nvme ($(date -u))"
[ -d "$PACKS/iq3_s" ] && [ ! -L "$PACKS/iq3_s" ] || fail "iq3_s pack not a plain hdd dir"
[ -f "$IQDIR/$I1" ] && [ ! -L "$IQDIR/$I1" ] || fail "iq3_s shard1 not a plain hdd file"
NEEDP=$(du -sb "$PACKS/iq3_s" | cut -f1)
NEEDS=$(stat -c%s "$IQDIR/$I1")
FREE=$(df --output=avail -B1 / | tail -1)
echo "free=$FREE need=$((NEEDP+NEEDS))"
[ "$FREE" -gt $((NEEDP + NEEDS + 5000000000)) ] || fail "not enough free space"
mkdir -p "$NV/iq3_s" "$NV/packs"
cp -a "$PACKS/iq3_s" "$NV/packs/iq3_s" || fail "pack copy"
cp -a "$IQDIR/$I1" "$NV/iq3_s/$I1" || fail "shard1 copy"
echo "copies done $(date -u)"; df -h / | tail -1

echo "--- [3] verify + flip"
a=$(du -sb "$PACKS/iq3_s" | cut -f1); b=$(du -sb "$NV/packs/iq3_s" | cut -f1)
echo "pack du hdd=$a nvme=$b"; [ "$a" = "$b" ] || fail "pack du mismatch"
x=$(stat -c%s "$IQDIR/$I1"); y=$(stat -c%s "$NV/iq3_s/$I1")
echo "shard1 hdd=$x nvme=$y"; [ "$x" = "$y" ] || fail "shard1 size mismatch"
sync
mv "$PACKS/iq3_s" "$PACKS/iq3_s.hdd-original" && ln -s "$NV/packs/iq3_s" "$PACKS/iq3_s" || fail "pack flip"
mv "$IQDIR/$I1" "$IQDIR/$I1.hdd-original" && ln -s "$NV/iq3_s/$I1" "$IQDIR/$I1" || fail "shard1 flip"
stat -L -c%s "$PACKS/iq3_s/experts.bin" >/dev/null || fail "pack not readable through symlink"
stat -L -c%s "$IQDIR/$I1" >/dev/null || fail "shard1 not readable through symlink"
echo "flip done"

echo "--- [4] strata update to v0.1.43 ($(date -u))"
cd "$STRATA" || fail "cd strata"
git fetch origin --tags --force || fail "fetch"
git checkout v0.1.43 || fail "checkout v0.1.43"
git describe --tags
export STRATA_EXPERIMENTAL_SM60=1
./setup.sh --update
echo "setup rc=$?"
grep '"version"' engine-cuda12/BUILD.json
echo "--- configs vs pre:"
md5sum -c "$BK/configs-pre.md5" 2>&1 | grep -v ': OK' || echo "all configs unchanged"

echo "--- [5] start v0.1.43 + bench ($(date -u))"
start_iq3s 0143
warmup
bench strata-0-1-43-base

echo "--- [6] rollback v0.1.42 + bench ($(date -u))"
stop_strata_only
git checkout v0.1.42 || fail "checkout v0.1.42"
git describe --tags
./setup.sh --update
echo "rollback setup rc=$?"
grep '"version"' engine-cuda12/BUILD.json
start_iq3s 0142
warmup
bench strata-0-1-42-base-rerun

echo "--- [7] restore v0.1.43 ($(date -u))"
stop_strata_only
git checkout v0.1.43 || fail "checkout v0.1.43"
git describe --tags
./setup.sh --update
echo "restore setup rc=$?"
grep '"version"' engine-cuda12/BUILD.json
start_iq3s 0143b
curl -s --max-time 5 http://127.0.0.1:8080/v1/models | head -c 250; echo
echo "=== strata update v0.1.43 + pair done $(date -u) ==="
echo 0 > "$DONE"
