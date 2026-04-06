# ============================================================
# Freedom ULTRA PRO V11 ELITE DASHBOARD
# Single File Streamlit Financial Planning Super App
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import math

st.set_page_config(page_title="Freedom ULTRA PRO V11", layout="wide")

# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------

def fmt(x):
    return f"₹{x:,.0f}"


def sip_future_value(pmt, r, years):
    r = r/100/12
    n = years*12
    if r == 0:
        return pmt*n
    return pmt*((1+r)**n - 1)/r*(1+r)


def lumpsum_future_value(pv, r, years):
    return pv*((1+r/100)**years)


def emi(p, r, y):
    r = r/100/12
    n = y*12
    if r == 0:
        return p/n
    return p*r*(1+r)**n/((1+r)**n-1)


def goal_future_cost(cost, infl, years):
    return cost*((1+infl/100)**years)

# ------------------------------------------------------------
# Session
# ------------------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ------------------------------------------------------------
# Navigation
# ------------------------------------------------------------

cols = st.columns(6)

with cols[0]:
    if st.button("Dashboard"):
        st.session_state.page="Dashboard"

with cols[1]:
    if st.button("Cashflow"):
        st.session_state.page="Cashflow"

with cols[2]:
    if st.button("Investments"):
        st.session_state.page="Invest"

with cols[3]:
    if st.button("Goals"):
        st.session_state.page="Goals"

with cols[4]:
    if st.button("Protection"):
        st.session_state.page="Protection"

with cols[5]:
    if st.button("Reports"):
        st.session_state.page="Reports"

st.divider()

# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":

    st.title("Freedom ULTRA PRO V11 Elite Dashboard")

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        income = st.number_input("Monthly Income",value=50000)

    with col2:
        expense = st.number_input("Monthly Expense",value=30000)

    with col3:
        sip = st.number_input("Monthly SIP",value=10000)

    with col4:
        emi_out = st.number_input("Loan EMI",value=5000)

    surplus = income-expense-sip-emi_out

    k1,k2,k3,k4 = st.columns(4)

    k1.metric("Income",fmt(income))
    k2.metric("Expense",fmt(expense))
    k3.metric("Investments",fmt(sip))
    k4.metric("Surplus",fmt(surplus))

    st.subheader("Financial Allocation")

    df = pd.DataFrame({
        "Category":["Expense","Investments","EMI","Surplus"],
        "Amount":[expense,sip,emi_out,max(surplus,0)]
    })

    st.bar_chart(df.set_index("Category"))


# ============================================================
# CASHFLOW
# ============================================================

if st.session_state.page == "Cashflow":

    st.header("Overall Cashflow Master")

    inc1,inc2,inc3 = st.columns(3)

    salary = inc1.number_input("Salary",value=50000)
    business = inc2.number_input("Business",value=0)
    rental = inc3.number_input("Rental",value=0)

    exp1,exp2,exp3 = st.columns(3)

    fixed = exp1.number_input("Fixed Expense",value=20000)
    variable = exp2.number_input("Variable Expense",value=10000)
    emi_out = exp3.number_input("EMI",value=5000)

    total_income = salary+business+rental
    total_expense = fixed+variable+emi_out

    surplus = total_income-total_expense

    c1,c2,c3 = st.columns(3)

    c1.metric("Total Income",fmt(total_income))
    c2.metric("Total Expense",fmt(total_expense))
    c3.metric("Surplus",fmt(surplus))


# ============================================================
# INVESTMENT
# ============================================================

if st.session_state.page == "Invest":

    st.header("Investment Calculators")

    tab1,tab2 = st.tabs(["SIP","Lumpsum"])

    with tab1:

        sip_amt = st.number_input("Monthly SIP",value=10000)
        r = st.number_input("Return %",value=12.0)
        y = st.number_input("Years",value=15)

        fv = sip_future_value(sip_amt,r,y)

        st.metric("Future Value",fmt(fv))

    with tab2:

        l = st.number_input("Investment",value=500000)
        r = st.number_input("Return %",value=12.0,key="l2")
        y = st.number_input("Years",value=10,key="l3")

        fv = lumpsum_future_value(l,r,y)

        st.metric("Future Value",fmt(fv))


# ============================================================
# GOALS
# ============================================================

if st.session_state.page == "Goals":

    st.header("Goal Planner")

    cost = st.number_input("Current Cost",value=2000000)
    infl = st.number_input("Inflation %",value=7.0)
    years = st.number_input("Years",value=10)

    future = goal_future_cost(cost,infl,years)

    st.metric("Future Cost",fmt(future))


# ============================================================
# PROTECTION
# ============================================================

if st.session_state.page == "Protection":

    st.header("Insurance Calculator")

    income = st.number_input("Annual Income",value=800000)
    years = st.number_input("Years to work",value=25)

    cover = income*years

    st.metric("Suggested Life Cover",fmt(cover))


# ============================================================
# REPORTS
# ============================================================

if st.session_state.page == "Reports":

    st.header("Client Report Center")

    st.write("Download summary reports and analysis.")

    data = {
        "Metric":["Sample A","Sample B"],
        "Value":[100,200]
    }

    df = pd.DataFrame(data)

    st.dataframe(df)

    st.download_button("Download CSV",df.to_csv(index=False),"report.csv")

# ============================================================
# END
# ============================================================
