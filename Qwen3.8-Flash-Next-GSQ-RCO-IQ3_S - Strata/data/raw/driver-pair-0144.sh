#!/bin/bash
# Strata on .5: update v0.1.43 -> v0.1.44, then the same-day pair v0.1.43 vs v0.1.44
# (six depths, model-bench standard). Old side FIRST: 0.1.43 is what is live/as-served,
# bench it, then update, bench 0.1.44. Deployed 2026-10-13.
set -u
LOG=/home/eamon/strata-update-0144.log
DONE=/home/eamon/strata-update-0144.done
BK=/home/eamon/strata-backup-2026-10-13-0144
STRATA=/home/eamon/Strata
exec > "$LOG" 2>&1
rm -f "$DONE"
mkdir -p "$BK"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
echo "=== strata update v0.1.44 + pair started $(date -u) ==="

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
    e=$(pgrep -f '[e]ngine-cuda12/strata' | head -1); echo "engine lingers ($e) - TERM"; kill -TERM "$e"; sleep 8
  fi
  pgrep -f '[e]ngine-cuda12/strata' >/dev/null 2>&1 && fail "strata engine will not stop"
  echo "strata stopped; vram: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
}
start_iq3s() {  # $1 tag, $2 logfile
  cd "$STRATA" || fail "cd strata"
  STRATA_EXPERIMENTAL_SM60=1 setsid -f bash -c "cd $STRATA && exec ./run-iq3_s.sh > $2 2>&1 < /dev/null"
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
cat engine-cuda12/BUILD.json > "$BK/BUILD-pre.txt" 2>/dev/null

echo "--- [1] v0.1.43 as-served pair side: warmup + bench as served ($(date -u))"
warmup
bench strata-0-1-43-base-rerun

echo "--- [2] update to v0.1.44 ($(date -u))"
stop_strata_only
cd "$STRATA" || fail "cd strata"
git fetch origin --tags --force || fail "fetch"
git checkout v0.1.44 || fail "checkout v0.1.44"
git describe --tags
export STRATA_EXPERIMENTAL_SM60=1
./setup.sh --update
echo "setup rc=$?"
grep '"version"' engine-cuda12/BUILD.json
[ -x engine-cuda12/strata ] || fail "engine binary missing after update"
echo "--- configs vs pre:"
md5sum -c "$BK/configs-pre.md5" 2>&1 | grep -v ': OK' || echo "all configs unchanged"

echo "--- [3] start v0.1.44 + bench ($(date -u))"
start_iq3s 0144 /home/eamon/strata-iq3_s-run.log
warmup
bench strata-0-1-44-base

echo "--- [4] summary ($(date -u))"
for d in /home/eamon/model-bench/runs/*strata-0-1-43-base-rerun* /home/eamon/model-bench/runs/*strata-0-1-44-base*; do
  echo "# $d"; sha256sum "$d/results.jsonl" "$d/meta.json" 2>/dev/null
done
curl -s http://127.0.0.1:8080/v1/models | head -c 250; echo
echo "=== strata update v0.1.44 + pair done $(date -u) ==="
echo 0 > "$DONE"
