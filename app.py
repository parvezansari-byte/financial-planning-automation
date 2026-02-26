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

/* Header */
.header-box {
    background: linear-gradient(90deg, #1E3A8A, #0EA5E9);
    padding: 24px;
    border-radius: 14px;
    text-align: center;
    color: white;
    font-size: 42px;
    font-weight: 700;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.4);
}
.subtitle {
    text-align:center;
    color:#93C5FD;
    font-size:18px;
    margin-top:10px;
    margin-bottom:25px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #2563EB, #0EA5E9);
    color: white;
    border-radius: 8px;
    height: 45px;
    font-weight: 600;
    border: none;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #1D4ED8, #0284C7);
}

/* Table Styling */
thead tr th {
    background-color: #2563EB !important;
    color: white !important;
}
tbody tr td {
    color: #E2E8F0 !important;
}
tbody tr:nth-child(even) {
    background-color: #111827 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}
label { color: #CBD5E1 !important; }

</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE NAVIGATION
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
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0) / 100
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0) / 100

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
        st.button("SIP & Lumpsum Calculator", on_click=lambda: go("sip"))
        st.button("Future Planning for Children", on_click=lambda: go("children"))

    with col2:
        st.button("SWP Calculator", on_click=lambda: go("swp"))
        st.button("Retirement Planner", on_click=lambda: go("retirement"))

    with col3:
        st.button("Term Insurance Calculator", on_click=lambda: go("term"))

# =====================================================
# SIP CALCULATOR
# =====================================================

if st.session_state.page == "sip":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Monthly SIP (₹)", value=5000)
    years = st.number_input("Investment Years", value=10)
    stepup = st.number_input("Annual Step-Up (%)", value=10.0) / 100

    corpus = 0
    table = []

    for y in range(years):
        yearly_sip = monthly_sip * 12 * ((1 + stepup) ** y)
        corpus = (corpus + yearly_sip) * (1 + expected_return)

        table.append([y+1, entry_age+y, yearly_sip, round(corpus,0)])

    df = pd.DataFrame(table, columns=["No.", "Age", "Yearly SIP", "Year End Corpus"])
    st.dataframe(df, use_container_width=True)

    st.success(f"Final Corpus: ₹ {corpus:,.0f}")

# =====================================================
# SWP CALCULATOR
# =====================================================

if st.session_state.page == "swp":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SWP Calculator")

    corpus = st.number_input("Initial Corpus (₹)", value=10000000)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=100000)
    years = st.number_input("Withdrawal Years", value=20)

    balance = corpus
    table = []

    for y in range(years):
        yearly_withdrawal = withdrawal * 12
        balance = balance * (1 + expected_return) - yearly_withdrawal

        table.append([y+1, entry_age+y, yearly_withdrawal, round(balance,0)])

    df = pd.DataFrame(table, columns=["No.", "Age", "Yearly Withdrawal", "Year End Corpus"])
    st.dataframe(df, use_container_width=True)

    if balance > 0:
        st.success(f"Corpus Remaining: ₹ {balance:,.0f}")
    else:
        st.error("⚠ Corpus depleted before selected period")

# =====================================================
# RETIREMENT PLANNER
# =====================================================

if st.session_state.page == "retirement":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    annual_expense = st.number_input("Annual Expense Today (₹)", value=900000)

    years_to_ret = retirement_age - entry_age
    expense_at_ret = future_value(annual_expense, inflation, years_to_ret)
    corpus_required = expense_at_ret * 25

    data = pd.DataFrame({
        "Metric": ["Expense at Retirement", "Corpus Required"],
        "Value": [f"₹ {expense_at_ret:,.0f}", f"₹ {corpus_required:,.0f}"]
    })

    st.table(data)

# =====================================================
# CHILD PLANNER
# =====================================================

if st.session_state.page == "children":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Future Planning for Children")

    child_age = st.number_input("Child Current Age", 0, 18, 2)

    goals = {
        "10th Board": (14, 200000),
        "12th Board": (16, 200000),
        "Graduation": (18, 2000000),
        "Marriage": (24, 2000000)
    }

    table = []

    for name, (goal_age, cost_today) in goals.items():
        years = goal_age - child_age
        future_cost = future_value(cost_today, inflation, years)
        table.append([name, goal_age, round(future_cost,0)])

    df = pd.DataFrame(table, columns=["Milestone", "Age", "Future Cost (₹)"])
    st.dataframe(df, use_container_width=True)

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
st.caption("Disclaimer: For illustration purposes only.")
