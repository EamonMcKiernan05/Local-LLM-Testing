#!/usr/bin/env python3
"""Posting chart: DeepSeek-V4.1-Flash-1017 (Maya-XS) speed on box .5, 128k context.

Every number is read from averages.csv (built from the two model-bench runs).
Same card as the Maya-S one (2026-10-21): header, tiles, two line panels, sidebar, footer.
"""
import csv, json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import font_manager

BASE = pathlib.Path(__file__).resolve().parent.parent
OUT = BASE / "charts" / "ds4-maya-xs-128k-v100.png"

BG, INK, DIM = "#15130F", "#EDE5D8", "#9A9184"
ACCENT, QUIET, RULE = "#D8A73C", "#585147", "#332E27"


def pick(cands, fallback):
    have = {f.name for f in font_manager.fontManager.ttflist}
    return next((c for c in cands if c in have), fallback)


DISPLAY = pick(["Liberation Sans Narrow", "Nimbus Sans Narrow"], "DejaVu Sans")
SANS = pick(["Liberation Sans"], "DejaVu Sans")
MONO = pick(["DejaVu Sans Mono"], "monospace")

rows = list(csv.DictReader(open(BASE / "data" / "csv" / "averages.csv")))
depths = [int(r["depth"]) for r in rows]
pre = [float(r["prefill_mean"]) for r in rows]
dec = [float(r["decode_mean"]) for r in rows]
pre_peak = max(float(r["prefill_peak"]) for r in rows)
dec_peak = max(float(r["decode_peak"]) for r in rows)
pre_peak_d = max(rows, key=lambda r: float(r["prefill_peak"]))["depth"]
dec_peak_d = max(rows, key=lambda r: float(r["decode_peak"]))["depth"]
pre_mean = sum(pre) / len(pre)
dec_mean = sum(dec) / len(dec)
vram0_mib = max(int(r["gpu0_used_mib"]) for r in rows)
vram1_mib = max(int(r["gpu1_used_mib"]) for r in rows)
facts = json.load(open(BASE / "data" / "csv" / "facts.json")) if (BASE / "data" / "csv" / "facts.json").exists() else {}


def kfmt(d):
    return "%dK" % round(d / 1000)


fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)

# ---------------- header ----------------
fig.text(0.055, 0.958, "BOX .5  ·  2× TESLA V100 32 GB  ·  128K CONTEXT", color=DIM,
         fontsize=12.5, fontfamily=MONO, va="top")
fig.text(0.055, 0.912, "DeepSeek-V4.1-Flash-1017 on Maya", color=INK, fontsize=40,
         fontfamily=DISPLAY, va="top")
fig.text(0.055, 0.848, "prefill %.0f–%.0f tok/s out to a 100K prompt; decode %.1f–%.1f tok/s"
         % (min(pre), max(pre), min(dec), max(dec)),
         color=ACCENT, fontsize=19, fontfamily=SANS, va="top")
fig.text(0.965, 0.952, "Maya v1.1.22 · maya-ds4", color=DIM, fontsize=12.5, fontfamily=MONO, ha="right")
fig.text(0.965, 0.922, "Maya-XS IQ1_S · 277 GB", color=DIM, fontsize=12.5, fontfamily=MONO, ha="right")
fig.text(0.965, 0.892, "131,072 tokens of context", color=DIM, fontsize=12.5, fontfamily=MONO, ha="right")

# ---------------- stat tiles ----------------
tiles = [
    ("Prefill peak", "%.1f" % pre_peak, "tok/s · %s prompt" % kfmt(int(pre_peak_d))),
    ("Decode peak", "%.1f" % dec_peak, "tok/s · %s prompt" % kfmt(int(dec_peak_d))),
    ("Prefill mean", "%.1f" % pre_mean, "tok/s · 3 depths"),
    ("Decode mean", "%.1f" % dec_mean, "tok/s · 3 depths"),
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
def panel(rect, vals, title, subtitle, ymax, ty, sy):
    ax = fig.add_axes(rect)
    ax.set_facecolor(BG)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(axis="x", colors=DIM, labelsize=12.5, length=0, pad=5)
    ax.set_yticks([])
    x = list(range(len(depths)))
    ax.plot(x, vals, color=ACCENT, lw=2.8, marker="o", ms=8, mfc=BG, mec=ACCENT, mew=2.2, zorder=3)
    for xi, v in zip(x, vals):
        ax.text(xi, v + ymax * 0.055, "%.1f" % v, color=INK, fontsize=15,
                fontfamily=MONO, ha="center", va="bottom", zorder=5)
    ax.set_ylim(0, ymax)
    ax.set_xlim(-0.42, len(depths) - 0.58)
    ax.set_xticks(x)
    ax.set_xticklabels([kfmt(d) for d in depths], fontfamily=MONO)
    fig.text(rect[0], ty, title, color=INK, fontsize=17, fontfamily=DISPLAY, va="top")
    fig.text(rect[0], sy, subtitle, color=DIM, fontsize=12, fontfamily=SANS, va="top")
    return ax


panel([0.055, 0.435, 0.60, 0.165], pre, "Prefill — prompt read speed",
      "tokens per second · line is the mean of 2 runs", max(pre) * 1.35, 0.640, 0.607)
panel([0.055, 0.150, 0.60, 0.165], dec, "Decode — answer speed",
      "tokens per second · line is the mean of 2 runs", max(dec) * 1.55, 0.355, 0.322)

# ---------------- sidebar ----------------
sax = fig.add_axes([0.705, 0.150, 0.26, 0.49])
sax.set_facecolor(BG); sax.set_xlim(0, 1); sax.set_ylim(0, 1); sax.axis("off")
sax.add_patch(Rectangle((0, 0), 1, 1, facecolor="none", edgecolor=RULE, lw=1.1))
sax.text(0.06, 0.93, "AVERAGE OF 2 RUNS", color=DIM, fontsize=11, fontfamily=MONO)
sax.text(0.06, 0.85, "depth", color=DIM, fontsize=11.5, fontfamily=MONO)
sax.text(0.52, 0.85, "prefill", color=DIM, fontsize=11.5, fontfamily=MONO, ha="right")
sax.text(0.94, 0.85, "decode", color=DIM, fontsize=11.5, fontfamily=MONO, ha="right")
y = 0.76
for r in rows:
    sax.text(0.06, y, kfmt(int(r["depth"])), color=INK, fontsize=15, fontfamily=MONO)
    sax.text(0.52, y, "%.1f" % float(r["prefill_mean"]), color=INK, fontsize=15, fontfamily=MONO, ha="right")
    sax.text(0.94, y, "%.1f" % float(r["decode_mean"]), color=INK, fontsize=15, fontfamily=MONO, ha="right")
    y -= 0.105
sax.plot([0.06, 0.94], [0.40, 0.40], color=RULE, lw=1.0)
fact_rows = [
    ("peak prefill", "%.1f tok/s" % pre_peak),
    ("peak decode", "%.1f tok/s" % dec_peak),
    ("run spread, prefill", "%.1f–%.1f%%" % (min(float(r["prefill_spread_pct"]) for r in rows),
                                             max(float(r["prefill_spread_pct"]) for r in rows))),
    ("run spread, decode", "%.0f–%.0f%%" % (min(float(r["decode_spread_pct"]) for r in rows),
                                            max(float(r["decode_spread_pct"]) for r in rows))),
    ("VRAM used per card", "%d / %d MiB" % (vram0_mib, vram1_mib)),
    ("experts on CPU lane", facts.get("cpu_lane_experts", "-")),
]
y = 0.33
for lab, val in fact_rows:
    sax.text(0.06, y, lab, color=DIM, fontsize=11.5, fontfamily=SANS)
    sax.text(0.94, y, val, color=INK, fontsize=12.5, fontfamily=MONO, ha="right")
    y -= 0.058

# ---------------- footer ----------------
fig.lines.append(plt.Line2D([0.055, 0.965], [0.072, 0.072], color=RULE, lw=1.0, transform=fig.transFigure))
fig.text(0.055, 0.048, facts.get("footer1", "2 runs averaged · warm-up burn excluded · gen 400 · temp 0.5 · seed 12345 · exact tokenizer"),
         color=ACCENT, fontsize=12, fontfamily=SANS)
fig.text(0.055, 0.020, facts.get("footer2", "model-bench on box .5 · tensor parallel across both V100s · single stream, one request at a time"),
         color=DIM, fontsize=11.5, fontfamily=SANS)

fig.savefig(OUT, facecolor=BG, dpi=150)
print("wrote", OUT)
