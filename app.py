import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO
from datetime import datetime

# Optional PDF parser for CAS PDF module
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

/* Main header */
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

/* Cards */
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

/* Buttons */
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

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111827;
}

/* Text */
label, .stMarkdown, .stText, .stCaption {
    color: #E5E7EB !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 10px;
}

/* Tables */
thead tr th {
    background-color: #2563EB !important;
    color: white !important;
}

tbody tr td {
    color: #E5E7EB !important;
}

/* Divider */
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

def go(page_name):
    st.session_state.page = page_name

# =====================================================
# HELPER FUNCTIONS
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

def monthly_sip_required_stepup(target, annual_return, years, step_up):
    months = int(max(years, 0) * 12)
    if months <= 0:
        return 0
    r = annual_return / 12
    g = step_up
    low, high = 0, target
    for _ in range(80):
        mid = (low + high) / 2
        corpus = 0
        sip = mid
        for m in range(1, months + 1):
            corpus = corpus * (1 + r) + sip
            if m % 12 == 0:
                sip *= (1 + g)
        if corpus >= target:
            high = mid
        else:
            low = mid
    return high

def lumpsum_required(target, annual_return, years):
    if years <= 0:
        return target
    return target / ((1 + annual_return) ** years)

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
        f'''
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

def back_button():
    st.button("⬅ Back", on_click=lambda: go("home"))

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
        st.button("Children Planner Pro", on_click=lambda: go("children"))
        st.button("Car Purchase Planner", on_click=lambda: go("car"))
        st.button("House Planning", on_click=lambda: go("house"))

    with c2:
        st.button("SWP Calculator", on_click=lambda: go("swp"))
        st.button("Retirement Planner", on_click=lambda: go("retirement"))
        st.button("Term Insurance", on_click=lambda: go("term"))
        st.button("Cashflow Planner", on_click=lambda: go("cashflow"))

    with c3:
        st.button("Portfolio Allocation", on_click=lambda: go("portfolio"))
        st.button("Net Worth Dashboard", on_click=lambda: go("networth"))
        st.button("Goal Feasibility", on_click=lambda: go("goal"))
        st.button("Portfolio Rebalancing", on_click=lambda: go("rebalance"))

    with c4:
        st.button("Retirement Monte Carlo", on_click=lambda: go("mc_retirement"))
        st.button("MF Portfolio + XIRR", on_click=lambda: go("mf_xirr"))
        st.button("CAS PDF + XIRR", on_click=lambda: go("cas_pdf"))
        st.button("iPhone Purchase Planner", on_click=lambda: go("iphone"))

    st.markdown("---")
    st.caption("Freedom Wealth Platform | Client-Facing Advisory Dashboard")

# =====================================================
# PART 2 MODULES WILL COME BELOW THIS LINE
# =====================================================
# SIP CALCULATOR
# =====================================================
if st.session_state.page == "sip":
    back_button()
    st.subheader("SIP Calculator")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        monthly_sip = st.number_input("Monthly SIP (₹)", 0, 100000000, 5000)
    with c2:
        years = st.number_input("Investment Period (Years)", 1, 60, 10)
    with c3:
        sip_return = st.number_input("Expected Return (%)", 0.0, 30.0, float(expected_return * 100)) / 100
    with c4:
        step_up = st.number_input("Annual Step-up (%)", 0.0, 50.0, 10.0) / 100

    months = years * 12
    monthly_rate = sip_return / 12

    corpus = 0
    total_invested = 0
    current_monthly_sip = monthly_sip
    table = []

    for y in range(1, years + 1):
        yearly_invested = 0
        for m in range(12):
            corpus = corpus * (1 + monthly_rate) + current_monthly_sip
            yearly_invested += current_monthly_sip
            total_invested += current_monthly_sip
        gain = corpus - total_invested
        table.append([
            y,
            round(current_monthly_sip, 0),
            round(yearly_invested, 0),
            round(total_invested, 0),
            round(gain, 0),
            round(corpus, 0)
        ])
        current_monthly_sip *= (1 + step_up)

    df = pd.DataFrame(
        table,
        columns=[
            "Year",
            "Monthly SIP (₹)",
            "Yearly Investment (₹)",
            "Total Invested (₹)",
            "Total Gain (₹)",
            "Year End Corpus (₹)"
        ]
    )

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total Invested", fmt(total_invested))
    with k2:
        st.metric("Total Gain", fmt(corpus - total_invested))
    with k3:
        st.metric("Final Corpus", fmt(corpus))

    st.dataframe(df, use_container_width=True)

# =====================================================
# SWP CALCULATOR (PRO)
# =====================================================
if st.session_state.page == "swp":
    back_button()
    st.subheader("SWP Calculator Pro")

    c1, c2, c3 = st.columns(3)
    with c1:
        initial_corpus = st.number_input("Initial Corpus (₹)", 0, 1000000000, 10000000)
    with c2:
        swp_entry_age = st.number_input("SWP Entry Age", 18, 100, current_age)
    with c3:
        withdrawal_start_age = st.number_input("Withdrawal Start Age", 18, 100, max(current_age + 5, 60))

    c4, c5, c6 = st.columns(3)
    with c4:
        withdrawal_end_age = st.number_input("Withdrawal End Age", withdrawal_start_age, 110, 80)
    with c5:
        withdrawal_per_year = st.number_input("Withdrawal Per Year (₹)", 0, 100000000, 1200000)
    with c6:
        swp_return = st.number_input("Expected Return in SWP (%)", 0.0, 25.0, float(expected_return * 100)) / 100

    c7, c8, c9 = st.columns(3)
    with c7:
        increasing_withdrawal = st.number_input("Yearly Increase in Withdrawal (%)", 0.0, 25.0, 5.0) / 100
    with c8:
        inflation_adjusted = st.selectbox("Inflation Adjusted Withdrawal?", ["No", "Yes"])
    with c9:
        monte_carlo_runs = st.number_input("Monte Carlo Runs", 100, 5000, 500, step=100)

    years_to_start = max(withdrawal_start_age - swp_entry_age, 0)
    total_years = max(withdrawal_end_age - swp_entry_age + 1, 1)

    balance = initial_corpus
    table = []

    # Growth before withdrawal starts
    for age in range(swp_entry_age, withdrawal_start_age):
        opening = balance
        withdrawal = 0
        balance = balance * (1 + swp_return)
        table.append([
            age,
            round(opening, 0),
            round(withdrawal, 0),
            round(balance, 0)
        ])

    # Withdrawal phase
    current_withdrawal = withdrawal_per_year
    for age in range(withdrawal_start_age, withdrawal_end_age + 1):
        opening = balance

        if inflation_adjusted == "Yes":
            effective_withdrawal = current_withdrawal * ((1 + inflation) ** (age - withdrawal_start_age))
        else:
            effective_withdrawal = current_withdrawal

        balance = balance * (1 + swp_return) - effective_withdrawal
        table.append([
            age,
            round(opening, 0),
            round(effective_withdrawal, 0),
            round(balance, 0)
        ])

        current_withdrawal *= (1 + increasing_withdrawal)

        if balance <= 0:
            break

    swp_df = pd.DataFrame(
        table,
        columns=["Age", "Opening Corpus (₹)", "Withdrawal Per Year (₹)", "Year End Corpus (₹)"]
    )

    # Safe withdrawal rate
    swr = (withdrawal_per_year / initial_corpus) * 100 if initial_corpus > 0 else 0

    # Monte Carlo survival
    survival = 0
    np.random.seed(42)
    for _ in range(monte_carlo_runs):
        mc_balance = initial_corpus
        mc_current_withdrawal = withdrawal_per_year

        # pre-withdrawal
        for _age in range(swp_entry_age, withdrawal_start_age):
            rand_ret = np.random.normal(swp_return, 0.08)
            mc_balance = mc_balance * (1 + rand_ret)

        # withdrawal phase
        survived = True
        for _age in range(withdrawal_start_age, withdrawal_end_age + 1):
            rand_ret = np.random.normal(swp_return, 0.08)

            if inflation_adjusted == "Yes":
                eff_w = mc_current_withdrawal * ((1 + inflation) ** (_age - withdrawal_start_age))
            else:
                eff_w = mc_current_withdrawal

            mc_balance = mc_balance * (1 + rand_ret) - eff_w
            mc_current_withdrawal *= (1 + increasing_withdrawal)

            if mc_balance <= 0:
                survived = False
                break

        if survived:
            survival += 1

    survival_prob = (survival / monte_carlo_runs) * 100 if monte_carlo_runs > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Final Corpus", fmt(max(balance, 0)))
    with k2:
        st.metric("Safe Withdrawal Rate", f"{swr:.2f}%")
    with k3:
        st.metric("Retirement Survival %", f"{survival_prob:.1f}%")
    with k4:
        st.metric("Years Covered", f"{len(swp_df)}")

    st.dataframe(swp_df, use_container_width=True)

# =====================================================
# CHILDREN PLANNER PRO
# =====================================================
if st.session_state.page == "children":
    back_button()
    st.subheader("Children Planner Pro")

    num_children = st.number_input("Number of Children", 1, 4, 1)

    all_rows = []

    goal_defaults = [
        ("10th Board", 15, 300000),
        ("12th Board", 17, 500000),
        ("Graduation", 21, 2000000),
        ("Masters", 24, 2500000),
        ("Marriage", 28, 3000000),
    ]

    for i in range(1, num_children + 1):
        st.markdown(f"### Child {i}")
        child_age = st.number_input(f"Current Age - Child {i}", 0, 25, 2, key=f"child_age_{i}")

        for goal_name, default_age, default_cost in goal_defaults:
            c1, c2 = st.columns(2)
            with c1:
                goal_age = st.number_input(
                    f"{goal_name} Age - Child {i}",
                    child_age,
                    40,
                    default_age,
                    key=f"{goal_name}_age_{i}"
                )
            with c2:
                goal_cost = st.number_input(
                    f"{goal_name} Current Cost (₹) - Child {i}",
                    0,
                    100000000,
                    default_cost,
                    key=f"{goal_name}_cost_{i}"
                )

            years_left = max(goal_age - child_age, 0)
            future_cost = future_value(goal_cost, inflation, years_left)
            sip_req = monthly_sip_required(future_cost, expected_return, years_left)
            lump_req = lumpsum_required(future_cost, expected_return, years_left)

            # Simple probability heuristic
            if years_left >= 10:
                prob = 95
            elif years_left >= 5:
                prob = 85
            else:
                prob = 70

            all_rows.append([
                f"Child {i}",
                goal_name,
                goal_age,
                round(future_cost, 0),
                round(sip_req, 0),
                round(lump_req, 0),
                prob
            ])

    child_df = pd.DataFrame(
        all_rows,
        columns=[
            "Child",
            "Goal",
            "Goal Age",
            "Future Cost (₹)",
            "Monthly SIP Required (₹)",
            "Lumpsum Required Today (₹)",
            "Success Probability %"
        ]
    )

    total_sip = child_df["Monthly SIP Required (₹)"].sum()
    total_lumpsum = child_df["Lumpsum Required Today (₹)"].sum()

    k1, k2 = st.columns(2)
    with k1:
        st.metric("Total SIP Required", fmt(total_sip))
    with k2:
        st.metric("Total Lumpsum Required Today", fmt(total_lumpsum))

    st.dataframe(child_df, use_container_width=True)

# =====================================================
# RETIREMENT PLANNER
# =====================================================
if st.session_state.page == "retirement":
    back_button()
    st.subheader("Retirement Planner")

    c1, c2, c3 = st.columns(3)
    with c1:
        retirement_age = st.number_input("Retirement Age", current_age + 1, 80, 60)
    with c2:
        life_expectancy = st.number_input("Plan Till Age", retirement_age + 1, 100, 90)
    with c3:
        retirement_return = st.number_input("Post-Retirement Return (%)", 0.0, 20.0, 8.0) / 100

    st.markdown("### Current Annual Expense (Today's Value)")
    annual_expense_today = st.number_input("Annual Expense Today (₹)", 0, 100000000, monthly_expense_global * 12)

    st.markdown("### Current Retirement Assets")
    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        equity_ret = st.number_input("Equity (₹)", 0, 1000000000, 1000000)
    with rc2:
        debt_ret = st.number_input("Debt (₹)", 0, 1000000000, 1000000)
    with rc3:
        gold_ret = st.number_input("Gold (₹)", 0, 1000000000, 0)
    with rc4:
        other_ret = st.number_input("Other (₹)", 0, 1000000000, 0)

    current_ret_corpus = equity_ret + debt_ret + gold_ret + other_ret

    years_to_ret = retirement_age - current_age
    retirement_years = life_expectancy - retirement_age

    expense_at_ret = annual_expense_today * ((1 + inflation) ** years_to_ret)
    future_existing = current_ret_corpus * ((1 + expected_return) ** years_to_ret)

    if retirement_return > inflation:
        required_corpus = expense_at_ret * (
            (1 - ((1 + inflation) / (1 + retirement_return)) ** retirement_years)
            / (retirement_return - inflation)
        )
    else:
        required_corpus = expense_at_ret * retirement_years

    gap = max(required_corpus - future_existing, 0)
    sip_needed = monthly_sip_required(gap, expected_return, years_to_ret)

    summary = pd.DataFrame({
        "Metric": [
            "Expense at Retirement",
            "Future Value of Existing Corpus",
            "Required Retirement Corpus",
            "Retirement Gap",
            "Required Monthly SIP"
        ],
        "Value": [
            fmt(expense_at_ret),
            fmt(future_existing),
            fmt(required_corpus),
            fmt(gap),
            fmt(sip_needed)
        ]
    })

    st.table(summary)

# =====================================================
# TERM INSURANCE
# =====================================================
if st.session_state.page == "term":
    back_button()
    st.subheader("Term Insurance Calculator")

    c1, c2, c3 = st.columns(3)
    with c1:
        annual_income = st.number_input("Annual Income (₹)", 0, 100000000, monthly_income_global * 12)
    with c2:
        annual_expense = st.number_input("Annual Expense (₹)", 0, 100000000, monthly_expense_global * 12)
    with c3:
        cover_till_age = st.number_input("Coverage Till Age", current_age + 1, 100, 60)

    liabilities = st.number_input("Outstanding Liabilities (₹)", 0, 1000000000, 0)
    existing_cover = st.number_input("Existing Insurance Cover (₹)", 0, 1000000000, 0)

    income_replacement_years = max(cover_till_age - current_age, 0)
    human_life_value = max((annual_income - annual_expense), 0) * income_replacement_years
    recommended_cover = max(human_life_value + liabilities - existing_cover, 0)

    st.metric("Recommended Additional Term Cover", fmt(recommended_cover))

# =====================================================
# CASHFLOW PLANNER
# =====================================================
if st.session_state.page == "cashflow":
    back_button()
    st.subheader("Cashflow Planner")

    st.markdown("### CASH INFLOWS")
    i1, i2, i3, i4 = st.columns(4)
    with i1:
        salary = st.number_input("Salary / Wages (₹)", 0, 100000000, 1000000)
    with i2:
        side_hustle = st.number_input("Side Hustle / Freelance (₹)", 0, 100000000, 0)
    with i3:
        investment_income = st.number_input("Investment Income (₹)", 0, 100000000, 0)
    with i4:
        other_income = st.number_input("Other Income (₹)", 0, 100000000, 0)

    total_inflow = salary + side_hustle + investment_income + other_income

    st.markdown("### CASH OUTFLOWS - Fixed Expenses")
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        rent = st.number_input("Rent / Mortgage (₹)", 0, 100000000, 300000)
    with f2:
        utilities = st.number_input("Utilities (₹)", 0, 100000000, 60000)
    with f3:
        debt_payments = st.number_input("Debt Payments (₹)", 0, 100000000, 0)
    with f4:
        insurance = st.number_input("Insurance (₹)", 0, 100000000, 50000)
    with f5:
        childcare = st.number_input("Childcare / Alimony (₹)", 0, 100000000, 0)

    st.markdown("### CASH OUTFLOWS - Variable Expenses")
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        groceries = st.number_input("Groceries (₹)", 0, 100000000, 120000)
    with v2:
        dining = st.number_input("Dining / Entertainment (₹)", 0, 100000000, 60000)
    with v3:
        transport = st.number_input("Transportation / Fuel (₹)", 0, 100000000, 50000)
    with v4:
        shopping = st.number_input("Shopping / Subscriptions (₹)", 0, 100000000, 50000)

    st.markdown("### CASH OUTFLOWS - Savings & Investments")
    s1, s2, s3 = st.columns(3)
    with s1:
        emergency = st.number_input("Emergency Fund Savings (₹)", 0, 100000000, 50000)
    with s2:
        retirement_contrib = st.number_input("Retirement Contributions (₹)", 0, 100000000, 100000)
    with s3:
        investments = st.number_input("Investments (MF / Stocks / Others) (₹)", 0, 100000000, 150000)

    total_outflow = (
        rent + utilities + debt_payments + insurance + childcare +
        groceries + dining + transport + shopping +
        emergency + retirement_contrib + investments
    )

    net_cashflow = total_inflow - total_outflow
    savings_rate = (net_cashflow / total_inflow * 100) if total_inflow > 0 else 0

    cashflow_df = pd.DataFrame([
        ["CASH INFLOWS", "Salary / Wages", salary],
        ["CASH INFLOWS", "Side Hustle / Freelance", side_hustle],
        ["CASH INFLOWS", "Investment Income", investment_income],
        ["CASH INFLOWS", "Other Income", other_income],
        ["CASH INFLOWS", "Total Inflow (A)", total_inflow],
        ["FIXED EXPENSES", "Rent / Mortgage", rent],
        ["FIXED EXPENSES", "Utilities", utilities],
        ["FIXED EXPENSES", "Debt Payments", debt_payments],
        ["FIXED EXPENSES", "Insurance", insurance],
        ["FIXED EXPENSES", "Childcare / Alimony", childcare],
        ["VARIABLE EXPENSES", "Groceries", groceries],
        ["VARIABLE EXPENSES", "Dining / Entertainment", dining],
        ["VARIABLE EXPENSES", "Transportation / Fuel", transport],
        ["VARIABLE EXPENSES", "Shopping / Subscriptions", shopping],
        ["SAVINGS & INVESTMENTS", "Emergency Fund Savings", emergency],
        ["SAVINGS & INVESTMENTS", "Retirement Contributions", retirement_contrib],
        ["SAVINGS & INVESTMENTS", "Investments", investments],
        ["TOTAL OUTFLOW", "Total Outflow (B)", total_outflow],
        ["NET CASH FLOW", "Total Inflow (A) – Total Outflow (B)", net_cashflow],
    ], columns=["Category", "Item", "Amount (₹)"])

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total Inflow", fmt(total_inflow))
    with k2:
        st.metric("Total Outflow", fmt(total_outflow))
    with k3:
        st.metric("Net Cash Flow", fmt(net_cashflow))

    st.metric("Savings Rate", f"{savings_rate:.1f}%")
    st.dataframe(cashflow_df, use_container_width=True)

# =====================================================
# CAR PURCHASE PLANNER
# =====================================================
if st.session_state.page == "car":
    back_button()
    st.subheader("Car Purchase Planner")

    c1, c2, c3 = st.columns(3)
    with c1:
        car_cost = st.number_input("Car Cost (₹)", 0, 100000000, 1500000)
    with c2:
        down_payment = st.number_input("Down Payment Available (₹)", 0, 100000000, 300000)
    with c3:
        buy_after_years = st.number_input("Purchase After (Years)", 1, 20, 3)

    future_car_cost = future_value(car_cost, inflation, buy_after_years)
    funding_gap = max(future_car_cost - down_payment, 0)
    sip_needed = monthly_sip_required(funding_gap, expected_return, buy_after_years)
    lump_needed = lumpsum_required(funding_gap, expected_return, buy_after_years)

    st.table(pd.DataFrame({
        "Metric": ["Future Car Cost", "Funding Gap", "Monthly SIP Required", "Lumpsum Required Today"],
        "Value": [fmt(future_car_cost), fmt(funding_gap), fmt(sip_needed), fmt(lump_needed)]
    }))

# =====================================================
# HOUSE PLANNING
# =====================================================
if st.session_state.page == "house":
    back_button()
    st.subheader("House Planning")

    c1, c2, c3 = st.columns(3)
    with c1:
        house_cost = st.number_input("House Cost Today (₹)", 0, 1000000000, 10000000)
    with c2:
        available_down = st.number_input("Available Down Payment (₹)", 0, 1000000000, 2000000)
    with c3:
        buy_house_after = st.number_input("Buy House After (Years)", 1, 30, 5)

    future_house_cost = future_value(house_cost, inflation, buy_house_after)
    target_down = future_house_cost * 0.20
    gap_down = max(target_down - available_down, 0)
    sip_needed = monthly_sip_required(gap_down, expected_return, buy_house_after)

    st.table(pd.DataFrame({
        "Metric": ["Future House Cost", "20% Down Payment Target", "Down Payment Gap", "Monthly SIP Required"],
        "Value": [fmt(future_house_cost), fmt(target_down), fmt(gap_down), fmt(sip_needed)]
    }))

# =====================================================
# PORTFOLIO ALLOCATION
# =====================================================
if st.session_state.page == "portfolio":
    back_button()
    st.subheader("Portfolio Allocation")

    total_invest = st.number_input("Total Investible Corpus (₹)", 0, 1000000000, 10000000)
    risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])

    if risk == "Conservative":
        eq, debt, gold = 30, 60, 10
    elif risk == "Moderate":
        eq, debt, gold = 60, 30, 10
    else:
        eq, debt, gold = 75, 15, 10

    alloc_df = pd.DataFrame({
        "Asset Class": ["Equity", "Debt", "Gold"],
        "Allocation %": [eq, debt, gold],
        "Amount (₹)": [total_invest * eq / 100, total_invest * debt / 100, total_invest * gold / 100]
    })

    st.dataframe(alloc_df, use_container_width=True)

# =====================================================
# NET WORTH DASHBOARD
# =====================================================
if st.session_state.page == "networth":
    back_button()
    st.subheader("Net Worth Dashboard")

    st.markdown("### Assets")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        mf_assets = st.number_input("Mutual Funds (₹)", 0, 1000000000, 2000000)
    with a2:
        equity_assets = st.number_input("Direct Equity (₹)", 0, 1000000000, 1000000)
    with a3:
        real_estate = st.number_input("Real Estate (₹)", 0, 10000000000, 5000000)
    with a4:
        cash_bank = st.number_input("Cash / Bank (₹)", 0, 1000000000, 500000)

    st.markdown("### Liabilities")
    l1, l2, l3 = st.columns(3)
    with l1:
        home_loan = st.number_input("Home Loan (₹)", 0, 1000000000, 0)
    with l2:
        car_loan = st.number_input("Car Loan (₹)", 0, 1000000000, 0)
    with l3:
        other_loan = st.number_input("Other Loans (₹)", 0, 1000000000, 0)

    total_assets = mf_assets + equity_assets + real_estate + cash_bank
    total_liabilities = home_loan + car_loan + other_loan
    net_worth = total_assets - total_liabilities

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total Assets", fmt(total_assets))
    with k2:
        st.metric("Total Liabilities", fmt(total_liabilities))
    with k3:
        st.metric("Net Worth", fmt(net_worth))

# =====================================================
# GOAL FEASIBILITY
# =====================================================
if st.session_state.page == "goal":
    back_button()
    st.subheader("Goal Feasibility Dashboard")

    goal_target = st.number_input("Goal Target Amount (₹)", 0, 1000000000, 5000000)
    years_left = st.number_input("Years to Goal", 1, 40, 10)
    existing_corpus = st.number_input("Existing Corpus for Goal (₹)", 0, 1000000000, 500000)
    monthly_sip = st.number_input("Current Monthly SIP for Goal (₹)", 0, 100000000, 20000)

    projected = future_value(existing_corpus, expected_return, years_left)

    temp_corpus = projected
    for _ in range(years_left * 12):
        temp_corpus = temp_corpus * (1 + expected_return / 12) + monthly_sip

    shortfall = goal_target - temp_corpus
    feasibility = (temp_corpus / goal_target * 100) if goal_target > 0 else 0

    st.table(pd.DataFrame({
        "Metric": ["Goal Target", "Projected Value", "Funding Shortfall / Surplus", "Goal Feasibility %"],
        "Value": [fmt(goal_target), fmt(temp_corpus), fmt(shortfall), f"{feasibility:.1f}%"]
    }))

# =====================================================
# PORTFOLIO REBALANCING
# =====================================================
if st.session_state.page == "rebalance":
    back_button()
    st.subheader("Portfolio Rebalancing Engine")

    st.markdown("### Current Portfolio")
    c1, c2, c3 = st.columns(3)
    with c1:
        cur_eq = st.number_input("Current Equity (₹)", 0, 1000000000, 600000)
    with c2:
        cur_debt = st.number_input("Current Debt (₹)", 0, 1000000000, 300000)
    with c3:
        cur_gold = st.number_input("Current Gold (₹)", 0, 1000000000, 100000)

    total_port = cur_eq + cur_debt + cur_gold

    st.markdown("### Target Allocation %")
    t1, t2, t3 = st.columns(3)
    with t1:
        tgt_eq = st.number_input("Target Equity %", 0, 100, 60)
    with t2:
        tgt_debt = st.number_input("Target Debt %", 0, 100, 30)
    with t3:
        tgt_gold = st.number_input("Target Gold %", 0, 100, 10)

    rebalance_df = pd.DataFrame({
        "Asset Class": ["Equity", "Debt", "Gold"],
        "Current Amount (₹)": [cur_eq, cur_debt, cur_gold],
        "Target Amount (₹)": [
            total_port * tgt_eq / 100,
            total_port * tgt_debt / 100,
            total_port * tgt_gold / 100
        ]
    })
    rebalance_df["Buy / Sell (₹)"] = rebalance_df["Target Amount (₹)"] - rebalance_df["Current Amount (₹)"]

    st.dataframe(rebalance_df, use_container_width=True)

# =====================================================
# RETIREMENT MONTE CARLO
# =====================================================
if st.session_state.page == "mc_retirement":
    back_button()
    st.subheader("Retirement Monte Carlo Survival Simulator")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        mc_corpus = st.number_input("Retirement Corpus (₹)", 0, 10000000000, 30000000)
    with c2:
        mc_withdrawal = st.number_input("Annual Withdrawal (₹)", 0, 1000000000, 1200000)
    with c3:
        mc_years = st.number_input("Retirement Years", 1, 50, 30)
    with c4:
        mc_runs = st.number_input("Simulation Runs", 100, 5000, 1000, step=100)

    success = 0
    np.random.seed(123)

    for _ in range(mc_runs):
        bal = mc_corpus
        survived = True
        wd = mc_withdrawal

        for y in range(mc_years):
            rand_ret = np.random.normal(expected_return, 0.12)
            bal = bal * (1 + rand_ret) - wd
            wd *= (1 + inflation)
            if bal <= 0:
                survived = False
                break

        if survived:
            success += 1

    survival_pct = (success / mc_runs) * 100 if mc_runs > 0 else 0
    st.metric("Retirement Survival Probability", f"{survival_pct:.1f}%")

# =====================================================
# MF PORTFOLIO + XIRR
# =====================================================
if st.session_state.page == "mf_xirr":
    back_button()
    st.subheader("Mutual Fund Portfolio Upload + XIRR")

    uploaded = st.file_uploader("Upload CSV / Excel (Date, Amount, Type)", type=["csv", "xlsx", "xls"])

    if uploaded is not None:
        try:
            if uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)

            st.write("Uploaded Data Preview")
            st.dataframe(df.head(20), use_container_width=True)

            # Try to auto-detect columns
            cols_lower = {c.lower(): c for c in df.columns}

            date_col = None
            amt_col = None
            type_col = None

            for c in df.columns:
                cl = c.lower()
                if "date" in cl:
                    date_col = c
                if "amount" in cl or "amt" in cl or "value" in cl:
                    amt_col = c
                if "type" in cl or "transaction" in cl or "txn" in cl:
                    type_col = c

            if date_col and amt_col and type_col:
                temp = df.copy()
                temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
                temp[amt_col] = temp[amt_col].apply(clean_amount)
                temp[type_col] = temp[type_col].apply(normalize_txn_type)

                cashflows = []
                current_value = 0

                for _, row in temp.iterrows():
                    if pd.isna(row[date_col]) or pd.isna(row[amt_col]):
                        continue

                    ttype = row[type_col]
                    amt = row[amt_col]

                    if ttype == "Purchase":
                        cashflows.append((row[date_col].date(), -amt))
                    elif ttype == "Redemption":
                        cashflows.append((row[date_col].date(), amt))
                    elif ttype == "Current Value":
                        current_value += amt

                if current_value > 0:
                    cashflows.append((datetime.today().date(), current_value))

                result = xirr(cashflows) if len(cashflows) >= 2 else None

                st.metric("Calculated XIRR", f"{result*100:.2f}%" if result is not None else "Insufficient Data")
                st.metric("Current Portfolio Value", fmt(current_value))
            else:
                st.warning("Could not auto-detect columns. Please keep columns like Date / Amount / Type.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# =====================================================
# CAS PDF + XIRR
# =====================================================
if st.session_state.page == "cas_pdf":
    back_button()
    st.subheader("CAMS / KFintech PDF CAS Parser + XIRR")

    if not PDF_OK:
        st.warning("pdfplumber not installed. Add 'pdfplumber' in requirements.txt")
    else:
        pdf_file = st.file_uploader("Upload CAS PDF", type=["pdf"])

        if pdf_file is not None:
            try:
                text = ""
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        txt = page.extract_text()
                        if txt:
                            text += "\n" + txt

                st.success("PDF text extracted successfully.")
                st.text_area("Extracted Preview", text[:5000], height=250)

                # Very basic pattern-based extraction placeholder
                amounts = re.findall(r"(?:₹|Rs\.?|INR)?\s?([\d,]+\.\d{2}|[\d,]+)", text)
                parsed_amounts = [clean_amount(a) for a in amounts if pd.notna(clean_amount(a))]
                sample_total = sum(parsed_amounts[:20]) if len(parsed_amounts) > 0 else 0

                st.metric("Sample Parsed Amount Total (Preview)", fmt(sample_total))
                st.info("For exact CAS XIRR, use structured transaction export or enhance parser rules fund-wise.")
            except Exception as e:
                st.error(f"PDF parsing error: {e}")

# =====================================================
# iPHONE PURCHASE PLANNER
# =====================================================
if st.session_state.page == "iphone":
    back_button()
    st.subheader("iPhone Purchase Planner")

    c1, c2, c3 = st.columns(3)
    with c1:
        iphone_cost = st.number_input("iPhone Cost Today (₹)", 0, 1000000, 80000)
    with c2:
        buy_after = st.number_input("Buy After (Months)", 1, 60, 12)
    with c3:
        existing_savings = st.number_input("Existing Savings (₹)", 0, 1000000, 10000)

    monthly_inflation = (1 + inflation) ** (1/12) - 1
    future_cost = iphone_cost * ((1 + monthly_inflation) ** buy_after)
    gap = max(future_cost - existing_savings, 0)

    if buy_after > 0:
        r = expected_return / 12
        if r > 0:
            sip_needed = gap / (((1 + r) ** buy_after - 1) / r)
        else:
            sip_needed = gap / buy_after
    else:
        sip_needed = gap

    st.table(pd.DataFrame({
        "Metric": ["Future iPhone Cost", "Funding Gap", "Monthly SIP Required"],
        "Value": [fmt(future_cost), fmt(gap), fmt(sip_needed)]
    }))

# =====================================================
# DEFAULT FALLBACK
# =====================================================
if st.session_state.page not in [
    "home", "sip", "swp", "children", "retirement", "term", "cashflow",
    "car", "house", "portfolio", "networth", "goal", "rebalance",
    "mc_retirement", "mf_xirr", "cas_pdf", "iphone"
]:
    st.session_state.page = "home"

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration / Advisory Discussion Purpose Only")
