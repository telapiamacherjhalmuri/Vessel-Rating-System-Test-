import csv, os

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(base, "data", "Sanctioned_Vessel_List_Processed.csv"), encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

print(f"Total rows processed: {len(rows)}")

types = {}
for r in rows:
    t = r.get("Vessel type", "Unknown")
    types[t] = types.get(t, 0) + 1

print("\nVessel type coverage:")
for t, c in sorted(types.items()):
    print(f"  {t}: {c}")

print("\nSample entries across vessel types:")
seen = set()
for r in rows:
    vt = r.get("Vessel type", "")
    if vt not in seen:
        seen.add(vt)
        print(f"  [{vt}] {r['Name']}")
        print(f"    Port={r['Port of Registry']}, CallSign={r['Call Sign']}, MMSI={r['MMSI']}")
        print(f"    Class={r['Classification Society']}, Status={r['Status']}")
        print(f"    L={r['Length (m)']}, W={r['Width (m)']}, D={r['Draught (m)']}")
        print(f"    GT={r['Gross Tonnage']}, NT={r['Net Tonnage']}, DWT={r['Deadweight Tonnage']}")
        print(f"    NameChanges={r['Name Changes']}, LastChange={r['Last Change Date']}")
        print()
