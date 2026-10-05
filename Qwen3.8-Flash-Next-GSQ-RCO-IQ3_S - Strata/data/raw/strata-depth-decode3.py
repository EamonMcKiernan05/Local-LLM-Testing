#!/usr/bin/env python3
"""Depth benchmark v3 — EXACT token slicing via the pack tokenizer (strata_tokenizer module).
Six unique documents, one per depth: 20k/60k/100k/150k/200k/250k prompt tokens (instruction adds ~40).
Stock config (gate 0.50), temp 0.5 seed 12345, 400 tokens generated per run.
Run with the Strata venv: /home/eamon/Strata/.venv/bin/python
Rows -> /tmp/depth-decode3.jsonl
"""
import json
import random
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, "/home/eamon/Strata/tools")
import strata_tokenizer as ST

BASE = "http://127.0.0.1:8080/v1/chat/completions"
DOCS = "/home/eamon/depth-docs"
LOG = "/tmp/depth-decode3.jsonl"
GGUF = ("/mnt/models/Qwen3.8-Flash-Next/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S ISTA-DASLab/"
        "Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf")
PACK = "/mnt/models/Strata-data/packs/iq3_s/tokenizer"
INSTR = ("[%s] Write a detailed technical explanation of lighthouse optics for an engineering audience. "
         "Aim for at least 400 words. ")
ARMS = [(20000, "frankenstein"), (60000, "sherlock"), (100000, "pride"),
        (150000, "tale2cities"), (200000, "greatexp"), (250000, "mobydick")]


def build_tok():
    try:
        return ST.Tokenizer.from_gguf(GGUF)
    except Exception as e:
        print("from_gguf failed (%s); using pack files" % e, flush=True)
        vocab = json.loads(open(PACK + "/vocab.json").read())
        tokens = [None] * len(vocab)
        for t, i in vocab.items():
            tokens[i] = t
        merges = open(PACK + "/merges.txt").read().split("\n")
        types = json.loads(open(PACK + "/token_type.json").read())
        return ST.Tokenizer(tokens, merges, types)


tok = build_tok()


def book_text(book):
    raw = open("%s/%s.txt" % (DOCS, book)).read()
    marker = "*** START OF THE PROJECT GUTENBERG"
    i = raw.find(marker)
    if i >= 0:
        j = raw.find("\n", i)
        raw = raw[j + 1:]
    return raw


def slice_exact(book, target):
    ids = tok.encode(book_text(book))
    n = min(target, len(ids))
    out = tok.decode(ids[:n])
    for _ in range(12):
        c = len(tok.encode(out))
        if c == target:
            break
        n += 1 if c < target else -1
        out = tok.decode(ids[:n])
    return out, len(tok.encode(out))


def req(text, maxtok, tag):
    payload = {"model": "qwen3.8-flash-next-iq3_s",
               "messages": [{"role": "user", "content": (INSTR % tag) + text}],
               "max_tokens": maxtok, "temperature": 0.5, "seed": 12345,
               "top_k": 20, "top_p": 0.95, "min_p": 0.0}
    r = urllib.request.urlopen(urllib.request.Request(BASE, data=json.dumps(payload).encode(),
                              headers={"Content-Type": "application/json"}), timeout=2400)
    return json.loads(r.read())


def vram():
    out = subprocess.run(["nvidia-smi", "--query-gpu=index,memory.used,memory.total,temperature.gpu",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()
    return [dict(zip(("idx", "used_mib", "total_mib", "temp_c"), [s.strip() for s in row.split(",")]))
            for row in out.splitlines()]


def main():
    import os
    if os.path.exists(LOG):
        os.remove(LOG)
    for target, book in ARMS:
        text, check = slice_exact(book, target)
        tag = "r%d" % random.randint(0, 10**9)
        t0 = time.time()
        row = {"kind": "depth", "depth_k_target": target, "book": book,
               "doc_tokens": check, "doc_chars": len(text)}
        try:
            d = req(text, 400, tag)
            tt = d.get("timings", {})
            u = d.get("usage", {})
            row.update({"ptok": u.get("prompt_tokens"), "gen": u.get("completion_tokens"),
                        "prefill_tps": round(tt.get("prompt_per_second", 0), 1),
                        "decode_tps": round(tt.get("predicted_per_second", 0), 1),
                        "draft_n": tt.get("draft_n"), "draft_acc": tt.get("draft_n_accepted")})
        except Exception as e:
            row["error"] = str(e)[:160]
        row["wall_s"] = round(time.time() - t0, 1)
        row["vram_after"] = vram()
        with open(LOG, "a") as f:
            f.write(json.dumps(row) + "\n")
        print(json.dumps(row), flush=True)
    print("DEPTH_DECODE3_DONE", flush=True)


if __name__ == "__main__":
    main()
