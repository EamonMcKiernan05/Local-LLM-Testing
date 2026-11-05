#!/usr/bin/env python3
"""The posting card for the Mia EXL3 2.9 bpw depth battery (2-run means, 20K-100K)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chartlib as C

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = C.load([os.path.join(HERE, "data/csv/means.csv")])

e0, e60, e100 = C.series(rows, "exl3", "suf0", "prefill")
f0, f60, f100 = C.series(rows, "exl3", "suf0", "decode")

C.card(
    rows, "exl3",
    "Mia EXL3 2.9 bpw on 2\u00d7 V100",
    "DeepSeek-V4.1-Flash \u00b7 EQ v1 trellis, mul1 codebook \u00b7 128K context \u00b7 2\u00d7 V100 32 GB + 31 GB RAM",
    "Proj\u0065ct Maya  \u00b7  sm_70 (legacy EXL3 kernels)  \u00b7  CUDA 12.9  \u00b7  2026-11-05",
    os.path.join(HERE, "charts", "ds4-mia-exl3-29bpw-128k-v100.png"),
    [("GPU", "2\u00d7 Tesla V100 32 GB"),
     ("System RAM", "31 GB"),
     ("Model", "EXL3 EAQ v1 2.9 bpw"),
     ("Weights on disk", "210.7 GB"),
     ("Engram table", "203.1 GB (FP8)"),
     ("Context", "128K (131,072)"),
     ("Tensor parallel", "2/2 per GPU"),
     ("CPU lane threads", "20 (calibrated)"),
     ("Experts in VRAM", "7,670 of 15,360"),
     ("Drafter", "DSpark off (3.3 vs 5.0)")],
    [("Context window", "128K", "131,072 tokens max", False),
     ("Prefill @ 100K", "{:,.0f} tok/s".format(e100), "drafting off", False),
     ("Decode @ 100K", "{:.1f} tok/s".format(f100), "drafting off", True),
     ("Tensor parallel", "2/2", "real TP, both cards", False),
     ("Arms measured", "2 \u00d7 2", "4 runs, 12 cells", False)],
    "Decode {:.1f}\u2013{:.1f} tok/s and prefill {:,.0f}\u2013{:,.0f} tok/s across 20K\u2013100K depths.".format(
        min(f0, f60, f100), max(f0, f60, f100), min(e0, e60, e100), max(e0, e60, e100)),
)
