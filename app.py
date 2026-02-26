import streamlit as st
import pandas as pd
import numpy as np
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import TableStyle

st.set_page_config(page_title="Premium Wealth Planner", layout="wide")

# =========================================================
# SESSION NAVIGATION
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "index"

def go(page):
    st.session_state.page = page

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div style='background:#6A35A3;padding:18px'>
<h1 style='color:white;text-align:center;'>Investment & Insurance Planner</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# INDEX PAGE
# =========================================================

if st.session_state.page == "index":

    st.subheader("Select Calculator")

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

# =========================================================
# COMMON INPUTS
# =========================================================

entry_age = st.sidebar.number_input("Entry Age", 18, 65, 30)
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0)/100
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0)/100

# =========================================================
# SIP CALCULATOR
# =========================================================

if st.session_state.page == "sip":

    st.button("⬅ Back to Index", on_click=lambda: go("index"))

    st.header("SIP & Lumpsum Calculator")

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

    st.subheader("Wealth Projection Table")
    st.table(df)

    st.success(f"Final Corpus: ₹ {corpus:,.0f}")

# =========================================================
# SWP CALCULATOR
# =========================================================

if st.session_state.page == "swp":

    st.button("⬅ Back to Index", on_click=lambda: go("index"))

    st.header("SWP Calculator")

    corpus = st.number_input("Initial Corpus (₹)", value=10000000)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=100000)
    years = st.number_input("Withdrawal Years", value=20)

    table = []
    balance = corpus

    for y in range(years):
        balance = balance * (1 + expected_return) - (withdrawal * 12)
        table.append([entry_age + y, withdrawal*12, round(balance,0)])

    df = pd.DataFrame(table, columns=["Age","Yearly Withdrawal","Year End Corpus"])

    st.subheader("SWP Projection Table")
    st.table(df)

# =========================================================
# RETIREMENT PLANNER
# =========================================================

if st.session_state.page == "retirement":

    st.button("⬅ Back to Index", on_click=lambda: go("index"))

    st.header("Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    annual_expense = st.number_input("Annual Expense Today (₹)", value=900000)

    years_to_ret = retirement_age - entry_age
    expense_at_ret = annual_expense * (1 + inflation)**years_to_ret
    corpus_required = expense_at_ret * 25

    summary = pd.DataFrame({
        "Metric":["Expense at Retirement","Corpus Required"],
        "Value":[f"₹ {expense_at_ret:,.0f}",f"₹ {corpus_required:,.0f}"]
    })

    st.table(summary)

# =========================================================
# TERM INSURANCE
# =========================================================

if st.session_state.page == "term":

    st.button("⬅ Back to Index", on_click=lambda: go("index"))

    st.header("Term Insurance Calculator")

    annual_income = st.number_input("Annual Income (₹)", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - entry_age
    cover = annual_income * years_left

    st.success(f"Recommended Term Cover: ₹ {cover:,.0f}")

# =========================================================
# CHILD PLANNER
# =========================================================

if st.session_state.page == "children":

    st.button("⬅ Back to Index", on_click=lambda: go("index"))

    st.header("Future Planning for Children")

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
        future_cost = cost_today*(1+inflation)**years
        table.append([name,goal_age,round(future_cost,0)])

    df = pd.DataFrame(table, columns=["Milestone","Age","Future Cost"])

    st.table(df)

# =========================================================
# SIP + SWP
# =========================================================

if st.session_state.page == "sip_swp":

    st.button("⬅ Back to Index", on_click=lambda: go("index"))

    st.header("SIP + SWP Planner")

    sip = st.number_input("Monthly SIP (₹)", value=50000)
    accumulation = st.number_input("Accumulation Years", value=10)
    withdrawal_years = st.number_input("Withdrawal Years", value=15)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=150000)

    corpus = sip * (((1+expected_return)**accumulation -1)/expected_return)

    balance = corpus
    for _ in range(withdrawal_years):
        balance = balance*(1+expected_return)-(withdrawal*12)

    st.success(f"Corpus Built: ₹ {corpus:,.0f}")
    st.info(f"Remaining Corpus: ₹ {balance:,.0f}")

st.markdown("---")
st.caption("Disclaimer: Outputs are illustrative.")
