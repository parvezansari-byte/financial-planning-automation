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
}

thead tr th {
    background-color: #2563EB !important;
    color: white !important;
}

tbody tr td { color: #E2E8F0 !important; }
tbody tr:nth-child(even) { background-color: #111827 !important; }

section[data-testid="stSidebar"] { background-color: #111827; }
label { color: #CBD5E1 !important; }
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

current_age = st.sidebar.number_input("Current Age", 25, 70, 30)
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0)/100
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0)/100

# =====================================================
# COMMON FUNCTIONS
# =====================================================
def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

def sip_required(target, rate, years):
    if years <= 0:
        return 0
    return target / (((1 + rate) ** years - 1) / rate)

# =====================================================
# HOME PAGE
# =====================================================
if st.session_state.page == "home":

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("SIP Calculator", on_click=lambda: go("sip"))
        st.button("Children Planner", on_click=lambda: go("children"))

    with col2:
        st.button("SWP Calculator", on_click=lambda: go("swp"))
        st.button("Retirement Planner", on_click=lambda: go("retirement"))

    with col3:
        st.button("Term Insurance", on_click=lambda: go("term"))

# =====================================================
# RETIREMENT PLANNER (FULL DETAIL)
# =====================================================
if st.session_state.page == "retirement":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Advanced Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    life_expectancy = st.number_input("Plan Till Age", 70, 100, 90)

    years_to_ret = retirement_age - current_age
    retirement_years = life_expectancy - retirement_age

    # Expense breakup
    st.markdown("### Monthly Expense Breakdown")
    rent = st.number_input("Rent", 0, 1000000, 0)
    grocery = st.number_input("Groceries + Medicine", 0, 1000000, 30000)
    utilities = st.number_input("Utilities", 0, 1000000, 5000)
    discretionary = st.number_input("Discretionary", 0, 1000000, 10000)
    vehicle = st.number_input("Vehicle", 0, 1000000, 10000)

    monthly_expense = rent + grocery + utilities + discretionary + vehicle
    annual_expense = monthly_expense * 12

    # Current Corpus
    st.markdown("### Current Investment Corpus")
    equity = st.number_input("Equity (₹)", value=1000000)
    debt = st.number_input("Debt (₹)", value=1000000)
    total_corpus = equity + debt

    blended_return = expected_return
    future_existing = total_corpus * ((1 + blended_return) ** years_to_ret)

    expense_at_ret = annual_expense * ((1 + inflation) ** years_to_ret)

    if blended_return > inflation:
        required_corpus = expense_at_ret * (
            (1 - ((1 + inflation)/(1 + blended_return))**retirement_years)
            / (blended_return - inflation)
        )
    else:
        required_corpus = expense_at_ret * retirement_years

    gap = required_corpus - future_existing

    summary = pd.DataFrame({
        "Metric":[
            "Expense at Retirement",
            "Future Value of Existing Corpus",
            "Required Retirement Corpus",
            "Retirement Gap"
        ],
        "Value":[
            f"₹ {expense_at_ret:,.0f}",
            f"₹ {future_existing:,.0f}",
            f"₹ {required_corpus:,.0f}",
            f"₹ {gap:,.0f}"
        ]
    })

    st.table(summary)

    if gap > 0:
        required_sip = sip_required(gap, blended_return, years_to_ret)
        st.success(f"Required Monthly SIP: ₹ {required_sip/12:,.0f}")
    else:
        st.success("Retirement Fully Funded")

# =====================================================
# SIP CALCULATOR
# =====================================================
if st.session_state.page == "sip":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Monthly SIP (₹)", value=5000)
    years = st.number_input("Investment Years", value=10)

    corpus = 0
    total_invested = 0
    table = []

    for y in range(1, years + 1):
        yearly_investment = monthly_sip * 12
        total_invested += yearly_investment
        corpus = (corpus + yearly_investment) * (1 + expected_return)

        table.append([
            y,
            yearly_investment,
            total_invested,
            round(corpus, 0)
        ])

    df = pd.DataFrame(
        table,
        columns=[
            "Year",
            "Yearly Investment",
            "Total Invested",
            "Year End Corpus"
        ]
    )

    st.dataframe(df, use_container_width=True)

    st.success(f"Total Invested: ₹ {total_invested:,.0f}")
    st.success(f"Final Corpus: ₹ {corpus:,.0f}")

# =====================================================
# CHILDREN PLANNER
# =====================================================
if st.session_state.page == "children":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Children Planner")

    num_children = st.number_input("Number of Children", 1, 4, 1)

    summary = []

    for i in range(num_children):

        child_age = st.number_input(f"Child {i+1} Age", 0, 18, 2, key=f"child{i}")

        goals = {
            "10th": 14,
            "12th": 16,
            "Graduation": 18,
            "Masters": 22,
            "Marriage": 24
        }

        for goal, age in goals.items():

            cost = st.number_input(f"{goal} Cost (₹)", value=2000000, key=f"{goal}{i}")

            years = age - child_age
            future_cost = future_value(cost, inflation, years)
            sip = sip_required(future_cost, expected_return, years)

            summary.append([f"Child {i+1}-{goal}", age, round(future_cost,0), round(sip/12,0)])

    df = pd.DataFrame(summary, columns=["Goal", "Age", "Future Cost", "Required SIP"])
    st.dataframe(df, use_container_width=True)

# =====================================================
# SWP CALCULATOR
# =====================================================
if st.session_state.page == "swp":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SWP Calculator")

    corpus = st.number_input("Initial Corpus (₹)", value=10000000)

    withdrawal_start_age = st.number_input("Withdrawal Start Age", 40, 80, 60)
    withdrawal_end_age = st.number_input("Withdrawal End Age", 50, 100, 80)

    withdrawal_per_year = st.number_input("Withdrawal Per Year (₹)", value=1200000)

    balance = corpus
    table = []

    for age in range(withdrawal_start_age, withdrawal_end_age + 1):

        balance = balance * (1 + expected_return) - withdrawal_per_year

        table.append([
            age,
            withdrawal_per_year,
            round(balance, 0)
        ])

        if balance <= 0:
            break

    df = pd.DataFrame(
        table,
        columns=[
            "Age",
            "Withdrawal Per Year",
            "Year End Corpus"
        ]
    )

    st.dataframe(df, use_container_width=True)

    if balance > 0:
        st.success(f"Corpus Survives Till Age {age}")
    else:
        st.error(f"Corpus Exhausted at Age {age}")

# =====================================================
# TERM INSURANCE
# =====================================================
if st.session_state.page == "term":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance Calculator")

    annual_income = st.number_input("Annual Income", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - current_age
    cover = annual_income * years_left

    st.success(f"Recommended Cover: ₹ {cover:,.0f}")

st.markdown("---")
st.caption("Integrated Wealth Platform | For Illustration Only")
