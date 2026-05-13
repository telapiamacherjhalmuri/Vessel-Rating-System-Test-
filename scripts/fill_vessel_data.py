"""
Fills all Unknown / blank / zero-placeholder cells in the Sanctioned Vessel List CSV
with realistic random values matched to each column's semantics.
"""

import csv, random, string, sys, os
from datetime import datetime, timedelta

# ── Lookup tables ──────────────────────────────────────────────────────────────

PORTS_BY_FLAG = {
    "IR": ["Bandar Abbas","Bandar Imam Khomeini","Khorramshahr","Bushehr","Chabahar"],
    "RU": ["Novorossiysk","Saint Petersburg","Vladivostok","Murmansk","Nakhodka","Rostov-on-Don"],
    "KP": ["Chongjin","Nampo","Rajin","Wonsan","Haeju"],
    "CN": ["Shanghai","Tianjin","Guangzhou","Qingdao","Dalian","Ningbo","Xiamen"],
    "HK": ["Hong Kong","Kwai Chung","Stonecutters Island"],
    "PA": ["Panama City","Colon","Balboa"],
    "MH": ["Majuro","Ebeye","Jaluit"],
    "LR": ["Monrovia","Buchanan","Greenville"],
    "BZ": ["Belize City","Dangriga"],
    "CW": ["Willemstad","Otrabanda"],
    "CM": ["Douala","Limbe","Kribi"],
    "SL": ["Freetown","Sherbro","Bonthe"],
    "KM": ["Moroni","Mutsamudu","Fomboni"],
    "MG": ["Toamasina","Mahajanga","Antsiranana"],
    "GN": ["Conakry","Kamsar"],
    "GQ": ["Malabo","Bata"],
    "BJ": ["Cotonou","Porto-Novo"],
    "TG": ["Lome","Kpeme"],
    "AO": ["Luanda","Lobito","Namibe"],
    "OM": ["Muscat","Salalah","Sohar","Duqm"],
    "GY": ["Georgetown","New Amsterdam"],
    "AW": ["Oranjestad","Sint Nicolaas"],
    "MW": ["Blantyre","Lilongwe"],
    "MZ": ["Maputo","Beira","Nacala"],
    "ZW": ["Harare","Bulawayo"],
    "VN": ["Ho Chi Minh City","Hai Phong","Da Nang"],
    "KH": ["Phnom Penh","Sihanoukville"],
    "SG": ["Singapore","Jurong"],
    "TH": ["Bangkok","Laem Chabang"],
    "ID": ["Jakarta","Surabaya","Belawan"],
    "PW": ["Koror","Melekeok"],
    "TO": ["Nuku'alofa","Vava'u"],
    "CK": ["Avarua"],
    "VU": ["Port Vila","Luganville"],
    "VC": ["Kingstown","Georgetown"],
    "VE": ["La Guaira","Puerto Cabello","Maracaibo"],
    "CU": ["Havana","Santiago de Cuba","Cienfuegos"],
    "BB": ["Bridgetown"],
    "KY": ["George Town"],
    "KN": ["Basseterre","Charlestown"],
    "DM": ["Roseau"],
    "TL": ["Dili","Hera"],
    "SM": ["San Marino"],
    "AG": ["St. John's"],
    "BW": ["Gaborone","Francistown"],
    "PK": ["Karachi","Port Qasim","Gwadar"],
    "IN": ["Mumbai","Chennai","Kolkata","Kandla","Kochi"],
    "LK": ["Colombo","Hambantota"],
    "AZ": ["Baku","Alat"],
    "GW": ["Bissau"],
    "ST": ["Sao Tome","Santo Antonio"],
    "TZ": ["Dar es Salaam","Zanzibar","Tanga"],
    "FJ": ["Suva","Lautoka"],
    "MT": ["Valletta","Marsaxlokk"],
    "CY": ["Limassol","Larnaca"],
    "GR": ["Piraeus","Thessaloniki"],
    "MM": ["Yangon","Thilawa"],
    "SY": ["Latakia","Tartus"],
    "DJ": ["Djibouti"],
    "GM": ["Banjul"],
    "NI": ["Managua","Puerto Corinto"],
    "SZ": ["Mbabane"],
    "TZ": ["Dar es Salaam","Zanzibar"],
    "BH": ["Manama","Mina Salman"],
    "NI": ["Managua","Puerto Corinto"],
    "KN": ["Basseterre"],
    "AZ": ["Baku","Alat"],
    "ML": ["Bamako"],
    "GQ": ["Malabo","Bata"],
    "Unknown": [
        "Panama City","Valletta","Majuro","Monrovia","Limassol",
        "Singapore","Hong Kong","Dubai","Istanbul","Piraeus",
        "Nassau","Willemstad","George Town","Kingstown","Bridgetown",
        "Freetown","Moroni","Conakry","Georgetown","Muscat",
        "Douala","Cotonou","Luanda","Maputo","Dar es Salaam",
        "Suva","Colombo","Karachi","Banjul","Libreville",
    ],
}

COMMON_FLAGS = [
    "PA","MH","LR","BS","CY","MT","GR","HK","SG","PW","TO",
    "KM","CK","BZ","CM","SL","VU","MG","BB","KN","AG","DM",
    "VC","KY","VG","TG","BJ","GN","GQ","AO","MW","MZ","GW",
]

CLASSIFICATION_SOCIETIES = [
    "Lloyd's Register","Lloyd's Register","Bureau Veritas","Bureau Veritas",
    "DNV","DNV","American Bureau of Shipping (ABS)","ClassNK",
    "RINA","Korean Register (KR)","China Classification Society (CCS)",
    "Indian Register of Shipping (IRS)","Turkish Lloyd (TL)",
    "Russian Maritime Register of Shipping","","",
]

STATUSES = ["Active","Active","Active","Active","Inactive","Inactive","Laid Up"]

AIS_STATUSES = [
    "Underway Using Engine","At Anchor","Moored",
    "Underway Using Engine","Underway Using Engine","Drifting","At Anchor",
]
SIGNAL_QUALITIES = ["Good","Good","Moderate","Moderate","Weak","Roaming"]

# (length_lo, length_hi, width_lo, width_hi, draught_lo, draught_hi, gt_lo, gt_hi, nt_r_lo, nt_r_hi, dwt_r_lo, dwt_r_hi)
VESSEL_DIMS = {
    "LIQUID TANKER":               (100,280, 16,48,  7,16,  8000,90000,  0.55,0.70, 1.50,2.00),
    "LNG TANKER":                  (200,310, 35,55,  10,13, 65000,140000,0.55,0.65, 0.55,0.70),
    "LPG TANKER":                  (80, 230, 14,38,  7,14,  4000,52000,  0.55,0.68, 0.85,1.20),
    "CONTAINER":                   (120,370, 20,55,  8,16,  10000,200000,0.50,0.65, 0.70,1.10),
    "BULK CARRIER":                (120,300, 22,50,  9,18,  10000,90000, 0.55,0.70, 1.65,1.85),
    "GENERAL CARGO SHIP":          (70, 200, 12,30,  5,12,  1500,22000,  0.55,0.70, 1.20,1.60),
    "CARGO RO RO":                 (100,220, 18,30,  5,10,  8000,30000,  0.50,0.65, 0.60,0.90),
    "FISHING VESSEL":              (20, 80,  6, 15,  2,8,   100,3000,    0.40,0.60, 0.50,0.80),
    "FISHING SUPPORT VESSEL":      (40, 120, 8, 20,  3,8,   500,5000,    0.45,0.60, 0.60,0.90),
    "TUG AND TOWAGE VESSEL":       (20, 55,  8, 15,  3,7,   150,2500,    0.40,0.55, 0.50,0.80),
    "YACHT":                       (20, 100, 5, 16,  2,6,   100,15000,   0.35,0.55, 0.20,0.40),
    "SAILING VESSEL":              (15, 60,  4, 12,  2,5,   50,1000,     0.35,0.55, 0.20,0.40),
    "SPECIAL PURPOSE SERVICE VESSEL":(60,160,12,25,  4,9,   1500,15000,  0.45,0.60, 0.50,0.80),
    "SUBSEA OPERATION VESSEL":     (80, 170, 15,28,  5,10,  3000,20000,  0.50,0.65, 0.55,0.80),
    "PIPELINE OPERATION UNIT":     (100,180, 20,35,  5,10,  5000,25000,  0.50,0.65, 0.60,0.85),
    "MULTIPURPOSE VESSEL":         (80, 180, 14,28,  5,10,  3000,18000,  0.52,0.65, 0.90,1.30),
    "SUPPORT VESSEL":              (50, 130, 12,22,  4,8,   1000,10000,  0.45,0.60, 0.55,0.80),
    "BUNKERING TANKER":            (60, 160, 12,25,  4,9,   1200,12000,  0.50,0.65, 1.20,1.60),
    "FERRY AND CRUISE SHIP":       (80, 280, 16,38,  5,10,  5000,70000,  0.50,0.65, 0.20,0.50),
    "REEFER SHIP":                 (100,200, 18,28,  6,10,  5000,20000,  0.52,0.65, 0.80,1.10),
    "DRILLING UNIT":               (80, 160, 60,90,  7,15,  15000,50000, 0.50,0.65, 0.55,0.80),
    "FLOATING PRODUCTION AND STORAGE UNIT":(200,350,40,65,12,20,50000,150000,0.55,0.70,1.50,2.00),
    "DRY CARGO BARGE":             (50, 140, 12,22,  2,7,   500,6000,    0.50,0.65, 1.40,1.80),
    "DREDGING VESSEL":             (60, 150, 12,25,  3,8,   1500,12000,  0.45,0.60, 0.50,0.80),
    "DEFAULT":                     (80, 200, 14,30,  5,10,  3000,25000,  0.52,0.65, 0.90,1.40),
}

# Approx bounding boxes for regions: (lat_lo, lat_hi, lon_lo, lon_hi)
REGION_COORDS = {
    "Persian Gulf":          (22.0, 30.0, 48.0, 60.0),
    "Black Sea":             (41.0, 46.5, 28.0, 41.5),
    "Yellow Sea":            (30.0, 38.5, 119.0, 127.0),
    "High-risk tanker corridor": (-5.0, 25.0, 50.0, 80.0),
    "Open sea":              (-30.0, 30.0, -60.0, 60.0),
    "Caribbean":             (10.0, 25.0, -85.0, -60.0),
    "Eastern Mediterranean": (30.0, 42.0, 24.0, 37.0),
    "Bulk trade corridor":   (-10.0, 20.0, 60.0, 100.0),
    "Black Sea":             (41.0, 46.5, 28.0, 41.5),
    "DEFAULT":               (-60.0, 60.0, -180.0, 180.0),
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def rnd_call_sign():
    return "".join(random.choices(string.ascii_uppercase, k=4)) + str(random.randint(0,9))

def rnd_mmsi():
    return str(random.randint(2,7)) + "".join([str(random.randint(0,9)) for _ in range(8)])

def rnd_port(flag):
    return random.choice(PORTS_BY_FLAG.get(flag, PORTS_BY_FLAG["Unknown"]))

def rnd_classification():
    return random.choice(CLASSIFICATION_SOCIETIES)

def rnd_status():
    return random.choice(STATUSES)

def get_dims(vtype):
    for k, v in VESSEL_DIMS.items():
        if k != "DEFAULT" and (k in vtype.upper() or vtype.upper() in k):
            return v
    return VESSEL_DIMS["DEFAULT"]

def rnd_dimensions(vtype):
    ll,lh,wl,wh,dl,dh,gl,gh,nrl,nrh,drl,drh = get_dims(vtype)
    length  = round(random.uniform(ll, lh), 2)
    w_lo    = max(wl, length / 8.5);  w_hi = min(wh, length / 5.5)
    if w_lo > w_hi: w_lo, w_hi = wl, wh
    width   = round(random.uniform(w_lo, w_hi), 2)
    draught = round(random.uniform(dl, dh), 2)
    gt      = random.randint(gl, gh)
    nt      = int(gt * random.uniform(nrl, nrh))
    dwt     = int(gt * random.uniform(drl, drh))
    return length, width, draught, gt, nt, dwt

def rnd_date(y0=2000, y1=2024):
    d = datetime(y0,1,1) + timedelta(days=random.randint(0,(datetime(y1,12,31)-datetime(y0,1,1)).days))
    return d.strftime("%#d-%b-%y") if sys.platform=="win32" else d.strftime("%-d-%b-%y")

def rnd_timestamp():
    d = datetime(2024,1,1) + timedelta(days=random.randint(0,365*2), hours=random.randint(0,23), minutes=random.randint(0,59))
    return d.strftime("%Y-%m-%d %H:%M (UTC+0)")

def rnd_coords(region):
    box = REGION_COORDS.get(region, REGION_COORDS["DEFAULT"])
    lat = round(random.uniform(box[0], box[1]), 5)
    lon = round(random.uniform(box[2], box[3]), 5)
    return lat, lon

def rnd_speed():
    return f"{round(random.uniform(0, 15), 1)} kn"

def rnd_course():
    return f"{random.randint(0, 359)} °"

def rnd_heading():
    return f"{random.randint(0, 359)} °"

def rnd_accuracy():
    return f"{random.randint(70, 99)}%"

def is_unknown(val):
    return val.strip().lower() in ("unknown", "")

def is_zero(val):
    try:
        return float(val.strip()) == 0.0
    except ValueError:
        return False

# ── Main ───────────────────────────────────────────────────────────────────────

def process(input_path, output_path):
    with open(input_path, newline="", encoding="utf-8-sig") as fin:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"Loaded {len(rows):,} rows from {os.path.basename(input_path)}")

    filled = 0

    for row in rows:
        # ── Flag ─────────────────────────────────────────────────────────────
        if is_unknown(row.get("Flag","")):
            fill("Flag", random.choice(COMMON_FLAGS))

        flag   = row.get("Flag","Unknown").strip()
        vtype  = row.get("Vessel type","").strip()
        region = row.get("Current Region","").strip()

        def fill(col, value):
            nonlocal filled
            if row.get(col,"").strip() != str(value):
                row[col] = str(value)
                filled += 1

        # ── Port of Registry ──────────────────────────────────────────────────
        if is_unknown(row.get("Port of Registry","")):
            fill("Port of Registry", rnd_port(flag))

        # ── Call Sign ─────────────────────────────────────────────────────────
        if is_unknown(row.get("Call Sign","")):
            fill("Call Sign", rnd_call_sign())

        # ── MMSI ──────────────────────────────────────────────────────────────
        if is_unknown(row.get("MMSI","")):
            fill("MMSI", rnd_mmsi())

        # ── Classification Society ────────────────────────────────────────────
        if is_unknown(row.get("Classification Society","")):
            fill("Classification Society", rnd_classification())

        # ── Status ────────────────────────────────────────────────────────────
        if is_unknown(row.get("Status","")):
            fill("Status", rnd_status())

        # ── Dimensions + Tonnage ──────────────────────────────────────────────
        l_raw  = row.get("Length (m)","").strip().lower()
        w_raw  = row.get("Width (m)","").strip().lower()
        d_raw  = row.get("Draught (m)","").strip().lower()
        gt_val = int(row.get("Gross Tonnage","0").strip() or "0")
        nt_val = int(row.get("Net Tonnage","0").strip() or "0")
        dw_val = int(row.get("Deadweight Tonnage","0").strip() or "0")

        need_dims = is_unknown(l_raw) or is_unknown(w_raw)
        need_ton  = gt_val == 0 or nt_val == 0 or dw_val == 0

        if need_dims or need_ton:
            length, width, draught, gt, nt, dwt = rnd_dimensions(vtype)
            if is_unknown(l_raw):
                fill("Length (m)",           f"{length}m")
            if is_unknown(w_raw):
                fill("Width (m)",            f"{width}m")
            if is_unknown(d_raw):
                fill("Draught (m)",          f"{draught}m")
            if gt_val == 0:
                fill("Gross Tonnage",        gt)
            if nt_val == 0:
                fill("Net Tonnage",          nt)
            if dw_val == 0:
                fill("Deadweight Tonnage",   dwt)

        # ── Coordinates ───────────────────────────────────────────────────────
        lat_raw = row.get("Latitude","0").strip()
        lon_raw = row.get("Longitude","0").strip()
        if is_zero(lat_raw) and is_zero(lon_raw):
            lat, lon = rnd_coords(region)
            fill("Latitude",  lat)
            fill("Longitude", lon)

        # ── Speed, Course, Heading ────────────────────────────────────────────
        if is_unknown(row.get("Speed (knots)","")):
            fill("Speed (knots)", rnd_speed())
        if is_unknown(row.get("Course","")):
            fill("Course", rnd_course())
        if is_unknown(row.get("Heading","")):
            fill("Heading", rnd_heading())

        # ── Last Update ───────────────────────────────────────────────────────
        if is_unknown(row.get("Last Update","")):
            fill("Last Update", rnd_timestamp())

        # ── AIS Status ────────────────────────────────────────────────────────
        if is_unknown(row.get("AIS Status","")):
            fill("AIS Status", random.choice(AIS_STATUSES))

        # ── Signal Quality ────────────────────────────────────────────────────
        if is_unknown(row.get("Signal Quality","")):
            fill("Signal Quality", random.choice(SIGNAL_QUALITIES))

        # ── Accuracy ──────────────────────────────────────────────────────────
        acc_raw = row.get("Accuracy","0").strip()
        if is_zero(acc_raw) or is_unknown(acc_raw):
            fill("Accuracy", rnd_accuracy())

        # ── Name Changes ──────────────────────────────────────────────────────
        if is_unknown(row.get("Name Changes","")):
            fill("Name Changes", random.randint(0, 4))

        # ── Last Change Date ──────────────────────────────────────────────────
        if is_unknown(row.get("Last Change Date","")):
            fill("Last Change Date", rnd_date())

    with open(output_path, "w", newline="", encoding="utf-8-sig") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Filled {filled:,} cells")
    print(f"Output → {os.path.basename(output_path)}")


if __name__ == "__main__":
    folder = r"e:\Vessel_Rating_System - Copy\outputs\sanctioned_vessel_completion"
    inp = os.path.join(folder, "Risk & Compliance - Sanctioned Vessel List - completed.csv")
    out = os.path.join(folder, "Risk & Compliance - Sanctioned Vessel List - completed_FILLED.csv")

    # Back up original once (copy, not overwrite)
    bak = inp.replace(".csv", "_original.csv")
    if not os.path.exists(bak):
        import shutil; shutil.copy2(inp, bak)
        print(f"Backup saved -> {os.path.basename(bak)}")

    process(inp, out)
