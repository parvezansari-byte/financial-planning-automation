# FINAL Freedom ULTRA PRO V19.1 SIGNATURE PRIVATE BANK EMPEROR FULL CLEAN SINGLE app.py
# Production-ready Streamlit super app for MFD / Financial Planning / Client Meetings

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import io
from datetime import datetime
from pathlib import Path

# =========================
# PDF SUPPORT
# =========================
PDF_READY = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
except Exception:
    PDF_READY = False

st.set_page_config(page_title="Freedom ULTRA PRO V19.1 | Signature Private Bank Emperor", layout="wide", page_icon="💜")

# =========================
# HELPERS
# =========================
def fmt_inr(x):
    try:
        return f"₹{float(x):,.2f}"
    except Exception:
        return f"₹{x}"


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


def inflation_adjusted_cost(current_cost, inflation, years):
    return current_cost * ((1 + inflation / 100) ** years)


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


def build_pdf_bytes(title, lines):
    if not PDF_READY:
        return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCenter", parent=styles["Title"], alignment=TA_CENTER, fontSize=18, leading=22, spaceAfter=12)
    body = styles["BodyText"]
    story = [Paragraph(title, title_style), Spacer(1, 8)]
    for line in lines:
        story.append(Paragraph(str(line).replace("\n", "<br/>"), body))
        story.append(Spacer(1, 6))
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def lifestyle_yearwise_table(current_cost, inflation, years, ret):
    rows = []
    for yr in range(1, years + 1):
        goal_val = inflation_adjusted_cost(current_cost, inflation, yr)
        sip_need = required_sip_for_goal(goal_val, ret, yr)
        rows.append({
            "Year": yr,
            "Projected Goal Value (₹)": round(goal_val, 2),
            "Required SIP (₹)": round(sip_need, 2),
        })
    return pd.DataFrame(rows)

# =========================
# SESSION
# =========================
if "module" not in st.session_state:
    st.session_state.module = "Dashboard"
if "clients" not in st.session_state:
    st.session_state.clients = []
if "leads" not in st.session_state:
    st.session_state.leads = []

# =========================
# STYLING
# =========================
st.markdown("""
<style>
.block-container {padding-top: 0.5rem; padding-bottom: 2rem;}
[data-testid="stSidebar"] {background: linear-gradient(180deg, #050816 0%, #0b1020 40%, #1e1b4b 100%);}    
.hero {
    background: linear-gradient(135deg, #050816 0%, #111827 18%, #1e1b4b 55%, #6d28d9 100%);
    border-radius: 28px; padding: 18px 24px; margin-bottom: 14px;
    border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 18px 42px rgba(0,0,0,0.32);
}
.hero-title {font-size: 2.35rem; font-weight: 900; color: #faf5ff;}
.hero-sub {color: #e5e7eb; font-size: 0.95rem;}
div.stButton > button {
    width: 100%; border-radius: 14px; padding: 0.72rem 0.85rem; font-weight: 800;
    background: linear-gradient(135deg, #4c1d95, #6d28d9); color: white;
    border: 1px solid rgba(139,92,246,0.35);
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGO
# =========================
logo_candidates = [Path("wealthy_logo.png"), Path("logo.png"), Path("image.png"), Path("/mnt/data/image.png")]
logo_path = next((p for p in logo_candidates if p.exists()), None)
if logo_path:
    st.sidebar.image(str(logo_path), use_container_width=True)
else:
    st.sidebar.markdown("## 💜 Wealthy")

# =========================
# NAVIGATION
# =========================
st.sidebar.title("Freedom ULTRA PRO V19.1")
st.sidebar.caption("WEALTHY SIGNATURE PRIVATE BANK EMPEROR")

nav = {
    "Emperor HQ": ["Dashboard", "Client Onboarding Master", "One-Click Client Recommendation", "Boardroom Client Summary", "Advisor Meeting Script", "Export Center"],
    "Core": ["Client Profile", "Net Worth Tracker", "Risk Profiler", "Asset Allocation Dashboard", "Risk-to-Product Mapper"],
    "Investments": ["SIP vs Lumpsum Comparator", "Normal SIP vs Step-Up SIP Chart", "SIP Calculator", "Lumpsum Calculator", "SWP Calculator", "Step-Up SIP Planner"],
    "Life Goals": ["Family Goals Master Dashboard", "Advanced Goal Prioritization Engine", "Goal Planner", "Goal Funding Gap Analyzer", "Retirement Planner", "Retirement Shortfall Analyzer", "Child Education Planner", "Marriage Planner", "Travel Planner", "Car Purchase Planner", "iPhone Purchase Planner"],
    "Protection & PDF": ["Insurance Need Analysis", "Insurance PDF Report", "Client Fact Find Form PDF", "Client Meeting Executive Summary PDF", "Master Combined Proposal PDF", "Goal PDF Report", "Retirement PDF Report"],
    "Cashflow & Business": ["Cashflow Planner", "EMI / Loan Planner", "MFD CRM Lead Tracker", "AUM Projection", "Client Proposal Generator"],
}
for grp, items in nav.items():
    st.sidebar.markdown(f"### {grp}")
    for item in items:
        if st.sidebar.button(item, key=f"nav_{item}"):
            st.session_state.module = item

module = st.session_state.module

# =========================
# HEADER
# =========================
col1, col2 = st.columns([1, 5])
with col1:
    if logo_path:
        st.image(str(logo_path), use_container_width=True)
with col2:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">FINAL Freedom ULTRA PRO V19.1</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Wealthy Signature Private Bank Emperor • Full Clean Flagship Build • Black Card Boardroom UI • Production-Ready MFD Client Conversion Suite</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# =========================
# DASHBOARD
# =========================
if module == "Dashboard":
    a, b, c, d = st.columns(4)
    a.metric("Version", "V19.1")
    b.metric("Brand", "Wealthy")
    c.metric("Modules", "35+")
    d.metric("PDF", "READY" if PDF_READY else "Install reportlab")
    st.success("Wealthy Signature Private Bank Emperor is ready for flagship client meetings.")

    st.markdown("### 🚀 Emperor Quick Launch")
    r1 = st.columns(4)
    with r1[0]:
        if st.button("👤 Onboarding"): st.session_state.module = "Client Onboarding Master"
    with r1[1]:
        if st.button("🎯 Goals"): st.session_state.module = "Family Goals Master Dashboard"
    with r1[2]:
        if st.button("👴 Retirement"): st.session_state.module = "Retirement Planner"
    with r1[3]:
        if st.button("📄 Proposal PDF"): st.session_state.module = "Master Combined Proposal PDF"

# =========================
# CORE MODULES
# =========================
elif module == "Client Onboarding Master":
    st.subheader("📝 Client Onboarding Master")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Client Name")
    age = c1.number_input("Age", 18, 100, 35)
    city = c1.text_input("City")
    mobile = c2.text_input("Mobile")
    email = c2.text_input("Email")
    occupation = c2.text_input("Occupation")
    annual_income = c3.number_input("Annual Income (₹)", 0.0, 1e9, 1200000.0, 50000.0)
    annual_expense = c3.number_input("Annual Expense (₹)", 0.0, 1e9, 600000.0, 50000.0)
    networth = st.number_input("Current Net Worth (₹)", 0.0, 1e10, 2500000.0, 100000.0)
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    surplus = max(annual_income - annual_expense, 0)
    st.info(f"Annual Investable Surplus: {fmt_inr(surplus)}")
    if st.button("💾 Save Full Onboarding"):
        st.session_state.clients.append({"name": name, "age": age, "city": city, "mobile": mobile, "email": email, "occupation": occupation, "annual_income": annual_income, "annual_expense": annual_expense, "surplus": surplus, "networth": networth, "goal": goal})
        st.success("Full client onboarding saved")

elif module == "Client Profile":
    st.subheader("👤 Client Profile")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Client Name")
    age = c1.number_input("Age", 18, 100, 35)
    city = c1.text_input("City")
    mobile = c2.text_input("Mobile")
    email = c2.text_input("Email")
    occupation = c2.text_input("Occupation")
    annual_income = c3.number_input("Annual Income (₹)", 0.0, 1e9, 1200000.0, 50000.0)
    annual_expense = c3.number_input("Annual Expense (₹)", 0.0, 1e9, 600000.0, 50000.0)
    surplus = max(annual_income - annual_expense, 0)
    st.info(f"Annual Investable Surplus: {fmt_inr(surplus)}")

elif module == "Net Worth Tracker":
    st.subheader("📊 Net Worth Tracker")
    c1, c2 = st.columns(2)
    equity = c1.number_input("Equity / MF (₹)", 0.0, 1e10, 500000.0, 50000.0)
    debt = c1.number_input("Debt / FD / Bonds (₹)", 0.0, 1e10, 300000.0, 50000.0)
    cash = c1.number_input("Cash / Bank (₹)", 0.0, 1e10, 200000.0, 50000.0)
    property_val = c2.number_input("Property Value (₹)", 0.0, 1e10, 3000000.0, 100000.0)
    gold = c2.number_input("Gold / Other Assets (₹)", 0.0, 1e10, 200000.0, 50000.0)
    loans = c2.number_input("Loans / Liabilities (₹)", 0.0, 1e10, 1500000.0, 100000.0)
    total_assets = equity + debt + cash + property_val + gold
    networth = total_assets - loans
    a, b, c = st.columns(3)
    a.metric("Assets", fmt_inr(total_assets))
    b.metric("Liabilities", fmt_inr(loans))
    c.metric("Net Worth", fmt_inr(networth))
    fig, ax = plt.subplots()
    ax.pie([equity, debt, cash, property_val, gold], labels=["Equity", "Debt", "Cash", "Property", "Gold"], autopct='%1.1f%%')
    ax.set_title("Net Worth Asset Mix")
    st.pyplot(fig)

elif module == "Risk Profiler":
    st.subheader("⚖️ Risk Profiler")
    score = sum([st.slider("Investment Horizon", 1, 10, 6), st.slider("Reaction to Market Fall", 1, 10, 5), st.slider("Return Preference", 1, 10, 6), st.slider("Market Experience", 1, 10, 4), st.slider("Income Stability", 1, 10, 7)])
    if score <= 20:
        profile, eq, debt_alloc = "Conservative", 25, 75
    elif score <= 35:
        profile, eq, debt_alloc = "Moderate", 55, 45
    else:
        profile, eq, debt_alloc = "Aggressive", 75, 25
    st.metric("Risk Score", score)
    st.success(f"Risk Profile: {profile}")
    st.info(f"Suggested Allocation: Equity {eq}% | Debt {debt_alloc}%")

elif module == "Asset Allocation Dashboard":
    st.subheader("🧠 Asset Allocation Dashboard")
    c1, c2 = st.columns(2)
    age = c1.number_input("Client Age", 18, 100, 35)
    risk = c2.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    if risk == "Conservative": eq = max(100 - age - 20, 10)
    elif risk == "Moderate": eq = max(100 - age, 20)
    else: eq = min(max(110 - age, 40), 85)
    debt_alloc = 100 - eq
    st.metric("Recommended Equity %", f"{eq}%")
    st.metric("Recommended Debt %", f"{debt_alloc}%")

elif module == "Risk-to-Product Mapper":
    st.subheader("🧭 Risk-to-Product Mapper")
    risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    products = ["Liquid Fund", "Short Duration Debt Fund", "Hybrid Conservative Fund", "Large Cap Fund"] if risk == "Conservative" else (["Large Cap Fund", "Flexi Cap Fund", "Balanced Advantage Fund", "Large & Mid Cap Fund"] if risk == "Moderate" else ["Flexi Cap Fund", "Mid Cap Fund", "Index Fund", "Aggressive Hybrid / Tactical Debt"])
    for p in products:
        st.write(f"- {p}")

# =========================
# INVESTMENT MODULES
# =========================
elif module == "SIP vs Lumpsum Comparator":
    st.subheader("📊 SIP vs Lumpsum Comparator")
    c1, c2, c3, c4 = st.columns(4)
    sip_amt = c1.number_input("Monthly SIP (₹)", 0.0, 1e8, 10000.0, 1000.0)
    lump_amt = c2.number_input("Lumpsum (₹)", 0.0, 1e10, 1200000.0, 10000.0)
    ret = c3.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    years = int(c4.number_input("Years", 1, 60, 10))
    st.metric("SIP Future Value", fmt_inr(future_value_sip(sip_amt, ret, years)))
    st.metric("Lumpsum Future Value", fmt_inr(future_value_lumpsum(lump_amt, ret, years)))

elif module == "Normal SIP vs Step-Up SIP Chart":
    st.subheader("📈 Normal SIP vs Step-Up SIP Chart")
    c1, c2, c3, c4 = st.columns(4)
    sip_amt = c1.number_input("Monthly SIP (₹)", 0.0, 1e8, 10000.0, 1000.0)
    years = int(c2.number_input("Years", 1, 60, 15))
    ret = c3.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    stepup = c4.number_input("Annual Step-Up (%)", 0.0, 50.0, 10.0, 1.0)
    normal = [future_value_sip(sip_amt, ret, y) for y in range(1, years + 1)]
    step = []
    corpus = 0
    yearly_sip = sip_amt * 12
    for y in range(1, years + 1):
        corpus = (corpus + yearly_sip) * (1 + ret / 100)
        step.append(corpus)
        yearly_sip *= (1 + stepup / 100)
    fig, ax = plt.subplots()
    ax.plot(range(1, years + 1), normal, label="Normal SIP")
    ax.plot(range(1, years + 1), step, label="Step-Up SIP")
    ax.legend(); ax.set_title("Normal SIP vs Step-Up SIP")
    st.pyplot(fig)

elif module == "SIP Calculator":
    st.subheader("📈 SIP Calculator")
    c1, c2, c3 = st.columns(3)
    sip_amt = c1.number_input("Monthly SIP (₹)", 0.0, 1e8, 10000.0, 1000.0)
    ret = c2.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    years = int(c3.number_input("Years", 1, 60, 10))
    fv = future_value_sip(sip_amt, ret, years)
    invested = sip_amt * 12 * years
    st.metric("Total Invested", fmt_inr(invested))
    st.metric("Current Value", fmt_inr(fv))
    st.metric("Gain", fmt_inr(fv - invested))
    rows = []
    for yr in range(1, years + 1):
        inv = sip_amt * 12 * yr
        val = future_value_sip(sip_amt, ret, yr)
        rows.append({"Year": yr, "Invested Value (₹)": round(inv, 2), "Current Value (₹)": round(val, 2), "Gain (₹)": round(val - inv, 2)})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif module == "Lumpsum Calculator":
    st.subheader("💰 Lumpsum Calculator")
    c1, c2, c3 = st.columns(3)
    amt = c1.number_input("Investment Amount (₹)", 0.0, 1e10, 100000.0, 10000.0)
    ret = c2.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    years = int(c3.number_input("Years", 1, 60, 10))
    fv = future_value_lumpsum(amt, ret, years)
    st.metric("Current Value", fmt_inr(fv))
    st.metric("Gain", fmt_inr(fv - amt))

elif module == "SWP Calculator":
    st.subheader("🏦 SWP Calculator")
    c1, c2, c3 = st.columns(3)
    corpus = c1.number_input("Corpus (₹)", 0.0, 1e10, 5000000.0, 100000.0)
    ret = c2.number_input("Expected Return (%)", 0.0, 30.0, 8.0, 0.5)
    years = int(c3.number_input("Withdrawal Years", 1, 60, 20))
    monthly = swp_monthly(corpus, ret, years)
    st.metric("Suggested Monthly SWP", fmt_inr(monthly))

elif module == "Step-Up SIP Planner":
    st.subheader("🚀 Step-Up SIP Planner")
    c1, c2, c3, c4 = st.columns(4)
    goal = c1.number_input("Target Corpus (₹)", 0.0, 1e10, 10000000.0, 100000.0)
    years = int(c2.number_input("Years", 1, 60, 15))
    ret = c3.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    stepup = c4.number_input("Annual Step-Up (%)", 0.0, 50.0, 10.0, 1.0)
    st.metric("Starting Monthly SIP Required", fmt_inr(annual_stepup_sip(goal, ret, years, stepup)))

# =========================
# GOAL MODULES
# =========================
elif module == "Family Goals Master Dashboard":
    st.subheader("👨‍👩‍👧‍👦 Family Goals Master Dashboard")
    c1, c2, c3 = st.columns(3)
    child_goal = c1.number_input("Child Education Goal (₹)", 0.0, 1e10, 2500000.0, 100000.0)
    marriage_goal = c2.number_input("Marriage Goal (₹)", 0.0, 1e10, 1500000.0, 100000.0)
    retirement_goal = c3.number_input("Retirement Goal (₹)", 0.0, 1e10, 30000000.0, 500000.0)
    travel_goal = c1.number_input("Travel Goal (₹)", 0.0, 1e10, 300000.0, 25000.0)
    car_goal = c2.number_input("Car Goal (₹)", 0.0, 1e10, 1200000.0, 50000.0)
    iphone_goal = c3.number_input("iPhone Goal (₹)", 0.0, 1e6, 100000.0, 5000.0)
    total_goal = child_goal + marriage_goal + retirement_goal + travel_goal + car_goal + iphone_goal
    st.metric("Total Family Goal Corpus", fmt_inr(total_goal))

elif module == "Advanced Goal Prioritization Engine":
    st.subheader("🎯 Advanced Goal Prioritization Engine")
    annual_surplus = st.number_input("Annual Investable Surplus (₹)", 0.0, 1e10, 600000.0, 50000.0)
    essential = st.number_input("Essential Goals Corpus (₹)", 0.0, 1e10, 3000000.0, 100000.0)
    important = st.number_input("Important Goals Corpus (₹)", 0.0, 1e10, 2000000.0, 100000.0)
    luxury = st.number_input("Luxury Goals Corpus (₹)", 0.0, 1e10, 1000000.0, 100000.0)
    st.write("**Priority 1:** Essential Goals")
    st.write("**Priority 2:** Important Goals")
    st.write("**Priority 3:** Luxury Goals")
    st.info(f"Approx years to cover essential goals from surplus only: {(essential / annual_surplus) if annual_surplus > 0 else 0:.2f}")

elif module == "Goal Planner":
    st.subheader("🎯 Goal Planner")
    c1, c2, c3, c4 = st.columns(4)
    current_cost = c1.number_input("Current Cost (₹)", 0.0, 1e10, 1000000.0, 50000.0)
    years = int(c2.number_input("Years to Goal", 1, 60, 10))
    inflation = c3.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    ret = c4.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    future_goal = inflation_adjusted_cost(current_cost, inflation, years)
    st.metric("Future Goal Value", fmt_inr(future_goal))
    st.metric("Required SIP", fmt_inr(required_sip_for_goal(future_goal, ret, years)))

elif module == "Goal Funding Gap Analyzer":
    st.subheader("🎯 Goal Funding Gap Analyzer")
    c1, c2, c3, c4 = st.columns(4)
    current_cost = c1.number_input("Current Goal Cost (₹)", 0.0, 1e10, 1000000.0, 50000.0)
    current_investment = c2.number_input("Current Monthly SIP (₹)", 0.0, 1e8, 10000.0, 1000.0)
    years = int(c3.number_input("Years to Goal", 1, 60, 10))
    inflation = c4.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    future_goal = inflation_adjusted_cost(current_cost, inflation, years)
    current_plan_value = future_value_sip(current_investment, ret, years)
    gap = max(future_goal - current_plan_value, 0)
    st.metric("Future Goal Value", fmt_inr(future_goal))
    st.metric("Projected Current Plan Value", fmt_inr(current_plan_value))
    st.metric("Funding Gap", fmt_inr(gap))

elif module == "Retirement Planner":
    st.subheader("👴 Retirement Planner")
    c1, c2, c3 = st.columns(3)
    current_age = int(c1.number_input("Current Age", 18, 80, 30))
    retire_age = int(c2.number_input("Retirement Age", current_age + 1, 90, 60))
    monthly_exp = c3.number_input("Current Monthly Expense (₹)", 0.0, 1e8, 50000.0, 5000.0)
    inflation = st.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    pre_ret_return = st.number_input("Pre-Retirement Return (%)", 0.0, 50.0, 12.0, 0.5)
    years_to_ret = retire_age - current_age
    future_monthly_exp = monthly_exp * ((1 + inflation / 100) ** years_to_ret)
    corpus_needed = future_monthly_exp * 12 * 25
    st.metric("Monthly Expense @ Retirement", fmt_inr(future_monthly_exp))
    st.metric("Retirement Corpus Needed", fmt_inr(corpus_needed))
    st.metric("Monthly SIP Needed", fmt_inr(required_sip_for_goal(corpus_needed, pre_ret_return, years_to_ret)))

elif module == "Retirement Shortfall Analyzer":
    st.subheader("👴 Retirement Shortfall Analyzer")
    c1, c2, c3, c4 = st.columns(4)
    current_age = int(c1.number_input("Current Age", 18, 80, 30))
    retire_age = int(c2.number_input("Retirement Age", current_age + 1, 90, 60))
    monthly_exp = c3.number_input("Current Monthly Expense (₹)", 0.0, 1e8, 50000.0, 5000.0)
    current_sip = c4.number_input("Current Monthly Retirement SIP (₹)", 0.0, 1e8, 15000.0, 1000.0)
    inflation = st.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    years_to_ret = retire_age - current_age
    corpus_needed = (monthly_exp * ((1 + inflation / 100) ** years_to_ret)) * 12 * 25
    projected = future_value_sip(current_sip, ret, years_to_ret)
    st.metric("Corpus Needed", fmt_inr(corpus_needed))
    st.metric("Projected Corpus", fmt_inr(projected))
    st.metric("Shortfall", fmt_inr(max(corpus_needed - projected, 0)))

elif module == "Child Education Planner":
    st.subheader("🎓 Child Education Planner")
    c1, c2, c3, c4 = st.columns(4)
    current_cost = c1.number_input("Current Education Cost (₹)", 0.0, 1e10, 2500000.0, 100000.0)
    years = int(c2.number_input("Years Left", 1, 30, 10))
    inflation = c3.number_input("Education Inflation (%)", 0.0, 20.0, 8.0, 0.5)
    ret = c4.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    future_cost = inflation_adjusted_cost(current_cost, inflation, years)
    st.metric("Future Education Corpus", fmt_inr(future_cost))
    st.metric("Required Monthly SIP", fmt_inr(required_sip_for_goal(future_cost, ret, years)))
    st.dataframe(lifestyle_yearwise_table(current_cost, inflation, years, ret), use_container_width=True)

elif module == "Marriage Planner":
    st.subheader("💍 Marriage Planner")
    c1, c2, c3, c4 = st.columns(4)
    current_cost = c1.number_input("Current Marriage Cost (₹)", 0.0, 1e10, 1500000.0, 100000.0)
    years = int(c2.number_input("Years Left", 1, 40, 8))
    inflation = c3.number_input("Inflation (%)", 0.0, 20.0, 7.0, 0.5)
    ret = c4.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    future_cost = inflation_adjusted_cost(current_cost, inflation, years)
    st.metric("Future Marriage Corpus", fmt_inr(future_cost))
    st.metric("Required Monthly SIP", fmt_inr(required_sip_for_goal(future_cost, ret, years)))
    st.dataframe(lifestyle_yearwise_table(current_cost, inflation, years, ret), use_container_width=True)

elif module == "Travel Planner":
    st.subheader("✈️ Travel Planner")
    c1, c2, c3, c4 = st.columns(4)
    current_cost = c1.number_input("Current Trip Cost (₹)", 0.0, 1e10, 300000.0, 25000.0)
    years = int(c2.number_input("Years Left", 1, 20, 3))
    inflation = c3.number_input("Travel Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    ret = c4.number_input("Expected Return (%)", 0.0, 50.0, 10.0, 0.5)
    future_cost = inflation_adjusted_cost(current_cost, inflation, years)
    st.metric("Future Travel Corpus", fmt_inr(future_cost))
    st.metric("Required Monthly SIP", fmt_inr(required_sip_for_goal(future_cost, ret, years)))
    st.dataframe(lifestyle_yearwise_table(current_cost, inflation, years, ret), use_container_width=True)

elif module == "Car Purchase Planner":
    st.subheader("🚗 Car Purchase Planner")
    c1, c2, c3, c4 = st.columns(4)
    current_cost = c1.number_input("Current Car Cost (₹)", 0.0, 1e10, 1200000.0, 50000.0)
    years = int(c2.number_input("Years Left", 1, 20, 4))
    inflation = c3.number_input("Car Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    ret = c4.number_input("Expected Return (%)", 0.0, 50.0, 10.0, 0.5)
    future_cost = inflation_adjusted_cost(current_cost, inflation, years)
    st.metric("Future Car Corpus", fmt_inr(future_cost))
    st.metric("Required Monthly SIP", fmt_inr(required_sip_for_goal(future_cost, ret, years)))
    st.dataframe(lifestyle_yearwise_table(current_cost, inflation, years, ret), use_container_width=True)

elif module == "iPhone Purchase Planner":
    st.subheader("📱 iPhone Purchase Planner")
    c1, c2, c3, c4 = st.columns(4)
    current_cost = c1.number_input("Current iPhone Cost (₹)", 0.0, 1e6, 100000.0, 5000.0)
    years = int(c2.number_input("Years Left", 1, 10, 2))
    inflation = c3.number_input("Price Increase (%)", 0.0, 20.0, 5.0, 0.5)
    ret = c4.number_input("Expected Return (%)", 0.0, 50.0, 8.0, 0.5)
    future_cost = inflation_adjusted_cost(current_cost, inflation, years)
    st.metric("Future iPhone Corpus", fmt_inr(future_cost))
    st.metric("Required Monthly SIP", fmt_inr(required_sip_for_goal(future_cost, ret, years)))
    st.dataframe(lifestyle_yearwise_table(current_cost, inflation, years, ret), use_container_width=True)

# =========================
# PROTECTION / PDF / BUSINESS
# =========================
elif module == "Insurance Need Analysis":
    st.subheader("🛡️ Insurance Need Analysis")
    c1, c2, c3, c4 = st.columns(4)
    annual_income = c1.number_input("Annual Income (₹)", 0.0, 1e10, 1200000.0, 50000.0)
    liabilities = c2.number_input("Outstanding Liabilities (₹)", 0.0, 1e10, 2000000.0, 100000.0)
    goals = c3.number_input("Future Goal Corpus Needed (₹)", 0.0, 1e10, 3000000.0, 100000.0)
    existing_cover = c4.number_input("Existing Life Cover (₹)", 0.0, 1e10, 1000000.0, 100000.0)
    recommended_cover = annual_income * 15 + liabilities + goals
    st.metric("Recommended Life Cover", fmt_inr(recommended_cover))
    st.metric("Insurance Gap", fmt_inr(max(recommended_cover - existing_cover, 0)))

elif module == "Insurance PDF Report":
    st.subheader("📄 Insurance PDF Report")
    annual_income = st.number_input("Annual Income (₹)", 0.0, 1e10, 1200000.0, 50000.0, key="ins_pdf_income")
    liabilities = st.number_input("Liabilities (₹)", 0.0, 1e10, 2000000.0, 100000.0, key="ins_pdf_liab")
    goals = st.number_input("Goal Corpus (₹)", 0.0, 1e10, 3000000.0, 100000.0, key="ins_pdf_goal")
    existing_cover = st.number_input("Existing Cover (₹)", 0.0, 1e10, 1000000.0, 100000.0, key="ins_pdf_exist")
    recommended_cover = annual_income * 15 + liabilities + goals
    gap = max(recommended_cover - existing_cover, 0)
    pdf = build_pdf_bytes("WEALTHY INSURANCE REPORT", [f"Recommended Life Cover: {fmt_inr(recommended_cover)}", f"Insurance Gap: {fmt_inr(gap)}"])
    if pdf:
        st.download_button("📄 Download Insurance PDF Report", data=pdf, file_name="wealthy_insurance_report.pdf", mime="application/pdf")

elif module == "Client Fact Find Form PDF":
    st.subheader("📄 Client Fact Find Form PDF")
    client_name = st.text_input("Client Name", "Premium Client")
    age = st.number_input("Age", 18, 100, 35)
    city = st.text_input("City", "Bengaluru")
    income = st.number_input("Annual Income (₹)", 0.0, 1e10, 1200000.0, 50000.0)
    expense = st.number_input("Annual Expense (₹)", 0.0, 1e10, 600000.0, 50000.0)
    pdf = build_pdf_bytes("WEALTHY CLIENT FACT FIND", [f"Client Name: {client_name}", f"Age: {age}", f"City: {city}", f"Annual Income: {fmt_inr(income)}", f"Annual Expense: {fmt_inr(expense)}"])
    if pdf:
        st.download_button("📄 Download Fact Find PDF", data=pdf, file_name="wealthy_fact_find.pdf", mime="application/pdf")

elif module == "Client Meeting Executive Summary PDF":
    st.subheader("📄 Client Meeting Executive Summary PDF")
    client_name = st.text_input("Client Name", "Premium Client", key="exec_name")
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation", key="exec_goal")
    annual_income = st.number_input("Annual Income (₹)", 0.0, 1e10, 1800000.0, 50000.0, key="exec_income")
    annual_expense = st.number_input("Annual Expense (₹)", 0.0, 1e10, 900000.0, 50000.0, key="exec_exp")
    surplus = max(annual_income - annual_expense, 0)
    pdf = build_pdf_bytes("WEALTHY EXECUTIVE SUMMARY", [f"Client Name: {client_name}", f"Primary Goal: {goal}", f"Annual Income: {fmt_inr(annual_income)}", f"Annual Expense: {fmt_inr(annual_expense)}", f"Annual Surplus: {fmt_inr(surplus)}"])
    if pdf:
        st.download_button("📄 Download Executive Summary PDF", data=pdf, file_name="wealthy_executive_summary.pdf", mime="application/pdf")

elif module == "Master Combined Proposal PDF":
    st.subheader("📄 Master Combined Proposal PDF")
    client_name = st.text_input("Client Name", "Premium Client", key="master_name")
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation", key="master_goal")
    sip = st.number_input("Suggested Monthly SIP (₹)", 0.0, 1e8, 50000.0, 5000.0, key="master_sip")
    cover = st.number_input("Suggested Life Cover (₹)", 0.0, 1e10, 25000000.0, 100000.0, key="master_cover")
    pdf = build_pdf_bytes("WEALTHY MASTER COMBINED PROPOSAL", [f"Client Name: {client_name}", f"Primary Goal: {goal}", f"Suggested SIP: {fmt_inr(sip)}", f"Suggested Life Cover: {fmt_inr(cover)}"])
    if pdf:
        st.download_button("📄 Download Master Combined Proposal PDF", data=pdf, file_name="wealthy_master_combined_proposal.pdf", mime="application/pdf")

elif module == "Goal PDF Report":
    st.subheader("📄 Goal PDF Report")
    goal_name = st.text_input("Goal Name", "Dream Goal")
    current_cost = st.number_input("Current Cost (₹)", 0.0, 1e10, 1000000.0, 50000.0)
    years = int(st.number_input("Years", 1, 60, 10))
    inflation = st.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    future_goal = inflation_adjusted_cost(current_cost, inflation, years)
    req_sip = required_sip_for_goal(future_goal, ret, years)
    pdf = build_pdf_bytes("WEALTHY GOAL PLANNER REPORT", [f"Goal Name: {goal_name}", f"Future Goal Value: {fmt_inr(future_goal)}", f"Required SIP: {fmt_inr(req_sip)}"])
    if pdf:
        st.download_button("📄 Download Goal PDF Report", data=pdf, file_name="wealthy_goal_report.pdf", mime="application/pdf")

elif module == "Retirement PDF Report":
    st.subheader("📄 Retirement PDF Report")
    current_age = int(st.number_input("Current Age", 18, 80, 30))
    retire_age = int(st.number_input("Retirement Age", current_age + 1, 90, 60))
    monthly_exp = st.number_input("Current Monthly Expense (₹)", 0.0, 1e8, 50000.0, 5000.0)
    inflation = st.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    years_to_ret = retire_age - current_age
    future_monthly_exp = monthly_exp * ((1 + inflation / 100) ** years_to_ret)
    corpus_needed = future_monthly_exp * 12 * 25
    pdf = build_pdf_bytes("WEALTHY RETIREMENT REPORT", [f"Current Age: {current_age}", f"Retirement Age: {retire_age}", f"Corpus Needed: {fmt_inr(corpus_needed)}"])
    if pdf:
        st.download_button("📄 Download Retirement PDF Report", data=pdf, file_name="wealthy_retirement_report.pdf", mime="application/pdf")

elif module == "Cashflow Planner":
    st.subheader("💸 Cashflow Planner")
    c1, c2, c3 = st.columns(3)
    monthly_income = c1.number_input("Monthly Income (₹)", 0.0, 1e8, 100000.0, 5000.0)
    monthly_expense = c2.number_input("Monthly Expense (₹)", 0.0, 1e8, 60000.0, 5000.0)
    emi_amt = c3.number_input("Monthly EMI (₹)", 0.0, 1e8, 15000.0, 1000.0)
    free_cash = monthly_income - monthly_expense - emi_amt
    st.metric("Monthly Free Cashflow", fmt_inr(free_cash))
    st.metric("Potential Investment Ratio", f"{(free_cash / monthly_income * 100) if monthly_income > 0 else 0:.2f}%")

elif module == "EMI / Loan Planner":
    st.subheader("🏠 EMI / Loan Planner")
    c1, c2, c3 = st.columns(3)
    principal = c1.number_input("Loan Amount (₹)", 0.0, 1e10, 1000000.0, 50000.0)
    rate = c2.number_input("Interest Rate (%)", 0.0, 30.0, 9.0, 0.25)
    years = int(c3.number_input("Tenure (Years)", 1, 40, 5))
    monthly_emi = emi(principal, rate, years)
    total = monthly_emi * years * 12
    st.metric("Monthly EMI", fmt_inr(monthly_emi))
    st.metric("Total Payment", fmt_inr(total))
    st.metric("Total Interest", fmt_inr(total - principal))

elif module == "MFD CRM Lead Tracker":
    st.subheader("📞 MFD CRM Lead Tracker")
    c1, c2, c3 = st.columns(3)
    lead_name = c1.text_input("Lead Name")
    source = c1.selectbox("Lead Source", ["Referral", "Walk-in", "Digital", "AMC", "Partner", "Other"])
    stage = c2.selectbox("Lead Stage", ["New", "Contacted", "Meeting Done", "Proposal Shared", "Converted", "Lost"])
    potential_aum = c2.number_input("Potential AUM (₹)", 0.0, 1e10, 500000.0, 50000.0)
    next_action = c3.text_input("Next Action")
    if st.button("💾 Save Lead"):
        st.session_state.leads.append({"Lead": lead_name, "Source": source, "Stage": stage, "Potential AUM": potential_aum, "Next Action": next_action})
        st.success("Lead saved")
    if st.session_state.leads:
        df = pd.DataFrame(st.session_state.leads)
        st.dataframe(df, use_container_width=True)
        st.metric("Pipeline AUM", fmt_inr(df["Potential AUM"].sum()))

elif module == "AUM Projection":
    st.subheader("💼 AUM Projection")
    c1, c2, c3, c4 = st.columns(4)
    current_aum = c1.number_input("Current AUM (₹)", 0.0, 1e12, 50000000.0, 1000000.0)
    monthly_new_sip = c2.number_input("Monthly New SIP Book (₹)", 0.0, 1e10, 500000.0, 50000.0)
    growth = c3.number_input("Annual Growth (%)", 0.0, 50.0, 10.0, 0.5)
    years = int(c4.number_input("Projection Years", 1, 30, 5))
    aum = current_aum
    for _ in range(years):
        aum = aum * (1 + growth / 100) + (monthly_new_sip * 12)
    st.metric("Projected AUM", fmt_inr(aum))
    st.metric("Indicative 0.8% Trail", fmt_inr(aum * 0.008))

elif module == "Client Proposal Generator":
    st.subheader("🧾 Client Proposal Generator")
    client_name = st.text_input("Client Name", "Premium Client")
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    monthly_commitment = st.number_input("Suggested Monthly Investment (₹)", 0.0, 1e8, 50000.0, 5000.0)
    proposal = f"Client {client_name} is recommended to begin a disciplined investment journey focused on {goal}. Suggested starting monthly commitment is {fmt_inr(monthly_commitment)} with annual review and step-up strategy."
    st.text_area("Proposal Note", proposal, height=180)

elif module == "One-Click Client Recommendation":
    st.subheader("✨ One-Click Client Recommendation")
    c1, c2, c3 = st.columns(3)
    client_name = c1.text_input("Client Name", "Premium Client")
    risk = c1.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    annual_income = c2.number_input("Annual Income (₹)", 0.0, 1e10, 1800000.0, 50000.0)
    annual_expense = c2.number_input("Annual Expense (₹)", 0.0, 1e10, 900000.0, 50000.0)
    goal_target = c3.number_input("Primary Goal Corpus (₹)", 0.0, 1e10, 7500000.0, 100000.0)
    goal_years = int(c3.number_input("Years to Goal", 1, 60, 10))
    exp_return = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    annual_surplus = max(annual_income - annual_expense, 0)
    req_sip = required_sip_for_goal(goal_target, exp_return, goal_years)
    mf_mix = "Large Cap + Hybrid" if risk == "Conservative" else ("Flexi Cap + Large & Mid Cap" if risk == "Moderate" else "Flexi Cap + Mid Cap + Index")
    st.write(f"**Suggested MF Mix:** {mf_mix}")
    st.write(f"**Required SIP:** {fmt_inr(req_sip)}")
    st.write(f"**Annual Surplus:** {fmt_inr(annual_surplus)}")

elif module == "Boardroom Client Summary":
    st.subheader("🏛️ Boardroom Client Summary")
    client_name = st.text_input("Client Name", "Premium Client")
    annual_income = st.number_input("Annual Income (₹)", 0.0, 1e10, 1800000.0, 50000.0)
    annual_expense = st.number_input("Annual Expense (₹)", 0.0, 1e10, 900000.0, 50000.0)
    networth = st.number_input("Current Net Worth (₹)", 0.0, 1e10, 5000000.0, 100000.0)
    annual_surplus = max(annual_income - annual_expense, 0)
    st.metric("Annual Surplus", fmt_inr(annual_surplus))
    st.metric("Net Worth", fmt_inr(networth))

elif module == "Advisor Meeting Script":
    st.subheader("🎤 Advisor Meeting Script")
    client_name = st.text_input("Client Name", "Premium Client")
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    script = f"Good morning {client_name}. Today we review your income, expenses, net worth, risk profile and create a goal-linked plan for {goal}. We will close protection gaps, align SIP strategy, and build a full family-office roadmap across protection, goals, retirement and lifestyle aspirations."
    st.text_area("Advisor Script", script, height=180)

elif module == "Export Center":
    st.subheader("📤 Export Center")
    export_data = {"generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "clients": st.session_state.clients, "leads": st.session_state.leads}
    json_str = json.dumps(export_data, indent=2)
    st.download_button("⬇️ Download Session Data (JSON)", data=json_str, file_name="wealthy_freedom_v19_1_export.json", mime="application/json")
    st.code(json_str[:5000])

st.divider()
st.caption("Wealthy | FINAL Freedom ULTRA PRO V19.1 SIGNATURE PRIVATE BANK EMPEROR FULL CLEAN SINGLE app.py • Full clean flagship build • Lifestyle planners with year-wise tables • Step-up comparison chart • Executive PDFs • Install: pip install streamlit pandas matplotlib reportlab")
