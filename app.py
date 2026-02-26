import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Investment & Insurance Planner", layout="wide")

# =========================================================
# GLOBAL HEADER
# =========================================================

st.markdown("""
    <h1 style='text-align:center; background:#6A35A3; color:white; padding:15px;'>
    Investment & Insurance Planner
    </h1>
""", unsafe_allow_html=True)

# =========================================================
# GLOBAL FILTERS
# =========================================================

st.sidebar.header("Client Profile")

client_name = st.sidebar.text_input("Client Name", "Aditya")
distributor = st.sidebar.text_input("Distributor Name", "Saurabh")

entry_age = st.sidebar.number_input("Entry Age", 18, 70, 30)
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 25.0, 12.0) / 100
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0) / 100

st.sidebar.markdown("---")

tool = st.sidebar.radio(
    "Select Calculator",
    [
        "Index",
        "SIP & Lumpsum Calculator",
        "SWP Calculator",
        "SIP + SWP Planner",
        "Future Planning for Children",
        "Retirement Planner",
        "Term Insurance Calculator"
    ]
)

# =========================================================
# COMMON FUNCTIONS
# =========================================================

def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

def sip_fv(sip, rate, years):
    return sip * (((1 + rate) ** years - 1) / rate)

# =========================================================
# INDEX PAGE
# =========================================================

if tool == "Index":
    st.subheader("Available Tools")

    tools_list = [
        "1️⃣ SIP & Lumpsum Calculator",
        "2️⃣ SWP Calculator",
        "3️⃣ SIP + SWP Planner",
        "4️⃣ Future Planning for Children",
        "5️⃣ Retirement Planner",
        "6️⃣ Term Insurance Calculator"
    ]

    for t in tools_list:
        st.markdown(f"### {t}")

# =========================================================
# 1️⃣ SIP & LUMPSUM
# =========================================================

elif tool == "SIP & Lumpsum Calculator":

    st.header("SIP & Lumpsum Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("SIP")

        sip = st.number_input("Monthly SIP (₹)", value=5000)
        years = st.number_input("Years", value=20)
        stepup = st.number_input("Annual Step Up (%)", value=10.0) / 100

        corpus = 0
        for y in range(years):
            yearly_sip = sip * (1 + stepup) ** y
            corpus += sip_fv(yearly_sip, expected_return, 1)

        st.success(f"SIP Future Value: ₹ {corpus:,.0f}")

    with col2:
        st.subheader("Lumpsum")

        invest = st.number_input("Investment Amount (₹)", value=100000)
        years_l = st.number_input("Investment Period (Years)", value=7)

        fv = future_value(invest, expected_return, years_l)

        st.success(f"Lumpsum Future Value: ₹ {fv:,.0f}")

# =========================================================
# 2️⃣ SWP
# =========================================================

elif tool == "SWP Calculator":

    st.header("SWP Calculator")

    corpus = st.number_input("Current Corpus (₹)", value=10000000)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=125000)
    years = st.number_input("Withdrawal Years", value=20)

    balance = corpus
    data = []

    for y in range(years):
        balance = balance * (1 + expected_return) - (withdrawal * 12)
        data.append(balance)

    st.success(f"Corpus after {years} years: ₹ {balance:,.0f}")
    st.line_chart(data)

# =========================================================
# 3️⃣ SIP + SWP
# =========================================================

elif tool == "SIP + SWP Planner":

    st.header("SIP Accumulation + SWP Distribution")

    sip = st.number_input("Monthly SIP (₹)", value=50000)
    accumulation = st.number_input("Accumulation Years", value=10)
    withdrawal_years = st.number_input("Withdrawal Years", value=15)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=150000)

    corpus = sip_fv(sip, expected_return, accumulation)

    balance = corpus
    for _ in range(withdrawal_years):
        balance = balance * (1 + expected_return) - (withdrawal * 12)

    st.success(f"Corpus Built: ₹ {corpus:,.0f}")
    st.info(f"Balance after withdrawal: ₹ {balance:,.0f}")

# =========================================================
# 4️⃣ FUTURE CHILD PLANNING
# =========================================================

elif tool == "Future Planning for Children":

    st.header("Future Planning for Children")

    child_age = st.number_input("Child Current Age", 0, 18, 2)

    milestones = {
        "10th Board": (14, 200000),
        "12th Board": (16, 200000),
        "Graduation": (18, 2000000),
        "Marriage": (24, 2000000)
    }

    total_sip = 0

    for name, (goal_age, cost_today) in milestones.items():
        years = goal_age - child_age
        future_cost = future_value(cost_today, inflation, years)

        sip_needed = future_cost / (((1 + expected_return) ** years - 1) / expected_return)
        total_sip += sip_needed

        st.write(f"{name} Goal → Future Cost ₹ {future_cost:,.0f} | SIP Needed ₹ {sip_needed/12:,.0f}")

    st.success(f"Total SIP Required: ₹ {total_sip/12:,.0f}")

# =========================================================
# 5️⃣ RETIREMENT PLANNER
# =========================================================

elif tool == "Retirement Planner":

    st.header("Retirement Planner")

    retire_age = st.number_input("Retirement Age", 45, 75, 60)
    annual_expense = st.number_input("Annual Expense Today (₹)", value=915000)

    years_to_ret = retire_age - entry_age
    expense_at_ret = future_value(annual_expense, inflation, years_to_ret)

    corpus_required = expense_at_ret * 25

    st.success(f"Retirement Corpus Required: ₹ {corpus_required:,.0f}")

# =========================================================
# 6️⃣ TERM INSURANCE
# =========================================================

elif tool == "Term Insurance Calculator":

    st.header("Term Insurance Calculator")

    annual_income = st.number_input("Annual Income (₹)", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - entry_age
    cover = annual_income * years_left

    st.success(f"Recommended Term Cover: ₹ {cover:,.0f}")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("Disclaimer: Outputs are illustrative and for educational purposes only.")
