import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from datetime import datetime
import requests

st.set_page_config(page_title="WealthTech Advisory Suite", layout="wide")

# =========================================================
# CORE FINANCIAL FUNCTIONS
# =========================================================

def future_value(present, inflation, years):
    return present * (1 + inflation) ** years

def monte_carlo_goal(target, years, mean=0.12, std=0.15, simulations=1000):
    results = []
    for _ in range(simulations):
        value = target
        for _ in range(years):
            annual_return = np.random.normal(mean, std)
            value = value * (1 + annual_return)
        results.append(value)
    return np.array(results)

# =========================================================
# MEAN-VARIANCE OPTIMIZER
# =========================================================

def mean_variance_optimizer(returns, risk_free=0.06):
    cov_matrix = returns.cov()
    mean_returns = returns.mean()

    weights = np.ones(len(mean_returns)) / len(mean_returns)

    portfolio_return = np.dot(weights, mean_returns)
    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    sharpe = (portfolio_return - risk_free) / portfolio_vol

    return weights, portfolio_return, portfolio_vol, sharpe

# =========================================================
# GLIDE PATH MODEL
# =========================================================

def glide_path_equity(age):
    equity = max(100 - age, 30)
    debt = 100 - equity
    return {"Equity": equity, "Debt": debt}

# =========================================================
# NAV INTEGRATION (AMFI API)
# =========================================================

def get_nav(scheme_code):
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url)
        data = response.json()
        nav = data["data"][0]["nav"]
        return nav
    except:
        return "NAV Fetch Error"

# =========================================================
# AI COMMENTARY (Rule-Based Smart Engine)
# =========================================================

def advisory_commentary(risk_score, glide_alloc, sharpe):
    if risk_score > 8:
        profile = "Aggressive"
    elif risk_score > 5:
        profile = "Balanced"
    else:
        profile = "Conservative"

    comment = f"""
    Client Risk Profile: {profile}

    Recommended Equity Allocation: {glide_alloc['Equity']}%

    Portfolio Sharpe Ratio: {round(sharpe,2)}

    Advisory Insight:
    Maintain disciplined allocation and rebalance annually.
    Consider staggered investments to reduce volatility risk.
    """

    return comment

# =========================================================
# UI START
# =========================================================

st.title("WealthTech Institutional Advisory Suite")

age = st.sidebar.number_input("Current Age", 25, 70, 35)
inflation = st.sidebar.number_input("Inflation (%)", 3.0, 10.0, 6.0) / 100
risk_score = st.sidebar.slider("Risk Score (1-12)", 1, 12, 7)

# =========================================================
# MULTI GOAL MONTE CARLO
# =========================================================

st.header("Monte Carlo Simulation Per Goal")

ret_goal = st.number_input("Retirement Goal Today (₹)", value=1200000)
ret_years = st.number_input("Years to Retirement", value=25)

child_goal = st.number_input("Child Goal Today (₹)", value=2500000)
child_years = st.number_input("Years to Child Goal", value=10)

vac_goal = st.number_input("Vacation Goal Today (₹)", value=500000)
vac_years = st.number_input("Years to Vacation", value=5)

ret_future = future_value(ret_goal, inflation, ret_years)
child_future = future_value(child_goal, inflation, child_years)
vac_future = future_value(vac_goal, inflation, vac_years)

ret_mc = monte_carlo_goal(ret_future, ret_years)
child_mc = monte_carlo_goal(child_future, child_years)
vac_mc = monte_carlo_goal(vac_future, vac_years)

fig, ax = plt.subplots()
ax.hist(ret_mc/10000000, bins=40, alpha=0.5, label="Retirement")
ax.hist(child_mc/10000000, bins=40, alpha=0.5, label="Child")
ax.hist(vac_mc/10000000, bins=40, alpha=0.5, label="Vacation")
ax.legend()
ax.set_title("Monte Carlo Distribution (₹ Cr)")
st.pyplot(fig)

# =========================================================
# MEAN VARIANCE OPTIMIZER
# =========================================================

st.header("Mean-Variance Portfolio Optimizer")

returns_data = pd.DataFrame({
    "Equity": np.random.normal(0.12, 0.18, 100),
    "Debt": np.random.normal(0.07, 0.05, 100),
    "Gold": np.random.normal(0.08, 0.12, 100)
})

weights, port_return, port_vol, sharpe = mean_variance_optimizer(returns_data)

st.write("Optimized Weights:", dict(zip(returns_data.columns, weights)))
st.write("Expected Return:", round(port_return*100,2), "%")
st.write("Portfolio Volatility:", round(port_vol*100,2), "%")
st.write("Sharpe Ratio:", round(sharpe,2))

# =========================================================
# GLIDE PATH
# =========================================================

st.header("Glide Path Allocation")

glide_alloc = glide_path_equity(age)
st.write(glide_alloc)

fig2, ax2 = plt.subplots()
ax2.pie(glide_alloc.values(), labels=glide_alloc.keys(), autopct='%1.1f%%')
st.pyplot(fig2)

# =========================================================
# NAV FETCH
# =========================================================

st.header("Mutual Fund NAV Fetch")

scheme_code = st.text_input("Enter MF Scheme Code (e.g., 119551)")
if scheme_code:
    nav = get_nav(scheme_code)
    st.write("Latest NAV:", nav)

# =========================================================
# AI COMMENTARY
# =========================================================

st.header("AI Advisory Commentary")

comment = advisory_commentary(risk_score, glide_alloc, sharpe)
st.text_area("Advisory Summary", comment, height=200)

# =========================================================
# IPS GENERATOR
# =========================================================

def generate_ips():
    file_path = "IPS_Report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Investment Policy Statement", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(comment, styles["Normal"]))

    doc.build(elements)
    return file_path

if st.button("Generate Client IPS PDF"):
    pdf = generate_ips()
    with open(pdf, "rb") as f:
        st.download_button("Download IPS", f, file_name="IPS_Report.pdf")
