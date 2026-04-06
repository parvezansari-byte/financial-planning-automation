# app.py
# ============================================================
# FINAL Freedom ULTRA PRO V11 ELITE DASHBOARD
# ULTRA ATTRACTIVE HOME SCREEN + TRUE CARD NAVIGATION + SECTION-WISE MODULES
# Single-file Streamlit app | No Sidebar | Premium MFD UI
# GitHub / Streamlit Cloud Ready
# Run: streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime
from io import BytesIO

# ============================================================
# OPTIONAL PDF SUPPORT
# ============================================================
PDF_AVAILABLE = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    )
except Exception:
    PDF_AVAILABLE = False

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Freedom ULTRA PRO V11 ELITE DASHBOARD",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# PREMIUM CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root{
    --bg1:#040816;
    --bg2:#081224;
    --bg3:#0f172a;
    --glass:rgba(15,23,42,0.74);
    --glass2:rgba(17,24,39,0.82);
    --line:rgba(255,255,255,0.08);
    --line2:rgba(255,255,255,0.12);
    --text:#f8fafc;
    --muted:#94a3b8;
    --green:#22c55e;
    --blue:#3b82f6;
    --amber:#f59e0b;
    --pink:#ec4899;
    --red:#ef4444;
    --cyan:#06b6d4;
    --violet:#8b5cf6;
    --shadow:0 16px 40px rgba(0,0,0,0.30);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(59,130,246,0.16), transparent 28%),
        radial-gradient(circle at 90% 8%, rgba(34,197,94,0.12), transparent 22%),
        radial-gradient(circle at 85% 88%, rgba(139,92,246,0.08), transparent 22%),
        radial-gradient(circle at 12% 85%, rgba(236,72,153,0.08), transparent 22%),
        linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 45%, var(--bg3) 100%);
    color: var(--text);
}

[data-testid="stSidebar"] {display:none !important;}

.block-container{
    max-width: 1550px;
    padding-top: 0.8rem;
    padding-bottom: 2rem;
    padding-left: 1.1rem;
    padding-right: 1.1rem;
}

.header-hero{
    position: relative;
    overflow: hidden;
    background:
      linear-gradient(135deg, rgba(34,197,94,0.10), rgba(59,130,246,0.14), rgba(139,92,246,0.10));
    border: 1px solid var(--line);
    border-radius: 28px;
    padding: 22px 24px;
    box-shadow: var(--shadow);
    margin-bottom: 14px;
    backdrop-filter: blur(14px);
}
.header-hero:before{
    content:'';
    position:absolute;
    top:-80px; right:-40px;
    width:220px; height:220px;
    background: radial-gradient(circle, rgba(255,255,255,0.10), transparent 60%);
    border-radius:50%;
}
.header-hero:after{
    content:'';
    position:absolute;
    bottom:-60px; left:-20px;
    width:180px; height:180px;
    background: radial-gradient(circle, rgba(34,197,94,0.10), transparent 60%);
    border-radius:50%;
}

.brand-title{
    font-size: 42px;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 0.2px;
    margin-bottom: 4px;
}
.brand-sub{
    font-size: 13px;
    color: #dbe4f0;
    margin-bottom: 10px;
}
.badge-row{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
}
.badge-pill{
    display:inline-block;
    padding:6px 12px;
    border-radius:999px;
    font-size:12px;
    font-weight:700;
    background: rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.08);
    color:#e2e8f0;
}

.top-strip{
    background: rgba(255,255,255,0.03);
    border:1px solid var(--line);
    border-radius:18px;
    padding:12px 14px;
    margin-bottom: 14px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.18);
}

.ribbon{
    background: rgba(255,255,255,0.03);
    border:1px solid var(--line);
    border-radius:18px;
    padding:14px;
    margin-bottom:14px;
    backdrop-filter: blur(10px);
}

.kpi-card{
    background: linear-gradient(180deg, rgba(17,24,39,0.78), rgba(15,23,42,0.86));
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 16px;
    box-shadow: var(--shadow);
    min-height: 112px;
    backdrop-filter: blur(10px);
}
.kpi-title{
    font-size:12px;
    color: #94a3b8;
    margin-bottom:8px;
}
.kpi-value{
    font-size:24px;
    font-weight:900;
    color:#ffffff;
    line-height:1.15;
}
.kpi-sub{
    font-size:11px;
    color:#cbd5e1;
    margin-top:6px;
}

.mega-kpi{
    background: linear-gradient(180deg, rgba(17,24,39,0.78), rgba(15,23,42,0.86));
    border:1px solid var(--line);
    border-radius:22px;
    padding:14px;
    min-height:104px;
    box-shadow: var(--shadow);
}

.section-card{
    background: linear-gradient(180deg, rgba(17,24,39,0.76), rgba(15,23,42,0.86));
    border:1px solid var(--line);
    border-radius:24px;
    padding:18px;
    box-shadow: var(--shadow);
    margin-bottom:14px;
    backdrop-filter: blur(12px);
}

.module-card{
    background: linear-gradient(180deg, rgba(17,24,39,0.76), rgba(15,23,42,0.86));
    border:1px solid var(--line);
    border-radius:22px;
    padding:14px;
    min-height:170px;
    box-shadow: var(--shadow);
}
.module-title{
    font-size:16px;
    font-weight:800;
    margin-bottom:8px;
}
.module-desc{
    font-size:12px;
    color: #94a3b8;
    min-height: 42px;
}
.module-tag{
    font-size:11px;
    color:#dbeafe;
    font-weight:700;
    margin-top:10px;
}

.quick-tile{
    background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(59,130,246,0.10));
    border:1px solid rgba(255,255,255,0.08);
    border-radius:20px;
    padding:14px;
    min-height:110px;
    box-shadow: var(--shadow);
}

.section-head{
    font-size:20px;
    font-weight:900;
    margin-bottom:12px;
}

.report-center{
    background: linear-gradient(180deg, rgba(34,197,94,0.08), rgba(59,130,246,0.08));
    border:1px solid var(--line);
    border-radius:22px;
    padding:16px;
    margin-top:16px;
    box-shadow: var(--shadow);
}

.footer-note{
    color:#94a3b8;
    font-size:12px;
}

.stButton > button{
    width:100%;
    border-radius:14px;
    border:1px solid rgba(255,255,255,0.08);
    background: linear-gradient(135deg, rgba(34,197,94,0.16), rgba(59,130,246,0.16));
    color:#ffffff;
    font-weight:800;
    padding:0.72rem 1rem;
    transition: all 0.2s ease-in-out;
}
.stButton > button:hover{
    transform: translateY(-1px);
    border-color: rgba(255,255,255,0.12);
    box-shadow: 0 10px 22px rgba(0,0,0,0.22);
}

div[data-testid="stMetric"]{
    background: rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:14px;
    padding:10px;
}

.stTabs [data-baseweb="tab-list"]{
    gap:8px;
}
.stTabs [data-baseweb="tab"]{
    background: rgba(255,255,255,0.04);
    border-radius:12px;
    padding:8px 14px;
}
.stTabs [aria-selected="true"]{
    background: rgba(34,197,94,0.18) !important;
}

hr{
    border-color: rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INIT
# ============================================================
DEFAULT_PAGE = "Dashboard"

if "page" not in st.session_state:
    st.session_state.page = DEFAULT_PAGE

if "report_rows" not in st.session_state:
    st.session_state.report_rows = []

if "advisor_notes" not in st.session_state:
    st.session_state.advisor_notes = ""

if "client_name" not in st.session_state:
    st.session_state.client_name = ""

if "client_age" not in st.session_state:
    st.session_state.client_age = 30

if "client_income" not in st.session_state:
    st.session_state.client_income = 50000.0

if "client_city" not in st.session_state:
    st.session_state.client_city = "Bengaluru"

if "client_risk" not in st.session_state:
    st.session_state.client_risk = "Moderate"

if "presentation_mode" not in st.session_state:
    st.session_state.presentation_mode = False

# ============================================================
# HELPERS
# ============================================================
def reroute(page_name: str):
    st.session_state.page = page_name
    st.rerun()

def safe_div(a, b):
    return a / b if b not in [0, None] else 0

def fmt_inr(x):
    try:
        x = float(x)
    except Exception:
        return "₹0"
    sign = "-" if x < 0 else ""
    x = abs(x)
    if x >= 1e7:
        return f"{sign}₹{x/1e7:,.2f} Cr"
    elif x >= 1e5:
        return f"{sign}₹{x/1e5:,.2f} L"
    else:
        return f"{sign}₹{x:,.2f}"

def annual_to_monthly(rate_annual_percent):
    return rate_annual_percent / 12 / 100

def future_value_lumpsum(pv, annual_rate, years):
    r = annual_rate / 100
    return pv * ((1 + r) ** years)

def future_value_sip(monthly_investment, annual_rate, years):
    r = annual_to_monthly(annual_rate)
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return monthly_investment * n
    return monthly_investment * (((1 + r) ** n - 1) / r) * (1 + r)

def required_sip_for_goal(goal_amount, annual_rate, years):
    r = annual_to_monthly(annual_rate)
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return goal_amount / n
    factor = (((1 + r) ** n - 1) / r) * (1 + r)
    return goal_amount / factor

def future_value_stepup_sip(monthly_sip, annual_rate, years, stepup_percent):
    r = annual_to_monthly(annual_rate)
    total = 0
    for y in range(int(math.ceil(years))):
        sip_for_year = monthly_sip * ((1 + stepup_percent / 100) ** y)
        months_remaining = int(max((years - y) * 12, 0))
        if months_remaining <= 0:
            continue
        months_this_year = min(12, months_remaining)
        if r == 0:
            fv_year = sip_for_year * months_this_year
        else:
            fv_year = sip_for_year * (((1 + r) ** months_this_year - 1) / r) * (1 + r)
        growth_after = max(months_remaining - months_this_year, 0)
        fv_year *= ((1 + r) ** growth_after)
        total += fv_year
    return total

def inflated_goal(current_cost, inflation, years):
    return current_cost * ((1 + inflation / 100) ** years)

def retirement_corpus_needed(monthly_expense_today, inflation, post_ret_return, years_to_retirement, years_in_retirement):
    expense_at_ret = monthly_expense_today * ((1 + inflation / 100) ** years_to_retirement)
    annual_expense_ret = expense_at_ret * 12
    real_return = ((1 + post_ret_return / 100) / (1 + inflation / 100)) - 1
    if abs(real_return) < 1e-9:
        corpus = annual_expense_ret * years_in_retirement
    else:
        corpus = annual_expense_ret * (1 - (1 + real_return) ** (-years_in_retirement)) / real_return
    return corpus, expense_at_ret

def emi(principal, annual_rate, years):
    r = annual_to_monthly(annual_rate)
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return principal / n
    return principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)

def loan_eligibility(monthly_income, foir_percent, existing_emi, annual_rate, years):
    max_emi = monthly_income * foir_percent / 100 - existing_emi
    max_emi = max(max_emi, 0)
    r = annual_to_monthly(annual_rate)
    n = int(years * 12)
    if n <= 0:
        return 0, max_emi
    if r == 0:
        return max_emi * n, max_emi
    principal = max_emi * ((((1 + r) ** n) - 1) / (r * ((1 + r) ** n)))
    return principal, max_emi

def swp_duration(corpus, monthly_withdrawal, annual_return):
    r = annual_to_monthly(annual_return)
    if monthly_withdrawal <= 0:
        return float("inf")
    if r == 0:
        return corpus / monthly_withdrawal
    if monthly_withdrawal <= corpus * r:
        return float("inf")
    try:
        n = -math.log(1 - (corpus * r / monthly_withdrawal)) / math.log(1 + r)
        return n
    except Exception:
        return 0

def insurance_human_life_value(annual_income, years_to_work, personal_expense_ratio=30, discount_rate=6):
    contribution = annual_income * (1 - personal_expense_ratio / 100)
    r = discount_rate / 100
    if r == 0:
        return contribution * years_to_work
    return contribution * (1 - (1 + r) ** (-years_to_work)) / r

def emergency_fund(monthly_expense, months):
    return monthly_expense * months

def asset_allocation(age, risk_profile):
    if risk_profile == "Conservative":
        equity = max(20, 80 - age)
    elif risk_profile == "Moderate":
        equity = max(30, 100 - age)
    else:
        equity = max(40, 120 - age)
    equity = min(max(equity, 20), 85)
    debt = 100 - equity
    gold = 0
    if risk_profile in ["Moderate", "Aggressive"]:
        gold = 10
        debt = max(debt - 10, 10)
    return equity, debt, gold

def basic_tax_old_regime(annual_income):
    taxable = max(annual_income - 50000, 0)
    tax = 0
    slabs = [(250000, 0), (250000, 0.05), (500000, 0.20), (float("inf"), 0.30)]
    remaining = taxable
    for slab_amt, rate in slabs:
        amt = min(remaining, slab_amt)
        tax += amt * rate
        remaining -= amt
        if remaining <= 0:
            break
    if taxable <= 500000:
        tax = 0
    return tax * 1.04

def basic_tax_new_regime(annual_income):
    taxable = max(annual_income - 75000, 0)
    slabs = [
        (400000, 0.00),
        (400000, 0.05),
        (400000, 0.10),
        (400000, 0.15),
        (400000, 0.20),
        (float("inf"), 0.30),
    ]
    tax = 0
    remaining = taxable
    for slab_amt, rate in slabs:
        amt = min(remaining, slab_amt)
        tax += amt * rate
        remaining -= amt
        if remaining <= 0:
            break
    if taxable <= 1200000:
        tax = 0
    return tax * 1.04

def add_report(module_name, metric_name, value, remarks=""):
    st.session_state.report_rows.append({
        "Module": module_name,
        "Metric": metric_name,
        "Value": value,
        "Remarks": remarks
    })

def report_df():
    if not st.session_state.report_rows:
        return pd.DataFrame(columns=["Module", "Metric", "Value", "Remarks"])
    return pd.DataFrame(st.session_state.report_rows)

def to_csv_download(df):
    return df.to_csv(index=False).encode("utf-8")

def build_pdf(df, client_info, advisor_notes):
    if not PDF_AVAILABLE:
        return None
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleX', parent=styles['Title'], textColor=colors.HexColor("#0f172a"), fontSize=18, leading=22)
    normal = styles["BodyText"]
    story = []
    story.append(Paragraph("Freedom ULTRA PRO V11 ELITE DASHBOARD - Client Financial Planning Report", title_style))
    story.append(Spacer(1, 10))

    lines = [
        f"Client Name: {client_info.get('name', '')}",
        f"Age: {client_info.get('age', '')}",
        f"Monthly Income: {client_info.get('income', '')}",
        f"City: {client_info.get('city', '')}",
        f"Risk Profile: {client_info.get('risk', '')}",
        f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    ]
    for line in lines:
        story.append(Paragraph(line, normal))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Advisor Notes", styles["Heading2"]))
    story.append(Paragraph(advisor_notes if advisor_notes else "No advisor notes added.", normal))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Summary Report", styles["Heading2"]))
    if df.empty:
        story.append(Paragraph("No report items added yet.", normal))
    else:
        table_data = [list(df.columns)] + df.astype(str).values.tolist()
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f8fafc")),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer

def render_kpi_cards(cards):
    cols = st.columns(len(cards))
    for i, card in enumerate(cards):
        with cols[i]:
            subtitle = f"<div class='kpi-sub'>{card.get('sub','')}</div>" if card.get("sub") else ""
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{card['title']}</div>
                <div class="kpi-value">{card['value']}</div>
                {subtitle}
            </div>
            """, unsafe_allow_html=True)

def render_mega_kpis(cards):
    cols = st.columns(len(cards))
    for i, card in enumerate(cards):
        with cols[i]:
            st.markdown(f"""
            <div class="mega-kpi">
                <div class="kpi-title">{card['title']}</div>
                <div class="kpi-value">{card['value']}</div>
                <div class="kpi-sub">{card.get('sub','')}</div>
            </div>
            """, unsafe_allow_html=True)

def monthly_projection_table(monthly_investment, annual_rate, years):
    r = annual_to_monthly(annual_rate)
    n = int(years * 12)
    rows = []
    balance = 0
    invested = 0
    for m in range(1, n + 1):
        balance = (balance + monthly_investment) * (1 + r)
        invested += monthly_investment
        if m % 12 == 0 or m == n:
            rows.append({
                "Year": math.ceil(m / 12),
                "Invested": round(invested, 2),
                "Value": round(balance, 2),
                "Gain": round(balance - invested, 2)
            })
    return pd.DataFrame(rows)

def stepup_projection_table(monthly_sip, annual_rate, years, stepup_percent):
    rows = []
    total_value = 0
    total_invested = 0
    r = annual_to_monthly(annual_rate)
    remaining_months = int(years * 12)
    for y in range(1, int(math.ceil(years)) + 1):
        sip = monthly_sip * ((1 + stepup_percent / 100) ** (y - 1))
        months_this_year = min(12, remaining_months)
        if months_this_year <= 0:
            break
        invested_this_year = sip * months_this_year
        total_invested += invested_this_year
        if r == 0:
            fv_this_year = invested_this_year
        else:
            fv_this_year = sip * (((1 + r) ** months_this_year - 1) / r) * (1 + r)
        total_value = total_value * ((1 + r) ** months_this_year) + fv_this_year
        rows.append({
            "Year": y,
            "Monthly SIP": round(sip, 2),
            "Total Invested": round(total_invested, 2),
            "Portfolio Value": round(total_value, 2),
            "Gain": round(total_value - total_invested, 2)
        })
        remaining_months -= months_this_year
    return pd.DataFrame(rows)

def back_button():
    c1, c2 = st.columns([1.2, 6])
    with c1:
        if st.button("⬅️ Dashboard"):
            reroute("Dashboard")

def module_card(title, desc, page_key, tag="Planner", btn_label="Open Module"):
    st.markdown(f"""
    <div class="module-card">
        <div class="module-title">{title}</div>
        <div class="module-desc">{desc}</div>
        <div class="module-tag">{tag}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(btn_label, key=f"open_{page_key}"):
        reroute(page_key)

def quick_tile(title, desc, page_key):
    st.markdown(f"""
    <div class="quick-tile">
        <div class="module-title">{title}</div>
        <div class="module-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch", key=f"quick_{page_key}"):
        reroute(page_key)

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="header-hero">
    <div class="brand-title">💼 Freedom ULTRA PRO V11 ELITE DASHBOARD</div>
    <div class="brand-sub">ULTRA ATTRACTIVE HOME SCREEN • TRUE CARD NAVIGATION • SECTION-WISE MODULES • Premium MFD Financial Planning Super App • No Sidebar • Single File</div>
    <div class="badge-row">
        <span class="badge-pill">Elite Dashboard</span>
        <span class="badge-pill">True Card Navigation</span>
        <span class="badge-pill">Overall Cashflow Master</span>
        <span class="badge-pill">CSV + PDF Report Center</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# TOP NAV STRIP
# ============================================================
st.markdown('<div class="top-strip">', unsafe_allow_html=True)
n1, n2, n3, n4, n5, n6 = st.columns([1.25, 1.35, 1.35, 1.3, 1.15, 1.5])
with n1:
    if st.button("🏠 Dashboard"):
        reroute("Dashboard")
with n2:
    if st.button("💵 Overall Cashflow"):
        reroute("Overall Cashflow Master")
with n3:
    if st.button("📄 Report Center"):
        reroute("Report Center")
with n4:
    if st.button("📝 Advisor Notes"):
        reroute("Advisor Notes")
with n5:
    if st.button("🧹 Clear Report"):
        st.session_state.report_rows = []
        st.success("Report cleared.")
with n6:
    st.session_state.presentation_mode = st.toggle("🎤 Presentation Mode", value=st.session_state.presentation_mode)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# CLIENT RIBBON
# ============================================================
if not st.session_state.presentation_mode:
    st.markdown('<div class="ribbon">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.session_state.client_name = st.text_input("Client Name", value=st.session_state.client_name, key="global_name_v11")
    with c2:
        st.session_state.client_age = st.number_input("Age", min_value=0, max_value=100, value=int(st.session_state.client_age), key="global_age_v11")
    with c3:
        st.session_state.client_income = st.number_input("Monthly Income (₹)", min_value=0.0, value=float(st.session_state.client_income), step=1000.0, key="global_income_v11")
    with c4:
        st.session_state.client_city = st.text_input("City", value=st.session_state.client_city, key="global_city_v11")
    with c5:
        idx = ["Conservative", "Moderate", "Aggressive"].index(st.session_state.client_risk)
        st.session_state.client_risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"], index=idx, key="global_risk_v11")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# GLOBAL KPI STRIP
# ============================================================
global_monthly_income = st.session_state.client_income
estimated_savings = global_monthly_income * 0.25
eq_alloc, debt_alloc, gold_alloc = asset_allocation(st.session_state.client_age, st.session_state.client_risk)

render_kpi_cards([
    {"title": "Client", "value": st.session_state.client_name or "Not Set", "sub": f"City: {st.session_state.client_city}"},
    {"title": "Monthly Income", "value": fmt_inr(global_monthly_income), "sub": "Primary earning snapshot"},
    {"title": "Suggested Savings", "value": fmt_inr(estimated_savings), "sub": "25% planning benchmark"},
    {"title": "Risk Profile", "value": st.session_state.client_risk, "sub": f"Suggested Equity {eq_alloc}%"},
])

# ============================================================
# ROUTER
# ============================================================
page = st.session_state.page

# ============================================================
# DASHBOARD
# ============================================================
if page == "Dashboard":
    st.subheader("🏠 Executive Dashboard Elite")

    # Quick Actions
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">⚡ Quick Action Tiles</div>', unsafe_allow_html=True)
    q1, q2, q3, q4, q5, q6 = st.columns(6)
    with q1: quick_tile("👤 New Client Meeting", "Capture client profile and planning inputs.", "Client Profile")
    with q2: quick_tile("💵 Cashflow Review", "Review total income, expenses, EMI and investable surplus.", "Overall Cashflow Master")
    with q3: quick_tile("🎯 Goal Check", "Quick goal planning with inflated cost and SIP.", "Goal Planner")
    with q4: quick_tile("🛡️ Insurance Review", "Term cover and family floater guidance.", "Insurance Planner")
    with q5: quick_tile("🧓 Retirement Review", "Retirement corpus and monthly SIP need.", "Retirement Planner")
    with q6: quick_tile("📄 Generate Report", "Open summary report center and export.", "Report Center")
    st.markdown('</div>', unsafe_allow_html=True)

    # Mega KPI strip
    monthly_surplus_est = global_monthly_income * 0.25
    savings_ratio_est = safe_div(monthly_surplus_est, max(global_monthly_income, 1)) * 100
    emergency_gap_est = max(global_monthly_income * 6 - global_monthly_income * 2, 0)
    insurance_gap_est = max(global_monthly_income * 12 * 15 - global_monthly_income * 12 * 8, 0)
    retirement_readiness = min(100, round((st.session_state.client_age / 60) * 40 + (eq_alloc * 0.5)))
    fire_progress = min(100, round((estimated_savings * 12 * 5) / max(global_monthly_income * 12 * 25, 1) * 1000))

    render_mega_kpis([
        {"title": "Net Monthly Surplus", "value": fmt_inr(monthly_surplus_est), "sub": "Estimated from 25% model"},
        {"title": "Savings Ratio", "value": f"{savings_ratio_est:.1f}%", "sub": "Advisor benchmark view"},
        {"title": "Emergency Fund Gap", "value": fmt_inr(emergency_gap_est), "sub": "6 months vs current estimate"},
        {"title": "Insurance Gap", "value": fmt_inr(insurance_gap_est), "sub": "15x income benchmark"},
        {"title": "Retirement Readiness", "value": f"{retirement_readiness}%", "sub": "Indicative planning score"},
        {"title": "FIRE Progress", "value": f"{fire_progress}%", "sub": "Indicative wealth momentum"},
    ])

    # Dashboard charts
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">📊 Dashboard Visual Intelligence</div>', unsafe_allow_html=True)
    ch1, ch2, ch3 = st.columns(3)

    with ch1:
        st.markdown("#### 💵 Income vs Outflow Snapshot")
        cf_df = pd.DataFrame({
            "Category": ["Income", "Expenses", "EMI", "SIP", "Surplus"],
            "Amount": [
                global_monthly_income,
                global_monthly_income * 0.45,
                global_monthly_income * 0.15,
                global_monthly_income * 0.10,
                global_monthly_income * 0.30
            ]
        })
        st.bar_chart(cf_df.set_index("Category"))

    with ch2:
        st.markdown("#### 🧩 Suggested Asset Allocation")
        alloc_df = pd.DataFrame({
            "Asset": ["Equity", "Debt", "Gold"],
            "Allocation %": [eq_alloc, debt_alloc, gold_alloc]
        })
        st.bar_chart(alloc_df.set_index("Asset"))

    with ch3:
        st.markdown("#### 🎯 Goal Bucket Readiness")
        goal_df = pd.DataFrame({
            "Goal": ["Emergency", "Insurance", "Retirement", "Child", "Lifestyle"],
            "Readiness %": [55, 60, retirement_readiness, 48, 65]
        })
        st.bar_chart(goal_df.set_index("Goal"))
    st.markdown('</div>', unsafe_allow_html=True)

    # Section-wise modules
    # Wealth Planning
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">💰 Wealth Planning</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: module_card("📈 SIP Calculator", "Monthly SIP projection with growth table and chart.", "SIP Calculator", "Investment Planning", "Launch")
    with c2: module_card("💰 Lumpsum Calculator", "One-time investment future value planning.", "Lumpsum Calculator", "Investment Planning", "Launch")
    with c3: module_card("📈 Step-up SIP", "Step-up SIP projection with yearly growth path.", "Step-up SIP", "Advanced SIP", "Launch")
    with c4: module_card("💸 SWP Calculator", "Corpus withdrawal sustainability analysis.", "SWP Calculator", "Retirement Income", "Launch")
    with c5: module_card("🧩 Asset Allocation", "Age and risk based allocation suggestion.", "Asset Allocation", "Portfolio Strategy", "Launch")
    st.markdown('</div>', unsafe_allow_html=True)

    # Goal Planning
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">🎯 Goal Planning</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: module_card("🎯 Goal Planner", "Inflated goal cost + SIP / lumpsum planning.", "Goal Planner", "Goal Planning", "Launch")
    with c2: module_card("👶 Child Planner", "Education and marriage planning for child future.", "Child Planner", "Family Goals", "Launch")
    with c3: module_card("🧓 Retirement Planner", "Corpus and SIP requirement for retirement.", "Retirement Planner", "Retirement Planning", "Launch")
    with c4: module_card("🔥 FIRE Calculator", "Financial independence target and timeline.", "FIRE Calculator", "Freedom Planning", "Launch")
    st.markdown('</div>', unsafe_allow_html=True)

    # Lifestyle Planning
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">🚗 Lifestyle Planning</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: module_card("🚗 Car Planner", "Car affordability and EMI check.", "Car Planner", "Lifestyle Goal", "Launch")
    with c2: module_card("📱 Gadget Planner", "iPhone / gadget saving plan.", "Gadget Planner", "Lifestyle Goal", "Launch")
    with c3: module_card("✈️ Vacation Planner", "Travel savings planner.", "Vacation Planner", "Lifestyle Goal", "Launch")
    with c4: module_card("🏦 EMI Planner", "EMI calculator and loan eligibility.", "EMI Planner", "Liability Planning", "Launch")
    st.markdown('</div>', unsafe_allow_html=True)

    # Protection & Stability
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">🛡️ Protection & Stability</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: module_card("💵 Overall Cashflow Master", "Complete income vs outflow + financial health signal.", "Overall Cashflow Master", "Master Cashflow", "Launch")
    with c2: module_card("🛡️ Insurance Need", "Life cover and health cover guidance.", "Insurance Planner", "Protection Planning", "Launch")
    with c3: module_card("🚨 Emergency Fund", "Emergency reserve gap analysis.", "Emergency Fund", "Protection Planning", "Launch")
    with c4: module_card("📊 Net Worth", "Assets vs liabilities dashboard.", "Net Worth", "Wealth Snapshot", "Launch")
    st.markdown('</div>', unsafe_allow_html=True)

    # Advisor Desk
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">📄 Advisor Desk</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: module_card("👤 Client Profile", "Capture client details, liabilities and surplus.", "Client Profile", "Client Discovery", "Launch")
    with c2: module_card("💵 Cashflow Planner", "Simple monthly income vs expenses planner.", "Cashflow Planner", "Cashflow Planning", "Launch")
    with c3: module_card("📝 Advisor Notes", "Save professional advisor recommendations.", "Advisor Notes", "Consultation", "Launch")
    with c4: module_card("📄 Report Center", "Client summary, CSV and PDF export.", "Report Center", "Output Center", "Launch")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# CLIENT PROFILE
# ============================================================
elif page == "Client Profile":
    back_button()
    st.subheader("👤 Client Profile")

    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Client Name", value=st.session_state.client_name)
        age = st.number_input("Age", 0, 100, value=int(st.session_state.client_age), key="cp_age_v11")
        spouse_age = st.number_input("Spouse Age", 0, 100, value=max(int(st.session_state.client_age)-2, 0))
        dependents = st.number_input("No. of Dependents", 0, 10, value=2)
    with col2:
        monthly_income = st.number_input("Monthly Income (₹)", 0.0, value=float(st.session_state.client_income), step=1000.0, key="cp_income_v11")
        monthly_expense = st.number_input("Monthly Expense (₹)", 0.0, value=float(st.session_state.client_income * 0.7), step=1000.0)
        current_savings = st.number_input("Current Savings / Investments (₹)", 0.0, value=500000.0, step=10000.0)
        liabilities = st.number_input("Total Liabilities (₹)", 0.0, value=1000000.0, step=10000.0)
    with col3:
        risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"], index=["Conservative", "Moderate", "Aggressive"].index(st.session_state.client_risk), key="cp_risk_v11")
        city = st.text_input("City", value=st.session_state.client_city)
        occupation = st.text_input("Occupation", value="Salaried")
        annual_increment = st.number_input("Expected Annual Income Growth (%)", 0.0, 50.0, value=8.0)

    if st.button("💾 Save Client Profile"):
        st.session_state.client_name = name
        st.session_state.client_age = age
        st.session_state.client_income = monthly_income
        st.session_state.client_city = city
        st.session_state.client_risk = risk
        add_report("Client Profile", "Net Surplus", fmt_inr(monthly_income - monthly_expense), f"Risk: {risk}, City: {city}, Occupation: {occupation}")
        st.success("Client profile saved.")

    networth = current_savings - liabilities
    surplus = monthly_income - monthly_expense
    render_kpi_cards([
        {"title": "Monthly Surplus", "value": fmt_inr(surplus)},
        {"title": "Current Net Worth", "value": fmt_inr(networth)},
        {"title": "Dependents", "value": str(dependents)},
        {"title": "Annual Income Growth", "value": f"{annual_increment:.1f}%"},
    ])

# ============================================================
# OVERALL CASHFLOW MASTER
# ============================================================
elif page == "Overall Cashflow Master":
    back_button()
    st.subheader("💵 Overall Cashflow Master")

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 💼 Income Inputs")
    i1, i2, i3, i4 = st.columns(4)
    with i1:
        salary_income = st.number_input("Salary Income (₹/month)", 0.0, value=float(st.session_state.client_income), step=1000.0)
    with i2:
        business_income = st.number_input("Business Income (₹/month)", 0.0, value=0.0, step=1000.0)
    with i3:
        rental_income = st.number_input("Rental Income (₹/month)", 0.0, value=0.0, step=1000.0)
    with i4:
        other_income = st.number_input("Other Income (₹/month)", 0.0, value=5000.0, step=500.0)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 💸 Outflow Inputs")
    o1, o2, o3, o4, o5 = st.columns(5)
    with o1:
        fixed_exp = st.number_input("Fixed Expenses (₹/month)", 0.0, value=30000.0, step=1000.0)
    with o2:
        variable_exp = st.number_input("Variable Expenses (₹/month)", 0.0, value=15000.0, step=1000.0)
    with o3:
        emi_outflow = st.number_input("EMI Outflow (₹/month)", 0.0, value=10000.0, step=1000.0)
    with o4:
        insurance_outflow = st.number_input("Insurance Premium (₹/month)", 0.0, value=3000.0, step=500.0)
    with o5:
        sip_outflow = st.number_input("SIP / Investments (₹/month)", 0.0, value=10000.0, step=1000.0)
    st.markdown('</div>', unsafe_allow_html=True)

    total_income = salary_income + business_income + rental_income + other_income
    total_expenses = fixed_exp + variable_exp + emi_outflow + insurance_outflow + sip_outflow
    surplus = total_income - total_expenses

    savings_ratio = safe_div(max(surplus, 0) + sip_outflow, max(total_income, 1)) * 100
    emi_ratio = safe_div(emi_outflow, max(total_income, 1)) * 100
    expense_ratio = safe_div(fixed_exp + variable_exp, max(total_income, 1)) * 100
    suggested_investable_surplus = max(surplus * 0.7, 0)

    if surplus < 0:
        health_signal = "Critical"
    elif savings_ratio < 15 or emi_ratio > 40:
        health_signal = "Weak"
    elif savings_ratio < 30 or emi_ratio > 25:
        health_signal = "Moderate"
    else:
        health_signal = "Strong"

    render_kpi_cards([
        {"title": "Total Monthly Income", "value": fmt_inr(total_income)},
        {"title": "Total Monthly Outflow", "value": fmt_inr(total_expenses)},
        {"title": "Surplus / Deficit", "value": fmt_inr(surplus)},
        {"title": "Financial Health Signal", "value": health_signal},
    ])

    render_kpi_cards([
        {"title": "Savings Ratio", "value": f"{savings_ratio:.1f}%"},
        {"title": "EMI Ratio", "value": f"{emi_ratio:.1f}%"},
        {"title": "Expense Ratio", "value": f"{expense_ratio:.1f}%"},
        {"title": "Investable Surplus", "value": fmt_inr(suggested_investable_surplus)},
    ])

    cf_breakdown = pd.DataFrame({
        "Category": [
            "Salary", "Business", "Rental", "Other",
            "Fixed", "Variable", "EMI", "Insurance", "SIP"
        ],
        "Amount": [
            salary_income, business_income, rental_income, other_income,
            fixed_exp, variable_exp, emi_outflow, insurance_outflow, sip_outflow
        ]
    })

    st.dataframe(cf_breakdown, use_container_width=True)
    st.bar_chart(cf_breakdown.set_index("Category"))

    if st.button("➕ Add Overall Cashflow Master to Report"):
        add_report(
            "Overall Cashflow Master",
            "Monthly Surplus / Deficit",
            fmt_inr(surplus),
            f"Savings {savings_ratio:.1f}% | EMI {emi_ratio:.1f}% | Expense {expense_ratio:.1f}% | Health {health_signal}"
        )
        st.success("Added to report.")

# ============================================================
# SIP CALCULATOR
# ============================================================
elif page == "SIP Calculator":
    back_button()
    st.subheader("📈 SIP Calculator")

    c1, c2, c3 = st.columns(3)
    with c1:
        sip = st.number_input("Monthly SIP (₹)", min_value=0.0, value=10000.0, step=500.0)
    with c2:
        rate = st.number_input("Expected Return (% p.a.)", min_value=0.0, value=12.0, step=0.1)
    with c3:
        years = st.number_input("Investment Duration (Years)", min_value=0.0, value=15.0, step=1.0)

    fv = future_value_sip(sip, rate, years)
    invested = sip * years * 12
    gain = fv - invested

    render_kpi_cards([
        {"title": "Total Invested", "value": fmt_inr(invested)},
        {"title": "Estimated Value", "value": fmt_inr(fv)},
        {"title": "Estimated Gain", "value": fmt_inr(gain)},
        {"title": "Return Assumption", "value": f"{rate:.2f}%"},
    ])

    df = monthly_projection_table(sip, rate, years)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.line_chart(df.set_index("Year")[["Invested", "Value"]])

    if st.button("➕ Add SIP Result to Report"):
        add_report("SIP Calculator", "Future Value", fmt_inr(fv), f"SIP {fmt_inr(sip)} for {years} years @ {rate}%")
        st.success("Added to report.")

# ============================================================
# LUMPSUM CALCULATOR
# ============================================================
elif page == "Lumpsum Calculator":
    back_button()
    st.subheader("💰 Lumpsum Calculator")

    c1, c2, c3 = st.columns(3)
    with c1:
        lumpsum = st.number_input("Lumpsum Amount (₹)", 0.0, value=500000.0, step=10000.0)
    with c2:
        rate = st.number_input("Expected Return (% p.a.)", 0.0, value=12.0, step=0.1)
    with c3:
        years = st.number_input("Duration (Years)", 0.0, value=10.0, step=1.0)

    fv = future_value_lumpsum(lumpsum, rate, years)
    gain = fv - lumpsum

    render_kpi_cards([
        {"title": "Initial Investment", "value": fmt_inr(lumpsum)},
        {"title": "Future Value", "value": fmt_inr(fv)},
        {"title": "Estimated Gain", "value": fmt_inr(gain)},
        {"title": "Return Assumption", "value": f"{rate:.2f}%"},
    ])

    rows = [{"Year": y, "Portfolio Value": round(future_value_lumpsum(lumpsum, rate, y), 2)} for y in range(1, int(years) + 1)]
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.line_chart(df.set_index("Year"))

    if st.button("➕ Add Lumpsum Result to Report"):
        add_report("Lumpsum Calculator", "Future Value", fmt_inr(fv), f"Lumpsum {fmt_inr(lumpsum)} for {years} years @ {rate}%")
        st.success("Added to report.")

# ============================================================
# SWP CALCULATOR
# ============================================================
elif page == "SWP Calculator":
    back_button()
    st.subheader("💸 SWP Calculator")

    c1, c2, c3 = st.columns(3)
    with c1:
        corpus = st.number_input("Current Corpus (₹)", 0.0, value=10000000.0, step=100000.0)
    with c2:
        withdrawal = st.number_input("Monthly Withdrawal (₹)", 0.0, value=50000.0, step=1000.0)
    with c3:
        rate = st.number_input("Expected Return (% p.a.)", 0.0, value=8.0, step=0.1)

    months = swp_duration(corpus, withdrawal, rate)
    years = months / 12 if months != float("inf") else float("inf")

    render_kpi_cards([
        {"title": "Corpus", "value": fmt_inr(corpus)},
        {"title": "Monthly SWP", "value": fmt_inr(withdrawal)},
        {"title": "Duration", "value": "Sustainable" if years == float("inf") else f"{years:.2f} Years"},
        {"title": "Return", "value": f"{rate:.2f}%"},
    ])

    r = annual_to_monthly(rate)
    balance = corpus
    rows = []
    for m in range(1, 601):
        balance = balance * (1 + r) - withdrawal
        if balance <= 0:
            rows.append({"Month": m, "Balance": 0})
            break
        if m % 12 == 0:
            rows.append({"Year": m // 12, "Balance": round(balance, 2)})

    sim_df = pd.DataFrame(rows)
    if not sim_df.empty:
        st.dataframe(sim_df, use_container_width=True)
        if "Year" in sim_df.columns:
            st.line_chart(sim_df.set_index("Year"))

    if st.button("➕ Add SWP Result to Report"):
        add_report("SWP Calculator", "SWP Sustainability", "Sustainable" if years == float("inf") else f"{years:.2f} Years", f"Corpus {fmt_inr(corpus)}, SWP {fmt_inr(withdrawal)}")
        st.success("Added to report.")

# ============================================================
# GOAL PLANNER
# ============================================================
elif page == "Goal Planner":
    back_button()
    st.subheader("🎯 Goal Planner")

    tabs = st.tabs(["Future Goal Cost", "Required SIP", "Required Lumpsum"])

    with tabs[0]:
        c1, c2, c3 = st.columns(3)
        with c1:
            current_cost = st.number_input("Current Goal Cost (₹)", 0.0, value=2000000.0, step=10000.0)
        with c2:
            inflation = st.number_input("Inflation (%)", 0.0, value=7.0, step=0.1)
        with c3:
            years = st.number_input("Years to Goal", 0.0, value=10.0, step=1.0)

        future_cost = inflated_goal(current_cost, inflation, years)
        render_kpi_cards([
            {"title": "Current Cost", "value": fmt_inr(current_cost)},
            {"title": "Future Cost", "value": fmt_inr(future_cost)},
            {"title": "Inflation", "value": f"{inflation:.2f}%"},
            {"title": "Time Horizon", "value": f"{years:.0f} Years"},
        ])

    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            exp_return = st.number_input("Expected Return (% p.a.)", 0.0, value=12.0, step=0.1)
        with c2:
            target = st.number_input("Target Amount (₹)", 0.0, value=float(future_cost), step=10000.0)
        sip_req = required_sip_for_goal(target, exp_return, years)
        st.metric("Required Monthly SIP", fmt_inr(sip_req))
        if st.button("➕ Add Goal SIP to Report"):
            add_report("Goal Planner", "Required SIP", fmt_inr(sip_req), f"Target {fmt_inr(target)} in {years} years @ {exp_return}%")
            st.success("Added to report.")

    with tabs[2]:
        req_lumpsum = target / ((1 + exp_return / 100) ** years) if years > 0 else target
        st.metric("Required Lumpsum Today", fmt_inr(req_lumpsum))
        if st.button("➕ Add Goal Lumpsum to Report"):
            add_report("Goal Planner", "Required Lumpsum", fmt_inr(req_lumpsum), f"Target {fmt_inr(target)} in {years} years")
            st.success("Added to report.")

# ============================================================
# RETIREMENT PLANNER
# ============================================================
elif page == "Retirement Planner":
    back_button()
    st.subheader("🧓 Retirement Planner")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        current_age = st.number_input("Current Age", 18, 100, value=max(st.session_state.client_age, 18))
    with c2:
        retirement_age = st.number_input("Retirement Age", 30, 100, value=60)
    with c3:
        monthly_expense = st.number_input("Monthly Expense Today (₹)", 0.0, value=50000.0, step=1000.0)
    with c4:
        inflation = st.number_input("Inflation (%)", 0.0, value=6.0, step=0.1)

    c5, c6, c7 = st.columns(3)
    with c5:
        post_ret_return = st.number_input("Post-Ret Return (%)", 0.0, value=7.0, step=0.1)
    with c6:
        pre_ret_return = st.number_input("Pre-Ret Return (%)", 0.0, value=12.0, step=0.1)
    with c7:
        years_in_ret = st.number_input("Years in Retirement", 1, 50, value=25)

    years_to_ret = max(retirement_age - current_age, 0)
    corpus, expense_at_ret = retirement_corpus_needed(monthly_expense, inflation, post_ret_return, years_to_ret, years_in_ret)
    req_sip = required_sip_for_goal(corpus, pre_ret_return, years_to_ret) if years_to_ret > 0 else corpus

    render_kpi_cards([
        {"title": "Years to Retirement", "value": f"{years_to_ret}"},
        {"title": "Expense at Retirement", "value": fmt_inr(expense_at_ret)},
        {"title": "Required Corpus", "value": fmt_inr(corpus)},
        {"title": "Required SIP", "value": fmt_inr(req_sip)},
    ])

    if st.button("➕ Add Retirement Plan to Report"):
        add_report("Retirement Planner", "Required Corpus", fmt_inr(corpus), f"Retire at {retirement_age}, SIP {fmt_inr(req_sip)}")
        st.success("Added to report.")

# ============================================================
# CHILD PLANNER
# ============================================================
elif page == "Child Planner":
    back_button()
    st.subheader("👶 Child Education / Marriage Planner")

    goal_type = st.selectbox("Select Goal Type", ["Child Education", "Child Marriage"])
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        child_age = st.number_input("Child Current Age", 0, 30, value=5)
    with c2:
        goal_age = st.number_input("Goal Age", 1, 40, value=18 if goal_type == "Child Education" else 25)
    with c3:
        current_cost = st.number_input("Current Estimated Cost (₹)", 0.0, value=2500000.0 if goal_type == "Child Education" else 1500000.0, step=10000.0)
    with c4:
        inflation = st.number_input("Education/Marriage Inflation (%)", 0.0, value=8.0, step=0.1)

    exp_return = st.number_input("Expected Return (% p.a.)", 0.0, value=12.0, step=0.1)
    years = max(goal_age - child_age, 0)
    future_cost = inflated_goal(current_cost, inflation, years)
    req_sip = required_sip_for_goal(future_cost, exp_return, years) if years > 0 else future_cost

    render_kpi_cards([
        {"title": "Years Remaining", "value": str(years)},
        {"title": "Future Goal Cost", "value": fmt_inr(future_cost)},
        {"title": "Required SIP", "value": fmt_inr(req_sip)},
        {"title": "Goal Type", "value": goal_type},
    ])

    if st.button("➕ Add Child Goal to Report"):
        add_report("Child Planner", f"{goal_type} Required SIP", fmt_inr(req_sip), f"Future Cost {fmt_inr(future_cost)} in {years} years")
        st.success("Added to report.")

# ============================================================
# EMI PLANNER
# ============================================================
elif page == "EMI Planner":
    back_button()
    st.subheader("🏦 EMI / Loan Planner")

    tabs = st.tabs(["EMI Calculator", "Loan Eligibility"])

    with tabs[0]:
        c1, c2, c3 = st.columns(3)
        with c1:
            principal = st.number_input("Loan Amount (₹)", 0.0, value=3000000.0, step=10000.0)
        with c2:
            rate = st.number_input("Interest Rate (% p.a.)", 0.0, value=9.0, step=0.1)
        with c3:
            years = st.number_input("Tenure (Years)", 0.0, value=20.0, step=1.0)

        emi_val = emi(principal, rate, years)
        total_payment = emi_val * years * 12
        interest = total_payment - principal

        render_kpi_cards([
            {"title": "Monthly EMI", "value": fmt_inr(emi_val)},
            {"title": "Total Payment", "value": fmt_inr(total_payment)},
            {"title": "Total Interest", "value": fmt_inr(interest)},
            {"title": "Tenure", "value": f"{years:.0f} Years"},
        ])

        if st.button("➕ Add EMI Result to Report"):
            add_report("EMI Planner", "Monthly EMI", fmt_inr(emi_val), f"Loan {fmt_inr(principal)} @ {rate}% for {years} years")
            st.success("Added to report.")

    with tabs[1]:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            income = st.number_input("
