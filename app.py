import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Freedom", layout="wide")

# =====================================================
# DARK THEME
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
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION NAVIGATION
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page

# =====================================================
# HEADER
# =====================================================
st.markdown('<div class="header-box">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Interactive Wealth Planning Platform</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================================
# SIDEBAR INPUTS
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
# HOME
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

# =====================================================
# SIP CALCULATOR
# =====================================================
if st.session_state.page == "sip":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Monthly SIP (₹)", value=5000)
    years = st.number_input("Years", value=10)

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
    fig.update_layout(title="SIP Wealth Growth",
                      xaxis_title="Age",
                      yaxis_title="Corpus (₹)",
                      template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# CHILDREN PLANNER
# =====================================================
if st.session_state.page == "children":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Children Planner")

    child_age = st.number_input("Child Current Age", 0, 18, 2)

    goals = {
        "10th": 14,
        "12th": 16,
        "Graduation": 18,
        "Masters": 22,
        "Marriage": 24
    }

    goal_names = []
    future_costs = []

    for goal, age in goals.items():
        cost = st.number_input(f"{goal} Cost Today (₹)", value=2000000, key=goal)
        years = age - child_age
        future_cost = future_value(cost, inflation, years)

        goal_names.append(goal)
        future_costs.append(future_cost)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=goal_names, y=future_costs,
                         marker_color="#0EA5E9"))

    fig.update_layout(title="Future Cost per Goal",
                      yaxis_title="Future Cost (₹)",
                      template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# SWP CALCULATOR
# =====================================================
if st.session_state.page == "swp":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SWP Calculator")

    corpus = st.number_input("Initial Corpus (₹)", value=10000000)
    monthly_withdrawal = st.number_input("Monthly Withdrawal (₹)", value=100000)
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
                             name="Corpus Depletion",
                             line=dict(color="red")))
    fig.update_layout(title="SWP Corpus Depletion",
                      xaxis_title="Age",
                      yaxis_title="Corpus (₹)",
                      template="plotly_dark")

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

    ages = []
    corpus_projection = []
    corpus = 0

    for y in range(years):
        corpus = (corpus + 500000) * (1 + expected_return)
        ages.append(current_age+y)
        corpus_projection.append(corpus)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ages, y=corpus_projection,
                             mode='lines',
                             name="Pre-Retirement Growth"))
    fig.add_hline(y=required_corpus, line_dash="dash",
                  annotation_text="Required Corpus",
                  annotation_position="top left")

    fig.update_layout(title="Retirement Corpus Projection",
                      xaxis_title="Age",
                      yaxis_title="Corpus (₹)",
                      template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TERM INSURANCE
# =====================================================
if st.session_state.page == "term":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance Calculator")

    annual_income = st.number_input("Annual Income (₹)", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - current_age
    cover = annual_income * years_left

    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=cover,
        title={"text": "Recommended Term Cover (₹)"},
        number={'valueformat': ',.0f'}
    ))

    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Interactive Wealth Dashboard | For Illustration Only")
