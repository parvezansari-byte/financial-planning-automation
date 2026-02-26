import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Goal Feasibility Advisory Dashboard", layout="wide")

# ======================================================
# FUNCTIONS
# ======================================================

def future_value(amount, inflation, years):
    return amount * (1 + inflation) ** years

def sip_required(target, current_savings, return_rate, years):
    r = return_rate
    n = years

    if target <= current_savings:
        return 0

    gap = target - current_savings
    sip = gap / (((1 + r)**n - 1) / r)
    return sip

def retirement_corpus(expense_at_ret, inflation, return_rate, retirement_years=30):
    r = return_rate
    g = inflation

    if r == g:
        return expense_at_ret * retirement_years
    else:
        return expense_at_ret * (1 - ((1 + g)/(1 + r))**retirement_years)/(r - g)

# ======================================================
# SIDEBAR INPUTS
# ======================================================

st.sidebar.header("Client Inputs")

current_age = st.sidebar.number_input("Current Age", 25, 70, 40)
retirement_age = st.sidebar.number_input("Retirement Age", 45, 75, 60)

annual_income = st.sidebar.number_input("Annual Income (₹)", value=3000000)
annual_expense = st.sidebar.number_input("Annual Expense (₹)", value=1200000)

income_growth = st.sidebar.number_input("Income Growth (%)", value=8.0)/100
inflation = st.sidebar.number_input("Inflation (%)", value=6.0)/100
return_rate = st.sidebar.number_input("Expected Return (%)", value=12.0)/100
post_ret_return = st.sidebar.number_input("Post Retirement Return (%)", value=7.0)/100

years_to_ret = retirement_age - current_age

# ======================================================
# SURPLUS CALCULATION
# ======================================================

annual_surplus = annual_income - annual_expense
monthly_surplus = annual_surplus / 12

# ======================================================
# RETIREMENT
# ======================================================

st.title("Goal Feasibility Dashboard")

expense_at_ret = future_value(annual_expense, inflation, years_to_ret)

ret_corpus = retirement_corpus(
    expense_at_ret,
    inflation,
    post_ret_return
)

ret_current = st.number_input("Current Retirement Savings (₹)", value=0)
ret_sip = sip_required(ret_corpus, ret_current, return_rate, years_to_ret)

# ======================================================
# CHILD 1
# ======================================================

child1_today = st.number_input("Child 1 Cost Today (₹)", value=2500000)
child1_years = st.number_input("Years to Child 1 Goal", value=10)
child1_current = st.number_input("Current Child 1 Savings (₹)", value=0)

child1_future = future_value(child1_today, inflation, child1_years)
child1_sip = sip_required(child1_future, child1_current, return_rate, child1_years)

# ======================================================
# CHILD 2
# ======================================================

child2_today = st.number_input("Child 2 Cost Today (₹)", value=2000000)
child2_years = st.number_input("Years to Child 2 Goal", value=15)
child2_current = st.number_input("Current Child 2 Savings (₹)", value=0)

child2_future = future_value(child2_today, inflation, child2_years)
child2_sip = sip_required(child2_future, child2_current, return_rate, child2_years)

# ======================================================
# VACATION
# ======================================================

vac_today = st.number_input("Vacation Cost Today (₹)", value=500000)
vac_years = st.number_input("Years to Vacation", value=5)
vac_current = st.number_input("Current Vacation Savings (₹)", value=0)

vac_future = future_value(vac_today, inflation, vac_years)
vac_sip = sip_required(vac_future, vac_current, return_rate, vac_years)

# ======================================================
# TOTAL SIP
# ======================================================

total_monthly_sip = (ret_sip + child1_sip + child2_sip + vac_sip) / 12

# ======================================================
# FEASIBILITY LOGIC
# ======================================================

st.subheader("Financial Health Overview")

col1, col2 = st.columns(2)

col1.metric("Monthly Surplus Available", f"₹ {monthly_surplus:,.0f}")
col2.metric("Total Monthly SIP Required", f"₹ {total_monthly_sip:,.0f}")

coverage_ratio = monthly_surplus / total_monthly_sip if total_monthly_sip > 0 else 0

if total_monthly_sip == 0:
    st.success("All Goals Fully Funded 🎉")
else:
    if coverage_ratio >= 1:
        st.success("Goals Feasible ✅")
    elif coverage_ratio >= 0.7:
        st.warning("Partially Feasible ⚠️ — Optimization Needed")
    else:
        st.error("Goals Not Feasible ❌ — Major Gap Exists")

# ======================================================
# GOAL LEVEL STATUS
# ======================================================

st.subheader("Goal-wise Feasibility")

def goal_status(sip):
    if sip/12 <= monthly_surplus:
        return "Feasible"
    elif sip/12 <= monthly_surplus * 1.3:
        return "Tight"
    else:
        return "Not Feasible"

st.write(f"Retirement: {goal_status(ret_sip)}")
st.write(f"Child 1: {goal_status(child1_sip)}")
st.write(f"Child 2: {goal_status(child2_sip)}")
st.write(f"Vacation: {goal_status(vac_sip)}")
