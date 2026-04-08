# FINAL Freedom ULTRA PRO V8 WEALTHY MASTER SINGLE app.py
# Single-file Streamlit super app for MFD / Financial Planning / CRM / Client Meetings

import streamlit as st
import math
import json
import io
from datetime import datetime
from pathlib import Path

# Optional imports (safe fallback if unavailable)
try:
    import pandas as pd
except Exception:
    pd = None

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

st.set_page_config(page_title="Freedom ULTRA PRO V8 | Wealthy", layout="wide", page_icon="💜")

# ============================================================
# UTILITIES
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
    # approximate via binary search
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

# ============================================================
# SESSION STATE
# ============================================================
if "clients" not in st.session_state:
    st.session_state.clients = []
if "notes" not in st.session_state:
    st.session_state.notes = []

# ============================================================
# THEME / CSS
# ============================================================
st.markdown(
    """
    <style>
    .block-container {padding-top: 0.7rem; padding-bottom: 2rem;}
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 50%, #1e1b4b 100%);
    }
    .hero {
        background: linear-gradient(135deg, #111827 0%, #1e1b4b 50%, #312e81 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 18px 22px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
        margin-bottom: 14px;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ddd6fe;
        margin-bottom: 4px;
    }
    .hero-sub {
        color: #cbd5e1;
        font-size: 0.95rem;
    }
    .tile {
        background: linear-gradient(135deg, rgba(139,92,246,0.12), rgba(99,102,241,0.10));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .small-note {
        color: #94a3b8;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# LOGO
# ============================================================
logo_candidates = [
    Path("wealthy_logo.png"),
    Path("logo.png"),
    Path("image.png"),
    Path("/mnt/data/image.png"),
]
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
# SIDEBAR
# ============================================================
st.sidebar.title("Freedom ULTRA PRO V8")
st.sidebar.caption("WEALTHY MASTER SINGLE VERSION")

module = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Client Profile",
        "Net Worth Tracker",
        "Risk Profiler",
        "SIP Calculator",
        "Lumpsum Calculator",
        "SWP Calculator",
        "Step-Up SIP Planner",
        "Goal Planner",
        "Retirement Planner",
        "Child Education Planner",
        "Marriage Planner",
        "Travel Planner",
        "Car Purchase Planner",
        "iPhone Purchase Planner",
        "EMI / Loan Planner",
        "Insurance Need Analysis",
        "Cashflow Planner",
        "FIRE Planner",
        "MFD CRM Lead Tracker",
        "Export Center",
    ],
)

# ============================================================
# HEADER
# ============================================================
col1, col2 = st.columns([1, 5])
with col1:
    if logo_path:
        st.image(str(logo_path), use_container_width=True)
with col2:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">FINAL Freedom ULTRA PRO V8</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Wealthy Master Single App • MFD Client Meeting Tool • Financial Planning Super App • Premium Purple UI</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ============================================================
# DASHBOARD
# ============================================================
if module == "Dashboard":
    a, b, c, d = st.columns(4)
    a.metric("Version", "V8")
    b.metric("Brand", "Wealthy")
    c.metric("Modules", "21")
    d.metric("Today", datetime.now().strftime("%d-%b-%Y"))

    st.success("Your Wealthy branded MFD client meeting super app is ready.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="tile"><b>Planning Suite</b><br>SIP • Lumpsum • SWP • Step-Up SIP • Goal • Retirement • FIRE</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="tile"><b>Life Goals</b><br>Child • Marriage • Travel • Car • iPhone • EMI • Insurance</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="tile"><b>MFD Tools</b><br>Client Profile • Risk Profile • Net Worth • CRM • Export Center</div>', unsafe_allow_html=True)

    st.markdown("### Client Meeting Flow (Recommended)")
    st.write("1. Client Profile → 2. Net Worth → 3. Risk Profiler → 4. Goal / Retirement → 5. Insurance → 6. Export")

# ============================================================
# CLIENT PROFILE
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

    if st.button("Save Client in Session"):
        st.session_state.clients.append({
            "name": name,
            "age": age,
            "city": city,
            "mobile": mobile,
            "email": email,
            "occupation": occupation,
            "annual_income": annual_income,
            "annual_expense": annual_expense,
            "investable_surplus": investable_surplus,
            "marital": marital,
            "dependents": dependents,
            "notes": notes,
        })
        st.success("Client saved in current session.")

    if st.session_state.clients:
        st.markdown("### Saved Clients (Session)")
        if pd:
            st.dataframe(pd.DataFrame(st.session_state.clients), use_container_width=True)
        else:
            st.write(st.session_state.clients)

# ============================================================
# NET WORTH TRACKER
# ============================================================
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
        labels = ["Equity/MF", "Debt/FD", "EPF/PPF/NPS", "Cash", "Property", "Gold", "Other"]
        values = [equity, fd, epf, cash, property_val, gold, other_assets]
        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%')
        ax.set_title("Asset Allocation Snapshot")
        st.pyplot(fig)

# ============================================================
# RISK PROFILER
# ============================================================
elif module == "Risk Profiler":
    st.subheader("⚖️ Risk Profiler")

    q1 = st.slider("Investment Horizon (1 = <3 yrs, 10 = >15 yrs)", 1, 10, 6)
    q2 = st.slider("Reaction to 20% market fall (1 = panic sell, 10 = buy more)", 1, 10, 5)
    q3 = st.slider("Return expectation vs stability (1 = safety first, 10 = growth first)", 1, 10, 6)
    q4 = st.slider("Experience with market products (1 = none, 10 = expert)", 1, 10, 4)
    q5 = st.slider("Income stability (1 = unstable, 10 = very stable)", 1, 10, 7)

    score = q1 + q2 + q3 + q4 + q5

    if score <= 20:
        profile = "Conservative"
        eq, debt = 20, 80
    elif score <= 35:
        profile = "Moderate"
        eq, debt = 50, 50
    else:
        profile = "Aggressive"
        eq, debt = 75, 25

    st.metric("Risk Score", score)
    st.success(f"Risk Profile: {profile}")
    st.info(f"Indicative Allocation: Equity {eq}% | Debt {debt}%")

# ============================================================
# SIP
# ============================================================
elif module == "SIP Calculator":
    st.subheader("📈 SIP Calculator")
    c1, c2, c3 = st.columns(3)
    with c1:
        sip_amt = st.number_input("Monthly SIP (₹)", min_value=0.0, value=10000.0, step=1000.0)
    with c2:
        ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    with c3:
        years = st.number_input("Years", min_value=1, value=10, step=1)

    fv = future_value_sip(sip_amt, ret, years)
    invested = sip_amt * years * 12
    gain = fv - invested

    a, b, c = st.columns(3)
    a.metric("Total Invested", fmt_inr(invested))
    b.metric("Estimated Value", fmt_inr(fv))
    c.metric("Wealth Gain", fmt_inr(gain))

# ============================================================
# LUMPSUM
# ============================================================
elif module == "Lumpsum Calculator":
    st.subheader("💰 Lumpsum Calculator")
    amt = st.number_input("Investment Amount (₹)", min_value=0.0, value=100000.0, step=10000.0)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    years = st.number_input("Years", min_value=1, value=10, step=1)
    fv = future_value_lumpsum(amt, ret, years)
    gain = fv - amt
    a, b = st.columns(2)
    a.metric("Future Value", fmt_inr(fv))
    b.metric("Gain", fmt_inr(gain))

# ============================================================
# SWP
# ============================================================
elif module == "SWP Calculator":
    st.subheader("🏦 SWP Calculator")
    corpus = st.number_input("Corpus (₹)", min_value=0.0, value=5000000.0, step=100000.0)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=8.0, step=0.5)
    years = st.number_input("Withdrawal Years", min_value=1, value=20, step=1)
    monthly = swp_monthly(corpus, ret, years)
    st.metric("Suggested Monthly SWP", fmt_inr(monthly))

# ============================================================
# STEP-UP SIP
# ============================================================
elif module == "Step-Up SIP Planner":
    st.subheader("🚀 Step-Up SIP Planner")
    goal = st.number_input("Target Corpus (₹)", min_value=0.0, value=10000000.0, step=100000.0)
    years = st.number_input("Years", min_value=1, value=15, step=1)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    stepup = st.number_input("Annual Step-Up (%)", min_value=0.0, value=10.0, step=1.0)

    base_sip = annual_stepup_sip(goal, ret, years, stepup)
    st.metric("Starting Monthly SIP Required", fmt_inr(base_sip))
    st.caption("This SIP increases every year by the chosen step-up percentage.")

# ============================================================
# GOAL PLANNER
# ============================================================
elif module == "Goal Planner":
    st.subheader("🎯 Goal Planner")
    goal_name = st.text_input("Goal Name", "Dream Goal")
    current_cost = st.number_input("Current Cost / Target Today (₹)", min_value=0.0, value=1000000.0, step=50000.0)
    years = st.number_input("Years to Goal", min_value=1, value=10, step=1)
    inflation = st.number_input("Inflation (%)", min_value=0.0, value=6.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)

    future_goal = inflation_adjusted_cost(current_cost, inflation, years)
    sip_req = required_sip_for_goal(future_goal, ret, years)
    lump_req = required_lumpsum_for_goal(future_goal, ret, years)

    a, b, c = st.columns(3)
    a.metric("Future Goal Value", fmt_inr(future_goal))
    b.metric("Required Monthly SIP", fmt_inr(sip_req))
    c.metric("Required Lumpsum Today", fmt_inr(lump_req))

# ============================================================
# RETIREMENT
# ============================================================
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

# ============================================================
# CHILD
# ============================================================
elif module == "Child Education Planner":
    st.subheader("🎓 Child Education Planner")
    current_cost = st.number_input("Current Education Cost (₹)", min_value=0.0, value=2000000.0, step=100000.0)
    years = st.number_input("Years Left", min_value=1, value=15, step=1)
    inflation = st.number_input("Education Inflation (%)", min_value=0.0, value=10.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    future_cost = inflation_adjusted_cost(current_cost, inflation, years)
    sip_req = required_sip_for_goal(future_cost, ret, years)
    st.metric("Future Education Cost", fmt_inr(future_cost))
    st.metric("Required SIP", fmt_inr(sip_req))

# ============================================================
# MARRIAGE
# ============================================================
elif module == "Marriage Planner":
    st.subheader("💍 Marriage Planner")
    current_cost = st.number_input("Current Marriage Budget (₹)", min_value=0.0, value=1500000.0, step=100000.0)
    years = st.number_input("Years Left", min_value=1, value=10, step=1)
    inflation = st.number_input("Marriage Inflation (%)", min_value=0.0, value=8.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    future_cost = inflation_adjusted_cost(current_cost, inflation, years)
    sip_req = required_sip_for_goal(future_cost, ret, years)
    st.metric("Future Marriage Cost", fmt_inr(future_cost))
    st.metric("Required SIP", fmt_inr(sip_req))

# ============================================================
# TRAVEL
# ============================================================
elif module == "Travel Planner":
    st.subheader("✈️ Travel Planner")
    budget = st.number_input("Current Travel Budget (₹)", min_value=0.0, value=300000.0, step=10000.0)
    years = st.number_input("Years Left", min_value=1, value=3, step=1)
    inflation = st.number_input("Travel Inflation (%)", min_value=0.0, value=7.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=10.0, step=0.5)
    future_cost = inflation_adjusted_cost(budget, inflation, years)
    sip_req = required_sip_for_goal(future_cost, ret, years)
    st.metric("Future Travel Budget", fmt_inr(future_cost))
    st.metric("Required SIP", fmt_inr(sip_req))

# ============================================================
# CAR
# ============================================================
elif module == "Car Purchase Planner":
    st.subheader("🚗 Car Purchase Planner")
    car_price = st.number_input("Current Car Price (₹)", min_value=0.0, value=1200000.0, step=50000.0)
    down_payment_pct = st.slider("Down Payment %", 0, 100, 20)
    years_to_buy = st.number_input("Years to Buy", min_value=1, value=3, step=1)
    inflation = st.number_input("Car Inflation (%)", min_value=0.0, value=6.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=10.0, step=0.5)
    future_price = inflation_adjusted_cost(car_price, inflation, years_to_buy)
    down_payment = future_price * down_payment_pct / 100
    sip_req = required_sip_for_goal(down_payment, ret, years_to_buy)
    st.metric("Estimated Future Car Price", fmt_inr(future_price))
    st.metric("Target Down Payment", fmt_inr(down_payment))
    st.metric("Required SIP", fmt_inr(sip_req))

# ============================================================
# IPHONE
# ============================================================
elif module == "iPhone Purchase Planner":
    st.subheader("📱 iPhone Purchase Planner")
    iphone_price = st.number_input("Current iPhone Price (₹)", min_value=0.0, value=80000.0, step=5000.0)
    months = st.number_input("Months to Buy", min_value=1, value=12, step=1)
    inflation = st.number_input("Price Increase (%)", min_value=0.0, value=5.0, step=0.5)
    future_price = iphone_price * ((1 + inflation/100) ** (months / 12))
    monthly_save = safe_div(future_price, months)
    st.metric("Estimated Future Price", fmt_inr(future_price))
    st.metric("Monthly Saving Needed", fmt_inr(monthly_save))

# ============================================================
# EMI
# ============================================================
elif module == "EMI / Loan Planner":
    st.subheader("🏠 EMI / Loan Planner")
    principal = st.number_input("Loan Amount (₹)", min_value=0.0, value=1000000.0, step=50000.0)
    rate = st.number_input("Interest Rate (%)", min_value=0.0, value=9.0, step=0.25)
    years = st.number_input("Tenure (Years)", min_value=1, value=5, step=1)
    monthly_emi = emi(principal, rate, years)
    total_payment = monthly_emi * years * 12
    total_interest = total_payment - principal
    x, y, z = st.columns(3)
    x.metric("Monthly EMI", fmt_inr(monthly_emi))
    y.metric("Total Payment", fmt_inr(total_payment))
    z.metric("Total Interest", fmt_inr(total_interest))

# ============================================================
# INSURANCE
# ============================================================
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

# ============================================================
# CASHFLOW
# ============================================================
elif module == "Cashflow Planner":
    st.subheader("💸 Monthly Cashflow Planner")
    income = st.number_input("Monthly Income (₹)", min_value=0.0, value=100000.0, step=5000.0)
    fixed = st.number_input("Fixed Expenses (₹)", min_value=0.0, value=40000.0, step=5000.0)
    variable = st.number_input("Variable Expenses (₹)", min_value=0.0, value=20000.0, step=5000.0)
    emi_amt = st.number_input("EMIs (₹)", min_value=0.0, value=10000.0, step=5000.0)
    invest = st.number_input("Investments / SIP (₹)", min_value=0.0, value=15000.0, step=5000.0)

    total_outflow = fixed + variable + emi_amt + invest
    surplus = income - total_outflow
    savings_rate = safe_div(invest, income) * 100

    a, b, c = st.columns(3)
    a.metric("Total Outflow", fmt_inr(total_outflow))
    b.metric("Monthly Surplus", fmt_inr(surplus))
    c.metric("Investment Rate", f"{savings_rate:.2f}%")

# ============================================================
# FIRE
# ============================================================
elif module == "FIRE Planner":
    st.subheader("🔥 FIRE Planner")
    annual_expense = st.number_input("Annual Expense (₹)", min_value=0.0, value=600000.0, step=50000.0)
    current_corpus = st.number_input("Current Invested Corpus (₹)", min_value=0.0, value=2000000.0, step=100000.0)
    monthly_investment = st.number_input("Monthly Investment (₹)", min_value=0.0, value=30000.0, step=5000.0)
    annual_return = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)

    fire_target = annual_expense * 25

    # rough estimate by yearly loop
    corpus = current_corpus
    years = 0
    while corpus < fire_target and years < 60:
        corpus = corpus * (1 + annual_return / 100) + (monthly_investment * 12)
        years += 1

    a, b = st.columns(2)
    a.metric("FIRE Target Corpus", fmt_inr(fire_target))
    b.metric("Estimated Years to FIRE", years if years < 60 else ">60")

# ============================================================
# MFD CRM
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

    if st.button("Save Lead Note"):
        st.session_state.notes.append({
            "lead_name": lead_name,
            "source": lead_source,
            "stage": lead_stage,
            "potential_aum": lead_aum,
            "next_action": next_action,
            "next_date": str(next_date),
        })
        st.success("Lead note saved in current session.")

    if st.session_state.notes:
        st.markdown("### Lead Notes (Session)")
        if pd:
            df_notes = pd.DataFrame(st.session_state.notes)
            st.dataframe(df_notes, use_container_width=True)
            st.metric("Total Pipeline AUM", fmt_inr(df_notes["potential_aum"].sum()))
        else:
            st.write(st.session_state.notes)

# ============================================================
# EXPORT CENTER
# ============================================================
elif module == "Export Center":
    st.subheader("📤 Export Center")
    st.markdown("Use this section to download session client / lead data as JSON.")

    export_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "clients": st.session_state.clients,
        "lead_notes": st.session_state.notes,
    }

    json_str = json.dumps(export_data, indent=2)
    st.download_button(
        label="Download Session Data (JSON)",
        data=json_str,
        file_name="wealthy_freedom_v8_session_export.json",
        mime="application/json",
    )

    st.code(json_str[:5000])

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("Wealthy | FINAL Freedom ULTRA PRO V8 WEALTHY MASTER SINGLE app.py • Keep wealthy_logo.png in same folder for best branding • Next upgrade can add PDF report + advanced charts + persistent database.")
