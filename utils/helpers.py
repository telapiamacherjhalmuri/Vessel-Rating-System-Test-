"""
Utility functions for Vessel Rating System
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def format_json_report(report: Dict[str, Any]) -> str:
    """Format report as pretty JSON string"""
    return json.dumps(report, indent=2, default=str)


def save_report_to_file(report: Dict[str, Any], filename: str = None) -> str:
    """Save report to JSON file"""
    if filename is None:
        vessel_info = report.get("vessel_info", {})
        imo = vessel_info.get("imo_number", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vessel_report_{imo}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info(f"Report saved to {filename}")
    return filename


def create_csv_summary(report: Dict[str, Any]) -> str:
    """Create CSV summary of module scores"""
    csv = "Module,Score,Band,Weight_Percent\n"
    
    modules = report.get("module_breakdown", [])
    for module in modules:
        csv += f"{module['module']},{module['score']},{module['band']},{module['weight_percent']}\n"
    
    return csv


def create_comprehensive_csv(report: Dict[str, Any], vessel_data: Dict[str, Any] = None) -> str:
    """Create comprehensive CSV with all vessel data, pictures, and ratings"""
    from .comprehensive_report import _flatten_vessel_data, _get_vessel_metadata
    
    # Flatten vessel data
    if vessel_data:
        flattened_data = _flatten_vessel_data(vessel_data)
        metadata = _get_vessel_metadata(vessel_data)
    else:
        flattened_data = {}
        metadata = {}
    
    # Get scoring data
    scoring = report.get("scoring", {})
    
    # Create CSV header
    headers = [
        # Vessel Identification
        "Vessel_Name", "IMO_Number", "Vessel_Type", "Built_Year", "Flag_State",
        "Port_of_Registry", "Call_Sign", "MMSI", "Classification_Society", "Status",
        
        # Dimensions
        "Length", "Width", "Draught", "Gross_Tonnage", "Net_Tonnage", "Deadweight_Tonnage",
        
        # Ownership
        "Current_Owner", "Manager", "Technical_Manager", "Beneficial_Owner", "Registered_Owner",
        "Ownership_Changes", "Name_Changes",
        
        # AIS Data
        "AIS_Latitude", "AIS_Longitude", "AIS_Speed", "AIS_Course", "AIS_Heading",
        "AIS_Timestamp", "AIS_Destination", "AIS_ETA",
        
        # Sanctions & Risk
        "OFAC_Hit", "UN_Hit", "EU_Hit", "Sanctions_Details",
        
        # Environmental
        "Piracy_Zone", "War_Zone", "Hurricane_Zone", "Weather_Conditions", "Temperature", "Wind_Speed",
        
        # Ratings & Scoring
        "Overall_Band_Rating", "Final_Score", "Risk_Level", "Classification",
        "General_Info_Band", "Ownership_Band", "AIS_Band", "Risk_Compliance_Band", "Environmental_Band",
        
        # Metadata
        "Vessel_Picture_URL", "Data_Sources", "Last_Updated", "Data_Completeness"
    ]
    
    # Create CSV content
    csv_content = ",".join(headers) + "\n"
    
    # Prepare data row
    row_data = []
    
    # Vessel info
    row_data.extend([
        flattened_data.get("vessel_name", ""),
        flattened_data.get("imo_number", ""),
        flattened_data.get("vessel_type", ""),
        str(flattened_data.get("built_year", "")),
        flattened_data.get("flag_state", ""),
        flattened_data.get("port_of_registry", ""),
        flattened_data.get("call_sign", ""),
        str(flattened_data.get("mmsi", "")),
        flattened_data.get("classification_society", ""),
        flattened_data.get("status", ""),
    ])
    
    # Dimensions
    row_data.extend([
        str(flattened_data.get("dimensions_length", "")),
        str(flattened_data.get("dimensions_width", "")),
        str(flattened_data.get("dimensions_draught", "")),
        str(flattened_data.get("tonnage_gross", "")),
        str(flattened_data.get("tonnage_net", "")),
        str(flattened_data.get("tonnage_deadweight", "")),
    ])
    
    # Ownership
    row_data.extend([
        flattened_data.get("current_owner", ""),
        flattened_data.get("manager", ""),
        flattened_data.get("technical_manager", ""),
        flattened_data.get("beneficial_owner", ""),
        flattened_data.get("registered_owner", ""),
        str(flattened_data.get("ownership_changes", "")),
        str(flattened_data.get("name_changes", "")),
    ])
    
    # AIS
    row_data.extend([
        str(flattened_data.get("ais_latitude", "")),
        str(flattened_data.get("ais_longitude", "")),
        str(flattened_data.get("ais_speed", "")),
        str(flattened_data.get("ais_course", "")),
        str(flattened_data.get("ais_heading", "")),
        flattened_data.get("ais_timestamp", ""),
        flattened_data.get("ais_destination", ""),
        flattened_data.get("ais_eta", ""),
    ])
    
    # Sanctions
    row_data.extend([
        str(flattened_data.get("ofac_hit", "")),
        str(flattened_data.get("un_hit", "")),
        str(flattened_data.get("eu_hit", "")),
        flattened_data.get("sanctions_details", ""),
    ])
    
    # Environmental
    row_data.extend([
        str(flattened_data.get("piracy_zone", "")),
        str(flattened_data.get("war_zone", "")),
        str(flattened_data.get("hurricane_zone", "")),
        flattened_data.get("weather_conditions", ""),
        str(flattened_data.get("weather_temperature", "")),
        str(flattened_data.get("weather_wind_speed", "")),
    ])
    
    # Ratings
    modules = report.get("module_breakdown", [])
    module_bands = {m["code"]: m["band"] for m in modules}
    
    row_data.extend([
        str(scoring.get("final_band", "")),
        str(scoring.get("final_score", "")),
        scoring.get("risk_level", ""),
        scoring.get("classification", ""),
        str(module_bands.get("general_info", "")),
        str(module_bands.get("ownership", "")),
        str(module_bands.get("ais", "")),
        str(module_bands.get("risk_compliance", "")),
        str(module_bands.get("environmental", "")),
    ])
    
    # Metadata
    row_data.extend([
        metadata.get("vessel_picture_url", ""),
        ";".join(metadata.get("data_sources", [])),
        metadata.get("last_updated", ""),
        str(metadata.get("data_completeness", "")),
    ])
    
    # Escape commas and quotes in data
    escaped_row = []
    for item in row_data:
        if isinstance(item, str):
            # Escape quotes and wrap in quotes if contains comma or quote
            if ',' in item or '"' in item or '\n' in item:
                item = '"' + item.replace('"', '""') + '"'
        escaped_row.append(str(item))
    
    csv_content += ",".join(escaped_row) + "\n"
    
    return csv_content


def export_summary_csv(report: Dict[str, Any], filename: str = None) -> str:
    """Export module summary to CSV file"""
    if filename is None:
        vessel_info = report.get("vessel_info", {})
        imo = vessel_info.get("imo_number", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vessel_summary_{imo}_{timestamp}.csv"
    
    csv_content = create_csv_summary(report)
    
    with open(filename, 'w') as f:
        f.write(csv_content)
    
    logger.info(f"CSV saved to {filename}")
    return filename


def create_pdf_report(report: Dict[str, Any], vessel_data: Dict[str, Any] = None) -> bytes:
    """Create comprehensive PDF report with vessel data and ratings"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from io import BytesIO

    PAGE_W, PAGE_H = A4
    NAVY   = colors.HexColor("#0F4C81")
    DARK   = colors.HexColor("#0F172A")
    SLATE  = colors.HexColor("#64748B")
    LIGHT  = colors.HexColor("#F8FAFC")
    BORDER = colors.HexColor("#E2E8F0")
    WHITE  = colors.white

    def band_color_hex(band: float) -> colors.HexColor:
        if band >= 8:   return colors.HexColor("#00A86B")
        if band >= 7:   return colors.HexColor("#00A3C7")
        if band >= 5:   return colors.HexColor("#F59E0B")
        if band >= 3:   return colors.HexColor("#F97316")
        return colors.HexColor("#CC3333")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
    )

    base = getSampleStyleSheet()
    sty = {
        "title": ParagraphStyle("vrs_title", parent=base["Normal"],
                                fontSize=22, leading=26, textColor=WHITE,
                                fontName="Helvetica-Bold", alignment=TA_LEFT),
        "sub":   ParagraphStyle("vrs_sub",   parent=base["Normal"],
                                fontSize=10, leading=14, textColor=colors.HexColor("#CBD5E1"),
                                fontName="Helvetica", alignment=TA_LEFT),
        "h2":    ParagraphStyle("vrs_h2",    parent=base["Normal"],
                                fontSize=12, leading=16, textColor=NAVY,
                                fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4),
        "body":  ParagraphStyle("vrs_body",  parent=base["Normal"],
                                fontSize=9,  leading=13, textColor=DARK,
                                fontName="Helvetica"),
        "small": ParagraphStyle("vrs_small", parent=base["Normal"],
                                fontSize=8,  leading=11, textColor=SLATE,
                                fontName="Helvetica"),
        "alert_crit": ParagraphStyle("alert_c", parent=base["Normal"],
                                     fontSize=9, leading=13,
                                     textColor=colors.HexColor("#991B1B"),
                                     fontName="Helvetica-Bold"),
        "alert_high": ParagraphStyle("alert_h", parent=base["Normal"],
                                     fontSize=9, leading=13,
                                     textColor=colors.HexColor("#92400E"),
                                     fontName="Helvetica-Bold"),
        "alert_med":  ParagraphStyle("alert_m", parent=base["Normal"],
                                     fontSize=9, leading=13,
                                     textColor=colors.HexColor("#1E3A5F"),
                                     fontName="Helvetica"),
    }

    vessel_info  = report.get("vessel_info", {})
    scoring      = report.get("scoring", {})
    modules      = report.get("module_breakdown", [])
    alerts       = report.get("alerts", [])
    vinfo        = (vessel_data or {}).get("vessel_info", {})
    ownership    = (vessel_data or {}).get("ownership", {})
    ais          = (vessel_data or {}).get("ais_data", {})
    weather      = (vessel_data or {}).get("weather", {})
    sanctions    = (vessel_data or {}).get("sanctions", {})

    final_band   = scoring.get("final_band", 0)
    final_score  = scoring.get("final_score", 0)
    risk_level   = scoring.get("risk_level", "Unknown")
    classification = scoring.get("classification", "unknown").upper()
    bc = band_color_hex(final_band)

    def _table(data, col_widths, header_bg=NAVY, alt_bg=LIGHT):
        t = Table(data, colWidths=col_widths, repeatRows=1)
        n = len(data)
        style_cmds = [
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0),  9),
            ("BACKGROUND",  (0, 0), (-1, 0),  header_bg),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  WHITE),
            ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",    (0, 1), (-1, -1), 8.5),
            ("TEXTCOLOR",   (0, 1), (-1, -1), DARK),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, alt_bg]),
            ("GRID",        (0, 0), (-1, -1), 0.4, BORDER),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ]
        t.setStyle(TableStyle(style_cmds))
        return t

    story = []

    # ── HEADER BANNER ──────────────────────────────────────────────────
    ts = datetime.now().strftime("%d %b %Y  %H:%M UTC")
    hdr_data = [[
        Paragraph(f"VESSEL RATING REPORT<br/>"
                  f"<font size='11'>{vessel_info.get('vessel_name','')}</font>", sty["title"]),
        Paragraph(f"IMO: {vessel_info.get('imo_number','N/A')}<br/>{ts}", sty["sub"]),
    ]]
    hdr = Table(hdr_data, colWidths=[12*cm, None])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,-1), NAVY),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0),(-1,-1), 14),
        ("RIGHTPADDING",(0,0),(-1,-1), 14),
        ("TOPPADDING",  (0,0),(-1,-1), 14),
        ("BOTTOMPADDING",(0,0),(-1,-1), 14),
        ("ALIGN",       (1,0),(1,0),   "RIGHT"),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 10))

    # ── EXECUTIVE SUMMARY ──────────────────────────────────────────────
    story.append(Paragraph("Executive Summary", sty["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 6))

    override_txt = scoring.get("override_reason") or "None"
    summary_rows = [
        ["FINAL BAND", "SCORE", "RISK LEVEL", "CLASSIFICATION", "OVERRIDE"],
        [
            Paragraph(f"<font color='#{bc.hexval()[2:]}' size='16'><b>{final_band:.1f}/9.0</b></font>", sty["body"]),
            Paragraph(f"<b>{final_score:.1f}/100</b>", sty["body"]),
            Paragraph(f"<b>{risk_level}</b>", sty["body"]),
            Paragraph(classification, sty["body"]),
            Paragraph(override_txt, sty["small"]),
        ]
    ]
    story.append(_table(summary_rows, [3.2*cm, 3*cm, 4*cm, 4.3*cm, None]))
    story.append(Spacer(1, 10))

    # ── VESSEL INFORMATION ─────────────────────────────────────────────
    story.append(Paragraph("Vessel Information", sty["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 4))

    dims = vinfo.get("dimensions", {})
    ton  = dims.get("tonnage", {})
    age  = datetime.now().year - int(vinfo["built_year"]) if vinfo.get("built_year") else "N/A"
    vi_rows = [
        ["Field", "Value", "Field", "Value"],
        ["Vessel Name",   vessel_info.get("vessel_name","N/A"),   "Vessel Type",  vinfo.get("vessel_type","N/A")],
        ["IMO Number",    vessel_info.get("imo_number","N/A"),    "Flag State",   vinfo.get("flag_state","N/A")],
        ["Built Year",    str(vinfo.get("built_year","N/A")),     "Age (years)",  str(age)],
        ["Gross Tonnage", str(ton.get("gross","N/A")),            "DWT",          str(ton.get("dead_weight",ton.get("deadweight","N/A")))],
        ["Call Sign",     vinfo.get("call_sign","N/A"),           "MMSI",         str(vinfo.get("mmsi","N/A"))],
        ["Classification",vinfo.get("classification_society","N/A"), "Status",    vinfo.get("status","N/A")],
    ]
    cw = [3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm]
    story.append(_table(vi_rows, cw))
    story.append(Spacer(1, 10))

    # ── OWNERSHIP ─────────────────────────────────────────────────────
    story.append(Paragraph("Ownership Information", sty["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 4))

    ow_rows = [
        ["Field", "Value", "Field", "Value"],
        ["Current Owner",  ownership.get("current_owner","N/A"),  "Manager",          ownership.get("manager","N/A")],
        ["Beneficial Owner",ownership.get("beneficial_owner","N/A"),"Operator",        ownership.get("operator","N/A")],
        ["Owner Country",  ownership.get("owner_country","N/A"),  "P&I Club",         ownership.get("p_and_i_club","N/A")],
        ["Ownership Changes",str(ownership.get("ownership_changes",0)),"Name Changes", str(ownership.get("name_changes",0))],
        ["Reputation Score",str(ownership.get("reputation_score","N/A")),"Last Change", ownership.get("last_change_date","N/A")],
    ]
    story.append(_table(ow_rows, cw))
    story.append(Spacer(1, 10))

    # ── MODULE BREAKDOWN ───────────────────────────────────────────────
    story.append(Paragraph("Scoring Module Breakdown", sty["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 4))

    mod_rows = [["Module", "Score /100", "Band /9.0", "Weight", "Contribution"]]
    for m in modules:
        b = float(m.get("band", 0))
        bc_m = band_color_hex(b)
        mod_rows.append([
            m.get("module",""),
            f"{m.get('score',0):.1f}",
            Paragraph(f"<font color='#{bc_m.hexval()[2:]}'><b>{b:.1f}</b></font>", sty["body"]),
            f"{m.get('weight_percent',0)}%",
            f"{m.get('weighted_contribution',0):.2f}",
        ])
    story.append(_table(mod_rows, [6*cm, 2.8*cm, 2.8*cm, 2.2*cm, None]))
    story.append(Spacer(1, 10))

    # ── AIS TRACKING ──────────────────────────────────────────────────
    story.append(Paragraph("AIS Tracking", sty["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 4))

    pos = ais.get("position", {})
    mov = ais.get("movement", {})
    anomalies = ais.get("anomalies", {})
    ais_rows = [
        ["Field", "Value", "Field", "Value"],
        ["Latitude",  str(pos.get("latitude","N/A")),   "Longitude",    str(pos.get("longitude","N/A"))],
        ["Speed (kn)",str(mov.get("speed","N/A")),       "Course",       str(mov.get("course","N/A"))],
        ["AIS Status",ais.get("status","N/A"),           "Signal Quality",ais.get("signal_quality","N/A")],
        ["Spoofing",  str(anomalies.get("spoofing_detected",False)), "Dark Activity", str(anomalies.get("dark_activity",False))],
        ["Destination",ais.get("destination","N/A"),     "ETA",          ais.get("eta","N/A")],
    ]
    story.append(_table(ais_rows, cw))
    story.append(Spacer(1, 10))

    # ── RISK & COMPLIANCE ─────────────────────────────────────────────
    story.append(Paragraph("Risk & Compliance", sty["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 4))

    rc_rows = [
        ["Field", "Value", "Field", "Value"],
        ["OFAC Listed",  str(sanctions.get("ofac_hit",False)),   "UN Sanctions",  str(sanctions.get("un_hit",False))],
        ["EU Sanctions", str(sanctions.get("eu_hit",False)),     "Total Hits",    str(sanctions.get("total_hits",0))],
        ["PSC Status",   sanctions.get("psc_status","N/A"),      "Deficiencies",  str(sanctions.get("deficiency_count",0))],
        ["Detention Count",str(sanctions.get("detention_count",0)),"Banned",      str(sanctions.get("banned",False))],
    ]
    story.append(_table(rc_rows, cw))
    story.append(Spacer(1, 10))

    # ── ENVIRONMENTAL ─────────────────────────────────────────────────
    story.append(Paragraph("Environmental & Voyage", sty["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 4))

    cond = weather.get("weather_conditions", {})
    env_rows = [
        ["Field", "Value", "Field", "Value"],
        ["Region",      weather.get("region","N/A"),            "Sea State",     cond.get("sea_state","N/A")],
        ["Wind Speed",  str(cond.get("wind_speed","N/A"))+" kn","Wave Height",   str(cond.get("wave_height","N/A"))+" m"],
        ["Visibility",  cond.get("visibility","N/A"),           "Temperature",   str(cond.get("temperature","N/A"))+" °C"],
        ["Piracy Zone", str(weather.get("piracy_zone",False)),  "War Zone",      str(weather.get("war_zone",False))],
        ["Storm Warning",str(weather.get("storm_warning",False)),"Voyage Risk",  weather.get("route_risk_assessment","N/A")],
    ]
    story.append(_table(env_rows, cw))
    story.append(Spacer(1, 10))

    # ── ALERTS ────────────────────────────────────────────────────────
    if alerts:
        story.append(Paragraph("Alerts & Risk Factors", sty["h2"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
        story.append(Spacer(1, 4))

        alert_rows = [["Severity", "Type", "Message"]]
        for a in alerts:
            sev = a.get("severity","INFO")
            alert_rows.append([sev, a.get("type",""), a.get("message","")])

        at = Table(alert_rows, colWidths=[2.2*cm, 4.5*cm, None], repeatRows=1)
        alert_style = TableStyle([
            ("FONTNAME",    (0,0),(-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0,0),(-1,-1), 8.5),
            ("BACKGROUND",  (0,0),(-1,0),  colors.HexColor("#7F1D1D")),
            ("TEXTCOLOR",   (0,0),(-1,0),  WHITE),
            ("GRID",        (0,0),(-1,-1), 0.4, BORDER),
            ("LEFTPADDING", (0,0),(-1,-1), 6),
            ("RIGHTPADDING",(0,0),(-1,-1), 6),
            ("TOPPADDING",  (0,0),(-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ])
        for i, a in enumerate(alerts, start=1):
            sev = a.get("severity","INFO")
            bg = colors.HexColor("#FEE2E2") if sev=="CRITICAL" else \
                 colors.HexColor("#FFEDD5") if sev=="HIGH" else \
                 colors.HexColor("#FEF9C3")
            alert_style.add("BACKGROUND", (0,i), (-1,i), bg)
            tc = colors.HexColor("#991B1B") if sev=="CRITICAL" else \
                 colors.HexColor("#92400E") if sev=="HIGH" else DARK
            alert_style.add("TEXTCOLOR", (0,i), (-1,i), tc)
            alert_style.add("FONTNAME",  (0,i), (0,i), "Helvetica-Bold")
        at.setStyle(alert_style)
        story.append(at)
        story.append(Spacer(1, 10))

    # ── FOOTER NOTE ───────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 4))
    footer_sty = ParagraphStyle("footer", parent=base["Normal"], fontSize=7,
                                textColor=SLATE, alignment=TA_CENTER)
    story.append(Paragraph(
        f"Vessel Rating System — Maritime Risk Intelligence | "
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} | "
        f"Confidential — For authorised use only",
        footer_sty
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def get_band_color(band: float) -> str:
    """Get color code for band score (for terminal output)"""
    if band >= 8:
        return "\033[92m"  # Green
    elif band >= 6:
        return "\033[93m"  # Yellow
    elif band >= 4:
        return "\033[91m"  # Orange
    else:
        return "\033[91m"  # Red


def get_band_emoji(band: float) -> str:
    """Get emoji for band score"""
    if band >= 8:
        return "🟢"
    elif band >= 6:
        return "🟡"
    elif band >= 4:
        return "🟠"
    else:
        return "🔴"


def print_console_report(report: Dict[str, Any]) -> None:
    """Pretty print report to console"""
    vessel_info = report.get("vessel_info", {})
    scoring = report.get("scoring", {})
    
    print("\n" + "="*70)
    print(f"  🚢 VESSEL RATING REPORT")
    print("="*70)
    
    print(f"\n📋 VESSEL INFORMATION")
    print(f"  Name: {vessel_info.get('vessel_name', 'N/A')}")
    print(f"  IMO:  {vessel_info.get('imo_number', 'N/A')}")
    print(f"  Time: {vessel_info.get('analysis_timestamp', 'N/A')}")
    
    print(f"\n📊 FINAL RATING")
    band = scoring.get("final_band", 0)
    emoji = get_band_emoji(band)
    print(f"  Band Score:     {emoji} {band:.1f}/9.0")
    print(f"  Final Score:    {scoring.get('final_score', 'N/A'):.1f}/100")
    print(f"  Classification: {scoring.get('classification', 'N/A').upper()}")
    print(f"  Risk Level:     {scoring.get('risk_level', 'N/A')}")
    
    if scoring.get("override_applied"):
        print(f"  ⚠️  Override:     {scoring.get('override_reason', 'N/A')}")
    
    print(f"\n📈 MODULE BREAKDOWN")
    for module in report.get("module_breakdown", []):
        print(f"  {module['emoji']} {module['module']:30} {module['score']:6.1f}/100 (Band: {module['band']:.1f})")
    
    alerts = report.get("alerts", [])
    if alerts:
        print(f"\n⚠️  ALERTS & ANOMALIES ({len(alerts)})")
        for alert in alerts:
            print(f"  {alert['emoji']} [{alert['severity']:8}] {alert['message']}")
    else:
        print(f"\n✅ No critical alerts")
    
    print("\n" + "="*70 + "\n")


def validate_vessel_input(vessel_name: str, imo_number: str) -> Dict[str, Any]:
    """Validate vessel input"""
    errors = []
    
    if not vessel_name or len(vessel_name.strip()) == 0:
        errors.append("Vessel name cannot be empty")
    
    if not imo_number or len(imo_number.strip()) == 0:
        errors.append("IMO number cannot be empty")
    
    if imo_number and len(imo_number.strip()) != 7:
        try:
            int(imo_number)
        except ValueError:
            errors.append("IMO number must be 7 digits")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def get_risk_summary(report: Dict[str, Any]) -> str:
    """Get human-readable risk summary"""
    scoring = report.get("scoring", {})
    alerts = report.get("alerts", [])
    
    critical_alerts = len([a for a in alerts if a["severity"] == "CRITICAL"])
    high_alerts = len([a for a in alerts if a["severity"] == "HIGH"])
    
    band = scoring.get("final_band", 0)
    
    if band >= 8:
        summary = "Excellent vessel - low risk, recommended for operation"
    elif band >= 6:
        summary = "Good vessel - moderate risk, standard monitoring recommended"
    elif band >= 4:
        summary = "Weak vessel - elevated risk, close monitoring required"
    else:
        summary = "Poor vessel - high risk, intervention/denial recommended"
    
    if critical_alerts > 0:
        summary += f" - {critical_alerts} CRITICAL ALERT(S)"
    elif high_alerts > 0:
        summary += f" - {high_alerts} high risk alert(s)"
    
    return summary


def merge_reports(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple vessel reports for comparison"""
    if not reports:
        return {}
    
    comparison = {
        "vessels": [],
        "analysis_time": datetime.now().isoformat(),
        "total_vessels": len(reports),
        "average_band": 0,
        "highest_risk": None,
        "lowest_risk": None
    }
    
    total_band = 0
    for report in reports:
        vessel = {
            "name": report.get("vessel_info", {}).get("vessel_name"),
            "imo": report.get("vessel_info", {}).get("imo_number"),
            "band": report.get("scoring", {}).get("final_band"),
            "classification": report.get("scoring", {}).get("classification"),
        }
        comparison["vessels"].append(vessel)
        total_band += vessel["band"]
        
        # Track extremes
        if comparison["highest_risk"] is None or vessel["band"] < comparison["highest_risk"]["band"]:
            comparison["highest_risk"] = vessel
        
        if comparison["lowest_risk"] is None or vessel["band"] > comparison["lowest_risk"]["band"]:
            comparison["lowest_risk"] = vessel
    
    comparison["average_band"] = total_band / len(reports) if reports else 0
    
    return comparison


# ==================== Comprehensive Reporting Functions ====================

def export_comprehensive_report_json(comprehensive_report: Dict[str, Any], filename: str = None) -> str:
    """Export comprehensive report with all data and band scoring to JSON"""
    if filename is None:
        imo = comprehensive_report.get("vessel_identification", {}).get("imo_number", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_report_{imo}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(comprehensive_report, f, indent=2, default=str)
    
    logger.info(f"Comprehensive JSON report saved to {filename}")
    return filename


def export_comprehensive_report_csv(comprehensive_report: Dict[str, Any], filename: str = None) -> str:
    """Export comprehensive report data to CSV format with band scoring"""
    if filename is None:
        imo = comprehensive_report.get("vessel_identification", {}).get("imo_number", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_data_{imo}_{timestamp}.csv"
    
    # Build CSV with all data sections
    csv_content = "VESSEL COMPREHENSIVE DATA REPORT\n"
    csv_content += f"Generated: {datetime.now().isoformat()}\n\n"
    
    # Vessel identification
    vessel_id = comprehensive_report.get("vessel_identification", {})
    csv_content += "VESSEL IDENTIFICATION\n"
    csv_content += f"Vessel Name,{vessel_id.get('vessel_name', 'N/A')}\n"
    csv_content += f"IMO Number,{vessel_id.get('imo_number', 'N/A')}\n"
    csv_content += f"Report Date,{vessel_id.get('report_date', 'N/A')}\n\n"
    
    # Executive Summary
    exec_summary = comprehensive_report.get("executive_summary", {})
    csv_content += "EXECUTIVE SUMMARY\n"
    csv_content += f"Overall Rating,{exec_summary.get('overall_rating', 'N/A')}/9\n"
    csv_content += f"Band Rating,{exec_summary.get('band_rating', 'N/A')}\n"
    csv_content += f"Risk Classification,{exec_summary.get('risk_classification', 'N/A')}\n"
    csv_content += f"Rating Interpretation,\"{exec_summary.get('rating_interpretation', 'N/A')}\"\n\n"
    
    # Scoring Breakdown
    scoring = comprehensive_report.get("scoring_breakdown", {})
    csv_content += "SCORING BY MODULE\n"
    csv_content += "Module,Raw Score,Normalized Score,Band Rating,Weight %,Weighted Contribution\n"
    for module in scoring.get("modules", []):
        csv_content += f"{module['module_name']},{module['raw_score']:.1f},"
        csv_content += f"{module['normalized_score']:.1f},{module['band_rating']:.1f},"
        csv_content += f"{module['weight_percentage']},{module['weighted_contribution']:.2f}\n"
    csv_content += "\n"
    
    # Detailed Sections
    sections = comprehensive_report.get("detailed_sections", {})
    
    for section_name, section_data in sections.items():
        csv_content += f"{section_name.upper()}\n"
        
        if "collected_data" in section_data:
            csv_content += "DATA POINT,VALUE\n"
            for key, value in section_data["collected_data"].items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        csv_content += f"{key}.{sub_key},{sub_value}\n"
                else:
                    csv_content += f"{key},{value}\n"
        
        if "risk_assessment" in section_data:
            csv_content += "\nRISK ASSESSMENT\n"
            csv_content += "Factor,Status\n"
            for factor, status in section_data["risk_assessment"].items():
                csv_content += f"{factor},{status}\n"
        
        csv_content += "\n"
    
    # Data Quality
    quality = comprehensive_report.get("data_quality_assessment", {})
    csv_content += "DATA QUALITY ASSESSMENT\n"
    sources = quality.get("source_status", {})
    for source, status in sources.items():
        csv_content += f"{source},{status}\n"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    logger.info(f"Comprehensive CSV report saved to {filename}")
    return filename


def export_comprehensive_report_html(comprehensive_report: Dict[str, Any], filename: str = None) -> str:
    """Export comprehensive report to HTML with styling and band scoring visualization"""
    if filename is None:
        imo = comprehensive_report.get("vessel_identification", {}).get("imo_number", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_report_{imo}_{timestamp}.html"
    
    vessel_id = comprehensive_report.get("vessel_identification", {})
    exec_summary = comprehensive_report.get("executive_summary", {})
    scoring = comprehensive_report.get("scoring_breakdown", {})
    sections = comprehensive_report.get("detailed_sections", {})
    
    # Generate band color
    band = exec_summary.get("band_rating", 0)
    if band >= 8:
        band_color = "#4CAF50"  # Green
        band_class = "excellent"
    elif band >= 6:
        band_color = "#FFC107"  # Yellow
        band_class = "good"
    elif band >= 4:
        band_color = "#FF9800"  # Orange
        band_class = "moderate"
    else:
        band_color = "#F44336"  # Red
        band_class = "poor"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Vessel Comprehensive Report - {vessel_id.get('vessel_name')}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; color: #333; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
            h1 {{ font-size: 28px; margin-bottom: 10px; }}
            .vessel-name {{ font-size: 20px; opacity: 0.9; }}
            
            .executive-summary {{ background: white; padding: 25px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .band-rating {{ font-size: 48px; font-weight: bold; color: {band_color}; text-align: center; margin: 20px 0; }}
            .band-rating-text {{ text-align: center; font-size: 18px; margin-bottom: 20px; }}
            
            .section {{ background: white; padding: 25px; margin-bottom: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .section h2 {{ color: #1e3c72; font-size: 20px; margin-bottom: 15px; border-bottom: 2px solid #2a5298; padding-bottom: 10px; }}
            
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th {{ background-color: #2a5298; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px 12px; border-bottom: 1px solid #ddd; }}
            tr:hover {{ background-color: #f9f9f9; }}
            
            .module-score {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 15px 0; }}
            .module-card {{ background: #f9f9f9; padding: 15px; border-radius: 6px; border-left: 4px solid #2a5298; }}
            .module-name {{ font-weight: bold; margin-bottom: 8px; }}
            .module-score-value {{ font-size: 18px; margin: 5px 0; }}
            .module-band {{ color: #2a5298; font-weight: bold; }}
            
            .risk-high {{ background-color: #ffebee; color: #c62828; padding: 10px; border-radius: 4px; margin: 5px 0; }}
            .risk-medium {{ background-color: #fff3e0; color: #e65100; padding: 10px; border-radius: 4px; margin: 5px 0; }}
            .risk-low {{ background-color: #e8f5e9; color: #2e7d32; padding: 10px; border-radius: 4px; margin: 5px 0; }}
            
            footer {{ text-align: center; color: #999; padding: 20px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🚢 VESSEL COMPREHENSIVE REPORT</h1>
                <div class="vessel-name">{vessel_id.get('vessel_name')} (IMO: {vessel_id.get('imo_number')})</div>
                <div class="vessel-name">Generated: {vessel_id.get('report_date')}</div>
            </header>
            
            <div class="executive-summary">
                <h2>Executive Summary</h2>
                <div class="band-rating">{exec_summary.get('band_rating', 'N/A')}/9.0</div>
                <div class="band-rating-text">{exec_summary.get('rating_interpretation', 'N/A')}</div>
                <table>
                    <tr><td><strong>Overall Rating</strong></td><td>{exec_summary.get('overall_rating', 'N/A')}/9</td></tr>
                    <tr><td><strong>Risk Classification</strong></td><td>{exec_summary.get('risk_classification', 'N/A')}</td></tr>
                    <tr><td><strong>Assessment Date</strong></td><td>{exec_summary.get('assessment_date', 'N/A')}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h2>📊 Module Scores & Band Ratings</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Module</th>
                            <th>Raw Score</th>
                            <th>Band Rating</th>
                            <th>Weight %</th>
                            <th>Contribution</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for module in scoring.get("modules", []):
        html += f"""
                        <tr>
                            <td>{module['module_name']}</td>
                            <td>{module['raw_score']:.1f}/100</td>
                            <td><span class="module-band">{module['band_rating']:.1f}/9.0</span></td>
                            <td>{module['weight_percentage']}%</td>
                            <td>{module['weighted_contribution']:.2f}</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
    """
    
    # Add detailed sections
    for section_name, section_data in sections.items():
        section_title = section_name.replace("_", " ").title()
        html += f"""
            <div class="section">
                <h2>{section_title}</h2>
        """
        
        if "collected_data" in section_data:
            html += "<h3>Collected Data</h3><table><tbody>"
            for key, value in section_data["collected_data"].items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        html += f"<tr><td><strong>{key.replace('_', ' ').title()}</strong></td><td>{sub_key.replace('_', ' ').title()}: {sub_value}</td></tr>"
                else:
                    html += f"<tr><td><strong>{key.replace('_', ' ').title()}</strong></td><td>{value}</td></tr>"
            html += "</tbody></table>"
        
        if "risk_assessment" in section_data:
            html += "<h3>Risk Assessment</h3><table><tbody>"
            for factor, status in section_data["risk_assessment"].items():
                if "⚠️" in str(status):
                    css_class = "risk-high"
                elif "✅" in str(status):
                    css_class = "risk-low"
                else:
                    css_class = "risk-medium"
                html += f'<tr><td class="{css_class}"><strong>{factor.replace("_", " ").title()}</strong></td><td class="{css_class}">{status}</td></tr>'
            html += "</tbody></table>"
        
        html += "</div>"
    
    html += f"""
            <footer>
                <p>Vessel Rating System - Comprehensive Maritime Risk Assessment</p>
                <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Comprehensive HTML report saved to {filename}")
    return filename


def create_band_scoring_summary(comprehensive_report: Dict[str, Any]) -> str:
    """Create a text summary of all band scoring across all modules"""
    summary = "\n" + "="*80 + "\n"
    summary += "COMPREHENSIVE DATA & BAND SCORING ANALYSIS\n"
    summary += "="*80 + "\n\n"
    
    vessel_id = comprehensive_report.get("vessel_identification", {})
    summary += f"Vessel: {vessel_id.get('vessel_name')} (IMO: {vessel_id.get('imo_number')})\n"
    summary += f"Report Date: {vessel_id.get('report_date')}\n\n"
    
    exec_summary = comprehensive_report.get("executive_summary", {})
    summary += f"FINAL RATING: {exec_summary.get('band_rating', 'N/A')}/9.0\n"
    summary += f"Risk Level: {exec_summary.get('risk_classification', 'N/A')}\n\n"
    
    summary += "-" * 80 + "\n"
    summary += "MODULE SCORES & BAND RATINGS\n"
    summary += "-" * 80 + "\n\n"
    
    scoring = comprehensive_report.get("scoring_breakdown", {})
    for module in scoring.get("modules", []):
        summary += f"• {module['module_name']}\n"
        summary += f"  Raw Score: {module['raw_score']:.1f}/100\n"
        summary += f"  Band Rating: {module['band_rating']:.1f}/9.0\n"
        summary += f"  Weight: {module['weight_percentage']}%\n"
        summary += f"  Contribution: {module['weighted_contribution']:.2f}\n"
        if module.get('risk_factors'):
            summary += f"  Risk Factors: {', '.join(module['risk_factors'])}\n"
        summary += "\n"
    
    summary += "="*80 + "\n"
    return summary


if __name__ == "__main__":
    # Test utility functions
    test_result = validate_vessel_input("Test Vessel", "9894765")
    print(f"Input validation: {test_result}")

