import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO
from datetime import datetime

# Optional PDF parser
try:
    import pdfplumber
    PDF_OK = True
except Exception:
    PDF_OK = False

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Freedom Ultra Pro V2", layout="wide")

# =====================================================
# THEME / STYLING
# =====================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0B1220 0%, #0F172A 100%);
    color: white;
}

.main-title {
    background: linear-gradient(90deg, #1D4ED8, #06B6D4);
    padding: 22px;
    border-radius: 18px;
    text-align: center;
    color: white;
    font-size: 42px;
    font-weight: 800;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}

.sub-title {
    text-align: center;
    color: #BFDBFE;
    font-size: 16px;
    margin-top: 8px;
    margin-bottom: 18px;
}

.section-title {
    color: #E0F2FE;
    font-size: 22px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 10px;
}

.card-box {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.20);
}

.kpi-card {
    background: linear-gradient(180deg, #111827, #0F172A);
    border: 1px solid #1E3A8A;
    border-radius: 16px;
    padding: 14px;
    text-align: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.20);
}

.kpi-title {
    color: #93C5FD;
    font-size: 13px;
    font-weight: 600;
}

.kpi-value {
    color: white;
    font-size: 24px;
    font-weight: 800;
    margin-top: 6px;
}

.stButton > button {
    width: 100%;
    height: 48px;
    border-radius: 12px;
    border: none;
    background: linear-gradient(90deg, #2563EB, #06B6D4);
    color: white;
    font-weight: 700;
    margin-bottom: 8px;
    box-shadow: 0 4px 12px rgba(37,99,235,0.25);
}

.stDownloadButton > button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(90deg, #059669, #10B981);
    color: white;
    font-weight: 700;
    border: none;
}

section[data-testid="stSidebar"] {
    background: #111827;
}

label, .stMarkdown, .stText, .stCaption {
    color: #E5E7EB !important;
}

[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 10px;
}

thead tr th {
    background-color: #2563EB !important;
    color: white !important;
}

tbody tr td {
    color: #E5E7EB !important;
}

hr {
    border: none;
    border-top: 1px solid #1F2937;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page

# =====================================================
# HELPERS
# =====================================================
def fmt(x):
    try:
        return f"₹ {x:,.0f}"
    except:
        return "₹ 0"

def future_value(pv, rate, years):
    return pv * ((1 + rate) ** max(years, 0))

def monthly_sip_required(target, annual_rate, years):
    months = int(max(years, 0) * 12)
    if months <= 0:
        return 0
    r = annual_rate / 12
    if r <= 0:
        return target / months
    factor = ((1 + r) ** months - 1) / r
    return target / factor if factor > 0 else 0

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
    except:
        return np.nan

def normalize_txn_type(x):
    x = str(x).lower().strip()

    buy = [
        "purchase", "sip", "systematic investment", "switch in", "stp in",
        "allotment", "buy", "investment", "additional purchase"
    ]
    sell = [
        "redemption", "switch out", "sell", "withdrawal", "swp", "stp out", "redeem"
    ]
    current = [
        "current value", "market value", "current market value", "valuation"
    ]

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

def kpi_card(title, value):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# HEADER
# =====================================================
st.markdown('<div class="main-title">Freedom Ultra Pro V2</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Professional Wealth Planning & Mutual Fund Advisory Platform</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================================
# SIDEBAR - CLIENT PROFILE
# =====================================================
st.sidebar.header("Client Profile")

client_name = st.sidebar.text_input("Client Name", "Client")
current_age = st.sidebar.number_input("Current Age", 18, 80, 35)
inflation = st.sidebar.number_input("General Inflation (%)", 0.0, 20.0, 6.0) / 100
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 25.0, 12.0) / 100
monthly_income_global = st.sidebar.number_input("Monthly Income (₹)", 0, 100000000, 100000)
monthly_expense_global = st.sidebar.number_input("Monthly Expense (₹)", 0, 100000000, 60000)

# =====================================================
# HOME PAGE - PROFESSIONAL LANDING DASHBOARD
# =====================================================
if st.session_state.page == "home":
    st.markdown('<div class="section-title">Advisor Landing Dashboard</div>', unsafe_allow_html=True)

    # Sample KPI cards based on sidebar values
    monthly_surplus = monthly_income_global - monthly_expense_global
    annual_surplus = monthly_surplus * 12
    projected_10y = 0
    if annual_surplus > 0:
        for _ in range(10):
            projected_10y = (projected_10y + annual_surplus) * (1 + expected_return)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        kpi_card("Client", client_name)
    with k2:
        kpi_card("Monthly Surplus", fmt(monthly_surplus))
    with k3:
        kpi_card("Annual Surplus", fmt(annual_surplus))
    with k4:
        kpi_card("10Y Wealth Potential", fmt(projected_10y))
    with k5:
        kpi_card("Inflation", f"{inflation*100:.1f}%")
    with k6:
        kpi_card("Expected Return", f"{expected_return*100:.1f}%")

    st.markdown("### Wealth Planning Modules")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.button("SIP Calculator", on_click=lambda: go("sip"))
        st.button("Children Planner Pro", on
