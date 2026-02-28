import streamlit as st
import pandas as pd
import numpy as np

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Freedom", layout="wide")

# =====================================================
# DARK THEME
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
    background: linear-gradient(90deg,#2563EB,#06B6D4);
    color: white;
    border-radius: 8px;
    height: 45px;
    font-weight: 600;
    border: none;
}

section[data-testid="stSidebar"] { background-color: #111827; }
label { color: #CBD5E1 !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# NAVIGATION
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
# SIDEBAR
# =====================================================
st.sidebar.header("Client Profile")
current_age = st.sidebar.number_input("Current Age", 25, 70, 30)

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
        st.button("House Planning", on_click=lambda: go("house"))
        st.button("Cashflow Planner", on_click=lambda: go("cashflow"))

# =====================================================
# CASHFLOW PLANNER (DETAILED STRUCTURE)
# =====================================================
if st.session_state.page == "cashflow":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Detailed Cashflow Planner")

    # ---------------------------
    # CASH INFLOWS
    # ---------------------------
    st.markdown("## CASH INFLOWS")

    salary = st.number_input("Salary / Wages (After-Tax)", value=0)
    side_income = st.number_input("Side Hustle / Freelance", value=0)
    investment_income = st.number_input("Investment Income", value=0)
    other_income = st.number_input("Other Income", value=0)

    total_inflow = salary + side_income + investment_income + other_income

    # ---------------------------
    # CASH OUTFLOWS
    # ---------------------------
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
    retirement = st.number_input("Retirement Contributions", value=0)
    investments = st.number_input("Investments (Stocks / MF / Crypto)", value=0)

    savings_total = emergency + retirement + investments

    total_outflow = fixed_total + variable_total + savings_total

    net_cashflow = total_inflow - total_outflow

    # ---------------------------
    # SUMMARY TABLE
    # ---------------------------
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

    st.markdown("## CASHFLOW SUMMARY")
    st.dataframe(summary, use_container_width=True)

    if net_cashflow > 0:
        st.success(f"Positive Cashflow: ₹ {net_cashflow:,.0f}")
    elif net_cashflow == 0:
        st.warning("Break-even Cashflow")
    else:
        st.error(f"Cashflow Deficit: ₹ {abs(net_cashflow):,.0f}")

# =====================================================
# PLACEHOLDER MODULES (Simplified)
# =====================================================
if st.session_state.page == "sip":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SIP Calculator")
    st.write("SIP module here...")

if st.session_state.page == "swp":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SWP Calculator")
    st.write("SWP module here...")

if st.session_state.page == "retirement":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Planner")
    st.write("Retirement module here...")

if st.session_state.page == "children":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Children Planner")
    st.write("Children module here...")

if st.session_state.page == "term":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance")
    st.write("Term module here...")

if st.session_state.page == "house":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("House Planning")
    st.write("House module here...")

st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration Only")
