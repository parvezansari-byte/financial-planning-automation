import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime
from dateutil import relativedelta
import tempfile
import os

st.set_page_config(page_title="Institutional Wealth Advisory Platform", layout="wide")

# ----------------------------
# Database
# ----------------------------
conn = sqlite3.connect("clients.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS clients (
    name TEXT,
    age INTEGER,
    ret_age INTEGER,
    expense REAL,
    inflation REAL,
    return_rate REAL
)
""")
conn.commit()

# ----------------------------
# Financial Logic
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
# India Tax Engine (Equity)
# ----------------------------

def india_equity_tax(purchase_price, sale_price, holding_days):
    gain = sale_price - purchase_price

    if holding_days < 365:
        tax = gain * 0.15  # STCG 15%
        tax_type = "STCG (15%)"
    else:
        exempt = 100000
        taxable_gain = max(gain - exempt, 0)
        tax = taxable_gain * 0.10
        tax_type = "LTCG (10% above ₹1L)"

    return gain, tax, tax_type

# ----------------------------
# XIRR Calculator
# ----------------------------

def xirr(cashflows, dates):
    def npv(rate):
        return sum([cf / (1 + rate) ** ((dates[i] - dates[0]).days / 365)
                    for i, cf in enumerate(cashflows)])

    rate = 0.1
    for _ in range(100):
        rate -= npv(rate) / 100000
    return rate

# ----------------------------
# Sidebar Inputs
# ----------------------------

st.sidebar.header("Client Management")

clients = pd.read_sql("SELECT DISTINCT name FROM clients", conn)

selected_client = st.sidebar.selectbox(
    "Load Client",
    ["New Client"] + clients["name"].tolist()
)

if selected_client != "New Client":
    data = pd.read_sql(f"SELECT * FROM clients WHERE name='{selected_client}'", conn)
    age = int(data["age"].values[0])
    ret_age = int(data["ret_age"].values[0])
    expense = float(data["expense"].values[0])
    inflation = float(data["inflation"].values[0])
    post_ret = float(data["return_rate"].values[0])
else:
    age = st.sidebar.number_input("Current Age", 25, 70, 40)
    ret_age = st.sidebar.number_input("Retirement Age", 40, 75, 60)
    expense = st.sidebar.number_input("Annual Expense (₹)", value=1200000)
    inflation = st.sidebar.number_input("Inflation (%)", value=6.0) / 100
    post_ret = st.sidebar.number_input("Return (%)", value=7.0) / 100

client_name = st.sidebar.text_input("Client Name")

if st.sidebar.button("Save Client"):
    c.execute("INSERT INTO clients VALUES (?,?,?,?,?,?)",
              (client_name, age, ret_age, expense, inflation, post_ret))
    conn.commit()
    st.sidebar.success("Client Saved")

years_to_ret = ret_age - age
corpus, expense_at_ret = retirement_corpus(expense, inflation, years_to_ret, post_ret)

# ----------------------------
# Dashboard
# ----------------------------

st.title("Institutional Wealth Advisory Dashboard")

col1, col2 = st.columns(2)
col1.metric("Expense at Retirement", f"₹ {expense_at_ret/10000000:.2f} Cr")
col2.metric("Required Corpus", f"₹ {corpus/10000000:.2f} Cr")

# ----------------------------
# Monte Carlo Histogram
# ----------------------------

st.subheader("Monte Carlo Distribution")

results = monte_carlo_distribution(corpus, expense_at_ret, 0.10, 0.15)
fig, ax = plt.subplots()
ax.hist(results/10000000, bins=50)
ax.set_title("Final Corpus Distribution (₹ Cr)")
st.pyplot(fig)

prob_ruin = np.sum(results <= 0) / len(results)
st.write(f"Probability of Ruin: {round(prob_ruin*100,2)}%")

# ----------------------------
# Portfolio Upload + XIRR
# ----------------------------

st.subheader("Portfolio Upload (CSV for XIRR)")

uploaded_file = st.file_uploader("Upload Portfolio CSV (Date, Cashflow)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"])
    rate = xirr(df["Cashflow"].tolist(), df["Date"].tolist())
    st.success(f"Portfolio XIRR: {round(rate*100,2)}%")

# ----------------------------
# India Tax Calculator
# ----------------------------

st.subheader("India Equity Tax Calculator")

purchase = st.number_input("Purchase Value (₹)", value=1000000)
sale = st.number_input("Sale Value (₹)", value=1500000)
holding = st.number_input("Holding Days", value=400)

gain, tax, tax_type = india_equity_tax(purchase, sale, holding)

st.write(f"Capital Gain: ₹ {gain:,.0f}")
st.write(f"Tax Type: {tax_type}")
st.write(f"Tax Payable: ₹ {tax:,.0f}")

# ----------------------------
# Styled PDF Generator (With Chart)
# ----------------------------

def generate_pdf():
    file_path = "wealth_report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Wealth Advisory Report", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Required Corpus: ₹ {corpus/10000000:.2f} Cr", styles["Normal"]))
    elements.append(Paragraph(f"Probability of Ruin: {round(prob_ruin*100,2)}%", styles["Normal"]))

    chart_path = "chart.png"
    fig.savefig(chart_path)
    elements.append(Spacer(1, 12))
    elements.append(Image(chart_path, width=400, height=250))

    doc.build(elements)
    return file_path

if st.button("Generate Professional PDF Report"):
    pdf_path = generate_pdf()
    with open(pdf_path, "rb") as f:
        st.download_button("Download PDF", f, file_name="Wealth_Report.pdf")
