# FINAL Freedom ULTRA PRO V12 WEALTHY SUPREME BOARDROOM GOD MODE SINGLE app.py
# Single-file Streamlit super app with REAL PDF report generation + premium boardroom experience

import streamlit as st
import json
import io
from datetime import datetime
from pathlib import Path

# Optional libraries
try:
    import pandas as pd
except Exception:
    pd = None

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

# PDF libraries (real PDF generation)
PDF_READY = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
except Exception:
    PDF_READY = False

st.set_page_config(page_title="Freedom ULTRA PRO V12 | Wealthy Supreme", layout="wide", page_icon="💜")

# ============================================================
# HELPERS
# ============================================================
def fmt_inr(x):
    try:
        return f"₹{float(x):,.2f}"
    except Exception:
        return f"₹{x}"


def safe_div(a, b):
    return a / b if b not in [0, None] else 0


def future_value_sip(monthly_investment, annual_return, years):
    r = annual_return / 12 / 100
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return monthly_investment * n
    return monthly_investment * (((1 + r) ** n - 1) / r) * (1 + r)


def future_value_lumpsum(amount, annual_return, years):
    return amount * ((1 + annual_return / 100) ** years)


def emi(principal, annual_rate, years):
    r = annual_rate / 12 / 100
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return principal / n
    return principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)


def swp_monthly(corpus, annual_return, years):
    r = annual_return / 12 / 100
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return corpus / n
    return corpus * r / (1 - (1 + r) ** (-n))


def required_sip_for_goal(goal_amount, annual_return, years):
    r = annual_return / 12 / 100
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return goal_amount / n
    denom = (((1 + r) ** n - 1) / r) * (1 + r)
    return goal_amount / denom if denom != 0 else 0


def required_lumpsum_for_goal(goal_amount, annual_return, years):
    if years <= 0:
        return goal_amount
    return goal_amount / ((1 + annual_return / 100) ** years)


def annual_stepup_sip(target_amount, annual_return, years, stepup_pct):
    low, high = 0, max(target_amount, 1000)
    r = annual_return / 12 / 100
    months = int(years * 12)

    def fv(base):
        total = 0
        sip = base
        for m in range(1, months + 1):
            if m > 1 and (m - 1) % 12 == 0:
                sip *= (1 + stepup_pct / 100)
            remain = months - m + 1
            total += sip * ((1 + r) ** remain)
        return total

    for _ in range(80):
        mid = (low + high) / 2
        if fv(mid) >= target_amount:
            high = mid
        else:
            low = mid
    return high


def inflation_adjusted_cost(current_cost, inflation, years):
    return current_cost * ((1 + inflation / 100) ** years)


def set_module(name):
    st.session_state.module = name


def generate_recommendation(risk_profile, annual_surplus, insurance_gap, monthly_sip_need):
    if risk_profile == "Conservative":
        mf = "Large Cap + Hybrid + Short Duration Debt"
    elif risk_profile == "Moderate":
        mf = "Flexi Cap + Large & Mid Cap + Hybrid"
    else:
        mf = "Flexi Cap + Mid Cap + Index + Tactical Debt"

    if annual_surplus / 12 >= monthly_sip_need:
        status = "Goal appears feasible with current surplus discipline."
    else:
        status = "Need expense optimisation or phased goal funding strategy."

    ins = "Insurance gap should be closed immediately." if insurance_gap > 0 else "Insurance appears broadly adequate based on current inputs."
    return mf, status, ins


def build_pdf_bytes(title, lines):
    if not PDF_READY:
        return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=12,
    )
    body = styles["BodyText"]
    story = [Paragraph(title, title_style), Spacer(1, 8)]
    for line in lines:
        story.append(Paragraph(str(line).replace("\n", "<br/>"), body))
        story.append(Spacer(1, 6))
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# ============================================================
# SESSION STATE
# ============================================================
if "clients" not in st.session_state:
    st.session_state.clients = []
if "notes" not in st.session_state:
    st.session_state.notes = []
if "module" not in st.session_state:
    st.session_state.module = "Dashboard"

# ============================================================
# THEME
# ============================================================
st.markdown(
    """
    <style>
    .block-container {padding-top: 0.45rem; padding-bottom: 2rem;}
    [data-testid="stSidebar"] {background: linear-gradient(180deg, #0b1020 0%, #111827 35%, #1e1b4b 100%);}    
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 30%, #4c1d95 65%, #7c3aed 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 28px;
        padding: 18px 24px;
        box-shadow: 0 16px 36px rgba(0,0,0,0.30);
        margin-bottom: 14px;
    }
    .hero-title {font-size: 2.55rem; font-weight: 900; color: #faf5ff; margin-bottom: 4px;}
    .hero-sub {color: #e5e7eb; font-size: 0.96rem;}
    div.stButton > button {
        width: 100%; border-radius: 14px; padding: 0.72rem 0.85rem; font-weight: 800;
        border: 1px solid rgba(139,92,246,0.35);
        background: linear-gradient(135deg, rgba(76,29,149,0.98), rgba(109,40,217,0.98));
        color: white; box-shadow: 0 8px 18px rgba(76,29,149,0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# LOGO
# ============================================================
logo_candidates = [Path("wealthy_logo.png"), Path("logo.png"), Path("image.png"), Path("/mnt/data/image.png")]
logo_path = None
for p in logo_candidates:
    if p.exists():
        logo_path = p
        break

if logo_path:
    st.sidebar.image(str(logo_path), use_container_width=True)
else:
    st.sidebar.markdown("## 💜 Wealthy")

# ============================================================
# NAVIGATION
# ============================================================
st.sidebar.title("Freedom ULTRA PRO V12")
st.sidebar.caption("WEALTHY SUPREME BOARDROOM GOD MODE")

nav_groups = {
    "Supreme": ["Dashboard", "Boardroom Client Summary", "CEO Proposal Summary", "One-Click Client Recommendation", "Advisor Meeting Script", "Export Center"],
    "Core": ["Client Profile", "Net Worth Tracker", "Risk Profiler", "Asset Allocation Engine"],
    "Investments": ["SIP Calculator", "Lumpsum Calculator", "SWP Calculator", "Step-Up SIP Planner"],
    "Planning": ["Goal Planner", "Retirement Planner", "FIRE Planner", "Insurance Need Analysis", "Cashflow Planner"],
    "Lifestyle": ["Child Education Planner", "Marriage Planner", "Travel Planner", "Car Purchase Planner", "iPhone Purchase Planner", "EMI / Loan Planner"],
    "Business": ["MFD CRM Lead Tracker", "AUM Projection", "Lead Conversion Analytics"],
}
for group, items in nav_groups.items():
    st.sidebar.markdown(f"### {group}")
    for item in items:
        if st.sidebar.button(item, key=f"side_{item}"):
            set_module(item)

module = st.session_state.module

# ============================================================
# HEADER
# ============================================================
col1, col2 = st.columns([1, 5])
with col1:
    if logo_path:
        st.image(str(logo_path), use_container_width=True)
with col2:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">FINAL Freedom ULTRA PRO V12</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Wealthy Supreme Boardroom God Mode • Real PDF Report Buttons • Advisor Script • Premium Executive Meeting Experience</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ============================================================
# DASHBOARD
# ============================================================
if module == "Dashboard":
    a, b, c, d = st.columns(4)
    a.metric("Version", "V12")
    b.metric("Brand", "Wealthy")
    c.metric("Modules", "28")
    d.metric("PDF Engine", "READY" if PDF_READY else "Install reportlab")
    st.success("Wealthy Supreme Boardroom God Mode is ready for elite client meetings.")

    st.markdown("### 🚀 Supreme Quick Launch")
    r1 = st.columns(4)
    with r1[0]:
        if st.button("👤 Client Profile"): set_module("Client Profile")
    with r1[1]:
        if st.button("📊 Net Worth"): set_module("Net Worth Tracker")
    with r1[2]:
        if st.button("⚖️ Risk"): set_module("Risk Profiler")
    with r1[3]:
        if st.button("✨ Recommendation"): set_module("One-Click Client Recommendation")

    r2 = st.columns(4)
    with r2[0]:
        if st.button("🧾 CEO Proposal"): set_module("CEO Proposal Summary")
    with r2[1]:
        if st.button("🏛️ Boardroom Summary"): set_module("Boardroom Client Summary")
    with r2[2]:
        if st.button("🎤 Advisor Script"): set_module("Advisor Meeting Script")
    with r2[3]:
        if st.button("📤 Export"): set_module("Export Center")

# ============================================================
# CORE MODULES
# ============================================================
elif module == "Client Profile":
    st.subheader("👤 Client Profile Master")
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Client Name", "")
        age = st.number_input("Age", min_value=18, max_value=100, value=30)
        city = st.text_input("City", "")
    with c2:
        mobile = st.text_input("Mobile", "")
        email = st.text_input("Email", "")
        occupation = st.text_input("Occupation", "")
    with c3:
        annual_income = st.number_input("Annual Income (₹)", min_value=0.0, value=1200000.0, step=50000.0)
        annual_expense = st.number_input("Annual Expense (₹)", min_value=0.0, value=600000.0, step=50000.0)
        investable_surplus = max(annual_income - annual_expense, 0)
    marital = st.selectbox("Marital Status", ["Single", "Married", "Other"])
    dependents = st.number_input("Dependents", min_value=0, max_value=10, value=0)
    notes = st.text_area("Advisor Notes", "")
    st.info(f"Estimated Annual Investable Surplus: {fmt_inr(investable_surplus)}")
    if st.button("💾 Save Client in Session"):
        st.session_state.clients.append({"name": name, "age": age, "city": city, "mobile": mobile, "email": email, "occupation": occupation, "annual_income": annual_income, "annual_expense": annual_expense, "investable_surplus": investable_surplus, "marital": marital, "dependents": dependents, "notes": notes})
        st.success("Client saved in current session.")
    if st.session_state.clients:
        st.markdown("### Saved Clients (Session)")
        if pd: st.dataframe(pd.DataFrame(st.session_state.clients), use_container_width=True)
        else: st.write(st.session_state.clients)

elif module == "Net Worth Tracker":
    st.subheader("📊 Net Worth Tracker")
    c1, c2 = st.columns(2)
    with c1:
        equity = st.number_input("Equity / Mutual Funds (₹)", min_value=0.0, value=500000.0, step=50000.0)
        fd = st.number_input("FD / Debt / Bonds (₹)", min_value=0.0, value=300000.0, step=50000.0)
        epf = st.number_input("EPF / PPF / NPS (₹)", min_value=0.0, value=400000.0, step=50000.0)
        cash = st.number_input("Cash / Bank Balance (₹)", min_value=0.0, value=200000.0, step=50000.0)
    with c2:
        property_val = st.number_input("Property Value (₹)", min_value=0.0, value=3000000.0, step=100000.0)
        gold = st.number_input("Gold / Other Assets (₹)", min_value=0.0, value=200000.0, step=50000.0)
        loans = st.number_input("Total Liabilities / Loans (₹)", min_value=0.0, value=1500000.0, step=100000.0)
        other_assets = st.number_input("Other Assets (₹)", min_value=0.0, value=100000.0, step=50000.0)
    total_assets = equity + fd + epf + cash + property_val + gold + other_assets
    net_worth = total_assets - loans
    a, b, c = st.columns(3)
    a.metric("Total Assets", fmt_inr(total_assets))
    b.metric("Total Liabilities", fmt_inr(loans))
    c.metric("Net Worth", fmt_inr(net_worth))
    if plt:
        labels = ["Equity", "Debt", "Retirement", "Cash", "Property", "Gold", "Other"]
        values = [equity, fd, epf, cash, property_val, gold, other_assets]
        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%')
        ax.set_title("Asset Allocation Snapshot")
        st.pyplot(fig)

elif module == "Risk Profiler":
    st.subheader("⚖️ Risk Profiler")
    q1 = st.slider("Investment Horizon", 1, 10, 6)
    q2 = st.slider("Reaction to 20% market fall", 1, 10, 5)
    q3 = st.slider("Return vs Stability preference", 1, 10, 6)
    q4 = st.slider("Market Experience", 1, 10, 4)
    q5 = st.slider("Income Stability", 1, 10, 7)
    score = q1 + q2 + q3 + q4 + q5
    if score <= 20: profile, eq, debt = "Conservative", 20, 80
    elif score <= 35: profile, eq, debt = "Moderate", 50, 50
    else: profile, eq, debt = "Aggressive", 75, 25
    st.metric("Risk Score", score)
    st.success(f"Risk Profile: {profile}")
    st.info(f"Suggested Allocation: Equity {eq}% | Debt {debt}%")

elif module == "Asset Allocation Engine":
    st.subheader("🧠 Asset Allocation Engine")
    age = st.number_input("Client Age", min_value=18, max_value=100, value=35)
    risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    if risk == "Conservative": eq = max(100 - age - 20, 10)
    elif risk == "Moderate": eq = max(100 - age, 20)
    else: eq = min(max(110 - age, 40), 85)
    debt = 100 - eq
    st.metric("Recommended Equity Allocation", f"{eq}%")
    st.metric("Recommended Debt Allocation", f"{debt}%")
    st.success("Indicative MF category mix: Large Cap / Flexi Cap / Hybrid / Short Duration Debt based on suitability.")

# ============================================================
# INVESTMENTS
# ============================================================
elif module == "SIP Calculator":
    st.subheader("📈 SIP Calculator")
    c1, c2, c3 = st.columns(3)
    sip_amt = c1.number_input("Monthly SIP (₹)", min_value=0.0, value=10000.0, step=1000.0)
    ret = c2.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    years = c3.number_input("Years", min_value=1, value=10, step=1)
    fv = future_value_sip(sip_amt, ret, years)
    invested = sip_amt * years * 12
    a, b, c = st.columns(3)
    a.metric("Total Invested", fmt_inr(invested))
    b.metric("Estimated Value", fmt_inr(fv))
    c.metric("Wealth Gain", fmt_inr(fv - invested))

elif module == "Lumpsum Calculator":
    st.subheader("💰 Lumpsum Calculator")
    amt = st.number_input("Investment Amount (₹)", min_value=0.0, value=100000.0, step=10000.0)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    years = st.number_input("Years", min_value=1, value=10, step=1)
    fv = future_value_lumpsum(amt, ret, years)
    a, b = st.columns(2)
    a.metric("Future Value", fmt_inr(fv))
    b.metric("Gain", fmt_inr(fv - amt))

elif module == "SWP Calculator":
    st.subheader("🏦 SWP Calculator")
    corpus = st.number_input("Corpus (₹)", min_value=0.0, value=5000000.0, step=100000.0)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=8.0, step=0.5)
    years = st.number_input("Withdrawal Years", min_value=1, value=20, step=1)
    st.metric("Suggested Monthly SWP", fmt_inr(swp_monthly(corpus, ret, years)))

elif module == "Step-Up SIP Planner":
    st.subheader("🚀 Step-Up SIP Planner")
    goal = st.number_input("Target Corpus (₹)", min_value=0.0, value=10000000.0, step=100000.0)
    years = st.number_input("Years", min_value=1, value=15, step=1)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    stepup = st.number_input("Annual Step-Up (%)", min_value=0.0, value=10.0, step=1.0)
    st.metric("Starting Monthly SIP Required", fmt_inr(annual_stepup_sip(goal, ret, years, stepup)))

# ============================================================
# PLANNING
# ============================================================
elif module == "Goal Planner":
    st.subheader("🎯 Goal Planner")
    goal_name = st.text_input("Goal Name", "Dream Goal")
    current_cost = st.number_input("Current Cost / Target Today (₹)", min_value=0.0, value=1000000.0, step=50000.0)
    years = st.number_input("Years to Goal", min_value=1, value=10, step=1)
    inflation = st.number_input("Inflation (%)", min_value=0.0, value=6.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    future_goal = inflation_adjusted_cost(current_cost, inflation, years)
    a, b, c = st.columns(3)
    a.metric("Future Goal Value", fmt_inr(future_goal))
    b.metric("Required Monthly SIP", fmt_inr(required_sip_for_goal(future_goal, ret, years)))
    c.metric("Required Lumpsum Today", fmt_inr(required_lumpsum_for_goal(future_goal, ret, years)))
    st.caption(f"Goal: {goal_name}")

elif module == "Retirement Planner":
    st.subheader("👴 Retirement Planner")
    current_age = st.number_input("Current Age", min_value=18, max_value=80, value=30)
    retire_age = st.number_input("Retirement Age", min_value=current_age+1, max_value=90, value=60)
    monthly_exp = st.number_input("Current Monthly Expense (₹)", min_value=0.0, value=50000.0, step=5000.0)
    inflation = st.number_input("Inflation (%)", min_value=0.0, value=6.0, step=0.5)
    post_ret_return = st.number_input("Post-Retirement Return (%)", min_value=0.0, value=8.0, step=0.5)
    life_expectancy = st.number_input("Life Expectancy", min_value=retire_age+1, max_value=100, value=85)
    pre_ret_return = st.number_input("Pre-Retirement Return (%)", min_value=0.0, value=12.0, step=0.5)
    years_to_ret = retire_age - current_age
    retirement_years = life_expectancy - retire_age
    future_monthly_exp = monthly_exp * ((1 + inflation/100) ** years_to_ret)
    corpus_factor = swp_monthly(1, post_ret_return, retirement_years)
    required_corpus = future_monthly_exp / corpus_factor if corpus_factor != 0 else 0
    sip_required = required_sip_for_goal(required_corpus, pre_ret_return, years_to_ret)
    a, b, c = st.columns(3)
    a.metric("Monthly Expense at Retirement", fmt_inr(future_monthly_exp))
    b.metric("Retirement Corpus Needed", fmt_inr(required_corpus))
    c.metric("Monthly SIP Needed", fmt_inr(sip_required))

elif module == "FIRE Planner":
    st.subheader("🔥 FIRE Planner")
    annual_expense = st.number_input("Annual Expense (₹)", min_value=0.0, value=600000.0, step=50000.0)
    current_corpus = st.number_input("Current Invested Corpus (₹)", min_value=0.0, value=2000000.0, step=100000.0)
    monthly_investment = st.number_input("Monthly Investment (₹)", min_value=0.0, value=30000.0, step=5000.0)
    annual_return = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    fire_target = annual_expense * 25
    corpus = current_corpus
    years = 0
    while corpus < fire_target and years < 60:
        corpus = corpus * (1 + annual_return / 100) + (monthly_investment * 12)
        years += 1
    a, b = st.columns(2)
    a.metric("FIRE Target Corpus", fmt_inr(fire_target))
    b.metric("Estimated Years to FIRE", years if years < 60 else ">60")

elif module == "Insurance Need Analysis":
    st.subheader("🛡️ Insurance Need Analysis")
    annual_income = st.number_input("Annual Income (₹)", min_value=0.0, value=1200000.0, step=50000.0)
    liabilities = st.number_input("Outstanding Liabilities (₹)", min_value=0.0, value=2000000.0, step=50000.0)
    future_goals = st.number_input("Future Goals Corpus (₹)", min_value=0.0, value=3000000.0, step=50000.0)
    existing_cover = st.number_input("Existing Life Cover (₹)", min_value=0.0, value=1000000.0, step=50000.0)
    emergency_fund = st.number_input("Existing Emergency / Liquid Assets (₹)", min_value=0.0, value=500000.0, step=50000.0)
    hlv_cover = annual_income * 15
    suggested_cover = max(hlv_cover + liabilities + future_goals - existing_cover - emergency_fund, 0)
    a, b = st.columns(2)
    a.metric("HLV Based Cover", fmt_inr(hlv_cover))
    b.metric("Suggested Additional Cover", fmt_inr(suggested_cover))

elif module == "Cashflow Planner":
    st.subheader("💸 Monthly Cashflow Planner")
    income = st.number_input("Monthly Income (₹)", min_value=0.0, value=100000.0, step=5000.0)
    fixed = st.number_input("Fixed Expenses (₹)", min_value=0.0, value=40000.0, step=5000.0)
    variable = st.number_input("Variable Expenses (₹)", min_value=0.0, value=20000.0, step=5000.0)
    emi_amt = st.number_input("EMIs (₹)", min_value=0.0, value=10000.0, step=5000.0)
    invest = st.number_input("Investments / SIP (₹)", min_value=0.0, value=15000.0, step=5000.0)
    total_outflow = fixed + variable + emi_amt + invest
    surplus = income - total_outflow
    a, b, c = st.columns(3)
    a.metric("Total Outflow", fmt_inr(total_outflow))
    b.metric("Monthly Surplus", fmt_inr(surplus))
    c.metric("Investment Rate", f"{safe_div(invest, income)*100:.2f}%")

# ============================================================
# LIFESTYLE
# ============================================================
elif module == "Child Education Planner":
    st.subheader("🎓 Child Education Planner")
    current_cost = st.number_input("Current Education Cost (₹)", min_value=0.0, value=2000000.0, step=100000.0)
    years = st.number_input("Years Left", min_value=1, value=15, step=1)
    inflation = st.number_input("Education Inflation (%)", min_value=0.0, value=10.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    future_cost = inflation_adjusted_cost(current_cost, inflation, years)
    st.metric("Future Education Cost", fmt_inr(future_cost))
    st.metric("Required SIP", fmt_inr(required_sip_for_goal(future_cost, ret, years)))

elif module == "Marriage Planner":
    st.subheader("💍 Marriage Planner")
    current_cost = st.number_input("Current Marriage Budget (₹)", min_value=0.0, value=1500000.0, step=100000.0)
    years = st.number_input("Years Left", min_value=1, value=10, step=1)
    inflation = st.number_input("Marriage Inflation (%)", min_value=0.0, value=8.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    future_cost = inflation_adjusted_cost(current_cost, inflation, years)
    st.metric("Future Marriage Cost", fmt_inr(future_cost))
    st.metric("Required SIP", fmt_inr(required_sip_for_goal(future_cost, ret, years)))

elif module == "Travel Planner":
    st.subheader("✈️ Travel Planner")
    budget = st.number_input("Current Travel Budget (₹)", min_value=0.0, value=300000.0, step=10000.0)
    years = st.number_input("Years Left", min_value=1, value=3, step=1)
    inflation = st.number_input("Travel Inflation (%)", min_value=0.0, value=7.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=10.0, step=0.5)
    future_cost = inflation_adjusted_cost(budget, inflation, years)
    st.metric("Future Travel Budget", fmt_inr(future_cost))
    st.metric("Required SIP", fmt_inr(required_sip_for_goal(future_cost, ret, years)))

elif module == "Car Purchase Planner":
    st.subheader("🚗 Car Purchase Planner")
    car_price = st.number_input("Current Car Price (₹)", min_value=0.0, value=1200000.0, step=50000.0)
    down_payment_pct = st.slider("Down Payment %", 0, 100, 20)
    years_to_buy = st.number_input("Years to Buy", min_value=1, value=3, step=1)
    inflation = st.number_input("Car Inflation (%)", min_value=0.0, value=6.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=10.0, step=0.5)
    future_price = inflation_adjusted_cost(car_price, inflation, years_to_buy)
    down_payment = future_price * down_payment_pct / 100
    st.metric("Estimated Future Car Price", fmt_inr(future_price))
    st.metric("Target Down Payment", fmt_inr(down_payment))
    st.metric("Required SIP for Down Payment", fmt_inr(required_sip_for_goal(down_payment, ret, years_to_buy)))

elif module == "iPhone Purchase Planner":
    st.subheader("📱 iPhone Purchase Planner")
    iphone_price = st.number_input("Current iPhone Price (₹)", min_value=0.0, value=80000.0, step=5000.0)
    months = st.number_input("Months to Buy", min_value=1, value=12, step=1)
    inflation = st.number_input("Price Increase (%)", min_value=0.0, value=5.0, step=0.5)
    future_price = iphone_price * ((1 + inflation/100) ** (months / 12))
    st.metric("Estimated Future Price", fmt_inr(future_price))
    st.metric("Monthly Saving Needed", fmt_inr(safe_div(future_price, months)))

elif module == "EMI / Loan Planner":
    st.subheader("🏠 EMI / Loan Planner")
    principal = st.number_input("Loan Amount (₹)", min_value=0.0, value=1000000.0, step=50000.0)
    rate = st.number_input("Interest Rate (%)", min_value=0.0, value=9.0, step=0.25)
    years = st.number_input("Tenure (Years)", min_value=1, value=5, step=1)
    monthly_emi = emi(principal, rate, years)
    total_payment = monthly_emi * years * 12
    a, b, c = st.columns(3)
    a.metric("Monthly EMI", fmt_inr(monthly_emi))
    b.metric("Total Payment", fmt_inr(total_payment))
    c.metric("Total Interest", fmt_inr(total_payment - principal))

# ============================================================
# BUSINESS
# ============================================================
elif module == "MFD CRM Lead Tracker":
    st.subheader("📞 MFD CRM Lead Tracker")
    c1, c2, c3 = st.columns(3)
    with c1:
        lead_name = st.text_input("Lead Name")
        lead_source = st.selectbox("Lead Source", ["Referral", "Walk-in", "Digital", "AMC", "Partner", "Other"])
    with c2:
        lead_stage = st.selectbox("Lead Stage", ["New", "Contacted", "Meeting Done", "Proposal Shared", "Converted", "Lost"])
        lead_aum = st.number_input("Potential AUM (₹)", min_value=0.0, value=500000.0, step=50000.0)
    with c3:
        next_action = st.text_input("Next Action")
        next_date = st.date_input("Next Follow-up Date")
    if st.button("💾 Save Lead"):
        st.session_state.notes.append({"lead_name": lead_name, "source": lead_source, "stage": lead_stage, "potential_aum": lead_aum, "next_action": next_action, "next_date": str(next_date)})
        st.success("Lead note saved in current session.")
    if st.session_state.notes:
        if pd:
            df_notes = pd.DataFrame(st.session_state.notes)
            st.dataframe(df_notes, use_container_width=True)
            st.metric("Total Pipeline AUM", fmt_inr(df_notes["potential_aum"].sum()))
        else:
            st.write(st.session_state.notes)

elif module == "AUM Projection":
    st.subheader("💼 AUM Projection")
    current_aum = st.number_input("Current AUM (₹)", min_value=0.0, value=50000000.0, step=1000000.0)
    monthly_new_sip = st.number_input("Monthly New SIP Book (₹)", min_value=0.0, value=500000.0, step=50000.0)
    annual_growth = st.number_input("Annual Market Growth (%)", min_value=0.0, value=10.0, step=0.5)
    years = st.number_input("Projection Years", min_value=1, value=5, step=1)
    aum = current_aum
    for _ in range(int(years)):
        aum = aum * (1 + annual_growth/100) + (monthly_new_sip * 12)
    trail_est = aum * 0.008
    a, b = st.columns(2)
    a.metric("Projected AUM", fmt_inr(aum))
    b.metric("Indicative 0.8% Trail Revenue", fmt_inr(trail_est))

elif module == "Lead Conversion Analytics":
    st.subheader("📈 Lead Conversion Analytics")
    if st.session_state.notes and pd:
        df = pd.DataFrame(st.session_state.notes)
        total = len(df)
        converted = len(df[df["stage"] == "Converted"])
        ratio = safe_div(converted, total) * 100
        a, b, c = st.columns(3)
        a.metric("Total Leads", total)
        b.metric("Converted", converted)
        c.metric("Conversion %", f"{ratio:.2f}%")
        st.bar_chart(df["stage"].value_counts())
    else:
        st.info("Add leads in CRM to view analytics.")

# ============================================================
# SUPREME / BOARDROOM
# ============================================================
elif module == "One-Click Client Recommendation":
    st.subheader("✨ One-Click Client Recommendation")
    client_name = st.text_input("Client Name", "Premium Client")
    risk_profile = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    annual_income = st.number_input("Annual Income (₹)", min_value=0.0, value=1800000.0, step=50000.0)
    annual_expense = st.number_input("Annual Expense (₹)", min_value=0.0, value=900000.0, step=50000.0)
    insurance_gap = st.number_input("Insurance Gap (₹)", min_value=0.0, value=5000000.0, step=100000.0)
    goal_target = st.number_input("Primary Goal Corpus (₹)", min_value=0.0, value=7500000.0, step=100000.0)
    goal_years = st.number_input("Years to Goal", min_value=1, value=10, step=1)
    exp_return = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    annual_surplus = max(annual_income - annual_expense, 0)
    monthly_sip_need = required_sip_for_goal(goal_target, exp_return, goal_years)
    mf_mix, status, ins = generate_recommendation(risk_profile, annual_surplus, insurance_gap, monthly_sip_need)

    st.markdown("### Recommended Strategy")
    st.write(f"**Client:** {client_name}")
    st.write(f"**Suggested MF Category Mix:** {mf_mix}")
    st.write(f"**Required SIP for Goal:** {fmt_inr(monthly_sip_need)}")
    st.write(f"**Goal Funding View:** {status}")
    st.write(f"**Insurance View:** {ins}")

    txt_report = f"WEALTHY CLIENT RECOMMENDATION\nGenerated: {datetime.now().strftime('%d-%m-%Y %H:%M')}\nClient: {client_name}\nRisk Profile: {risk_profile}\nAnnual Surplus: {fmt_inr(annual_surplus)}\nRequired SIP: {fmt_inr(monthly_sip_need)}\nMF Mix: {mf_mix}\nGoal View: {status}\nInsurance View: {ins}\n"
    st.download_button("⬇️ Download Recommendation Note (.txt)", data=txt_report, file_name=f"wealthy_recommendation_{client_name.replace(' ', '_')}.txt", mime="text/plain")

    pdf_lines = [
        f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        f"Client Name: {client_name}",
        f"Risk Profile: {risk_profile}",
        f"Annual Income: {fmt_inr(annual_income)}",
        f"Annual Expense: {fmt_inr(annual_expense)}",
        f"Annual Surplus: {fmt_inr(annual_surplus)}",
        f"Insurance Gap: {fmt_inr(insurance_gap)}",
        f"Primary Goal Corpus: {fmt_inr(goal_target)}",
        f"Years to Goal: {goal_years}",
        f"Expected Return: {exp_return}%",
        f"Required SIP: {fmt_inr(monthly_sip_need)}",
        f"Suggested MF Category Mix: {mf_mix}",
        f"Goal Funding View: {status}",
        f"Insurance View: {ins}",
        "Advisor Note: Indicative planning output for client meeting discussion.",
    ]
    pdf_bytes = build_pdf_bytes("WEALTHY CLIENT RECOMMENDATION REPORT", pdf_lines)
    if pdf_bytes:
        st.download_button("📄 Download Real PDF Recommendation Report", data=pdf_bytes, file_name=f"wealthy_recommendation_{client_name.replace(' ', '_')}.pdf", mime="application/pdf")
    else:
        st.warning("Install reportlab for real PDF download: pip install reportlab")

elif module == "CEO Proposal Summary":
    st.subheader("🧾 CEO Proposal Summary")
    client_name = st.text_input("Client Name for Proposal", "Prospect Client")
    annual_income = st.number_input("Annual Income (₹)", min_value=0.0, value=1200000.0, step=50000.0)
    annual_expense = st.number_input("Annual Expense (₹)", min_value=0.0, value=600000.0, step=50000.0)
    target_goal = st.number_input("Primary Goal Corpus (₹)", min_value=0.0, value=5000000.0, step=100000.0)
    goal_years = st.number_input("Years to Primary Goal", min_value=1, value=10, step=1)
    exp_return = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    annual_surplus = max(annual_income - annual_expense, 0)
    monthly_surplus = annual_surplus / 12
    rec_sip = required_sip_for_goal(target_goal, exp_return, goal_years)
    coverage = "Feasible" if monthly_surplus >= rec_sip else "Need Surplus Optimization"
    st.markdown("### Proposal Snapshot")
    st.write(f"**Client:** {client_name}")
    st.write(f"**Annual Investable Surplus:** {fmt_inr(annual_surplus)}")
    st.write(f"**Recommended SIP for Goal:** {fmt_inr(rec_sip)}")
    st.write(f"**Status:** {coverage}")

elif module == "Boardroom Client Summary":
    st.subheader("🏛️ Boardroom Client Summary")
    client_name = st.text_input("Client Name", "Premium Client")
    annual_income = st.number_input("Annual Income (₹)", min_value=0.0, value=1800000.0, step=50000.0)
    annual_expense = st.number_input("Annual Expense (₹)", min_value=0.0, value=900000.0, step=50000.0)
    networth = st.number_input("Current Net Worth (₹)", min_value=0.0, value=5000000.0, step=100000.0)
    insurance_gap = st.number_input("Insurance Gap (₹)", min_value=0.0, value=5000000.0, step=100000.0)
    retirement_target = st.number_input("Retirement Corpus Target (₹)", min_value=0.0, value=30000000.0, step=500000.0)
    monthly_sip = st.number_input("Recommended SIP (₹)", min_value=0.0, value=50000.0, step=5000.0)
    annual_surplus = max(annual_income - annual_expense, 0)
    a, b, c, d = st.columns(4)
    a.metric("Annual Surplus", fmt_inr(annual_surplus))
    b.metric("Net Worth", fmt_inr(networth))
    c.metric("Insurance Gap", fmt_inr(insurance_gap))
    d.metric("Recommended SIP", fmt_inr(monthly_sip))
    st.write(f"**Client {client_name}** should prioritise emergency reserve, insurance gap closure, disciplined SIP execution, and retirement corpus acceleration.")

    pdf_lines = [
        f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        f"Client Name: {client_name}",
        f"Annual Income: {fmt_inr(annual_income)}",
        f"Annual Expense: {fmt_inr(annual_expense)}",
        f"Annual Surplus: {fmt_inr(annual_surplus)}",
        f"Net Worth: {fmt_inr(networth)}",
        f"Insurance Gap: {fmt_inr(insurance_gap)}",
        f"Retirement Target: {fmt_inr(retirement_target)}",
        f"Recommended SIP: {fmt_inr(monthly_sip)}",
        "Strategic Note: Prioritise liquidity reserve, insurance closure, goal-linked SIP, retirement acceleration, and periodic portfolio review.",
    ]
    pdf_bytes = build_pdf_bytes("WEALTHY BOARDROOM CLIENT SUMMARY", pdf_lines)
    if pdf_bytes:
        st.download_button("📄 Download Real PDF Boardroom Summary", data=pdf_bytes, file_name=f"wealthy_boardroom_summary_{client_name.replace(' ', '_')}.pdf", mime="application/pdf")
    else:
        st.warning("Install reportlab for real PDF download: pip install reportlab")

elif module == "Advisor Meeting Script":
    st.subheader("🎤 Advisor Meeting Script")
    client_name = st.text_input("Client Name", "Premium Client")
    main_goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    script = f"""
Good morning {client_name}. Thank you for your time today.

In today’s meeting, our focus is to understand your current financial position, identify the protection gaps, and create a goal-linked investment roadmap for {main_goal}.

First, we review your income, expenses, and investable surplus.
Second, we assess your net worth and current asset allocation.
Third, we evaluate your risk profile and align the investment mix accordingly.
Fourth, we calculate the SIP required for your major goals and retirement.
Finally, we summarise the action plan: insurance optimisation, disciplined SIP execution, periodic review, and long-term wealth creation.

My recommendation is to start with a realistic monthly commitment, increase it every year, and keep the portfolio aligned with your life goals.

Thank you. I will now walk you through your personalised recommendation summary.
"""
    st.text_area("Advisor Script", script, height=320)
    st.download_button("⬇️ Download Advisor Script (.txt)", data=script, file_name=f"wealthy_advisor_script_{client_name.replace(' ', '_')}.txt", mime="text/plain")

# ============================================================
# EXPORT
# ============================================================
elif module == "Export Center":
    st.subheader("📤 Export Center")
    export_data = {"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "clients": st.session_state.clients, "lead_notes": st.session_state.notes}
    json_str = json.dumps(export_data, indent=2)
    st.download_button("⬇️ Download Session Data (JSON)", data=json_str, file_name="wealthy_freedom_v12_export.json", mime="application/json")
    st.code(json_str[:5000])

st.divider()
st.caption("Wealthy | FINAL Freedom ULTRA PRO V12 WEALTHY SUPREME BOARDROOM GOD MODE SINGLE app.py • REAL PDF report generation added • Advisor meeting script added • Keep wealthy_logo.png in same folder • Install: pip install streamlit pandas matplotlib reportlab")
