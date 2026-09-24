#!/usr/bin/env python3
"""One measurement against a llama-server, with NO sampler overrides.

Unlike dflash_test_big.py this request sets only n_predict / cache_prompt /
temperature / seed -- it does not send top_k, top_p, min_p or presence_penalty.
Those therefore come from the SERVER's own configuration, which is what the
n-max and trim sweeps are varying. Sending them per-request would override the
server and make every arm identical.

Builds one deterministic ~N-token prompt (identical across configs so runs are
comparable), then measures ONE non-streaming /completion with cache_prompt=false.
Prints one JSON line.
"""
import argparse, hashlib, json, random, urllib.request

WORDS = ("amber basalt cedar delta ember fathom granite harbour ingot juniper kelp "
         "lantern marble nimbus obsidian pier quartz rookery saffron tundra umbra "
         "vellum willow xenon yarrow zephyr anvil bramble cinder dune estuary "
         "fjord gantry hollow inlet jetty kiln lagoon mire necropolis ore").split()


def post(port, path, obj, timeout=3600):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 data=json.dumps(obj).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8086)
    p.add_argument("--tokens", type=int, default=100000)
    p.add_argument("--n-predict", type=int, default=256)
    p.add_argument("--temp", type=float, default=0.5)
    p.add_argument("--seed", type=int, default=12345)
    p.add_argument("--ignore-eos", action="store_true")
    p.add_argument("--label", required=True)
    a = p.parse_args()

    random.seed(20260918)  # SAME prompt for every config
    text = "\n".join(
        f"Sentence {i:06d}: " + " ".join(random.choice(WORDS) for _ in range(12)) + "."
        for i in range(9000))
    count = len(post(a.port, "/tokenize", {"content": text})["tokens"])
    for _ in range(8):
        if abs(count - a.tokens) <= a.tokens * 0.01:
            break
        text = text[:max(1, int(len(text) * (a.tokens / count) * 0.997))]
        count = len(post(a.port, "/tokenize", {"content": text})["tokens"])

    params = {"n_predict": a.n_predict, "cache_prompt": False,
              "temperature": a.temp, "seed": a.seed}
    if a.ignore_eos:
        params["ignore_eos"] = True

    post(a.port, "/completion", {"prompt": "Warm up.", "n_predict": 16,
                                 "cache_prompt": False, "seed": a.seed})

    r = post(a.port, "/completion", dict(params, prompt=text))
    t = r["timings"]
    out = r.get("content", "")
    print(json.dumps({
        "label": a.label,
        "temp": a.temp,
        "prompt_tokens": t["prompt_n"],
        "prefill_tok_s": round(t["prompt_per_second"], 2),
        "prefill_ms": round(t["prompt_ms"]),
        "gen_tokens": t["predicted_n"],
        "gen_tok_s": round(t["predicted_per_second"], 2),
        "gen_ms": round(t["predicted_ms"]),
        "output_sha256": hashlib.sha256(out.encode()).hexdigest()[:16],
    }))


if __name__ == "__main__":
    main()
