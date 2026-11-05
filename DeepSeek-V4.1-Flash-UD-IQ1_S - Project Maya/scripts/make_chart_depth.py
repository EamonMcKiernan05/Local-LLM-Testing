#!/usr/bin/env python3
"""The posting card for the UD-IQ1_S depth battery (2-run means, 20K-100K)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chartlib as C

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = C.load([os.path.join(HERE, "data/csv/means.csv")])

g0, g60, g100 = C.series(rows, "gguf", "suf0", "prefill")
d0, d60, d100 = C.series(rows, "gguf", "suf0", "decode")

C.card(
    rows, "gguf",
    "UD-IQ1_S on 2\u00d7 V100",
    "DeepSeek-V4.1-Flash \u00b7 1-bit experts + Q6_K Engram \u00b7 128K context \u00b7 2\u00d7 V100 32 GB + 31 GB RAM",
    "Proj\u0065ct Maya  \u00b7  sm_70  \u00b7  CUDA 12.9  \u00b7  2026-11-05",
    os.path.join(HERE, "charts", "ds4-udiq1s-128k-v100.png"),
    [("GPU", "2\u00d7 Tesla V100 32 GB"),
     ("System RAM", "31 GB"),
     ("Model", "UD-IQ1_S (unsloth)"),
     ("Weights on disk", "123.4 GB"),
     ("Engram table", "161.3 GB"),
     ("Context", "128K (131,072)"),
     ("Tensor parallel", "1/1 per GPU"),
     ("CPU lane threads", "20 (calibrated)"),
     ("Experts in VRAM", "6,448 of 15,360"),
     ("Drafter", "DSpark off")],
    [("Context window", "128K", "131,072 tokens max", False),
     ("Prefill @ 100K", "{:,.0f} tok/s".format(g100), "drafting off", False),
     ("Decode @ 100K", "{:.1f} tok/s".format(d100), "drafting off", True),
     ("Prefill @ 20K", "{:,.0f} tok/s".format(g0), "shallow-prompt cell", False),
     ("Arms measured", "2 \u00d7 2", "4 runs, 12 cells", False)],
    "Decode {:.1f}\u2013{:.1f} tok/s and prefill {:,.0f}\u2013{:,.0f} tok/s across 20K\u2013100K depths.".format(
        min(d0, d60, d100), max(d0, d60, d100), min(g0, g60, g100), max(g0, g60, g100)),
)
