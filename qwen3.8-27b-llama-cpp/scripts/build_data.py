#!/usr/bin/env python3
"""
Extract benchmark tables from the source reports into CSVs.

Every table written here is copied verbatim from a source markdown file that
itself was written from the test runs. Nothing is recalculated, rounded or
inferred: the parser only moves pipe-table cells into CSV columns.

Sources (absolute paths on the collection host):
  1. vault report  - llama-dflash2-sweep-2026-09-18.md
  2. vault report  - two-card-tensor-split-gsq-iq3s-2026-09-22.md
  3. vault report  - two-card-100k-nmax-trims-2026-09-23.md
  4. desktop copy  - qwen38-exl3-dflash2-on-.5.md  (section 13 only; the vault
                     copy of that file is missing section 13)
"""
import csv
import os
import re
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "csv")
os.makedirs(OUT, exist_ok=True)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def split_tables(text):
    """Yield (heading, [lines]) for each markdown table, carrying the nearest
    preceding heading above it."""
    lines = text.splitlines()
    heading = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#"):
            heading = line.lstrip("# ").strip()
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]
        ):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            yield heading, block
            continue
        i += 1


def cells(row):
    parts = [c.strip() for c in row.strip().strip("|").split("|")]
    return [p.replace("**", "").replace("`", "").strip() for p in parts]


def write_csv(name, header, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {name:52s} {len(rows):3d} data rows")
    return len(rows)


def grab(text, heading_fragment, table_index=0):
    """Return the rows of the nth table under a heading whose text contains
    heading_fragment."""
    seen = 0
    for heading, block in split_tables(text):
        if heading_fragment.lower() in heading.lower():
            if seen == table_index:
                return cells(block[0]), [cells(r) for r in block[2:]]
            seen += 1
    raise SystemExit(f"table not found: heading~{heading_fragment!r} index={table_index}")


def main(vault, desktop):
    total = 0

    # ---------------------------------------------------------------- report 1
    print("\n[1] llama.cpp speculative-decoding sweep, Qwen3.8-27B UD-Q4_K_XL, 3x RTX 3060 (2026-09-18)")
    r1 = read(os.path.join(vault, "llama-dflash2-sweep-2026-09-18.md"))

    h, rows = grab(r1, "Summary: best measured row per drafter")
    total += write_csv("dflash2-best-per-drafter-per-temp.csv", h, rows)

    h, rows = grab(r1, "Table 1 - temp 0.0")
    total += write_csv("dflash2-sweep-temp0.0.csv", h, rows)

    h, rows = grab(r1, "Table 2 - temp 0.6")
    total += write_csv("dflash2-sweep-temp0.6.csv", h, rows)

    h, rows = grab(r1, "Table 3 - temp 0.8")
    total += write_csv("dflash2-sweep-temp0.8.csv", h, rows)

    h, rows = grab(r1, "Table 4 - temp 0.9")
    total += write_csv("dflash2-sweep-temp0.9.csv", h, rows)

    h, rows = grab(r1, "Reference measurements on the live production service")
    total += write_csv("live-service-build11041-20k.csv", h, rows)

    # ---------------------------------------------------------------- report 2
    print("\n[2] Qwen3.8-27B GSQ-RCO IQ3_S-mtp, 2x RTX 3060, tensor split (2026-09-22/23)")
    r2 = read(os.path.join(vault, "two-card-tensor-split-gsq-iq3s-2026-09-22.md"))

    h, rows = grab(r2, "What fits at 160k context")
    total += write_csv("two-card-160k-load-vram.csv", h, rows)

    h, rows = grab(r2, "MTP n-max sweep — 20,000-token depth")
    total += write_csv("two-card-mtp-nmax-20k.csv", h, rows)

    h, rows = grab(r2, "Verification of the ungated result")
    total += write_csv("two-card-20k-verification-3-repeats.csv", h, rows)

    h, rows = grab(r2, "MTP n-max sweep — 150,000-token depth")
    total += write_csv("two-card-mtp-nmax-150k.csv", h, rows)

    h, rows = grab(r2, "150,000-token depth", table_index=1)
    total += write_csv("two-card-bub-grid-150k.csv", h, rows)

    h, rows = grab(r2, "20,000-token depth", table_index=1)
    total += write_csv("two-card-bub-grid-20k.csv", h, rows)

    h, rows = grab(r2, "Fastest configurations measured")
    total += write_csv("two-card-fastest-configs.csv", h, rows)

    # ---------------------------------------------------------------- report 3
    print("\n[3] Qwen3.8-27B GSQ-RCO IQ3_S-mtp, 100k depth, 2 and 3 cards (2026-09-23)")
    r3 = read(os.path.join(vault, "two-card-100k-nmax-trims-2026-09-23.md"))

    h, rows = grab(r3, "Stage A — MTP n-max")
    total += write_csv("100k-stageA-nmax.csv", h, rows)

    h, rows = grab(r3, "Stage B — top_k")
    total += write_csv("100k-stageB-topk-minp.csv", h, rows)

    h, rows = grab(r3, "Self-check")
    total += write_csv("100k-selftest-gguf-metadata.csv", h, rows)

    h, rows = grab(r3, "Means and spreads")
    total += write_csv("100k-confirm-nmax5-8-3-repeats.csv", h, rows)

    h, rows = grab(r3, "Split-mode matrix at n-max 7")
    total += write_csv("100k-split-mode-matrix.csv", h, rows)

    h, rows = grab(r3, "Three-GPU matrix")
    total += write_csv("three-card-matrix.csv", h, rows)

    h, rows = grab(r3, "DFlash2 n-max 1–8 on three cards")
    total += write_csv("three-card-dflash2-nmax.csv", h, rows)

    # ---------------------------------------------------------------- report 4
    print("\n[4] llama.cpp prefill rate by prompt depth, q8_0 KV (2026-09-20)")
    r4 = read(os.path.join(desktop, "qwen38-exl3-dflash2-on-.5.md"))

    h, rows = grab(r4, "llama.cpp prefill rate at q8_0 KV by prompt depth")
    total += write_csv("prefill-by-depth.csv", h, rows)

    # ------------------------------------------------------- report 4, sections 11/12
    print("\n[5] llama.cpp comparison + buun-llama-cpp fork runs (2026-09-19/20)")

    h, rows = grab(r4, "Results (tok/s)")   # section 12 fork sweep results table
    total += write_csv("buun-fork-sweep-tok_s.csv", h, rows)

    h, rows = grab(r4, "Fork vs stock: where the prefill time actually goes")
    total += write_csv("buun-vs-stock-harness.csv", h, rows)

    h, rows = grab(r4, "Long context (131,072-token cache")
    total += write_csv("buun-vs-stock-long-context-100k.csv", h, rows)

    h, rows = grab(r4, "Drafter-quant coverage")
    total += write_csv("buun-vs-stock-drafter-quants.csv", h, rows)

    print(f"\n{total} data rows written to data/csv/\n")
    return total


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_data.py <vault-reports-dir> <desktop-dir>")
    main(sys.argv[1], sys.argv[2])
