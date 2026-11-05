#!/usr/bin/env python3
"""House card renderer for the Stage E DeepSeek batch (box .5, 2x V100, 128K).

Reads data/csv/means.csv (one row per run per depth) and renders either a single
model file's depth card or the two-file comparison card. Palette, layout and the
verification loop are the house ones:
benchmark-results-publishing -> references/social-chart-recipe.md ("Report-card variant").
"""
import csv
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

BG = "#15130F"
CARD = "#1A1712"
INK = "#EDE5D8"
INK_DIM = "#9A9184"
ACCENT = "#D8A73C"
SECOND = "#C9BFAE"
FILL = "#585147"
RULE = "#332E27"
DEPTHS = [20000, 60000, 100000]


def pick(cands, fallback):
    have = {f.name for f in font_manager.fontManager.ttflist}
    for c in cands:
        if c in have:
            return c
    return fallback


DISPLAY = pick(["Franklin Gothic Demi Cond", "Franklin Gothic Medium Cond"], "DejaVu Sans")
SANS = pick(["Franklin Gothic Book", "Gill Sans MT", "Segoe UI"], "DejaVu Sans")
MONO = pick(["Consolas", "Cascadia Mono", "DejaVu Sans Mono"], "DejaVu Sans Mono")


def load(paths):
    rows = []
    for p in paths:
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            r["depth"] = int(r["depth"])
            r["prefill"] = float(r["prefill"])
            r["decode"] = float(r["decode"])
            rows.append(r)
    return rows


def series(rows, side, arm, key):
    return [st.mean([r[key] for r in rows if r["side"] == side and r["arm"] == arm and r["depth"] == d])
            for d in DEPTHS]


def frame(fig, title, subtitle, meta):
    fig.text(0.055, 0.965, title, color=INK, fontsize=30, fontfamily=DISPLAY, va="top")
    fig.text(0.055, 0.900, subtitle, color=INK_DIM, fontsize=15.5, fontfamily=SANS, va="top")
    fig.text(0.965, 0.965, meta, color=INK_DIM, fontsize=12.5, fontfamily=MONO, ha="right", va="top")


def tiles(axt, items):
    gap = 0.018
    tw = (1.0 - 4 * gap) / 5.0
    for i, (label, val, sub, hi) in enumerate(items):
        x0 = i * (tw + gap)
        axt.add_patch(Rectangle((x0, 0), tw, 1, facecolor=CARD,
                                edgecolor=ACCENT if hi else RULE, lw=1.6 if hi else 1.0, clip_on=False))
        axt.text(x0 + 0.011, 0.80, label, color=INK_DIM, fontsize=12.5, fontfamily=SANS, va="center")
        axt.text(x0 + 0.011, 0.42, val, color=INK, fontsize=21, fontfamily=MONO, va="center")
        if sub:
            axt.text(x0 + 0.011, 0.15, sub, color=INK_DIM, fontsize=11, fontfamily=MONO, va="center")


def panel(ax):
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor="none",
                           edgecolor=RULE, lw=1.0, clip_on=False, zorder=0))
    ax.set_xticks([0] + DEPTHS)
    ax.set_xticklabels(["0", "20K", "60K", "100K"])
    ax.tick_params(colors=INK_DIM, labelsize=11.5, length=0)
    for lbl in ax.get_xticklabels():
        lbl.set_fontfamily(MONO)
    ax.set_yticks([])
    ax.set_xlim(0, 112000)


def draw(ax, ys, colour, above=True, fmt="{:,.0f}", hi_last=True):
    ax.plot(DEPTHS, ys, color=colour, lw=2.4, zorder=4)
    ax.plot(DEPTHS, ys, "o", color=colour, ms=6.5, markeredgecolor=BG, markeredgewidth=1.4, zorder=5)
    for k, (x, y) in enumerate(zip(DEPTHS, ys)):
        ax.annotate(fmt.format(y), (x, y), xytext=(0, 14 if above else -22), textcoords="offset points",
                    ha="center", color=colour if (hi_last and k == len(ys) - 1) else INK_DIM,
                    fontsize=11, fontfamily=MONO)


def sidebar(ax, heading, srows):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor=CARD, edgecolor=RULE, lw=1.0, clip_on=False))
    ax.text(0.055, 0.945, heading, color=INK, fontsize=18, fontfamily=DISPLAY, va="center")
    ax.add_patch(Rectangle((0.055, 0.90), 0.89, 0.0018, facecolor=RULE, clip_on=False))
    y = 0.845
    for lab, val in srows:
        ax.text(0.055, y, lab, color=INK_DIM, fontsize=12, fontfamily=SANS, va="center")
        ax.text(0.945, y, val, color=INK, fontsize=12, fontfamily=MONO, ha="right", va="center")
        y -= 0.079


def footer(fig, accent_line, note_line):
    fig.add_artist(plt.Line2D([0.055, 0.965], [0.105, 0.105], color=RULE, lw=1))
    fig.text(0.055, 0.075, accent_line, color=ACCENT, fontsize=13, fontfamily=SANS, va="bottom")
    fig.text(0.055, 0.042, note_line, color=INK_DIM, fontsize=11, fontfamily=SANS, va="bottom")


def card(rows, side, title, subtitle, meta, out, side_rows, tile_items, note):
    fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)
    frame(fig, title, subtitle, meta)
    axt = fig.add_axes([0.055, 0.735, 0.91, 0.125])
    axt.set_xlim(0, 1)
    axt.set_ylim(0, 1)
    axt.axis("off")
    tiles(axt, tile_items)

    pre_off, pre_on = series(rows, side, "suf0", "prefill"), series(rows, side, "suf3", "prefill")
    dec_off, dec_on = series(rows, side, "suf0", "decode"), series(rows, side, "suf3", "decode")

    axp = fig.add_axes([0.055, 0.44, 0.60, 0.22])
    panel(axp)
    draw(axp, pre_off, ACCENT)
    draw(axp, pre_on, SECOND, above=False, hi_last=False)
    axp.set_ylim(0, max(pre_off + pre_on) * 1.32)
    axp.set_title("Prompt Processing Speed by Depth", color=INK, fontsize=18, fontfamily=DISPLAY, loc="left", pad=26)
    axp.annotate("mean of 2 runs per point \u00b7 gold above the line: drafting off \u00b7 pale below: drafting on",
                 xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")

    axd = fig.add_axes([0.055, 0.13, 0.60, 0.21])
    panel(axd)
    draw(axd, dec_off, ACCENT, fmt="{:.1f}")
    draw(axd, dec_on, SECOND, above=False, hi_last=False, fmt="{:.1f}")
    axd.set_ylim(0, max(dec_off + dec_on) * 1.38)
    axd.set_title("Token Generation Speed by Depth", color=INK, fontsize=18, fontfamily=DISPLAY, loc="left", pad=26)
    axd.annotate("decode tokens per second \u00b7 400 tokens generated per run \u00b7 gold above: drafting off",
                 xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")

    sidebar(fig.add_axes([0.678, 0.13, 0.287, 0.53]), "Benchmark Summary", side_rows)
    footer(fig, note, "128K context \u00b7 temperature 0.5, fixed seed \u00b7 model-bench on box .5 \u00b7 "
                      "Maya v1.1.53 \u00b7 2 fresh loads per arm")
    fig.savefig(out, facecolor=BG)
    plt.close(fig)
    print("wrote", out)


def compare(rows, out, title, subtitle, meta, tile_items, side_rows, accent_line, note_line):
    fig = plt.figure(figsize=(16, 10), dpi=150, facecolor=BG)
    frame(fig, title, subtitle, meta)
    axt = fig.add_axes([0.055, 0.735, 0.91, 0.125])
    axt.set_xlim(0, 1)
    axt.set_ylim(0, 1)
    axt.axis("off")
    tiles(axt, tile_items)

    gp = series(rows, "gguf", "suf0", "prefill")
    ep = series(rows, "exl3", "suf0", "prefill")
    axp = fig.add_axes([0.055, 0.44, 0.60, 0.22])
    panel(axp)
    draw(axp, gp, ACCENT)
    draw(axp, ep, SECOND, above=False, hi_last=False)
    axp.set_ylim(0, max(gp) * 1.32)
    axp.set_title("Prompt Processing Speed by Depth", color=INK, fontsize=18, fontfamily=DISPLAY, loc="left", pad=26)
    axp.annotate("mean of 2 runs per point \u00b7 gold above the line: UD-IQ1_S \u00b7 pale below: EXL3 2.9 bpw",
                 xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")

    gd = series(rows, "gguf", "suf0", "decode")
    ed = series(rows, "exl3", "suf0", "decode")
    axd = fig.add_axes([0.055, 0.13, 0.60, 0.21])
    panel(axd)
    draw(axd, gd, ACCENT, fmt="{:.1f}")
    draw(axd, ed, SECOND, above=False, hi_last=False, fmt="{:.1f}")
    axd.set_ylim(0, max(gd) * 1.38)
    axd.set_title("Token Generation Speed by Depth", color=INK, fontsize=18, fontfamily=DISPLAY, loc="left", pad=26)
    axd.annotate("decode tokens per second \u00b7 400 tokens generated per run \u00b7 gold: UD-IQ1_S \u00b7 pale: EXL3",
                 xy=(0, 1.02), xycoords="axes fraction", color=INK_DIM, fontsize=11.5, fontfamily=SANS, va="bottom")

    sidebar(fig.add_axes([0.678, 0.13, 0.287, 0.53]), "Benchmark Summary", side_rows)
    footer(fig, accent_line, note_line)
    fig.savefig(out, facecolor=BG)
    plt.close(fig)
    print("wrote", out)
