#!/usr/bin/env python3
"""Posting chart: Maya-XS vs the last Maya DeepSeek test (Maya-S, 21 Oct) on box .5, 128k.

Every number is read from compare.csv (built from the two averages.csv sets).
Same card design as the single-quant charts: header, tiles, two line panels, delta sidebar, footer.
"""
import csv, json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import font_manager

BASE = pathlib.Path(__file__).resolve().parent.parent
OUT = BASE / "charts" / "ds4-maya-xs-vs-maya-s-128k-v100.png"

BG, INK, DIM = "#15130F", "#EDE5D8", "#9A9184"
ACCENT, QUIET, RULE = "#D8A73C", "#8C8578", "#332E27"


def pick(cands, fallback):
    have = {f.name for f in font_manager.fontManager.ttflist}
    return next((c for c in cands if c in have), fallback)


DISPLAY = pick(["Liberation Sans Narrow", "Nimbus Sans Narrow"], "DejaVu Sans")
SANS = pick(["Liberation Sans"], "DejaVu Sans")
MONO = pick(["DejaVu Sans Mono"], "monospace")

rows = list(csv.DictReader(open(BASE / "data" / "csv" / "compare.csv")))
facts = json.load(open(BASE / "data" / "csv" / "facts.json")) if (BASE / "data" / "csv" / "facts.json").exists() else {}
depths = [int(r["depth"]) for r in rows]
s_pre = [float(r["s_prefill"]) for r in rows]
x_pre = [float(r["xs_prefill"]) for r in rows]
s_dec = [float(r["s_decode"]) for r in rows]
x_dec = [float(r["xs_decode"]) for r in rows]
s_pre_m, x_pre_m = sum(s_pre) / len(s_pre), sum(x_pre) / len(x_pre)
s_dec_m, x_dec_m = sum(s_dec) / len(s_dec), sum(x_dec) / len(x_dec)
pre_ratio, dec_ratio = x_pre_m / s_pre_m, x_dec_m / s_dec_m


def kfmt(d):
    return "%dK" % round(d / 1000)


fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)

# ---------------- header ----------------
fig.text(0.055, 0.958, "BOX .5  ·  2× TESLA V100 32 GB  ·  128K CONTEXT", color=DIM,
         fontsize=12.5, fontfamily=MONO, va="top")
fig.text(0.055, 0.912, "Maya-XS vs Maya-S on DeepSeek-V4.1-Flash", color=INK, fontsize=40,
         fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.848, "the 1.6-bit quant on the same two cards: prompts %.2f× faster, answers %.2f× faster"
         % (pre_ratio, dec_ratio), color=ACCENT, fontsize=19, fontfamily=SANS, va="top")
fig.text(0.965, 0.952, "today  · Maya v1.1.22 · Maya-XS IQ1_S", color=DIM, fontsize=12.5, fontfamily=MONO, ha="right")
fig.text(0.965, 0.922, "21 Oct  · Maya v1.1.19 · Maya-S IQ2_XXS", color=DIM, fontsize=12.5, fontfamily=MONO, ha="right")
fig.text(0.965, 0.892, "131,072 tokens of context", color=DIM, fontsize=12.5, fontfamily=MONO, ha="right")

# ---------------- stat tiles ----------------
tiles = [
    ("Prefill speedup", "%.2f×" % pre_ratio, "mean · 3 depths"),
    ("Decode speedup", "%.2f×" % dec_ratio, "mean · 3 depths"),
    ("Maya-XS prefill", "%.0f" % x_pre_m, "tok/s · 3 depths"),
    ("Maya-XS decode", "%.1f" % x_dec_m, "tok/s · 3 depths"),
    ("Test scope", "3 depths", "400 generated tokens each"),
]
tax = fig.add_axes([0.055, 0.678, 0.91, 0.122])
tax.set_xlim(0, 1); tax.set_ylim(0, 1); tax.axis("off")
n = len(tiles); gap = 0.012; w = (1 - gap * (n - 1)) / n
for i, (lab, val, sub) in enumerate(tiles):
    x0 = i * (w + gap)
    tax.add_patch(Rectangle((x0, 0), w, 1, facecolor="none", edgecolor=RULE, lw=1.1))
    tax.text(x0 + 0.018, 0.80, lab.upper(), color=DIM, fontsize=11, fontfamily=MONO, va="center")
    tax.text(x0 + 0.018, 0.47, val, color=INK, fontsize=30, fontfamily=DISPLAY, va="center")
    tax.text(x0 + 0.018, 0.17, sub, color=DIM, fontsize=10.5, fontfamily=MONO, va="center")

# ---------------- panels ----------------
def panel(rect, before, after, title, subtitle, ymax, ty, sy):
    ax = fig.add_axes(rect)
    ax.set_facecolor(BG)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(axis="x", colors=DIM, labelsize=12.5, length=0, pad=5)
    ax.set_yticks([])
    x = list(range(len(depths)))
    ax.fill_between(x, before, after, color=ACCENT, alpha=0.10, lw=0, zorder=1)
    ax.plot(x, before, color=QUIET, lw=2.4, marker="o", ms=7, mfc=BG, mec=QUIET, mew=2.0, zorder=3)
    ax.plot(x, after, color=ACCENT, lw=2.8, marker="o", ms=8, mfc=BG, mec=ACCENT, mew=2.2, zorder=4)
    for xi, v in zip(x, before):
        ax.text(xi, v - ymax * 0.055, "%.1f" % v, color=QUIET, fontsize=14,
                fontfamily=MONO, ha="center", va="top", zorder=5)
    for xi, v in zip(x, after):
        ax.text(xi, v + ymax * 0.055, "%.1f" % v, color=INK, fontsize=15,
                fontfamily=MONO, ha="center", va="bottom", zorder=5)
    ax.set_ylim(0, ymax)
    ax.set_xlim(-0.42, len(depths) - 0.58)
    ax.set_xticks(x)
    ax.set_xticklabels([kfmt(d) for d in depths], fontfamily=MONO)
    fig.text(rect[0], ty, title, color=INK, fontsize=17, fontfamily=DISPLAY, va="top")
    fig.text(rect[0], sy, subtitle, color=DIM, fontsize=12, fontfamily=SANS, va="top")
    return ax


panel([0.055, 0.435, 0.60, 0.165], s_pre, x_pre, "Prefill — prompt read speed",
      "grey: Maya-S (21 Oct, v1.1.19) · gold: Maya-XS (today, v1.1.22) · a 2-card layer split on both · mean of 2 runs",
      max(x_pre) * 1.42, 0.640, 0.607)
panel([0.055, 0.150, 0.60, 0.165], s_dec, x_dec, "Decode — answer speed",
      "grey: Maya-S (21 Oct, v1.1.19) · gold: Maya-XS (today, v1.1.22) · a 2-card layer split on both · mean of 2 runs",
      max(x_dec) * 1.55, 0.355, 0.322)

# ---------------- sidebar ----------------
sax = fig.add_axes([0.705, 0.150, 0.26, 0.49])
sax.set_facecolor(BG); sax.set_xlim(0, 1); sax.set_ylim(0, 1); sax.axis("off")
sax.add_patch(Rectangle((0, 0), 1, 1, facecolor="none", edgecolor=RULE, lw=1.1))
sax.text(0.06, 0.93, "SPEEDUP BY DEPTH", color=DIM, fontsize=11, fontfamily=MONO)
sax.text(0.06, 0.85, "depth", color=DIM, fontsize=11.5, fontfamily=MONO)
sax.text(0.52, 0.85, "prefill", color=DIM, fontsize=11.5, fontfamily=MONO, ha="right")
sax.text(0.94, 0.85, "decode", color=DIM, fontsize=11.5, fontfamily=MONO, ha="right")
y = 0.76
for r in rows:
    sax.text(0.06, y, kfmt(int(r["depth"])), color=INK, fontsize=15, fontfamily=MONO)
    for col, key in ((0.52, "prefill_ratio"), (0.94, "decode_ratio")):
        v = float(r[key])
        sax.text(col, y, "%.2f×" % v, color=ACCENT if v >= 1 else QUIET, fontsize=15,
                 fontfamily=MONO, ha="right")
    y -= 0.105
sax.plot([0.06, 0.94], [0.40, 0.40], color=RULE, lw=1.0)
sax.text(0.06, 0.345, "mean", color=DIM, fontsize=12, fontfamily=SANS)
sax.text(0.52, 0.345, "%.2f×" % pre_ratio, color=INK, fontsize=13, fontfamily=MONO, ha="right")
sax.text(0.94, 0.345, "%.2f×" % dec_ratio, color=INK, fontsize=13, fontfamily=MONO, ha="right")
fact_rows = [
    ("prefill mean, S → XS", "%.1f → %.1f tok/s" % (s_pre_m, x_pre_m)),
    ("decode mean, S → XS", "%.1f → %.1f tok/s" % (s_dec_m, x_dec_m)),
    ("weights on disk", "339 → 277 GB"),
    ("VRAM", facts.get("vram", "32 GB per card")),
    ("experts on CPU lane", facts.get("cpu_lane_experts", "-")),
]
y = 0.275
for lab, val in fact_rows:
    sax.text(0.06, y, lab, color=DIM, fontsize=11.5, fontfamily=SANS)
    sax.text(0.94, y, val, color=INK, fontsize=12.5, fontfamily=MONO, ha="right")
    y -= 0.058

# ---------------- footer ----------------
fig.lines.append(plt.Line2D([0.055, 0.965], [0.072, 0.072], color=RULE, lw=1.0, transform=fig.transFigure))
fig.text(0.055, 0.048, facts.get("cmp_footer1", "Maya-XS: 2 runs today · Maya-S: 2 runs 21 Oct 2026 · gen 400 · temp 0.5 · seed 12345 · exact tokenizer"),
         color=ACCENT, fontsize=12, fontfamily=SANS)
fig.text(0.055, 0.020, facts.get("cmp_footer2", "Maya-S was not re-run today: its quant was deleted before the update, so the delta also carries v1.1.19 → v1.1.22"),
         color=DIM, fontsize=11.5, fontfamily=SANS)

fig.savefig(OUT, facecolor=BG, dpi=150)
print("wrote", OUT)
