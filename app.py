import pandas as pd
import matplotlib.pyplot as plt
from financial_engine import (
    retirement_corpus,
    retirement_projection,
    sequence_risk_projection
)
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

col1.metric("Expense at Retirement (₹)", f"₹ {expense_at_ret/10000000:.2f} Cr")
col2.metric("Required Corpus (₹)", f"₹ {corpus/10000000:.2f} Cr")
st.subheader("Retirement Sustainability (30 Years)")

projection_df = retirement_projection(
    corpus,
    expense_at_ret,
    inflation,
    post_ret
)

fig, ax = plt.subplots()
ax.plot(projection_df["Year"], projection_df["Closing Corpus"])
ax.set_title("Corpus Depletion Over Time")
ax.set_xlabel("Year")
ax.set_ylabel("Corpus")
st.pyplot(fig)

st.dataframe(projection_df)

if st.button("Run Monte Carlo Simulation"):
    success_rate = monte_carlo_simulation(
        corpus,
        expense_at_ret,
        0.10,
        0.15,
        30
    )

    st.success(f"Success Probability: {round(success_rate*100,2)}%")
