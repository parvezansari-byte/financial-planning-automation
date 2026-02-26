import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Wealth Advisory Engine", layout="wide")

# ======================================================
# CORE FINANCIAL FUNCTIONS
# ======================================================

def future_value(present, inflation, years):
    return present * (1 + inflation) ** years

def goal_corpus(goal_amount_today, inflation, years):
    return future_value(goal_amount_today, inflation, years)

def sip_required(target, rate, years):
    r = rate
    n = years
    return target / (((1 + r)**n - 1) / r)

# ======================================================
# RISK PROFILING
# ======================================================

def calculate_risk_score(age, volatility_tolerance, investment_horizon, reaction_to_loss):
    score = 0
    
    if age < 35:
        score += 3
    elif age < 50:
        score += 2
    else:
        score += 1
    
    score += volatility_tolerance
    score += investment_horizon
    score += reaction_to_loss
    
    return score

def asset_allocation(score):
    if score <= 5:
        return {"Equity": 30, "Debt": 60, "Gold": 10}
    elif score <= 8:
        return {"Equity": 50, "Debt": 40, "Gold": 10}
    elif score <= 11:
        return {"Equity": 70, "Debt": 20, "Gold": 10}
    else:
        return {"Equity": 85, "Debt": 10, "Gold": 5}

# ======================================================
# REBALANCING ENGINE
# ======================================================

def rebalance_portfolio(current_allocation, target_allocation, total_value):
    rebalance_plan = {}
    for asset in target_allocation:
        target_value = total_value * (target_allocation[asset] / 100)
        current_value = total_value * (current_allocation.get(asset, 0) / 100)
        rebalance_plan[asset] = target_value - current_value
    return rebalance_plan

# ======================================================
# SIDEBAR INPUTS
# ======================================================

st.sidebar.header("Client Inputs")

age = st.sidebar.number_input("Current Age", 20, 70, 35)
ret_age = st.sidebar.number_input("Retirement Age", 40, 75, 60)

inflation = st.sidebar.number_input("Inflation (%)", 3.0, 10.0, 6.0) / 100
expected_return = st.sidebar.number_input("Expected Return (%)", 5.0, 15.0, 12.0) / 100

# ======================================================
# MULTI-GOAL PLANNING
# ======================================================

st.title("Multi-Goal Wealth Planning Engine")

st.header("Goal Planning")

col1, col2, col3 = st.columns(3)

# Retirement Goal
ret_expense = col1.number_input("Retirement Annual Expense (₹)", value=1200000)
ret_years = ret_age - age
ret_corpus = goal_corpus(ret_expense, inflation, ret_years)

# Child Education
child_goal = col2.number_input("Child Education Goal Today (₹)", value=2500000)
child_years = col2.number_input("Years to Child Goal", value=10)
child_corpus = goal_corpus(child_goal, inflation, child_years)

# Vacation Goal
vac_goal = col3.number_input("Vacation Goal Today (₹)", value=500000)
vac_years = col3.number_input("Years to Vacation", value=5)
vac_corpus = goal_corpus(vac_goal, inflation, vac_years)

st.subheader("Goal Corpus Required (Future Value)")

st.write(f"Retirement Corpus Needed: ₹ {ret_corpus:,.0f}")
st.write(f"Child Education Corpus Needed: ₹ {child_corpus:,.0f}")
st.write(f"Vacation Corpus Needed: ₹ {vac_corpus:,.0f}")

# SIP Calculations
st.subheader("Required Monthly SIP for Each Goal")

ret_sip = sip_required(ret_corpus, expected_return, ret_years) / 12
child_sip = sip_required(child_corpus, expected_return, child_years) / 12
vac_sip = sip_required(vac_corpus, expected_return, vac_years) / 12

st.write(f"Retirement SIP: ₹ {ret_sip:,.0f}")
st.write(f"Child SIP: ₹ {child_sip:,.0f}")
st.write(f"Vacation SIP: ₹ {vac_sip:,.0f}")

# ======================================================
# RISK PROFILING SECTION
# ======================================================

st.header("Risk Profiling Questionnaire")

volatility = st.slider("Comfort with Market Volatility (1 Low - 3 High)", 1, 3, 2)
horizon = st.slider("Investment Horizon Comfort (1 Short - 3 Long)", 1, 3, 2)
reaction = st.slider("Reaction to 20% Market Fall (1 Panic - 3 Buy More)", 1, 3, 2)

risk_score = calculate_risk_score(age, volatility, horizon, reaction)

st.write(f"Risk Score: {risk_score}")

allocation = asset_allocation(risk_score)

st.subheader("Recommended Asset Allocation")

st.write(allocation)

# Pie Chart
fig1, ax1 = plt.subplots()
ax1.pie(allocation.values(), labels=allocation.keys(), autopct='%1.1f%%')
ax1.set_title("Recommended Allocation")
st.pyplot(fig1)

# ======================================================
# PORTFOLIO REBALANCING
# ======================================================

st.header("Portfolio Rebalancing Engine")

total_value = st.number_input("Current Portfolio Value (₹)", value=1000000)

eq_current = st.slider("Current Equity %", 0, 100, 50)
debt_current = st.slider("Current Debt %", 0, 100, 40)
gold_current = st.slider("Current Gold %", 0, 100, 10)

current_alloc = {
    "Equity": eq_current,
    "Debt": debt_current,
    "Gold": gold_current
}

rebalance = rebalance_portfolio(current_alloc, allocation, total_value)

st.subheader("Rebalancing Action (₹)")

for asset, value in rebalance.items():
    if value > 0:
        st.write(f"Buy {asset}: ₹ {value:,.0f}")
    else:
        st.write(f"Sell {asset}: ₹ {abs(value):,.0f}")
