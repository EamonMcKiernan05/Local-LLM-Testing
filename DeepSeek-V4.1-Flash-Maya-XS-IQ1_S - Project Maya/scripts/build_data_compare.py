#!/usr/bin/env python3
"""Build the Maya-XS vs Maya-S comparison table.

Refuses to write unless the two datasets are comparable: same depth set, same
document sliced at every depth. Maya-S values come from the sibling dataset's
averages.csv (21 Oct 2026, v1.1.19); Maya-XS from this folder's.
"""
import csv, pathlib, sys

BASE = pathlib.Path(__file__).resolve().parent.parent
S_CSV = BASE.parent / "DeepSeek-V4.1-Flash-Maya-S-IQ2_XXS - Project Maya" / "data" / "csv" / "averages.csv"
XS_CSV = BASE / "data" / "csv" / "averages.csv"
OUT = BASE / "data" / "csv" / "compare.csv"

s = {int(r["depth"]): r for r in csv.DictReader(open(S_CSV))}
xs = {int(r["depth"]): r for r in csv.DictReader(open(XS_CSV))}
depths = sorted(s)
if sorted(xs) != depths:
    sys.exit("depth sets differ: Maya-S %s vs Maya-XS %s" % (depths, sorted(xs)))

rows = []
for d in depths:
    a, b = s[d], xs[d]
    if a["book"] != b["book"]:
        sys.exit("depth %d: different documents (%s vs %s) - not comparable" % (d, a["book"], b["book"]))
    sp, xp = float(a["prefill_mean"]), float(b["prefill_mean"])
    sd, xd = float(a["decode_mean"]), float(b["decode_mean"])
    rows.append(dict(
        depth=d, book=a["book"],
        s_prefill=round(sp, 2), xs_prefill=round(xp, 2),
        prefill_delta_pct=round(100 * (xp - sp) / sp, 1), prefill_ratio=round(xp / sp, 3),
        s_decode=round(sd, 3), xs_decode=round(xd, 3),
        decode_delta_pct=round(100 * (xd - sd) / sd, 1), decode_ratio=round(xd / sd, 3),
    ))

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

mp = sum(r["s_prefill"] for r in rows) / len(rows)
xp = sum(r["xs_prefill"] for r in rows) / len(rows)
md = sum(r["s_decode"] for r in rows) / len(rows)
xd = sum(r["xs_decode"] for r in rows) / len(rows)
print("rows:", len(rows), "| books:", [r["book"] for r in rows])
print("means: prefill %.2f -> %.2f (%.3fx) | decode %.3f -> %.3f (%.3fx)"
      % (mp, xp, xp / mp, md, xd, xd / md))
