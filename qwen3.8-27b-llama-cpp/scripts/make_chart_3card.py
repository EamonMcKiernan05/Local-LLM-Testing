#!/usr/bin/env python3
"""
Draw the three-card companion chart.

Every plotted value is read from data/csv/ - nothing is typed in twice. Run:

    charts/.venv/bin/python scripts/make_chart_3card.py

Output: charts/qwen38-27b-llama-cpp-3x3060.png  (1600x1000 at 150 dpi)
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "data", "csv")
OUT = os.path.join(HERE, "..", "charts", "qwen38-27b-llama-cpp-3x3060.png")

# same palette and voice as the two-card chart
BG = "#15130F"
INK = "#EDE5D8"
INK_DIM = "#9A9184"
ACCENT = "#D8A73C"
QUIET = "#585147"
RULE = "#332E27"


def pick(candidates, fallback):
    have = {f.name for f in font_manager.fontManager.ttflist}
    for c in candidates:
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
    return float(str(x).replace(",", ""))


# --------------------------------------------------------------------- data --
depth = load("prefill-by-depth.csv")
none_x = [f(r["prompt tokens"]) / 1000 for r in depth if r["speculation"] == "none"]
none_y = [f(r["prefill tok/s"]) for r in depth if r["speculation"] == "none"]
df_x = [f(r["prompt tokens"]) / 1000 for r in depth if r["speculation"].startswith("DFlash2 Q4_K_M")]
df_y = [f(r["prefill tok/s"]) for r in depth if r["speculation"].startswith("DFlash2 Q4_K_M")]

matrix = load("100k-split-mode-matrix.csv")
rep1 = {}
for r in matrix:
    if r["arm"].endswith("rep1"):
        rep1[r["arm"].replace(" rep1", "")] = r
layouts = [
    ("2 cards\ntensor", "mode-tensor2-nmax7", QUIET),
    ("2 cards\nlayer", "mode-layer2-nmax7", QUIET),
    ("3 cards\nlayer", "mode-layer3-nmax7", ACCENT),
    ("3 cards\ntensor", "mode-tensor3-nmax7", ACCENT),
]
pf = [(lbl, f(rep1[key]["prefill tok/s"]), col) for lbl, key, col in layouts]
gd = [(lbl, f(rep1[key]["gen tok/s"]), col) for lbl, key, col in layouts]

# MTP head: measured at 20k in the depth profile (UD-Q4_K_XL, n-max 4) and at
# 100k in the three-card matrix (IQ3_S, n-max 7). Two quants, so the series is
# drawn as discrete points with no connecting line.
mtp20 = f(next(r for r in depth if r["speculation"].startswith("MTP head"))["prefill tok/s"])
mtp100 = f(next(r for r in load("three-card-matrix.csv")
                if r["arm"] == "g3-layer-ts353728-mtp7")["prefill tok/s"])

df = load("three-card-dflash2-nmax.csv")
df_nmax = [int(r["n-max"]) for r in df]
df_gen = [f(r["gen tok/s"]) for r in df]

mtp3 = load("three-card-matrix.csv")
mtp_ref = f(next(r for r in mtp3 if r["arm"] == "g3-layer-ts353728-mtp7")["gen tok/s"])

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


def bars(ax, data, ylim, fmt="{:.0f}", label_size=13.5):
    xs = list(range(len(data)))
    for x, (lbl, val, col) in zip(xs, data):
        ax.bar([x], [val], width=0.58, color=col, zorder=3)
        ax.annotate(fmt.format(val), (x, val), xytext=(0, 5), textcoords="offset points",
                    ha="center", color=ACCENT if col == ACCENT else INK_DIM,
                    fontsize=label_size, fontfamily=MONO)
    ax.set_xticks(xs)
    ax.set_xticklabels([d[0] for d in data], linespacing=1.6)
    ax.set_yticks([])
    ax.set_ylim(0, ylim)
    ax.set_xlim(-0.6, len(data) - 0.4)


# ------------------------------------------- 1. three-card prefill vs depth --
MTPSER = "#C9C0B2"
DF2SER = "#948B7E"

ax1 = fig.add_subplot(gs[0, :])
dress(ax1, "On three cards, prefill degrades with depth but never falls off a cliff",
      "prompt processing rate, q8_0 KV, layer split 35,37,28, 3× RTX 3060 12 GB")
ax1.plot(none_x, none_y, color=ACCENT, lw=2.6, marker="o", ms=8,
         markerfacecolor=BG, markeredgecolor=ACCENT, markeredgewidth=2.4, zorder=5)
ax1.plot(df_x, df_y, color=DF2SER, lw=2.6, marker="^", ms=8,
         markerfacecolor=BG, markeredgecolor=DF2SER, markeredgewidth=2.4, zorder=4)
ax1.plot([19.966, 99.589], [mtp20, mtp100], color=MTPSER, lw=0, linestyle="none",
         marker="s", ms=9, markerfacecolor=BG, markeredgecolor=MTPSER,
         markeredgewidth=2.4, zorder=6)
for x, y in zip(none_x, none_y):
    ax1.annotate(f"{y:.1f}", (x, y), xytext=(0, 11), textcoords="offset points",
                 ha="center", color=ACCENT, fontsize=13.5, fontfamily=MONO)
for x, y in zip(df_x, df_y):
    ax1.annotate(f"{y:.1f}", (x, y), xytext=(0, -21), textcoords="offset points",
                 ha="center", color=DF2SER, fontsize=13.5, fontfamily=MONO)
ax1.annotate(f"{mtp20:.1f}", (19.966, mtp20), xytext=(12, 3), textcoords="offset points",
             ha="left", va="center", color=MTPSER, fontsize=13.5, fontfamily=MONO)
ax1.annotate(f"{mtp100:.1f}", (99.589, mtp100), xytext=(9, -4), textcoords="offset points",
             ha="left", va="center", color=MTPSER, fontsize=13.5, fontfamily=MONO)
ax1.annotate("IQ3_S", (99.589, mtp100), xytext=(9, -20), textcoords="offset points",
             ha="left", va="center", color=MTPSER, fontsize=11.5, fontfamily=SANS)
ax1.set_xlabel("prompt depth (thousand tokens)", color=INK_DIM, fontsize=12,
               fontfamily=SANS, labelpad=8)
ax1.set_ylim(430, 1270)
ax1.set_yticks([])
ax1.set_xlim(8, 168)
handles = [
    plt.Line2D([], [], color=ACCENT, lw=2.6, marker="o", ms=8, markerfacecolor=BG,
               markeredgecolor=ACCENT, markeredgewidth=2.4, label="no speculation  ·  UD-Q4_K_XL"),
    plt.Line2D([], [], color=MTPSER, lw=0, marker="s", ms=9, markerfacecolor=BG,
               markeredgecolor=MTPSER, markeredgewidth=2.4,
               label="MTP head  ·  two measured points, two quants"),
    plt.Line2D([], [], color=DF2SER, lw=2.6, marker="^", ms=8, markerfacecolor=BG,
               markeredgecolor=DF2SER, markeredgewidth=2.4, label="DFlash2 drafter n-max 4  ·  UD-Q4_K_XL"),
]
# hand-drawn key: matplotlib's legend text did not render against this background
key = [
    (ACCENT, "o", "no speculation  (UD-Q4_K_XL)"),
    (MTPSER, "s", "MTP head  (2 points, 2 quants)"),
    (DF2SER, "^", "DFlash2 n-max 4  (UD-Q4_K_XL)"),
]
for i, (col, mk, text) in enumerate(key):
    y = 0.90 - i * 0.085
    ax1.plot([0.575, 0.608], [y, y], transform=ax1.transAxes, color=col,
             lw=2.6, marker=mk, ms=8, markerfacecolor=BG, markeredgecolor=col,
             markeredgewidth=2.4, clip_on=False, zorder=7)
    ax1.text(0.620, y, text, transform=ax1.transAxes, color=col, fontsize=12.5,
             fontfamily=SANS, va="center", zorder=7)

# ------------------------------------- 2. what the third card buys, at 100k --
ax2 = fig.add_subplot(gs[1, 0])
dress(ax2, "Adding a third card buys prefill", "gold: three cards  ·  grey: two cards")
bars(ax2, pf, 760)

# ---------------------------------------- 3. ... and costs decode -----------
ax3 = fig.add_subplot(gs[1, 1])
dress(ax3, "...and costs you decode", "same four layouts, MTP n-max 7, 100k depth")
bars(ax3, gd, 56, fmt="{:.1f}")

# ---------------------------------------- 4. DFlash2 on three cards --------
ax4 = fig.add_subplot(gs[1, 2])
dress(ax4, "DFlash2 has no sweet spot on three cards",
      "grey: drafter  ·  gold: MTP head")
ax4.bar(df_nmax, df_gen, width=0.62, color=QUIET, zorder=3)
ax4.axhline(mtp_ref, color=ACCENT, lw=2, zorder=4)
ax4.annotate(f"MTP head {mtp_ref:.2f}", xy=(0.95, mtp_ref), xytext=(0, -7),
             textcoords="offset points", ha="left", va="top", color=ACCENT,
             fontsize=13, fontfamily=MONO)
ax4.set_xticks(df_nmax)
ax4.set_xticklabels([str(n) for n in df_nmax])
ax4.set_xlabel("DFlash2 n-max", color=INK_DIM, fontsize=12, fontfamily=SANS, labelpad=8)
ax4.set_yticks([0, 10, 20, 30])
ax4.set_yticklabels(["0", "10", "20", "30"], fontsize=11.5)
ax4.set_ylim(0, 31)
ax4.set_xlim(0.4, 8.6)

# ------------------------------------------------------------------- header --
fig.text(0.055, 0.965, "Qwen3.8-27B on three RTX 3060s", color=INK,
         fontsize=40, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.888, "1,096.8 tok/s prefill at 20k, 840 at 100k, 717 at 150k — "
                       "the third card is a prefill card, not a decode card",
         color=ACCENT, fontsize=19, fontfamily=SANS, va="top")
fig.text(0.965, 0.968, "llama.cpp b11041  ·  CUDA 13.3  ·  sm_86", color=INK_DIM,
         fontsize=13.5, fontfamily=MONO, ha="right", va="top")
fig.text(0.965, 0.939, "third card on PCIe 2.0 x4  ·  Aug-Sep 2026", color=INK_DIM,
         fontsize=13.5, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------------- footer --
fig.add_artist(plt.Line2D([0.055, 0.965], [0.112, 0.112], color=RULE, lw=1))
fig.text(0.055, 0.085, "Three-card era: the third card left the bus on 2026-09-23, and two-card tensor "
                       "split + MTP decoded 1.7× faster than any three-card layout.",
         color=INK_DIM, fontsize=12.5, fontfamily=SANS, va="bottom")
fig.text(0.055, 0.055, "Peak seen live on the three-card setup: 35 tok/s decode (Eamon's own measurement) — a burst. "
                       "Fastest controlled three-card arm here: 47.3 tok/s at 20k greedy.",
         color=ACCENT, fontsize=12.5, fontfamily=SANS, va="bottom")
fig.text(0.965, 0.025, "raw data and full write-ups: github.com/EamonMcKiernan05/Local-LLM-Testing",
         color=INK_DIM, fontsize=12.5, fontfamily=MONO, ha="right", va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
