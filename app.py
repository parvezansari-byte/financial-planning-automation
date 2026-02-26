import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Goal Funding & SIP Planning Engine", layout="wide")

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
expense_growth = st.sidebar.number_input("Inflation (%)", value=6.0)/100
return_rate = st.sidebar.number_input("Expected Return (%)", value=12.0)/100
post_ret_return = st.sidebar.number_input("Post Retirement Return (%)", value=7.0)/100

years_to_ret = retirement_age - current_age

# ======================================================
# RETIREMENT CALCULATION
# ======================================================

st.title("Goal Funding & SIP Requirement Planner")

expense_at_ret = future_value(annual_expense, expense_growth, years_to_ret)

ret_corpus = retirement_corpus(
    expense_at_ret,
    expense_growth,
    post_ret_return,
    retirement_years=30
)

st.subheader("Retirement Requirement")

col1, col2 = st.columns(2)
col1.metric("Expense at Retirement", f"₹ {expense_at_ret:,.0f}")
col2.metric("Required Retirement Corpus", f"₹ {ret_corpus:,.0f}")

current_ret_savings = st.number_input("Current Retirement Savings (₹)", value=0)

ret_sip = sip_required(ret_corpus, current_ret_savings, return_rate, years_to_ret)

if ret_sip == 0:
    st.success("Retirement Goal Already Funded")
else:
    st.write(f"Required Monthly SIP for Retirement: ₹ {ret_sip/12:,.0f}")

ret_shortfall = ret_corpus - current_ret_savings
st.write(f"Retirement Funding Shortfall: ₹ {max(ret_shortfall,0):,.0f}")

# ======================================================
# CHILD 1
# ======================================================

st.subheader("Child 1 Education Goal")

child1_today = st.number_input("Child 1 Cost Today (₹)", value=2500000)
child1_years = st.number_input("Years to Child 1 Goal", value=10)
child1_current = st.number_input("Current Child 1 Savings (₹)", value=0)

child1_future = future_value(child1_today, expense_growth, child1_years)

child1_sip = sip_required(child1_future, child1_current, return_rate, child1_years)
child1_shortfall = child1_future - child1_current

st.write(f"Future Corpus Required: ₹ {child1_future:,.0f}")
st.write(f"Funding Shortfall: ₹ {max(child1_shortfall,0):,.0f}")

if child1_sip == 0:
    st.success("Child 1 Goal Fully Funded")
else:
    st.write(f"Required Monthly SIP: ₹ {child1_sip/12:,.0f}")

# ======================================================
# CHILD 2
# ======================================================

st.subheader("Child 2 Education Goal")

child2_today = st.number_input("Child 2 Cost Today (₹)", value=2000000)
child2_years = st.number_input("Years to Child 2 Goal", value=15)
child2_current = st.number_input("Current Child 2 Savings (₹)", value=0)

child2_future = future_value(child2_today, expense_growth, child2_years)

child2_sip = sip_required(child2_future, child2_current, return_rate, child2_years)
child2_shortfall = child2_future - child2_current

st.write(f"Future Corpus Required: ₹ {child2_future:,.0f}")
st.write(f"Funding Shortfall: ₹ {max(child2_shortfall,0):,.0f}")

if child2_sip == 0:
    st.success("Child 2 Goal Fully Funded")
else:
    st.write(f"Required Monthly SIP: ₹ {child2_sip/12:,.0f}")

# ======================================================
# VACATION
# ======================================================

st.subheader("Vacation Goal")

vac_today = st.number_input("Vacation Cost Today (₹)", value=500000)
vac_years = st.number_input("Years to Vacation", value=5)
vac_current = st.number_input("Current Vacation Savings (₹)", value=0)

vac_future = future_value(vac_today, expense_growth, vac_years)

vac_sip = sip_required(vac_future, vac_current, return_rate, vac_years)
vac_shortfall = vac_future - vac_current

st.write(f"Future Corpus Required: ₹ {vac_future:,.0f}")
st.write(f"Funding Shortfall: ₹ {max(vac_shortfall,0):,.0f}")

if vac_sip == 0:
    st.success("Vacation Goal Fully Funded")
else:
    st.write(f"Required Monthly SIP: ₹ {vac_sip/12:,.0f}")

# ======================================================
# TOTAL SUMMARY
# ======================================================

st.subheader("Total SIP Commitment Summary")

total_monthly_sip = (
    ret_sip +
    child1_sip +
    child2_sip +
    vac_sip
) / 12

st.metric("Total Monthly SIP Required (All Goals)", f"₹ {total_monthly_sip:,.0f}")
