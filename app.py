import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Freedom", layout="wide")

# ---------------- THEME ---------------- #
st.markdown("""
<style>
.stApp { background-color: #0F172A; }

.header-box {
    background: linear-gradient(90deg, #1E3A8A, #0EA5E9);
    padding: 28px;
    border-radius: 18px;
    text-align: center;
    color: white;
    font-size: 48px;
    font-weight: 800;
}

.subtitle {
    text-align:center;
    color:#93C5FD;
    font-size:18px;
    margin-bottom:30px;
}

.stButton > button {
    background: linear-gradient(90deg,#2563EB,#06B6D4);
    color: white;
    border-radius: 10px;
    height: 55px;
    font-weight: 600;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ---------------- NAV ---------------- #
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(p):
    st.session_state.page = p

# ---------------- HEADER ---------------- #
st.markdown('<div class="header-box">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Integrated Wealth Planning Platform</div>', unsafe_allow_html=True)
st.divider()

# ---------------- SIDEBAR ---------------- #
st.sidebar.header("Client Profile")
current_age = st.sidebar.number_input("Current Age", 25, 70, 30)
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0) / 100
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0) / 100

# ---------------- COMMON FUNCTIONS ---------------- #
def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

def sip_required(target, rate, years):
    if years <= 0 or rate == 0:
        return 0
    return target / (((1 + rate) ** years - 1) / rate)

# ---------------- HOME ---------------- #
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

# ---------------- SIP ---------------- #
if st.session_state.page == "sip":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Monthly SIP (₹)", value=5000)
    years = st.number_input("Investment Years", value=10)

    corpus = 0
    table = []

    for y in range(1, years + 1):
        yearly = monthly_sip * 12
        corpus = (corpus + yearly) * (1 + expected_return)
        table.append([y, yearly, round(corpus, 0)])

    df = pd.DataFrame(table, columns=["Year", "Yearly SIP", "Year End Corpus"])
    st.dataframe(df, use_container_width=True)
    st.success(f"Final Corpus: ₹ {corpus:,.0f}")

# ---------------- SWP ---------------- #
if st.session_state.page == "swp":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SWP Calculator")

    corpus = st.number_input("Initial Corpus (₹)", value=10000000)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=100000)
    years = st.number_input("Withdrawal Years", value=20)

    balance = corpus
    table = []

    for y in range(1, years + 1):
        yearly_withdraw = withdrawal * 12
        balance = balance * (1 + expected_return) - yearly_withdraw
        table.append([y, round(balance, 0)])
        if balance <= 0:
            break

    df = pd.DataFrame(table, columns=["Year", "Remaining Corpus"])
    st.dataframe(df, use_container_width=True)

# ---------------- RETIREMENT ---------------- #
if st.session_state.page == "retirement":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    annual_expense = st.number_input("Annual Expense Today (₹)", value=600000)

    years_to_ret = retirement_age - current_age
    expense_at_ret = annual_expense * ((1 + inflation) ** years_to_ret)

    required_corpus = expense_at_ret * 25

    summary = pd.DataFrame({
        "Metric": ["Expense at Retirement", "Required Corpus"],
        "Value": [f"₹ {expense_at_ret:,.0f}", f"₹ {required_corpus:,.0f}"]
    })

    st.table(summary)

    sip = sip_required(required_corpus, expected_return, years_to_ret)
    st.success(f"Required Monthly SIP: ₹ {sip/12:,.0f}")

# ---------------- CHILDREN ---------------- #
if st.session_state.page == "children":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Children Planner")

    num_children = st.number_input("Number of Children", 1, 4, 1)
    summary = []

    for i in range(num_children):
        child_age = st.number_input(f"Child {i+1} Age", 0, 18, 2, key=f"child{i}")
        goal_age = st.number_input(f"Goal Age Child {i+1}", 10, 30, 21, key=f"goal{i}")
        cost = st.number_input(f"Goal Cost (₹) Child {i+1}", value=2000000, key=f"cost{i}")

        years = goal_age - child_age
        future_cost = future_value(cost, inflation, years)
        sip = sip_required(future_cost, expected_return, years)

        summary.append([f"Child {i+1}", goal_age, round(future_cost,0), round(sip/12,0)])

    df = pd.DataFrame(summary, columns=["Child", "Goal Age", "Future Cost", "Monthly SIP Required"])
    st.dataframe(df, use_container_width=True)

# ---------------- TERM ---------------- #
if st.session_state.page == "term":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance")

    annual_income = st.number_input("Annual Income (₹)", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - current_age
    cover = annual_income * years_left

    st.success(f"Recommended Cover: ₹ {cover:,.0f}")

st.divider()
st.caption("Freedom Wealth Platform | For Illustration Only")
