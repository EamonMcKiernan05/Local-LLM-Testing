#!/bin/bash
# Strata on .5: RESUME the v0.1.43 pair (steps [6]+[7]) after the cwd bug — bench() leaves
# cwd in ~/model-bench, so the original [6] git checkout ran in the wrong repo.
set -u
LOG=/home/eamon/strata-resume-0143.log
DONE=/home/eamon/strata-resume-0143.done
BK=/home/eamon/strata-backup-2026-10-11-0143
STRATA=/home/eamon/Strata
exec > "$LOG" 2>&1
rm -f "$DONE"
fail() { echo "!!! FAILED: $1"; echo 1 > "$DONE"; exit 1; }
echo "=== strata v0.1.43 pair RESUME started $(date -u) ==="
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

echo "--- [6r] rollback v0.1.42 + bench ($(date -u))"
stop_strata_only
cd "$STRATA" || fail "cd strata"
git checkout v0.1.42 || fail "checkout v0.1.42"
git describe --tags
./setup.sh --update
echo "rollback setup rc=$?"
grep '"version"' engine-cuda12/BUILD.json
start_iq3s 0142r
warmup
bench strata-0-1-42-base-rerun

echo "--- [7r] restore v0.1.43 ($(date -u))"
stop_strata_only
cd "$STRATA" || fail "cd strata"
git checkout v0.1.43 || fail "checkout v0.1.43"
git describe --tags
./setup.sh --update
echo "restore setup rc=$?"
grep '"version"' engine-cuda12/BUILD.json
start_iq3s 0143b
curl -s --max-time 5 http://127.0.0.1:8080/v1/models | head -c 250; echo
echo "=== strata v0.1.43 pair RESUME done $(date -u) ==="
echo 0 > "$DONE"
