"""
app.py — CAMPUSX AI Smart Campus Simulator
Streamlit dashboard: campus overview, building drill-down, anomaly
detection, AI advisor, and a simple 3-hour energy prediction.

Layout: fixed left sidebar (branding, status, building selector,
high-level metrics) + a scrolling main panel (campus map, real-world
map, building detail, anomalies, AI advisor, prediction).
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import time

from data import (
    generate_campus_data, inject_anomaly, LOCATIONS, COORDINATES,
    CAMPUS_NAME, CAMPUS_CENTER, generate_24h_history, generate_week_dataframe,
)
from detector import detect_anomalies, TOLERANCE as DEFAULT_TOLERANCE
from ai import get_ai_recommendation
from icons import icon, status_icon
from sustainability import (
    energy_to_cost, energy_to_co2, anomaly_savings, rank_buildings,
    green_score, green_grade, DEFAULT_RATE_PER_KWH, DEFAULT_CO2_PER_KWH,
)
from weather import get_forecast, energy_multiplier

st.set_page_config(page_title="CAMPUSX AI", layout="wide")

# ---------- theme colors (kept in sync with .streamlit/config.toml) ----------
BG = "#0e1117"
CARD_BG = "#161b22"
CARD_BG_HOVER = "#1c2129"
BORDER = "#2a2f3a"
BORDER_HOVER = "#3d4452"
ACCENT = "#22c55e"
TEXT_MUTED = "#8b949e"

# ---------- global CSS polish ----------
st.markdown(f"""
<style>
    .block-container {{ padding-top: 1.6rem; }}

    /* subtle tech gradient + grid backdrop */
    .stApp {{
        background:
            radial-gradient(circle at 12% 0%, rgba(34,197,94,0.07) 0%, rgba(34,197,94,0) 38%),
            radial-gradient(circle at 88% 100%, rgba(88,166,255,0.06) 0%, rgba(88,166,255,0) 40%),
            repeating-linear-gradient(0deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 34px),
            repeating-linear-gradient(90deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 34px),
            {BG};
        background-attachment: fixed;
    }}

    /* skeleton loader shimmer */
    .skeleton {{
        border-radius: 12px;
        background: linear-gradient(100deg, {CARD_BG} 30%, #232a35 50%, {CARD_BG} 70%);
        background-size: 200% 100%;
        animation: shimmer 1.15s ease-in-out infinite;
        border: 1px solid {BORDER};
    }}
    @keyframes shimmer {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}

    /* fixed left sidebar styling */
    section[data-testid="stSidebar"] {{
        background: {CARD_BG};
        border-right: 1px solid {BORDER};
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.4rem;
    }}

    .campusx-header {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.1rem;
    }}
    .campusx-header .logo {{
        color: {ACCENT};
        line-height: 1;
    }}
    .campusx-header h1 {{
        margin: 0;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }}
    .campusx-caption {{
        color: {TEXT_MUTED};
        font-size: 0.85rem;
        margin-bottom: 1.1rem;
    }}

    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.88rem;
        border: 1px solid {BORDER};
        background: {BG};
        transition: border-color 0.2s ease, background 0.2s ease;
    }}
    .status-pill:hover {{
        border-color: {BORDER_HOVER};
    }}

    /* side metric cards */
    .side-metric {{
        background: {BG};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 0.65rem 0.8rem;
        margin-bottom: 0.55rem;
        transition: border-color 0.2s ease, transform 0.15s ease;
    }}
    .side-metric:hover {{
        border-color: {BORDER_HOVER};
        transform: translateX(2px);
    }}
    .side-metric .label {{
        display: flex;
        align-items: center;
        gap: 0.4rem;
        color: {TEXT_MUTED};
        font-size: 0.78rem;
        margin-bottom: 0.2rem;
    }}
    .side-metric .value {{
        font-size: 1.3rem;
        font-weight: 700;
    }}

    .sidebar-heading {{
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: {TEXT_MUTED};
        margin: 1.1rem 0 0.6rem 0;
    }}

    /* building cards, now with a real hover/transition state */
    .building-card {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 1rem 1rem 0.8rem 1rem;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background 0.18s ease;
    }}
    .building-card:hover {{
        transform: translateY(-3px);
        border-color: {BORDER_HOVER};
        background: {CARD_BG_HOVER};
        box-shadow: 0 10px 24px -12px rgba(0, 0, 0, 0.55);
    }}
    .building-card.alert {{
        border-color: #f85149;
    }}
    .building-card.alert:hover {{
        box-shadow: 0 10px 24px -12px rgba(248, 81, 73, 0.35);
    }}
    .building-card .name {{
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .building-card .row {{
        font-size: 0.88rem;
        color: {TEXT_MUTED};
        margin: 0.3rem 0;
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }}
    .severity-bar {{
        height: 5px;
        border-radius: 3px;
        background: {BORDER};
        margin-top: 0.7rem;
        overflow: hidden;
    }}
    .severity-fill {{
        height: 100%;
        border-radius: 3px;
        transition: width 0.3s ease;
    }}

    .section-heading {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 0.2rem 0 0.8rem 0;
        letter-spacing: -0.01em;
    }}

    /* AI advisor cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        transition: border-color 0.18s ease, box-shadow 0.18s ease;
        border-radius: 10px;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: {BORDER_HOVER} !important;
        box-shadow: 0 8px 20px -12px rgba(0, 0, 0, 0.5);
    }}

    /* buttons: smoother hover */
    .stButton > button {{
        transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
    }}

    hr {{ border-color: {BORDER} !important; }}

    /* cosmetic login overlay */
    .login-card {{
        max-width: 420px;
        margin: 5rem auto 0 auto;
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 2.2rem 2rem;
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGIN TOGGLE (always visible in sidebar, even while gated)
# =========================================================
if "login_enabled" not in st.session_state:
    st.session_state.login_enabled = False
if "authed" not in st.session_state:
    st.session_state.authed = False

with st.sidebar:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">'
        f'<span style="color:{ACCENT};">{icon("lock", size=15)}</span>'
        f'<span style="font-size:0.82rem; color:{TEXT_MUTED}; font-weight:600;">Demo Options</span></div>',
        unsafe_allow_html=True,
    )
    st.session_state.login_enabled = st.toggle(
        "Require sign-in overlay", value=st.session_state.login_enabled,
    )
    st.divider()

# ---------- cosmetic login gate (not real auth — for demo realism) ----------
if st.session_state.login_enabled and not st.session_state.authed:
    st.markdown(f"""
    <div class="login-card">
        <div style="display:flex; justify-content:center; margin-bottom:0.8rem; color:{ACCENT};">{icon('building', size=40)}</div>
        <h2 style="margin-bottom:0.2rem;">CAMPUSX AI</h2>
        <p style="color:{TEXT_MUTED}; font-size:0.9rem; margin-bottom:1.6rem;">Facilities Operations Console</p>
    </div>
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        st.text_input("Operator name", placeholder="e.g. Facilities Team", key="login_name")
        if st.button("Sign in", use_container_width=True, type="primary"):
            st.session_state.authed = True
            st.session_state.operator_name = st.session_state.login_name or "Guest"
            st.rerun()
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state.authed = True
            st.session_state.operator_name = "Guest"
            st.rerun()
    st.stop()

# ---------- session state ----------
if "df" not in st.session_state:
    st.session_state.df = generate_campus_data()
if "history" not in st.session_state:
    # keep a short rolling history per location for the prediction chart
    st.session_state.history = {loc: [] for loc in LOCATIONS}
    for loc in LOCATIONS:
        base = st.session_state.df.loc[st.session_state.df.location == loc, "energy"].iloc[0]
        st.session_state.history[loc] = [base + np.random.uniform(-5, 5) for _ in range(6)]
if "trend_24h" not in st.session_state:
    st.session_state.trend_24h = {loc: generate_24h_history(loc, "energy") for loc in LOCATIONS}
if "tolerance" not in st.session_state:
    st.session_state.tolerance = DEFAULT_TOLERANCE
if "rate_per_kwh" not in st.session_state:
    st.session_state.rate_per_kwh = DEFAULT_RATE_PER_KWH
if "co2_per_kwh" not in st.session_state:
    st.session_state.co2_per_kwh = DEFAULT_CO2_PER_KWH
if "week_seed" not in st.session_state:
    st.session_state.week_seed = 0
if "weather_seed" not in st.session_state:
    st.session_state.weather_seed = 0
if "loading" not in st.session_state:
    st.session_state.loading = False

# ---------- skeleton loading flash (triggered by Refresh / Simulate) ----------
if st.session_state.loading:
    st.markdown(
        f'<div class="section-heading">{icon("map", size=18)} Campus Map</div>',
        unsafe_allow_html=True,
    )
    sk_cols = st.columns(len(LOCATIONS))
    for sk_col in sk_cols:
        with sk_col:
            st.markdown('<div class="skeleton" style="height:150px; margin-bottom:0.6rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="skeleton" style="height:280px;"></div>', unsafe_allow_html=True)
    time.sleep(0.55)
    st.session_state.loading = False
    st.rerun()
    st.stop()

df = st.session_state.df
anomalies_preview = detect_anomalies(df, st.session_state.tolerance)

# full-week simulation (weekday vs weekend patterns) + mock weather —
# cached in session_state and only rebuilt when the user asks to reshuffle
week_df_all = generate_week_dataframe(seed_suffix=str(st.session_state.week_seed))
forecast = get_forecast(seed=f"campusx-{st.session_state.weather_seed}")
today_weather = forecast[0]
today_multiplier = energy_multiplier(today_weather["condition"], today_weather["temp_c"])


if not anomalies_preview:
    status_state, status_label = "normal", "Normal"
elif len(anomalies_preview) <= 1:
    status_state, status_label = "warning", "Warning"
else:
    status_state, status_label = "critical", "Critical"


@st.dialog("Detection Settings")
def settings_dialog():
    st.write("Adjust how sensitive the anomaly detector is.")
    new_tol = st.slider(
        "Sensitivity (lower = stricter)", 0.0, 0.5, st.session_state.tolerance, 0.05,
    )
    st.caption(f"A reading must be {new_tol * 100:.0f}% beyond its normal range to be flagged as an anomaly.")

    st.divider()
    st.write("Cost & sustainability assumptions.")
    new_rate = st.slider(
        "Electricity tariff (₹ per kWh)", 4.0, 15.0, st.session_state.rate_per_kwh, 0.5,
    )
    new_co2 = st.slider(
        "Grid CO2 intensity (kg CO2 per kWh)", 0.3, 1.2, st.session_state.co2_per_kwh, 0.01,
    )
    st.caption("Defaults approximate an institutional tariff and India's grid-average emission factor — override with your DISCOM rate and local CEA factor.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Apply", use_container_width=True, type="primary"):
            st.session_state.tolerance = new_tol
            st.session_state.rate_per_kwh = new_rate
            st.session_state.co2_per_kwh = new_co2
            st.session_state.loading = True
            st.rerun()
    with c2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

# =========================================================
# LEFT SIDEBAR — branding, status, building selector, KPIs
# =========================================================
with st.sidebar:
    st.markdown(
        f'<div class="campusx-header"><span class="logo">{icon("logo", size=26)}</span>'
        f'<h1>CAMPUSX AI</h1></div>'
        f'<div class="campusx-caption">AI Smart Campus Simulator</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<span class="status-pill">{status_icon(status_state)} {status_label}</span>',
        unsafe_allow_html=True,
    )

    b1, b2 = st.columns(2)
    with b1:
        if st.button(f"Refresh", icon=":material/refresh:", use_container_width=True):
            st.session_state.df = generate_campus_data()
            st.session_state.loading = True
            st.rerun()
    with b2:
        if st.button(f"Simulate", icon=":material/warning:", use_container_width=True):
            st.session_state.df = inject_anomaly(st.session_state.df, "Library")
            st.session_state.loading = True
            st.rerun()

    if st.button("Settings", icon=":material/tune:", use_container_width=True):
        settings_dialog()

    st.markdown(
        f'<div class="sidebar-heading">{icon("building", size=14)} Building selector</div>',
        unsafe_allow_html=True,
    )
    selected = st.selectbox("Select Building", LOCATIONS, label_visibility="collapsed")

    st.markdown(
        f'<div class="sidebar-heading">{icon("trend", size=14)} Campus KPIs</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"""
    <div class="side-metric">
        <div class="label">{icon('person', size=14)} Occupancy (avg)</div>
        <div class="value">{df['occupancy'].mean():.0f}%</div>
    </div>
    <div class="side-metric">
        <div class="label">{icon('bolt', size=14, color=ACCENT)} Energy (total)</div>
        <div class="value">{df['energy'].sum():.0f} kWh</div>
    </div>
    <div class="side-metric">
        <div class="label">{icon('coin', size=14, color='#eab308')} Est. Cost (total)</div>
        <div class="value">₹{energy_to_cost(df['energy'].sum(), st.session_state.rate_per_kwh):,.0f}</div>
    </div>
    <div class="side-metric">
        <div class="label">{icon('leaf', size=14, color=ACCENT)} CO2 (total)</div>
        <div class="value">{energy_to_co2(df['energy'].sum(), st.session_state.co2_per_kwh):,.0f} kg</div>
    </div>
    <div class="side-metric">
        <div class="label">{icon('droplet', size=14)} Water (avg)</div>
        <div class="value">{df['water'].mean():.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

df = st.session_state.df
sel_row = df[df.location == selected].iloc[0]

# =========================================================
# MAIN PANEL
# =========================================================

# ---------- campus map (styled building cards) ----------
st.markdown(
    f'<div class="section-heading">{icon("map", size=18)} Campus Map</div>',
    unsafe_allow_html=True,
)
anomaly_locations = {a["location"] for a in anomalies_preview}
cols = st.columns(len(LOCATIONS))
for col, (_, row) in zip(cols, df.iterrows()):
    loc = row["location"]
    is_alert = loc in anomaly_locations
    dot = status_icon("critical" if is_alert else "normal")

    # severity = how far energy sits from its baseline midpoint (0-100 bar width)
    from data import BASELINES
    b_low, b_high = BASELINES[loc]["energy"]
    mid, spread = (b_low + b_high) / 2, (b_high - b_low) / 2
    severity_pct = min(100, max(6, abs(row["energy"] - mid) / spread * 55))
    bar_color = "#f85149" if is_alert else ACCENT

    bldg_score = green_score(loc, row["energy"])
    bldg_grade = green_grade(bldg_score)
    grade_color = ACCENT if bldg_score >= 80 else ("#eab308" if bldg_score >= 50 else "#f85149")
    bldg_cost = energy_to_cost(row["energy"], st.session_state.rate_per_kwh)

    with col:
        st.markdown(f"""
        <div class="building-card {'alert' if is_alert else ''}">
            <div class="name">{row['location']} <span>{dot}</span></div>
            <div class="row">{icon('person', size=14)} Occupancy&nbsp; {row['occupancy']}%</div>
            <div class="row">{icon('thermometer', size=14)} Temp&nbsp; {row['temperature']}°C</div>
            <div class="row">{icon('bolt', size=14, color=ACCENT)} Energy&nbsp; {row['energy']} kWh</div>
            <div class="row">{icon('coin', size=14, color='#eab308')} Cost&nbsp; ₹{bldg_cost:,.0f}/hr</div>
            <div class="row">{icon('leaf', size=14, color=grade_color)} Green Score&nbsp;
                <span style="color:{grade_color}; font-weight:700;">{bldg_score} ({bldg_grade})</span></div>
            <div class="severity-bar"><div class="severity-fill" style="width:{severity_pct:.0f}%; background:{bar_color};"></div></div>
        </div>
        """, unsafe_allow_html=True)

        # sparkline: recent energy trend for this building
        spark_hist = st.session_state.history.get(loc, [row["energy"]] * 6)[-10:]
        spark_fig = go.Figure(go.Scatter(
            y=spark_hist, mode="lines", line=dict(color=bar_color, width=2),
            fill="tozeroy",
            fillcolor=f"rgba({'248,81,73' if is_alert else '34,197,94'},0.12)",
        ))
        spark_fig.update_layout(
            height=46,
            margin=dict(t=2, b=2, l=2, r=2),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            showlegend=False,
        )
        st.plotly_chart(spark_fig, use_container_width=True, config={"displayModeBar": False}, key=f"spark_{loc}")

st.divider()

# ---------- real-world campus location ----------
st.markdown(
    f'<div class="section-heading">{icon("pin", size=18)} Real Campus Location — {CAMPUS_NAME}</div>',
    unsafe_allow_html=True,
)

map_df = df.copy()
map_df["lat"] = map_df["location"].map(lambda loc: COORDINATES[loc][0])
map_df["lon"] = map_df["location"].map(lambda loc: COORDINATES[loc][1])
map_df["status"] = map_df["location"].apply(lambda loc: "Anomaly" if loc in anomaly_locations else "Normal")

map_fig = px.scatter_map(
    map_df,
    lat="lat",
    lon="lon",
    color="status",
    color_discrete_map={"Normal": ACCENT, "Anomaly": "#f85149"},
    hover_name="location",
    hover_data={"occupancy": True, "energy": True, "lat": False, "lon": False, "status": False},
    zoom=16,
    height=420,
    center={"lat": CAMPUS_CENTER[0], "lon": CAMPUS_CENTER[1]},
)
map_fig.update_traces(marker=dict(size=18))
map_fig.update_layout(
    map_style="open-street-map",
    margin=dict(t=10, b=10, l=10, r=10),
    paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(font=dict(color="#e6edf3"), bgcolor="rgba(0,0,0,0)"),
)
st.plotly_chart(map_fig, use_container_width=True)
st.caption("Building pins reflect actual campus coordinates.")

st.divider()

# ---------- cost & sustainability ----------
st.markdown(
    f'<div class="section-heading">{icon("leaf", size=18)} Cost & Sustainability</div>',
    unsafe_allow_html=True,
)

ranked = rank_buildings(df, st.session_state.rate_per_kwh, st.session_state.co2_per_kwh)
total_cost = sum(r["cost"] for r in ranked)
total_co2 = sum(r["co2"] for r in ranked)
best, worst = ranked[0], ranked[-1]

s1, s2, s3, s4 = st.columns(4)
s1.metric("Campus Energy Cost", f"₹{total_cost:,.0f}/hr", help=f"At ₹{st.session_state.rate_per_kwh:.1f}/kWh")
s2.metric("Campus Carbon Footprint", f"{total_co2:,.1f} kg CO₂/hr", help=f"At {st.session_state.co2_per_kwh:.2f} kg CO₂/kWh")
s3.metric("Greenest Building", f"{best['location']}", f"{best['score']} ({best['grade']})")
s4.metric("Least Efficient", f"{worst['location']}", f"{worst['score']} ({worst['grade']})", delta_color="inverse")

lb_col, tbl_col = st.columns([3, 2])

with lb_col:
    lb_fig = go.Figure(go.Bar(
        x=[r["score"] for r in ranked],
        y=[r["location"] for r in ranked],
        orientation="h",
        marker_color=[
            ACCENT if r["score"] >= 80 else ("#eab308" if r["score"] >= 50 else "#f85149")
            for r in ranked
        ],
        text=[f"{r['score']} ({r['grade']})" for r in ranked],
        textposition="auto",
    ))
    lb_fig.update_layout(
        title="Green Score Leaderboard",
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e6edf3"),
        margin=dict(t=50, b=30, l=10, r=20),
        xaxis=dict(range=[0, 100], gridcolor=BORDER, title="Score"),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(lb_fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Green Score (0-100) rates each building's current energy draw against its own normal baseline band — higher is more efficient.")

with tbl_col:
    cost_df = pd.DataFrame([
        {
            "Building": r["location"],
            "₹/hr": f"₹{r['cost']:,.0f}",
            "kg CO₂/hr": f"{r['co2']:,.1f}",
            "Grade": r["grade"],
        }
        for r in ranked
    ])
    st.dataframe(cost_df, use_container_width=True, hide_index=True, height=246)

st.divider()

# ---------- weekly pattern (weekday vs weekend) + mock weather ----------
wk_head_col, wk_btn_col = st.columns([5, 1])
with wk_head_col:
    st.markdown(
        f'<div class="section-heading">{icon("history", size=18)} Weekly Pattern & Weather Outlook — {selected}</div>',
        unsafe_allow_html=True,
    )
with wk_btn_col:
    if st.button("Reshuffle", icon=":material/casino:", use_container_width=True):
        st.session_state.week_seed += 1
        st.session_state.weather_seed += 1
        st.rerun()

week_df = week_df_all[week_df_all["location"] == selected]
weekday_avg = week_df[~week_df["is_weekend"]][["occupancy", "energy"]].mean()
weekend_avg = week_df[week_df["is_weekend"]][["occupancy", "energy"]].mean()
energy_delta_pct = (
    (weekend_avg["energy"] - weekday_avg["energy"]) / weekday_avg["energy"] * 100
    if weekday_avg["energy"] else 0
)

wk_chart_col, wk_side_col = st.columns([2, 1])

with wk_chart_col:
    daily = week_df.groupby(["day_index", "day_name", "is_weekend"], as_index=False)[["occupancy", "energy"]].mean()
    daily = daily.sort_values("day_index")
    week_fig = go.Figure(go.Bar(
        x=daily["day_name"], y=daily["energy"],
        marker_color=["#58a6ff" if w else ACCENT for w in daily["is_weekend"]],
        text=[f"{v:.0f}" for v in daily["energy"]],
        textposition="outside",
        name="Avg Energy (kWh)",
    ))
    week_fig.update_layout(
        title="Simulated 7-Day Avg Energy — Weekday vs Weekend",
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e6edf3"),
        margin=dict(t=50, b=30, l=30, r=20),
        showlegend=False,
    )
    week_fig.update_xaxes(gridcolor=BORDER)
    week_fig.update_yaxes(gridcolor=BORDER, title="kWh")
    st.plotly_chart(week_fig, use_container_width=True)
    st.caption(f"{icon('bolt', size=12, color=ACCENT)} Weekday &nbsp;&nbsp; {icon('bolt', size=12, color='#58a6ff')} Weekend — a full simulated week, regenerated on demand.", unsafe_allow_html=True)

with wk_side_col:
    st.markdown(f"""
    <div class="side-metric">
        <div class="label">{icon('person', size=14)} Weekday Avg Occupancy</div>
        <div class="value">{weekday_avg['occupancy']:.0f}%</div>
    </div>
    <div class="side-metric">
        <div class="label">{icon('person', size=14)} Weekend Avg Occupancy</div>
        <div class="value">{weekend_avg['occupancy']:.0f}%</div>
    </div>
    <div class="side-metric">
        <div class="label">{icon('bolt', size=14, color=ACCENT)} Weekend Energy Shift</div>
        <div class="value" style="color:{'#f85149' if energy_delta_pct > 0 else ACCENT};">{energy_delta_pct:+.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="sidebar-heading" style="margin-top:0.4rem;">{icon("map", size=13)} 7-Day Weather Outlook</div>',
        unsafe_allow_html=True,
    )
    for f in forecast:
        mult = energy_multiplier(f["condition"], f["temp_c"])
        mult_color = "#f85149" if mult > 1.03 else (ACCENT if mult < 0.98 else TEXT_MUTED)
        st.markdown(
            f"<div style='display:flex; justify-content:space-between; align-items:center; "
            f"font-size:0.82rem; padding:0.25rem 0; border-bottom:1px solid {BORDER};'>"
            f"<span>{f['icon']} {f['day']}</span>"
            f"<span style='color:{TEXT_MUTED};'>{f['temp_c']}°C</span>"
            f"<span style='color:{mult_color}; font-weight:600;'>{mult:.2f}x</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    st.caption("Mock forecast — condition drives the energy-prediction multiplier below, standing in for a real weather-API feed.")

st.divider()

# ---------- occupancy vs energy correlation ----------
st.markdown(
    f'<div class="section-heading">{icon("trend", size=18)} Occupancy vs Energy Correlation</div>',
    unsafe_allow_html=True,
)

corr_val = week_df_all["occupancy"].corr(week_df_all["energy"])
loc_colors = {"Block A": "#58a6ff", "Block B": "#a371f7", "Library": ACCENT, "Canteen": "#eab308", "Hostel": "#f85149"}

corr_fig = go.Figure()
for loc in LOCATIONS:
    sub = week_df_all[week_df_all["location"] == loc]
    corr_fig.add_trace(go.Scatter(
        x=sub["occupancy"], y=sub["energy"], mode="markers", name=loc,
        marker=dict(color=loc_colors.get(loc, ACCENT), size=5, opacity=0.55),
    ))

# manual OLS trendline (no extra ML dependency) across all buildings/hours
slope, intercept = np.polyfit(week_df_all["occupancy"], week_df_all["energy"], 1)
x_line = np.array([week_df_all["occupancy"].min(), week_df_all["occupancy"].max()])
corr_fig.add_trace(go.Scatter(
    x=x_line, y=slope * x_line + intercept, mode="lines",
    name="Trend", line=dict(color="#e6edf3", width=2, dash="dash"),
))
corr_fig.update_layout(
    height=360,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e6edf3"),
    margin=dict(t=20, b=30, l=30, r=20),
    xaxis=dict(title="Occupancy (%)", gridcolor=BORDER),
    yaxis=dict(title="Energy (kWh)", gridcolor=BORDER),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)
st.plotly_chart(corr_fig, use_container_width=True)
st.caption(f"Across a simulated week of hourly readings for every building, occupancy and energy move together (correlation ≈ {corr_val:.2f}) — more people on-site tracks with more energy draw.")

st.divider()

# ---------- building detail (selected in sidebar) ----------
st.markdown(
    f'<div class="section-heading">{icon("building", size=18)} Building Detail — {selected}</div>',
    unsafe_allow_html=True,
)

d1, d2, d3, d4 = st.columns(4)
d1.metric("Occupancy", f"{sel_row['occupancy']}%")
d2.metric("Temperature", f"{sel_row['temperature']}°C")
d3.metric("Energy", f"{sel_row['energy']} kWh")
d4.metric("Water", f"{sel_row['water']} L")

chart_col, gauge_col = st.columns([2, 1])

with chart_col:
    # energy usage chart — themed to match dark background
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["location"], y=df["energy"], name="Energy (kWh)",
        marker_color=[ACCENT if loc == selected else "#3b4252" for loc in df["location"]],
    ))
    fig.update_layout(
        title="Energy Usage by Location",
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e6edf3"),
        margin=dict(t=50, b=30, l=30, r=20),
    )
    fig.update_xaxes(gridcolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER)
    st.plotly_chart(fig, use_container_width=True)

with gauge_col:
    from data import BASELINES
    occ_high = BASELINES[selected]["occupancy"][1]
    occ_over = sel_row["occupancy"] > occ_high
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sel_row["occupancy"],
        number={"suffix": "%", "font": {"color": "#e6edf3", "size": 26}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": TEXT_MUTED, "tickfont": {"color": TEXT_MUTED, "size": 9}},
            "bar": {"color": "#f85149" if occ_over else ACCENT},
            "bgcolor": CARD_BG,
            "borderwidth": 1,
            "bordercolor": BORDER,
            "steps": [
                {"range": [0, occ_high], "color": "rgba(34,197,94,0.15)"},
                {"range": [occ_high, 100], "color": "rgba(248,81,73,0.15)"},
            ],
        },
    ))
    gauge_fig.update_layout(
        height=320,
        title=dict(text="Occupancy Level", font=dict(color="#e6edf3", size=13)),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=10, l=25, r=25),
    )
    st.plotly_chart(gauge_fig, use_container_width=True, config={"displayModeBar": False})

st.divider()

# ---------- 24-hour historical trend (simulated) ----------
st.markdown(
    f'<div class="section-heading">{icon("history", size=18)} 24-Hour Historical Trend — {selected}</div>',
    unsafe_allow_html=True,
)
trend_vals = st.session_state.trend_24h[selected]
hours_ago = list(range(-len(trend_vals) + 1, 1))
trend_fig = go.Figure(go.Scatter(
    x=hours_ago, y=trend_vals, mode="lines",
    line=dict(color="#58a6ff", width=2.5),
    fill="tozeroy", fillcolor="rgba(88,166,255,0.12)",
))
trend_fig.update_layout(
    height=260,
    margin=dict(t=10, b=30, l=30, r=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e6edf3"),
    xaxis=dict(title="Hours ago", gridcolor=BORDER),
    yaxis=dict(title="Energy (kWh)", gridcolor=BORDER),
)
st.plotly_chart(trend_fig, use_container_width=True)
st.caption("Simulated 24-hour trend — regenerates each session, not tied to live readings above.")

st.divider()

# ---------- anomaly detection ----------
st.markdown(
    f'<div class="section-heading">{icon("alert", size=18)} Anomaly Detection</div>',
    unsafe_allow_html=True,
)
anomalies = detect_anomalies(df, st.session_state.tolerance)

if not anomalies:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:0.5rem;color:{ACCENT};font-weight:600;">'
        f'{icon("check", size=18, color=ACCENT)} Normal — no anomalies detected.</div>',
        unsafe_allow_html=True,
    )
else:
    for a in anomalies:
        st.error(
            f"{a['metric'].title()} anomaly detected in {a['location']} "
            f"— current: {a['value']}, expected: {a['expected_low']}–{a['expected_high']}",
            icon=":material/warning:",
        )

    st.markdown(
        f'<div class="section-heading">{icon("cpu", size=18)} AI Advisor</div>',
        unsafe_allow_html=True,
    )
    priority_state = {"High": "critical", "Medium": "warning", "Low": "normal"}
    for a in anomalies:
        with st.spinner(f"Analyzing {a['location']} {a['metric']}..."):
            advice = get_ai_recommendation(a)
        with st.container(border=True):
            dot = status_icon(priority_state.get(advice.get("priority", "Medium"), "warning"))
            st.markdown(
                f"**{a['location']} — {a['metric'].title()} anomaly** &nbsp;{dot} {advice.get('priority', 'Medium')}",
                unsafe_allow_html=True,
            )
            st.write(f"**What happened:** {advice['what_happened']}")
            st.write(f"**Possible cause:** {advice['possible_cause']}")
            st.write(f"**Predicted impact:** {advice['predicted_impact']}")
            st.write(f"**Recommendation:** {advice['recommendation']}")

            if a["metric"] == "energy" and a["value"] > a["expected_high"]:
                sav = anomaly_savings(
                    a["location"], a["value"],
                    st.session_state.rate_per_kwh, st.session_state.co2_per_kwh,
                )
                if sav["excess_kwh_per_hour"] > 0:
                    st.markdown(
                        f"<div style='margin-top:0.4rem; padding:0.6rem 0.8rem; border-radius:8px; "
                        f"background:{BG}; border:1px solid {BORDER};'>"
                        f"<div style='font-weight:700; font-size:0.85rem; margin-bottom:0.35rem; display:flex; align-items:center; gap:0.4rem;'>"
                        f"{icon('leaf', size=14, color=ACCENT)} Cost & Sustainability Impact</div>"
                        f"<div style='font-size:0.85rem; color:{TEXT_MUTED};'>"
                        f"Running {sav['excess_kwh_per_hour']} kWh above normal &nbsp;→&nbsp; "
                        f"<b style='color:#e6edf3;'>₹{sav['quick_fix_cost']:,.0f}</b> / "
                        f"<b style='color:#e6edf3;'>{sav['quick_fix_co2']:,.1f} kg CO₂</b> "
                        f"if fixed within {sav['hours_quick']:.0f} hr — but "
                        f"<b style='color:#f85149;'>₹{sav['delayed_cost']:,.0f}</b> / "
                        f"<b style='color:#f85149;'>{sav['delayed_co2']:,.1f} kg CO₂</b> "
                        f"if left unresolved for {sav['hours_delay']:.0f} hrs."
                        f"</div></div>",
                        unsafe_allow_html=True,
                    )

st.divider()

# ---------- simple prediction (Step 9) ----------
st.markdown(
    f'<div class="section-heading">{icon("trend", size=18)} Weather-Adjusted Energy Prediction (next 3 hours)</div>',
    unsafe_allow_html=True,
)

hist = st.session_state.history[selected]
hist.append(sel_row["energy"])
st.session_state.history[selected] = hist[-12:]  # keep last 12 points

X = np.arange(len(hist)).reshape(-1, 1)
y = np.array(hist)
model = LinearRegression().fit(X, y)
future_x = np.array([[len(hist) + 2]])  # ~3 steps ahead
raw_predicted = max(model.predict(future_x)[0], 0)
predicted = raw_predicted * today_multiplier

st.markdown(
    f"<div style='display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem; color:{TEXT_MUTED}; font-size:0.88rem;'>"
    f"<span>{today_weather['icon']} Today: {today_weather['condition']}, {today_weather['temp_c']}°C</span>"
    f"<span style='color:{'#f85149' if today_multiplier > 1 else ACCENT}; font-weight:700;'>"
    f"&nbsp;→&nbsp; energy demand x{today_multiplier:.2f}</span></div>",
    unsafe_allow_html=True,
)

p1, p2, p3 = st.columns(3)
p1.metric("Current Energy", f"{sel_row['energy']} kWh")
p2.metric("Predicted in 3 hrs", f"{predicted:.0f} kWh", help=f"Trend-only estimate: {raw_predicted:.0f} kWh, weather-adjusted x{today_multiplier:.2f}")
change_pct = ((predicted - sel_row["energy"]) / sel_row["energy"]) * 100 if sel_row["energy"] else 0
p3.metric("Expected Change", f"{change_pct:+.1f}%")

pred_fig = go.Figure()
pred_fig.add_trace(go.Scatter(
    y=hist, mode="lines+markers", name="History",
    line=dict(color="#58a6ff"),
))
pred_fig.add_trace(go.Scatter(
    x=[len(hist) - 1, len(hist) + 2],
    y=[hist[-1], raw_predicted],
    mode="lines+markers",
    name="Trend-only Prediction",
    line=dict(dash="dot", color=TEXT_MUTED),
))
pred_fig.add_trace(go.Scatter(
    x=[len(hist) - 1, len(hist) + 2],
    y=[hist[-1], predicted],
    mode="lines+markers",
    name="Weather-Adjusted Prediction",
    line=dict(dash="dash", color=ACCENT),
))
pred_fig.update_layout(
    height=300,
    title=f"{selected} Energy Trend",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e6edf3"),
    margin=dict(t=50, b=30, l=30, r=20),
)
pred_fig.update_xaxes(gridcolor=BORDER)
pred_fig.update_yaxes(gridcolor=BORDER)
st.plotly_chart(pred_fig, use_container_width=True)
