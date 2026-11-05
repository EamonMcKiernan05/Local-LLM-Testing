#!/usr/bin/env python3
"""The posting card for the 2026-11-01 engine pair: Maya v1.1.45 against Strata 0.2.9.

Both engines, same model file (unsloth UD-IQ1_S), same 128K context, same fastest config,
drafter OFF (the arm the battery recommended). Drafter-on arms are in data/csv/averages.csv.
"""
import csv
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chartlib as C

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "data/csv/means.csv")
OUT = os.path.join(HERE, "charts", "ds4-udiq1s-maya-vs-strata-128k-v100.png")

rows = []
for r in csv.DictReader(open(SRC, encoding="utf-8-sig")):
    r["depth"] = int(r["depth"])
    r["prefill"] = float(r["prefill"])
    r["decode"] = float(r["decode"])
    rows.append(r)


def series(engine, arm, key):
    return [st.mean([r[key] for r in rows if r["engine"] == engine and r["arm"] == arm and r["depth"] == d])
            for d in C.DEPTHS]


mp, md = series("maya", "dsparkoff", "prefill"), series("maya", "dsparkoff", "decode")
sp, sd = series("strata", "dsparkoff", "prefill"), series("strata", "dsparkoff", "decode")

fig = C.plt.figure(figsize=(16, 10), dpi=150, facecolor=C.BG)
C.frame(fig, "Maya vs Strata on 2\u00d7 V100",
        "DeepSeek-V4.1-Flash-1017 UD-IQ1_S \u00b7 128K context \u00b7 2\u00d7 Tesla V100 32 GB + 31 GB RAM \u00b7 drafter off on both",
        "Maya v1.1.45  vs  Strata 0.2.9  \u00b7  sm_70  \u00b7  2026-11-01")

axt = fig.add_axes([0.055, 0.735, 0.91, 0.125])
axt.set_xlim(0, 1)
axt.set_ylim(0, 1)
axt.axis("off")
C.tiles(axt, [
    ("Prefill ratio @ 100K", "{:.2f}\u00d7".format(mp[2] / sp[2]), "Maya / Strata", False),
    ("Decode ratio @ 100K", "{:.2f}\u00d7".format(md[2] / sd[2]), "Maya / Strata", True),
    ("Maya decode", "{:.1f} tok/s".format(md[2]), "at 100K, peaks 60K", False),
    ("Strata decode", "{:.1f} tok/s".format(sd[2]), "at 100K", False),
    ("Runs per arm", "3", "12 runs, 36 cells", False),
])

axp = fig.add_axes([0.055, 0.44, 0.60, 0.22])
C.panel(axp)
C.draw(axp, mp, C.ACCENT)
C.draw(axp, sp, C.SECOND, above=False, hi_last=False)
axp.set_ylim(0, max(mp) * 1.32)
axp.set_title("Prompt Processing Speed by Depth", color=C.INK, fontsize=18, fontfamily=C.DISPLAY, loc="left", pad=26)
axp.annotate("mean of 3 runs per point \u00b7 gold above the line: Maya \u00b7 pale below: Strata",
             xy=(0, 1.02), xycoords="axes fraction", color=C.INK_DIM, fontsize=11.5, fontfamily=C.SANS, va="bottom")

axd = fig.add_axes([0.055, 0.13, 0.60, 0.21])
C.panel(axd)
C.draw(axd, md, C.ACCENT, fmt="{:.1f}")
C.draw(axd, sd, C.SECOND, above=False, hi_last=False, fmt="{:.1f}")
axd.set_ylim(0, max(md) * 1.38)
axd.set_title("Token Generation Speed by Depth", color=C.INK, fontsize=18, fontfamily=C.DISPLAY, loc="left", pad=26)
axd.annotate("decode tokens per second \u00b7 400 tokens generated per run \u00b7 gold: Maya \u00b7 pale: Strata",
             xy=(0, 1.02), xycoords="axes fraction", color=C.INK_DIM, fontsize=11.5, fontfamily=C.SANS, va="bottom")

C.sidebar(fig.add_axes([0.678, 0.13, 0.287, 0.53]), "Benchmark Summary", [
    ("GPU", "2\u00d7 Tesla V100 32 GB"),
    ("System RAM", "31 GB"),
    ("Model file", "UD-IQ1_S"),
    ("Context", "128K (131,072)"),
    ("Maya", "v1.1.45"),
    ("Strata", "0.2.9"),
    ("Config, both", "tuned, 16K chunk"),
    ("Drafter", "off, measured"),
    ("Experts in VRAM", "6,705 of 15,360"),
])

C.footer(fig,
         "Maya wins both axes at every depth \u00b7 decode 10.5 \u2192 16.3 \u2192 11.5 tok/s (peaks at 60K, not monotonic) "
         "against Strata's 7.9 \u2192 8.1 \u2192 8.3.",
         "same model file, same prompts, 3 fresh loads per arm \u00b7 the drafter cost both engines and was measured off \u00b7 "
         "temperature 0.5, fixed seed")
fig.savefig(OUT, facecolor=C.BG)
C.plt.close(fig)
print("wrote", OUT)
