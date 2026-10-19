#!/usr/bin/env python3
"""Strata 0.2.0-beta: the PLE (n-gram) shard on the SATA boot SSD vs the NVMe.
Same engine, same config, same model file, same six documents — one file moved.
Every value parsed from data/csv/ple-location-020-beta.csv.
Output: charts/strata-v100-020-ple-location.png
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "csv", "ple-location-020-beta.csv")
OUT = os.path.join(HERE, "..", "charts", "strata-v100-020-ple-location.png")

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


DISPLAY = pick(["Franklin Gothic Demi Cond", "Franklin Gothic Medium Cond", "Liberation Sans Narrow", "Nimbus Sans Narrow"], "DejaVu Sans")
SANS = pick(["Franklin Gothic Book", "Gill Sans MT", "Segoe UI", "Liberation Sans"], "DejaVu Sans")
MONO = pick(["Consolas", "Cascadia Mono", "DejaVu Sans Mono"], "DejaVu Sans Mono")


def load(config):
    by = {}
    with open(SRC, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["config"] == config:
                by[int(r["depth_k"])] = {
                    "ptok": int(r["ptok"]),
                    "prefill_tps": float(r["prefill_tps"]),
                }
    return by


B = load("PLE on SATA SSD")
A = load("PLE on NVMe")
depths = sorted(set(B) & set(A))
assert len(depths) == 6, "need all six depths in both configs"

xs = [A[d]["ptok"] for d in depths]
pre_b = [B[d]["prefill_tps"] for d in depths]
pre_a = [A[d]["prefill_tps"] for d in depths]
pre_pct = [100.0 * (a - b) / b for b, a in zip(pre_b, pre_a)]
pre_mean = sum(pre_pct) / len(pre_pct)


def pct(v):
    s = "{:+.1f}".format(v)
    if s in ("+0.0", "-0.0"):
        s = "0.0"
    return s + "%"


fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)

# ------------------------------------------------------------------ header ---
fig.text(0.055, 0.965, "Strata 0.2.0-beta \u00b7 Where the PLE Table Lives", color=INK,
         fontsize=38, fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.902, "Qwen 3.8 Flash base IQ3_S \u00b7 2\u00d7 Tesla V100 32 GB \u00b7 same engine, config and documents \u00b7 "
                       "grey: PLE on SATA, gold: PLE on NVMe",
         color=INK_DIM, fontsize=16.5, fontfamily=SANS, va="top")
fig.text(0.965, 0.965, "model-bench  \u00b7  CUDA 12.9  \u00b7  sm_70  \u00b7  2026-10-19",
         color=INK_DIM, fontsize=13, fontfamily=MONO, ha="right", va="top")

# ------------------------------------------------------------------- tiles ---
axt = fig.add_axes([0.055, 0.735, 0.91, 0.125])
axt.set_xlim(0, 1)
axt.set_ylim(0, 1)
axt.axis("off")
tiles = [
    ("Prefill mean gain", pct(pre_mean), "20K \u2013 250K, six depths", True),
    ("Prefill @ 250K", "{:,.0f} \u2192 {:,.0f}".format(pre_b[-1], pre_a[-1]), "tok/s \u00b7 " + pct(pre_pct[-1]), False),
    ("PLE read probe", "10,447 \u2192 76,986", "rows per second \u00b7 7.4\u00d7", False),
    ("The variable", "1 file", "28.8 GB PLE shard moved", False),
    ("Test scope", "6 depths", "one pass per side", False),
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

# ----------------------------------------------------------- prefill panel ---
ax = fig.add_axes([0.055, 0.175, 0.60, 0.44])
ax.set_facecolor(BG)
for s in ax.spines.values():
    s.set_visible(False)
ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor="none",
                       edgecolor=RULE, lw=1.0, clip_on=False, zorder=0))
ax.fill_between(xs, pre_b, pre_a, color=ACCENT, alpha=0.10, zorder=2)
ax.plot(xs, pre_b, color=BEFORE, lw=2.2, zorder=4)
ax.plot(xs, pre_a, color=AFTER, lw=2.6, zorder=5)
ax.plot(xs, pre_b, "o", color=BEFORE, ms=5.5, markeredgecolor=BG, markeredgewidth=1.2, zorder=4)
ax.plot(xs, pre_a, "o", color=AFTER, ms=6.5, markeredgecolor=BG, markeredgewidth=1.4, zorder=6)
ax.annotate("{:,.0f}".format(pre_b[0]), (xs[0], pre_b[0]), xytext=(-18, -26), textcoords="offset points",
            ha="center", color=INK_DIM, fontsize=11, fontfamily=MONO)
ax.annotate("{:,.0f}".format(pre_a[0]), (xs[0], pre_a[0]), xytext=(0, 16), textcoords="offset points",
            ha="center", color=ACCENT, fontsize=11, fontfamily=MONO)
ax.annotate("{:,.0f}".format(pre_b[-1]), (xs[-1], pre_b[-1]), xytext=(18, -20), textcoords="offset points",
            ha="center", color=INK_DIM, fontsize=11, fontfamily=MONO)
ax.annotate("{:,.0f}".format(pre_a[-1]), (xs[-1], pre_a[-1]), xytext=(0, 20), textcoords="offset points",
            ha="center", color=ACCENT, fontsize=11, fontfamily=MONO)
ax.set_xticks([0, 50000, 100000, 150000, 200000, 250000])
ax.set_xticklabels(["0", "50K", "100K", "150K", "200K", "250K"])
ax.tick_params(colors=INK_DIM, labelsize=11.5, length=0)
for lbl in ax.get_xticklabels():
    lbl.set_fontfamily(MONO)
ax.set_yticks([])
ax.set_xlim(0, 268000)
lo = min(min(pre_b), min(pre_a))
hi = max(max(pre_b), max(pre_a))
ax.set_ylim(lo * 0.72, hi * 1.30)
ax.set_title("Prompt Processing Speed by Depth", color=INK, fontsize=18, fontfamily=DISPLAY, loc="left", pad=26)
ax.annotate("prompt tokens per second \u00b7 grey line: PLE on the SATA SSD (as served), gold line: PLE on the NVMe \u00b7 shaded: gain",
            xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=12,
            fontfamily=SANS, va="bottom")

# ----------------------------------------------------------------- sidebar ---
axs = fig.add_axes([0.678, 0.175, 0.287, 0.44])
axs.set_xlim(0, 1)
axs.set_ylim(0, 1)
axs.axis("off")
axs.add_patch(Rectangle((0, 0), 1, 1, facecolor=CARD, edgecolor=RULE, lw=1.0, clip_on=False))
axs.text(0.055, 0.945, "Gain by Depth", color=INK, fontsize=18, fontfamily=DISPLAY, va="center")
axs.add_patch(Rectangle((0.055, 0.905), 0.89, 0.0018, facecolor=RULE, clip_on=False))
axs.text(0.055, 0.855, "depth", color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="center")
axs.text(0.72, 0.855, "prefill", color=INK_DIM, fontsize=11.5, fontfamily=SANS, ha="center", va="center")
y = 0.775
for i, d in enumerate(depths):
    axs.text(0.055, y, "{}K".format(d // 1000), color=INK, fontsize=13, fontfamily=MONO, va="center")
    axs.text(0.72, y, pct(pre_pct[i]), color=ACCENT, fontsize=13, fontfamily=MONO, ha="center", va="center")
    y -= 0.068
axs.add_patch(Rectangle((0.055, y + 0.030), 0.89, 0.0018, facecolor=RULE, clip_on=False))
y -= 0.012
axs.text(0.055, y, "mean", color=INK_DIM, fontsize=13, fontfamily=SANS, va="center")
axs.text(0.72, y, pct(pre_mean), color=ACCENT, fontsize=13.5, fontfamily=MONO, ha="center", va="center")
y -= 0.095
axs.text(0.055, y, "Absolute @ 250K", color=INK_DIM, fontsize=12, fontfamily=SANS, va="center")
y -= 0.055
axs.text(0.055, y, "prefill  {:,.0f} \u2192 {:,.0f}".format(pre_b[-1], pre_a[-1]), color=INK,
         fontsize=12.5, fontfamily=MONO, va="center")

# ----------------------------------------------------------------- footer ----
fig.add_artist(plt.Line2D([0.055, 0.965], [0.098, 0.098], color=RULE, lw=1))
fig.text(0.055, 0.068, "The 28.8 GB PLE shard moved from the SATA boot SSD to the NVMe: 0.2.0's 4 KiB random reads run 7.4\u00d7 "
                       "faster there (engine probe). Decode unchanged; prefill is the I/O-bound stage.",
         color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")
fig.text(0.055, 0.040, "raw: model-bench runs 2026-10-19 T1556/T1607/T1618Z (SATA) vs T1627Z (NVMe) \u00b7 box .5.",
         color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")
fig.text(0.965, 0.040, "prefill {} mean".format(pct(pre_mean)),
         color=ACCENT, fontsize=12.5, fontfamily=SANS, ha="right", va="bottom")

fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
