import csv, os

folder = r"e:\Vessel_Rating_System - Copy\outputs\sanctioned_vessel_completion"
path = os.path.join(folder, "Risk & Compliance - Sanctioned Vessel List - completed_FILLED.csv")

with open(path, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

print(f"Total rows: {len(rows):,}")

# Count remaining Unknowns
remaining = sum(
    1 for row in rows for v in row.values() if v.strip().lower() == "unknown"
)
print(f"Remaining 'Unknown' cells: {remaining}")

# Show sample of different vessel types
print("\nSample rows (one per vessel type):")
seen = set()
check_cols = [
    "Port of Registry","Call Sign","MMSI","Classification Society","Status",
    "Length (m)","Width (m)","Draught (m)","Gross Tonnage","Net Tonnage",
    "Deadweight Tonnage","Latitude","Longitude","Speed (knots)","Course",
    "Heading","Last Update","AIS Status","Signal Quality","Accuracy",
    "Name Changes","Last Change Date",
]
for row in rows:
    vt = row.get("Vessel type","")
    if vt not in seen:
        seen.add(vt)
        print(f"\n  [{vt}]  {row['Name']}  (Flag:{row['Flag']})")
        for col in check_cols:
            print(f"    {col:<32} {row.get(col,'')}")
