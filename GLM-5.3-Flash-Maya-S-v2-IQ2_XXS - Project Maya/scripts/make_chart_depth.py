#!/usr/bin/env python3
"""Maya depth report card — stat tiles / prefill curve / decode curve / sidebar / footer
in the flat grey-gold house design. Values parsed from data/csv/depth-64k-v109.csv
(model-bench run 2026-10-08T1000Z-maya-s-v2-64k-v109, box .5, 64K context, Project Maya v1.0.9).
Re-issue of the card posted on 2026-10-07: same layout, the v1.0.9 numbers.
Output: charts/maya-v100-64k-depth.png
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "csv", "depth-64k-v109.csv")
OUT = os.path.join(HERE, "..", "charts", "maya-v100-64k-depth.png")

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
run_id = ""
with open(SRC, encoding="utf-8-sig") as fh:
    for r in csv.DictReader(fh):
        run_id = r.get("run_id", run_id)
        by_depth[int(r["depth_k"])] = {
            "ptok": int(r["ptok"]),
            "prefill_tps": float(r["prefill_tps"]),
            "decode_tps": float(r["decode_tps"]),
            "gpu0_used_mib": int(r["gpu0_used_mib"]),
            "gpu1_used_mib": int(r["gpu1_used_mib"]),
        }

rows = sorted(by_depth.values(), key=lambda r: r["ptok"])
d20, d60 = rows[0], rows[-1]
xs = [r["ptok"] for r in rows]
pre_ys = [r["prefill_tps"] for r in rows]
dec_ys = [r["decode_tps"] for r in rows]
pf_min, pf_max = min(pre_ys), max(pre_ys)
dec_min, dec_max = min(dec_ys), max(dec_ys)

g0 = d60["gpu0_used_mib"] / 1024.0
g1 = d60["gpu1_used_mib"] / 1024.0
ctx_pct = 100.0 * d60["ptok"] / 65536.0

fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)

# ------------------------------------------------------------------ header ---
fig.text(0.055, 0.965, "GLM-5.3-Flash on 2\u00d7 Tesla V100", color=INK,
         fontsize=38, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.902, "Maya-S IQ2_XXS \u00b7 321B MoE, ~18B active \u00b7 96.5 GB \u00b7 64K context \u00b7 "
                       "2\u00d7 V100 32 GB + 30 GB RAM",
         color=INK_DIM, fontsize=16.5, fontfamily=SANS, va="top")
fig.text(0.965, 0.965, "Project Maya v1.0.9  \u00b7  sm_70  \u00b7  CUDA 12.9  \u00b7  2026-10-08",
         color=INK_DIM, fontsize=13, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------------- tiles ---
axt = fig.add_axes([0.055, 0.735, 0.91, 0.125])
axt.set_xlim(0, 1)
axt.set_ylim(0, 1)
axt.axis("off")
tiles = [
    ("Context window", "64K", "65,536 tokens max", False),
    ("Prefill @ 60K depth", "{:,.0f} tok/s".format(d60["prefill_tps"]), "", False),
    ("Decode @ 60K depth", "{:.1f} tok/s".format(d60["decode_tps"]), "", True),
    ("VRAM in use", "{:.1f} / {:.1f} GB".format(g0, g1), "GPU0 / GPU1 of 32 GB", False),
    ("Context used", "{:,} / 64K".format(d60["ptok"]), "{:.1f}% of 64K".format(ctx_pct), False),
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
    if i == 4:
        bar_x = x0 + 0.011
        bar_w = tw - 0.022
        axt.add_patch(Rectangle((bar_x, 0.14), bar_w, 0.13, facecolor=RULE, clip_on=False))
        axt.add_patch(Rectangle((bar_x, 0.14), bar_w * ctx_pct / 100.0, 0.13, facecolor=ACCENT, clip_on=False))
    elif sub:
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
axp.set_xticks([0, 20000, 40000, 60000])
axp.set_xticklabels(["0", "20K", "40K", "60K"])
axp.tick_params(colors=INK_DIM, labelsize=11.5, length=0)
for lbl in axp.get_xticklabels():
    lbl.set_fontfamily(MONO)
axp.set_yticks([])
axp.set_xlim(0, 66000)
axp.set_ylim(0, max(pre_ys) * 1.30)
axp.set_title("Prompt Processing Speed by Depth", color=INK, fontsize=18, fontfamily=DISPLAY,
              loc="left", pad=26)
axp.annotate("average tokens per second per run \u00b7 exact-token slices, one text per depth",
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
axd.set_xticks([0, 20000, 40000, 60000])
axd.set_xticklabels(["0", "20K", "40K", "60K"])
axd.tick_params(colors=INK_DIM, labelsize=11.5, length=0)
for lbl in axd.get_xticklabels():
    lbl.set_fontfamily(MONO)
axd.set_yticks([])
axd.set_xlim(0, 66000)
axd.set_ylim(0, max(dec_ys) * 1.35)
axd.set_title("Token Generation Speed by Depth", color=INK, fontsize=18, fontfamily=DISPLAY,
              loc="left", pad=26)
axd.annotate("decode tokens per second after each prompt \u00b7 400 tokens generated per run",
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
    ("Model", "Maya-S IQ2_XXS (GLM-5.3-Flash)"),
    ("Context", "64K (65,536)"),
    ("Decode @ 20K", "{:.1f} tok/s".format(d20["decode_tps"])),
    ("Decode @ 60K", "{:.1f} tok/s".format(d60["decode_tps"])),
    ("Prefill @ 20K", "{:,.0f} tok/s".format(d20["prefill_tps"])),
    ("Prefill @ 60K", "{:,.0f} tok/s".format(d60["prefill_tps"])),
    ("VRAM @ 60K", "{:.1f} / {:.1f} GB".format(g0, g1)),
]
y = 0.855
for lab, val in srows:
    axs.text(0.055, y, lab, color=INK_DIM, fontsize=12.5, fontfamily=SANS, va="center")
    axs.text(0.945, y, val, color=INK, fontsize=13, fontfamily=MONO, ha="right", va="center")
    y -= 0.084

# ----------------------------------------------------------------- footer ----
fig.add_artist(plt.Line2D([0.055, 0.965], [0.105, 0.105], color=RULE, lw=1))
fig.text(0.055, 0.075, "Decode {:,.1f}\u2013{:,.1f} tok/s and prefill {:,.0f}\u2013{:,.0f} tok/s across "
                       "20K\u201360K-token depths.".format(dec_min, dec_max, pf_min, pf_max),
         color=ACCENT, fontsize=13.5, fontfamily=SANS, va="bottom")
fig.text(0.055, 0.042, "64K context \u00b7 temperature 0.5, fixed seed \u00b7 one run per depth \u00b7 "
                       "raw: model-bench run " + run_id + " on box .5",
         color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
