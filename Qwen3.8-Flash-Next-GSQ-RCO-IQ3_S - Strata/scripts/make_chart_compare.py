#!/usr/bin/env python3
"""Strata 0.1.39 vs 0.1.32 comparison — same model, same battery, one day, one box.
Decode + prefill curves, two series each (grey: 0.1.32, gold: 0.1.39), per-depth delta sidebar.
Every value parsed from data/csv/release-0-1-32-vs-0-1-39.csv.
Output: charts/strata-v100-0132-vs-0139.png
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "csv", "release-0-1-32-vs-0-1-39.csv")
OUT = os.path.join(HERE, "..", "charts", "strata-v100-0132-vs-0139.png")

BG = "#15130F"
CARD = "#1A1712"
INK = "#EDE5D8"
INK_DIM = "#9A9184"
ACCENT = "#D8A73C"
BEFORE = "#9A9184"
AFTER = "#D8A73C"
FILL = "#585147"
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


def load(engine):
    by = {}
    with open(SRC, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["engine"] == engine:
                by[int(r["depth_k"])] = {
                    "ptok": int(r["ptok"]),
                    "prefill_tps": float(r["prefill_tps"]),
                    "decode_tps": float(r["decode_tps"]),
                }
    return by


B = load("0.1.32")   # before
A = load("0.1.39")   # after
depths = sorted(set(B) & set(A))
assert len(depths) == 6, "need all six depths in both runs"

xs = [A[d]["ptok"] for d in depths]
pre_b = [B[d]["prefill_tps"] for d in depths]
pre_a = [A[d]["prefill_tps"] for d in depths]
dec_b = [B[d]["decode_tps"] for d in depths]
dec_a = [A[d]["decode_tps"] for d in depths]
pre_pct = [100.0 * (a - b) / b for b, a in zip(pre_b, pre_a)]
dec_pct = [100.0 * (a - b) / b for b, a in zip(dec_b, dec_a)]
pre_mean = sum(pre_pct) / len(pre_pct)
dec_mean = sum(dec_pct) / len(dec_pct)


def pct(v):
    return "{:+.1f}%".format(v)


fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)

# ------------------------------------------------------------------ header ---
fig.text(0.055, 0.965, "Strata 0.1.39 vs 0.1.32 \u00b7 Depth Benchmark", color=INK,
         fontsize=38, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.902, "Qwen 3.8 Flash base IQ3_S (GSQ-RCO) \u00b7 2\u00d7 Tesla V100 32 GB \u00b7 same six documents, "
                       "same config, same day \u00b7 grey: 0.1.32, gold: 0.1.39",
         color=INK_DIM, fontsize=16.5, fontfamily=SANS, va="top")
fig.text(0.965, 0.965, "model-bench  \u00b7  CUDA 12.9  \u00b7  sm_70  \u00b7  2026-10-04",
         color=INK_DIM, fontsize=13, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------------- tiles ---
axt = fig.add_axes([0.055, 0.735, 0.91, 0.125])
axt.set_xlim(0, 1)
axt.set_ylim(0, 1)
axt.axis("off")
tiles = [
    ("Decode @ 250K", "{:.1f} \u2192 {:.1f}".format(dec_b[-1], dec_a[-1]), "tok/s \u00b7 " + pct(dec_pct[-1]), False),
    ("Decode mean gain", pct(dec_mean), "20K \u2013 250K across six depths", True),
    ("Prefill @ 250K", "{:,.0f} \u2192 {:,.0f}".format(pre_b[-1], pre_a[-1]), "tok/s \u00b7 " + pct(pre_pct[-1]), False),
    ("Prefill mean gain", pct(pre_mean), "20K \u2013 250K across six depths", False),
    ("Battery", "6 \u00d7 400", "unique docs \u00b7 gate 0.50", False),
]
gap = 0.018
tw = (1.0 - 4 * gap) / 5.0
for i, (label, val, sub, hi) in enumerate(tiles):
    x0 = i * (tw + gap)
    axt.add_patch(Rectangle((x0, 0), tw, 1, facecolor=CARD,
                            edgecolor=ACCENT if hi else RULE, lw=1.6 if hi else 1.0,
                            clip_on=False))
    axt.text(x0 + 0.011, 0.82, label, color=INK_DIM, fontsize=12.5, fontfamily=SANS, va="center")
    axt.text(x0 + 0.011, 0.42, val, color=INK, fontsize=21, fontfamily=MONO, va="center")
    axt.text(x0 + 0.011, 0.16, sub, color=ACCENT if hi else INK_DIM, fontsize=11, fontfamily=MONO, va="center")


def series_plot(ax, ys_b, ys_a, pcts, fmt, title, sub, first_b=(-14, 14)):
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor="none",
                           edgecolor=RULE, lw=1.0, clip_on=False, zorder=0))
    ax.fill_between(xs, ys_b, ys_a, color=ACCENT, alpha=0.10, zorder=2)
    ax.plot(xs, ys_b, color=BEFORE, lw=2.2, zorder=4)
    ax.plot(xs, ys_a, color=AFTER, lw=2.6, zorder=5)
    ax.plot(xs, ys_b, "o", color=BEFORE, ms=5.5, markeredgecolor=BG, markeredgewidth=1.2, zorder=4)
    ax.plot(xs, ys_a, "o", color=AFTER, ms=6.5, markeredgecolor=BG, markeredgewidth=1.4, zorder=6)
    # label both series at the first and last depth only
    ax.annotate(fmt(ys_b[0]), (xs[0], ys_b[0]), xytext=first_b, textcoords="offset points",
                ha="center", color=INK_DIM, fontsize=11, fontfamily=MONO)
    ax.annotate(fmt(ys_a[0]), (xs[0], ys_a[0]), xytext=(0, 16), textcoords="offset points",
                ha="center", color=ACCENT, fontsize=11, fontfamily=MONO)
    ax.annotate(fmt(ys_b[-1]), (xs[-1], ys_b[-1]), xytext=(14, 12), textcoords="offset points",
                ha="center", color=INK_DIM, fontsize=11, fontfamily=MONO)
    ax.annotate(fmt(ys_a[-1]), (xs[-1], ys_a[-1]), xytext=(0, 16), textcoords="offset points",
                ha="center", color=ACCENT, fontsize=11, fontfamily=MONO)
    ax.set_xticks([0, 50000, 100000, 150000, 200000, 250000])
    ax.set_xticklabels(["0", "50K", "100K", "150K", "200K", "250K"])
    ax.tick_params(colors=INK_DIM, labelsize=11.5, length=0)
    for lbl in ax.get_xticklabels():
        lbl.set_fontfamily(MONO)
    ax.set_yticks([])
    ax.set_xlim(0, 268000)
    lo = min(min(ys_b), min(ys_a))
    hi = max(max(ys_b), max(ys_a))
    ax.set_ylim(lo * 0.72, hi * 1.30)
    ax.set_title(title, color=INK, fontsize=18, fontfamily=DISPLAY, loc="left", pad=26)
    ax.annotate(sub, xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=12,
                fontfamily=SANS, va="bottom")


# --------------------------------------------------- decode comparison ------
axd = fig.add_axes([0.055, 0.455, 0.60, 0.215])
series_plot(axd, dec_b, dec_a, dec_pct, lambda v: "%.1f" % v,
            "Token Generation Speed by Depth",
            "decode tokens per second \u00b7 grey line: 0.1.32, gold line: 0.1.39 \u00b7 shaded: gain")

# -------------------------------------------------- prefill comparison ------
axp = fig.add_axes([0.055, 0.13, 0.60, 0.215])
series_plot(axp, pre_b, pre_a, pre_pct, lambda v: "{:,.0f}".format(v),
            "Prompt Processing Speed by Depth",
            "prompt tokens per second \u00b7 grey line: 0.1.32, gold line: 0.1.39 \u00b7 shaded: gain",
            first_b=(-18, -26))

# ----------------------------------------------------------------- sidebar ---
axs = fig.add_axes([0.678, 0.13, 0.287, 0.54])
axs.set_xlim(0, 1)
axs.set_ylim(0, 1)
axs.axis("off")
axs.add_patch(Rectangle((0, 0), 1, 1, facecolor=CARD, edgecolor=RULE, lw=1.0, clip_on=False))
axs.text(0.055, 0.955, "Gain by Depth", color=INK, fontsize=18, fontfamily=DISPLAY, va="center")
axs.add_patch(Rectangle((0.055, 0.918), 0.89, 0.0018, facecolor=RULE, clip_on=False))
axs.text(0.055, 0.875, "depth", color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="center")
axs.text(0.40, 0.875, "decode", color=INK_DIM, fontsize=11.5, fontfamily=SANS, ha="center", va="center")
axs.text(0.72, 0.875, "prefill", color=INK_DIM, fontsize=11.5, fontfamily=SANS, ha="center", va="center")
y = 0.795
for i, d in enumerate(depths):
    axs.text(0.055, y, "{}K".format(d // 1000), color=INK, fontsize=13, fontfamily=MONO, va="center")
    axs.text(0.40, y, pct(dec_pct[i]), color=ACCENT if dec_pct[i] >= 0 else INK_DIM,
             fontsize=13, fontfamily=MONO, ha="center", va="center")
    axs.text(0.72, y, pct(pre_pct[i]), color=ACCENT if pre_pct[i] >= 0 else INK_DIM,
             fontsize=13, fontfamily=MONO, ha="center", va="center")
    y -= 0.062
axs.add_patch(Rectangle((0.055, y + 0.028), 0.89, 0.0018, facecolor=RULE, clip_on=False))
y -= 0.01
axs.text(0.055, y, "mean", color=INK_DIM, fontsize=13, fontfamily=SANS, va="center")
axs.text(0.40, y, pct(dec_mean), color=ACCENT, fontsize=13.5, fontfamily=MONO, ha="center", va="center")
axs.text(0.72, y, pct(pre_mean), color=ACCENT, fontsize=13.5, fontfamily=MONO, ha="center", va="center")
y -= 0.085
axs.text(0.055, y, "Absolute @ 250K", color=INK_DIM, fontsize=12, fontfamily=SANS, va="center")
y -= 0.052
axs.text(0.055, y, "decode   {:.1f} \u2192 {:.1f}".format(dec_b[-1], dec_a[-1]), color=INK,
         fontsize=12.5, fontfamily=MONO, va="center")
y -= 0.052
axs.text(0.055, y, "prefill  {:,.0f} \u2192 {:,.0f}".format(pre_b[-1], pre_a[-1]), color=INK,
         fontsize=12.5, fontfamily=MONO, va="center")

# ----------------------------------------------------------------- footer ----
fig.add_artist(plt.Line2D([0.055, 0.965], [0.098, 0.098], color=RULE, lw=1))
fig.text(0.055, 0.068, "Only the engine differs: same six documents, same config (drafter gate 0.50), same day, "
                       "one battery each.",
         color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")
fig.text(0.055, 0.040, "raw: model-bench runs 2026-10-04T1320Z (0.1.32) and 2026-10-04T1335Z (0.1.39) \u00b7 box .5.",
         color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")
fig.text(0.965, 0.040, "decode {} mean \u00b7 prefill {} mean".format(pct(dec_mean), pct(pre_mean)),
         color=ACCENT, fontsize=12.5, fontfamily=SANS, ha="right", va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
