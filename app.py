import streamlit as st
import pandas as pd
import numpy as np

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Freedom", layout="wide")

# =====================================================
# PREMIUM DARK THEME
# =====================================================
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
    box-shadow: 0px 10px 25px rgba(0,0,0,0.4);
}

.subtitle {
    text-align:center;
    color:#93C5FD;
    font-size:20px;
    margin-top:10px;
    margin-bottom:40px;
}

.big-button button {
    background: linear-gradient(135deg,#2563EB,#06B6D4);
    color: white;
    border-radius: 14px;
    height: 70px;
    font-size: 20px;
    font-weight: 700;
    border: none;
    width: 100%;
    transition: 0.3s ease-in-out;
}

.big-button button:hover {
    transform: scale(1.05);
    box-shadow: 0px 8px 20px rgba(0,0,0,0.5);
}

.section-card {
    background-color:#111827;
    padding:20px;
    border-radius:16px;
    box-shadow:0px 5px 15px rgba(0,0,0,0.3);
}

thead tr th {
    background-color: #2563EB !important;
    color: white !important;
}

tbody tr td { color: #E2E8F0 !important; }
tbody tr:nth-child(even) { background-color: #111827 !important; }

section[data-testid="stSidebar"] { background-color: #111827; }
label { color: #CBD5E1 !important; }
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
st.markdown('<div class="subtitle">Integrated Wealth Planning Platform</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================================
# SIDEBAR CLIENT PROFILE
# =====================================================
st.sidebar.header("Client Profile")

current_age = st.sidebar.number_input("Current Age", 25, 70, 30)
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0) / 100
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0) / 100

# =====================================================
# COMMON FUNCTIONS
# =====================================================
def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

def sip_required(target, rate, years):
    if years <= 0 or rate == 0:
        return 0
    return target / (((1 + rate) ** years - 1) / rate)

# =====================================================
# HOME
# =====================================================
if st.session_state.page == "home":

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        st.button("SIP Calculator", on_click=lambda: go("sip"))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        st.button("Children Planner", on_click=lambda: go("children"))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        st.button("SWP Calculator", on_click=lambda: go("swp"))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        st.button("Retirement Planner", on_click=lambda: go("retirement"))
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        st.button("Term Insurance", on_click=lambda: go("term"))
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# SIP CALCULATOR
# =====================================================
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
    st.line_chart(df.set_index("Year")["Year End Corpus"])
    st.success(f"Final Corpus: ₹ {corpus:,.0f}")

# =====================================================
# SWP CALCULATOR
# =====================================================
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
    st.line_chart(df.set_index("Year"))

# =====================================================
# RETIREMENT PLANNER
# =====================================================
if st.session_state.page == "retirement":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Advanced Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    life_expectancy = st.number_input("Plan Till Age", 70, 100, 90)

    years_to_ret = retirement_age - current_age
    retirement_years = life_expectancy - retirement_age

    annual_expense = st.number_input("Annual Expense Today (₹)", value=600000)

    expense_at_ret = annual_expense * ((1 + inflation) ** years_to_ret)

    required_corpus = expense_at_ret * retirement_years
    gap = required_corpus

    st.table(pd.DataFrame({
        "Metric": ["Expense at Retirement", "Required Corpus"],
        "Value": [f"₹ {expense_at_ret:,.0f}", f"₹ {required_corpus:,.0f}"]
    }))

    sip = sip_required(gap, expected_return, years_to_ret)
    st.success(f"Required Monthly SIP: ₹ {sip/12:,.0f}")

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
        goals = {"10th":14,"12th":16,"Graduation":18,"Masters":22,"Marriage":24}

        for goal, age in goals.items():
            cost = st.number_input(f"{goal} Cost (₹) Child {i+1}", value=2000000, key=f"{goal}{i}")
            years = age - child_age
            future_cost = future_value(cost, inflation, years)
            sip = sip_required(future_cost, expected_return, years)
            summary.append([f"Child {i+1}-{goal}", age, round(future_cost,0), round(sip/12,0)])

    df = pd.DataFrame(summary, columns=["Goal", "Goal Age", "Future Cost", "Monthly SIP Required"])
    st.dataframe(df, use_container_width=True)

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

    st.success(f"Recommended Cover: ₹ {cover:,.0f}")

st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration Only")
