#!/usr/bin/env python3
"""
Chart: why the dedicated DFlash2 drafter lost to the built-in MTP head.

Every plotted value is read from data/csv/. Run:
    charts/.venv/bin/python scripts/make_chart_mtp_vs_dflash2.py
Output: charts/qwen38-27b-mtp-vs-dflash2-3x3060.png
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "data", "csv")
OUT = os.path.join(HERE, "..", "charts", "qwen38-27b-mtp-vs-dflash2-3x3060.png")

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
temps = ["0.0", "0.6", "0.8", "0.9"]
best = load("dflash2-best-per-drafter-per-temp.csv")


def fastest(fam, t):
    rows = [r for r in best if r["Temperature"].strip() == t and r["Drafter"].startswith(fam)]
    return max(rows, key=lambda r: f(r["best gen tok/s (measured)"]))


df2 = {t: fastest("DFlash2", t) for t in temps}   # the Q4_K_M row is fastest at all four
mtp = {t: fastest("MTP", t) for t in temps}

df2_v = [f(df2[t]["best gen tok/s (measured)"]) for t in temps]
mtp_v = [f(mtp[t]["best gen tok/s (measured)"]) for t in temps]
df2_acc = [f(df2[t]["draft acceptance %"]) for t in temps]
mtp_acc = [f(mtp[t]["draft acceptance %"]) for t in temps]
df2_n = [int(df2[t]["at n-max"]) for t in temps]
mtp_n = [int(mtp[t]["at n-max"]) for t in temps]
margins = [(m - d) / d * 100 for d, m in zip(df2_v, mtp_v)]

depth = load("prefill-by-depth.csv")


def prefill(key, toks="19,966"):
    return f(next(r["prefill tok/s"] for r in depth
                  if r["prompt tokens"] == toks and r["speculation"].startswith(key)))


pf_none = prefill("none")
pf_mtp = prefill("MTP head")
pf_df2 = prefill("DFlash2 Q4_K_M")
pf_tax_df2 = (pf_df2 - pf_none) / pf_none * 100
pf_tax_mtp = (pf_mtp - pf_none) / pf_none * 100

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


# -------------------------------------------- 1. the reason: acceptance -------
ax1 = fig.add_subplot(gs[0, :])
dress(ax1, "MTP's acceptance holds — DFlash2's collapses once it samples",
      "draft acceptance %, fastest arm per family  ·  grey: DFlash2 Q4_K_M  ·  gold: MTP")
xs = list(range(4))
w = 0.30
ax1.bar([x - 0.17 for x in xs], df2_acc, width=w, color=QUIET, zorder=3)
ax1.bar([x + 0.17 for x in xs], mtp_acc, width=w, color=ACCENT, zorder=3)
for x, v in zip([x - 0.17 for x in xs], df2_acc):
    ax1.annotate(f"{v:.1f}%", (x, v), xytext=(0, 6), textcoords="offset points",
                 ha="center", color=INK_DIM, fontsize=13, fontfamily=MONO)
for x, v in zip([x + 0.17 for x in xs], mtp_acc):
    ax1.annotate(f"{v:.1f}%", (x, v), xytext=(0, 6), textcoords="offset points",
                 ha="center", color=ACCENT, fontsize=13, fontfamily=MONO)
ax1.set_xticks(xs)
ax1.set_xticklabels([f"temp {t}" for t in temps], fontsize=13)
ax1.set_yticks([])
ax1.set_ylim(0, 112)
ax1.set_xlim(-0.5, 3.5)

# -------------------------------------------- 2. it lost at every temp -------
ax2 = fig.add_subplot(gs[1, 0])
dress(ax2, "It lost at every temperature",
      "best measured decode, tok/s  ·  gold: MTP  ·  grey: DFlash2")
xs2 = list(range(4))
w2 = 0.34
ax2.bar([x - w2 / 2 for x in xs2], mtp_v, width=w2, color=ACCENT, zorder=3)
ax2.bar([x + w2 / 2 for x in xs2], df2_v, width=w2, color=QUIET, zorder=3)
for x, v in zip([x - w2 / 2 for x in xs2], mtp_v):
    ax2.annotate(f"{v:.1f}", (x, v), xytext=(0, 5), textcoords="offset points",
                 ha="center", color=ACCENT, fontsize=11.5, fontfamily=MONO)
for x, v in zip([x + w2 / 2 for x in xs2], df2_v):
    ax2.annotate(f"{v:.1f}", (x, v), xytext=(0, -6), textcoords="offset points",
                 ha="center", va="top", color=BG, fontsize=11.5, fontfamily=MONO)
for x, m in zip(xs2, margins):
    ax2.annotate(f"+{m:.1f}%", (x, 57.0), ha="center", color=INK_DIM,
                 fontsize=11, fontfamily=MONO)
ax2.set_xticks(xs2)
ax2.set_xticklabels([f"temp {t}" for t in temps], fontsize=11.5)
ax2.set_yticks([])
ax2.set_ylim(0, 63)

# -------------------------------------------- 3. the window it can afford ----
ax3 = fig.add_subplot(gs[1, 1])
dress(ax3, "Its best draft window shrinks", "n-max of the fastest arm, per temperature")
ax3.plot(xs2, df2_n, color=SER3, lw=2.2, marker="s", ms=9, markerfacecolor=BG,
         markeredgecolor=SER3, markeredgewidth=2.2, zorder=4)
ax3.plot(xs2, mtp_n, color=ACCENT, lw=2.2, marker="o", ms=9, markerfacecolor=BG,
         markeredgecolor=ACCENT, markeredgewidth=2.2, zorder=5)
for x, v in zip(xs2, df2_n):
    ax3.annotate(str(v), (x, v), xytext=(-16, 1), textcoords="offset points",
                 ha="center", va="center", color=SER3, fontsize=13, fontfamily=MONO)
for x, v in zip(xs2, mtp_n):
    ax3.annotate(str(v), (x, v), xytext=(16, 1), textcoords="offset points",
                 ha="center", va="center", color=ACCENT, fontsize=13, fontfamily=MONO)
ax3.set_xticks(xs2)
ax3.set_xticklabels([f"temp {t}" for t in temps], fontsize=11.5)
ax3.set_yticks([])
ax3.set_ylim(0, 10)
ax3.set_xlim(-0.4, 3.4)

# -------------------------------------------- 4. and it taxes prefill ---------
ax4 = fig.add_subplot(gs[1, 2])
dress(ax4, "And it taxes prefill",
      "prefill tok/s at ~20k, n-max 4 arms")
vals = [pf_none, pf_mtp, pf_df2]
cols = [SER2, ACCENT, QUIET]
ax4.bar([0, 1, 2], vals, width=0.5, color=cols, zorder=3)
for x, v in zip([0, 1, 2], vals):
    ax4.annotate(f"{v:.1f}", (x, v), xytext=(0, 4), textcoords="offset points",
                 ha="center", color=ACCENT if x == 1 else INK_DIM, fontsize=12.5,
                 fontfamily=MONO)
ax4.annotate(f"{pf_tax_df2:.0f}%", (2, pf_df2 * 0.5), ha="center", va="center",
             color=BG, fontsize=13.5, fontfamily=MONO)
ax4.annotate(f"{pf_tax_mtp:.0f}%", (1, pf_mtp * 0.5), ha="center", va="center",
             color=BG, fontsize=13.5, fontfamily=MONO)
ax4.set_xticks([0, 1, 2])
ax4.set_xticklabels(["no spec", "MTP", "DFlash2"], fontsize=11.5)
ax4.set_yticks([])
ax4.set_ylim(0, 1290)

# ------------------------------------------------------------------- header --
fig.text(0.055, 0.965, "Qwen3.8-27B  ·  DFlash2 vs the built-in MTP head", color=INK,
         fontsize=34, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.888, "UD-Q4_K_XL on three RTX 3060s — 107 measured runs, four temperatures: "
                       "MTP won every one, and this is why",
         color=ACCENT, fontsize=19, fontfamily=SANS, va="top")
fig.text(0.965, 0.968, "llama.cpp b11041  ·  CUDA 13.3  ·  sm_86", color=INK_DIM,
         fontsize=13.5, fontfamily=MONO, ha="right", va="top")
fig.text(0.965, 0.939, "ctx 32k  ·  q8_0 KV  ·  layer split 35,37,28",
         color=INK_DIM, fontsize=13.5, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------------- footer --
fig.add_artist(plt.Line2D([0.055, 0.965], [0.112, 0.112], color=RULE, lw=1))
fig.text(0.055, 0.085, "107 runs at ~20k prompt depth: 32 arms greedy, 11 at temp 0.6, 32 at 0.8, 32 at 0.9 — "
                       "three DFlash2 quants, n-max 1-8, one throwaway server per arm.",
         color=INK_DIM, fontsize=12.5, fontfamily=SANS, va="bottom")
fig.text(0.055, 0.055, "Drafter size bought nothing: Q4_K_M, Q8_0 and BF16 accepted identical token counts "
                       "at every setting — the bigger quants only ran slower.",
         color=ACCENT, fontsize=12.5, fontfamily=SANS, va="bottom")
fig.text(0.965, 0.025, "raw data and full write-ups: github.com/EamonMcKiernan05/Local-LLM-Testing",
         color=INK_DIM, fontsize=12.5, fontfamily=MONO, ha="right", va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
