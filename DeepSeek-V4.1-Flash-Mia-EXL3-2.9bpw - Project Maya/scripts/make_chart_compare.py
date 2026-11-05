#!/usr/bin/env python3
"""The comparison card: unsloth UD-IQ1_S against Mia EXL3 2.9 bpw, same box, same prompts.

Reads this folder's means.csv and the sibling UD-IQ1_S folder's, so both series are
drawn from the same published record.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chartlib as C

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIBLING = os.path.join(os.path.dirname(HERE), "DeepSeek-V4.1-Flash-UD-IQ1_S - Project Maya")

rows = C.load([os.path.join(HERE, "data/csv/means.csv"), os.path.join(SIBLING, "data/csv/means.csv")])

gp = C.series(rows, "gguf", "suf0", "prefill")
ep = C.series(rows, "exl3", "suf0", "prefill")
gd = C.series(rows, "gguf", "suf0", "decode")
ed = C.series(rows, "exl3", "suf0", "decode")

C.compare(
    rows,
    os.path.join(HERE, "charts", "ds4-udiq1s-vs-mia-exl3-128k-v100.png"),
    "IQ1_S vs EXL3 2.9 bpw",
    "same model, same box, same prompts \u00b7 128K context \u00b7 2\u00d7 Tesla V100 32 GB + 31 GB RAM",
    "Proj\u0065ct Maya  \u00b7  sm_70  \u00b7  CUDA 12.9  \u00b7  2026-11-05",
    [("Prefill ratio @ 100K", "{:.2f}\u00d7".format(gp[2] / ep[2]), "IQ1_S / EXL3", False),
     ("Decode ratio @ 100K", "{:.2f}\u00d7".format(gd[2] / ed[2]), "IQ1_S / EXL3", True),
     ("IQ1_S prefill", "{:,.0f} tok/s".format(gp[2]), "at 100K depth", False),
     ("IQ1_S decode", "{:.1f} tok/s".format(gd[2]), "at 100K depth", False),
     ("EXL3 decode", "{:.1f} tok/s".format(ed[2]), "at 100K depth", False)],
    [("GPU", "2\u00d7 Tesla V100 32 GB"),
     ("System RAM", "31 GB"),
     ("IQ1_S size", "284.6 GB"),
     ("EXL3 size", "413.7 GB"),
     ("IQ1_S TP", "1/1 per GPU"),
     ("EXL3 TP", "2/2 per GPU"),
     ("IQ1_S experts in VRAM", "6,448"),
     ("EXL3 experts in VRAM", "7,670"),
     ("Experts on the CPU lane", "8,918 / 11,525"),
     ("Expert lane on CPU", "67 / 148 GB")],
    "UD-IQ1_S is {:.2f}\u00d7 faster at reading prompts and {:.2f}\u00d7 faster at writing, at 100K depth.".format(
        gp[2] / ep[2], gd[2] / ed[2]),
    "both calibrated by Maya's own tuner, DSpark off, prompt-lookup drafting off \u00b7 "
    "identical prompts (same tokenizer file) \u00b7 2 fresh loads per arm \u00b7 temperature 0.5, fixed seed",
)
