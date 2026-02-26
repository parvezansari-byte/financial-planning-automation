import streamlit as st
import pandas as pd
import numpy as np

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
    margin-top:10px;
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
st.markdown('<div class="subtitle">Investment & Insurance Planner</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================================
# SIDEBAR GLOBAL INPUTS
# =====================================================

st.sidebar.header("Client Profile")
entry_age = st.sidebar.number_input("Entry Age", 18, 65, 30)
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0)/100
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0)/100

# =====================================================
# COMMON FUNCTIONS
# =====================================================

def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

def sip_required(target, rate, years):
    if years <= 0:
        return 0
    return target / (((1 + rate) ** years - 1) / rate)

def monte_carlo(target, sip, years, simulations=1000):
    success = 0
    for _ in range(simulations):
        corpus = 0
        for _ in range(years):
            annual_return = np.random.normal(expected_return, 0.15)
            corpus = (corpus + sip*12) * (1 + annual_return)
        if corpus >= target:
            success += 1
    return success / simulations

# =====================================================
# HOME PAGE
# =====================================================

if st.session_state.page == "home":

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("Children Planner", on_click=lambda: go("children"))

    with col2:
        st.button("SWP Calculator", on_click=lambda: go("swp"))
        st.button("Retirement Planner", on_click=lambda: go("retirement"))

    with col3:
        st.button("Term Insurance", on_click=lambda: go("term"))

# =====================================================
# CHILDREN PLANNER
# =====================================================

if st.session_state.page == "children":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Advanced Multi-Child Planning")

    num_children = st.number_input("Number of Children", 1, 4, 1)

    summary = []

    for i in range(num_children):

        st.markdown(f"## Child {i+1}")

        child_age = st.number_input(
            f"Child {i+1} Current Age",
            0, 18, 2,
            key=f"child_age_{i}"
        )

        # EDUCATION
        st.markdown("### 🎓 Education Goal")

        edu_age = st.number_input(
            "Education Goal Age",
            15, 30, 18,
            key=f"edu_age_{i}"
        )

        edu_cost = st.number_input(
            "Education Cost Today (₹)",
            value=2000000,
            key=f"edu_cost_{i}"
        )

        edu_years = edu_age - child_age
        edu_future = future_value(edu_cost, inflation, edu_years)
        edu_sip = sip_required(edu_future, expected_return, edu_years)
        edu_prob = monte_carlo(edu_future, edu_sip/12, edu_years)

        # MARRIAGE
        st.markdown("### 💍 Marriage Goal")

        mar_age = st.number_input(
            "Marriage Goal Age",
            18, 35, 24,
            key=f"mar_age_{i}"
        )

        mar_cost = st.number_input(
            "Marriage Cost Today (₹)",
            value=3000000,
            key=f"mar_cost_{i}"
        )

        mar_years = mar_age - child_age
        mar_future = future_value(mar_cost, inflation, mar_years)
        mar_sip = sip_required(mar_future, expected_return, mar_years)
        mar_prob = monte_carlo(mar_future, mar_sip/12, mar_years)

        summary.append([
            f"Child {i+1} - Education",
            edu_age,
            round(edu_future,0),
            round(edu_sip/12,0),
            f"{round(edu_prob*100,1)}%"
        ])

        summary.append([
            f"Child {i+1} - Marriage",
            mar_age,
            round(mar_future,0),
            round(mar_sip/12,0),
            f"{round(mar_prob*100,1)}%"
        ])

    df = pd.DataFrame(summary, columns=[
        "Goal",
        "Goal Age",
        "Future Cost (₹)",
        "Required Monthly SIP (₹)",
        "Success Probability"
    ])

    st.markdown("## Goal Summary")
    st.dataframe(df, use_container_width=True)

# =====================================================
# SWP CALCULATOR (START & END AGE)
# =====================================================

if st.session_state.page == "swp":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Advanced SWP Calculator")

    corpus = st.number_input("Initial Corpus (₹)", value=10000000)
    start_age = st.number_input("Withdrawal Start Age", 30, 80, 60)
    end_age = st.number_input("Withdrawal End Age", 40, 95, 80)
    monthly_withdrawal = st.number_input("Monthly Withdrawal (₹)", value=100000)

    balance = corpus
    table = []

    for age in range(entry_age, end_age + 1):

        if age < start_age:
            withdrawal = 0
            balance = balance * (1 + expected_return)
        else:
            withdrawal = monthly_withdrawal * 12
            balance = balance * (1 + expected_return) - withdrawal

        table.append([age, withdrawal, round(balance,0)])

        if balance <= 0:
            break

    df = pd.DataFrame(table, columns=[
        "Age",
        "Yearly Withdrawal",
        "Year End Corpus"
    ])

    st.dataframe(df, use_container_width=True)

    if balance > 0:
        st.success(f"Corpus Remaining at Age {end_age}: ₹ {balance:,.0f}")
    else:
        st.error("⚠ Corpus depleted before end age")

# =====================================================
# RETIREMENT PLANNER
# =====================================================

if st.session_state.page == "retirement":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    annual_expense = st.number_input("Annual Expense Today (₹)", value=900000)

    years = retirement_age - entry_age
    expense_at_ret = future_value(annual_expense, inflation, years)
    corpus_required = expense_at_ret * 25

    st.success(f"Required Retirement Corpus: ₹ {corpus_required:,.0f}")

# =====================================================
# TERM INSURANCE
# =====================================================

if st.session_state.page == "term":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance Calculator")

    annual_income = st.number_input("Annual Income (₹)", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - entry_age
    cover = annual_income * years_left

    st.success(f"Recommended Term Cover: ₹ {cover:,.0f}")

st.markdown("---")
st.caption("Monte Carlo based probability uses 15% volatility assumption. For illustration purposes only.")
