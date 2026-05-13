import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from scoring_engine.engine import get_scoring_engine
from storage.sources import SOURCE_CLOUD, SOURCE_DEVICE, SOURCE_LOCAL, StorageError, get_storage_manager
from utils.helpers import create_pdf_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HISTORY_FILE = Path(_root) / "local_storage" / "_search_history.json"

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VRS - Maritime Risk Intelligence",
    page_icon="VRS",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── session state init ─────────────────────────────────────────────────────────
def _load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def _save_history(history: list) -> None:
    try:
        HISTORY_FILE.write_text(json.dumps(history, indent=2, default=str), encoding="utf-8")
    except Exception as e:
        logger.warning("Could not persist history: %s", e)

for key, default in [
    ("analysis_result", None),
    ("vessel_data", None),
    ("search_history", None),   # None = not yet loaded
    ("active_page", "Vessels"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Load history from disk once per session
if st.session_state.search_history is None:
    st.session_state.search_history = _load_history()

scoring_engine = get_scoring_engine()
storage_manager = get_storage_manager()

# ── global CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { background:#0A1628; border-right:1px solid #1e3a5f; }
    [data-testid="stSidebar"] * { color:#CBD5E1 !important; }
    .topbar {
        display:flex; justify-content:space-between; align-items:center;
        border:1px solid #E2E8F0; padding:.75rem 1rem; border-radius:8px;
        margin-bottom:1.25rem; background:#FFFFFF;
    }
    .page-header h1 { margin:0 0 .2rem 0; color:#0F172A; font-size:1.55rem; }
    .page-subtitle  { color:#64748B; font-size:.9rem; }
    .section-title  {
        font-size:1rem; font-weight:800; color:#0F172A;
        border-left:4px solid #0066CC; padding-left:.7rem;
        margin:1.25rem 0 .75rem 0;
    }
    .panel { border:1px solid #E2E8F0; border-radius:8px; padding:1rem; background:#FFFFFF; margin-bottom:1rem; }
    .hero  { background:#0F4C81; color:#FFFFFF; border-radius:8px; padding:1.1rem 1.25rem; margin-bottom:1rem; }
    .hero-name { font-size:1.55rem; font-weight:900; }
    .hero-sub  { opacity:.86; font-size:.86rem; margin-top:.2rem; }
    .tags  { display:flex; flex-wrap:wrap; gap:.45rem; margin-top:.75rem; }
    .tag   { background:rgba(255,255,255,.18); border:1px solid rgba(255,255,255,.2);
              padding:.2rem .55rem; border-radius:999px; font-size:.78rem; font-weight:700; }
    .band-wrap   { text-align:center; padding:.75rem 0; }
    .band-circle {
        width:142px; height:142px; border-radius:50%; color:white;
        display:inline-flex; flex-direction:column; align-items:center; justify-content:center;
        box-shadow:0 10px 28px rgba(0,0,0,.16);
    }
    .band-val { font-size:2.7rem; font-weight:900; line-height:1; }
    .band-max { font-size:.88rem; opacity:.78; }
    .info-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.75rem; }
    .info-item { border:1px solid #E2E8F0; border-radius:8px; padding:.65rem .75rem; background:#F8FAFC; }
    .info-lbl  { color:#64748B; text-transform:uppercase; font-weight:800; font-size:.68rem; letter-spacing:.03em; }
    .info-val  { color:#0F172A; font-weight:800; overflow-wrap:anywhere; margin-top:.12rem; }
    .module-card { border:1px solid #E2E8F0; border-radius:8px; padding:.9rem 1rem; background:#FFFFFF; margin-bottom:.75rem; }
    .module-head { display:flex; justify-content:space-between; gap:1rem; align-items:center; margin-bottom:.6rem; }
    .module-name { color:#0F172A; font-weight:900; text-transform:uppercase; font-size:.78rem; letter-spacing:.04em; }
    .badge { border-radius:999px; padding:.16rem .55rem; font-size:.72rem; font-weight:900; white-space:nowrap; }
    .module-score { font-size:1.9rem; font-weight:900; color:#0F172A; line-height:1; }
    .bar  { height:6px; border-radius:999px; background:#E2E8F0; margin-top:.7rem; overflow:hidden; }
    .fill { height:100%; border-radius:999px; }
    .stat-card {
        border:1px solid #E2E8F0; border-radius:8px; padding:1rem 1.2rem;
        background:#FFFFFF; text-align:center;
    }
    .stat-num { font-size:2rem; font-weight:900; color:#0F172A; }
    .stat-lbl { color:#64748B; font-size:.82rem; margin-top:.2rem; }
    .hist-row-ok   { color:#15803D; font-weight:700; }
    .hist-row-fail { color:#DC2626; font-weight:700; }
    .back-btn { margin-bottom:1rem; }
    .err-box {
        border:2px solid #DC2626; border-radius:8px; padding:1rem 1.2rem;
        background:#FEF2F2; color:#7F1D1D;
    }
    .err-title { font-weight:900; font-size:1.05rem; margin-bottom:.4rem; }
    .err-hint  { font-size:.88rem; color:#991B1B; margin-top:.4rem; }
    @media (max-width:900px) { .info-grid { grid-template-columns:1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── helpers ────────────────────────────────────────────────────────────────────
def band_color(band: float) -> str:
    if band >= 8:   return "#00A86B"
    if band >= 7:   return "#00A3C7"
    if band >= 5:   return "#F59E0B"
    if band >= 3:   return "#F97316"
    return "#CC3333"

def band_gradient(band: float) -> str:
    c = band_color(band)
    if band >= 7: return f"linear-gradient(135deg,{c},#007A5A)"
    if band >= 5: return f"linear-gradient(135deg,{c},#B45309)"
    return f"linear-gradient(135deg,{c},#7F1D1D)"

def render_topbar() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d  %H:%M UTC")
    st.markdown(
        f'<div class="topbar"><strong>Vessel Rating System</strong><span>{now}</span></div>',
        unsafe_allow_html=True,
    )

def render_band_circle(band: float, risk_level: str, score: float) -> str:
    return f"""
    <div class="band-wrap">
        <div class="band-circle" style="background:{band_gradient(band)}">
            <div class="band-val">{band:.1f}</div>
            <div class="band-max">/ 9.0</div>
        </div>
        <div style="font-weight:900;margin-top:.5rem;color:{band_color(band)}">{risk_level}</div>
        <div style="color:#64748B;font-size:.82rem">Score: {score:.1f}/100</div>
    </div>"""

def fmt(value) -> str:
    if isinstance(value, bool):  return "Yes" if value else "No"
    if isinstance(value, float): return f"{value:.2f}".rstrip("0").rstrip(".")
    if isinstance(value, dict):  return json.dumps(value, default=str)
    if isinstance(value, list):  return f"{len(value)} item(s)"
    if value in (None, ""):      return "N/A"
    return str(value)

def key_table(rows: list, height: int | None = None) -> None:
    df = pd.DataFrame([{"Parameter": k, "Value": fmt(v)} for k, v in rows])
    st.dataframe(
        df, use_container_width=True, hide_index=True,
        height=height or min(560, 92 + len(rows) * 38),
        column_config={
            "Parameter": st.column_config.TextColumn("Parameter", width="medium"),
            "Value":     st.column_config.TextColumn("Value",     width="large"),
        },
    )

def valid_cert(cert: dict) -> bool:
    return str(cert.get("status", "")).strip().upper() == "VALID" or bool(cert.get("valid", False))

# ── validation ─────────────────────────────────────────────────────────────────
_IMO_RE = re.compile(r"^\d{7}$")

def validate_inputs(name: str, imo: str) -> list[str]:
    """Return list of validation error strings (empty = valid)."""
    errors = []
    name = name.strip()
    imo  = imo.strip()
    if not name:
        errors.append("Vessel Name is required.")
    elif len(name) < 2:
        errors.append("Vessel Name is too short (minimum 2 characters).")
    elif re.match(r"^\d+$", name):
        errors.append("Vessel Name should not be a number — did you swap Name and IMO?")

    if not imo:
        errors.append("IMO Number is required.")
    elif not _IMO_RE.match(imo):
        errors.append(
            f"IMO Number '{imo}' is invalid — must be exactly 7 digits (e.g. 9267962)."
        )
    return errors

# ── history helpers ────────────────────────────────────────────────────────────
def _record_search(
    name: str,
    imo: str,
    source: str,
    success: bool,
    band: float | None = None,
    risk: str | None = None,
    duration_ms: int = 0,
    error: str | None = None,
) -> None:
    entry = {
        "id":          len(st.session_state.search_history) + 1,
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date":        datetime.now().strftime("%Y-%m-%d"),
        "time":        datetime.now().strftime("%H:%M:%S"),
        "vessel_name": name,
        "imo":         imo,
        "source":      source,
        "success":     success,
        "band":        round(band, 2) if band is not None else None,
        "risk_level":  risk or "",
        "duration_ms": duration_ms,
        "error":       error or "",
    }
    st.session_state.search_history.append(entry)
    _save_history(st.session_state.search_history)

# ── analysis runner ────────────────────────────────────────────────────────────
def run_analysis(name: str, imo: str, source: str, uploaded_file=None, cloud_location: str | None = None) -> None:
    t0 = time.time()
    try:
        vessel_data = storage_manager.fetch_vessel_data(
            name, imo, source=source,
            uploaded_file=uploaded_file,
            cloud_location=cloud_location,
        )
    except StorageError:
        dur = int((time.time() - t0) * 1000)
        _record_search(name, imo, source, False, error="Not found in storage", duration_ms=dur)
        st.markdown(
            f"""
            <div class="err-box">
                <div class="err-title">Invalid Vessel Name or IMO Number</div>
                <p>No record found for <strong>"{name}"</strong> with IMO <strong>{imo}</strong>
                in the selected data source.</p>
                <div class="err-hint">
                    Check that:<br>
                    &bull; The vessel name matches exactly (e.g. <em>ADENA</em>, not <em>Adena</em>)<br>
                    &bull; The IMO is the correct 7-digit number<br>
                    &bull; The correct data source is selected<br>
                    &bull; The vessel exists in the local_storage database
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    report = scoring_engine.generate_report(name, imo, vessel_data)
    dur    = int((time.time() - t0) * 1000)

    st.session_state.vessel_data      = vessel_data
    st.session_state.analysis_result  = report

    _record_search(
        name, imo, source, True,
        band=report["scoring"]["final_band"],
        risk=report["scoring"]["risk_level"],
        duration_ms=dur,
    )
    st.rerun()

# ── module reason ──────────────────────────────────────────────────────────────
def module_reason(module: dict) -> str:
    details = module.get("details") or {}
    code    = module.get("code")
    reasons: list[str] = []
    if code == "risk_compliance" and details.get("sanctions_hit"):
        reasons.append("Sanctions were detected, causing a critical score.")
    if code == "ais":
        if details.get("spoofing_detected"): reasons.append("AIS spoofing was detected.")
        if details.get("dark_activity"):     reasons.append("Dark activity was detected.")
        if details.get("ais_gap_hours", 0):  reasons.append(f"AIS gap: {details['ais_gap_hours']} hours.")
    if code == "ownership":
        if details.get("name_changes", 0):       reasons.append(f"{details['name_changes']} name changes reduced stability.")
        if details.get("reputation_score", 1) < .5: reasons.append("Low owner/manager reputation.")
    if code == "environmental":
        if details.get("wave_height", 0) > 2.5: reasons.append(f"Wave height {details['wave_height']}m.")
        if details.get("piracy_zone"):           reasons.append("Piracy-zone exposure.")
        if details.get("war_zone"):              reasons.append("War-zone exposure.")
    if code == "general_info":
        if details.get("vessel_age", 0) > 20:   reasons.append(f"Vessel age: {details['vessel_age']} years.")
        if details.get("classification_society"): reasons.append(f"Society: {details['classification_society']}.")
    if reasons:
        return " ".join(reasons)
    score = module.get("score", 0)
    if score >= 80: return "No major negative risk factors detected in this module."
    if score >= 50: return "Some risk factors present, but not critical."
    return "Major risk factors detected in this module."

# ── render helpers ─────────────────────────────────────────────────────────────
def render_module_breakdown(report: dict) -> None:
    for module in report["module_breakdown"]:
        color = band_color(float(module.get("band", 0)))
        score = max(0, min(100, int(module.get("score", 0))))
        title = f"{module['module']} — Score {module['score']:.0f}/100 | Band {module['band']:.1f}/9.0"
        with st.expander(title, expanded=module.get("band", 9) < 4):
            st.markdown(
                f"""
                <div class="module-card">
                    <div class="module-head">
                        <div class="module-name">{module['module']}</div>
                        <div class="badge" style="background:{color}22;color:{color}">{module['weight_percent']}% weight</div>
                    </div>
                    <div class="module-score">{module['score']:.0f}<span style="font-size:.9rem;color:#64748B">/100</span></div>
                    <div style="color:#64748B;margin-top:.25rem">Band: <strong style="color:{color}">{module['band']:.1f}/9.0</strong>
                    | Weighted: <strong>{module['weighted_contribution']:.2f}</strong></div>
                    <div class="bar"><div class="fill" style="width:{score}%;background:{color}"></div></div>
                </div>""",
                unsafe_allow_html=True,
            )
            st.markdown("**Why this score**")
            st.write(module_reason(module))
            details = module.get("details") or {}
            if details:
                key_table([(k.replace("_", " ").title(), v) for k, v in details.items()])

def render_charts(modules: list[dict]) -> None:
    rows = [
        {
            "module":   m["module"],
            "short":    m["module"].replace(" Information", "").replace(" & ", " + ")[:18],
            "band":     float(m.get("band", 0)),
            "score":    float(m.get("score", 0)),
            "weight":   float(m.get("weight_percent", 0)),
            "weighted": float(m.get("weighted_contribution", 0)),
            "color":    band_color(float(m.get("band", 0))),
        }
        for m in modules
    ]
    ordered  = sorted(rows, key=lambda r: r["band"])
    weighted = sorted(rows, key=lambda r: r["weighted"], reverse=True)
    radar    = rows + [rows[0]] if rows else []

    band_fig = go.Figure()
    for x0, x1, col in [(0,3,"#FEE2E2"),(3,5,"#FFEDD5"),(5,7,"#FEF9C3"),(7,9,"#DCFCE7")]:
        band_fig.add_vrect(x0=x0, x1=x1, fillcolor=col, opacity=.35, line_width=0)
    band_fig.add_trace(go.Bar(
        x=[r["band"] for r in ordered], y=[r["short"] for r in ordered],
        orientation="h", marker={"color":[r["color"] for r in ordered]},
        text=[f"{r['band']:.1f}" for r in ordered], textposition="outside",
        customdata=[[r["module"], r["score"]] for r in ordered],
        hovertemplate="<b>%{customdata[0]}</b><br>Band:%{x:.1f}/9<br>Score:%{customdata[1]:.0f}/100<extra></extra>",
    ))
    band_fig.update_layout(height=360,margin={"l":12,"r":42,"t":22,"b":28},
        xaxis={"range":[0,9.4],"dtick":1,"title":"Band score"},yaxis={"title":None},
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",showlegend=False)

    radar_fig = go.Figure(go.Scatterpolar(
        r=[r["band"] for r in radar], theta=[r["short"] for r in radar],
        fill="toself", fillcolor="rgba(0,102,204,.18)",
        line={"color":"#0066CC","width":3}, marker={"size":7,"color":[r["color"] for r in radar]},
    ))
    radar_fig.update_layout(height=360,margin={"l":34,"r":34,"t":24,"b":24},
        polar={"radialaxis":{"range":[0,9],"dtick":3}},
        paper_bgcolor="rgba(0,0,0,0)",showlegend=False)

    impact_fig = go.Figure(go.Bar(
        x=[r["short"] for r in weighted], y=[r["weighted"] for r in weighted],
        marker={"color":[r["color"] for r in weighted]},
        text=[f"{r['weighted']:.1f}" for r in weighted], textposition="outside",
    ))
    impact_fig.update_layout(height=360,margin={"l":24,"r":24,"t":22,"b":80},
        yaxis={"title":"Weighted contribution"},xaxis={"tickangle":-25},
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",showlegend=False)

    t1, t2, t3 = st.tabs(["Band Ranking","Risk Shape","Weight Impact"])
    with t1: st.plotly_chart(band_fig,   use_container_width=True, config={"displayModeBar":False})
    with t2: st.plotly_chart(radar_fig,  use_container_width=True, config={"displayModeBar":False})
    with t3: st.plotly_chart(impact_fig, use_container_width=True, config={"displayModeBar":False})

# ── sidebar ────────────────────────────────────────────────────────────────────
def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("### VRS")
        st.caption("Maritime Risk Intelligence")
        history_count = len(st.session_state.search_history)
        page = st.radio(
            "Navigation",
            ["Vessels", "Dashboard", "History", "Settings"],
            label_visibility="collapsed",
            key="nav_radio",
        )
        if history_count:
            st.markdown(f"---\n**{history_count}** search{'es' if history_count != 1 else ''} recorded")
        else:
            st.markdown("---")
        st.caption("Storage-enabled rating system")
    return page

# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

def page_vessels() -> None:
    render_topbar()
    st.markdown(
        '<div class="page-header"><h1>Vessel Search & Analysis</h1>'
        '<div class="page-subtitle">Search by exact Vessel Name and IMO Number, then run the rating engine.</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        vessel_name = st.text_input("Vessel Name", placeholder="e.g. ADENA", key="inp_name")
    with col2:
        imo_number  = st.text_input("IMO Number", placeholder="e.g. 9254862 (7 digits)", key="inp_imo")
    with col3:
        st.selectbox("Analysis Type", ["Full Assessment", "Quick Scan", "Compliance Check"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    s1, s2 = st.columns([1, 2])
    source_map = {"Local storage": SOURCE_LOCAL, "Device file": SOURCE_DEVICE, "Cloud storage": SOURCE_CLOUD}
    with s1:
        source_label = st.radio("Pull data from", list(source_map.keys()), horizontal=True)
    source = source_map[source_label]
    uploaded_file = cloud_location = None
    with s2:
        if source == SOURCE_DEVICE:
            uploaded_file = st.file_uploader("Choose JSON or CSV", type=["json", "csv"])
        elif source == SOURCE_CLOUD:
            cloud_location = st.text_input("Cloud storage path or URL")
        else:
            st.info("Searching 1,791 vessels in ./local_storage")
    st.markdown("</div>", unsafe_allow_html=True)

    b1, b2, b3 = st.columns(3)
    with b1:
        analyze = st.button("Analyze Vessel", type="primary", use_container_width=True)
    with b2:
        sample  = st.button("Load Sample (HOOT)", use_container_width=True)
    with b3:
        if st.button("Clear Result", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.vessel_data     = None
            st.rerun()

    if analyze:
        name = vessel_name.strip().upper()
        imo  = imo_number.strip()
        errors = validate_inputs(name, imo)
        if errors:
            for err in errors:
                st.markdown(
                    f'<div class="err-box"><div class="err-title">Validation Error</div><p>{err}</p></div>',
                    unsafe_allow_html=True,
                )
        else:
            with st.spinner(f"Searching for {name} / IMO {imo}…"):
                run_analysis(name, imo, source, uploaded_file, cloud_location)

    if sample:
        with st.spinner("Loading sample vessel…"):
            run_analysis("HOOT", "9267962", SOURCE_LOCAL)

    history = st.session_state.search_history
    if history:
        recent = list(reversed(history[-10:]))
        st.markdown('<div class="section-title">Recent Searches</div>', unsafe_allow_html=True)
        st.dataframe(
            pd.DataFrame([
                {
                    "Date":        h["date"],
                    "Time":        h["time"],
                    "Vessel Name": h["vessel_name"],
                    "IMO":         h["imo"],
                    "Band":        f"{h['band']:.1f}/9.0" if h["success"] and h["band"] is not None else "—",
                    "Risk Level":  h["risk_level"] if h["success"] else "—",
                    "Status":      "Found" if h["success"] else "Not Found",
                    "Duration":    f"{h['duration_ms']} ms",
                }
                for h in recent
            ]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Band":   st.column_config.TextColumn("Band",      width="small"),
                "Status": st.column_config.TextColumn("Status",    width="small"),
            },
        )


def page_results() -> None:
    report      = st.session_state.analysis_result
    vessel_data = st.session_state.vessel_data or {}
    scoring     = report["scoring"]
    vessel_info = report["vessel_info"]
    modules     = report["module_breakdown"]
    vinfo       = vessel_data.get("vessel_info",  {})
    ownership   = vessel_data.get("ownership",    {})
    ais         = vessel_data.get("ais_data",     {})
    pos         = ais.get("position",  {})
    mov         = ais.get("movement",  {})
    dims        = vinfo.get("dimensions", {})
    ton         = dims.get("tonnage", {})

    render_topbar()

    # ── Back button ────────────────────────────────────────────────────────────
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to Search", key="back_btn"):
        st.session_state.analysis_result = None
        st.session_state.vessel_data     = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    age  = datetime.now().year - int(vinfo["built_year"]) if vinfo.get("built_year") else "N/A"
    flag = vinfo.get("flag_state") or vinfo.get("flag") or "Unknown"
    override_tag = "Override Applied" if scoring.get("override_applied") else "Normal Assessment"

    left, right = st.columns([3, 1])
    with left:
        st.markdown(
            f"""
            <div class="hero">
                <div class="hero-name">{vessel_info.get('vessel_name','Vessel')}</div>
                <div class="hero-sub">IMO: {vessel_info.get('imo_number','N/A')} &nbsp;|&nbsp;
                Analysis: {vessel_info.get('analysis_timestamp','')[:19]} UTC</div>
                <div class="tags">
                    <span class="tag">{vinfo.get('vessel_type','Unknown')}</span>
                    <span class="tag">{flag}</span>
                    <span class="tag">Age: {age} yrs</span>
                    <span class="tag">{override_tag}</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(render_band_circle(scoring["final_band"], scoring["risk_level"], scoring["final_score"]),
                    unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="info-grid">
            <div class="info-item"><div class="info-lbl">Gross Tonnage</div><div class="info-val">{ton.get('gross','N/A')}</div></div>
            <div class="info-item"><div class="info-lbl">Owner</div><div class="info-val">{ownership.get('current_owner','N/A')}</div></div>
            <div class="info-item"><div class="info-lbl">Manager</div><div class="info-val">{ownership.get('manager','N/A')}</div></div>
            <div class="info-item"><div class="info-lbl">Position</div><div class="info-val">{pos.get('latitude','N/A')}, {pos.get('longitude','N/A')}</div></div>
            <div class="info-item"><div class="info-lbl">Speed</div><div class="info-val">{mov.get('speed','N/A')} kn</div></div>
            <div class="info-item"><div class="info-lbl">Classification</div><div class="info-val">{vinfo.get('classification_society','N/A')}</div></div>
        </div>""",
        unsafe_allow_html=True,
    )

    if report.get("alerts"):
        st.markdown('<div class="section-title">Alerts & Risk Factors</div>', unsafe_allow_html=True)
        for alert in report["alerts"][:8]:
            sev = alert.get("severity", "INFO")
            msg = f"{sev}: {alert.get('message','')}"
            if sev == "CRITICAL": st.error(msg)
            elif sev == "HIGH":   st.warning(msg)
            else:                 st.info(msg)

    st.markdown('<div class="section-title">Scoring Module Breakdown</div>', unsafe_allow_html=True)
    render_module_breakdown(report)

    st.markdown('<div class="section-title">Comprehensive Data Analysis Report</div>', unsafe_allow_html=True)
    tabs = st.tabs(["Overview","General Info","Ownership","AIS Tracking","Risk & Compliance","Environmental","Data Quality"])

    with tabs[0]:
        st.markdown("#### Rating Snapshot")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Final Band",  f"{scoring['final_band']:.1f}/9.0")
        m2.metric("Final Score", f"{scoring['final_score']:.1f}/100")
        m3.metric("Risk Level",  scoring.get("risk_level","Unknown"))
        m4.metric("Override",    scoring.get("override_reason") or "None")
        if scoring.get("override_applied"):
            st.warning(f"Override applied: {scoring.get('override_reason','N/A')}")
        st.markdown("#### Module Band Scores")
        render_charts(modules)
        st.markdown("#### Summary")
        st.info(report.get("summary","No summary available."))

    with tabs[1]:
        key_table([
            ("Vessel Name",            vessel_info.get("vessel_name","N/A")),
            ("IMO Number",             vessel_info.get("imo_number","N/A")),
            ("Vessel Type",            vinfo.get("vessel_type","N/A")),
            ("Built Year",             vinfo.get("built_year","N/A")),
            ("Age (Years)",            age),
            ("Flag State",             flag),
            ("Port of Registry",       vinfo.get("port_of_registry","N/A")),
            ("Call Sign",              vinfo.get("call_sign","N/A")),
            ("MMSI",                   vinfo.get("mmsi","N/A")),
            ("Classification Society", vinfo.get("classification_society","N/A")),
            ("Status",                 vinfo.get("status","N/A")),
            ("Length (m)",             dims.get("length","N/A")),
            ("Width (m)",              dims.get("width","N/A")),
            ("Draught (m)",            dims.get("draught", dims.get("depth","N/A"))),
            ("Gross Tonnage",          ton.get("gross","N/A")),
            ("Net Tonnage",            ton.get("net","N/A")),
            ("Deadweight Tonnage",     ton.get("dead_weight","N/A")),
        ], height=560)

    with tabs[2]:
        key_table([
            ("Current Owner",      ownership.get("current_owner","N/A")),
            ("Owner Country",      ownership.get("owner_country","N/A")),
            ("Manager",            ownership.get("manager","N/A")),
            ("Operator",           ownership.get("operator","N/A")),
            ("Beneficial Owner",   ownership.get("beneficial_owner","N/A")),
            ("Ownership Changes",  ownership.get("ownership_changes",0)),
            ("Name Changes",       ownership.get("name_changes",0)),
            ("Last Change Date",   ownership.get("last_change_date","N/A")),
            ("Owner Sanctions",    bool(ownership.get("owner_sanctioned",False))),
            ("Manager Reputation", ownership.get("manager_reputation","N/A")),
        ])

    with tabs[3]:
        anomalies = ais.get("anomalies", {})
        key_table([
            ("Latitude",            pos.get("latitude","N/A")),
            ("Longitude",           pos.get("longitude","N/A")),
            ("Speed (knots)",       mov.get("speed","N/A")),
            ("Course",              mov.get("course","N/A")),
            ("Heading",             mov.get("heading","N/A")),
            ("Last Update",         pos.get("timestamp","N/A")),
            ("AIS Status",          ais.get("status","N/A")),
            ("Signal Quality",      ais.get("signal_quality","N/A")),
            ("Accuracy",            ais.get("accuracy","N/A")),
            ("Spoofing Risk",       anomalies.get("spoofing_detected",False)),
            ("Dark Activity",       anomalies.get("dark_activity",False)),
            ("STS Transfer Events", anomalies.get("sts_transfer_events","N/A")),
        ])
        if pos.get("latitude") and pos.get("longitude"):
            st.info(f"Position: {pos['latitude']}, {pos['longitude']} | Speed: {mov.get('speed','N/A')} kn")

    with tabs[4]:
        sanctions = vessel_data.get("sanctions", {})
        key_table([
            ("OFAC Listed",      sanctions.get("ofac_hit",False)),
            ("UN Sanctions",     sanctions.get("un_hit",False)),
            ("EU Sanctions",     sanctions.get("eu_hit",False)),
            ("Total Hits",       sanctions.get("total_hits", len(sanctions.get("sanctioned_entities",[])))),
            ("Last Violation",   sanctions.get("last_violation_date","None")),
            ("Detention History",sanctions.get("detention_count",0)),
            ("Port State Control",sanctions.get("psc_status","N/A")),
            ("Deficiency Count", sanctions.get("deficiency_count",0)),
            ("Banning Status",   sanctions.get("banned",False)),
            ("Trade Route Risk", sanctions.get("route_risk_level","N/A")),
        ])
        st.error("Highest-impact module on final rating.")

    with tabs[5]:
        weather    = vessel_data.get("weather", {})
        conditions = weather.get("weather_conditions", {})
        key_table([
            ("Current Region",  weather.get("region","N/A")),
            ("Temperature",     f"{conditions.get('temperature',weather.get('temperature','N/A'))} C"),
            ("Wind Speed",      f"{conditions.get('wind_speed',weather.get('wind_speed','N/A'))} m/s"),
            ("Wave Height",     f"{conditions.get('wave_height',weather.get('wave_height','N/A'))}m"),
            ("Sea State",       conditions.get("sea_state",weather.get("sea_state","N/A"))),
            ("Piracy Zone",     weather.get("piracy_zone",False)),
            ("War Zone",        weather.get("war_zone",False)),
            ("Storm Area",      weather.get("storm_area",weather.get("storm_warning",False))),
            ("Ice Zone",        weather.get("ice_zone",False)),
            ("Voyage Risk",     weather.get("route_risk_assessment","N/A")),
        ])

    with tabs[6]:
        st.dataframe(pd.DataFrame([
            {"Data Source":"Vessel Information","Last Updated":vinfo.get("last_updated","Unknown"),"Status":"Loaded"},
            {"Data Source":"Ownership Data",    "Last Updated":ownership.get("last_updated","Unknown"),"Status":"Loaded"},
            {"Data Source":"AIS Tracking",      "Last Updated":pos.get("timestamp","Unknown"),"Status":"Loaded"},
            {"Data Source":"Sanctions Check",   "Last Updated":vessel_data.get("sanctions",{}).get("last_checked","Unknown"),"Status":"Loaded"},
            {"Data Source":"Weather Data",      "Last Updated":weather.get("last_updated","Unknown"),"Status":"Loaded"},
            {"Data Source":"Compliance Records","Last Updated":vessel_data.get("compliance",{}).get("last_updated","Unknown"),"Status":"Loaded"},
        ]), use_container_width=True, hide_index=True)
        st.info("Data quality reflects fields loaded from the selected storage source.")

    st.markdown('<div class="section-title">Export & Download</div>', unsafe_allow_html=True)
    e1, e2, e3, e4 = st.columns(4)
    imo_str  = vessel_info.get("imo_number","vessel")
    vname_str = vessel_info.get("vessel_name","vessel").replace(" ","_")
    ts_str   = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    with e1:
        st.download_button("PDF Report", data=create_pdf_report(report, vessel_data),
            file_name=f"Vessel_Report_{vname_str}_{ts_str}.pdf", mime="application/pdf",
            use_container_width=True)
    with e2:
        st.download_button("JSON Report", data=json.dumps(report, indent=2, default=str),
            file_name=f"vessel_{imo_str}.json", mime="application/json",
            use_container_width=True)
    with e3:
        csv_data = "Module,Score,Band,Weight\n" + "\n".join(
            f"{m['module']},{m['score']},{m['band']},{m['weight_percent']}" for m in modules)
        st.download_button("CSV Summary", data=csv_data,
            file_name=f"vessel_{imo_str}_summary.csv", mime="text/csv",
            use_container_width=True)
    with e4:
        if st.button("New Analysis", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.vessel_data     = None
            st.rerun()


def page_dashboard() -> None:
    render_topbar()
    st.markdown('<div class="page-header"><h1>Fleet Dashboard</h1></div>', unsafe_allow_html=True)
    history = [h for h in st.session_state.search_history if h["success"]]
    if not history:
        st.info("No successful analyses yet. Analyze a vessel first.")
        return
    bands = [h["band"] for h in history if h["band"] is not None]
    avg        = sum(bands) / len(bands) if bands else 0
    high_risk  = sum(1 for b in bands if b < 5)
    critical   = sum(1 for b in bands if b < 3)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fleet Avg Band",    f"{avg:.1f}/9.0")
    c2.metric("High Risk Vessels", high_risk)
    c3.metric("Critical (<3.0)",   critical)
    c4.metric("Total Analyzed",    len(history))

    if bands:
        st.markdown('<div class="section-title">Band Distribution</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Histogram(
            x=bands, nbinsx=18,
            marker={"color": ["#CC3333" if b < 3 else "#F97316" if b < 5 else "#F59E0B" if b < 7 else "#00A86B" for b in bands]},
        ))
        fig.update_layout(height=300, margin={"l":20,"r":20,"t":20,"b":40},
            xaxis={"title":"Band (0-9)","range":[0,9]},
            yaxis={"title":"Vessel count"},
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})


def page_history() -> None:
    render_topbar()
    st.markdown(
        '<div class="page-header"><h1>Historical Usage Portal</h1>'
        '<div class="page-subtitle">Complete log of all vessel searches with date, time, result, and performance metrics.</div></div>',
        unsafe_allow_html=True,
    )

    history = st.session_state.search_history

    # ── summary stat cards ─────────────────────────────────────────────────────
    total       = len(history)
    successful  = sum(1 for h in history if h["success"])
    failed      = total - successful
    today_str   = datetime.now().strftime("%Y-%m-%d")
    today_cnt   = sum(1 for h in history if h["date"] == today_str)
    unique_imos = len({h["imo"] for h in history})
    avg_ms      = int(sum(h["duration_ms"] for h in history) / total) if total else 0
    bands_ok    = [h["band"] for h in history if h["success"] and h["band"] is not None]
    avg_band    = sum(bands_ok) / len(bands_ok) if bands_ok else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, num, lbl in [
        (c1, total,         "Total Searches"),
        (c2, successful,    "Successful"),
        (c3, failed,        "Not Found"),
        (c4, today_cnt,     "Today"),
        (c5, unique_imos,   "Unique Vessels"),
        (c6, f"{avg_band:.1f}", "Avg Band"),
    ]:
        col.markdown(
            f'<div class="stat-card"><div class="stat-num">{num}</div><div class="stat-lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    if not history:
        st.info("No search history yet. Start analyzing vessels.")
        return

    st.markdown("")  # spacer

    # ── timeline chart ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Search Activity Timeline</div>', unsafe_allow_html=True)
    df_hist = pd.DataFrame(history)
    df_hist["dt"] = pd.to_datetime(df_hist["timestamp"])
    by_date = df_hist.groupby("date").agg(
        searches=("id", "count"),
        found=("success", "sum"),
    ).reset_index()
    by_date["not_found"] = by_date["searches"] - by_date["found"]

    timeline = go.Figure()
    timeline.add_trace(go.Bar(name="Found",     x=by_date["date"], y=by_date["found"],     marker_color="#00A86B"))
    timeline.add_trace(go.Bar(name="Not Found", x=by_date["date"], y=by_date["not_found"], marker_color="#CC3333"))
    timeline.update_layout(
        barmode="stack", height=240, showlegend=True,
        margin={"l":20,"r":20,"t":10,"b":40},
        xaxis={"title":None}, yaxis={"title":"Searches"},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend={"orientation":"h","y":1.12},
    )
    st.plotly_chart(timeline, use_container_width=True, config={"displayModeBar":False})

    # ── filters ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Search Log</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([2, 2, 1, 1])
    with f1:
        name_filter = st.text_input("Filter by vessel name", placeholder="e.g. ADENA", key="hist_name_filter")
    with f2:
        imo_filter  = st.text_input("Filter by IMO", placeholder="e.g. 9254862", key="hist_imo_filter")
    with f3:
        status_opts = ["All", "Found", "Not Found"]
        status_filter = st.selectbox("Status", status_opts, key="hist_status_filter")
    with f4:
        dates = sorted({h["date"] for h in history}, reverse=True)
        date_filter = st.selectbox("Date", ["All dates"] + dates, key="hist_date_filter")

    filtered = list(reversed(history))
    if name_filter.strip():
        filtered = [h for h in filtered if name_filter.strip().upper() in h["vessel_name"].upper()]
    if imo_filter.strip():
        filtered = [h for h in filtered if imo_filter.strip() in h["imo"]]
    if status_filter == "Found":
        filtered = [h for h in filtered if h["success"]]
    elif status_filter == "Not Found":
        filtered = [h for h in filtered if not h["success"]]
    if date_filter != "All dates":
        filtered = [h for h in filtered if h["date"] == date_filter]

    st.caption(f"Showing {len(filtered)} of {total} records")

    if filtered:
        log_df = pd.DataFrame([
            {
                "#":           h["id"],
                "Date":        h["date"],
                "Time":        h["time"],
                "Vessel Name": h["vessel_name"],
                "IMO":         h["imo"],
                "Source":      h.get("source","local_storage"),
                "Status":      "Found" if h["success"] else "Not Found",
                "Band":        f"{h['band']:.1f}" if h["success"] and h["band"] is not None else "—",
                "Risk Level":  h["risk_level"] if h["success"] else h.get("error",""),
                "Duration":    f"{h['duration_ms']} ms",
            }
            for h in filtered
        ])
        st.dataframe(
            log_df,
            use_container_width=True,
            hide_index=True,
            height=min(600, 56 + len(filtered) * 38),
            column_config={
                "#":           st.column_config.NumberColumn("#",          width="small"),
                "Date":        st.column_config.TextColumn("Date",         width="small"),
                "Time":        st.column_config.TextColumn("Time",         width="small"),
                "Vessel Name": st.column_config.TextColumn("Vessel Name",  width="medium"),
                "IMO":         st.column_config.TextColumn("IMO",          width="small"),
                "Source":      st.column_config.TextColumn("Source",       width="small"),
                "Status":      st.column_config.TextColumn("Status",       width="small"),
                "Band":        st.column_config.TextColumn("Band",         width="small"),
                "Risk Level":  st.column_config.TextColumn("Risk Level",   width="medium"),
                "Duration":    st.column_config.TextColumn("Duration",     width="small"),
            },
        )

        # ── export ─────────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">Export History</div>', unsafe_allow_html=True)
        ex1, ex2, ex3 = st.columns([1, 1, 2])
        with ex1:
            st.download_button(
                "Export as CSV",
                data=log_df.to_csv(index=False),
                file_name=f"vrs_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with ex2:
            st.download_button(
                "Export as JSON",
                data=json.dumps(filtered, indent=2, default=str),
                file_name=f"vrs_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )
        with ex3:
            if st.button("Clear All History", type="secondary", use_container_width=True):
                st.session_state.search_history = []
                _save_history([])
                st.success("History cleared.")
                st.rerun()
    else:
        st.info("No records match the selected filters.")


def page_settings() -> None:
    render_topbar()
    st.markdown('<div class="page-header"><h1>Settings</h1></div>', unsafe_allow_html=True)
    st.json({
        "version":        "1.0.0",
        "storage_sources":["Local storage","Device file import","Cloud storage path/URL"],
        "band_scale":     "0.0 – 9.0",
        "vessels_loaded": 1791,
        "history_file":   str(HISTORY_FILE),
    })


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    page = render_sidebar()
    if page == "Vessels":
        if st.session_state.analysis_result:
            page_results()
        else:
            page_vessels()
    elif page == "Dashboard":
        page_dashboard()
    elif page == "History":
        page_history()
    else:
        page_settings()


if __name__ == "__main__":
    main()
