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
    margin-top:10px;
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
st.markdown('<div class="subtitle">Investment & Insurance Planner</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================================
# SIDEBAR GLOBAL INPUTS
# =====================================================

st.sidebar.header("Client Profile")
entry_age = st.sidebar.number_input("Entry Age", 18, 65, 30)
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0)/100
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0)/100

# =====================================================
# COMMON FUNCTIONS
# =====================================================

def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

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
# SIP CALCULATOR (NEW SEPARATE PAGE)
# =====================================================

if st.session_state.page == "sip":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Monthly SIP (₹)", value=5000)
    years = st.number_input("Investment Years", value=10)
    stepup = st.number_input("Annual Step-Up (%)", value=10.0)/100

    corpus = 0
    table = []

    for y in range(years):
        yearly_sip = monthly_sip * 12 * ((1 + stepup) ** y)
        corpus = (corpus + yearly_sip) * (1 + expected_return)

        table.append([
            y+1,
            entry_age+y,
            round(yearly_sip,0),
            round(corpus,0)
        ])

    df = pd.DataFrame(table, columns=[
        "Year No.",
        "Age",
        "Yearly Investment (₹)",
        "Year End Corpus (₹)"
    ])

    st.dataframe(df, use_container_width=True)
    st.success(f"Final Corpus After {years} Years: ₹ {corpus:,.0f}")

# =====================================================
# CHILDREN PLANNER
# =====================================================

if st.session_state.page == "children":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Children Planner")

    num_children = st.number_input("Number of Children", 1, 4, 1)

    summary = []

    for i in range(num_children):

        st.markdown(f"## Child {i+1}")
        child_age = st.number_input(f"Child {i+1} Age", 0, 18, 2, key=f"child{i}")

        edu_age = st.number_input("Education Age", 15, 30, 18, key=f"edu{i}")
        edu_cost = st.number_input("Education Cost Today (₹)", 2000000, key=f"ec{i}")

        years = edu_age - child_age
        future_cost = future_value(edu_cost, inflation, years)

        summary.append([f"Child {i+1}", edu_age, round(future_cost,0)])

    df = pd.DataFrame(summary, columns=["Child", "Goal Age", "Future Cost (₹)"])
    st.dataframe(df, use_container_width=True)

# =====================================================
# SWP CALCULATOR
# =====================================================

if st.session_state.page == "swp":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SWP Calculator")

    corpus = st.number_input("Initial Corpus (₹)", value=10000000)
    monthly_withdrawal = st.number_input("Monthly Withdrawal (₹)", value=100000)
    years = st.number_input("Withdrawal Years", value=20)

    balance = corpus
    table = []

    for y in range(years):
        withdrawal = monthly_withdrawal * 12
        balance = balance * (1 + expected_return) - withdrawal

        table.append([
            y+1,
            entry_age+y,
            withdrawal,
            round(balance,0)
        ])

    df = pd.DataFrame(table, columns=[
        "Year No.",
        "Age",
        "Yearly Withdrawal (₹)",
        "Year End Corpus (₹)"
    ])

    st.dataframe(df, use_container_width=True)

# =====================================================
# RETIREMENT
# =====================================================

if st.session_state.page == "retirement":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    annual_expense = st.number_input("Annual Expense Today (₹)", value=900000)

    years = retirement_age - entry_age
    expense_at_ret = future_value(annual_expense, inflation, years)
    corpus_required = expense_at_ret * 25

    st.success(f"Required Retirement Corpus: ₹ {corpus_required:,.0f}")

# =====================================================
# TERM INSURANCE
# =====================================================

if st.session_state.page == "term":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance Calculator")

    annual_income = st.number_input("Annual Income (₹)", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - entry_age
    cover = annual_income * years_left

    st.success(f"Recommended Term Cover: ₹ {cover:,.0f}")

st.markdown("---")
st.caption("For illustration purposes only.")
