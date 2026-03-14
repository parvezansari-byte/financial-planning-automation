import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
from io import BytesIO

try:
    import pdfplumber
    PDF_OK = True
except Exception:
    PDF_OK = False

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Freedom V4 ULTRA - Roman Imperial",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# SESSION STATE
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page_name):
    st.session_state.page = page_name

def back_button():
    st.markdown("<div style='margin-top:4px; margin-bottom:8px;'></div>", unsafe_allow_html=True)
    st.button("⬅ Back to Roman Index", on_click=lambda: go("home"), use_container_width=True)

# =====================================================
# IMPERIAL ROMAN ULTRA THEME
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* =========================
   GLOBAL
========================= */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 85% 10%, rgba(212,175,55,0.18) 0%, rgba(212,175,55,0.02) 20%, transparent 42%),
        radial-gradient(circle at 10% 90%, rgba(122,31,31,0.12) 0%, rgba(122,31,31,0.02) 24%, transparent 46%),
        linear-gradient(135deg, #f8f2e8 0%, #f2e4cb 28%, #e5d1a8 60%, #d6b97d 100%);
    color: #2B1E12;
    background-attachment: fixed;
}

/* =========================
   MAIN CONTAINER
========================= */
.main .block-container {
    max-width: 94%;
    padding-top: 1.15rem;
    padding-bottom: 2.2rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
    background: rgba(255, 248, 237, 0.52);
    border: 1px solid rgba(107, 30, 30, 0.10);
    border-radius: 24px;
    backdrop-filter: blur(6px);
    box-shadow: 0 12px 35px rgba(92, 26, 26, 0.08);
}

/* =========================
   SIDEBAR
========================= */
section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #f4e8d0 0%, #ead8b3 45%, #ddc08a 100%);
    border-right: 2px solid #C58B39;
    box-shadow: inset -8px 0 22px rgba(107, 30, 30, 0.05);
}

section[data-testid="stSidebar"] * {
    color: #2B1E12 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: 'Cinzel', serif !important;
    color: #6B1E1E !important;
    font-weight: 800 !important;
}

/* =========================
   INPUTS
========================= */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background: linear-gradient(180deg, #fffdf8 0%, #f9f0dc 100%) !important;
    color: #2B1E12 !important;
    border: 1px solid #B8860B !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

button[kind="secondary"] {
    border-radius: 10px !important;
}

/* =========================
   TITLES
========================= */
.main-title {
    background:
        linear-gradient(90deg, #5C1212 0%, #7A1F1F 25%, #A52A2A 58%, #C58B39 100%);
    padding: 26px;
    border-radius: 20px;
    text-align: center;
    color: #FFF8ED;
    font-size: 54px;
    font-weight: 800;
    font-family: 'Cinzel', serif;
    border: 2px solid #D4AF37;
    box-shadow: 0 12px 30px rgba(92, 26, 26, 0.22);
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.sub-title {
    background:
        linear-gradient(90deg, #4A120F 0%, #6B1E1E 55%, #8B6B2E 100%);
    color: #FFF8ED;
    text-align: center;
    padding: 10px;
    font-size: 19px;
    font-weight: 700;
    border-radius: 12px;
    border: 1px solid rgba(212,175,55,0.65);
    margin-bottom: 14px;
    box-shadow: 0 4px 14px rgba(92, 26, 26, 0.10);
}

.hero-banner {
    background:
        linear-gradient(135deg, rgba(255,248,237,0.82), rgba(247,231,201,0.76));
    border: 1px solid rgba(184,134,11,0.22);
    border-radius: 20px;
    padding: 16px 18px;
    margin-bottom: 14px;
    box-shadow: 0 8px 22px rgba(92, 26, 26, 0.06);
}

.summary-strip {
    background: linear-gradient(90deg, #5C1212 0%, #7A1F1F 35%, #A52A2A 68%, #C58B39 100%);
    color: #FFF8ED !important;
    border: 1px solid rgba(212,175,55,0.55);
    border-radius: 18px;
    padding: 14px 18px;
    margin-bottom: 14px;
    box-shadow: 0 10px 24px rgba(92, 26, 26, 0.14);
    font-weight: 700;
}

.tile-card {
    background: linear-gradient(180deg, rgba(255,248,237,0.96) 0%, rgba(249,238,214,0.96) 100%);
    border: 1px solid rgba(107, 30, 30, 0.14);
    border-top: 4px solid #B8860B;
    border-radius: 18px;
    padding: 16px;
    min-height: 170px;
    box-shadow: 0 8px 20px rgba(92, 26, 26, 0.08);
    margin-bottom: 12px;
}

.tile-title {
    font-family: 'Cinzel', serif;
    color: #6B1E1E !important;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 8px;
}

.tile-text {
    color: #3A2918 !important;
    font-size: 14px;
    line-height: 1.55;
}

.export-panel {
    background: linear-gradient(135deg, rgba(242,217,155,0.45), rgba(255,248,237,0.88));
    border: 1px solid rgba(184,134,11,0.25);
    border-left: 6px solid #7A1F1F;
    border-radius: 18px;
    padding: 16px;
    margin-top: 8px;
    margin-bottom: 12px;
    box-shadow: 0 8px 18px rgba(92, 26, 26, 0.06);
}

.report-panel {
    background: linear-gradient(180deg, rgba(255,248,237,0.98) 0%, rgba(248,236,208,0.97) 100%);
    border: 1px solid rgba(107, 30, 30, 0.14);
    border-left: 6px solid #B8860B;
    border-radius: 18px;
    padding: 18px;
    margin-top: 8px;
    margin-bottom: 12px;
    box-shadow: 0 8px 18px rgba(92, 26, 26, 0.06);
}

.report-title {
    font-family: 'Cinzel', serif;
    color: #6B1E1E !important;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 8px;
}

.report-text {
    color: #3A2918 !important;
    font-size: 14px;
    line-height: 1.65;
}

.signature-banner {
    background: linear-gradient(90deg, #4A120F 0%, #6B1E1E 25%, #8E2B2B 55%, #C58B39 100%);
    color: #FFF8ED !important;
    border: 1px solid rgba(212,175,55,0.55);
    border-radius: 22px;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: 0 12px 28px rgba(92, 26, 26, 0.18);
}

.boardroom-banner {
    background: linear-gradient(90deg, #3E0F0F 0%, #5C1212 22%, #7A1F1F 48%, #A52A2A 72%, #D4AF37 100%);
    color: #FFF8ED !important;
    border: 1px solid rgba(212,175,55,0.65);
    border-radius: 24px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 14px 32px rgba(92, 26, 26, 0.20);
}

.boardroom-panel {
    background: linear-gradient(180deg, rgba(255,248,237,0.98) 0%, rgba(248,236,208,0.97) 100%);
    border: 1px solid rgba(107, 30, 30, 0.14);
    border-top: 5px solid #B8860B;
    border-radius: 20px;
    padding: 18px;
    min-height: 210px;
    box-shadow: 0 10px 24px rgba(92, 26, 26, 0.08);
    margin-bottom: 12px;
}

.signature-card {
    background: linear-gradient(180deg, rgba(255,248,237,0.97) 0%, rgba(248,236,208,0.96) 100%);
    border: 1px solid rgba(107, 30, 30, 0.14);
    border-left: 6px solid #B8860B;
    border-radius: 18px;
    padding: 18px;
    min-height: 190px;
    box-shadow: 0 8px 20px rgba(92, 26, 26, 0.08);
    margin-bottom: 12px;
}

.signature-title {
    font-family: 'Cinzel', serif;
    color: #6B1E1E !important;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 8px;
}

.signature-text {
    color: #3A2918 !important;
    font-size: 14px;
    line-height: 1.6;
}

.score-strip {
    background: linear-gradient(90deg, rgba(255,248,237,0.95) 0%, rgba(249,238,214,0.96) 100%);
    border: 1px solid rgba(184,134,11,0.22);
    border-radius: 18px;
    padding: 14px 16px;
    margin-bottom: 14px;
    box-shadow: 0 8px 18px rgba(92, 26, 26, 0.06);
}

/* =========================
   SECTION BOXES
========================= */
.imperial-box {
    border: 1px solid rgba(107, 30, 30, 0.14);
    background: linear-gradient(180deg, rgba(255,248,237,0.92) 0%, rgba(250,240,220,0.92) 100%);
    margin-bottom: 14px;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 8px 22px rgba(92, 26, 26, 0.08);
}

.imperial-header {
    background: linear-gradient(90deg, #7A1F1F 0%, #A52A2A 58%, #C58B39 100%);
    color: #FFF8ED;
    text-align: center;
    font-weight: 800;
    font-size: 24px;
    font-family: 'Cinzel', serif;
    padding: 12px;
    border-bottom: 1px solid rgba(255,248,237,0.35);
}

.imperial-subheader {
    background: linear-gradient(90deg, #F2D99B 0%, #D4A15A 100%);
    color: #2B1E12;
    text-align: center;
    font-weight: 800;
    padding: 8px;
    font-family: 'Cinzel', serif;
    border-bottom: 1px solid rgba(107, 30, 30, 0.10);
}

/* =========================
   KPI / CARDS
========================= */
.kpi-card {
    background: linear-gradient(180deg, #FFF8ED 0%, #F8EBD2 100%);
    border: 1px solid rgba(107, 30, 30, 0.14);
    border-left: 6px solid #B8860B;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 6px 18px rgba(92, 26, 26, 0.07);
    margin-bottom: 10px;
    text-align: center;
}

.kpi-title {
    font-family: 'Cinzel', serif;
    color: #5C1A1A;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 6px;
}

.kpi-value {
    font-family: 'Cinzel', serif;
    color: #7A1F1F;
    font-size: 28px;
    font-weight: 800;
}

/* =========================
   NAV BUTTONS
========================= */
.stButton > button {
    width: 100%;
    min-height: 58px;
    border-radius: 14px;
    border: 1px solid #C58B39;
    background: linear-gradient(145deg, #FFF8ED 0%, #F8E7C5 55%, #E8C989 100%);
    color: #5C1A1A !important;
    font-weight: 800;
    font-family: 'Cinzel', serif;
    box-shadow: 0 6px 18px rgba(92, 26, 26, 0.10);
    transition: all 0.25s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    background: linear-gradient(145deg, #FFFDF8 0%, #F6E6C0 45%, #DDB56A 100%);
    color: #4A120F !important;
    border: 1px solid #D4AF37;
    box-shadow: 0 10px 24px rgba(92, 26, 26, 0.16);
}

.stDownloadButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 12px;
    border: 1px solid #8B6B2E;
    background: linear-gradient(145deg, #E5C47A 0%, #C58B39 100%);
    color: #2B1E12 !important;
    font-weight: 800;
    box-shadow: 0 4px 12px rgba(92, 26, 26, 0.10);
}

/* =========================
   METRICS / ALERTS
========================= */
[data-testid="metric-container"] {
    background: linear-gradient(180deg, #FFF8ED 0%, #F7E9D0 100%);
    border: 1px solid rgba(107, 30, 30, 0.14);
    border-left: 6px solid #B8860B;
    border-radius: 16px;
    padding: 12px;
    box-shadow: 0 6px 16px rgba(92, 26, 26, 0.07);
}

[data-testid="stAlert"] {
    border-radius: 14px !important;
    border: 1px solid rgba(184,134,11,0.30) !important;
    background: linear-gradient(180deg, #FFF8ED 0%, #F7E9D0 100%) !important;
}

/* =========================
   TABS
========================= */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: #F8EFD9;
    border-radius: 10px 10px 0 0;
    border: 1px solid #D4A15A;
    color: #5C1A1A;
    font-weight: 700;
    font-family: 'Cinzel', serif;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #7A1F1F 0%, #C58B39 100%) !important;
    color: #FFF8ED !important;
}

/* =========================
   TABLES
========================= */
thead tr th {
    background: linear-gradient(90deg, #7A1F1F 0%, #A52A2A 60%, #C58B39 100%) !important;
    color: #FFF8ED !important;
    border: 1px solid #6B1E1E !important;
    font-weight: 800 !important;
}

tbody tr td {
    color: #2B1E12 !important;
    border: 1px solid #E6D0A8 !important;
    background: #FFF8ED !important;
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(107, 30, 30, 0.10);
    box-shadow: 0 6px 18px rgba(92, 26, 26, 0.05);
}

/* =========================
   TEXT
========================= */
label, .stMarkdown, .stText, .stCaption, p, div {
    color: #2B1E12 !important;
}

hr {
    border: none;
    border-top: 2px solid rgba(197, 139, 57, 0.35);
}

header[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HELPERS
# =====================================================
def fmt(x):
    try:
        return f"₹ {x:,.0f}"
    except Exception:
        return "₹ 0"

def future_value(pv, rate, years):
    return pv * ((1 + rate) ** max(years, 0))

def future_value_sip(monthly_investment, annual_return, years):
    months = int(max(years, 0) * 12)
    if months <= 0:
        return 0
    r = annual_return / 12
    if r <= 0:
        return monthly_investment * months
    return monthly_investment * (((1 + r) ** months - 1) / r) * (1 + r)

def lumpsum_required(target, annual_return, years):
    if years <= 0:
        return target
    return target / ((1 + annual_return) ** years)

def monthly_sip_required(target, annual_rate, years):
    months = int(max(years, 0) * 12)
    if months <= 0:
        return 0
    r = annual_rate / 12
    if r <= 0:
        return target / months
    factor = (((1 + r) ** months - 1) / r) * (1 + r)
    return target / factor if factor > 0 else 0

def monthly_sip_required_stepup(target, annual_return, years, step_up):
    months = int(max(years, 0) * 12)
    if months <= 0:
        return 0
    r = annual_return / 12
    low, high = 0, max(target, 1)
    for _ in range(80):
        mid = (low + high) / 2
        corpus = 0
        sip = mid
        for m in range(1, months + 1):
            corpus = corpus * (1 + r) + sip
            if m % 12 == 0:
                sip *= (1 + step_up)
        if corpus >= target:
            high = mid
        else:
            low = mid
    return high

def swp_corpus_required(monthly_withdrawal, annual_return, years):
    r = annual_return / 12
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return monthly_withdrawal * n
    return monthly_withdrawal * ((1 - (1 + r) ** (-n)) / r)

def emi_calculator(principal, annual_rate, years):
    r = annual_rate / 12
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return principal / n
    return principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)

def xnpv(rate, cashflows):
    if len(cashflows) < 1:
        return 0
    t0 = cashflows[0][0]
    return sum(cf / ((1 + rate) ** ((dt - t0).days / 365.0)) for dt, cf in cashflows)

def xirr(cashflows):
    if len(cashflows) < 2:
        return None
    low, high = -0.9999, 10.0
    for _ in range(200):
        mid = (low + high) / 2
        val = xnpv(mid, cashflows)
        if abs(val) < 1e-6:
            return mid
        if val > 0:
            low = mid
        else:
            high = mid
    return mid

def clean_amount(x):
    x = str(x).replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "").strip()
    x = re.sub(r"[^0-9.\-]", "", x)
    try:
        return float(x)
    except Exception:
        return np.nan

def normalize_txn_type(x):
    x = str(x).lower().strip()
    buy = ["purchase", "sip", "systematic investment", "switch in", "stp in", "allotment", "buy", "investment", "additional purchase"]
    sell = ["redemption", "switch out", "sell", "withdrawal", "swp", "stp out", "redeem"]
    current = ["current value", "market value", "current market value", "valuation"]
    for k in buy:
        if k in x:
            return "Purchase"
    for k in sell:
        if k in x:
            return "Redemption"
    for k in current:
        if k in x:
            return "Current Value"
    return "Unknown"

def advisor_note(title, lines):
    st.markdown('<div class="imperial-box">', unsafe_allow_html=True)
    st.markdown('<div class="imperial-subheader">Private Banker Advisory Notes</div>', unsafe_allow_html=True)
    st.markdown(f"**{title}**")
    for line in lines:
        st.write(f"• {line}")
    st.markdown('</div>', unsafe_allow_html=True)

def kpi_row(items):
    cols = st.columns(len(items))
    for i, (label, value) in enumerate(items):
        with cols[i]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown('<div class="main-title">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Roman Imperial Private Banker Edition | Investment & Insurance Planner</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-banner">
    <b>Prepared for:</b> {st.session_state.get('client_name', 'Client')} &nbsp;&nbsp; | &nbsp;&nbsp;
    <b>Advisor:</b> {st.session_state.get('advisor_name', 'Advisor')} &nbsp;&nbsp; | &nbsp;&nbsp;
    <b>Theme:</b> Roman Imperial Wealth Interface
</div>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.markdown("## Client Profile")
client_name = st.sidebar.text_input("Client Name", "Aditya")
advisor_name = st.sidebar.text_input("Advisor Name", "Saurabh")
current_age = st.sidebar.number_input("Current Age", 18, 80, 30)
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 20.0, 6.0) / 100
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 25.0, 12.0) / 100

st.session_state.client_name = client_name
st.session_state.advisor_name = advisor_name

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Navigation")
st.sidebar.caption("Production Ready Navigation Panel")
if st.sidebar.button("🏛️ Home Dashboard", use_container_width=True):
    go("home")
if st.sidebar.button("📈 SIP & Lumpsum", use_container_width=True):
    go("sip")
if st.sidebar.button("💸 SWP Planner", use_container_width=True):
    go("swp")
if st.sidebar.button("👨‍👩‍👧 Children Planning", use_container_width=True):
    go("children")
if st.sidebar.button("🛡️ Retirement Planner", use_container_width=True):
    go("retirement")
if st.sidebar.button("📊 Net Worth", use_container_width=True):
    go("networth")
if st.sidebar.button("🏦 Fund Suggestion & Performance", use_container_width=True):
    go("fund_suggestion")

# =====================================================
# HOME PAGE
# =====================================================
if st.session_state.page == "home":
    st.markdown('<div class="imperial-box"><div class="imperial-header">Freedom Planner Index</div></div>', unsafe_allow_html=True)

    total_modules = 15
    base_score = min(100, max(45, round((expected_return * 100) * 5 + (12 - inflation * 100) * 3)))
    wealth_mode = "Imperial Growth" if expected_return >= 0.12 else "Capital Shield"
    suggested_eq = 75 if current_age <= 35 else (60 if current_age <= 50 else 40)
    suggested_debt = 20 if current_age <= 35 else (30 if current_age <= 50 else 45)
    suggested_gold = 5 if current_age <= 35 else (10 if current_age <= 50 else 15)
    retirement_priority = "High" if current_age >= 40 else "Moderate"
    protection_score = min(100, max(55, 100 - current_age))
    discipline_score = min(100, max(50, round((expected_return * 100) * 6)))
    boardroom_score = min(100, max(60, round((base_score + protection_score + discipline_score) / 3)))

    kpi_row([
        ("Client", client_name),
        ("Advisor", advisor_name),
        ("Inflation", f"{inflation*100:.1f}%"),
        ("Expected Return", f"{expected_return*100:.1f}%")
    ])

    st.markdown(f"""
    <div class="boardroom-banner">
        <div style="font-family:'Cinzel', serif; font-size:28px; font-weight:800; margin-bottom:6px;">FINAL V6 BOARDROOM ELITE EDITION</div>
        <div style="font-size:14px; line-height:1.65;">
            Executive-grade HNI financial planning interface built for boardroom-style client meetings. Use this elite dashboard to present
            net worth, cashflow, goals, retirement, insurance, allocation, and rebalancing in a premium structured advisory flow.
        </div>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""
        <div class="kpi-card"><div class="kpi-title">Modules</div><div class="kpi-value">{total_modules}</div></div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card"><div class="kpi-title">Readiness</div><div class="kpi-value">{base_score}%</div></div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card"><div class="kpi-title">Protection</div><div class="kpi-value">{protection_score}%</div></div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card"><div class="kpi-title">Discipline</div><div class="kpi-value">{discipline_score}%</div></div>
        """, unsafe_allow_html=True)
    with k5:
        st.markdown(f"""
        <div class="kpi-card"><div class="kpi-title">Boardroom Score</div><div class="kpi-value">{boardroom_score}%</div></div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-strip">
        Boardroom Allocation Lens &nbsp;&nbsp; | &nbsp;&nbsp;
        <b>{suggested_eq}% Equity</b> · <b>{suggested_debt}% Debt</b> · <b>{suggested_gold}% Gold</b>
        &nbsp;&nbsp; | &nbsp;&nbsp; Mode: <b>{wealth_mode}</b>
        &nbsp;&nbsp; | &nbsp;&nbsp; Retirement Priority: <b>{retirement_priority}</b>
    </div>
    """, unsafe_allow_html=True)

    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(f"""
        <div class="boardroom-panel">
            <div class="signature-title">👤 HNI Client Profile Panel</div>
            <div class="signature-text">
                <b>Client:</b> {client_name}<br>
                <b>Advisor:</b> {advisor_name}<br>
                <b>Age:</b> {current_age}<br>
                <b>Inflation Assumption:</b> {inflation*100:.1f}%<br>
                <b>Expected Return:</b> {expected_return*100:.1f}%<br><br>
                Use as opening boardroom profile before moving into wealth, protection, and lifestyle planning.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with b2:
        st.markdown(f"""
        <div class="boardroom-panel">
            <div class="signature-title">🎯 Executive Goal Scorecards</div>
            <div class="signature-text">
                <b>Advisory Readiness:</b> {base_score}%<br>
                <b>Protection Score:</b> {protection_score}%<br>
                <b>Discipline Score:</b> {discipline_score}%<br>
                <b>Boardroom Score:</b> {boardroom_score}%<br><br>
                Ideal for premium discussion framing before detailed module walkthrough.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with b3:
        st.markdown(f"""
        <div class="boardroom-panel">
            <div class="signature-title">📊 Advisor Recommendation Engine</div>
            <div class="signature-text">
                <b>Suggested Allocation:</b><br>
                Equity {suggested_eq}% | Debt {suggested_debt}% | Gold {suggested_gold}%<br>
                <b>Portfolio Mode:</b> {wealth_mode}<br>
                <b>Priority:</b> {retirement_priority}<br><br>
                Pair this with Portfolio Allocation + Rebalancing for a final premium recommendation close.
            </div>
        </div>
        """, unsafe_allow_html=True)

    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown(f"""
        <div class="tile-card">
            <div class="tile-title">🏛️ Core Wealth Planning</div>
            <div class="tile-text">SIP, SWP, goal feasibility, and allocation modules to build the long-term compounding blueprint.</div>
        </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown(f"""
        <div class="tile-card">
            <div class="tile-title">🛡️ Protection & Retirement</div>
            <div class="tile-text">Retirement, term cover, and Monte Carlo modules to stress-test sustainability and family protection.</div>
        </div>
        """, unsafe_allow_html=True)
    with t3:
        st.markdown(f"""
        <div class="tile-card">
            <div class="tile-title">💼 Lifestyle & Balance Sheet</div>
            <div class="tile-text">Cashflow, net worth, and lifestyle purchase planners to preserve financial discipline without harming goals.</div>
        </div>
        """, unsafe_allow_html=True)

    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown("### 🏛️ Core Wealth Planning")
        st.button("SIP & Lumpsum Calculator", on_click=lambda: go("sip"), use_container_width=True)
        st.button("SIP + SWP Planner", on_click=lambda: go("sip_swp"), use_container_width=True)
        st.button("SWP Calculator", on_click=lambda: go("swp"), use_container_width=True)
        st.button("Goal Feasibility", on_click=lambda: go("goal"), use_container_width=True)
        st.button("Portfolio Allocation", on_click=lambda: go("portfolio"), use_container_width=True)
        st.button("Fund Suggestion & Performance", on_click=lambda: go("fund_suggestion"), use_container_width=True)
    with a2:
        st.markdown("### 👨‍👩‍👧 Life Goal & Protection")
        st.button("Future Planning for Children", on_click=lambda: go("children"), use_container_width=True)
        st.button("Retirement Planner", on_click=lambda: go("retirement"), use_container_width=True)
        st.button("Term Insurance Calculator", on_click=lambda: go("term"), use_container_width=True)
        st.button("Retirement Monte Carlo", on_click=lambda: go("mc_retirement"), use_container_width=True)
        st.button("Portfolio Rebalancing", on_click=lambda: go("rebalance"), use_container_width=True)
    with a3:
        st.markdown("### 💼 Lifestyle & Balance Sheet")
        st.button("Cashflow Planner", on_click=lambda: go("cashflow"), use_container_width=True)
        st.button("Net Worth Dashboard", on_click=lambda: go("networth"), use_container_width=True)
        st.button("House Planning", on_click=lambda: go("house"), use_container_width=True)
        st.button("Car Purchase Planner", on_click=lambda: go("car"), use_container_width=True)
        st.button("EMI vs SIP Calculator", on_click=lambda: go("emi_vs_sip"), use_container_width=True)
        st.button("iPhone Purchase Planner", on_click=lambda: go("iphone"), use_container_width=True)

    st.markdown("---")
    st.markdown("### 🏛️ Boardroom Elite Master Summary")
    s1, s2, s3 = st.columns(3)
    with s1:
        alloc_df = pd.DataFrame({"Asset Class": ["Equity", "Debt", "Gold"], "Suggested %": [suggested_eq, suggested_debt, suggested_gold]})
        st.dataframe(alloc_df, use_container_width=True, hide_index=True)
    with s2:
        fund_df = pd.DataFrame({
            "Model Bucket": ["Large Cap / Flexi Cap", "Hybrid / Debt", "Gold / SGB"],
            "Boardroom Role": ["Growth Engine", "Capital Stability", "Strategic Hedge"]
        })
        st.dataframe(fund_df, use_container_width=True, hide_index=True)
    with s3:
        st.markdown(f"""
        <div class="export-panel">
            <b>HNI Client Presentation Flow</b><br><br>
            • Open with Client Profile & Net Worth<br>
            • Move to Cashflow & Goal Feasibility<br>
            • Present Children + Retirement Planning<br>
            • Close with Insurance + Allocation + Rebalancing<br><br>
            <b>Meeting Tone:</b> Boardroom | Elite | Private Banker
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🧾 V6.2 EXPORT + PDF READY | Advisor Summary")
    r1, r2 = st.columns([1.4, 1])
    with r1:
        st.markdown(f"""
        <div class="report-panel">
            <div class="report-title">Executive Meeting Summary</div>
            <div class="report-text">
                <b>Client:</b> {client_name}<br>
                <b>Advisor:</b> {advisor_name}<br>
                <b>Boardroom Score:</b> {boardroom_score}%<br>
                <b>Suggested Allocation:</b> {suggested_eq}% Equity | {suggested_debt}% Debt | {suggested_gold}% Gold<br>
                <b>Portfolio Mode:</b> {wealth_mode}<br>
                <b>Retirement Priority:</b> {retirement_priority}<br><br>
                <b>Recommended Meeting Flow:</b><br>
                1. Net Worth + Cashflow Review<br>
                2. Goal Feasibility + Children Planning<br>
                3. Retirement Sustainability + SWP Logic<br>
                4. Insurance Adequacy + Allocation + Rebalancing<br><br>
                <b>Advisor Closing Note:</b> Focus first on retirement security, then goal-based investing, and finally lifestyle aspirations without disturbing core wealth compounding.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with r2:
        summary_df = pd.DataFrame({
            "Metric": ["Readiness", "Protection", "Discipline", "Boardroom"],
            "Score": [f"{base_score}%", f"{protection_score}%", f"{discipline_score}%", f"{boardroom_score}%"]
        })
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.markdown(f"""
        <div class="export-panel">
            <b>PDF / Print Ready Guidance</b><br><br>
            • Use this home dashboard as cover page<br>
            • Export screenshots module-wise for client deck<br>
            • Present summary first, then calculators<br>
            • Use Boardroom Master Summary as closing page<br><br>
            <b>Format:</b> HNI | Boardroom | Presentation Ready
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📜 Executive Private Banker Notes")
    note1, note2, note3 = st.columns(3)
    with note1:
        st.info("Prioritize retirement first, then child goals, then lifestyle purchases.")
    with note2:
        st.info("Use SWP only after a sustainable corpus is validated through retirement modules.")
    with note3:
        st.info("Close every meeting with allocation + rebalancing for a professional advisory finish.")

    st.caption("Disclaimer: Output of these calculators is for illustration / advisory discussion purpose only. Please validate before execution.")

# =====================================================
# SIP & LUMPSUM CALCULATOR
# =====================================================
if st.session_state.page == "sip":
    back_button()
    st.markdown(f'<div class="imperial-box"><div class="imperial-header">SIP & Lumpsum Calculator</div></div>', unsafe_allow_html=True)

    t1, t2 = st.tabs(["SIP Planner", "Lumpsum Planner"])

    with t1:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            monthly_sip = st.number_input("Monthly SIP (₹)", 0, 100000000, 5000)
        with c2:
            years = st.number_input("Investment Period (Years)", 1, 60, 20)
        with c3:
            sip_return = st.number_input("Expected Return (%)", 0.0, 30.0, float(expected_return * 100)) / 100
        with c4:
            step_up = st.number_input("Annual Step-up (%)", 0.0, 50.0, 10.0) / 100

        corpus = 0
        total_invested = 0
        current_sip = monthly_sip
        rows = []

        for y in range(1, years + 1):
            yearly_invested = 0
            for _ in range(12):
                corpus = corpus * (1 + sip_return / 12) + current_sip
                total_invested += current_sip
                yearly_invested += current_sip
            gain = corpus - total_invested
            rows.append([y, round(current_sip, 0), round(yearly_invested, 0), round(total_invested, 0), round(gain, 0), round(corpus, 0)])
            current_sip *= (1 + step_up)

        sip_df = pd.DataFrame(rows, columns=["Year", "Monthly SIP (₹)", "Yearly Invested (₹)", "Total Invested (₹)", "Total Gain (₹)", "Year End Corpus (₹)"])

        kpi_row([
            ("Invested", fmt(total_invested)),
            ("Final Value", fmt(corpus)),
            ("Absolute Gain", f"{((corpus-total_invested)/total_invested*100 if total_invested>0 else 0):.2f}%")
        ])

        st.dataframe(sip_df, use_container_width=True)

    with t2:
        c1, c2, c3 = st.columns(3)
        with c1:
            lumpsum_amt = st.number_input("Investment Amount (₹)", 0, 1000000000, 1000000)
        with c2:
            lumpsum_return = st.number_input("Expected Return for Lumpsum (%)", 0.0, 30.0, 12.0) / 100
        with c3:
            lumpsum_years = st.number_input("Investment Period in Years", 1, 60, 7)

        final_lumpsum = future_value(lumpsum_amt, lumpsum_return, lumpsum_years)

        kpi_row([
            ("Invested", fmt(lumpsum_amt)),
            ("Final Value", fmt(final_lumpsum)),
            ("Absolute Gain", f"{((final_lumpsum-lumpsum_amt)/lumpsum_amt*100 if lumpsum_amt>0 else 0):.2f}%")
        ])

    advisor_note("SIP Recommendation", [
        "Step-up SIP materially improves long-term corpus.",
        "If cashflow allows, increasing SIP by 10% yearly is ideal.",
        "Use this module for disciplined long-term goal building."
    ])

# =====================================================
# SWP CALCULATOR PRO
# =====================================================
if st.session_state.page == "swp":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">SWP Calculator</div></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        initial_corpus = st.number_input("Current Corpus (₹)", 0, 1000000000, 10000000)
        entry_age = st.number_input("Current Age", 18, 100, current_age)
        pre_return = st.number_input("Expected Return before Withdrawal (%)", 0.0, 25.0, 12.0) / 100
    with c2:
        withdrawal_start_age = st.number_input("Withdrawal Starts at Age", entry_age, 110, 60)
        withdrawal_end_age = st.number_input("Withdrawal Ends at Age", withdrawal_start_age, 110, 80)
        yearly_withdrawal = st.number_input("Withdrawal Per Year (₹)", 0, 100000000, 1200000)
    with c3:
        yearly_increase = st.number_input("Yearly Increase in Withdrawal (%)", 0.0, 25.0, 5.0) / 100
        withdrawal_return = st.number_input("Expected Return in Withdrawal Phase (%)", 0.0, 25.0, 10.0) / 100
        inflation_adjusted = st.selectbox("Inflation Adjusted Withdrawal?", ["No", "Yes"])

    balance = initial_corpus
    rows = []

    for age in range(entry_age, withdrawal_start_age):
        opening = balance
        balance = balance * (1 + pre_return)
        rows.append([age, round(opening, 0), 0, round(balance, 0)])

    curr_wd = yearly_withdrawal
    for age in range(withdrawal_start_age, withdrawal_end_age + 1):
        opening = balance
        if inflation_adjusted == "Yes":
            eff_wd = curr_wd * ((1 + inflation) ** (age - withdrawal_start_age))
        else:
            eff_wd = curr_wd
        balance = balance * (1 + withdrawal_return) - eff_wd
        rows.append([age, round(opening, 0), round(eff_wd, 0), round(balance, 0)])
        curr_wd *= (1 + yearly_increase)
        if balance <= 0:
            break

    swp_df = pd.DataFrame(rows, columns=["Age", "Opening Corpus (₹)", "Withdrawal Per Year (₹)", "Year End Corpus (₹)"])
    swr = (yearly_withdrawal / initial_corpus * 100) if initial_corpus > 0 else 0

    kpi_row([
        ("Final Corpus", fmt(max(balance, 0))),
        ("Safe Withdrawal Rate", f"{swr:.2f}%"),
        ("Withdrawal Till Age", str(swp_df['Age'].iloc[-1] if len(swp_df) else entry_age))
    ])

    st.dataframe(swp_df, use_container_width=True)

    advisor_note("SWP Recommendation", [
        "If corpus depletes too early, reduce withdrawal or delay start age.",
        "Inflation-adjusted withdrawal gives a more realistic retirement view.",
        "Keep SWR near 3.5%–5.0% for stability depending on asset mix."
    ])

# =====================================================
# SIP + SWP PLANNER
# =====================================================
if st.session_state.page == "sip_swp":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">SIP + SWP Planner</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        sip_age = st.number_input("Current Age", 18, 100, 30)
        sip_till_age = st.number_input("SIP to Continue Till Age", sip_age + 1, 100, 40)
        sip_amt = st.number_input("Monthly SIP Amount (₹)", 0, 100000000, 50000)
        sip_ret = st.number_input("Expected Return During SIP (%)", 0.0, 25.0, 13.0) / 100
        sip_step = st.number_input("Annual Step-up (%)", 0.0, 50.0, 10.0) / 100
    with c2:
        swp_start_age = st.number_input("SWP Start Age", sip_till_age, 110, 40)
        swp_amt = st.number_input("Monthly Withdrawal Amount (₹)", 0, 100000000, 150000)
        swp_step = st.number_input("Yearly Increase in Withdrawal (%)", 0.0, 25.0, 8.0) / 100
        swp_ret = st.number_input("Expected Return in Withdrawal Phase (%)", 0.0, 25.0, 9.0) / 100

    corpus = 0
    monthly = sip_amt
    rows = []

    for age in range(sip_age, sip_till_age):
        opening = corpus
        yearly_invested = 0
        for _ in range(12):
            corpus = corpus * (1 + sip_ret / 12) + monthly
            yearly_invested += monthly
        rows.append([age, round(opening,0), round(monthly,0), round(yearly_invested,0), 0, 0, round(corpus,0)])
        monthly *= (1 + sip_step)

    swp_monthly = swp_amt
    for age in range(swp_start_age, 111):
        opening = corpus
        yearly_wd = swp_monthly * 12
        for _ in range(12):
            corpus = corpus * (1 + swp_ret / 12) - swp_monthly
        rows.append([age, round(opening,0), 0, 0, round(swp_monthly,0), round(yearly_wd,0), round(corpus,0)])
        swp_monthly *= (1 + swp_step)
        if corpus <= 0:
            break

    df = pd.DataFrame(rows, columns=["Age", "Year Beginning Corpus (₹)", "SIP Monthly (₹)", "SIP Yearly (₹)", "SWP Monthly (₹)", "SWP Yearly (₹)", "Year End Corpus (₹)"])

    kpi_row([
        ("Withdraw Till Age", str(df['Age'].iloc[-1] if len(df) else swp_start_age)),
        ("Final Corpus", fmt(max(corpus,0)))
    ])

    st.dataframe(df, use_container_width=True)

# =====================================================
# CHILDREN PLANNER PRO
# =====================================================
if st.session_state.page == "children":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Future Planning for Children</div></div>', unsafe_allow_html=True)

    num_children = st.number_input("How many children you have", 1, 4, 1)
    all_rows = []
    total_sip = 0
    total_lump = 0

    goal_defaults = [
        ("10th Board", 15, 300000),
        ("12th Board", 17, 500000),
        ("Graduation", 21, 2000000),
        ("Masters", 24, 2500000),
        ("Marriage", 28, 3000000),
    ]

    for i in range(1, num_children + 1):
        st.markdown(f"### Child {i}")
        child_name = st.text_input(f"Child {i} Name", f"Child {i}", key=f"child_name_{i}")
        child_age = st.number_input(f"Child {i} Age", 0, 25, 2, key=f"child_age_{i}")

        for goal_name, default_age, default_cost in goal_defaults:
            c1, c2 = st.columns(2)
            with c1:
                goal_age = st.number_input(f"{goal_name} Age - {child_name}", child_age, 40, default_age, key=f"{goal_name}_age_{i}")
            with c2:
                goal_cost = st.number_input(f"{goal_name} Cost Today (₹) - {child_name}", 0, 100000000, default_cost, key=f"{goal_name}_cost_{i}")

            years_left = max(goal_age - child_age, 0)
            future_cost = future_value(goal_cost, inflation, years_left)
            sip_req = monthly_sip_required(future_cost, expected_return, years_left)
            lump_req = lumpsum_required(future_cost, expected_return, years_left)
            prob = 97 if years_left >= 10 else (90 if years_left >= 5 else 75)

            all_rows.append([child_name, goal_name, goal_age, round(future_cost,0), round(sip_req,0), round(lump_req,0), prob])
            total_sip += sip_req
            total_lump += lump_req

    child_df = pd.DataFrame(all_rows, columns=["Child", "Goal", "Goal Age", "Future Cost (₹)", "Monthly SIP Required (₹)", "Lumpsum Required Today (₹)", "Success Probability %"])

    kpi_row([
        ("Total SIP Required", fmt(total_sip)),
        ("Total Lumpsum Today", fmt(total_lump))
    ])

    st.dataframe(child_df, use_container_width=True)

    advisor_note("Children Planning Recommendation", [
        "Create separate folios or buckets for each child goal.",
        "Education and marriage goals should not be mixed with retirement assets.",
        "Review this plan every 12 months and increase SIP as income rises."
    ])

# =====================================================
# RETIREMENT PLANNER
# =====================================================
if st.session_state.page == "retirement":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Retirement Planner</div></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        my_age = st.number_input("My Age (Years)", 18, 80, current_age)
    with c2:
        retire_age = st.number_input("I want to retire at age", my_age + 1, 80, 50)
    with c3:
        plan_till = st.number_input("I want to plan till age", retire_age + 1, 100, 90)

    st.markdown("### Expense Details")
    e1, e2, e3 = st.columns(3)
    with e1:
        monthly_exp = st.number_input("Monthly Expenses (₹)", 0, 100000000, 60000)
    with e2:
        yearly_one_time = st.number_input("One-time Yearly Expenses (₹)", 0, 100000000, 125000)
    with e3:
        retire_infl = st.number_input("Inflation for Expenses (%)", 0.0, 20.0, 7.0) / 100

    st.markdown("### Retirement Assets")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        eq = st.number_input("Equity + NPS (₹)", 0, 1000000000, 1000000)
    with a2:
        debt = st.number_input("Debt + PPF + EPF (₹)", 0, 1000000000, 1000000)
    with a3:
        real_estate = st.number_input("Real Estate (₹)", 0, 1000000000, 0)
    with a4:
        gold = st.number_input("Gold (₹)", 0, 1000000000, 0)

    total_corpus = eq + debt + real_estate + gold
    curr_sip = st.number_input("Current Monthly SIP + NPS (₹)", 0, 100000000, 57500)
    curr_step = st.number_input("Current Annual Step-up (%)", 0.0, 50.0, 8.0) / 100
    post_ret_return = st.number_input("Post Retirement Expected Return (%)", 0.0, 20.0, 8.0) / 100

    years_to_ret = retire_age - my_age
    ret_years = plan_till - retire_age
    annual_exp_today = monthly_exp * 12 + yearly_one_time
    expense_at_ret = annual_exp_today * ((1 + retire_infl) ** years_to_ret)

    future_existing = total_corpus * ((1 + expected_return) ** years_to_ret)
    sip_future = 0
    sip_now = curr_sip
    for _ in range(1, years_to_ret + 1):
        for _m in range(12):
            sip_future = sip_future * (1 + expected_return / 12) + sip_now
        sip_now *= (1 + curr_step)

    total_future_assets = future_existing + sip_future

    if post_ret_return > retire_infl:
        required_corpus = expense_at_ret * ((1 - ((1 + retire_infl) / (1 + post_ret_return)) ** ret_years) / (post_ret_return - retire_infl))
    else:
        required_corpus = expense_at_ret * ret_years

    gap = max(required_corpus - total_future_assets, 0)
    additional_sip = monthly_sip_required_stepup(gap, expected_return, years_to_ret, 0.05)

    kpi_row([
        ("Required Corpus", fmt(required_corpus)),
        ("Projected Assets", fmt(total_future_assets)),
        ("Gap", fmt(gap)),
        ("Addl SIP (5% Step-up)", fmt(additional_sip))
    ])

    bal = total_future_assets
    rows = []
    exp = expense_at_ret
    for age in range(retire_age, plan_till + 1):
        opening = bal
        bal = bal * (1 + post_ret_return) - exp
        rows.append([age, round(opening,0), round(exp,0), round(bal,0)])
        exp *= (1 + retire_infl)
        if bal <= 0:
            break

    ret_df = pd.DataFrame(rows, columns=["Age", "Year Beginning Balance (₹)", "Year Expense (₹)", "Year End Balance (₹)"])
    st.dataframe(ret_df, use_container_width=True)

    advisor_note("Retirement Recommendation", [
        "Protect retirement corpus from child goals and lifestyle upgrades.",
        "Increase SIP annually with income growth to reduce future gap.",
        "Review retirement inflation assumptions carefully for medical and lifestyle costs."
    ])

# =====================================================
# TERM INSURANCE
# =====================================================
if st.session_state.page == "term":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Term Insurance Calculator</div></div>', unsafe_allow_html=True)

    curr_age = st.number_input("Current Age (Years)", 18, 80, current_age)
    coverage_till = st.number_input("Coverage till Age (Years)", curr_age + 1, 100, 90)
    curr_monthly_income = st.number_input("Current Monthly Income (₹)", 0, 100000000, 200000)
    curr_monthly_expense = st.number_input("Current Monthly Expenses (₹)", 0, 100000000, 50000)
    liabilities = st.number_input("Outstanding Liabilities (₹)", 0, 1000000000, 0)
    existing_cover = st.number_input("Existing Cover (₹)", 0, 1000000000, 0)

    years_left = coverage_till - curr_age
    annual_surplus = max((curr_monthly_income - curr_monthly_expense) * 12, 0)
    hlv = annual_surplus * years_left
    recommended_cover = max(hlv + liabilities - existing_cover, 0)

    kpi_row([
        ("Recommended Cover", fmt(recommended_cover)),
        ("Coverage Till", str(coverage_till)),
        ("Existing Cover", fmt(existing_cover))
    ])

    advisor_note("Insurance Recommendation", [
        "Term plan is a protection product, not an investment product.",
        "Buying early reduces premium and locks insurability.",
        "Reassess cover after major life events like marriage, children, or large loans."
    ])

# =====================================================
# CASHFLOW PLANNER
# =====================================================
if st.session_state.page == "cashflow":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Cashflow Planner</div></div>', unsafe_allow_html=True)

    st.markdown("### CASH INFLOWS")
    salary = st.number_input("Salary/Wages (After-Tax)", 0, 100000000, 1000000)
    side = st.number_input("Side Hustle / Freelance", 0, 100000000, 0)
    inv_income = st.number_input("Investment Income (Dividends, Interest)", 0, 100000000, 0)
    other_inc = st.number_input("Other Income (Rental, Tax Refund)", 0, 100000000, 0)
    total_inflow = salary + side + inv_income + other_inc

    st.markdown("### CASH OUTFLOWS - Fixed Expenses")
    rent = st.number_input("Rent / Mortgage", 0, 100000000, 300000)
    utilities = st.number_input("Utilities", 0, 100000000, 60000)
    debt = st.number_input("Debt Payments", 0, 100000000, 0)
    insurance = st.number_input("Insurance", 0, 100000000, 50000)
    childcare = st.number_input("Childcare / Alimony", 0, 100000000, 0)

    st.markdown("### CASH OUTFLOWS - Variable Expenses")
    groceries = st.number_input("Groceries", 0, 100000000, 120000)
    dining = st.number_input("Dining Out / Entertainment", 0, 100000000, 60000)
    transport = st.number_input("Transportation / Fuel", 0, 100000000, 50000)
    shopping = st.number_input("Shopping / Subscriptions", 0, 100000000, 50000)

    st.markdown("### CASH OUTFLOWS - Savings & Investments")
    emergency = st.number_input("Emergency Fund Savings", 0, 100000000, 50000)
    retirement_contrib = st.number_input("Retirement Contributions", 0, 100000000, 100000)
    investments = st.number_input("Investments", 0, 100000000, 150000)

    total_outflow = rent + utilities + debt + insurance + childcare + groceries + dining + transport + shopping + emergency + retirement_contrib + investments
    net_cf = total_inflow - total_outflow

    kpi_row([
        ("Total Inflow", fmt(total_inflow)),
        ("Total Outflow", fmt(total_outflow)),
        ("Net Cash Flow", fmt(net_cf))
    ])

    cashflow_df = pd.DataFrame([
        ["CASH INFLOWS", "Total Inflow (A)", total_inflow],
        ["TOTAL OUTFLOW", "Total Outflow (B)", total_outflow],
        ["NET CASH FLOW", "A - B", net_cf],
    ], columns=["Category", "Item", "Amount (₹)"])

    st.dataframe(cashflow_df, use_container_width=True)

    advisor_note("Cashflow Recommendation", [
        "Positive cashflow should be directed toward goals and emergency reserve.",
        "Track lifestyle inflation yearly.",
        "Keep fixed obligations controlled to protect investing capacity."
    ])

# =====================================================
# CAR PURCHASE
# =====================================================
if st.session_state.page == "car":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Car Purchase Planner</div></div>', unsafe_allow_html=True)

    car_cost = st.number_input("Car Cost Today (₹)", 0, 100000000, 1500000)
    down = st.number_input("Down Payment Available (₹)", 0, 100000000, 300000)
    after = st.number_input("Purchase After (Years)", 1, 20, 3)

    future_car = future_value(car_cost, inflation, after)
    gap = max(future_car - down, 0)
    sip_need = monthly_sip_required(gap, expected_return, after)
    lump_need = lumpsum_required(gap, expected_return, after)

    kpi_row([
        ("Future Car Cost", fmt(future_car)),
        ("Funding Gap", fmt(gap)),
        ("Monthly SIP", fmt(sip_need)),
        ("Lumpsum Today", fmt(lump_need))
    ])

# =====================================================
# HOUSE PLANNING
# =====================================================
if st.session_state.page == "house":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">House Planning</div></div>', unsafe_allow_html=True)

    house_cost = st.number_input("House Cost Today (₹)", 0, 1000000000, 10000000)
    available = st.number_input("Available Down Payment (₹)", 0, 1000000000, 2000000)
    after = st.number_input("Buy House After (Years)", 1, 30, 5)
    home_loan_rate = st.number_input("Home Loan Rate (%)", 0.0, 20.0, 8.5) / 100
    loan_years = st.number_input("Loan Tenure (Years)", 1, 30, 20)

    future_house = future_value(house_cost, inflation, after)
    target_down = future_house * 0.20
    gap = max(target_down - available, 0)
    sip_need = monthly_sip_required(gap, expected_return, after)
    loan_amount = max(future_house - target_down, 0)
    emi = emi_calculator(loan_amount, home_loan_rate, loan_years)

    kpi_row([
        ("Future House Cost", fmt(future_house)),
        ("20% Down Payment", fmt(target_down)),
        ("Monthly SIP", fmt(sip_need)),
        ("Estimated EMI", fmt(emi))
    ])

# =====================================================
# EMI VS SIP CALCULATOR
# =====================================================
if st.session_state.page == "emi_vs_sip":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">EMI vs SIP Calculator</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        asset_cost = st.number_input("Asset / Loan Amount (₹)", 0, 1000000000, 1000000)
        down_payment = st.number_input("Down Payment (₹)", 0, 1000000000, 200000)
        loan_rate = st.number_input("Loan Interest Rate (%)", 0.0, 25.0, 9.0) / 100
        loan_years = st.number_input("Loan Tenure (Years)", 1, 30, 5)
    with c2:
        sip_return_alt = st.number_input("Expected SIP Return (%)", 0.0, 25.0, 12.0) / 100
        compare_years = st.number_input("Comparison Period (Years)", 1, 30, int(loan_years))
        annual_stepup_alt = st.number_input("SIP Annual Step-up (%)", 0.0, 30.0, 0.0) / 100

    loan_principal = max(asset_cost - down_payment, 0)
    emi = emi_calculator(loan_principal, loan_rate, loan_years)

    sip_corpus = 0
    monthly_sip_alt = emi
    total_sip_invested = 0
    months_alt = int(compare_years * 12)
    for m in range(1, months_alt + 1):
        sip_corpus = sip_corpus * (1 + sip_return_alt / 12) + monthly_sip_alt
        total_sip_invested += monthly_sip_alt
        if annual_stepup_alt > 0 and m % 12 == 0:
            monthly_sip_alt *= (1 + annual_stepup_alt)

    total_emi_outflow = emi * min(int(loan_years * 12), months_alt)
    wealth_difference = sip_corpus - total_emi_outflow

    kpi_row([
        ("Monthly EMI", fmt(emi)),
        ("Total EMI Outflow", fmt(total_emi_outflow)),
        ("SIP Corpus (If Invested)", fmt(sip_corpus)),
        ("Wealth Gap", fmt(wealth_difference))
    ])

    compare_df = pd.DataFrame({
        "Metric": ["Loan Principal", "Monthly EMI", "Total EMI Outflow", "Equivalent SIP", "Projected SIP Corpus", "Net Wealth Difference"],
        "Value (₹)": [round(loan_principal,0), round(emi,0), round(total_emi_outflow,0), round(emi,0), round(sip_corpus,0), round(wealth_difference,0)]
    })
    st.dataframe(compare_df, use_container_width=True, hide_index=True)

    advisor_note("EMI vs SIP Recommendation", [
        "If the asset is non-essential, compare EMI burden with wealth creation lost via SIP.",
        "For depreciating assets, financing should be balanced against long-term investment discipline.",
        "Use this module in client meetings to show opportunity cost of EMIs."
    ])

# =====================================================
# iPHONE PURCHASE
# =====================================================
if st.session_state.page == "iphone":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">iPhone Purchase Planner</div></div>', unsafe_allow_html=True)

    cost = st.number_input("iPhone Cost Today (₹)", 0, 1000000, 80000)
    months = st.number_input("Buy After (Months)", 1, 60, 12)
    existing = st.number_input("Existing Savings (₹)", 0, 1000000, 10000)

    monthly_infl = (1 + inflation) ** (1/12) - 1
    future_cost = cost * ((1 + monthly_infl) ** months)
    gap = max(future_cost - existing, 0)
    r = expected_return / 12
    sip_need = gap / ((((1 + r) ** months - 1) / r) * (1 + r)) if r > 0 and months > 0 else (gap / months if months > 0 else gap)

    kpi_row([
        ("Future Cost", fmt(future_cost)),
        ("Funding Gap", fmt(gap)),
        ("Monthly SIP", fmt(sip_need))
    ])

# =====================================================
# PORTFOLIO ALLOCATION
# =====================================================
if st.session_state.page == "portfolio":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Portfolio Allocation</div></div>', unsafe_allow_html=True)

    total = st.number_input("Total Investible Corpus (₹)", 0, 1000000000, 10000000)
    risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])

    if risk == "Conservative":
        eq, debt, gold, cash = 30, 50, 10, 10
    elif risk == "Moderate":
        eq, debt, gold, cash = 55, 25, 10, 10
    else:
        eq, debt, gold, cash = 75, 10, 5, 10

    df = pd.DataFrame({
        "Asset Class": ["Equity", "Debt", "Gold", "Cash / Liquid"],
        "Allocation %": [eq, debt, gold, cash],
        "Amount (₹)": [total*eq/100, total*debt/100, total*gold/100, total*cash/100]
    })

    st.dataframe(df, use_container_width=True)

# =====================================================
# FUND SUGGESTION & PERFORMANCE
# =====================================================
if st.session_state.page == "fund_suggestion":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Mutual Fund Suggestion & Performance</div></div>', unsafe_allow_html=True)

    risk_profile = st.selectbox("Client Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    investment_horizon = st.selectbox("Investment Horizon", ["1-3 Years", "3-5 Years", "5+ Years"])

    fund_data = [
        ["Tata Multi Asset Opportunities Fund", "Multi Asset", 18.2, 16.1, 15.4, "Moderate", 0.72, 3800, "Diversified core allocation"],
        ["ICICI Prudential Multi-Asset Fund", "Multi Asset", 17.4, 15.3, 14.8, "Moderate", 0.88, 42000, "Balanced all-weather allocation"],
        ["HDFC Balanced Advantage Fund", "Dynamic Hybrid", 15.1, 14.2, 13.0, "Moderate", 1.03, 95000, "Volatility management"],
        ["Parag Parikh Flexi Cap Fund", "Flexi Cap", 20.5, 18.9, 21.2, "Moderate-High", 0.78, 78000, "Long-term core growth"],
        ["Kotak Equity Opportunities Fund", "Large & Mid Cap", 22.0, 19.1, 20.0, "High", 0.74, 21000, "Aggressive growth satellite"],
        ["SBI Short Term Debt Fund", "Short Duration Debt", 7.4, 6.9, 6.8, "Low", 0.42, 14000, "Stability / short-term parking"]
    ]

    funds_df = pd.DataFrame(fund_data, columns=[
        "Fund Name", "Category", "1Y %", "3Y CAGR %", "5Y CAGR %", "Risk", "Expense Ratio %", "AUM (₹ Cr)", "Advisor Role"
    ])

    if risk_profile == "Conservative":
        filtered = funds_df[funds_df["Category"].isin(["Multi Asset", "Dynamic Hybrid", "Short Duration Debt"])]
        model_text = "Suggested Mix: 40% Multi Asset | 35% Dynamic Hybrid | 25% Short Duration Debt"
    elif risk_profile == "Moderate":
        filtered = funds_df[funds_df["Category"].isin(["Multi Asset", "Dynamic Hybrid", "Flexi Cap"])]
        model_text = "Suggested Mix: 35% Multi Asset | 25% Dynamic Hybrid | 40% Flexi Cap"
    else:
        filtered = funds_df[funds_df["Category"].isin(["Flexi Cap", "Large & Mid Cap", "Multi Asset"])]
        model_text = "Suggested Mix: 45% Flexi Cap | 35% Large & Mid Cap | 20% Multi Asset"

    if investment_horizon == "1-3 Years":
        horizon_note = "Prefer stability-oriented allocation. Use debt / hybrid heavier positioning."
    elif investment_horizon == "3-5 Years":
        horizon_note = "Balanced allocation can be used with limited equity volatility tolerance."
    else:
        horizon_note = "Long-term horizon supports higher equity allocation for compounding."

    top_fund = filtered.sort_values(by="3Y CAGR %", ascending=False).iloc[0]

    kpi_row([
        ("Top Suggested Fund", top_fund["Fund Name"][:18] + "..." if len(top_fund["Fund Name"]) > 18 else top_fund["Fund Name"]),
        ("Best 3Y CAGR", f"{top_fund['3Y CAGR %']:.1f}%"),
        ("Risk Profile", risk_profile),
        ("Horizon", investment_horizon)
    ])

    st.markdown(f"""
    <div class="report-panel">
        <div class="report-title">Advisor Allocation Recommendation</div>
        <div class="report-text">
            <b>Model Allocation:</b> {model_text}<br>
            <b>Horizon View:</b> {horizon_note}<br><br>
            <b>Highlighted Example:</b> Tata Multi Asset Opportunities Fund can be used as a core diversified bucket for clients seeking balanced exposure across equity, debt, and commodities / gold-linked allocation style.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    advisor_note("Mutual Fund Recommendation Notes", [
        "Use Tata Multi Asset or ICICI Pru Multi Asset as a diversified core allocation bucket for moderate clients.",
        "Use Parag Parikh Flexi Cap for long-term core equity allocation where valuation discipline matters.",
        "For conservative clients, combine hybrid + debt rather than forcing full equity exposure.",
        "Review performance, rolling returns, and category suitability before final client recommendation."
    ])

# =====================================================
# NET WORTH DASHBOARD
# =====================================================
if st.session_state.page == "networth":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Net Worth Dashboard</div></div>', unsafe_allow_html=True)

    mf = st.number_input("Mutual Funds (₹)", 0, 1000000000, 2000000)
    equity = st.number_input("Direct Equity (₹)", 0, 1000000000, 1000000)
    re_asset = st.number_input("Real Estate (₹)", 0, 10000000000, 5000000)
    cash = st.number_input("Cash / Bank (₹)", 0, 1000000000, 500000)
    gold = st.number_input("Gold / Other Assets (₹)", 0, 1000000000, 300000)

    home_loan = st.number_input("Home Loan (₹)", 0, 1000000000, 0)
    car_loan = st.number_input("Car Loan (₹)", 0, 1000000000, 0)
    other = st.number_input("Other Loans (₹)", 0, 1000000000, 0)

    assets = mf + equity + re_asset + cash + gold
    liabilities = home_loan + car_loan + other
    nw = assets - liabilities

    kpi_row([
        ("Total Assets", fmt(assets)),
        ("Total Liabilities", fmt(liabilities)),
        ("Net Worth", fmt(nw))
    ])

# =====================================================
# GOAL FEASIBILITY
# =====================================================
if st.session_state.page == "goal":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Goal Feasibility Dashboard</div></div>', unsafe_allow_html=True)

    target = st.number_input("Goal Target Amount (₹)", 0, 1000000000, 5000000)
    years = st.number_input("Years to Goal", 1, 40, 10)
    existing = st.number_input("Existing Corpus for Goal (₹)", 0, 1000000000, 500000)
    sip = st.number_input("Current Monthly SIP for Goal (₹)", 0, 100000000, 20000)

    proj = future_value(existing, expected_return, years)
    temp = proj
    for _ in range(years * 12):
        temp = temp * (1 + expected_return / 12) + sip

    shortfall = target - temp
    feas = temp / target * 100 if target > 0 else 0

    kpi_row([
        ("Goal Target", fmt(target)),
        ("Projected Value", fmt(temp)),
        ("Shortfall / Surplus", fmt(shortfall)),
        ("Feasibility", f"{feas:.1f}%")
    ])

# =====================================================
# PORTFOLIO REBALANCING
# =====================================================
if st.session_state.page == "rebalance":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Portfolio Rebalancing Engine</div></div>', unsafe_allow_html=True)

    cur_eq = st.number_input("Current Equity (₹)", 0, 1000000000, 600000)
    cur_debt = st.number_input("Current Debt (₹)", 0, 1000000000, 300000)
    cur_gold = st.number_input("Current Gold (₹)", 0, 1000000000, 100000)

    total = cur_eq + cur_debt + cur_gold

    tgt_eq = st.number_input("Target Equity %", 0, 100, 60)
    tgt_debt = st.number_input("Target Debt %", 0, 100, 30)
    tgt_gold = st.number_input("Target Gold %", 0, 100, 10)

    df = pd.DataFrame({
        "Asset Class": ["Equity", "Debt", "Gold"],
        "Current Amount (₹)": [cur_eq, cur_debt, cur_gold],
        "Target Amount (₹)": [total*tgt_eq/100, total*tgt_debt/100, total*tgt_gold/100]
    })
    df["Buy / Sell (₹)"] = df["Target Amount (₹)"] - df["Current Amount (₹)"]

    st.dataframe(df, use_container_width=True)

# =====================================================
# RETIREMENT MONTE CARLO
# =====================================================
if st.session_state.page == "mc_retirement":
    back_button()
    st.markdown('<div class="imperial-box"><div class="imperial-header">Retirement Monte Carlo Survival Simulator</div></div>', unsafe_allow_html=True)

    corpus = st.number_input("Retirement Corpus (₹)", 0, 10000000000, 30000000)
    withdrawal = st.number_input("Annual Withdrawal (₹)", 0, 1000000000, 1200000)
    years = st.number_input("Retirement Years", 1, 50, 30)
    runs = st.number_input("Simulation Runs", 100, 5000, 1000, step=100)

    np.random.seed(123)
    success = 0
    ending_vals = []

    for _ in range(runs):
        bal = corpus
        wd = withdrawal
        ok = True
        for _y in range(years):
            bal = bal * (1 + np.random.normal(expected_return, 0.12)) - wd
            wd *= (1 + inflation)
            if bal <= 0:
                ok = False
                break
        ending_vals.append(max(bal, 0))
        if ok:
            success += 1

    success_rate = (success / runs * 100 if runs > 0 else 0)
    median_end = np.median(ending_vals) if len(ending_vals) else 0

    kpi_row([
        ("Survival Probability", f"{success_rate:.1f}%"),
        ("Median Ending Corpus", fmt(median_end)),
        ("Simulations", str(runs))
    ])

# =====================================================
# DEFAULT PAGE CHECK
# =====================================================
valid_pages = [
    "home", "sip", "swp", "sip_swp", "children", "retirement", "term",
    "cashflow", "car", "house", "iphone", "portfolio", "networth",
    "goal", "rebalance", "mc_retirement", "emi_vs_sip", "fund_suggestion"
]
if st.session_state.page not in valid_pages:
    st.session_state.page = "home"

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Freedom V6.1 PRODUCTION READY | Boardroom Elite Roman Imperial Edition | For Illustration / Advisory Discussion Purpose Only")
