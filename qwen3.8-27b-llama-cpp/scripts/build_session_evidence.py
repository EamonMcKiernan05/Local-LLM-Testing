#!/usr/bin/env python3
"""
Extract the live-service (production) measurements from the Hermes session
records that captured them.

The inference box was unreachable at collection time, so the live-service
numbers are re-derived from the journal text and tool output preserved in the
session database dumps. Every row carries the timestamp it was logged at and
the source session, so the claim is traceable and nothing is re-measured from
memory.

Input  (session dumps written by the collection step, not shipped):
    scratch/senior_20260815_210812_d226745d.txt   Aug 14-15 live traffic, MTP vs no-MTP
    scratch/senior_20260923_224000_7f00e7.txt     Sep 23 production journal, adopted config
Output:
    data/csv/live-traffic-draft-acceptance-aug14-15.csv
    data/csv/live-service-2026-09-23-prefill-progress.csv
    data/csv/live-service-2026-09-23-decode-series.csv
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.expanduser("~/.hermes/profiles/senior/cache/scratch/qwen")
OUT = os.path.join(HERE, "..", "data", "csv")

AUG = os.path.join(SCRATCH, "senior_20260815_210812_d226745d.txt")
SEP23 = os.path.join(SCRATCH, "senior_20260923_224000_7f00e7.txt")

ACCEPT = re.compile(
    r"(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+eamon-ai llama-server\[(?P<pid>\d+)\]:"
    r".*?draft acceptance = (?P<rate>[\d.]+) \(\s*(?P<acc>\d+) accepted /\s*(?P<gen>\d+) generated\),"
    r" mean len =\s*(?P<mean>[\d.]+)"
)
PP = re.compile(
    r"(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+eamon-ai llama-server\[(?P<pid>\d+)\]:"
    r".*?prompt processing, n_tokens =\s*(?P<n>\d+), progress = (?P<prog>[\d.]+), t = (?P<t>[\d.]+) s"
    r" / (?P<rate>[\d.]+) tokens per second"
)
TG = re.compile(
    r"(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+eamon-ai llama-server\[(?P<pid>\d+)\]:"
    r".*?n_gen =\s*(?P<n>\d+), tg =\s*(?P<tg>[\d.]+) t/s, tg_3s =\s*(?P<tg3>[\d.]+) t/s"
)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def unescape(text):
    return text.replace("\\n", "\n").replace("\\r", "")


def write(name, header, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {name:52s} {len(rows):3d} rows")


def main():
    aug = unescape(read(AUG))
    sep = unescape(read(SEP23))

    # --- Aug 14/15: per-request "draft acceptance" log lines, deduplicated ---
    seen, rows = set(), []
    for m in ACCEPT.finditer(aug):
        key = (m.group("pid"), m.group("ts"))
        if key in seen:
            continue
        seen.add(key)
        rows.append([m.group("ts"), m.group("pid"), m.group("rate"),
                     m.group("acc"), m.group("gen"), m.group("mean")])
    rows.sort()
    write("live-traffic-draft-acceptance-aug14-15.csv",
          ["logged_at_BST", "llama_server_pid", "draft_acceptance_rate",
           "accepted_tokens", "generated_tokens", "mean_draft_len"], rows)

    # --- Sep 23: cold-prefill progress on the adopted two-card config ---
    seen, rows = set(), []
    for m in PP.finditer(sep):
        key = (m.group("pid"), m.group("n"))
        if key in seen:
            continue
        seen.add(key)
        rows.append([m.group("ts"), m.group("pid"), m.group("n"),
                     m.group("prog"), m.group("t"), m.group("rate")])
    rows.sort(key=lambda r: int(r[2]))
    write("live-service-2026-09-23-prefill-progress.csv",
          ["logged_at_BST", "llama_server_pid", "prompt_tokens_processed",
           "progress", "elapsed_s", "prefill_tok_s"], rows)

    # --- Sep 23: decode series on the same request ---
    seen, rows = set(), []
    for m in TG.finditer(sep):
        key = (m.group("pid"), m.group("n"))
        if key in seen:
            continue
        seen.add(key)
        rows.append([m.group("ts"), m.group("pid"), m.group("n"),
                     m.group("tg"), m.group("tg3")])
    rows.sort(key=lambda r: int(r[2]))
    write("live-service-2026-09-23-decode-series.csv",
          ["logged_at_BST", "llama_server_pid", "tokens_generated",
           "decode_tok_s_avg", "decode_tok_s_last_3s"], rows)


if __name__ == "__main__":
    main()
