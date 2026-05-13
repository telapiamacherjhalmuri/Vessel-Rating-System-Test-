import csv, os

folder = r"e:\Vessel_Rating_System - Copy\outputs\sanctioned_vessel_completion"
path = os.path.join(folder, "Risk & Compliance - Sanctioned Vessel List - completed_FILLED.csv")

with open(path, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

from collections import Counter
col_counts = Counter()
for row in rows:
    for col, val in row.items():
        if val.strip().lower() == "unknown":
            col_counts[col] += 1

print("Columns still containing 'Unknown':")
for col, cnt in col_counts.most_common():
    print(f"  {col:<40} {cnt}")
