import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Freedom", layout="wide")

# =====================================================
# DARK FINTECH THEME
# =====================================================
st.markdown("""
<style>
.stApp { background-color: #0F172A; }

.header-box {
    background: linear-gradient(90deg, #1E3A8A, #0EA5E9);
    padding: 24px;
    border-radius: 14px;
    text-align: center;
    color: white;
    font-size: 42px;
    font-weight: 700;
}

.subtitle {
    text-align:center;
    color:#93C5FD;
    font-size:18px;
    margin-bottom:25px;
}

.stButton > button {
    background: linear-gradient(90deg, #2563EB, #0EA5E9);
    color: white;
    border-radius: 8px;
    height: 45px;
    font-weight: 600;
    border: none;
}

section[data-testid="stSidebar"] { background-color: #111827; }
label { color: #CBD5E1 !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# NAVIGATION
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page

# =====================================================
# HEADER
# =====================================================
st.markdown('<div class="header-box">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Integrated Wealth Planning Platform</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================================
# SIDEBAR GLOBAL INPUTS
# =====================================================
st.sidebar.header("Client Profile")

current_age = st.sidebar.number_input("Current Age", 25, 70, 30)
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0)/100
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0)/100

# =====================================================
# COMMON FUNCTIONS
# =====================================================
def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

def sip_required(target, rate, years):
    if years <= 0:
        return 0
    return target / (((1 + rate) ** years - 1) / rate)

# =====================================================
# HOME PAGE
# =====================================================
if st.session_state.page == "home":

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("SIP Calculator", on_click=lambda: go("sip"))
        st.button("Children Planner", on_click=lambda: go("children"))

    with col2:
        st.button("SWP Calculator", on_click=lambda: go("swp"))
        st.button("Retirement Planner", on_click=lambda: go("retirement"))

    with col3:
        st.button("Term Insurance", on_click=lambda: go("term"))
        st.button("Cashflow Planner", on_click=lambda: go("cashflow"))

# =====================================================
# SIP CALCULATOR
# =====================================================
if st.session_state.page == "sip":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Monthly SIP (₹)", value=5000)
    years = st.number_input("Investment Years", value=10)

    corpus = 0
    ages = []
    corpus_list = []

    for y in range(years):
        corpus = (corpus + monthly_sip*12) * (1 + expected_return)
        ages.append(current_age+y)
        corpus_list.append(corpus)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ages, y=corpus_list,
                             mode='lines+markers',
                             name="Corpus Growth"))
    fig.update_layout(template="plotly_dark",
                      title="SIP Wealth Growth")

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# CHILDREN PLANNER
# =====================================================
if st.session_state.page == "children":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Children Planner")

    num_children = st.number_input("Number of Children", 1, 4, 1)
    summary = []

    for i in range(num_children):

        child_age = st.number_input(f"Child {i+1} Age", 0, 18, 2, key=f"child{i}")

        goals = {
            "10th": 14,
            "12th": 16,
            "Graduation": 18,
            "Masters": 22,
            "Marriage": 24
        }

        for goal, age in goals.items():

            cost = st.number_input(f"{goal} Cost (₹)", value=2000000, key=f"{goal}{i}")

            years = age - child_age
            future_cost = future_value(cost, inflation, years)
            sip = sip_required(future_cost, expected_return, years)

            summary.append([f"Child {i+1}-{goal}", age, round(future_cost,0), round(sip/12,0)])

    df = pd.DataFrame(summary, columns=["Goal", "Age", "Future Cost", "Monthly SIP"])
    st.dataframe(df, use_container_width=True)

# =====================================================
# SWP CALCULATOR
# =====================================================
if st.session_state.page == "swp":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SWP Calculator")

    corpus = st.number_input("Initial Corpus", value=10000000)
    monthly_withdrawal = st.number_input("Monthly Withdrawal", value=100000)
    years = st.number_input("Withdrawal Years", value=20)

    ages = []
    balances = []

    for y in range(years):
        corpus = corpus*(1+expected_return)-(monthly_withdrawal*12)
        ages.append(current_age+y)
        balances.append(corpus)
        if corpus <= 0:
            break

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ages, y=balances,
                             mode='lines+markers',
                             name="Corpus Depletion"))
    fig.update_layout(template="plotly_dark",
                      title="SWP Corpus Depletion")

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# RETIREMENT PLANNER
# =====================================================
if st.session_state.page == "retirement":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    annual_expense = st.number_input("Annual Expense Today (₹)", value=900000)

    years = retirement_age - current_age
    expense_at_ret = future_value(annual_expense, inflation, years)
    required_corpus = expense_at_ret * 25

    fig = go.Figure()
    fig.add_hline(y=required_corpus, line_dash="dash",
                  annotation_text="Required Corpus")
    fig.update_layout(template="plotly_dark",
                      title="Required Retirement Corpus")

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TERM INSURANCE
# =====================================================
if st.session_state.page == "term":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance Calculator")

    annual_income = st.number_input("Annual Income", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - current_age
    cover = annual_income * years_left

    fig = go.Figure(go.Indicator(
        mode="number",
        value=cover,
        title={"text": "Recommended Cover (₹)"}
    ))

    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# CASHFLOW PLANNER
# =====================================================
if st.session_state.page == "cashflow":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Cashflow Planner")

    plan_till_age = st.number_input("Plan Till Age", 60, 100, 85)
    annual_income = st.number_input("Annual Income (₹)", value=1800000)
    annual_expense = st.number_input("Annual Expense (₹)", value=900000)
    annual_investment = st.number_input("Annual Investment (₹)", value=300000)
    corpus = st.number_input("Current Corpus (₹)", value=1000000)

    balance = corpus
    ages = []
    corpus_list = []

    for age in range(current_age, plan_till_age + 1):
        surplus = annual_income - annual_expense - annual_investment
        balance = (balance + annual_investment) * (1 + expected_return)
        ages.append(age)
        corpus_list.append(balance)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ages, y=corpus_list,
                             mode='lines',
                             name="Wealth Projection"))
    fig.update_layout(template="plotly_dark",
                      title="Cashflow Wealth Projection")

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration Only")
