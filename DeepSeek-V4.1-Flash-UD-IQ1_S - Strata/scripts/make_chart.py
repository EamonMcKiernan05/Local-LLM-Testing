#!/usr/bin/env python3
"""Depth card for a backfilled dataset. The constants block at the top is the only per-folder edit.

Reads ../data/csv/averages.csv (engine,arm,depth_k,runs,prefill_mean/min/max,decode_mean/min/max,gen,ptok)
and renders one line per arm on two panels (prefill, decode), 0-based y, every point labelled.
"""
import csv
import os
import sys

from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chartlib as C

# ---------------------------------------------------------------- per-folder constants
TITLE = "Strata 0.2.9 on UD-IQ1_S"
SUBTITLE = "DeepSeek-V4.1-Flash-1017 \u00b7 128K context \u00b7 2\u00d7 V100 32 GB + 31 GB RAM \u00b7 no drafter (the set has no MTP head)"
META = "Strata 0.2.9  \u00b7  sm_70  \u00b7  CUDA 12.9  \u00b7  2026-10-31"
OUT = "charts/ds4-udiq1s-strata-128k-v100.png"
# the two arms cross: the tuned config reads faster and writes slower, so the higher line at
# each depth gets its labels above it and the lower line gets them below - no collisions.
PREFILL_FMT = "{:,.0f}"
SERIES = [("strata", "opt", "tuned", "accent", False),
          ("strata", "default", "as shipped", "pale", True)]
SIDEBAR = [("GPU", "2\u00d7 Tesla V100 32 GB"),
           ("System RAM", "31 GB"),
           ("Model", "UD-IQ1_S (284.6 GB)"),
           ("Context", "128K (131,072)"),
           ("Engine", "Strata 0.2.9"),
           ("Tensor parallel", "2 \u2192 1 (layer split)"),
           ("Drafter", "none (no MTP head)"),
           ("Depths", "20K / 60K / 100K"),
           ("Runs", "2, one per config")]
ACCENT_LINE = "Tuning buys prefill and pays decode: 422 \u2192 553 \u2192 601 tok/s against 361 \u2192 397 \u2192 382, but decode falls 10.2 \u2192 8.1."
NOTE_LINE = "one run per config, fresh load each \u00b7 400 tokens per depth \u00b7 temperature 0.5, fixed seed \u00b7 model-bench on box .5"
# --------------------------------------------------------------------------------------

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(HERE, "data/csv/averages.csv"), encoding="utf-8-sig")))
for r in rows:
    r["depth_k"] = int(r["depth_k"])
    r["prefill_mean"] = float(r["prefill_mean"])
    r["decode_mean"] = float(r["decode_mean"])
    r["runs"] = int(r["runs"])

depths = sorted({r["depth_k"] for r in rows})
gen = rows[0]["gen"]
tones = {"accent": C.ACCENT, "pale": C.SECOND}
xpos = list(range(len(depths)))


def ys(engine, arm, key):
    out = []
    for d in depths:
        v = [r for r in rows if r["engine"] == engine and r["arm"] == arm and r["depth_k"] == d]
        assert v, (engine, arm, d)
        out.append(float(v[0][key]))
    return out


fig = C.plt.figure(figsize=(16, 10), dpi=150, facecolor=C.BG)
C.frame(fig, TITLE, SUBTITLE, META)

axt = fig.add_axes([0.055, 0.735, 0.91, 0.125])
axt.set_xlim(0, 1)
axt.set_ylim(0, 1)
axt.axis("off")
e0, a0, l0 = SERIES[0][0], SERIES[0][1], SERIES[0][2]
last = depths[-1]
C.tiles(axt, [
    ("Prefill @ {:,}K".format(last // 1000), "{:,.0f} tok/s".format(ys(e0, a0, "prefill_mean")[-1]), l0, False),
    ("Decode @ {:,}K".format(last // 1000), "{:.1f} tok/s".format(ys(e0, a0, "decode_mean")[-1]), l0, True),
    ("Depths", str(len(depths)), "{}K to {}K".format(depths[0] // 1000, last // 1000), False),
    ("Generated", "{} tok".format(gen), "per depth per run", False),
    ("Series", str(len(SERIES)), "measured, 0 failed", False),
])


def panel(ax):
    ax.set_facecolor(C.BG)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor="none",
                           edgecolor=C.RULE, lw=1.0, clip_on=False, zorder=0))
    ax.set_xticks(xpos)
    ax.set_xticklabels(["{}K".format(d // 1000) for d in depths])
    ax.tick_params(colors=C.INK_DIM, labelsize=11.5, length=0)
    for lbl in ax.get_xticklabels():
        lbl.set_fontfamily(C.MONO)
    ax.set_yticks([])
    ax.set_xlim(-0.35, len(depths) - 0.65)


axp = fig.add_axes([0.055, 0.44, 0.60, 0.22])
panel(axp)
axd = fig.add_axes([0.055, 0.13, 0.60, 0.21])
panel(axd)

def draw_panel(ax, key, fmt):
    """Labels go above the HIGHEST line at each depth and below the rest, so two series that
    cross still read as two columns of numbers instead of overprinting each other."""
    pairs = [(s, ys(s[0], s[1], key)) for s in SERIES]
    order = sorted(pairs, key=lambda t: -sum(t[1]) / len(t[1]))
    for rank, (s, vals) in enumerate(order):
        tone = tones[s[3]]
        above = rank == 0
        ax.plot(xpos, vals, color=tone, lw=2.4, zorder=4)
        ax.plot(xpos, vals, "o", color=tone, ms=6.5, markeredgecolor=C.BG, markeredgewidth=1.4, zorder=5)
        for x, y in zip(xpos, vals):
            ax.annotate(fmt.format(y), (x, y), xytext=(0, 14 if above else -22), textcoords="offset points",
                        ha="center", color=C.INK_DIM, fontsize=11, fontfamily=C.MONO)


draw_panel(axp, "prefill_mean", PREFILL_FMT)
draw_panel(axd, "decode_mean", "{:.1f}")

axp.set_ylim(0, max(max(ys(e, a, "prefill_mean")) for e, a, *_ in SERIES) * 1.32)
axd.set_ylim(0, max(max(ys(e, a, "decode_mean")) for e, a, *_ in SERIES) * 1.38)

key = " \u00b7 ".join("{}: {}".format(s[2], "gold" if s[3] == "accent" else "pale") for s in SERIES)
axp.set_title("Prompt Processing Speed by Depth", color=C.INK, fontsize=18, fontfamily=C.DISPLAY, loc="left", pad=26)
axp.annotate("mean of each arm's runs per point" + (" \u00b7 " + key if len(SERIES) > 1 else ""),
             xy=(0, 1.02), xycoords="axes fraction", color=C.INK_DIM, fontsize=11.5, fontfamily=C.SANS, va="bottom")
axd.set_title("Token Generation Speed by Depth", color=C.INK, fontsize=18, fontfamily=C.DISPLAY, loc="left", pad=26)
axd.annotate("decode tokens per second after each prompt \u00b7 {} tokens generated per run".format(gen),
             xy=(0, 1.02), xycoords="axes fraction", color=C.INK_DIM, fontsize=11.5, fontfamily=C.SANS, va="bottom")

C.sidebar(fig.add_axes([0.678, 0.13, 0.287, 0.53]), "Benchmark Summary", SIDEBAR)
C.footer(fig, ACCENT_LINE, NOTE_LINE)
out = os.path.join(HERE, OUT)
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, facecolor=C.BG)
C.plt.close(fig)
print("wrote", out)
