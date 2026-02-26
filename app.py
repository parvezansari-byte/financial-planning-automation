import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter


# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(page_title="Wealth Advisory Platform", layout="wide")


# ----------------------------
# Database Setup
# ----------------------------
conn = sqlite3.connect("clients.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS clients (
    username TEXT,
    age INTEGER,
    ret_age INTEGER,
    expense REAL,
    inflation REAL,
    return_rate REAL
)
""")
conn.commit()


# ----------------------------
# Login System
# ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Client Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if password == "wealth123":  # simple demo login
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful")
        else:
            st.error("Invalid Credentials")

    st.stop()


# ----------------------------
# Financial Functions
# ----------------------------

def future_value(present, inflation, years):
    return present * (1 + inflation) ** years


def retirement_corpus(expense_today, inflation, years_to_ret, post_ret_return, retirement_years=30):
    expense_at_ret = future_value(expense_today, inflation, years_to_ret)
    r = post_ret_return
    g = inflation
    corpus = expense_at_ret * (1 - ((1 + g) / (1 + r)) ** retirement_years) / (r - g)
    return corpus, expense_at_ret


def monte_carlo_distribution(initial_corpus, withdrawal, mean_return, std_dev, years=30, simulations=1000):
    results = []

    for _ in range(simulations):
        corpus = initial_corpus
        for year in range(years):
            annual_return = np.random.normal(mean_return, std_dev)
            corpus = corpus * (1 + annual_return) - withdrawal
            if corpus <= 0:
                break
        results.append(corpus)

    return np.array(results)


# ----------------------------
# Sidebar Inputs
# ----------------------------

st.sidebar.header("Client Inputs")

age = st.sidebar.number_input("Current Age", 25, 70, 40)
ret_age = st.sidebar.number_input("Retirement Age", 40, 75, 60)
expense = st.sidebar.number_input("Annual Expense (₹)", value=1200000)
inflation = st.sidebar.number_input("Inflation (%)", value=6.0) / 100
post_ret = st.sidebar.number_input("Return (%)", value=7.0) / 100

years_to_ret = ret_age - age

corpus, expense_at_ret = retirement_corpus(expense, inflation, years_to_ret, post_ret)


# Save client data
if st.sidebar.button("Save Client"):
    c.execute("INSERT INTO clients VALUES (?,?,?,?,?,?)",
              (st.session_state.username, age, ret_age, expense, inflation, post_ret))
    conn.commit()
    st.sidebar.success("Client Saved")


# ----------------------------
# Dashboard
# ----------------------------

st.title("Institutional Wealth Advisory Dashboard")

col1, col2 = st.columns(2)
col1.metric("Expense at Retirement", f"₹ {expense_at_ret/10000000:.2f} Cr")
col2.metric("Required Corpus", f"₹ {corpus/10000000:.2f} Cr")


# ----------------------------
# SIP Gap Calculator
# ----------------------------

st.subheader("SIP Gap Calculator")

current_investment = st.number_input("Current Investment (₹)", value=0)

gap = corpus - current_investment

if gap > 0:
    sip_required = gap / ((1 + 0.12) ** years_to_ret - 1) * 12
    st.write(f"SIP Required (₹/month): ₹ {sip_required:,.0f}")
else:
    st.success("No SIP required. Goal funded.")


# ----------------------------
# Tax Adjusted SWP
# ----------------------------

st.subheader("Tax Adjusted SWP")

capital_gain_tax = 0.10
after_tax_return = post_ret * (1 - capital_gain_tax)

st.write(f"Effective Post-Tax Return: {round(after_tax_return*100,2)}%")


# ----------------------------
# Monte Carlo Histogram
# ----------------------------

st.subheader("Monte Carlo Distribution")

results = monte_carlo_distribution(corpus, expense_at_ret, 0.10, 0.15)

fig, ax = plt.subplots()
ax.hist(results/10000000, bins=50)
ax.set_title("Final Corpus Distribution (₹ Cr)")
st.pyplot(fig)


# ----------------------------
# Probability of Ruin
# ----------------------------

prob_ruin = np.sum(results <= 0) / len(results)
st.write(f"Probability of Ruin: {round(prob_ruin*100,2)}%")


# ----------------------------
# PDF Report Generator
# ----------------------------

def generate_pdf():
    file_path = "report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Wealth Advisory Report", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Required Corpus: ₹ {corpus/10000000:.2f} Cr", styles["Normal"]))
    elements.append(Paragraph(f"Probability of Ruin: {round(prob_ruin*100,2)}%", styles["Normal"]))

    doc.build(elements)
    return file_path


if st.button("Generate PDF Report"):
    file_path = generate_pdf()
    with open(file_path, "rb") as f:
        st.download_button("Download Report", f, file_name="Wealth_Report.pdf")
