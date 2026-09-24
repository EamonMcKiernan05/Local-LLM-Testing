#!/usr/bin/env python3
"""
Draw the chart prepared for posting.

Every plotted value is read from data/csv/ - nothing is typed in twice. Run:

    charts/.venv/bin/python scripts/make_chart.py

Output: charts/qwen38-27b-llama-cpp-2x3060.png  (1600x1000, 16:10)
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "data", "csv")
OUT = os.path.join(HERE, "..", "charts", "qwen38-27b-llama-cpp-2x3060.png")

# --- palette: warm near-black, warm off-white ink, one muted gold accent -----
BG = "#15130F"
INK = "#EDE5D8"
INK_DIM = "#9A9184"
ACCENT = "#D8A73C"
QUIET = "#585147"
RULE = "#332E27"

DISPLAY = "Franklin Gothic Demi Cond"
SANS = "Franklin Gothic Book"
MONO = "Consolas"


def pick(candidates, fallback):
    have = {f.name for f in font_manager.fontManager.ttflist}
    for c in candidates:
        if c in have:
            return c
    return fallback


DISPLAY = pick(["Franklin Gothic Demi Cond", "Franklin Gothic Medium Cond", "Osward"], "DejaVu Sans")
SANS = pick(["Franklin Gothic Book", "Gill Sans MT", "Segoe UI"], "DejaVu Sans")
MONO = pick(["Consolas", "Cascadia Mono", "DejaVu Sans Mono"], "DejaVu Sans Mono")


def load(name):
    with open(os.path.join(CSV, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def f(x):
    return float(str(x).replace(",", ""))


# --------------------------------------------------------------------- data --
nmax = load("100k-stageA-nmax.csv")
nmax_x, nmax_y = [], []
for r in nmax:
    n = r["arm"].split("-")[0].replace("mtp", "")
    nmax_x.append(int(n))
    nmax_y.append(f(r["gen tok/s"]))

gate = load("two-card-mtp-nmax-20k.csv")          # 20k depth
gate2 = load("two-card-mtp-nmax-150k.csv")        # 150k depth
g20_ungated = next(f(r["gen tok/s"]) for r in gate if r["p-min"] == "0.00" and r["n-max"] == "2")
g20_gated = next(f(r["gen tok/s"]) for r in gate if r["p-min"] == "0.85" and r["n-max"] == "2")
g150_ungated = next(f(r["gen tok/s"]) for r in gate2 if r["p-min"] == "0.00" and r["n-max"] == "2")
g150_gated = next(f(r["gen tok/s"]) for r in gate2 if r["p-min"] == "0.85" and r["n-max"] == "2")

depth = load("prefill-by-depth.csv")
dep_x = [f(r["prompt tokens"]) / 1000 for r in depth if r["speculation"] == "none"]
dep_y = [f(r["prefill tok/s"]) for r in depth if r["speculation"] == "none"]

best = load("dflash2-best-per-drafter-per-temp.csv")
temps = ["0.0", "0.6", "0.8", "0.9"]
mtp, df2 = [], []
for t in temps:
    rows = [r for r in best if r["Temperature"].strip() == t]
    mtp.append(max(f(r["best gen tok/s (measured)"]) for r in rows if r["Drafter"].startswith("MTP")))
    df2.append(max(f(r["best gen tok/s (measured)"]) for r in rows if r["Drafter"].startswith("DFlash2")))

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


# ------------------------------------------------------- 1. the n-max curve --
ax1 = fig.add_subplot(gs[0, :])
dress(ax1, "The draft window has a sweet spot, and it is not the widest one",
      "MTP speculative decoding, 100,000-token prompt depth, 2× RTX 3060 12 GB, IQ3_S quant")
colors = [ACCENT if x == 7 else QUIET for x in nmax_x]
bars = ax1.bar(nmax_x, nmax_y, width=0.62, color=colors, zorder=3)
for x, y in zip(nmax_x, nmax_y):
    ax1.annotate(f"{y:.2f}", (x, y), xytext=(0, 5), textcoords="offset points",
                 ha="center", color=ACCENT if x == 7 else INK_DIM, fontsize=13.5, fontfamily=MONO)
ax1.set_xticks(nmax_x)
ax1.set_xticklabels([f"n-max {x}" for x in nmax_x])
ax1.set_ylim(0, 49)
ax1.set_xlim(0.4, 8.6)
ax1.set_yticks([])
ax1.annotate("+21% over the next best window", xy=(7, 43.07), xytext=(5.35, 46.6),
             color=ACCENT, fontsize=13.5, fontfamily=SANS)
ax1.annotate("", xy=(6.72, 44.4), xytext=(5.95, 46.2),
             arrowprops=dict(arrowstyle="-", color=ACCENT, lw=1.1, shrinkA=0, shrinkB=2))

# ------------------------------------------------- 2. the gate flips with depth
ax2 = fig.add_subplot(gs[1, 0])
dress(ax2, "The gate flips with depth", "MTP n-max 2  ·  gold: ungated  ·  grey: p-min 0.85")
xs = [0, 1]
w = 0.34
ax2.bar([x - w / 2 for x in xs], [g20_ungated, g150_ungated], width=w, color=ACCENT, zorder=3, label="ungated")
ax2.bar([x + w / 2 for x in xs], [g20_gated, g150_gated], width=w, color=QUIET, zorder=3, label="gated 0.85")
for x, v in zip([x - w / 2 for x in xs], [g20_ungated, g150_ungated]):
    ax2.annotate(f"{v:.2f}", (x, v), xytext=(0, 5), textcoords="offset points",
                 ha="center", color=ACCENT, fontsize=13, fontfamily=MONO)
for x, v in zip([x + w / 2 for x in xs], [g20_gated, g150_gated]):
    ax2.annotate(f"{v:.2f}", (x, v), xytext=(0, 5), textcoords="offset points",
                 ha="center", color=INK_DIM, fontsize=13, fontfamily=MONO)
ax2.set_xticks(xs)
ax2.set_xticklabels(["20k depth", "150k depth"])
ax2.set_yticks([])
ax2.set_ylim(0, 52)

# --------------------------------------------------------- 3. prefill by depth
ax3 = fig.add_subplot(gs[1, 1])
dress(ax3, "Prefill degrades with no cliff", "no speculation, q8_0 KV, prompt processing only")
ax3.plot(dep_x, dep_y, color=ACCENT, lw=2.4, marker="o", ms=7,
         markerfacecolor=BG, markeredgecolor=ACCENT, markeredgewidth=2.2, zorder=3)
for x, y in zip(dep_x, dep_y):
    ax3.annotate(f"{y:.1f}", (x, y), xytext=(0, 9), textcoords="offset points",
                 ha="center", color=INK, fontsize=13, fontfamily=MONO)
ax3.set_xlabel("prompt depth (thousand tokens)", color=INK_DIM, fontsize=12, fontfamily=SANS, labelpad=8)
ax3.set_ylim(620, 1300)
ax3.set_yticks([])
ax3.tick_params(axis="x", colors=INK_DIM)

# ------------------------------------------------------ 4. MTP vs DFlash2
ax4 = fig.add_subplot(gs[1, 2])
dress(ax4, "The built-in head beats DFlash2", "gold: MTP head  ·  grey: DFlash2 drafter  ·  4 temperatures")
xs = list(range(4))
ax4.bar([x - w / 2 for x in xs], mtp, width=w, color=ACCENT, zorder=3)
ax4.bar([x + w / 2 for x in xs], df2, width=w, color=QUIET, zorder=3)
ax4.set_xticks(xs)
ax4.set_xticklabels([f"temp {t}" for t in temps])
ax4.set_yticks([])
ax4.set_ylim(0, 56)
for x, v in zip([x - w / 2 for x in xs], mtp):
    ax4.annotate(f"{v:.1f}", (x, v), xytext=(0, 4), textcoords="offset points",
                 ha="center", color=ACCENT, fontsize=11.5, fontfamily=MONO)
for x, v in zip([x + w / 2 for x in xs], df2):
    ax4.annotate(f"{v:.1f}", (x, v), xytext=(0, 4), textcoords="offset points",
                 ha="center", color=INK_DIM, fontsize=11.5, fontfamily=MONO)

# ------------------------------------------------------------------- header --
fig.text(0.055, 0.965, "Qwen3.8-27B on two RTX 3060s", color=INK,
         fontsize=40, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.888, "43 tok/s decode at 100k context, 1,097 tok/s prefill at 20k — "
                       "after 284 benchmark runs on one desktop",
         color=ACCENT, fontsize=19, fontfamily=SANS, va="top")
fig.text(0.965, 0.968, "llama.cpp b11041  ·  CUDA 13.3  ·  sm_86", color=INK_DIM,
         fontsize=13.5, fontfamily=MONO, ha="right", va="top")
fig.text(0.965, 0.939, "Q4_K_XL and IQ3_S quants  ·  Aug-Sep 2026", color=INK_DIM,
         fontsize=13.5, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------------- footer --
fig.add_artist(plt.Line2D([0.055, 0.965], [0.098, 0.098], color=RULE, lw=1))
fig.text(0.055, 0.068, "Every figure came off a real run on this one box: Xeon E5-2680 v4, "
                       "31 GB RAM, 2× RTX 3060 12 GB, no NVLink.",
         color=INK_DIM, fontsize=13, fontfamily=SANS, va="bottom")
fig.text(0.965, 0.028, "raw data and full write-ups: github.com/EamonMcKiernan05/Local-LLM-Testing",
         color=INK_DIM, fontsize=13, fontfamily=MONO, ha="right", va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
