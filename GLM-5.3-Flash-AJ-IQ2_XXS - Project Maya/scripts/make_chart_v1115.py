#!/usr/bin/env python3
"""AJ-IQ2_XXS depth report card - 262,144 ctx, SN730, Project Maya v1.1.15 - stat tiles / prefill curve /
decode curve / sidebar / footer in the flat grey-gold house design. Values parsed from data/chartdata-256k-v1115.csv
(model-bench runs 2026-10-17, three fresh-load runs, mean shown; box .5, model set on the SN730 NVMe, no MTP block).
Output: aj-iq2xxs-256k-v1115.png
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "csv", "depth-aj-v1115.csv")
OUT = os.path.join(HERE, "..", "charts", "aj-iq2xxs-256k-v1115.png")

BG = "#15130F"
CARD = "#1A1712"
INK = "#EDE5D8"
INK_DIM = "#9A9184"
ACCENT = "#D8A73C"
LINE = "#9A9184"
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

by_depth = {}
with open(SRC, encoding="utf-8-sig") as fh:
    for r in csv.DictReader(fh):
        by_depth[int(r["depth_k"])] = {
            "ptok": int(r["ptok"]),
            "prefill_tps": float(r["prefill_tps"]),
            "decode_tps": float(r["decode_tps"]),
        }

rows = sorted(by_depth.values(), key=lambda r: r["ptok"])
d20, d250 = rows[0], rows[-1]
xs = [r["ptok"] for r in rows]
pre_ys = [r["prefill_tps"] for r in rows]
dec_ys = [r["decode_tps"] for r in rows]
pf_min, pf_max = min(pre_ys), max(pre_ys)
dec_min, dec_max = min(dec_ys), max(dec_ys)
pf_pk = round(rows[pre_ys.index(pf_max)]["ptok"] / 1000)
dec_pk = round(rows[dec_ys.index(dec_max)]["ptok"] / 1000)

fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)

# ------------------------------------------------------------------ header ---
fig.text(0.055, 0.965, "GLM-5.3-Flash on 2\u00d7 Tesla V100", color=INK,
         fontsize=38, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.902, "aj9o9's AJ-IQ2_XXS \u00b7 87.4 GB, 2.23 bpw \u00b7 262,144 context \u00b7 "
                       "no MTP block \u2014 drafting off \u00b7 mean of three fresh-load runs",
         color=INK_DIM, fontsize=16.5, fontfamily=SANS, va="top")
fig.text(0.965, 0.965, "Project Maya v1.1.15  \u00b7  sm_70  \u00b7  CUDA 12.9  \u00b7  2026-10-17",
         color=INK_DIM, fontsize=13, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------------- tiles ---
axt = fig.add_axes([0.055, 0.735, 0.91, 0.125])
axt.set_xlim(0, 1)
axt.set_ylim(0, 1)
axt.axis("off")
tiles = [
    ("Context window", "256K", "262,144 tokens max", False),
    ("Prefill peak (mean)", "{:,.0f} tok/s".format(pf_max), "at {}K depth".format(pf_pk), False),
    ("Decode peak (mean)", "{:.1f} tok/s".format(dec_max), "at {}K depth".format(dec_pk), True),
    ("Quant size", "87.4 GB", "2.23 bpw \u00b7 two shards", False),
    ("Test scope", "6 depths", "400 generated tokens each", False),
]
gap = 0.018
tw = (1.0 - 4 * gap) / 5.0
for i, (label, val, sub, hi) in enumerate(tiles):
    x0 = i * (tw + gap)
    axt.add_patch(Rectangle((x0, 0), tw, 1, facecolor=CARD,
                            edgecolor=ACCENT if hi else RULE, lw=1.6 if hi else 1.0,
                            clip_on=False))
    axt.text(x0 + 0.011, 0.82, label, color=INK_DIM, fontsize=12.5, fontfamily=SANS, va="center")
    axt.text(x0 + 0.011, 0.42, val, color=INK, fontsize=23, fontfamily=MONO, va="center")
    if sub:
        axt.text(x0 + 0.011, 0.16, sub, color=INK_DIM, fontsize=11.5, fontfamily=MONO, va="center")

# ------------------------------------------------ prompt processing curve ----
axp = fig.add_axes([0.055, 0.44, 0.60, 0.22])
axp.set_facecolor(BG)
for s in axp.spines.values():
    s.set_visible(False)
axp.add_patch(Rectangle((0, 0), 1, 1, transform=axp.transAxes, facecolor="none",
                        edgecolor=RULE, lw=1.0, clip_on=False, zorder=0))
axp.plot(xs, pre_ys, color=LINE, lw=2.4, zorder=4)
axp.fill_between(xs, [0] * len(xs), pre_ys, color=FILL, alpha=0.30, zorder=2)
axp.plot(xs, pre_ys, "o", color=ACCENT, ms=6.5, markeredgecolor=BG, markeredgewidth=1.4, zorder=5)
for k, (x, y) in enumerate(zip(xs, pre_ys)):
    dy = (14, -21, 14)[k % 3]
    axp.annotate("{:,.0f}".format(y), (x, y), xytext=(0, dy), textcoords="offset points",
                 ha="center", color=ACCENT if k == len(xs) - 1 else INK_DIM,
                 fontsize=11, fontfamily=MONO)
axp.set_xticks([20000, 60000, 100000, 150000, 200000, 250000])
axp.set_xticklabels(["20K", "60K", "100K", "150K", "200K", "250K"])
axp.tick_params(colors=INK_DIM, labelsize=11.5, length=0)
for lbl in axp.get_xticklabels():
    lbl.set_fontfamily(MONO)
axp.set_yticks([])
axp.set_xlim(0, 262144)
axp.set_ylim(0, max(pre_ys) * 1.30)
axp.set_title("Prompt Processing Speed by Depth", color=INK, fontsize=18, fontfamily=DISPLAY,
              loc="left", pad=26)
axp.annotate("average tokens per second per run \u00b7 exact-token slices, mean of three runs",
             xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=12,
             fontfamily=SANS, va="bottom")

# --------------------------------------------------- decode speed curve -----
axd = fig.add_axes([0.055, 0.13, 0.60, 0.21])
axd.set_facecolor(BG)
for s in axd.spines.values():
    s.set_visible(False)
axd.add_patch(Rectangle((0, 0), 1, 1, transform=axd.transAxes, facecolor="none",
                        edgecolor=RULE, lw=1.0, clip_on=False, zorder=0))
axd.plot(xs, dec_ys, color=LINE, lw=2.4, zorder=4)
axd.fill_between(xs, [0] * len(xs), dec_ys, color=FILL, alpha=0.30, zorder=2)
axd.plot(xs, dec_ys, "o", color=ACCENT, ms=6.5, markeredgecolor=BG, markeredgewidth=1.4, zorder=5)
for k, (x, y) in enumerate(zip(xs, dec_ys)):
    dy = (14, -21, 14)[k % 3]
    axd.annotate("{:.1f}".format(y), (x, y), xytext=(0, dy), textcoords="offset points",
                 ha="center", color=ACCENT if k == len(xs) - 1 else INK_DIM,
                 fontsize=11, fontfamily=MONO)
axd.set_xticks([20000, 60000, 100000, 150000, 200000, 250000])
axd.set_xticklabels(["20K", "60K", "100K", "150K", "200K", "250K"])
axd.tick_params(colors=INK_DIM, labelsize=11.5, length=0)
for lbl in axd.get_xticklabels():
    lbl.set_fontfamily(MONO)
axd.set_yticks([])
axd.set_xlim(0, 262144)
axd.set_ylim(0, max(dec_ys) * 1.35)
axd.set_title("Token Generation Speed by Depth", color=INK, fontsize=18, fontfamily=DISPLAY,
              loc="left", pad=26)
axd.annotate("decode tokens per second after each prompt \u00b7 400 tokens generated per run, mean of three",
             xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=12,
             fontfamily=SANS, va="bottom")

# ----------------------------------------------------------------- sidebar ---
axs = fig.add_axes([0.678, 0.13, 0.287, 0.53])
axs.set_xlim(0, 1)
axs.set_ylim(0, 1)
axs.axis("off")
axs.add_patch(Rectangle((0, 0), 1, 1, facecolor=CARD, edgecolor=RULE, lw=1.0, clip_on=False))
axs.text(0.055, 0.945, "Benchmark Summary", color=INK, fontsize=18, fontfamily=DISPLAY, va="center")
axs.add_patch(Rectangle((0.055, 0.90), 0.89, 0.0018, facecolor=RULE, clip_on=False))
srows = [
    ("GPU", "2\u00d7 Tesla V100 32 GB"),
    ("System RAM", "30 GB"),
    ("Model", "AJ-IQ2_XXS (GLM-5.3-Flash)"),
    ("Context", "256K (262,144)"),
    ("Drafting", "off (no MTP block)"),
    ("Storage", "SN730 NVMe"),
    ("Decode @ 20K", "{:.1f} tok/s".format(d20["decode_tps"])),
    ("Decode @ 250K", "{:.1f} tok/s".format(d250["decode_tps"])),
    ("Prefill @ 20K", "{:,.0f} tok/s".format(d20["prefill_tps"])),
    ("Prefill @ 250K", "{:,.0f} tok/s".format(d250["prefill_tps"])),
]
y = 0.855
for lab, val in srows:
    axs.text(0.055, y, lab, color=INK_DIM, fontsize=12.5, fontfamily=SANS, va="center")
    axs.text(0.945, y, val, color=INK, fontsize=13, fontfamily=MONO, ha="right", va="center")
    y -= 0.076

# ----------------------------------------------------------------- footer ----
fig.add_artist(plt.Line2D([0.055, 0.965], [0.105, 0.105], color=RULE, lw=1))
fig.text(0.055, 0.075, "Decode {:,.1f}\u2013{:,.1f} tok/s and prefill {:,.0f}\u2013{:,.0f} tok/s across "
                       "20K\u2013250K-token depths.".format(dec_min, dec_max, pf_min, pf_max),
         color=ACCENT, fontsize=13.5, fontfamily=SANS, va="bottom")
fig.text(0.055, 0.042, "256K context \u00b7 temperature 0.5, fixed seed \u00b7 three fresh-load runs per depth, "
                       "mean shown \u00b7 raw: model-bench runs 0910Z\u20131032Z, 2026-10-17",
         color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
