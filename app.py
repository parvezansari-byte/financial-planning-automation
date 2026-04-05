# app.py
# FINAL Freedom ULTRA PRO V8 (FULL PROFESSIONAL MFD VERSION)
# Single-file Streamlit app | GitHub / Streamlit Cloud ready

import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime
from io import BytesIO

# Optional PDF support
PDF_AVAILABLE = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    )
except Exception:
    PDF_AVAILABLE = False

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Freedom ULTRA PRO V8",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# PREMIUM DARK CSS
# -------------------------------
st.markdown("""
<style>
:root {
    --bg: #0b1020;
    --card: #131a2a;
    --card2: #182235;
    --text: #f8fafc;
    --muted: #94a3b8;
    --accent: #22c55e;
    --accent2: #3b82f6;
    --danger: #ef4444;
    --warning: #f59e0b;
    --border: rgba(255,255,255,0.08);
}
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0b1020 0%, #0f172a 35%, #111827 100%);
    color: var(--text);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}
.premium-header {
    background: linear-gradient(90deg, rgba(34,197,94,0.15), rgba(59,130,246,0.15));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 22px 24px;
    margin-bottom: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}
.brand-title {
    font-size: 34px;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 6px;
}
.brand-sub {
    font-size: 14px;
    color: #cbd5e1;
}
.kpi-card {
    background: linear-gradient(180deg, rgba(19,26,42,0.95), rgba(24,34,53,0.95));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.18);
}
.kpi-title {
    font-size: 13px;
    color: #94a3b8;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 24px;
    font-weight: 800;
    color: #f8fafc;
}
.section-card {
    background: linear-gradient(180deg, rgba(19,26,42,0.92), rgba(24,34,53,0.92));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.15);
}
.small-note {
    color: #94a3b8;
    font-size: 12px;
}
hr {
    border-color: rgba(255,255,255,0.08);
}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 10px;
    border-radius: 14px;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 8px 14px;
}
.stTabs [aria-selected="true"] {
    background: rgba(34,197,94,0.18) !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SESSION STATE
# -------------------------------
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

# -------------------------------
# HELPERS
# -------------------------------
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

def monthly_to_annual(rate_monthly):
    return rate_monthly * 12 * 100

def future_value_lumpsum(pv, annual_rate, years):
    r = annual_rate / 100
    return pv * ((1 + r) ** years)

def future_value_sip(monthly_investment, annual_rate, years):
    r = annual_to_monthly(annual_rate)
    n = int(years * 12)
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
        if r == 0:
            total += sip_for_year * min(12, months_remaining)
        else:
            months_this_year = min(12, months_remaining)
            fv_year = sip_for_year * (((1 + r) ** months_this_year - 1) / r) * (1 + r)
            growth_after = max(months_remaining - months_this_year, 0)
            fv_year *= ((1 + r) ** growth_after)
            total += fv_year
    return total

def present_value_of_goal(goal_future, inflation, years):
    return goal_future / ((1 + inflation / 100) ** years)

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
    taxable = max(annual_income - 50000, 0)  # std deduction rough
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
    cess = tax * 0.04
    return tax + cess

def basic_tax_new_regime(annual_income):
    taxable = max(annual_income - 75000, 0)  # rough std deduction
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
        tax = 0  # simplified rebate logic
    cess = tax * 0.04
    return tax + cess

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
    title_style = ParagraphStyle(
        'TitleX',
        parent=styles['Title'],
        textColor=colors.HexColor("#0f172a"),
        fontSize=20,
        leading=24
    )
    normal = styles["BodyText"]
    story = []

    story.append(Paragraph("Freedom ULTRA PRO V8 - Client Financial Planning Report", title_style))
    story.append(Spacer(1, 12))

    client_lines = [
        f"Client Name: {client_info.get('name', '')}",
        f"Age: {client_info.get('age', '')}",
        f"Monthly Income: {client_info.get('income', '')}",
        f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    ]
    for line in client_lines:
        story.append(Paragraph(line, normal))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Advisor Notes", styles["Heading2"]))
    story.append(Paragraph(advisor_notes if advisor_notes else "No advisor notes added.", normal))
    story.append(Spacer(1, 12))

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
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{card['title']}</div>
                <div class="kpi-value">{card['value']}</div>
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

        # grow existing corpus for the year
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

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div class="premium-header">
    <div class="brand-title">💼 Freedom ULTRA PRO V8</div>
    <div class="brand-sub">FULL PROFESSIONAL MFD VERSION • Premium Financial Planning Super App • Single-File Streamlit Edition</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    st.markdown("## 🚀 Navigation")
    module = st.radio(
        "Choose Module",
        [
            "🏠 Dashboard",
            "👤 Client Profile",
            "📈 SIP Calculator",
            "💰 Lumpsum Calculator",
            "💸 SWP Calculator",
            "🎯 Goal Planner",
            "🧓 Retirement Planner",
            "👶 Child Education / Marriage Planner",
            "🏦 EMI / Loan Planner",
            "🚗 Car Purchase Planner",
            "📱 iPhone / Gadget Purchase Planner",
            "✈️ Vacation / Travel Planner",
            "🛡️ Insurance Need Calculator",
            "🚨 Emergency Fund Planner",
            "📊 Net Worth Dashboard",
            "💵 Cashflow Planner",
            "🔥 FIRE / Financial Freedom Calculator",
            "📉 Inflation Impact Calculator",
            "📈 Step-up SIP Planner",
            "🧩 Asset Allocation Suggestion",
            "🧾 Tax Saving Projection",
            "📝 Advisor Notes",
            "📄 Client Summary Dashboard / Report"
        ]
    )

    st.markdown("---")
    st.markdown("### Client Quick Inputs")
    st.session_state.client_name = st.text_input("Client Name", value=st.session_state.client_name)
    st.session_state.client_age = st.number_input("Client Age", min_value=0, max_value=100, value=int(st.session_state.client_age))
    st.session_state.client_income = st.number_input("Monthly Income (₹)", min_value=0.0, value=float(st.session_state.client_income), step=1000.0)

    st.markdown("---")
    if st.button("🧹 Clear Report Summary"):
        st.session_state.report_rows = []
        st.success("Report summary cleared.")

# -------------------------------
# GLOBAL KPI STRIP
# -------------------------------
global_monthly_income = st.session_state.client_income
estimated_savings = global_monthly_income * 0.25
estimated_expense = global_monthly_income - estimated_savings
render_kpi_cards([
    {"title": "Client", "value": st.session_state.client_name or "Not Set"},
    {"title": "Age", "value": str(st.session_state.client_age)},
    {"title": "Monthly Income", "value": fmt_inr(global_monthly_income)},
    {"title": "Suggested Savings", "value": fmt_inr(estimated_savings)},
])

st.markdown("")

# -------------------------------
# MODULES
# -------------------------------

if module == "🏠 Dashboard":
    st.subheader("🏠 Freedom ULTRA PRO V8 - Executive Dashboard")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 📌 Planning Snapshot")
        st.write(f"**Client:** {st.session_state.client_name or 'Not Set'}")
        st.write(f"**Age:** {st.session_state.client_age}")
        st.write(f"**Monthly Income:** {fmt_inr(st.session_state.client_income)}")
        st.write(f"**Suggested Monthly Savings (25%):** {fmt_inr(st.session_state.client_income * 0.25)}")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Financial Health Score")
        savings_ratio = safe_div(estimated_savings, max(global_monthly_income, 1)) * 100
        score = min(100, round(40 + savings_ratio * 1.8))
        st.metric("Health Score", f"{score}/100")
        st.progress(score / 100)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🗂 Report Summary")
        df = report_df()
        st.metric("Saved Report Items", len(df))
        st.metric("PDF Ready", "Yes" if PDF_AVAILABLE else "No (Install reportlab)")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Quick Allocation Suggestion")
    eq, debt, gold = asset_allocation(st.session_state.client_age, "Moderate")
    alloc_df = pd.DataFrame({
        "Asset Class": ["Equity", "Debt", "Gold"],
        "Allocation %": [eq, debt, gold]
    })
    st.dataframe(alloc_df, use_container_width=True)
    st.bar_chart(alloc_df.set_index("Asset Class"))
    st.markdown('</div>', unsafe_allow_html=True)

elif module == "👤 Client Profile":
    st.subheader("👤 Client Profile Section")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Client Name", value=st.session_state.client_name)
        age = st.number_input("Age", 0, 100, value=int(st.session_state.client_age))
        spouse_age = st.number_input("Spouse Age", 0, 100, value=max(int(st.session_state.client_age)-2, 0))
        dependents = st.number_input("No. of Dependents", 0, 10, value=2)
    with col2:
        monthly_income = st.number_input("Monthly Income (₹)", 0.0, value=float(st.session_state.client_income), step=1000.0)
        monthly_expense = st.number_input("Monthly Expense (₹)", 0.0, value=float(st.session_state.client_income * 0.7), step=1000.0)
        current_savings = st.number_input("Current Savings / Investments (₹)", 0.0, value=500000.0, step=10000.0)
        liabilities = st.number_input("Total Liabilities (₹)", 0.0, value=1000000.0, step=10000.0)
    with col3:
        risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"], index=1)
        city = st.text_input("City", value="Bengaluru")
        occupation = st.text_input("Occupation", value="Salaried")
        annual_increment = st.number_input("Expected Annual Income Growth (%)", 0.0, 50.0, value=8.0)

    if st.button("💾 Save Client Profile"):
        st.session_state.client_name = name
        st.session_state.client_age = age
        st.session_state.client_income = monthly_income
        add_report("Client Profile", "Net Surplus", fmt_inr(monthly_income - monthly_expense), f"Risk: {risk}, City: {city}")
        st.success("Client profile saved to dashboard/report summary.")

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    networth = current_savings - liabilities
    surplus = monthly_income - monthly_expense
    render_kpi_cards([
        {"title": "Monthly Surplus", "value": fmt_inr(surplus)},
        {"title": "Current Net Worth", "value": fmt_inr(networth)},
        {"title": "Dependents", "value": str(dependents)},
        {"title": "Risk Profile", "value": risk},
    ])
    st.markdown('</div>', unsafe_allow_html=True)

elif module == "📈 SIP Calculator":
    st.subheader("📈 SIP Calculator")
    col1, col2, col3 = st.columns(3)
    with col1:
        sip = st.number_input("Monthly SIP (₹)", min_value=0.0, value=10000.0, step=500.0)
    with col2:
        rate = st.number_input("Expected Return (% p.a.)", min_value=0.0, value=12.0, step=0.1)
    with col3:
        years = st.number_input("Investment Duration (Years)", min_value=0.0, value=15.0, step=1.0)

    fv = future_value_sip(sip, rate, years)
    invested = sip * years * 12
    gain = fv - invested

    render_kpi_cards([
        {"title": "Total Invested", "value": fmt_inr(invested)},
        {"title": "Estimated Value", "value": fmt_inr(fv)},
        {"title": "Estimated Gain", "value": fmt_inr(gain)},
        {"title": "XIRR Proxy", "value": f"{rate:.2f}%"},
    ])

    df = monthly_projection_table(sip, rate, years)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.line_chart(df.set_index("Year")[["Invested", "Value"]])

    if st.button("➕ Add SIP Result to Report"):
        add_report("SIP Calculator", "Future Value", fmt_inr(fv), f"SIP {fmt_inr(sip)} for {years} years @ {rate}%")
        st.success("Added to report.")

elif module == "💰 Lumpsum Calculator":
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

    rows = []
    for y in range(1, int(years) + 1):
        val = future_value_lumpsum(lumpsum, rate, y)
        rows.append({"Year": y, "Portfolio Value": round(val, 2)})
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.line_chart(df.set_index("Year"))

    if st.button("➕ Add Lumpsum Result to Report"):
        add_report("Lumpsum Calculator", "Future Value", fmt_inr(fv), f"Lumpsum {fmt_inr(lumpsum)} for {years} years @ {rate}%")
        st.success("Added to report.")

elif module == "💸 SWP Calculator":
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
        {"title": "Return Assumption", "value": f"{rate:.2f}%"},
    ])

    # Simulation
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

elif module == "🎯 Goal Planner":
    st.subheader("🎯 Goal Planner")
    tabs = st.tabs(["Future Goal Cost", "Required SIP", "Required Lumpsum"])
    with tabs[0]:
        c1, c2, c3 = st.columns(3)
        with c1:
            current_cost = st.number_input("Current Goal Cost (₹)", 0.0, value=2000000.0, step=10000.0, key="goal_current")
        with c2:
            inflation = st.number_input("Inflation (%)", 0.0, value=7.0, step=0.1, key="goal_inf")
        with c3:
            years = st.number_input("Years to Goal", 0.0, value=10.0, step=1.0, key="goal_years")
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
            exp_return = st.number_input("Expected Return (% p.a.)", 0.0, value=12.0, step=0.1, key="goal_ret")
        with c2:
            target = st.number_input("Target Amount (₹)", 0.0, value=float(future_cost), step=10000.0, key="goal_target")
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

elif module == "🧓 Retirement Planner":
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

elif module == "👶 Child Education / Marriage Planner":
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

elif module == "🏦 EMI / Loan Planner":
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
            income = st.number_input("Monthly Income (₹)", 0.0, value=float(st.session_state.client_income), step=1000.0, key="elig_income")
        with c2:
            foir = st.number_input("FOIR (%)", 10.0, 90.0, value=50.0, step=1.0)
        with c3:
            existing_emi = st.number_input("Existing EMI (₹)", 0.0, value=10000.0, step=1000.0)
        with c4:
            rate2 = st.number_input("Interest Rate (% p.a.)", 0.0, value=9.0, step=0.1, key="elig_rate")
        years2 = st.number_input("Tenure (Years)", 1.0, 40.0, value=20.0, step=1.0, key="elig_years")
        eligible_loan, max_emi = loan_eligibility(income, foir, existing_emi, rate2, years2)
        render_kpi_cards([
            {"title": "Max EMI Capacity", "value": fmt_inr(max_emi)},
            {"title": "Estimated Eligible Loan", "value": fmt_inr(eligible_loan)},
            {"title": "FOIR", "value": f"{foir:.0f}%"},
            {"title": "Net EMI Headroom", "value": fmt_inr(max_emi)},
        ])

elif module == "🚗 Car Purchase Planner":
    st.subheader("🚗 Car Purchase Planner")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        car_cost = st.number_input("Car Cost (₹)", 0.0, value=1200000.0, step=10000.0)
    with c2:
        down_pct = st.number_input("Down Payment (%)", 0.0, 100.0, value=20.0, step=1.0)
    with c3:
        loan_rate = st.number_input("Car Loan Rate (% p.a.)", 0.0, value=9.0, step=0.1)
    with c4:
        tenure = st.number_input("Loan Tenure (Years)", 1.0, 10.0, value=5.0, step=1.0)

    down_amt = car_cost * down_pct / 100
    loan_amt = car_cost - down_amt
    emi_val = emi(loan_amt, loan_rate, tenure)

    render_kpi_cards([
        {"title": "Down Payment", "value": fmt_inr(down_amt)},
        {"title": "Loan Amount", "value": fmt_inr(loan_amt)},
        {"title": "Monthly EMI", "value": fmt_inr(emi_val)},
        {"title": "Affordable? (30% Rule)", "value": "Yes" if emi_val <= st.session_state.client_income * 0.3 else "Stretch"},
    ])

    if st.button("➕ Add Car Plan to Report"):
        add_report("Car Planner", "Car EMI", fmt_inr(emi_val), f"Car {fmt_inr(car_cost)} with {down_pct}% down")
        st.success("Added to report.")

elif module == "📱 iPhone / Gadget Purchase Planner":
    st.subheader("📱 iPhone / Gadget Purchase Planner")
    c1, c2, c3 = st.columns(3)
    with c1:
        gadget_cost = st.number_input("Gadget Cost (₹)", 0.0, value=100000.0, step=1000.0)
    with c2:
        months = st.number_input("Target Purchase In (Months)", 1, 60, value=12)
    with c3:
        return_rate = st.number_input("Parking Return (% p.a.)", 0.0, value=6.0, step=0.1)

    years = months / 12
    req_sip = required_sip_for_goal(gadget_cost, return_rate, years)
    render_kpi_cards([
        {"title": "Target Cost", "value": fmt_inr(gadget_cost)},
        {"title": "Timeline", "value": f"{months} Months"},
        {"title": "Required Monthly Saving", "value": fmt_inr(req_sip)},
        {"title": "Advice", "value": "Cash > EMI" if req_sip <= st.session_state.client_income * 0.1 else "Delay / Upgrade Later"},
    ])

    if st.button("➕ Add Gadget Plan to Report"):
        add_report("Gadget Planner", "Required Monthly Saving", fmt_inr(req_sip), f"Gadget {fmt_inr(gadget_cost)} in {months} months")
        st.success("Added to report.")

elif module == "✈️ Vacation / Travel Planner":
    st.subheader("✈️ Vacation / Travel Planner")
    c1, c2, c3 = st.columns(3)
    with c1:
        trip_cost = st.number_input("Current Trip Cost (₹)", 0.0, value=300000.0, step=5000.0)
    with c2:
        months = st.number_input("Trip After (Months)", 1, 60, value=18)
    with c3:
        travel_infl = st.number_input("Travel Inflation (%)", 0.0, value=7.0, step=0.1)

    years = months / 12
    future_cost = inflated_goal(trip_cost, travel_infl, years)
    req_sip = required_sip_for_goal(future_cost, 6.0, years)

    render_kpi_cards([
        {"title": "Future Trip Cost", "value": fmt_inr(future_cost)},
        {"title": "Monthly Saving Needed", "value": fmt_inr(req_sip)},
        {"title": "Timeline", "value": f"{months} Months"},
        {"title": "Best Bucket", "value": "RD / Liquid / Ultra Short"},
    ])

    if st.button("➕ Add Vacation Plan to Report"):
        add_report("Vacation Planner", "Monthly Saving Needed", fmt_inr(req_sip), f"Trip target {fmt_inr(future_cost)}")
        st.success("Added to report.")

elif module == "🛡️ Insurance Need Calculator":
    st.subheader("🛡️ Insurance Need Calculator")
    tabs = st.tabs(["Life Insurance", "Health Insurance"])
    with tabs[0]:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            annual_income = st.number_input("Annual Income (₹)", 0.0, value=float(st.session_state.client_income * 12), step=10000.0)
        with c2:
            years_to_work = st.number_input("Years to Retirement", 1, 50, value=max(60 - st.session_state.client_age, 1))
        with c3:
            personal_expense = st.number_input("Personal Expense Ratio (%)", 0.0, 100.0, value=30.0)
        with c4:
            liabilities = st.number_input("Outstanding Liabilities (₹)", 0.0, value=2000000.0, step=10000.0)

        hlv = insurance_human_life_value(annual_income, years_to_work, personal_expense)
        final_cover = hlv + liabilities

        render_kpi_cards([
            {"title": "HLV Cover", "value": fmt_inr(hlv)},
            {"title": "Liability Add-on", "value": fmt_inr(liabilities)},
            {"title": "Suggested Term Cover", "value": fmt_inr(final_cover)},
            {"title": "Rule Check", "value": "Adequate if ≥ 15x Income"},
        ])

        if st.button("➕ Add Life Cover to Report"):
            add_report("Insurance Planner", "Suggested Term Cover", fmt_inr(final_cover), f"HLV {fmt_inr(hlv)} + Liabilities")
            st.success("Added to report.")

    with tabs[1]:
        family_members = st.number_input("Family Members Covered", 1, 10, value=4)
        city_tier = st.selectbox("City Category", ["Tier 1", "Tier 2", "Tier 3"])
        base_cover = 1000000 if city_tier == "Tier 1" else 700000 if city_tier == "Tier 2" else 500000
        suggested_cover = base_cover + max((family_members - 2), 0) * 250000
        st.metric("Suggested Family Floater Health Cover", fmt_inr(suggested_cover))

elif module == "🚨 Emergency Fund Planner":
    st.subheader("🚨 Emergency Fund Planner")
    c1, c2, c3 = st.columns(3)
    with c1:
        monthly_exp = st.number_input("Monthly Household Expense (₹)", 0.0, value=50000.0, step=1000.0)
    with c2:
        months = st.slider("Emergency Fund Months", 3, 24, 6)
    with c3:
        current_emergency = st.number_input("Current Emergency Fund (₹)", 0.0, value=100000.0, step=5000.0)

    req = emergency_fund(monthly_exp, months)
    gap = max(req - current_emergency, 0)

    render_kpi_cards([
        {"title": "Required Emergency Fund", "value": fmt_inr(req)},
        {"title": "Current Available", "value": fmt_inr(current_emergency)},
        {"title": "Gap", "value": fmt_inr(gap)},
        {"title": "Suggested Bucket", "value": "Savings + Liquid Fund"},
    ])

    if st.button("➕ Add Emergency Fund to Report"):
        add_report("Emergency Fund", "Required Fund", fmt_inr(req), f"Gap {fmt_inr(gap)}")
        st.success("Added to report.")

elif module == "📊 Net Worth Dashboard":
    st.subheader("📊 Net Worth Dashboard")
    st.write("Enter assets and liabilities for a quick net worth snapshot.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Assets")
        cash = st.number_input("Cash / Bank (₹)", 0.0, value=200000.0, step=5000.0)
        mf = st.number_input("Mutual Funds (₹)", 0.0, value=800000.0, step=10000.0)
        stocks = st.number_input("Stocks (₹)", 0.0, value=300000.0, step=10000.0)
        epf = st.number_input("EPF / PPF / NPS (₹)", 0.0, value=600000.0, step=10000.0)
        gold = st.number_input("Gold (₹)", 0.0, value=250000.0, step=5000.0)
        real_estate = st.number_input("Real Estate (₹)", 0.0, value=5000000.0, step=100000.0)

    with c2:
        st.markdown("### Liabilities")
        home_loan = st.number_input("Home Loan Outstanding (₹)", 0.0, value=2500000.0, step=10000.0)
        car_loan = st.number_input("Car Loan Outstanding (₹)", 0.0, value=300000.0, step=10000.0)
        personal_loan = st.number_input("Personal Loan (₹)", 0.0, value=100000.0, step=5000.0)
        credit_card = st.number_input("Credit Card Outstanding (₹)", 0.0, value=25000.0, step=1000.0)

    total_assets = cash + mf + stocks + epf + gold + real_estate
    total_liab = home_loan + car_loan + personal_loan + credit_card
    networth = total_assets - total_liab

    render_kpi_cards([
        {"title": "Total Assets", "value": fmt_inr(total_assets)},
        {"title": "Total Liabilities", "value": fmt_inr(total_liab)},
        {"title": "Net Worth", "value": fmt_inr(networth)},
        {"title": "Debt Ratio", "value": f"{safe_div(total_liab, max(total_assets,1))*100:.1f}%"},
    ])

    asset_df = pd.DataFrame({
        "Asset": ["Cash", "Mutual Funds", "Stocks", "EPF/PPF/NPS", "Gold", "Real Estate"],
        "Value": [cash, mf, stocks, epf, gold, real_estate]
    })
    st.bar_chart(asset_df.set_index("Asset"))

    if st.button("➕ Add Net Worth to Report"):
        add_report("Net Worth", "Current Net Worth", fmt_inr(networth), f"Assets {fmt_inr(total_assets)}, Liabilities {fmt_inr(total_liab)}")
        st.success("Added to report.")

elif module == "💵 Cashflow Planner":
    st.subheader("💵 Cashflow Planner")
    c1, c2 = st.columns(2)
    with c1:
        income_salary = st.number_input("Salary Income (₹/month)", 0.0, value=float(st.session_state.client_income), step=1000.0)
        income_other = st.number_input("Other Income (₹/month)", 0.0, value=5000.0, step=500.0)
    with c2:
        fixed_exp = st.number_input("Fixed Expenses (₹/month)", 0.0, value=30000.0, step=1000.0)
        variable_exp = st.number_input("Variable Expenses (₹/month)", 0.0, value=15000.0, step=1000.0)
        emis = st.number_input("Total EMIs (₹/month)", 0.0, value=10000.0, step=1000.0)
        investments = st.number_input("Current Investments (₹/month)", 0.0, value=10000.0, step=1000.0)

    total_income = income_salary + income_other
    total_outflow = fixed_exp + variable_exp + emis + investments
    surplus = total_income - total_outflow
    savings_rate = safe_div(investments + max(surplus, 0), max(total_income, 1)) * 100

    render_kpi_cards([
        {"title": "Total Income", "value": fmt_inr(total_income)},
        {"title": "Total Outflow", "value": fmt_inr(total_outflow)},
        {"title": "Monthly Surplus", "value": fmt_inr(surplus)},
        {"title": "Savings Rate", "value": f"{savings_rate:.1f}%"},
    ])

    cf_df = pd.DataFrame({
        "Category": ["Income", "Expenses+EMI+Investments"],
        "Amount": [total_income, total_outflow]
    })
    st.bar_chart(cf_df.set_index("Category"))

    if st.button("➕ Add Cashflow to Report"):
        add_report("Cashflow Planner", "Monthly Surplus", fmt_inr(surplus), f"Savings Rate {savings_rate:.1f}%")
        st.success("Added to report.")

elif module == "🔥 FIRE / Financial Freedom Calculator":
    st.subheader("🔥 FIRE / Financial Freedom Calculator")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        annual_expense = st.number_input("Annual Expense (₹)", 0.0, value=600000.0, step=10000.0)
    with c2:
        swr = st.number_input("Safe Withdrawal Rate (%)", 1.0, 10.0, value=4.0, step=0.1)
    with c3:
        current_corpus = st.number_input("Current Invested Corpus (₹)", 0.0, value=3000000.0, step=10000.0)
    with c4:
        annual_contribution = st.number_input("Annual Contribution (₹)", 0.0, value=300000.0, step=10000.0)

    return_rate = st.number_input("Expected Portfolio Return (% p.a.)", 0.0, value=11.0, step=0.1)

    fire_number = annual_expense / (swr / 100)
    years = 0
    corpus = current_corpus
    rows = []
    while corpus < fire_number and years < 100:
        years += 1
        corpus = corpus * (1 + return_rate / 100) + annual_contribution
        rows.append({"Year": years, "Corpus": round(corpus, 2)})

    render_kpi_cards([
        {"title": "FIRE Number", "value": fmt_inr(fire_number)},
        {"title": "Current Corpus", "value": fmt_inr(current_corpus)},
        {"title": "Gap", "value": fmt_inr(max(fire_number - current_corpus, 0))},
        {"title": "Years to FIRE", "value": f"{years}" if corpus >= fire_number else "100+"},
    ])

    df = pd.DataFrame(rows)
    if not df.empty:
        st.line_chart(df.set_index("Year"))

    if st.button("➕ Add FIRE Result to Report"):
        add_report("FIRE Calculator", "FIRE Number", fmt_inr(fire_number), f"Years to FIRE {years}")
        st.success("Added to report.")

elif module == "📉 Inflation Impact Calculator":
    st.subheader("📉 Inflation Impact Calculator")
    c1, c2, c3 = st.columns(3)
    with c1:
        current_amount = st.number_input("Current Cost / Expense (₹)", 0.0, value=100000.0, step=1000.0)
    with c2:
        inflation = st.number_input("Inflation (%)", 0.0, value=6.0, step=0.1)
    with c3:
        years = st.number_input("Years", 0.0, value=10.0, step=1.0)

    future_amount = inflated_goal(current_amount, inflation, years)
    purchasing_power_loss = future_amount - current_amount

    render_kpi_cards([
        {"title": "Current Amount", "value": fmt_inr(current_amount)},
        {"title": "Future Equivalent", "value": fmt_inr(future_amount)},
        {"title": "Increase Due to Inflation", "value": fmt_inr(purchasing_power_loss)},
        {"title": "Inflation", "value": f"{inflation:.2f}%"},
    ])

    rows = []
    for y in range(1, int(years) + 1):
        rows.append({"Year": y, "Future Cost": round(inflated_goal(current_amount, inflation, y), 2)})
    df = pd.DataFrame(rows)
    if not df.empty:
        st.line_chart(df.set_index("Year"))

    if st.button("➕ Add Inflation Result to Report"):
        add_report("Inflation Calculator", "Future Cost", fmt_inr(future_amount), f"{current_amount} growing @ {inflation}%")
        st.success("Added to report.")

elif module == "📈 Step-up SIP Planner":
    st.subheader("📈 Step-up SIP Planner")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sip = st.number_input("Starting Monthly SIP (₹)", 0.0, value=10000.0, step=500.0)
    with c2:
        stepup = st.number_input("Annual Step-up (%)", 0.0, value=10.0, step=1.0)
    with c3:
        rate = st.number_input("Expected Return (% p.a.)", 0.0, value=12.0, step=0.1)
    with c4:
        years = st.number_input("Duration (Years)", 1.0, value=15.0, step=1.0)

    fv = future_value_stepup_sip(sip, rate, years, stepup)
    df = stepup_projection_table(sip, rate, years, stepup)
    total_invested = df["Total Invested"].iloc[-1] if not df.empty else sip * years * 12
    gain = fv - total_invested

    render_kpi_cards([
        {"title": "Total Invested", "value": fmt_inr(total_invested)},
        {"title": "Estimated Future Value", "value": fmt_inr(fv)},
        {"title": "Estimated Gain", "value": fmt_inr(gain)},
        {"title": "Annual Step-up", "value": f"{stepup:.1f}%"},
    ])

    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.line_chart(df.set_index("Year")[["Total Invested", "Portfolio Value"]])

    if st.button("➕ Add Step-up SIP to Report"):
        add_report("Step-up SIP", "Future Value", fmt_inr(fv), f"Start SIP {fmt_inr(sip)}, step-up {stepup}%")
        st.success("Added to report.")

elif module == "🧩 Asset Allocation Suggestion":
    st.subheader("🧩 Asset Allocation Suggestion")
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age", 0, 100, value=int(st.session_state.client_age))
    with c2:
        risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"], index=1)

    eq, debt, gold = asset_allocation(age, risk)
    alloc_df = pd.DataFrame({
        "Asset Class": ["Equity", "Debt", "Gold"],
        "Allocation %": [eq, debt, gold]
    })

    render_kpi_cards([
        {"title": "Equity", "value": f"{eq}%"},
        {"title": "Debt", "value": f"{debt}%"},
        {"title": "Gold", "value": f"{gold}%"},
        {"title": "Profile", "value": risk},
    ])

    st.dataframe(alloc_df, use_container_width=True)
    st.bar_chart(alloc_df.set_index("Asset Class"))

    if st.button("➕ Add Allocation to Report"):
        add_report("Asset Allocation", "Suggested Allocation", f"Equity {eq}% / Debt {debt}% / Gold {gold}%", f"Risk {risk}")
        st.success("Added to report.")

elif module == "🧾 Tax Saving Projection":
    st.subheader("🧾 Tax Saving Projection (Basic)")
    c1, c2, c3 = st.columns(3)
    with c1:
        annual_income = st.number_input("Annual Gross Income (₹)", 0.0, value=float(st.session_state.client_income * 12), step=10000.0)
    with c2:
        section_80c = st.number_input("80C Eligible Investment (₹)", 0.0, value=150000.0, step=5000.0)
    with c3:
        other_deductions = st.number_input("Other Deductions (₹)", 0.0, value=50000.0, step=5000.0)

    old_tax_before = basic_tax_old_regime(annual_income)
    old_tax_after = basic_tax_old_regime(max(annual_income - min(section_80c, 150000) - other_deductions, 0))
    tax_saved_old = max(old_tax_before - old_tax_after, 0)

    new_tax = basic_tax_new_regime(annual_income)

    render_kpi_cards([
        {"title": "Old Regime Tax (Before)", "value": fmt_inr(old_tax_before)},
        {"title": "Old Regime Tax (After)", "value": fmt_inr(old_tax_after)},
        {"title": "Tax Saved (Old Regime)", "value": fmt_inr(tax_saved_old)},
        {"title": "New Regime Tax", "value": fmt_inr(new_tax)},
    ])

    suggestion = "Old Regime may be better" if old_tax_after < new_tax else "New Regime may be better"
    st.info(f"**Basic Suggestion:** {suggestion}")

    if st.button("➕ Add Tax Projection to Report"):
        add_report("Tax Projection", "Suggested Regime", suggestion, f"Old after deductions {fmt_inr(old_tax_after)} vs New {fmt_inr(new_tax)}")
        st.success("Added to report.")

elif module == "📝 Advisor Notes":
    st.subheader("📝 Advisor Notes Section")
    notes = st.text_area(
        "Enter Advisor Notes / Recommendations",
        value=st.session_state.advisor_notes,
        height=250,
        placeholder="Example: Increase SIP by 10% yearly, build 6 months emergency fund, take term cover of ₹1 Cr, reduce unsecured debt..."
    )
    st.session_state.advisor_notes = notes
    st.success("Notes auto-saved in session.")

    if st.button("➕ Add Advisor Notes Marker to Report"):
        add_report("Advisor Notes", "Notes Added", "Yes", "Advisor recommendations available in report.")
        st.success("Added to report.")

elif module == "📄 Client Summary Dashboard / Report":
    st.subheader("📄 Client Summary Dashboard / Report")
    df = report_df()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Client", st.session_state.client_name or "Not Set")
    with c2:
        st.metric("Age", st.session_state.client_age)
    with c3:
        st.metric("Monthly Income", fmt_inr(st.session_state.client_income))
    with c4:
        st.metric("Report Items", len(df))

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Summary Report Table")
    st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Advisor Notes")
    st.write(st.session_state.advisor_notes if st.session_state.advisor_notes else "No advisor notes added yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    if not df.empty:
        csv_bytes = to_csv_download(df)
        st.download_button(
            "⬇️ Download Summary CSV",
            data=csv_bytes,
            file_name="freedom_ultra_pro_v8_summary.csv",
            mime="text/csv"
        )

    if PDF_AVAILABLE:
        pdf_buffer = build_pdf(
            df,
            {
                "name": st.session_state.client_name,
                "age": st.session_state.client_age,
                "income": fmt_inr(st.session_state.client_income)
            },
            st.session_state.advisor_notes
        )
        if pdf_buffer:
            st.download_button(
                "⬇️ Download PDF Report",
                data=pdf_buffer,
                file_name="freedom_ultra_pro_v8_report.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("PDF export unavailable. Install `reportlab` to enable PDF download.")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown(
    """
    <div class="small-note">
    <b>Freedom ULTRA PRO V8</b> • Professional MFD Financial Planning Super App •
    For education / planning assistance only. Final recommendations should be validated by a qualified advisor and applicable regulations.
    </div>
    """,
    unsafe_allow_html=True
)
