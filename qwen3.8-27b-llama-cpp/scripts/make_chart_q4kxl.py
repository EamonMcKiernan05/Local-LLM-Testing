#!/usr/bin/env python3
"""
Chart: the UD-Q4_K_XL quant (17.56 GB, 4.5 bpw) on three RTX 3060s.

Every plotted value is read from data/csv/. Run:
    charts/.venv/bin/python scripts/make_chart_q4kxl.py
Output: charts/qwen38-27b-q4-k-xl-3x3060.png
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "data", "csv")
OUT = os.path.join(HERE, "..", "charts", "qwen38-27b-q4-k-xl-3x3060.png")

BG = "#15130F"
INK = "#EDE5D8"
INK_DIM = "#9A9184"
ACCENT = "#D8A73C"
QUIET = "#6B6459"
SER2 = "#C9C0B2"
SER3 = "#948B7E"
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
depth = load("prefill-by-depth.csv")


def series(key, col):
    rows = [r for r in depth if r["speculation"].startswith(key)]
    return ([f(r["prompt tokens"]) / 1000 for r in rows],
            [f(r[col]) for r in rows])


nx, ny = series("none", "prefill tok/s")
mx, my = series("MTP head", "prefill tok/s")
dx, dy = series("DFlash2 Q4_K_M", "prefill tok/s")
ndx, ndy = series("none", "decode at depth")
ddx, ddy = series("DFlash2 Q4_K_M", "decode at depth")

best = load("dflash2-best-per-drafter-per-temp.csv")
temps = ["0.0", "0.6", "0.8", "0.9"]
mtp_temp, df2_temp = [], []
for t in temps:
    rows = [r for r in best if r["Temperature"].strip() == t]
    mtp_temp.append(max(f(r["best gen tok/s (measured)"]) for r in rows if r["Drafter"].startswith("MTP")))
    df2_temp.append(max(f(r["best gen tok/s (measured)"]) for r in rows if r["Drafter"].startswith("DFlash2")))

live = load("live-service-summary.csv")
live_none = next(f(r["decode_tok_s"]) for r in live if "no MTP" in r["what"])
live_mtp = next(f(r["decode_tok_s"]) for r in live if "MTP n-max 8" in r["what"] and "sustained" in r["what"])

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


def keyrows(ax, rows, x0=0.60, y0=0.90, dy=0.085):
    for i, (col, mk, text) in enumerate(rows):
        y = y0 - i * dy
        ax.plot([x0, x0 + 0.033], [y, y], transform=ax.transAxes, color=col, lw=2.6,
                marker=mk, ms=8, markerfacecolor=BG, markeredgecolor=col,
                markeredgewidth=2.4, clip_on=False, zorder=7)
        ax.text(x0 + 0.045, y, text, transform=ax.transAxes, color=col, fontsize=12.5,
                fontfamily=SANS, va="center", zorder=7)


# ------------------------------------------------- 1. prefill against depth --
ax1 = fig.add_subplot(gs[0, :])
dress(ax1, "Prefill collapses with depth, and drafting makes it worse",
      "prompt processing, q8_0 KV, layer split 35,37,28, 3× RTX 3060 12 GB")
ax1.plot(nx, ny, color=ACCENT, lw=2.6, marker="o", ms=8, markerfacecolor=BG,
         markeredgecolor=ACCENT, markeredgewidth=2.4, zorder=5)
ax1.plot(mx, my, color=SER2, lw=0, marker="s", ms=9, markerfacecolor=BG,
         markeredgecolor=SER2, markeredgewidth=2.4, zorder=6)
ax1.plot(dx, dy, color=SER3, lw=2.6, marker="s", ms=8, markerfacecolor=BG,
         markeredgecolor=SER3, markeredgewidth=2.4, zorder=4)
for x, y in zip(nx, ny):
    ax1.annotate(f"{y:.1f}", (x, y), xytext=(0, 11), textcoords="offset points",
                 ha="center", color=ACCENT, fontsize=13.5, fontfamily=MONO)
for x, y in zip(mx, my):
    ax1.annotate(f"{y:.1f}", (x, y), xytext=(12, 3), textcoords="offset points",
                 ha="left", va="center", color=SER2, fontsize=13.5, fontfamily=MONO)
for x, y in zip(dx, dy):
    ax1.annotate(f"{y:.1f}", (x, y), xytext=(0, -21), textcoords="offset points",
                 ha="center", color=SER3, fontsize=13.5, fontfamily=MONO)
keyrows(ax1, [
    (ACCENT, "o", "no speculation"),
    (SER2, "s", "MTP head n-max 4  (20k only)"),
    (SER3, "s", "DFlash2 Q4_K_M n-max 4"),
])
ax1.set_xlabel("prompt depth (thousand tokens)", color=INK_DIM, fontsize=12,
               fontfamily=SANS, labelpad=8)
ax1.set_ylim(430, 1270)
ax1.set_yticks([])
ax1.set_xlim(8, 168)

# --------------------------------------------- 2. MTP vs DFlash2 by temp ----
ax2 = fig.add_subplot(gs[1, 0])
dress(ax2, "The built-in head beats DFlash2", "gold: MTP  ·  grey: DFlash2")
xs = list(range(4))
w = 0.34
ax2.bar([x - w / 2 for x in xs], mtp_temp, width=w, color=ACCENT, zorder=3)
ax2.bar([x + w / 2 for x in xs], df2_temp, width=w, color=QUIET, zorder=3)
for x, v in zip([x - w / 2 for x in xs], mtp_temp):
    ax2.annotate(f"{v:.1f}", (x, v), xytext=(-5, 4), textcoords="offset points",
                 ha="right", color=ACCENT, fontsize=12, fontfamily=MONO)
for x, v in zip([x + w / 2 for x in xs], df2_temp):
    ax2.annotate(f"{v:.1f}", (x, v), xytext=(0, -6), textcoords="offset points",
                 ha="center", va="top", color=BG, fontsize=11.5, fontfamily=MONO)
ax2.set_xticks(xs)
ax2.set_xticklabels([f"temp {t}" for t in temps], fontsize=11.5)
ax2.set_yticks([])
ax2.set_ylim(0, 58)

# --------------------------------------------------- 3. decode against depth -
ax3 = fig.add_subplot(gs[1, 1])
dress(ax3, "Decode runs the other way", "")
ax3.plot(ndx, ndy, color=ACCENT, lw=2.6, marker="o", ms=8, markerfacecolor=BG,
         markeredgecolor=ACCENT, markeredgewidth=2.4, zorder=5)
ax3.plot(ddx, ddy, color=SER3, lw=2.6, marker="^", ms=8, markerfacecolor=BG,
         markeredgecolor=SER3, markeredgewidth=2.4, zorder=4)
for x, y in zip(ndx, ndy):
    ax3.annotate(f"{y:.1f}", (x, y), xytext=(0, -20), textcoords="offset points",
                 ha="center", color=ACCENT, fontsize=12, fontfamily=MONO)
for x, y in zip(ddx, ddy):
    ax3.annotate(f"{y:.1f}", (x, y), xytext=(0, 9), textcoords="offset points",
                 ha="center", color=SER3, fontsize=12, fontfamily=MONO)
ax3.set_xlabel("prompt depth (thousand tokens)", color=INK_DIM, fontsize=12,
               fontfamily=SANS, labelpad=8)
ax3.set_ylim(0, 38)
ax3.set_yticks([])
ax3.set_xlim(8, 168)

# --------------------------------------------- 4. what it did on real traffic
ax4 = fig.add_subplot(gs[1, 2])
dress(ax4, "On real fleet traffic", "weighted over 23.4M generated tokens, live service")
ax4.bar([0], [live_none], width=0.5, color=QUIET, zorder=3)
ax4.bar([1], [live_mtp], width=0.5, color=ACCENT, zorder=3)
for x, v in [(0, live_none), (1, live_mtp)]:
    ax4.annotate(f"{v:.1f}", (x, v), xytext=(0, 4), textcoords="offset points",
                 ha="center", color=ACCENT if x else INK_DIM, fontsize=13, fontfamily=MONO)
ax4.set_xticks([0, 1])
ax4.set_xticklabels(["no MTP", "MTP n-max 8\np-min 0.85"], fontsize=11.5, linespacing=1.7)
ax4.set_yticks([])
ax4.set_ylim(0, 31)


# ------------------------------------------------------------------- header --
fig.text(0.055, 0.965, "Qwen3.8-27B  UD-Q4_K_XL", color=INK,
         fontsize=40, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.888, "17.56 GB, 4.5 bpw, three RTX 3060s — 1,096.8 tok/s prefill at 20k, "
                       "~30 tok/s decode at 20k, and the flag worth +42% on real traffic",
         color=ACCENT, fontsize=19, fontfamily=SANS, va="top")
fig.text(0.965, 0.968, "llama.cpp b10068 / b11041  ·  CUDA 13.3  ·  sm_86", color=INK_DIM,
         fontsize=13.5, fontfamily=MONO, ha="right", va="top")
fig.text(0.965, 0.939, "q4_K_XL weights  ·  q8_0 KV cache", color=INK_DIM,
         fontsize=13.5, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------------- footer --
fig.add_artist(plt.Line2D([0.055, 0.965], [0.112, 0.112], color=RULE, lw=1))
fig.text(0.055, 0.085, "107-run speculative-decoding bake-off, three DFlash2 quants, n-max 1-8, four temperatures: "
                       "the built-in MTP head won at every one.",
         color=INK_DIM, fontsize=12.5, fontfamily=SANS, va="bottom")
fig.text(0.055, 0.055, "Peak seen live on the three-card setup: 35 tok/s decode — a burst, not a steady-state rate.",
         color=ACCENT, fontsize=12.5, fontfamily=SANS, va="bottom")
fig.text(0.965, 0.025, "raw data and full write-ups: github.com/EamonMcKiernan05/Local-LLM-Testing",
         color=INK_DIM, fontsize=12.5, fontfamily=MONO, ha="right", va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
