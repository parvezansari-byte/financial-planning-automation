import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Cashflow Retirement & Goal Planning", layout="wide")

# ==========================================================
# FUNCTIONS
# ==========================================================

def future_value(amount, inflation, years):
    return amount * (1 + inflation) ** years

def retirement_corpus(expense_at_ret, inflation, return_rate, retirement_years=30):
    r = return_rate
    g = inflation
    
    if r == g:
        return expense_at_ret * retirement_years
    else:
        return expense_at_ret * (1 - ((1 + g)/(1 + r))**retirement_years)/(r - g)

# ==========================================================
# SIDEBAR INPUTS
# ==========================================================

st.sidebar.header("Client Inputs")

current_age = st.sidebar.number_input("Current Age", 25, 70, 40)
retirement_age = st.sidebar.number_input("Retirement Age", 45, 75, 60)

annual_income = st.sidebar.number_input("Annual Income (₹)", value=3000000)
income_growth = st.sidebar.number_input("Income Growth (%)", value=8.0)/100

annual_expense = st.sidebar.number_input("Annual Expense (₹)", value=1200000)
expense_growth = st.sidebar.number_input("Expense Growth (%)", value=6.0)/100

post_ret_return = st.sidebar.number_input("Post Retirement Return (%)", value=7.0)/100

years_to_ret = retirement_age - current_age

# ==========================================================
# PRE-RETIREMENT CASHFLOW
# ==========================================================

st.title("Cashflow-Based Retirement & Goal Planning")

cashflow_data = []
income = annual_income
expense = annual_expense

for year in range(years_to_ret):
    surplus = income - expense
    cashflow_data.append([current_age + year, income, expense, surplus])
    income *= (1 + income_growth)
    expense *= (1 + expense_growth)

df_cashflow = pd.DataFrame(cashflow_data, columns=["Age", "Income", "Expense", "Surplus"])

st.subheader("Pre-Retirement Cashflow Projection")
st.dataframe(df_cashflow)

# ==========================================================
# RETIREMENT CALCULATION
# ==========================================================

expense_at_retirement = future_value(annual_expense, expense_growth, years_to_ret)

required_corpus = retirement_corpus(
    expense_at_retirement,
    expense_growth,
    post_ret_return,
    retirement_years=30
)

st.subheader("Retirement Planning Summary")

col1, col2 = st.columns(2)

col1.metric("Expense at Retirement", f"₹ {expense_at_retirement:,.0f}")
col2.metric("Required Retirement Corpus", f"₹ {required_corpus:,.0f}")

# ==========================================================
# GOAL PLANNING
# ==========================================================

st.subheader("Goal Planning")

# Child 1
child1_cost = st.number_input("Child 1 Education Cost Today (₹)", value=2500000)
child1_years = st.number_input("Years to Child 1 Goal", value=10)

# Child 2
child2_cost = st.number_input("Child 2 Education Cost Today (₹)", value=2000000)
child2_years = st.number_input("Years to Child 2 Goal", value=15)

# Vacation
vacation_cost = st.number_input("Vacation Cost Today (₹)", value=500000)
vacation_years = st.number_input("Years to Vacation", value=5)

child1_future = future_value(child1_cost, expense_growth, child1_years)
child2_future = future_value(child2_cost, expense_growth, child2_years)
vacation_future = future_value(vacation_cost, expense_growth, vacation_years)

st.write(f"Child 1 Required Corpus: ₹ {child1_future:,.0f}")
st.write(f"Child 2 Required Corpus: ₹ {child2_future:,.0f}")
st.write(f"Vacation Required Corpus: ₹ {vacation_future:,.0f}")

# ==========================================================
# TOTAL REQUIRED CASHFLOW
# ==========================================================

total_goal_requirement = (
    required_corpus +
    child1_future +
    child2_future +
    vacation_future
)

st.subheader("Total Capital Required")

st.metric("Total Required Corpus (All Goals + Retirement)", 
          f"₹ {total_goal_requirement:,.0f}")
