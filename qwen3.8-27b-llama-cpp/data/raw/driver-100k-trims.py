#!/usr/bin/env python3
"""Two-card (CUDA0+CUDA1, tensor split) sweep at 100k depth — MTP n-max, then sampler trims.

Stage A  `nmax`  : MTP --spec-draft-n-max 1..8, --spec-draft-p-min 0.00 (ungated),
                   NO top_k / top_p / min_p passed to the server, so llama.cpp's
                   stock sampler defaults apply (top_k 40, top_p 0.95, min_p 0.05).
Stage B  `trims` : at the winning n-max from stage A, every combination of
                   top_k {20,30,40,50} x min_p {0.05,0.08,0.1}. top_p stays unset.

Fixed: temp 0.5, -b 2048 -ub 256, tensor split 1,1, q8_0 KV, ctx 131,072,
100,000-token prompt, 256 generated, seed 12345, on CUDA0+CUDA1 only.

The harness used here (depth_test.py) sends NO sampler parameters per request, so
the server's own configuration decides them — otherwise every arm would be identical.

    nohup setsid python3 ~/two-card-nmax-trims-sweep.py --stage all --nohup > ~/trims.out 2>&1 &
    python3 ~/two-card-nmax-trims-sweep.py --report
"""
import argparse, itertools, json, os, re, signal, subprocess, sys, threading, time, urllib.request

HOME = "/home/eamon"
BIN = f"{HOME}/llama.cpp/build/bin/llama-server"
HARNESS = f"{HOME}/depth_test.py"
TARGET = f"{HOME}/models/Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf"
DRAFTER = f"{HOME}/models/Qwen3.8-27B-DFlash2-Q2_K_S-MIX.gguf"
TARGET_BYTES = 12120016960
PORT = 8086
DEVICES = "CUDA0,CUDA1"
CTX = {100000: 131072}
RESULT = f"{HOME}/two-card-trims-results.jsonl"
LOGDIR = f"{HOME}/two-card-trims-logs"
DEPTH = 100000
TOP_KS = [20, 30, 40, 50]
MIN_PS = [0.05, 0.08, 0.1]


def nmax_cards():
    return [{"label": f"mtp{n}-untrimmed", "split": "tensor", "ts": "1,1",
             "kv": "q8_0", "spec": ("mtp", n, 0.00), "top_k": None, "min_p": None}
            for n in range(1, 9)]


def trim_cards(n_max):
    out = []
    for tk, mp in itertools.product(TOP_KS, MIN_PS):
        out.append({"label": f"mtp{n_max}-topk{tk}-minp{str(mp).replace('.', '')}",
                    "split": "tensor", "ts": "1,1", "kv": "q8_0",
                    "spec": ("mtp", n_max, 0.00), "top_k": tk, "min_p": mp})
    return out


def get(path, timeout=15):
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}", timeout=timeout) as r:
        return r.read().decode()


def vram():
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=30)
    return [int(x.strip()) for x in r.stdout.strip().splitlines() if x.strip()]


def live_service_active():
    r = subprocess.run(["systemctl", "is-active", "llama-server"], capture_output=True, text=True, timeout=30)
    return r.stdout.strip() == "active"


def interlock(allow):
    if live_service_active():
        return ("llama-server.service is ACTIVE — the cards only hold one model. "
                "Stop it first: sudo systemctl stop llama-server")
    used = vram()
    if any(u > allow for u in used):
        return f"GPUs still hold VRAM {used} MiB — something else has the cards."
    return None


def preflight():
    bad = []
    if not os.path.exists(TARGET):
        bad.append("target GGUF missing: " + TARGET)
    elif os.path.getsize(TARGET) != TARGET_BYTES:
        bad.append(f"target size {os.path.getsize(TARGET)} != {TARGET_BYTES}")
    if not os.path.exists(HARNESS):
        bad.append("harness missing: " + HARNESS)
    return bad


def metrics():
    out = {}
    try:
        text = get("/metrics")
    except Exception:
        return out
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        m = re.match(r'llamacpp:spec_decode_num_accepted_tokens_per_pos_total\{position="(\d+)"\}\s+([\d.e+]+)', line)
        if m:
            out.setdefault("per_pos", {})[int(m.group(1))] = float(m.group(2))
            continue
        m = re.match(r"llamacpp:(spec_decode_num_drafts_total|spec_decode_num_draft_tokens_total|spec_decode_num_accepted_tokens_total)\s+([\d.e+]+)", line)
        if m:
            out[m.group(1)] = float(m.group(2))
    return out


class Poller(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.stop_flag, self.peak = False, [0, 0, 0]

    def run(self):
        while not self.stop_flag:
            try:
                u = vram()
                for i, v in enumerate(u[:3]):
                    self.peak[i] = max(self.peak[i], v)
            except Exception:
                pass
            time.sleep(4)


def wait_health(timeout=180):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if '"ok"' in get("/health", timeout=4):
                return True
        except Exception:
            pass
        time.sleep(3)
    return False


def wait_vram_free(allow=2000, timeout=150):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if all(u <= allow for u in vram()):
            return True
        time.sleep(5)
    return False


def build_argv(card, temp):
    args = ["--parallel", "1", "-m", TARGET, "--device", card.get("devices", DEVICES), "--fit", "off",
            "--ctx-size", str(CTX[DEPTH]), "--flash-attn", "on",
            "--cache-type-k", card["kv"], "--cache-type-v", card["kv"],
            "-ub", "256", "-b", "2048", "--jinja", "--reasoning-preserve", "--metrics",
            "--temp", str(temp), "--split-mode", card["split"], "--tensor-split", card["ts"]]
    kind, n_max, p_min = card["spec"]
    if kind == "dflash":
        args += ["-md", DRAFTER, "--spec-type", "draft-dflash"]
    else:
        args += ["--spec-type", "draft-mtp"]
    if card.get("devd"):
        args += ["--spec-draft-device", card["devd"]]
    args += ["--spec-draft-n-max", str(n_max), "--spec-draft-p-min", f"{p_min:.2f}"]
    if card["top_k"] is not None:
        args += ["--top-k", str(card["top_k"])]
    if card["min_p"] is not None:
        args += ["--min-p", str(card["min_p"])]
    return [BIN] + args + ["--host", "127.0.0.1", "--port", str(PORT)]


def run_one(card, temp, n_predict, logdir):
    tag = card["label"]
    log_path = f"{logdir}/{tag}-100k.log"
    rec = {"label": tag, "depth": DEPTH, "ctx": CTX[DEPTH], "kv": card["kv"], "split": card["split"],
           "ts": card["ts"], "spec": list(card["spec"]), "top_k": card["top_k"],
           "min_p": card["min_p"], "temp": temp, "b": 2048, "ub": 256,
           "n_predict": n_predict, "log": log_path, "target": TARGET}
    print(f"=== {tag}", flush=True)
    with open(log_path, "w") as log:
        p = subprocess.Popen(build_argv(card, temp), stdout=log, stderr=subprocess.STDOUT,
                             start_new_session=True)
    poller = None
    try:
        if not wait_health():
            rec["error"] = "server never became healthy | " + open(log_path, errors="ignore").read()[-400:].replace("\n", " ")
            return rec
        rec["vram_after_load_mib"] = vram()
        logtext = open(log_path, errors="ignore").read()
        marks = [m for m in ("cudaMalloc failed", "failed to allocate compute buffers",
                             "retrying without pipeline parallelism", "GGML_ASSERT", "ggml_abort")
                 if m in logtext]
        if marks:
            rec["load_warnings"] = marks
        try:
            props = json.loads(get("/props", timeout=20))
            rec["n_ctx"] = props.get("default_generation_settings", {}).get("n_ctx")
        except Exception:
            pass
        poller = Poller(); poller.start()
        t0 = time.time()
        cmd = ["python3", HARNESS, "--port", str(PORT), "--tokens", str(DEPTH),
               "--n-predict", str(n_predict), "--temp", str(temp), "--seed", "12345",
               "--label", tag]
        if card.get("ignore_eos"):
            cmd.append("--ignore-eos")
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10800)
        rec["wall_s"] = round(time.time() - t0, 1)
        for line in out.stdout.strip().splitlines():
            try:
                rec.update(json.loads(line)); break
            except Exception:
                continue
        if "gen_tok_s" not in rec:
            rec["error"] = "no timing line: " + (out.stderr or out.stdout)[-300:]
        m = metrics()
        if m:
            d = m.get("spec_decode_num_drafts_total", 0)
            a = m.get("spec_decode_num_accepted_tokens_total", 0)
            pr = m.get("spec_decode_num_draft_tokens_total", 0)
            rec["rounds"], rec["draft_tokens"], rec["accepted_tokens"] = d, pr, a
            if d:
                rec["acceptance_length"] = round(1 + a / d, 3)
                rec["proposed_per_round"] = round(pr / d, 3)
            if pr:
                rec["token_accept_rate"] = round(a / pr, 4)
    except Exception as e:
        rec["error"] = str(e)[:250]
    finally:
        if poller:
            poller.stop_flag = True
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            pass
        time.sleep(6)
        rec["peak_vram_mib"] = poller.peak if poller else None
        rec["vram_freed"] = wait_vram_free()
        time.sleep(2)
    return rec


def load_done(path):
    done = set()
    if os.path.exists(path):
        for line in open(path):
            try:
                r = json.loads(line)
                if "gen_tok_s" in r:
                    done.add(r["label"])
            except Exception:
                pass
    return done


def append(rec, path):
    rec["timestamp"] = round(time.time(), 1)
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")


def best(cards, results_path, key="gen_tok_s"):
    rows = [json.loads(l) for l in open(results_path)] if os.path.exists(results_path) else []
    labels = {c["label"] for c in cards}
    ok = [r for r in rows if r.get("label") in labels and key in r]
    if not ok:
        return None
    return max(ok, key=lambda r: r[key])


def report(path):
    if not os.path.exists(path):
        print("no results yet")
        return
    rows = [json.loads(l) for l in open(path) if l.strip()]
    print("\n| config | top_k | min_p | p-min | prefill tok/s | gen tok/s | AL | accept | prop/round | peak VRAM (0/1) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: (r.get("top_k") or 0, r.get("min_p") or 0, r["label"])):
        if "gen_tok_s" not in r:
            print(f"| {r['label']} | | | | FAILED | | | | | {str(r.get('error'))[:60]} |")
            continue
        print("| {l} | {tk} | {mp} | {pm} | {pf} | {g} | {al} | {ac} | {pr} | {pv} |".format(
            l=r["label"], tk=r.get("top_k") or "unset", mp=r.get("min_p") or "unset",
            pm=r["spec"][2], pf=r.get("prefill_tok_s"), g=r.get("gen_tok_s"),
            al=r.get("acceptance_length", "-"), ac=r.get("token_accept_rate", "-"),
            pr=r.get("proposed_per_round", "-"), pv=r.get("peak_vram_mib")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all", choices=["nmax", "trims", "all"])
    ap.add_argument("--temp", type=float, default=0.5)
    ap.add_argument("--n-predict", type=int, default=256)
    ap.add_argument("--result", default=RESULT)
    ap.add_argument("--logdir", default=LOGDIR)
    ap.add_argument("--allow-vram-mib", type=int, default=1200)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--only-labels", default="")
    a = ap.parse_args()

    if a.report:
        report(a.result)
        return

    bad = preflight()
    if bad:
        print("PREFLIGHT FAILED:\n  - " + "\n  - ".join(bad), flush=True)
        sys.exit(2)
    why = interlock(a.allow_vram_mib)
    if why:
        print("REFUSING TO START: " + why, flush=True)
        sys.exit(2)

    os.makedirs(a.logdir, exist_ok=True)
    done = set() if a.no_resume else load_done(a.result)
    only = [x for x in a.only_labels.split(",") if x]

    print(f"sweep start {time.strftime('%Y-%m-%d %H:%M:%S')} stage={a.stage} depth={DEPTH} "
          f"temp={a.temp} b=2048 ub=256 tensor {DEVICES}", flush=True)

    nm = nmax_cards()
    if a.stage in ("nmax", "all"):
        print(f"stage A: {len(nm)} n-max arms, spec p-min 0.00, no top_k/top_p/min_p passed "
              f"(llama.cpp stock defaults apply)", flush=True)
        for card in nm:
            if only and card["label"] not in only:
                continue
            if card["label"] in done:
                print(f"skip (done): {card['label']}", flush=True)
                continue
            rec = run_one(card, a.temp, a.n_predict, a.logdir)
            append(rec, a.result)
            print(json.dumps({k: v for k, v in rec.items() if k != "load_warnings"}), flush=True)

    if a.stage in ("trims", "all"):
        win = best(nm, a.result, "gen_tok_s")
        if not win:
            print("no completed n-max rows — run --stage nmax first", flush=True)
            sys.exit(2)
        n_max = win["spec"][1]
        print(f"stage B base: n-max {n_max} (fastest at {DEPTH:,}: {win['gen_tok_s']} tok/s gen, "
              f"{win['prefill_tok_s']} tok/s prefill); top_k x min_p = "
              f"{len(TOP_KS)}x{len(MIN_PS)} = {len(TOP_KS) * len(MIN_PS)} arms", flush=True)
        for card in trim_cards(n_max):
            if only and card["label"] not in only:
                continue
            if card["label"] in done:
                print(f"skip (done): {card['label']}", flush=True)
                continue
            rec = run_one(card, a.temp, a.n_predict, a.logdir)
            append(rec, a.result)
            print(json.dumps({k: v for k, v in rec.items() if k != "load_warnings"}), flush=True)

    print("SWEEP DONE", flush=True)
    report(a.result)


if __name__ == "__main__":
    main()
