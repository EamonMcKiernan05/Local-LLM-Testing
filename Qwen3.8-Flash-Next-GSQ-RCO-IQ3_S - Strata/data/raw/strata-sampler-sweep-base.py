#!/usr/bin/env python3
"""Strata per-request sweep: drafter spec-min-p, then top_k/top_p/min_p sampling trims.
Replays the llama.cpp 27B (3060) value grids on the Strata server. Per-request params, no restarts.
Rows -> /tmp/strata-sweep2.jsonl ; human log on stdout (ends SWEEP2_DONE).
"""
import json
import time
import urllib.request
import random

BASE = "http://127.0.0.1:8080/v1/chat/completions"
TMPL = "Long document follows. Reply with exactly ACK. "
SEED = 12345
MAXTOK = 256


def load(path, chars):
    with open(path) as f:
        return f.read()[:chars]


P20 = load("/tmp/p20k.txt", 72000)
P100 = load("/tmp/p100.txt", 360000)


def run_arm(label, prompt_text, spec_min_p, top_k, top_p, min_p):
    tag = "run%d" % random.randint(0, 10 ** 9)
    req = {"model": "qwen3.8-flash-next-iq3_s",
           "messages": [{"role": "user", "content": "[%s %s] %s" % (tag, label, TMPL) + prompt_text}],
           "max_tokens": MAXTOK, "temperature": 0.5, "seed": SEED,
           "top_k": top_k, "top_p": top_p, "min_p": min_p}
    if spec_min_p is not None:
        req["strata_tune"] = {"spec_min_p": spec_min_p}
    data = json.dumps(req).encode()
    t0 = time.time()
    row = {"label": label, "spec_min_p": spec_min_p, "top_k": top_k, "top_p": top_p, "min_p": min_p}
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(BASE, data=data, headers={"Content-Type": "application/json"}),
            timeout=1800)
        d = json.loads(r.read())
        tt = d.get("timings", {})
        u = d.get("usage", {})
        row.update({"wall_s": round(time.time() - t0, 1), "ptok": u.get("prompt_tokens"),
                    "gen": u.get("completion_tokens"),
                    "prefill_tps": round(tt.get("prompt_per_second", 0), 1),
                    "decode_tps": round(tt.get("predicted_per_second", 0), 1),
                    "draft_n": tt.get("draft_n"), "draft_acc": tt.get("draft_n_accepted")})
    except Exception as e:
        row.update({"error": str(e)[:200], "wall_s": round(time.time() - t0, 1)})
    with open("/tmp/strata-sweep2.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")
    print(json.dumps(row), flush=True)
    return row


print("SWEEP2 START", flush=True)

# Stage A: drafter gate x depth, sampler baseline top_k 20 / top_p 0.95 / min_p 0.0
a_rows = []
for v in (0.0, 0.6, 0.85):
    a_rows.append(run_arm("A-pmin%.2f-20k" % v, P20, v, 20, 0.95, 0.0))
    a_rows.append(run_arm("A-pmin%.2f-100k" % v, P100, v, 20, 0.95, 0.0))
cand = [r for r in a_rows if r.get("label", "").endswith("100k") and "decode_tps" in r]
best_a = max(cand, key=lambda r: r["decode_tps"]) if cand else None
vstar = best_a["spec_min_p"] if best_a else 0.5
print("STAGE A winner spec_min_p =", vstar, "(%s)" % (best_a or {}).get("label"), flush=True)

# Stage B: top_k x min_p at the stage A winner, 100k depth
b_rows = []
for tk in (20, 30, 40, 50):
    for mp in (0.05, 0.08, 0.10):
        b_rows.append(run_arm("B-tk%d-minp%02d" % (tk, round(mp * 100)), P100, vstar, tk, 0.95, mp))
cand = [r for r in b_rows if "decode_tps" in r]
best_b = max(cand, key=lambda r: r["decode_tps"]) if cand else None
tkstar = best_b["top_k"] if best_b else 20
mpstar = best_b["min_p"] if best_b else 0.05
print("STAGE B winner top_k =", tkstar, "min_p =", mpstar, "(%s)" % (best_b or {}).get("label"), flush=True)

# Stage C: top_p probe at the winner (0.95 already covered by the stage B winner row)
for tp in (0.90, 1.0):
    run_arm("C-topp%.2f" % tp, P100, vstar, tkstar, tp, mpstar)

print("SWEEP2_DONE", flush=True)
