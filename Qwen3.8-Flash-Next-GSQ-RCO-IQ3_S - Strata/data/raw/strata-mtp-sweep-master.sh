#!/bin/bash
# Full sweep 3 chain on box .5: stage A (gate x depth) -> suffix 0 -> suffix 8 -> coupled on ->
# stage B (samplers) -> restore config (winner gate as default). All as eamon; server restarts
# for engine-flag stages. Ends with /tmp/strata-sweep3.done.
cd /home/eamon/Strata || exit 1
OUT=/tmp/strata-sweep3.out

run() {
  echo "== $(date -u +%H:%M:%S) run $*" >> "$OUT"
  python3 /tmp/strata-sweep3.py "$@" >> "$OUT" 2>&1
}

restart() {
  PID=$(pgrep -f "serve/server.py" | head -1)
  [ -n "$PID" ] && kill -TERM "$PID"
  sleep 6
  setsid bash -c "/home/eamon/strata-start.sh > /tmp/strata-start-sweep3.log 2>&1 < /dev/null" < /dev/null > /dev/null 2>&1 &
  r=""
  for i in $(seq 1 30); do
    sleep 10
    r=$(curl -s -m 4 http://127.0.0.1:8080/v1/models)
    [ -n "$r" ] && { echo "== $(date -u +%H:%M:%S) restart ready ~$((i*10))s" >> "$OUT"; return 0; }
  done
  echo "RESTART FAILED" >> "$OUT"
  return 1
}

setcfg() {
  python3 - "$1" "$2" >> "$OUT" <<'PY'
import json, sys
mode, val = sys.argv[1], sys.argv[2]
p = "/home/eamon/Strata/strata-iq3_s.json"
d = json.load(open(p))
a = d["args"]
def drop(flag):
    while flag in a:
        i = a.index(flag)
        del a[i:i + (2 if i + 1 < len(a) and not str(a[i + 1]).startswith("--") else 1)]
if mode == "suffix":
    drop("--suffix-draft")
    if val != "default":
        a += ["--suffix-draft", val]
elif mode == "coupled":
    drop("--coupled-draft")
    drop("--no-coupled-draft")
    if val == "on":
        a += ["--coupled-draft"]
elif mode == "gate":
    try:
        win = open("/tmp/strata-sweep3.winner").read().strip()
    except Exception:
        win = "0.5"
    i = a.index("--spec-min-p")
    a[i + 1] = win
json.dump(d, open(p, "w"), indent=1)
print("cfg", mode, val, "-> tail:", " ".join(str(x) for x in a[-4:]))
PY
}

echo "SWEEP3 MASTER START $(date -u +%H:%M:%S)" > "$OUT"
run stageA
[ -f /tmp/strata-sweep3.winner ] || { echo "NO WINNER - ABORT" >> "$OUT"; touch /tmp/strata-sweep3.done; exit 1; }

setcfg suffix 0;   restart; run stageS 0
setcfg suffix 8;   restart; run stageS 8
setcfg suffix default; setcfg coupled on; restart; run stageC on
setcfg coupled off; restart; run stageB
setcfg suffix default
setcfg coupled off
setcfg gate winner
restart
echo "SWEEP3 ALL DONE $(date -u +%H:%M:%S)" >> "$OUT"
touch /tmp/strata-sweep3.done
