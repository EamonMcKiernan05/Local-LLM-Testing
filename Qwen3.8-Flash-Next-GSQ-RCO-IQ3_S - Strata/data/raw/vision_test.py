#!/usr/bin/env python3
"""Send the vision test image to the local Strata API and print the answer + timings."""
import base64, json, sys, time, urllib.request

IMG = sys.argv[1] if len(sys.argv) > 1 else "/tmp/vision-test.png"
URL = "http://127.0.0.1:8080/v1/chat/completions"
img = base64.b64encode(open(IMG, "rb").read()).decode()
body = {
    "model": "qwen3.8-flash-next-iq3_s",
    "messages": [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}},
        {"type": "text", "text": "Read the text in this image exactly. Then name each shape and its colour. One short paragraph."},
    ]}],
    "max_tokens": 1536,
    "temperature": 0.2,
}
req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
t = time.time()
with urllib.request.urlopen(req, timeout=600) as r:
    d = json.load(r)
wall = time.time() - t
m = d["choices"][0]["message"]
print(json.dumps({
    "wall_s": round(wall, 1),
    "finish": d["choices"][0].get("finish_reason"),
    "content": m.get("content"),
    "reasoning_head": (m.get("reasoning_content") or "")[:300],
    "timings": d.get("timings"),
}, indent=1))
