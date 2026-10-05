#!/usr/bin/env python3
"""Hero data for the V100 graphic: prefill-by-depth points + one long streaming generation.
All prompts are slices of /tmp/p250.txt (same text family). Output: /tmp/strata-hero.jsonl
"""
import json
import time
import urllib.request

BASE = "http://127.0.0.1:8080/v1/chat/completions"
TXT = open("/tmp/p250.txt").read()
RATIO = len(TXT) / 250592.0  # chars per token, measured on this exact file


def post(body, stream=False, timeout=2400):
    req = urllib.request.Request(BASE, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    r = urllib.request.urlopen(req, timeout=timeout)
    if not stream:
        d = json.loads(r.read())
        d["_t0"] = t0
        d["_t_end"] = time.time()
        return d
    t_first = None
    events = []
    for raw in r:
        line = raw.decode("utf-8", "replace").strip()
        if not line.startswith("data:"):
            continue
        p = line[5:].strip()
        if p == "[DONE]":
            break
        try:
            d = json.loads(p)
        except Exception:
            continue
        delta = d.get("choices", [{}])[0].get("delta", {})
        if delta.get("content") or delta.get("reasoning_content"):
            now = time.time()
            if t_first is None:
                t_first = now
            events.append(now)
    return {"_t0": t0, "_t_first": t_first, "_t_end": time.time(), "_events": events}


def log(row):
    with open("/tmp/strata-hero.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")
    print(json.dumps({k: v for k, v in row.items() if k != "_events"}), flush=True)


print("HERO START", flush=True)
tag = str(int(time.time()))

# 1) prefill-by-depth points
for depth in (8000, 20000, 50000, 100000, 150000):
    chars = int(depth * RATIO)
    body = {"model": "qwen3.8-flash-next-iq3_s",
            "messages": [{"role": "user",
                          "content": "[%s d%d] Reply with exactly ACK. " % (tag, depth) + TXT[:chars]}],
            "max_tokens": 16, "temperature": 0}
    d = post(body)
    t = d.get("timings", {})
    u = d.get("usage", {})
    log({"kind": "depth", "depth": depth, "ptok": u.get("prompt_tokens"),
         "prefill_tps": t.get("prompt_per_second"), "decode_tps": t.get("predicted_per_second"),
         "gen": u.get("completion_tokens"), "wall": round(d["_t_end"] - d["_t0"], 1)})

# 2) hero run: 250k prompt + long streaming generation
body = {"model": "qwen3.8-flash-next-iq3_s",
        "messages": [{"role": "user",
                      "content": "[%s hero] Here is a long reference document. After reading it, write a detailed "
                                 "technical essay of at least 2000 words on how a lighthouse works: the optics, "
                                 "the rotation mechanism, the power source, and fog signals. Keep going until the "
                                 "essay is complete." % tag + TXT}],
        "max_tokens": 6000, "temperature": 0, "stream": True}
d = post(body, stream=True)
ev = d["_events"]
row = {"kind": "hero", "ptok": 250592, "gen": len(ev),
       "ingest_s": round((d["_t_first"] or d["_t0"]) - d["_t0"], 2) if d["_t_first"] else None,
       "decode_s": round(d["_t_end"] - (d["_t_first"] or d["_t_end"]), 2),
       "events_epoch": [round(x - d["_t0"], 4) for x in ev]}
log(row)
print("HERO DONE", flush=True)
