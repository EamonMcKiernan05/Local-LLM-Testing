#!/usr/bin/env python3
"""AJ-IQ2_XXS context comparison - 262,144 vs 131,072, same quant, same rig, same depths, same day.
Decode + prefill curves, two series (grey: 256K, gold: 131K), per-depth delta sidebar, house design.
Three fresh-load runs per side, mean shown; every value parsed from ../data/csv/ctx-aj-256k-vs-131k.csv.
Output: aj-iq2xxs-256k-vs-131k.png
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "csv", "ctx-aj-256k-vs-131k.csv")
OUT = os.path.join(HERE, "..", "charts", "aj-iq2xxs-256k-vs-131k.png")

BG = "#15130F"
CARD = "#1A1712"
INK = "#EDE5D8"
INK_DIM = "#9A9184"
ACCENT = "#D8A73C"
BEFORE = "#C9C0B2"
AFTER = "#D8A73C"
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
    with open(SRC, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if r["ctx"] == engine:
                by[int(r["depth_k"])] = {
                    "ptok": int(r["ptok"]),
                    "prefill_tps": float(r["prefill_tps"]),
                    "decode_tps": float(r["decode_tps"]),
                }
    return by


B = load("262144 ctx")   # grey: the 256K run
A = load("131072 ctx")   # gold: the 131K run
depths = sorted(set(B) & set(A))
assert len(depths) == 3, "need all three shared depths"

xs = [B[d]["ptok"] for d in depths]
pre_b = [B[d]["prefill_tps"] for d in depths]
pre_a = [A[d]["prefill_tps"] for d in depths]
dec_b = [B[d]["decode_tps"] for d in depths]
dec_a = [A[d]["decode_tps"] for d in depths]
pre_pct = [100.0 * (a - b) / b for b, a in zip(pre_b, pre_a)]
dec_pct = [100.0 * (a - b) / b for b, a in zip(dec_b, dec_a)]
pre_mean = sum(pre_pct) / len(pre_pct)
dec_mean = sum(dec_pct) / len(dec_pct)


def pct(v):
    s = "{:+.1f}".format(v)
    if s in ("+0.0", "-0.0"):
        s = "0.0"
    return s + "%"


fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)

# ------------------------------------------------------------------ header ---
fig.text(0.055, 0.965, "AJ-IQ2_XXS: 256K vs 131K context", color=INK,
         fontsize=38, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.902, "GLM-5.3-Flash \u00b7 aj9o9's AJ-IQ2_XXS \u00b7 same rig, same depths \u00b7 grey: 256K, gold: 131K \u00b7 "
                       "no MTP block \u2014 drafting off \u00b7 three runs per side, means",
         color=INK_DIM, fontsize=16.5, fontfamily=SANS, va="top")
fig.text(0.965, 0.965, "Project Maya v1.1.13  \u00b7  sm_70  \u00b7  CUDA 12.9  \u00b7  2026-10-16",
         color=INK_DIM, fontsize=13, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------------- tiles ---
axt = fig.add_axes([0.055, 0.735, 0.91, 0.125])
axt.set_xlim(0, 1)
axt.set_ylim(0, 1)
axt.axis("off")
tiles = [
    ("Decode @ 100K", "{:.1f} \u2192 {:.1f}".format(dec_b[-1], dec_a[-1]), "tok/s \u00b7 " + pct(dec_pct[-1]), True),
    ("Decode mean change", pct(dec_mean), "20K\u2013100K across three depths", False),
    ("Prefill @ 100K", "{:,.0f} \u2192 {:,.0f}".format(pre_b[-1], pre_a[-1]), "tok/s \u00b7 " + pct(pre_pct[-1]), False),
    ("Prefill mean change", pct(pre_mean), "20K\u2013100K across three depths", False),
    ("Test scope", "3 depths", "400 gen tokens, 3 runs each", False),
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


def series_plot(ax, ys_b, ys_a, title, sub):
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
    # grey below its points, gold above - the parity-safe offsets
    fmt_b = (lambda v: "%.1f" % v) if max(ys_b) < 100 else (lambda v: "{:,.0f}".format(v))
    fmt_a = (lambda v: "%.1f" % v) if max(ys_a) < 100 else (lambda v: "{:,.0f}".format(v))
    for xv, yb_, ya_ in zip(xs, ys_b, ys_a):
        ax.annotate(fmt_b(yb_), (xv, yb_), xytext=(0, -21), textcoords="offset points",
                    ha="center", color=INK_DIM, fontsize=11, fontfamily=MONO)
        ax.annotate(fmt_a(ya_), (xv, ya_), xytext=(0, 16), textcoords="offset points",
                    ha="center", color=ACCENT, fontsize=11, fontfamily=MONO)
    ax.set_xticks([20000, 60000, 100000])
    ax.set_xticklabels(["20K", "60K", "100K"])
    ax.tick_params(colors=INK_DIM, labelsize=11.5, length=0)
    for lbl in ax.get_xticklabels():
        lbl.set_fontfamily(MONO)
    ax.set_yticks([])
    ax.set_xlim(0, 110000)
    lo = min(min(ys_b), min(ys_a))
    hi = max(max(ys_b), max(ys_a))
    ax.set_ylim(lo * 0.72, hi * 1.30)
    ax.set_title(title, color=INK, fontsize=18, fontfamily=DISPLAY, loc="left", pad=26)
    ax.annotate(sub, xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=12,
                fontfamily=SANS, va="bottom")


axd = fig.add_axes([0.055, 0.455, 0.60, 0.215])
series_plot(axd, dec_b, dec_a, "Token Generation Speed by Depth",
            "decode tokens per second \u00b7 grey: 256K, gold: 131K \u00b7 shaded: gain")
axp = fig.add_axes([0.055, 0.13, 0.60, 0.215])
series_plot(axp, pre_b, pre_a, "Prompt Processing Speed by Depth",
            "prompt tokens per second \u00b7 grey: 256K, gold: 131K \u00b7 shaded: gain")

# ----------------------------------------------------------------- sidebar ---
axs = fig.add_axes([0.678, 0.13, 0.287, 0.54])
axs.set_xlim(0, 1)
axs.set_ylim(0, 1)
axs.axis("off")
axs.add_patch(Rectangle((0, 0), 1, 1, facecolor=CARD, edgecolor=RULE, lw=1.0, clip_on=False))
axs.text(0.055, 0.955, "Change by Depth", color=INK, fontsize=18, fontfamily=DISPLAY, va="center")
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
axs.text(0.055, y, "Absolute @ 100K", color=INK_DIM, fontsize=12, fontfamily=SANS, va="center")
y -= 0.052
axs.text(0.055, y, "decode   {:.1f} \u2192 {:.1f}".format(dec_b[-1], dec_a[-1]), color=INK,
         fontsize=12.5, fontfamily=MONO, va="center")
y -= 0.052
axs.text(0.055, y, "prefill  {:,.0f} \u2192 {:,.0f}".format(pre_b[-1], pre_a[-1]), color=INK,
         fontsize=12.5, fontfamily=MONO, va="center")

# ----------------------------------------------------------------- footer ----
fig.add_artist(plt.Line2D([0.055, 0.965], [0.098, 0.098], color=RULE, lw=1))
fig.text(0.055, 0.068, "Only the context length differs (262,144 vs 131,072); same quant file, same rig, same three "
                       "documents, same day, three fresh-load runs per side, means shown.",
         color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")
fig.text(0.055, 0.040, "raw: model-bench runs on box .5, 2026-10-16 \u00b7 256K: r1\u2013r3 (1411Z\u20131453Z) \u00b7 "
                       "131K: r1\u2013r3 (1516Z\u20131531Z), mean shown.",
         color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")
fig.text(0.965, 0.040, "decode {} mean \u00b7 prefill {} mean".format(pct(dec_mean), pct(pre_mean)),
         color=ACCENT, fontsize=12.5, fontfamily=SANS, ha="right", va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
print("decode mean {} \u00b7 prefill mean {}".format(pct(dec_mean), pct(pre_mean)))
