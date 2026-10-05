#!/usr/bin/env python3
"""Strata full sweep v3: drafter gate x depth, suffix-draft, coupled-draft, sampler grids - all at
six depths (20k/60k/100k/150k/200k/250k), prompts sliced from /tmp/p250.txt.
Rows -> /tmp/strata-sweep3.jsonl ; stage markers -> stdout. Usage: strata-sweep3.py <stage> [val]
"""
import json
import random
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8080/v1/chat/completions"
TXT = open("/tmp/p250.txt").read()
RATIO = 900000.0 / 250566.0  # chars per token, measured on this file
DEPTHS = (20000, 60000, 100000, 150000, 200000, 250000)
LOG = "/tmp/strata-sweep3.jsonl"
WINNER_FILE = "/tmp/strata-sweep3.winner"
INSTR = ("[%s] Write a detailed technical explanation of lighthouse optics for an engineering audience. "
         "Aim for at least 400 words. ")


def prompt_for(depth_k):
    chars = min(int(depth_k * RATIO), len(TXT))
    return TXT[:chars]


def run_arm(stage, label, depth_k, spec_min_p, top_k, top_p, min_p, temp=0.5, seed=12345, maxtok=400):
    tag = "r%d" % random.randint(0, 10 ** 9)
    req = {"model": "qwen3.8-flash-next-iq3_s",
           "messages": [{"role": "user", "content": (INSTR % tag) + prompt_for(depth_k)}],
           "max_tokens": maxtok, "temperature": temp, "seed": seed,
           "top_k": top_k, "top_p": top_p, "min_p": min_p}
    if spec_min_p is not None:
        req["strata_tune"] = {"spec_min_p": spec_min_p}
    data = json.dumps(req).encode()
    t0 = time.time()
    row = {"stage": stage, "label": label, "depth_k": depth_k, "spec_min_p": spec_min_p,
           "top_k": top_k, "top_p": top_p, "min_p": min_p}
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE, data=data,
                                  headers={"Content-Type": "application/json"}), timeout=2400)
        d = json.loads(r.read())
        tt = d.get("timings", {})
        u = d.get("usage", {})
        row.update({"wall_s": round(time.time() - t0, 1), "ptok": u.get("prompt_tokens"),
                    "gen": u.get("completion_tokens"),
                    "prefill_tps": round(tt.get("prompt_per_second", 0), 1),
                    "decode_tps": round(tt.get("predicted_per_second", 0), 1),
                    "draft_n": tt.get("draft_n"), "draft_acc": tt.get("draft_n_accepted")})
    except Exception as e:
        row.update({"error": str(e)[:160], "wall_s": round(time.time() - t0, 1)})
    with open(LOG, "a") as f:
        f.write(json.dumps(row) + "\n")
    print(json.dumps(row), flush=True)
    return row


def winner_gate():
    try:
        return float(open(WINNER_FILE).read().strip())
    except Exception:
        return 0.85


def stageA():
    gates = (0.0, 0.5, 0.6, 0.85)
    rows = []
    for g in gates:
        for d in DEPTHS:
            rows.append(run_arm("A", "A-g%.2f-%dk" % (g, d // 1000), d, g, 20, 0.95, 0.0))
    ok = [r for r in rows if "decode_tps" in r]
    means = {}
    for g in gates:
        v = [r["decode_tps"] for r in ok if r["spec_min_p"] == g]
        means[g] = sum(v) / len(v) if v else -1
    win = max(means, key=means.get) if ok else 0.85
    open(WINNER_FILE, "w").write("%.2f" % win)
    print("STAGE A winner gate=%.2f means=%s" % (win, {k: round(v, 1) for k, v in means.items()}), flush=True)
    print("STAGE_A_DONE", flush=True)


def stage_depths(stage, label_prefix, spec_min_p, top_k, top_p, min_p):
    for d in DEPTHS:
        run_arm(stage, "%s-%dk" % (label_prefix, d // 1000), d, spec_min_p, top_k, top_p, min_p)


def stageB():
    g = winner_gate()
    rows = []
    for tk in (20, 30, 40, 50):
        for mp in (0.05, 0.08, 0.10):
            for d in DEPTHS:
                rows.append(run_arm("B", "B-tk%d-mp%02d-%dk" % (tk, round(mp * 100), d // 1000),
                                    d, g, tk, 0.95, mp))
    ok = [r for r in rows if "decode_tps" in r and r["depth_k"] == 100000]
    best = max(ok, key=lambda r: r["decode_tps"]) if ok else None
    tk = best["top_k"] if best else 30
    mp = best["min_p"] if best else 0.08
    print("STAGE B cell winner: tk=%d mp=%.2f" % (tk, mp), flush=True)
    for tp in (0.90, 1.00):
        for d in DEPTHS:
            run_arm("B", "B-tp%.2f-%dk" % (tp, d // 1000), d, g, tk, tp, mp)
    print("STAGE_B_DONE", flush=True)


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "stageA":
        stageA()
    elif stage == "stageS":
        v = sys.argv[2] if len(sys.argv) > 2 else "3"
        stage_depths("S", "S-sfx%s" % v, winner_gate(), 20, 0.95, 0.0)
        print("STAGE_S%s_DONE" % v, flush=True)
    elif stage == "stageC":
        v = sys.argv[2] if len(sys.argv) > 2 else "on"
        stage_depths("C", "C-cpl%s" % v, winner_gate(), 20, 0.95, 0.0)
        print("STAGE_C%s_DONE" % v, flush=True)
    elif stage == "stageB":
        stageB()


if __name__ == "__main__":
    main()
