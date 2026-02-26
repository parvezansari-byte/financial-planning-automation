import streamlit as st
import pandas as pd
import numpy as np

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(page_title="Freedom", layout="wide")

# ======================================================
# THEME STYLING
# ======================================================

st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #FFF4E6;
}

/* Freedom Header */
.freedom-title {
    background: linear-gradient(90deg, #F97316, #FB923C);
    padding: 22px;
    border-radius: 14px;
    text-align: center;
    color: white;
    font-size: 44px;
    font-weight: 700;
    letter-spacing: 1px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}

/* Subtitle */
.subtitle {
    text-align:center;
    font-size:20px;
    color:#C2410C;
    margin-top:8px;
    margin-bottom:20px;
}

/* Cards */
.card {
    background-color: white;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

/* Buttons */
.stButton > button {
    background-color: #F97316;
    color: white;
    border-radius: 8px;
    height: 45px;
    font-weight: 600;
}

/* Tables */
thead tr th {
    background-color: #F97316 !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# SESSION NAVIGATION
# ======================================================

if "page" not in st.session_state:
    st.session_state.page = "index"

def go(page):
    st.session_state.page = page

# ======================================================
# HEADER
# ======================================================

st.markdown('<div class="freedom-title">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Investment & Insurance Planner</div>', unsafe_allow_html=True)
st.markdown("---")

# ======================================================
# SIDEBAR GLOBAL FILTERS
# ======================================================

st.sidebar.header("Client Profile")

entry_age = st.sidebar.number_input("Entry Age", 18, 65, 30)
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0)/100
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0)/100

# ======================================================
# COMMON FUNCTIONS
# ======================================================

def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

def sip_fv(sip, rate, years):
    return sip * (((1 + rate) ** years - 1) / rate)

# ======================================================
# INDEX PAGE
# ======================================================

if st.session_state.page == "index":

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("SIP & Lumpsum Calculator"):
            go("sip")
        if st.button("Future Planning for Children"):
            go("children")

    with col2:
        if st.button("SWP Calculator"):
            go("swp")
        if st.button("Retirement Planner"):
            go("retirement")

    with col3:
        if st.button("SIP + SWP Planner"):
            go("sip_swp")
        if st.button("Term Insurance Calculator"):
            go("term")

# ======================================================
# SIP CALCULATOR
# ======================================================

if st.session_state.page == "sip":

    st.button("⬅ Back", on_click=lambda: go("index"))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("SIP & Lumpsum Calculator")

    sip = st.number_input("Monthly SIP (₹)", value=5000)
    years = st.number_input("Investment Years", value=20)
    stepup = st.number_input("Annual Step-up (%)", value=10.0)/100

    corpus = 0
    table = []

    for y in range(years):
        yearly_sip = sip * 12 * ((1 + stepup)**y)
        corpus = (corpus + yearly_sip) * (1 + expected_return)
        table.append([entry_age + y, round(yearly_sip,0), round(corpus,0)])

    df = pd.DataFrame(table, columns=["Age","Yearly SIP","Year End Corpus"])

    st.table(df)
    st.success(f"Final Corpus: ₹ {corpus:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# SWP CALCULATOR
# ======================================================

if st.session_state.page == "swp":

    st.button("⬅ Back", on_click=lambda: go("index"))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("SWP Calculator")

    corpus = st.number_input("Initial Corpus (₹)", value=10000000)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=100000)
    years = st.number_input("Withdrawal Years", value=20)

    table = []
    balance = corpus

    for y in range(years):
        balance = balance * (1 + expected_return) - (withdrawal * 12)
        table.append([entry_age + y, withdrawal*12, round(balance,0)])

    df = pd.DataFrame(table, columns=["Age","Yearly Withdrawal","Year End Corpus"])
    st.table(df)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# RETIREMENT PLANNER
# ======================================================

if st.session_state.page == "retirement":

    st.button("⬅ Back", on_click=lambda: go("index"))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    annual_expense = st.number_input("Annual Expense Today (₹)", value=900000)

    years_to_ret = retirement_age - entry_age
    expense_at_ret = future_value(annual_expense, inflation, years_to_ret)
    corpus_required = expense_at_ret * 25

    summary = pd.DataFrame({
        "Metric":["Expense at Retirement","Corpus Required"],
        "Value":[f"₹ {expense_at_ret:,.0f}",f"₹ {corpus_required:,.0f}"]
    })

    st.table(summary)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# CHILD PLANNER
# ======================================================

if st.session_state.page == "children":

    st.button("⬅ Back", on_click=lambda: go("index"))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Future Planning for Children")

    child_age = st.number_input("Child Current Age", 0, 18, 2)

    milestones = {
        "10th Board": (14, 200000),
        "12th Board": (16, 200000),
        "Graduation": (18, 2000000),
        "Marriage": (24, 2000000)
    }

    table = []

    for name,(goal_age,cost_today) in milestones.items():
        years = goal_age - child_age
        future_cost = future_value(cost_today, inflation, years)
        table.append([name,goal_age,round(future_cost,0)])

    df = pd.DataFrame(table, columns=["Milestone","Age","Future Cost"])
    st.table(df)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# SIP + SWP
# ======================================================

if st.session_state.page == "sip_swp":

    st.button("⬅ Back", on_click=lambda: go("index"))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("SIP + SWP Planner")

    sip = st.number_input("Monthly SIP (₹)", value=50000)
    accumulation = st.number_input("Accumulation Years", value=10)
    withdrawal_years = st.number_input("Withdrawal Years", value=15)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=150000)

    corpus = sip_fv(sip, expected_return, accumulation)

    balance = corpus
    for _ in range(withdrawal_years):
        balance = balance*(1+expected_return)-(withdrawal*12)

    st.success(f"Corpus Built: ₹ {corpus:,.0f}")
    st.info(f"Remaining Corpus: ₹ {balance:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# TERM INSURANCE
# ======================================================

if st.session_state.page == "term":

    st.button("⬅ Back", on_click=lambda: go("index"))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Term Insurance Calculator")

    annual_income = st.number_input("Annual Income (₹)", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - entry_age
    cover = annual_income * years_left

    st.success(f"Recommended Term Cover: ₹ {cover:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Disclaimer: This planner is for illustration purposes only.")
