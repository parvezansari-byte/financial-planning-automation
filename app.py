import streamlit as st
import pandas as pd
import numpy as np

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Freedom", layout="wide")

# =====================================================
# DARK FINTECH THEME
# =====================================================
st.markdown("""
<style>
.stApp { background-color: #0F172A; }

.header-box {
    background: linear-gradient(90deg, #1E3A8A, #0EA5E9);
    padding: 24px;
    border-radius: 14px;
    text-align: center;
    color: white;
    font-size: 42px;
    font-weight: 700;
}

.subtitle {
    text-align:center;
    color:#93C5FD;
    font-size:18px;
    margin-bottom:25px;
}

.stButton > button {
    background: linear-gradient(90deg, #2563EB, #0EA5E9);
    color: white;
    border-radius: 8px;
    height: 45px;
    font-weight: 600;
    border: none;
    width: 100%;
    margin-bottom: 8px;
}

thead tr th {
    background-color: #2563EB !important;
    color: white !important;
}

tbody tr td { color: #E2E8F0 !important; }
tbody tr:nth-child(even) { background-color: #111827 !important; }

section[data-testid="stSidebar"] { background-color: #111827; }
label { color: #CBD5E1 !important; }

[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1F2937;
    padding: 10px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION NAVIGATION
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page

# =====================================================
# HEADER
# =====================================================
st.markdown('<div class="header-box">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Integrated Wealth Planning Platform</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================================
# SIDEBAR GLOBAL INPUTS
# =====================================================
st.sidebar.header("Client Profile")

current_age = st.sidebar.number_input("Current Age", 18, 80, 30)
inflation = st.sidebar.number_input("General Inflation (%)", 0.0, 15.0, 6.0) / 100
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 25.0, 12.0) / 100

# =====================================================
# COMMON FUNCTIONS
# =====================================================
def future_value(pv, rate, years):
    return pv * ((1 + rate) ** years)

def sip_required(target, rate, years):
    if years <= 0 or rate <= 0:
        return 0
    return target / (((1 + rate) ** years - 1) / rate)

def monthly_sip_required(target, annual_rate, years):
    months = int(years * 12)
    if months <= 0:
        return 0
    monthly_rate = annual_rate / 12
    if monthly_rate <= 0:
        return target / months
    factor = ((1 + monthly_rate) ** months - 1) / monthly_rate
    return target / factor

def format_inr(x):
    return f"₹ {x:,.0f}"

# =====================================================
# HOME PAGE
# =====================================================
if st.session_state.page == "home":

    st.subheader("Financial Planning Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("SIP Calculator", on_click=lambda: go("sip"))
        st.button("Children Planner", on_click=lambda: go("children"))
        st.button("Car Purchase Planner", on_click=lambda: go("car"))
        st.button("Goal Feasibility", on_click=lambda: go("goal"))

    with col2:
        st.button("SWP Calculator", on_click=lambda: go("swp"))
        st.button("Retirement Planner", on_click=lambda: go("retirement"))
        st.button("iPhone Purchase Planner", on_click=lambda: go("iphone"))
        st.button("Portfolio Rebalancing", on_click=lambda: go("rebalance"))

    with col3:
        st.button("Term Insurance", on_click=lambda: go("term"))
        st.button("Cashflow Planner", on_click=lambda: go("cashflow"))
        st.button("Portfolio Allocation", on_click=lambda: go("portfolio"))
        st.button("Net Worth Dashboard", on_click=lambda: go("networth"))
        st.button("Retirement Monte Carlo", on_click=lambda: go("mc_retirement"))
        st.button("MF Portfolio + XIRR", on_click=lambda: go("mf_xirr"))

# =====================================================
# SIP CALCULATOR
# =====================================================
if st.session_state.page == "sip":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Starting Monthly SIP (₹)", min_value=0, value=5000)
    years = st.number_input("Investment Years", min_value=1, max_value=50, value=10)
    step_up = st.number_input("Annual Step-Up (%)", 0.0, 50.0, 10.0) / 100

    corpus = 0
    invested = 0
    table = []

    current_monthly_sip = monthly_sip

    for y in range(1, years + 1):
        yearly_sip = current_monthly_sip * 12
        invested += yearly_sip
        corpus = (corpus + yearly_sip) * (1 + expected_return)

        table.append([
            y,
            round(current_monthly_sip, 0),
            round(yearly_sip, 0),
            round(invested, 0),
            round(corpus, 0)
        ])

        current_monthly_sip = current_monthly_sip * (1 + step_up)

    df = pd.DataFrame(
        table,
        columns=[
            "Year",
            "Monthly SIP",
            "Yearly Investment",
            "Total Invested",
            "Year End Corpus"
        ]
    )

    st.dataframe(df, use_container_width=True)

    total_gain = corpus - invested

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Invested", format_inr(invested))
    c2.metric("Total Gain", format_inr(total_gain))
    c3.metric("Final Corpus", format_inr(corpus))

# =====================================================
# SWP CALCULATOR (ADVANCED)
# =====================================================
if st.session_state.page == "swp":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SWP Calculator")

    initial_corpus = st.number_input("Initial Corpus (₹)", min_value=0, value=10000000)
    entry_age = st.number_input("Entry Age", min_value=18, max_value=90, value=max(current_age, 30))
    start_age = st.number_input("Withdrawal Start Age", min_value=entry_age, max_value=95, value=max(entry_age, 60))
    end_age = st.number_input("Withdrawal End Age", min_value=start_age + 1, max_value=100, value=min(start_age + 20, 90))

    annual_withdrawal = st.number_input("Withdrawal Per Year (₹)", min_value=0, value=1200000)
    withdrawal_inflation = st.number_input("Withdrawal Increase / Inflation (%)", 0.0, 15.0, 6.0) / 100
    swp_return = st.number_input("Expected Return During SWP (%)", 0.0, 20.0, 8.0) / 100

    # Accumulation phase before withdrawal
    years_before_swp = max(0, start_age - entry_age)
    corpus_at_start = initial_corpus * ((1 + swp_return) ** years_before_swp)

    balance = corpus_at_start
    current_withdrawal = annual_withdrawal
    rows = []

    for age in range(start_age, end_age + 1):
        opening = balance
        growth = opening * swp_return
        closing = opening + growth - current_withdrawal

        if closing < 0:
            closing = 0

        rows.append([
            age,
            round(opening, 0),
            round(growth, 0),
            round(current_withdrawal, 0),
            round(closing, 0)
        ])

        balance = closing
        current_withdrawal = current_withdrawal * (1 + withdrawal_inflation)

        if balance <= 0:
            break

    df = pd.DataFrame(
        rows,
        columns=[
            "Age",
            "Opening Corpus",
            "Growth",
            "Withdrawal",
            "Closing Corpus"
        ]
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Corpus at Withdrawal Start", format_inr(corpus_at_start))
    c2.metric("Years Before SWP", f"{years_before_swp}")
    c3.metric("End Corpus", format_inr(balance))

    st.dataframe(df, use_container_width=True)

    swr = (annual_withdrawal / corpus_at_start * 100) if corpus_at_start > 0 else 0

    if swr <= 4:
        st.success(f"Safe Withdrawal Rate: {swr:.2f}% (Healthy)")
    elif swr <= 6:
        st.warning(f"Safe Withdrawal Rate: {swr:.2f}% (Moderate)")
    else:
        st.error(f"Safe Withdrawal Rate: {swr:.2f}% (Aggressive)")

# =====================================================
# CHILDREN PLANNER PRO
# =====================================================
if st.session_state.page == "children":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Children Planner (Pro)")

    num_children = st.number_input("Number of Children", 1, 4, 1)

    education_inflation = st.number_input("Education Inflation (%)", 0.0, 20.0, 10.0) / 100
    marriage_inflation = st.number_input("Marriage Inflation (%)", 0.0, 20.0, 8.0) / 100

    results = []

    for c in range(num_children):

        st.markdown(f"### Child {c+1}")

        child_age = st.number_input(f"Child {c+1} Current Age", 0, 18, 2, key=f"child_age_{c}")

        goals = {
            "10th Board": (15, education_inflation),
            "12th Board": (17, education_inflation),
            "Graduation": (21, education_inflation),
            "Masters": (24, education_inflation),
            "Marriage": (28, marriage_inflation)
        }

        for goal, (goal_age, infl) in goals.items():

            cost_today = st.number_input(
                f"{goal} Cost Today (₹) - Child {c+1}",
                min_value=0,
                value=2000000,
                key=f"{goal}_{c}"
            )

            years = goal_age - child_age

            if years > 0:
                future_cost = cost_today * ((1 + infl) ** years)
                monthly_sip = monthly_sip_required(future_cost, expected_return, years)
                lumpsum_required = future_cost / ((1 + expected_return) ** years)

                # Monte Carlo probability
                simulations = 300
                success = 0

                for _ in range(simulations):
                    corpus = 0
                    for _yr in range(years):
                        annual_invest = monthly_sip * 12
                        rand_return = np.random.normal(expected_return, 0.15)
                        corpus = (corpus + annual_invest) * (1 + rand_return)

                    if corpus >= future_cost:
                        success += 1

                probability = round((success / simulations) * 100)

                results.append([
                    f"Child {c+1}",
                    goal,
                    goal_age,
                    round(future_cost, 0),
                    round(monthly_sip, 0),
                    round(lumpsum_required, 0),
                    probability
                ])

    if results:
        df = pd.DataFrame(
            results,
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

        st.dataframe(df, use_container_width=True)

        total_sip = df["Monthly SIP Required (₹)"].sum()
        total_lumpsum = df["Lumpsum Required Today (₹)"].sum()

        c1, c2 = st.columns(2)
        c1.metric("Total Monthly SIP Required", format_inr(total_sip))
        c2.metric("Total Lumpsum Required Today", format_inr(total_lumpsum))

# =====================================================
# RETIREMENT PLANNER
# =====================================================
if st.session_state.page == "retirement":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    life_expectancy = st.number_input("Plan Till Age", 70, 100, 90)

    years_to_ret = retirement_age - current_age
    retirement_years = life_expectancy - retirement_age

    st.markdown("### Monthly Expense Breakdown")

    rent = st.number_input("Rent", 0, 1000000, 0)
    grocery = st.number_input("Groceries + Medicine", 0, 1000000, 30000)
    utilities = st.number_input("Utilities", 0, 1000000, 5000)
    discretionary = st.number_input("Discretionary", 0, 1000000, 10000)
    vehicle = st.number_input("Vehicle", 0, 1000000, 10000)

    monthly_expense = rent + grocery + utilities + discretionary + vehicle
    annual_expense = monthly_expense * 12

    st.markdown("### Current Investment Corpus")
    equity = st.number_input("Equity (₹)", min_value=0, value=1000000)
    debt = st.number_input("Debt (₹)", min_value=0, value=1000000)
    total_corpus = equity + debt

    future_existing = total_corpus * ((1 + expected_return) ** years_to_ret)
    expense_at_ret = annual_expense * ((1 + inflation) ** years_to_ret)

    # Conservative retirement corpus method
    post_ret_return = st.number_input("Post-Retirement Return (%)", 0.0, 15.0, 8.0) / 100

    if post_ret_return > inflation:
        required_corpus = expense_at_ret * (
            (1 - ((1 + inflation) / (1 + post_ret_return)) ** retirement_years)
            / (post_ret_return - inflation)
        )
    else:
        required_corpus = expense_at_ret * retirement_years

    gap = max(0, required_corpus - future_existing)
    required_monthly_sip = monthly_sip_required(gap, expected_return, years_to_ret) if years_to_ret > 0 else 0

    summary = pd.DataFrame({
        "Metric": [
            "Annual Expense Today",
            "Expense at Retirement",
            "Future Value of Existing Corpus",
            "Required Retirement Corpus",
            "Retirement Gap"
        ],
        "Value": [
            format_inr(annual_expense),
            format_inr(expense_at_ret),
            format_inr(future_existing),
            format_inr(required_corpus),
            format_inr(gap)
        ]
    })

    st.table(summary)

    c1, c2 = st.columns(2)
    c1.metric("Required Monthly SIP", format_inr(required_monthly_sip))
    c2.metric("Years to Retirement", f"{years_to_ret}")

# =====================================================
# TERM INSURANCE
# =====================================================
if st.session_state.page == "term":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance Calculator")

    annual_income = st.number_input("Annual Income (₹)", min_value=0, value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    liabilities = st.number_input("Outstanding Liabilities (₹)", min_value=0, value=0)
    existing_cover = st.number_input("Existing Insurance Cover (₹)", min_value=0, value=0)

    years_left = max(0, retirement_age - current_age)

    income_replacement = annual_income * years_left
    recommended_cover = max(0, income_replacement + liabilities - existing_cover)

    df = pd.DataFrame({
        "Metric": [
            "Income Replacement Value",
            "Outstanding Liabilities",
            "Existing Cover",
            "Recommended Additional Cover"
        ],
        "Amount": [
            format_inr(income_replacement),
            format_inr(liabilities),
            format_inr(existing_cover),
            format_inr(recommended_cover)
        ]
    })

    st.table(df)
    st.success(f"Recommended Additional Cover: {format_inr(recommended_cover)}")

# =====================================================
# CASHFLOW PLANNER (ADVANCED)
# =====================================================
if st.session_state.page == "cashflow":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Advanced Cashflow Planner")

    plan_till_age = st.number_input("Plan Till Age", 50, 100, 85)

    st.markdown("## CASH INFLOWS")
    salary = st.number_input("Salary / Wages (After-Tax)", value=0)
    side_income = st.number_input("Side Hustle / Freelance", value=0)
    investment_income = st.number_input("Investment Income (Dividends / Interest)", value=0)
    other_income = st.number_input("Other Income (Rental / Refund)", value=0)

    total_inflow = salary + side_income + investment_income + other_income

    st.markdown("## FIXED EXPENSES (Needs)")
    rent = st.number_input("Rent / Mortgage", value=0)
    utilities = st.number_input("Utilities", value=0)
    debt = st.number_input("Debt Payments", value=0)
    insurance = st.number_input("Insurance", value=0)
    childcare = st.number_input("Childcare / Alimony", value=0)

    fixed_total = rent + utilities + debt + insurance + childcare

    st.markdown("## VARIABLE EXPENSES (Wants)")
    groceries = st.number_input("Groceries", value=0)
    dining = st.number_input("Dining / Entertainment", value=0)
    transport = st.number_input("Transportation / Fuel", value=0)
    shopping = st.number_input("Shopping / Subscriptions", value=0)

    variable_total = groceries + dining + transport + shopping

    st.markdown("## SAVINGS & INVESTMENTS")
    emergency = st.number_input("Emergency Fund Savings", value=0)
    retirement_contribution = st.number_input("Retirement Contributions", value=0)
    investments = st.number_input("Investments (Stocks / Mutual Funds / Other)", value=0)

    savings_total = emergency + retirement_contribution + investments

    total_outflow = fixed_total + variable_total + savings_total
    net_cashflow = total_inflow - total_outflow

    summary = pd.DataFrame({
        "Category": [
            "Total Inflow (A)",
            "Total Fixed Expenses",
            "Total Variable Expenses",
            "Total Savings & Investments",
            "Total Outflow (B)",
            "Net Cash Flow (A - B)"
        ],
        "Amount": [
            total_inflow,
            fixed_total,
            variable_total,
            savings_total,
            total_outflow,
            net_cashflow
        ]
    })

    st.dataframe(summary, use_container_width=True)

    if net_cashflow > 0:
        st.success(f"Positive Cashflow: {format_inr(net_cashflow)}")
    elif net_cashflow == 0:
        st.warning("Break-even Cashflow")
    else:
        st.error(f"Cashflow Deficit: {format_inr(abs(net_cashflow))}")

    # Projection
    years = plan_till_age - current_age
    corpus = 0
    projection = []

    for i in range(1, years + 1):
        inflow_adj = total_inflow * ((1 + inflation) ** i)
        outflow_adj = total_outflow * ((1 + inflation) ** i)

        surplus = inflow_adj - outflow_adj
        corpus = corpus * (1 + expected_return) + surplus

        projection.append([
            current_age + i,
            round(inflow_adj, 0),
            round(outflow_adj, 0),
            round(surplus, 0),
            round(corpus, 0)
        ])

    df_projection = pd.DataFrame(
        projection,
        columns=[
            "Age",
            "Inflation Adjusted Inflow",
            "Inflation Adjusted Outflow",
            "Net Surplus",
            "Projected Corpus"
        ]
    )

    st.markdown("### Long-Term Projection")
    st.dataframe(df_projection, use_container_width=True)

# =====================================================
# CAR PURCHASE PLANNER
# =====================================================
if st.session_state.page == "car":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Car Purchase Planner 🚗")

    car_price = st.number_input("Car Price Today (₹)", min_value=0, value=1000000)
    years = st.number_input("Years to Buy Car", min_value=1, max_value=30, value=5)
    car_inflation = st.number_input("Car Price Inflation (%)", 0.0, 15.0, 6.0) / 100

    future_price = car_price * ((1 + car_inflation) ** years)
    monthly_sip = monthly_sip_required(future_price, expected_return, years)
    lumpsum = future_price / ((1 + expected_return) ** years)

    c1, c2, c3 = st.columns(3)
    c1.metric("Future Car Price", format_inr(future_price))
    c2.metric("Required Monthly SIP", format_inr(monthly_sip))
    c3.metric("Lumpsum Required Today", format_inr(lumpsum))

# =====================================================
# IPHONE PURCHASE PLANNER
# =====================================================
if st.session_state.page == "iphone":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("iPhone Purchase Planner 📱")

    iphone_price = st.number_input("iPhone Price Today (₹)", min_value=0, value=120000)
    months = st.number_input("Months to Buy", min_value=1, max_value=60, value=12)

    monthly_rate = expected_return / 12
    future_price = iphone_price * ((1 + inflation) ** (months / 12))

    if monthly_rate > 0:
        sip = future_price / (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        sip = future_price / months

    lumpsum = future_price / ((1 + expected_return) ** (months / 12))

    c1, c2, c3 = st.columns(3)
    c1.metric("Future iPhone Price", format_inr(future_price))
    c2.metric("Monthly Saving Needed", format_inr(sip))
    c3.metric("Lumpsum Required Today", format_inr(lumpsum))

# =====================================================
# PORTFOLIO ALLOCATION
# =====================================================
if st.session_state.page == "portfolio":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Portfolio Allocation")

    total_investment = st.number_input("Total Investment Amount (₹)", min_value=0, value=1000000)

    st.markdown("### Asset Allocation (%)")
    equity_pct = st.slider("Equity %", 0, 100, 50)
    debt_pct = st.slider("Debt %", 0, 100, 30)
    gold_pct = st.slider("Gold %", 0, 100, 10)
    realestate_pct = st.slider("Real Estate %", 0, 100, 5)
    cash_pct = st.slider("Cash / Liquid %", 0, 100, 5)

    total_pct = equity_pct + debt_pct + gold_pct + realestate_pct + cash_pct

    if total_pct != 100:
        st.warning(f"Allocation Total = {total_pct}% (should be 100%)")

    data = {
        "Asset Class": ["Equity", "Debt", "Gold", "Real Estate", "Cash / Liquid"],
        "Allocation %": [equity_pct, debt_pct, gold_pct, realestate_pct, cash_pct],
        "Amount (₹)": [
            total_investment * (equity_pct / 100),
            total_investment * (debt_pct / 100),
            total_investment * (gold_pct / 100),
            total_investment * (realestate_pct / 100),
            total_investment * (cash_pct / 100)
        ]
    }

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

# =====================================================
# NET WORTH DASHBOARD
# =====================================================
if st.session_state.page == "networth":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Net Worth Dashboard")

    st.markdown("### Assets")
    mf = st.number_input("Mutual Funds (₹)", value=0)
    stocks = st.number_input("Stocks (₹)", value=0)
    realestate = st.number_input("Real Estate (₹)", value=0)
    gold = st.number_input("Gold (₹)", value=0)
    cash = st.number_input("Cash / Bank Balance (₹)", value=0)
    other_assets = st.number_input("Other Assets (₹)", value=0)

    total_assets = mf + stocks + realestate + gold + cash + other_assets

    st.markdown("### Liabilities")
    home_loan = st.number_input("Home Loan (₹)", value=0)
    personal_loan = st.number_input("Personal Loan (₹)", value=0)
    car_loan = st.number_input("Car Loan (₹)", value=0)
    credit_card = st.number_input("Credit Card Outstanding (₹)", value=0)
    other_liabilities = st.number_input("Other Liabilities (₹)", value=0)

    total_liabilities = home_loan + personal_loan + car_loan + credit_card + other_liabilities
    networth = total_assets - total_liabilities

    df = pd.DataFrame({
        "Category": ["Total Assets", "Total Liabilities", "Net Worth"],
        "Amount": [total_assets, total_liabilities, networth]
    })

    st.table(df)

    if networth > 0:
        st.success(f"Net Worth: {format_inr(networth)}")
    else:
        st.error("Net Worth Negative – Review liabilities")

# =====================================================
# GOAL FEASIBILITY DASHBOARD
# =====================================================
if st.session_state.page == "goal":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Goal Feasibility Dashboard")

    num_goals = st.number_input("Number of Goals", 1, 10, 3)

    results = []

    for i in range(num_goals):
        st.markdown(f"### Goal {i+1}")

        goal_name = st.text_input(f"Goal Name {i+1}", value=f"Goal {i+1}", key=f"gname{i}")

        target_amount = st.number_input(
            f"Target Amount (₹) - {goal_name}",
            min_value=0,
            value=1000000,
            key=f"gtarget{i}"
        )

        years = st.number_input(
            f"Years to Goal - {goal_name}",
            min_value=1,
            max_value=50,
            value=10,
            key=f"gyears{i}"
        )

        existing_investment = st.number_input(
            f"Existing Investment (₹) - {goal_name}",
            min_value=0,
            value=0,
            key=f"gexist{i}"
        )

        goal_inflation = st.number_input(
            f"Goal Inflation (%) - {goal_name}",
            min_value=0.0,
            max_value=20.0,
            value=6.0,
            key=f"ginfl{i}"
        ) / 100

        future_target = target_amount * ((1 + goal_inflation) ** years)
        future_existing = existing_investment * ((1 + expected_return) ** years)

        gap = max(0, future_target - future_existing)
        req_sip = monthly_sip_required(gap, expected_return, years)

        if gap == 0:
            status = "Fully Funded"
        elif req_sip <= 10000:
            status = "Easy"
        elif req_sip <= 50000:
            status = "Moderate"
        else:
            status = "Stretch"

        results.append([
            goal_name,
            round(future_target),
            round(future_existing),
            round(gap),
            round(req_sip),
            status
        ])

    df = pd.DataFrame(results, columns=[
        "Goal",
        "Future Target (₹)",
        "Future Value of Existing Investment (₹)",
        "Funding Gap (₹)",
        "Required Monthly SIP (₹)",
        "Feasibility"
    ])

    st.dataframe(df, use_container_width=True)

    total_sip = df["Required Monthly SIP (₹)"].sum()
    st.success(f"Total Monthly SIP Needed Across All Goals: {format_inr(total_sip)}")

# =====================================================
# PORTFOLIO REBALANCING ENGINE
# =====================================================
if st.session_state.page == "rebalance":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Portfolio Rebalancing Engine")

    total_portfolio = st.number_input("Total Portfolio Value (₹)", min_value=0, value=1000000)

    st.markdown("### Current Allocation (%)")
    curr_equity = st.slider("Current Equity %", 0, 100, 60, key="ceq")
    curr_debt = st.slider("Current Debt %", 0, 100, 25, key="cdebt")
    curr_gold = st.slider("Current Gold %", 0, 100, 10, key="cgold")
    curr_cash = st.slider("Current Cash %", 0, 100, 5, key="ccash")

    st.markdown("### Target Allocation (%)")
    tgt_equity = st.slider("Target Equity %", 0, 100, 50, key="teq")
    tgt_debt = st.slider("Target Debt %", 0, 100, 30, key="tdebt")
    tgt_gold = st.slider("Target Gold %", 0, 100, 10, key="tgold")
    tgt_cash = st.slider("Target Cash %", 0, 100, 10, key="tcash")

    current_total = curr_equity + curr_debt + curr_gold + curr_cash
    target_total = tgt_equity + tgt_debt + tgt_gold + tgt_cash

    if current_total != 100:
        st.warning(f"Current Allocation Total = {current_total}% (should be 100%)")
    if target_total != 100:
        st.warning(f"Target Allocation Total = {target_total}% (should be 100%)")

    assets = ["Equity", "Debt", "Gold", "Cash"]
    current_pcts = [curr_equity, curr_debt, curr_gold, curr_cash]
    target_pcts = [tgt_equity, tgt_debt, tgt_gold, tgt_cash]

    rows = []

    for asset, cp, tp in zip(assets, current_pcts, target_pcts):
        current_amt = total_portfolio * (cp / 100)
        target_amt = total_portfolio * (tp / 100)
        diff = target_amt - current_amt

        if diff > 0:
            action = f"Buy {format_inr(abs(diff))}"
        elif diff < 0:
            action = f"Sell {format_inr(abs(diff))}"
        else:
            action = "No Change"

        rows.append([
            asset,
            cp,
            tp,
            round(current_amt, 0),
            round(target_amt, 0),
            round(diff, 0),
            action
        ])

    df = pd.DataFrame(rows, columns=[
        "Asset Class",
        "Current %",
        "Target %",
        "Current Amount (₹)",
        "Target Amount (₹)",
        "Rebalancing Amount (₹)",
        "Action"
    ])

    st.dataframe(df, use_container_width=True)
    # =====================================================
# MUTUAL FUND PORTFOLIO UPLOAD + XIRR (AUTO-DETECT CAS)
# =====================================================
if st.session_state.page == "mf_xirr":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Mutual Fund Portfolio Upload + XIRR (Auto-Detect CAS)")

    st.markdown("""
    ### Supported File Types
    - CSV
    - Excel (.xlsx)

    ### Auto-Detects Common CAS / Portfolio Formats
    It will try to identify:
    - Date column
    - Fund / Scheme name
    - Transaction type
    - Amount / Value
    """)

    uploaded_file = st.file_uploader(
        "Upload CAS / Portfolio File",
        type=["csv", "xlsx"],
        key="mf_portfolio_upload"
    )

    # -----------------------------
    # XIRR FUNCTIONS
    # -----------------------------
    def xnpv(rate, cashflows):
        t0 = cashflows[0][0]
        return sum(cf / ((1 + rate) ** ((dt - t0).days / 365.0)) for dt, cf in cashflows)

    def xirr(cashflows):
        low = -0.9999
        high = 10.0

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

    # -----------------------------
    # COLUMN DETECTION
    # -----------------------------
    def normalize_col(col):
        return str(col).strip().lower().replace("_", " ").replace("-", " ")

    def detect_columns(df):
        original_cols = list(df.columns)
        norm_map = {col: normalize_col(col) for col in original_cols}

        date_col = None
        fund_col = None
        txn_col = None
        amount_col = None

        # Possible aliases
        date_aliases = [
            "date", "transaction date", "txn date", "trade date", "posting date"
        ]

        fund_aliases = [
            "fund name", "scheme name", "scheme", "fund", "scheme/fund name", "scheme/fund"
        ]

        txn_aliases = [
            "transaction type", "txn type", "nature", "transaction nature", "type", "txn"
        ]

        amount_aliases = [
            "amount", "transaction amount", "value", "txn amount", "gross amount", "net amount"
        ]

        for col, norm in norm_map.items():
            if any(alias == norm for alias in date_aliases):
                date_col = col
            if any(alias == norm for alias in fund_aliases):
                fund_col = col
            if any(alias == norm for alias in txn_aliases):
                txn_col = col
            if any(alias == norm for alias in amount_aliases):
                amount_col = col

        # fallback partial matching
        if date_col is None:
            for col, norm in norm_map.items():
                if "date" in norm:
                    date_col = col
                    break

        if fund_col is None:
            for col, norm in norm_map.items():
                if "scheme" in norm or "fund" in norm:
                    fund_col = col
                    break

        if txn_col is None:
            for col, norm in norm_map.items():
                if "type" in norm or "nature" in norm or "txn" in norm:
                    txn_col = col
                    break

        if amount_col is None:
            for col, norm in norm_map.items():
                if "amount" in norm or "value" in norm:
                    amount_col = col
                    break

        return date_col, fund_col, txn_col, amount_col

    # -----------------------------
    # TRANSACTION TYPE NORMALIZER
    # -----------------------------
    def normalize_txn_type(x):
        x = str(x).strip().lower()

        purchase_keywords = [
            "purchase", "sip", "purchase sip", "systematic investment",
            "systematic investment plan", "switch in", "allotment", "buy", "investment"
        ]

        redemption_keywords = [
            "redemption", "sell", "switch out", "withdrawal", "redeem"
        ]

        current_value_keywords = [
            "current value", "market value", "current market value", "nav value", "valuation"
        ]

        for kw in purchase_keywords:
            if kw in x:
                return "Purchase"

        for kw in redemption_keywords:
            if kw in x:
                return "Redemption"

        for kw in current_value_keywords:
            if kw in x:
                return "Current Value"

        return "Unknown"

    # -----------------------------
    # PROCESS FILE
    # -----------------------------
    if uploaded_file is not None:

        try:
            # Read file
            if uploaded_file.name.endswith(".csv"):
                raw_df = pd.read_csv(uploaded_file)
            else:
                raw_df = pd.read_excel(uploaded_file)

            st.markdown("### Raw Uploaded Data")
            st.dataframe(raw_df, use_container_width=True)

            # Detect columns
            date_col, fund_col, txn_col, amount_col = detect_columns(raw_df)

            st.markdown("### Auto-Detected Columns")
            detect_df = pd.DataFrame({
                "Field": ["Date", "Fund Name", "Transaction Type", "Amount"],
                "Detected Column": [date_col, fund_col, txn_col, amount_col]
            })
            st.table(detect_df)

            if not all([date_col, fund_col, txn_col, amount_col]):
                st.error("Unable to auto-detect all required columns. Please ensure your file has Date, Fund/Scheme Name, Transaction Type, and Amount/Value.")
            else:
                # Create standardized dataframe
                df = pd.DataFrame()
                df["Date"] = pd.to_datetime(raw_df[date_col], errors="coerce")
                df["Fund Name"] = raw_df[fund_col].astype(str).str.strip()
                df["Transaction Type Raw"] = raw_df[txn_col].astype(str).str.strip()
                df["Transaction Type"] = df["Transaction Type Raw"].apply(normalize_txn_type)
                df["Amount"] = pd.to_numeric(raw_df[amount_col], errors="coerce")

                # Drop invalid rows
                df = df.dropna(subset=["Date", "Fund Name", "Amount"])

                st.markdown("### Standardized Cleaned Data")
                st.dataframe(df, use_container_width=True)

                # Filter unknown separately
                unknown_df = df[df["Transaction Type"] == "Unknown"]

                if not unknown_df.empty:
                    st.warning("Some rows could not be classified and were ignored in XIRR calculations.")
                    st.dataframe(unknown_df, use_container_width=True)

                valid_df = df[df["Transaction Type"] != "Unknown"].copy()

                if valid_df.empty:
                    st.error("No valid transaction rows found after cleaning.")
                else:
                    # -----------------------------
                    # FUND-WISE SUMMARY
                    # -----------------------------
                    fund_summary = []

                    for fund in valid_df["Fund Name"].unique():

                        fund_df = valid_df[valid_df["Fund Name"] == fund].copy()

                        purchases = fund_df[fund_df["Transaction Type"] == "Purchase"]["Amount"].sum()
                        redemptions = fund_df[fund_df["Transaction Type"] == "Redemption"]["Amount"].sum()
                        current_value = fund_df[fund_df["Transaction Type"] == "Current Value"]["Amount"].sum()

                        profit_loss = current_value + redemptions - purchases

                        # Build cashflows
                        cashflows = []

                        for _, row in fund_df.iterrows():
                            txn_type = row["Transaction Type"]

                            if txn_type == "Purchase":
                                cashflows.append((row["Date"], -row["Amount"]))

                            elif txn_type == "Redemption":
                                cashflows.append((row["Date"], row["Amount"]))

                        # Add current value as terminal cashflow
                        if current_value > 0:
                            cashflows.append((pd.Timestamp.today().normalize(), current_value))

                        fund_xirr = None

                        if len(cashflows) >= 2:
                            try:
                                fund_xirr = xirr(cashflows) * 100
                            except:
                                fund_xirr = None

                        fund_summary.append([
                            fund,
                            round(purchases, 0),
                            round(redemptions, 0),
                            round(current_value, 0),
                            round(profit_loss, 0),
                            round(fund_xirr, 2) if fund_xirr is not None else "N/A"
                        ])

                    summary_df = pd.DataFrame(
                        fund_summary,
                        columns=[
                            "Fund Name",
                            "Fund-wise Purchase",
                            "Fund-wise Redemption",
                            "Current Value",
                            "Profit / Loss",
                            "XIRR %"
                        ]
                    )

                    st.markdown("### Fund-wise Portfolio Summary")
                    st.dataframe(summary_df, use_container_width=True)

                    # -----------------------------
                    # PORTFOLIO LEVEL SUMMARY
                    # -----------------------------
                    total_purchase = summary_df["Fund-wise Purchase"].sum()
                    total_redemption = summary_df["Fund-wise Redemption"].sum()
                    total_current = summary_df["Current Value"].sum()
                    total_pl = summary_df["Profit / Loss"].sum()

                    portfolio_cashflows = []

                    for _, row in valid_df.iterrows():
                        txn_type = row["Transaction Type"]

                        if txn_type == "Purchase":
                            portfolio_cashflows.append((row["Date"], -row["Amount"]))

                        elif txn_type == "Redemption":
                            portfolio_cashflows.append((row["Date"], row["Amount"]))

                    if total_current > 0:
                        portfolio_cashflows.append((pd.Timestamp.today().normalize(), total_current))

                    portfolio_xirr = None

                    if len(portfolio_cashflows) >= 2:
                        try:
                            portfolio_xirr = xirr(portfolio_cashflows) * 100
                        except:
                            portfolio_xirr = None

                    c1, c2, c3, c4, c5 = st.columns(5)

                    c1.metric("Total Purchase", f"₹ {total_purchase:,.0f}")
                    c2.metric("Total Redemption", f"₹ {total_redemption:,.0f}")
                    c3.metric("Current Value", f"₹ {total_current:,.0f}")
                    c4.metric("Profit / Loss", f"₹ {total_pl:,.0f}")
                    c5.metric("Portfolio XIRR", f"{portfolio_xirr:.2f}%" if portfolio_xirr is not None else "N/A")

        except Exception as e:
            st.error(f"Error reading or processing file: {e}")

# =====================================================
# RETIREMENT MONTE CARLO SURVIVAL SIMULATOR
# =====================================================
if st.session_state.page == "mc_retirement":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Monte Carlo Survival Simulator")

    initial_corpus = st.number_input("Initial Retirement Corpus (₹)", min_value=0, value=50000000)
    retirement_age = st.number_input("Retirement Start Age", 45, 80, 60)
    life_expectancy = st.number_input("Plan Till Age", 70, 100, 90)

    annual_expense_today = st.number_input("Annual Expense Today (₹)", min_value=0, value=1200000)
    post_ret_inflation = st.number_input("Post-Retirement Inflation (%)", 0.0, 15.0, 6.0) / 100

    mean_return = st.number_input("Expected Return After Retirement (%)", 0.0, 20.0, 8.0) / 100
    std_dev = st.number_input("Volatility / Std Deviation (%)", 0.0, 50.0, 12.0) / 100
    simulations = st.number_input("Number of Simulations", 100, 5000, 1000, step=100)

    years = life_expectancy - retirement_age

    success = 0
    ruin = 0
    sample_path = []
    worst_path = []
    worst_final = float("inf")

    for s in range(simulations):
        corpus = initial_corpus
        annual_expense = annual_expense_today
        path = []

        for y in range(1, years + 1):
            annual_return = np.random.normal(mean_return, std_dev)
            corpus = corpus * (1 + annual_return) - annual_expense

            if corpus < 0:
                corpus = 0

            path.append([
                retirement_age + y,
                round(annual_expense, 0),
                round(corpus, 0)
            ])

            annual_expense = annual_expense * (1 + post_ret_inflation)

            if corpus <= 0:
                break

        if s == 0:
            sample_path = path

        if corpus > 0:
            success += 1
        else:
            ruin += 1

        if corpus < worst_final:
            worst_final = corpus
            worst_path = path

    success_rate = (success / simulations) * 100
    ruin_rate = (ruin / simulations) * 100

    if success_rate >= 85:
        status = "Safe"
    elif success_rate >= 65:
        status = "Moderate"
    else:
        status = "Risky"

    c1, c2, c3 = st.columns(3)
    c1.metric("Success Probability", f"{success_rate:.1f}%")
    c2.metric("Ruin Probability", f"{ruin_rate:.1f}%")
    c3.metric("Retirement Status", status)

    swr = (annual_expense_today / initial_corpus * 100) if initial_corpus > 0 else 0

    if swr <= 4:
        st.success(f"Current Withdrawal Rate: {swr:.2f}% (Healthy)")
    elif swr <= 6:
        st.warning(f"Current Withdrawal Rate: {swr:.2f}% (Moderate)")
    else:
        st.error(f"Current Withdrawal Rate: {swr:.2f}% (Aggressive)")

    st.markdown("### Sample Retirement Survival Path")
    if sample_path:
        df_sample = pd.DataFrame(sample_path, columns=["Age", "Inflation Adjusted Expense", "Corpus Balance"])
        st.dataframe(df_sample, use_container_width=True)

    st.markdown("### Worst Case Path")
    if worst_path:
        df_worst = pd.DataFrame(worst_path, columns=["Age", "Inflation Adjusted Expense", "Corpus Balance"])
        st.dataframe(df_worst, use_container_width=True)

st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration Only")
