#!/usr/bin/env python3
"""
Chart: the GSQ-RCO IQ3_S-mtp quant (12.12 GB, 3.5 bpw) on two RTX 3060s.

Every plotted value is read from data/csv/. Run:
    charts/.venv/bin/python scripts/make_chart_iq3s.py
Output: charts/qwen38-27b-iq3-s-2x3060.png
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "data", "csv")
OUT = os.path.join(HERE, "..", "charts", "qwen38-27b-iq3-s-2x3060.png")

BG = "#15130F"
INK = "#EDE5D8"
INK_DIM = "#9A9184"
ACCENT = "#D8A73C"
QUIET = "#6B6459"
RULE = "#332E27"


def pick(cands, fallback):
    have = {f.name for f in font_manager.fontManager.ttflist}
    for c in cands:
        if c in have:
            return c
    return fallback


DISPLAY = pick(["Franklin Gothic Demi Cond", "Franklin Gothic Medium Cond"], "DejaVu Sans")
SANS = pick(["Franklin Gothic Book", "Gill Sans MT", "Segoe UI"], "DejaVu Sans")
MONO = pick(["Consolas", "Cascadia Mono", "DejaVu Sans Mono"], "DejaVu Sans Mono")


def load(name):
    with open(os.path.join(CSV, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def f(x):
    return float(str(x).replace(",", "").replace("−", "-"))


# --------------------------------------------------------------------- data --
nmax = load("100k-stageA-nmax.csv")
nx = [int(r["arm"].split("-")[0].replace("mtp", "")) for r in nmax]
ny = [f(r["gen tok/s"]) for r in nmax]

gate = {r["arm"]: r for r in load("two-card-20k-verification-3-repeats.csv")}
g20_un = f(gate["n-max 2, p-min 0.00"]["mean"])
g20_g = f(gate["n-max 2, p-min 0.85"]["mean"])
n150 = load("two-card-mtp-nmax-150k.csv")
g150_un = f(next(r["gen tok/s"] for r in n150 if r["p-min"] == "0.00" and r["n-max"] == "2"))
g150_g = f(next(r["gen tok/s"] for r in n150 if r["p-min"] == "0.85" and r["n-max"] == "2"))

trims = load("100k-stageB-topk-minp.csv")
topk_groups = {}
for r in trims:
    topk_groups.setdefault(int(r["top_k"]), []).append(f(r["gen tok/s"]))
topks = sorted(topk_groups)
tk_max = [max(topk_groups[k]) for k in topks]
tk_min = [min(topk_groups[k]) for k in topks]
worst = min(trims, key=lambda r: f(r["gen tok/s"]))

rep1 = {}
for r in load("100k-split-mode-matrix.csv"):
    if r["arm"].endswith("rep1"):
        rep1[r["arm"].replace(" rep1", "")] = r
layouts = [
    ("2 cards\ntensor", "mode-tensor2-nmax7", ACCENT, "507"),
    ("2 cards\nlayer", "mode-layer2-nmax7", QUIET, "490"),
    ("3 cards\nlayer", "mode-layer3-nmax7", QUIET, "599"),
    ("3 cards\ntensor", "mode-tensor3-nmax7", QUIET, "302"),
]

# ------------------------------------------------------------------- canvas --
fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)
gs = fig.add_gridspec(3, 3, height_ratios=[1.35, 1.0, 0.30],
                      left=0.055, right=0.965, top=0.755, bottom=0.135,
                      hspace=0.85, wspace=0.30)


def dress(ax, title, sub):
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors=INK_DIM, labelsize=13, length=0)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontfamily(MONO)
    ax.set_title(title, color=INK, fontsize=19, fontfamily=DISPLAY, loc="left", pad=20)
    ax.annotate(sub, xy=(0, 1.025), xycoords="axes fraction", color=INK_DIM,
                fontsize=12.5, fontfamily=SANS, va="bottom")


# ----------------------------------------------------- 1. the n-max curve ----
ax1 = fig.add_subplot(gs[0, :])
dress(ax1, "The draft window has a sweet spot, and it is not the widest one",
      "MTP speculative decoding, 100,000-token prompt depth, tensor split 1,1, 2× RTX 3060 12 GB")
ax1.bar(nx, ny, width=0.62, color=[ACCENT if x == 7 else QUIET for x in nx], zorder=3)
for x, y in zip(nx, ny):
    ax1.annotate(f"{y:.2f}", (x, y), xytext=(0, 5), textcoords="offset points",
                 ha="center", color=ACCENT if x == 7 else INK_DIM, fontsize=13.5,
                 fontfamily=MONO)
ax1.set_xticks(nx)
ax1.set_xticklabels([f"n-max {x}" for x in nx])
ax1.set_yticks([])
ax1.set_ylim(0, 49)
ax1.set_xlim(0.4, 8.6)
ax1.annotate("+21% over the next best window", xy=(6.7, 44.4), xytext=(5.15, 46.4),
             color=ACCENT, fontsize=13.5, fontfamily=SANS)
ax1.annotate("", xy=(6.72, 44.4), xytext=(5.5, 46.0),
             arrowprops=dict(arrowstyle="-", color=ACCENT, lw=1.1, shrinkA=0, shrinkB=2))

# ------------------------------------------- 2. the gate flips with depth ----
ax2 = fig.add_subplot(gs[1, 0])
dress(ax2, "The confidence gate flips with depth",
      "MTP n-max 2  ·  gold: ungated  ·  grey: p-min 0.85")
xs, w = [0, 1], 0.34
vals_un = [g20_un, g150_un]
vals_g = [g20_g, g150_g]
ax2.bar([x - w / 2 for x in xs], vals_un, width=w, color=ACCENT, zorder=3)
ax2.bar([x + w / 2 for x in xs], vals_g, width=w, color=QUIET, zorder=3)
for x, v in zip([x - w / 2 for x in xs], vals_un):
    ax2.annotate(f"{v:.2f}", (x, v), xytext=(0, 4), textcoords="offset points",
                 ha="center", color=ACCENT, fontsize=12, fontfamily=MONO)
for x, v in zip([x + w / 2 for x in xs], vals_g):
    ax2.annotate(f"{v:.2f}", (x, v), xytext=(0, 4), textcoords="offset points",
                 ha="center", color=INK_DIM, fontsize=12, fontfamily=MONO)
ax2.set_xticks(xs)
ax2.set_xticklabels(["20k depth", "150k depth"])
ax2.set_yticks([])
ax2.set_ylim(0, 62)
ax2.annotate("1.72× faster", xy=(0, 53.5), ha="center", color=ACCENT,
             fontsize=12.5, fontfamily=SANS)
ax2.annotate("18% slower", xy=(1, 17.0), ha="center", color=ACCENT,
             fontsize=12.5, fontfamily=SANS)

# ------------------------------------------------------ 3. the top_k trap ----
ax3 = fig.add_subplot(gs[1, 1])
dress(ax3, "top_k runs backwards", "decode at 100k depth  ·  bar: best min_p arm  ·  line: its spread")
xs = list(range(len(topks)))
ax3.bar(xs, tk_max, width=0.5, color=[ACCENT if k == 20 else QUIET for k in topks], zorder=3)
for x, hi, lo in zip(xs, tk_max, tk_min):
    ax3.plot([x, x], [lo, hi], color=INK_DIM, lw=1.4, zorder=4)
    ax3.plot([x - 0.11, x + 0.11], [lo, lo], color=INK_DIM, lw=1.4, zorder=4)
    ax3.annotate(f"{hi:.1f}", (x, hi), xytext=(0, 5), textcoords="offset points",
                 ha="center", color=ACCENT if topks[x] == 20 else INK_DIM,
                 fontsize=12.5, fontfamily=MONO)
ax3.set_xticks(xs)
ax3.set_xticklabels([f"top_k {k}" for k in topks])
ax3.set_yticks([])
ax3.set_ylim(0, 62)
ax3.annotate("35%", xy=(2.52, 20.0), ha="center", color=ACCENT, fontsize=13.5, fontfamily=SANS)

# ------------------------------------------------- 4. two cards or three -----
ax4 = fig.add_subplot(gs[1, 2])
dress(ax4, "Two cards beat three for decode",
      "100k depth  ·  prefill: 507 / 490 / 599 / 302")
xs = list(range(len(layouts)))
lvals = [f(rep1[k]["gen tok/s"]) for _, k, _, _ in layouts]
ax4.bar(xs, lvals, width=0.5, color=[c for _, _, c, _ in layouts], zorder=3)
for x, v, (_, _, c, _) in zip(xs, lvals, layouts):
    ax4.annotate(f"{v:.2f}", (x, v), xytext=(0, 4), textcoords="offset points",
                 ha="center", color=ACCENT if c == ACCENT else INK_DIM,
                 fontsize=12.5, fontfamily=MONO)
ax4.set_xticks(xs)
ax4.set_xticklabels([lbl for lbl, _, _, _ in layouts], fontsize=11.5, linespacing=1.7)
ax4.set_yticks([])
ax4.set_ylim(0, 58)

# ------------------------------------------------------------------- header --
fig.text(0.055, 0.965, "Qwen3.8-27B  GSQ-RCO  IQ3_S-mtp", color=INK,
         fontsize=40, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.888, "12.12 GB, 3.5 bpw, two RTX 3060s — 43.07 tok/s decode at 100k context, "
                       "1.7× faster than any three-card layout",
         color=ACCENT, fontsize=19, fontfamily=SANS, va="top")
fig.text(0.965, 0.968, "llama.cpp b11041  ·  CUDA 13.3  ·  sm_86", color=INK_DIM,
         fontsize=13.5, fontfamily=MONO, ha="right", va="top")
fig.text(0.965, 0.939, "this is the file serving today  ·  Sep 2026", color=INK_DIM,
         fontsize=13.5, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------------- footer --
fig.add_artist(plt.Line2D([0.055, 0.965], [0.112, 0.112], color=RULE, lw=1))
fig.text(0.055, 0.085, "The DFlash2 drafter also loses here — 23.27 tok/s at 100k depth on three cards against MTP's 24.99 — "
                       "so the quant ships with the built-in head.",
         color=INK_DIM, fontsize=12.5, fontfamily=SANS, va="bottom")
fig.text(0.055, 0.055, "Peak seen live: 81 tok/s decode on a short coding task (Eamon's own measurement) — a burst. "
                       "Production: 511 tok/s cold prefill of a 103,726-token prompt, 27.7 tok/s sustained.",
         color=ACCENT, fontsize=12.5, fontfamily=SANS, va="bottom")
fig.text(0.965, 0.025, "raw data and full write-ups: github.com/EamonMcKiernan05/Local-LLM-Testing",
         color=INK_DIM, fontsize=12.5, fontfamily=MONO, ha="right", va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
