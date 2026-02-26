import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------
# Page Config (HNI Layout)
# ---------------------------------
st.set_page_config(page_title="Premium Financial Planning Dashboard", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #0e1117; }
        .stMetric { font-size: 20px; }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------
# Financial Logic Functions
# ---------------------------------

def future_value(present, inflation, years):
    return present * (1 + inflation) ** years


def retirement_corpus(expense_today, inflation, years_to_ret, post_ret_return, retirement_years=30):

    expense_at_ret = future_value(expense_today, inflation, years_to_ret)

    r = post_ret_return
    g = inflation

    if r == g:
        corpus = expense_at_ret * retirement_years
    else:
        corpus = expense_at_ret * (1 - ((1 + g) / (1 + r)) ** retirement_years) / (r - g)

    return corpus, expense_at_ret


def retirement_projection(corpus, expense_at_ret, inflation, post_ret_return, years=30):

    data = []
    current_corpus = corpus
    expense = expense_at_ret

    for year in range(1, years + 1):

        opening = current_corpus
        growth = opening * post_ret_return
        closing = opening + growth - expense

        data.append([year, opening, expense, growth, closing])

        current_corpus = closing
        expense *= (1 + inflation)

    df = pd.DataFrame(data, columns=["Year", "Opening Corpus", "Withdrawal", "Growth", "Closing Corpus"])
    return df


def sequence_risk_projection(corpus, expense_at_ret, inflation, post_ret_return, years=30, shock=-0.20):

    data = []
    current_corpus = corpus
    expense = expense_at_ret

    for year in range(1, years + 1):

        opening = current_corpus

        if year == 1:
            growth = opening * shock
        else:
            growth = opening * post_ret_return

        closing = opening + growth - expense

        data.append([year, opening, expense, growth, closing])

        current_corpus = closing
        expense *= (1 + inflation)

    df = pd.DataFrame(data, columns=["Year", "Opening Corpus", "Withdrawal", "Growth", "Closing Corpus"])
    return df


def monte_carlo_simulation(initial_corpus, withdrawal, mean_return, std_dev, years, simulations=1000):

    success = 0

    for _ in range(simulations):
        corpus = initial_corpus
        for year in range(years):
            annual_return = np.random.normal(mean_return, std_dev)
            corpus = corpus * (1 + annual_return) - withdrawal
            if corpus <= 0:
                break
        if corpus > 0:
            success += 1

    return success / simulations


# ---------------------------------
# Sidebar Inputs
# ---------------------------------

st.sidebar.header("Client Inputs")

age = st.sidebar.number_input("Current Age", 25, 70, 40)
ret_age = st.sidebar.number_input("Retirement Age", 40, 75, 60)
expense = st.sidebar.number_input("Annual Expense (₹)", value=1200000)
inflation = st.sidebar.number_input("Inflation (%)", value=6.0) / 100
post_ret = st.sidebar.number_input("Post Retirement Return (%)", value=7.0) / 100

years_to_ret = ret_age - age


# ---------------------------------
# Retirement Analysis
# ---------------------------------

st.title("Premium Financial Planning Dashboard")

corpus, expense_at_ret = retirement_corpus(expense, inflation, years_to_ret, post_ret)

col1, col2 = st.columns(2)

col1.metric("Expense at Retirement", f"₹ {expense_at_ret/10000000:.2f} Cr")
col2.metric("Required Corpus", f"₹ {corpus/10000000:.2f} Cr")


# ---------------------------------
# Monte Carlo Simulation
# ---------------------------------

if st.button("Run Monte Carlo Simulation"):

    success_rate = monte_carlo_simulation(
        corpus,
        expense_at_ret,
        0.10,
        0.15,
        30
    )

    st.success(f"Success Probability: {round(success_rate*100,2)}%")


# ---------------------------------
# Sustainability Graph
# ---------------------------------

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


# ---------------------------------
# 8% vs 12% Scenario Comparison
# ---------------------------------

st.subheader("Return Scenario Comparison")

corpus_8, _ = retirement_corpus(expense, inflation, years_to_ret, 0.08)
corpus_12, _ = retirement_corpus(expense, inflation, years_to_ret, 0.12)

comparison = pd.DataFrame({
    "Scenario": ["8% Return", "12% Return"],
    "Required Corpus (₹ Cr)": [
        corpus_8 / 10000000,
        corpus_12 / 10000000
    ]
})

st.table(comparison)


# ---------------------------------
# Sequence Risk Model
# ---------------------------------

st.subheader("Sequence Risk Impact (-20% First Year Crash)")

shock_df = sequence_risk_projection(
    corpus,
    expense_at_ret,
    inflation,
    post_ret
)

fig2, ax2 = plt.subplots()
ax2.plot(shock_df["Year"], shock_df["Closing Corpus"])
ax2.set_title("Sequence Risk Impact")
ax2.set_xlabel("Year")
ax2.set_ylabel("Corpus")
st.pyplot(fig2)


# ---------------------------------
# Net Worth + Asset Allocation
# ---------------------------------

st.sidebar.header("Net Worth Inputs")

equity = st.sidebar.number_input("Equity (₹)", value=5000000)
debt = st.sidebar.number_input("Debt (₹)", value=2000000)
real_estate = st.sidebar.number_input("Real Estate (₹)", value=10000000)
cash = st.sidebar.number_input("Cash (₹)", value=1000000)

total_assets = equity + debt + real_estate + cash

st.subheader("Net Worth Summary")
st.write(f"Total Assets: ₹ {total_assets/10000000:.2f} Cr")

fig3, ax3 = plt.subplots()
ax3.pie(
    [equity, debt, real_estate, cash],
    labels=["Equity", "Debt", "Real Estate", "Cash"],
    autopct='%1.1f%%'
)
st.pyplot(fig3)
