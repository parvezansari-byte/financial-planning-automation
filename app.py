import streamlit as st
import numpy as np

st.set_page_config(page_title="Investment & Insurance Planner", layout="wide")

# ======================================================
# HEADER
# ======================================================

st.markdown(
    """
    <h1 style='text-align:center; background-color:#6A35A3; color:white; padding:15px;'>
    Investment & Insurance Planner
    </h1>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    client_name = st.text_input("Client Name", "Aditya")

with col2:
    distributor_name = st.text_input("Distributor Name", "Saurabh")

st.markdown("---")

# ======================================================
# ENTRY AGE FILTER
# ======================================================

st.sidebar.header("Client Profile")

entry_age = st.sidebar.number_input("Entry Age", 18, 65, 30)
retirement_age = st.sidebar.number_input("Retirement Age", 45, 75, 60)
expected_return = st.sidebar.number_input("Expected Return (%)", value=12.0)/100
inflation = st.sidebar.number_input("Inflation (%)", value=6.0)/100

years_to_ret = retirement_age - entry_age

st.sidebar.markdown("---")
selected_tool = st.sidebar.radio(
    "Select Calculator",
    [
        "Lumpsum & SIP Calculator",
        "SWP Calculator",
        "SIP + SWP",
        "Future Planning for Children",
        "Retirement Planner",
        "Term Insurance Calculator"
    ]
)

# ======================================================
# FUNCTIONS
# ======================================================

def future_value(amount, rate, years):
    return amount * (1 + rate) ** years

def sip_future_value(sip, rate, years):
    return sip * (((1 + rate)**years - 1) / rate)

def retirement_corpus(expense, inflation, years):
    inflated_expense = future_value(expense, inflation, years)
    return inflated_expense * 20

# ======================================================
# CALCULATOR MODULES
# ======================================================

# 1️⃣ LUMPSUM & SIP
if selected_tool == "Lumpsum & SIP Calculator":
    st.header("Lumpsum & SIP Calculator")

    investment = st.number_input("Lumpsum Investment (₹)", value=100000)
    sip = st.number_input("Monthly SIP (₹)", value=10000)
    years = st.number_input("Investment Years", value=10)

    lumpsum_value = future_value(investment, expected_return, years)
    sip_value = sip_future_value(sip, expected_return, years)

    total_value = lumpsum_value + sip_value

    st.success(f"Total Future Value: ₹ {total_value:,.0f}")

# 2️⃣ SWP
elif selected_tool == "SWP Calculator":
    st.header("SWP Calculator")

    corpus = st.number_input("Initial Corpus (₹)", value=5000000)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=30000)
    years = st.number_input("Withdrawal Years", value=20)

    remaining = corpus
    for _ in range(years):
        remaining = remaining * (1 + expected_return) - (withdrawal * 12)

    st.success(f"Remaining Corpus After {years} Years: ₹ {remaining:,.0f}")

# 3️⃣ SIP + SWP
elif selected_tool == "SIP + SWP":
    st.header("SIP Accumulation + SWP Distribution")

    sip = st.number_input("Monthly SIP (₹)", value=15000)
    accumulation_years = st.number_input("Accumulation Years", value=15)
    withdrawal_years = st.number_input("Withdrawal Years", value=20)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=50000)

    corpus = sip_future_value(sip, expected_return, accumulation_years)

    remaining = corpus
    for _ in range(withdrawal_years):
        remaining = remaining * (1 + expected_return) - (withdrawal * 12)

    st.success(f"Corpus Built: ₹ {corpus:,.0f}")
    st.info(f"Remaining After Withdrawal: ₹ {remaining:,.0f}")

# 4️⃣ CHILD FUTURE PLANNING
elif selected_tool == "Future Planning for Children":
    st.header("Child Future Planning")

    child_cost_today = st.number_input("Education Cost Today (₹)", value=2500000)
    years = st.number_input("Years to Goal", value=10)
    current_savings = st.number_input("Current Savings (₹)", value=0)

    future_cost = future_value(child_cost_today, inflation, years)
    gap = future_cost - current_savings

    sip_required = gap / (((1 + expected_return)**years - 1) / expected_return)

    st.success(f"Future Cost: ₹ {future_cost:,.0f}")
    st.warning(f"Required Monthly SIP: ₹ {sip_required/12:,.0f}")

# 5️⃣ RETIREMENT PLANNER
elif selected_tool == "Retirement Planner":
    st.header("Retirement Planner")

    annual_expense = st.number_input("Annual Expense Today (₹)", value=1000000)

    corpus_needed = retirement_corpus(annual_expense, inflation, years_to_ret)

    st.success(f"Required Retirement Corpus: ₹ {corpus_needed:,.0f}")

# 6️⃣ TERM INSURANCE
elif selected_tool == "Term Insurance Calculator":
    st.header("Term Insurance Calculator")

    annual_expense = st.number_input("Annual Family Expense (₹)", value=800000)
    income_years = retirement_age - entry_age

    cover_needed = annual_expense * income_years

    st.success(f"Recommended Term Cover: ₹ {cover_needed:,.0f}")

# ======================================================
# FOOTER
# ======================================================

st.markdown("---")
st.caption("Disclaimer: Results are illustrative. Consult a financial advisor before investing.")
