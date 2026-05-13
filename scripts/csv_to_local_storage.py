"""
Converts the filled Sanctioned Vessel List CSV into per-vessel JSON files
in the local_storage/ directory, using the exact schema expected by the
Vessel Rating System scoring engine.
"""

import csv, json, os, re
from datetime import datetime
from pathlib import Path

CSV_PATH = (
    Path(__file__).resolve().parents[1]
    / "outputs" / "sanctioned_vessel_completion"
    / "Risk & Compliance - Sanctioned Vessel List - completed_FILLED.csv"
)
OUT_DIR = Path(__file__).resolve().parents[1] / "local_storage"
TODAY   = datetime.now().strftime("%Y-%m-%d")
CUR_YEAR = datetime.now().year

# ── value parsers ──────────────────────────────────────────────────────────────

def _flt(val, default=0.0):
    if not val or str(val).strip().lower() in ("", "unknown", "-"):
        return default
    cleaned = re.sub(r"[^\d.\-]", "", str(val))
    try:
        return float(cleaned)
    except ValueError:
        return default

def _int(val, default=0):
    return int(_flt(val, default))

def _bool(val):
    return str(val).strip().lower() in ("yes", "true", "1", "y")

def _strip(val):
    v = str(val).strip()
    return "" if v.lower() in ("-", "unknown") else v

def _year_from_age(age_str):
    age = _int(age_str)
    if age <= 0:
        return CUR_YEAR
    return CUR_YEAR - age

def _safe_filename(name, imo):
    safe = re.sub(r"[^a-z0-9_]", "_", name.lower().strip())
    safe = re.sub(r"_+", "_", safe).strip("_")
    return f"{safe}_{imo}.json"

def _sanctions_risk(ofac, un, eu, flag, risk_status):
    if ofac or un or eu:
        return "CRITICAL"
    if str(risk_status).lower() == "sanctioned":
        return "HIGH"
    if str(flag).upper() in ("IR", "KP", "SY", "CU", "VE"):
        return "HIGH"
    return "LOW"

def _build_events(row, ofac, un, eu):
    events = []
    if ofac:
        events.append({"type": "OFAC_HIT",      "severity": "CRITICAL", "date": TODAY,
                        "description": "Vessel is OFAC listed"})
    if un:
        events.append({"type": "UN_SANCTION",   "severity": "CRITICAL", "date": TODAY,
                        "description": "Vessel is UN-sanctioned"})
    if eu:
        events.append({"type": "EU_SANCTION",   "SEVERITY": "HIGH",     "date": TODAY,
                        "description": "Vessel is EU-sanctioned"})
    if _bool(row.get("Spoofing Risk", "No")):
        events.append({"type": "AIS_SPOOFING",  "severity": "HIGH",     "date": TODAY,
                        "description": "AIS spoofing risk detected"})
    if _bool(row.get("Dark Activity", "No")):
        events.append({"type": "DARK_ACTIVITY", "severity": "HIGH",     "date": TODAY,
                        "description": "Dark activity (AIS off) detected"})
    critical = sum(1 for e in events if e.get("severity") == "CRITICAL")
    high     = sum(1 for e in events if e.get("severity") == "HIGH")
    return {"total_events": len(events), "critical_events": critical,
            "high_risk_events": high, "medium_risk_events": 0, "recent_events": events}

def _psc_status(deficiency_count):
    d = _int(deficiency_count)
    if d == 0:
        return "CLEAR"
    return f"{d} deficiency" + ("" if d == 1 else "ies") + " detected"

def _cert(society):
    if not society:
        return []
    today = datetime.now()
    expiry = f"{today.year + 2}-{today.month:02d}-01"
    return [{"type": f"Classification Certificate ({society})",
             "status": "VALID", "expiry_date": expiry}]

def _owner_rep(row):
    rep = _strip(row.get("Manager Reputation", ""))
    if rep.lower() == "sanctioned":
        return "Sanctioned", 0.1
    if rep.lower() in ("high", "good"):
        return "Good", 0.8
    return "Not Sanctioned", 0.5

def _sanitize_speed(val):
    """Return float knots from strings like '11.3 kn' or '0.1 kn'."""
    return _flt(val)

# ── main ───────────────────────────────────────────────────────────────────────

def convert(csv_path: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    print(f"Converting {len(rows):,} vessels -> {out_dir}")

    written = skipped = 0
    for row in rows:
        name = _strip(row.get("Name", ""))
        imo  = _strip(row.get("IMO", ""))
        if not name or not imo:
            skipped += 1
            continue

        flag    = _strip(row.get("Flag", ""))
        vtype   = _strip(row.get("Vessel type", ""))
        risk_st = _strip(row.get("Risk status", ""))

        ofac = _bool(row.get("OFAC Listed", "No"))
        un   = _bool(row.get("UN Sanctions", "No"))
        eu   = _bool(row.get("EU Sanctions", "No"))

        owner       = _strip(row.get("Beneficial owner", ""))
        manager     = _strip(row.get("Commercial manager", ""))
        reg_owner   = _strip(row.get("Registered owner", ""))
        ism_mgr     = _strip(row.get("ISM manager", ""))
        rep_label, rep_score = _owner_rep(row)

        society      = _strip(row.get("Classification Society", ""))
        status       = _strip(row.get("Status", "Active"))
        port_reg     = _strip(row.get("Port of Registry", ""))
        call_sign    = _strip(row.get("Call Sign", ""))
        mmsi         = _strip(row.get("MMSI", ""))
        det_count    = _int(row.get("Detention History", 0))
        def_count    = _int(row.get("Deficiency Count", 0))
        banned       = _bool(row.get("Banning Status", "No"))
        route_risk   = _strip(row.get("Trade Route Risk", "Clean"))
        region       = _strip(row.get("Current Region", ""))

        lat = _flt(row.get("Latitude", 0))
        lon = _flt(row.get("Longitude", 0))
        spd = _sanitize_speed(row.get("Speed (knots)", "0"))
        crs = _flt(row.get("Course", 0))
        hdg = _flt(row.get("Heading", 0))
        lu  = _strip(row.get("Last Update", TODAY))
        ais = _strip(row.get("AIS Status", "Unknown"))
        sig = _strip(row.get("Signal Quality", "Good"))
        acc = _strip(row.get("Accuracy", "90%"))

        temp   = _flt(row.get("Temperature", 25))
        wind   = _flt(row.get("Wind Speed", 10))
        wave   = _flt(row.get("Wave Height", 1))
        sea    = _strip(row.get("Sea State", "Moderate"))
        piracy = _bool(row.get("Piracy Zone", "No"))
        war    = _bool(row.get("War Zone", "No"))
        storm  = _bool(row.get("Storm Area", "No"))
        ice    = _bool(row.get("Ice Zone", "No"))

        spoofing = _bool(row.get("Spoofing Risk", "No"))
        dark_act = _bool(row.get("Dark Activity", "No"))
        sts_ev   = _int(row.get("STS Transfer Events", 0))

        own_chg  = _int(row.get("Ownership Changes", 0))
        nm_chg   = _int(row.get("Name Changes", 0))
        lcd      = _strip(row.get("Last Change Date", ""))
        try:
            lcd_iso = datetime.strptime(lcd, "%d-%b-%y").strftime("%Y-%m-%d")
        except Exception:
            lcd_iso = lcd or TODAY

        psc_stat = _psc_status(def_count or det_count)
        risk_lvl = _sanctions_risk(ofac, un, eu, flag, risk_st)

        built_yr = _year_from_age(row.get("Age", 10))

        vessel = {
            "vessel_info": {
                "vessel_name": name,
                "imo_number":  imo,
                "flag":        flag,
                "vessel_type": vtype,
                "dimensions": {
                    "length": _flt(row.get("Length (m)", 0)),
                    "width":  _flt(row.get("Width (m)", 0)),
                    "depth":  _flt(row.get("Draught (m)", 0)),
                    "tonnage": {
                        "gross":       _int(row.get("Gross Tonnage", 0)),
                        "net":         _int(row.get("Net Tonnage", 0)),
                        "dead_weight": _int(row.get("Deadweight Tonnage", 0)),
                    },
                },
                "engine":   {"type": "", "fuel_type": ""},
                "built_year": built_yr,
                "classification_society": society,
                "status":          status,
                "port_of_registry": port_reg,
                "call_sign":       call_sign,
                "mmsi":            mmsi,
                "last_updated":    TODAY,
            },
            "ais_data": {
                "position": {"latitude": lat, "longitude": lon, "timestamp": lu},
                "movement": {"speed": spd, "course": crs, "heading": hdg},
                "status":         ais,
                "signal_quality": sig,
                "accuracy":       acc,
                "ais_gaps": {
                    "detected":    False,
                    "gap_hours":   0,
                    "last_signal": lu,
                },
                "anomalies": {
                    "spoofing_detected":    spoofing,
                    "dark_activity":        dark_act,
                    "unusual_speed":        False,
                    "unusual_route":        False,
                    "spoofing_events":      1 if spoofing else 0,
                    "sts_transfer_events":  sts_ev,
                },
            },
            "ownership": {
                "current_owner":      owner or reg_owner,
                "owner_country":      flag,
                "registered_owner":   reg_owner,
                "manager":            manager or ism_mgr,
                "operator":           ism_mgr,
                "beneficial_owner":   owner,
                "ownership_changes":  own_chg,
                "name_changes":       nm_chg,
                "last_change_date":   lcd_iso,
                "owner_sanctioned":   ofac or un or eu,
                "manager_reputation": rep_label,
                "reputation_score":   rep_score,
            },
            "sanctions": {
                "ofac_hit":  ofac,
                "un_hit":    un,
                "eu_hit":    eu,
                "sanctioned_entities": (
                    [{"name": owner, "relationship": "owner", "list": "OFAC/UN/EU"}]
                    if (ofac or un or eu) and owner else []
                ),
                "risk_level":          risk_lvl,
                "last_checked":        TODAY,
                "last_violation_date": _strip(row.get("Last Violation", "0")),
                "detention_count":     det_count,
                "psc_status":          psc_stat,
                "deficiency_count":    def_count,
                "banned":              banned,
                "route_risk_level":    route_risk,
            },
            "weather": {
                "region": region,
                "weather_conditions": {
                    "temperature": temp,
                    "wind_speed":  wind,
                    "sea_state":   sea,
                    "visibility":  "Good",
                    "wave_height": wave,
                },
                "piracy_zone":         piracy,
                "war_zone":            war,
                "storm_warning":       storm,
                "ice_zone":            ice,
                "route_risk_assessment": "Yes" if (piracy or war or storm) else "No",
                "last_updated":        TODAY,
            },
            "compliance": {
                "certificates":      _cert(society),
                "insurance_valid":   not (ofac or un or eu),
                "cii_rating":        "Unknown",
                "eedi_compliant":    False,
                "ism_certified":     bool(ism_mgr),
                "isps_certified":    True,
                "doc_quality_score": "Poor" if (ofac or un or eu) else "Fair",
                "inspection_status": psc_stat,
                "port_state_control": {
                    "inspections":     max(det_count, def_count),
                    "deficiencies":    def_count,
                    "last_inspection": lcd_iso,
                },
                "last_updated": TODAY,
            },
            "risk_events": _build_events(row, ofac, un, eu),
            "port_call_history": {
                "total_port_calls":  0,
                "high_risk_ports":   0,
                "sts_transfers":     sts_ev,
                "suspicious_routes": 1 if dark_act else 0,
                "recent_ports":      [],
            },
        }

        payload  = {"vessels": [vessel]}
        filename = _safe_filename(name, imo)
        out_path = out_dir / filename
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        written += 1

    print(f"Written : {written:,} JSON files")
    print(f"Skipped : {skipped}")
    print(f"Location: {out_dir}")


if __name__ == "__main__":
    convert(CSV_PATH, OUT_DIR)
