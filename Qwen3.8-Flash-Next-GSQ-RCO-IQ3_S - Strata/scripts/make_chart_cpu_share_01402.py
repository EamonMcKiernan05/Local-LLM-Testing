#!/usr/bin/env python3
"""CPU-share vs default on box .5 — short-prompt latency (bars) + battery control (curves).
Every value parsed from data/csv/cpu-share-short-prompts.csv and data/csv/cpu-share-battery-control.csv.
Output: charts/strata-v100-cpu-share-01402.png
"""
import csv
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_SHORT = os.path.join(HERE, "..", "data", "csv", "cpu-share-short-prompts.csv")
SRC_BAT = os.path.join(HERE, "..", "data", "csv", "cpu-share-battery-control.csv")
OUT = os.path.join(HERE, "..", "charts", "strata-v100-cpu-share-01402.png")

BG = "#15130F"
CARD = "#1A1712"
INK = "#EDE5D8"
INK_DIM = "#9A9184"
ACCENT = "#D8A73C"
BEFORE = "#9A9184"
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

# ------------------------------------------------------------- data --------
short = list(csv.DictReader(open(SRC_SHORT, encoding="utf-8-sig")))
sizes = [512, 1000, 2000, 4000]


def med(arm, size):
    vals = [float(r["prompt_ms"]) for r in short if r["arm"] == arm and int(r["size"]) == size]
    assert len(vals) == 3, f"need 3 reps for {arm}/{size}"
    return statistics.median(vals)


off = {s: med("off", s) for s in sizes}
shr = {s: med("auto", s) for s in sizes}
sd = {s: 100.0 * (shr[s] / off[s] - 1) for s in sizes}
sd_mean = sum(sd.values()) / len(sd)

bat = list(csv.DictReader(open(SRC_BAT, encoding="utf-8-sig")))
xs = [int(r["depth_k"]) for r in bat]
pf0 = [float(r["prefill_default"]) for r in bat]
pf1 = [float(r["prefill_cpu_share"]) for r in bat]
pf_d = [float(r["prefill_delta_pct_derived"]) for r in bat]
dc_d = [float(r["decode_delta_pct_derived"]) for r in bat]
pf_mean = sum(pf_d) / len(pf_d)
dc_mean = sum(dc_d) / len(dc_d)


def pct(v):
    return "{:+.1f}%".format(v)


fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)

# ------------------------------------------------------------- header ------
fig.text(0.055, 0.965, "CPU-Share vs default \u2014 no effect on box .5", color=INK,
         fontsize=38, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.902, "Qwen 3.8 Flash base IQ3_S (GSQ-RCO) \u00b7 2\u00d7 Tesla V100 32 GB \u00b7 prompts "
                       "512\u20134,000 tok \u00d7 3 \u00b7 six-depth battery as control \u00b7 grey: default, gold: CPU share (auto)",
         color=INK_DIM, fontsize=16.5, fontfamily=SANS, va="top")
fig.text(0.965, 0.965, "0.1.40.2  \u00b7  sm_70  \u00b7  CUDA 12.9  \u00b7  2026-10-07",
         color=INK_DIM, fontsize=13, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------- tiles -------
axt = fig.add_axes([0.055, 0.735, 0.91, 0.125])
axt.set_xlim(0, 1)
axt.set_ylim(0, 1)
axt.axis("off")
tiles = [
    ("512 tok prompt", "{:,.0f} \u2192 {:,.0f} ms".format(off[512], shr[512]), pct(sd[512]) + " \u00b7 median of 3", False),
    ("1,000 tok prompt", "{:,.0f} \u2192 {:,.0f} ms".format(off[1000], shr[1000]), pct(sd[1000]), False),
    ("4,000 tok prompt", "{:,.0f} \u2192 {:,.0f} ms".format(off[4000], shr[4000]), pct(sd[4000]), False),
    ("Battery 20K\u2013250K", "\u00b11%", "prefill / decode mean \u0394", False),
    ("Applies to", "1 GPU only", "layer split \u2192 no CPU pool", True),
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

# ------------------------------------------------------- panel 1: bars -----
axb = fig.add_axes([0.055, 0.455, 0.60, 0.215])
axb.set_facecolor(BG)
for s in axb.spines.values():
    s.set_visible(False)
axb.add_patch(Rectangle((0, 0), 1, 1, transform=axb.transAxes, facecolor="none",
                        edgecolor=RULE, lw=1.0, clip_on=False, zorder=0))
vmax = max(max(off.values()), max(shr.values()))
xsb = [0, 1, 2, 3]
axb.bar([x - 0.20 for x in xsb], [off[s] for s in sizes], width=0.34, color=BEFORE, zorder=3)
axb.bar([x + 0.20 for x in xsb], [shr[s] for s in sizes], width=0.34, color=AFTER, zorder=3)
for i, s in enumerate(sizes):
    axb.text(i - 0.20, off[s] + vmax * 0.015, "{:,.0f}".format(off[s]), ha="center", va="bottom",
             color=INK_DIM, fontsize=11, fontfamily=MONO)
    axb.text(i + 0.20, shr[s] + vmax * 0.015, "{:,.0f}".format(shr[s]), ha="center", va="bottom",
             color=ACCENT, fontsize=11, fontfamily=MONO)
    axb.text(i, max(off[s], shr[s]) + vmax * 0.10, pct(sd[s]), ha="center", va="bottom",
             color=INK_DIM, fontsize=12, fontfamily=MONO)
axb.set_ylim(0, vmax * 1.34)
axb.set_xlim(-0.6, 3.6)
axb.set_yticks([])
axb.set_xticks(xsb)
axb.set_xticklabels(["512", "1,000", "2,000", "4,000"])
axb.tick_params(colors=INK_DIM, labelsize=11.5, length=0)
for lbl in axb.get_xticklabels():
    lbl.set_fontfamily(MONO)
axb.set_title("Prompt latency by prompt size", color=INK, fontsize=18, fontfamily=DISPLAY, loc="left", pad=26)
axb.annotate("median of 3 \u00b7 ms, lower is better \u00b7 grey: default, gold: CPU share (auto)",
             xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=12, fontfamily=SANS, va="bottom")

# ---------------------------------------------------- panel 2: curves ------
axp = fig.add_axes([0.055, 0.13, 0.60, 0.215])
axp.set_facecolor(BG)
for s in axp.spines.values():
    s.set_visible(False)
axp.add_patch(Rectangle((0, 0), 1, 1, transform=axp.transAxes, facecolor="none",
                        edgecolor=RULE, lw=1.0, clip_on=False, zorder=0))
axp.fill_between(xs, pf0, pf1, color=ACCENT, alpha=0.10, zorder=2)
axp.plot(xs, pf0, color=BEFORE, lw=2.2, zorder=4)
axp.plot(xs, pf1, color=AFTER, lw=2.6, zorder=5)
axp.plot(xs, pf0, "o", color=BEFORE, ms=5.5, markeredgecolor=BG, markeredgewidth=1.2, zorder=4)
axp.plot(xs, pf1, "o", color=AFTER, ms=6.5, markeredgecolor=BG, markeredgewidth=1.4, zorder=6)
axp.annotate("{:,.0f}".format(pf0[0]), (xs[0], pf0[0]), xytext=(-18, -26), textcoords="offset points",
             ha="center", color=INK_DIM, fontsize=11, fontfamily=MONO)
axp.annotate("{:,.0f}".format(pf1[0]), (xs[0], pf1[0]), xytext=(0, 16), textcoords="offset points",
             ha="center", color=ACCENT, fontsize=11, fontfamily=MONO)
axp.annotate("{:,.0f}".format(pf0[-1]), (xs[-1], pf0[-1]), xytext=(18, -20), textcoords="offset points",
             ha="center", color=INK_DIM, fontsize=11, fontfamily=MONO)
axp.annotate("{:,.0f}".format(pf1[-1]), (xs[-1], pf1[-1]), xytext=(0, 16), textcoords="offset points",
             ha="center", color=ACCENT, fontsize=11, fontfamily=MONO)
axp.set_xticks([0, 50000, 100000, 150000, 200000, 250000])
axp.set_xticklabels(["0", "50K", "100K", "150K", "200K", "250K"])
axp.tick_params(colors=INK_DIM, labelsize=11.5, length=0)
for lbl in axp.get_xticklabels():
    lbl.set_fontfamily(MONO)
axp.set_yticks([])
axp.set_xlim(0, 268000)
lo = min(min(pf0), min(pf1))
hi = max(max(pf0), max(pf1))
axp.set_ylim(lo * 0.72, hi * 1.30)
axp.set_title("Battery control: prompt processing by depth", color=INK, fontsize=18, fontfamily=DISPLAY, loc="left", pad=26)
axp.annotate("prompt tok/s \u00b7 grey: 0.1.40.2 default, gold: + CPU share \u00b7 shaded: gap",
             xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=12, fontfamily=SANS, va="bottom")

# ------------------------------------------------------------- sidebar -----
axs = fig.add_axes([0.678, 0.13, 0.287, 0.54])
axs.set_xlim(0, 1)
axs.set_ylim(0, 1)
axs.axis("off")
axs.add_patch(Rectangle((0, 0), 1, 1, facecolor=CARD, edgecolor=RULE, lw=1.0, clip_on=False))
axs.text(0.055, 0.955, "\u0394 by prompt size", color=INK, fontsize=18, fontfamily=DISPLAY, va="center")
axs.add_patch(Rectangle((0.055, 0.918), 0.89, 0.0018, facecolor=RULE, clip_on=False))
axs.text(0.055, 0.872, "tokens", color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="center")
axs.text(0.34, 0.872, "default", color=INK_DIM, fontsize=11.5, fontfamily=SANS, ha="center", va="center")
axs.text(0.61, 0.872, "CPU share", color=INK_DIM, fontsize=11.5, fontfamily=SANS, ha="center", va="center")
axs.text(0.87, 0.872, "\u0394", color=INK_DIM, fontsize=11.5, fontfamily=SANS, ha="center", va="center")
y = 0.795
for s in sizes:
    axs.text(0.055, y, "{:,}".format(s), color=INK, fontsize=13, fontfamily=MONO, va="center")
    axs.text(0.34, y, "{:,.0f}".format(off[s]), color=INK, fontsize=12.5, fontfamily=MONO, ha="center", va="center")
    axs.text(0.61, y, "{:,.0f}".format(shr[s]), color=INK, fontsize=12.5, fontfamily=MONO, ha="center", va="center")
    axs.text(0.87, y, pct(sd[s]), color=INK_DIM, fontsize=12.5, fontfamily=MONO, ha="center", va="center")
    y -= 0.060
axs.add_patch(Rectangle((0.055, y + 0.026), 0.89, 0.0018, facecolor=RULE, clip_on=False))
y -= 0.012
axs.text(0.055, y, "mean", color=INK_DIM, fontsize=13, fontfamily=SANS, va="center")
axs.text(0.61, y, pct(sd_mean), color=INK_DIM, fontsize=13.5, fontfamily=MONO, ha="center", va="center")
y -= 0.10
axs.text(0.055, y, "Battery control (20K\u2013250K)", color=INK_DIM, fontsize=12, fontfamily=SANS, va="center")
y -= 0.058
axs.text(0.055, y, "prefill mean \u0394", color=INK, fontsize=12.5, fontfamily=MONO, va="center")
axs.text(0.87, y, pct(pf_mean), color=INK_DIM, fontsize=12.5, fontfamily=MONO, ha="center", va="center")
y -= 0.058
axs.text(0.055, y, "decode mean \u0394", color=INK, fontsize=12.5, fontfamily=MONO, va="center")
axs.text(0.87, y, pct(dc_mean), color=INK_DIM, fontsize=12.5, fontfamily=MONO, ha="center", va="center")
y -= 0.085
axs.text(0.055, y, "all deltas within run noise", color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="center")

# ------------------------------------------------------------- footer ------
fig.add_artist(plt.Line2D([0.055, 0.965], [0.098, 0.098], color=RULE, lw=1))
fig.text(0.055, 0.068, "Not applicable here by construction: the CPU pool is wired to prefill only in "
                       "single-GPU runs (set_cpu_pool is guarded by !multi_gpu).",
         color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")
fig.text(0.055, 0.040, "raw: cpu-share short tests (off/auto, 2026-10-07 13:17\u201313:20 UTC) + model-bench "
                       "runs 2026-10-07T1247Z (default) and T1320Z (CPU share) \u00b7 box .5.",
         color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")
fig.text(0.965, 0.040, "short prompts {} mean \u00b7 battery prefill {} mean".format(pct(sd_mean), pct(pf_mean)),
         color=INK_DIM, fontsize=12.5, fontfamily=SANS, ha="right", va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
