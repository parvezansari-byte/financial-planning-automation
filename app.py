import streamlit as st
from financial_engine import retirement_corpus, monte_carlo_simulation

st.set_page_config(page_title="Wealth Planning Dashboard", layout="wide")

st.title("Premium Financial Planning Dashboard")

st.sidebar.header("Client Inputs")

age = st.sidebar.number_input("Current Age", 25, 70, 40)
ret_age = st.sidebar.number_input("Retirement Age", 40, 75, 60)
expense = st.sidebar.number_input("Annual Expense (₹)", value=1200000)
inflation = st.sidebar.number_input("Inflation (%)", value=6.0) / 100
post_ret = st.sidebar.number_input("Post Retirement Return (%)", value=7.0) / 100

years_to_ret = ret_age - age

corpus, expense_at_ret = retirement_corpus(expense, inflation, years_to_ret, post_ret)

st.subheader("Retirement Analysis")

col1, col2 = st.columns(2)

col1.metric("Expense at Retirement (₹)", f"{expense_at_ret:,.0f}")
col2.metric("Required Corpus (₹)", f"{corpus:,.0f}")

if st.button("Run Monte Carlo Simulation"):
    success_rate = monte_carlo_simulation(
        corpus,
        expense_at_ret,
        0.10,
        0.15,
        30
    )

    st.success(f"Success Probability: {round(success_rate*100,2)}%")
