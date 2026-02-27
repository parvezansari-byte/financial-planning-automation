import streamlit as st
import pandas as pd
import numpy as np

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="Freedom", layout="wide")

# ---------------- DARK STYLE ---------------- #
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: white;
}
.big-title {
    font-size: 50px;
    font-weight: bold;
    text-align: center;
    color: #38bdf8;
}
.sub-title {
    text-align: center;
    color: #cbd5e1;
}
.button-style button {
    background: linear-gradient(90deg,#2563eb,#06b6d4);
    color: white;
    border-radius: 10px;
    height: 60px;
    width: 100%;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown('<div class="big-title">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interactive Wealth Planning Platform</div>', unsafe_allow_html=True)
st.divider()

# ---------------- SESSION NAV ---------------- #
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_home():
    st.session_state.page = "home"

# ---------------- HOME PAGE ---------------- #
if st.session_state.page == "home":

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("SIP Calculator"):
            st.session_state.page = "sip"

        if st.button("Children Planner"):
            st.session_state.page = "children"

    with col2:
        if st.button("SWP Calculator"):
            st.session_state.page = "swp"

        if st.button("Retirement Planner"):
            st.session_state.page = "retirement"

    with col3:
        if st.button("Term Insurance"):
            st.session_state.page = "term"

# ================= SIP CALCULATOR ================= #
elif st.session_state.page == "sip":

    st.button("⬅ Back", on_click=go_home)
    st.header("SIP Calculator")

    sip = st.number_input("Monthly SIP (₹)", value=5000)
    years = st.number_input("Years", value=10)
    return_rate = st.number_input("Expected Return (%)", value=12.0)

    monthly_rate = return_rate / 100 / 12
    months = years * 12

    future_value = sip * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)

    st.success(f"Final Corpus: ₹ {int(future_value):,}")

    # Yearly Wealth Table
    data = []
    corpus = 0
    for year in range(1, int(years) + 1):
        corpus = sip * 12 * year * (1 + return_rate/100)
        data.append([year, sip*12, int(corpus)])

    df = pd.DataFrame(data, columns=["Year", "Yearly Investment", "Corpus"])
    st.dataframe(df, use_container_width=True)
    st.line_chart(df.set_index("Year")["Corpus"])

# ================= SWP ================= #
elif st.session_state.page == "swp":

    st.button("⬅ Back", on_click=go_home)
    st.header("SWP Calculator")

    corpus = st.number_input("Current Corpus (₹)", value=1000000)
    withdrawal = st.number_input("Monthly Withdrawal (₹)", value=20000)
    return_rate = st.number_input("Expected Return (%)", value=8.0)

    months = 0
    monthly_rate = return_rate/100/12

    balance = corpus
    data = []

    while balance > 0 and months < 600:
        balance = balance * (1 + monthly_rate) - withdrawal
        months += 1
        data.append([months, max(balance,0)])

    years = months // 12

    st.success(f"Corpus lasts approx: {years} years")

    df = pd.DataFrame(data, columns=["Month", "Balance"])
    st.line_chart(df.set_index("Month"))

# ================= CHILDREN PLANNER ================= #
elif st.session_state.page == "children":

    st.button("⬅ Back", on_click=go_home)
    st.header("Children Planner")

    inflation = st.number_input("Education Inflation (%)", value=8.0)

    total_sip = 0
    results = []

    for i in range(1,5):
        st.subheader(f"Child {i}")

        current_age = st.number_input(f"Current Age Child {i}", value=2, key=f"age{i}")
        goal_age = st.number_input(f"Graduation Age Child {i}", value=21, key=f"goal{i}")
        goal_amount = st.number_input(f"Graduation Cost Today (₹)", value=2000000, key=f"cost{i}")

        years = goal_age - current_age
        future_cost = goal_amount * (1 + inflation/100) ** years
        sip_required = future_cost / (years * 12)

        total_sip += sip_required
        results.append([f"Child {i}", int(future_cost), int(sip_required)])

    df = pd.DataFrame(results, columns=["Child", "Future Cost", "Monthly SIP Needed"])
    st.dataframe(df, use_container_width=True)

    st.success(f"Total SIP Required For All Children: ₹ {int(total_sip):,}")

# ================= RETIREMENT ================= #
elif st.session_state.page == "retirement":

    st.button("⬅ Back", on_click=go_home)
    st.header("Retirement Planner")

    current_age = st.number_input("Current Age", value=30)
    retire_age = st.number_input("Retirement Age", value=60)
    expense = st.number_input("Annual Expense Today (₹)", value=600000)
    inflation = st.number_input("Inflation (%)", value=6.0)
    return_rate = st.number_input("Return (%)", value=10.0)

    years = retire_age - current_age
    future_expense = expense * (1 + inflation/100) ** years
    corpus_needed = future_expense / (return_rate/100)

    st.success(f"Required Retirement Corpus: ₹ {int(corpus_needed):,}")

    ages = list(range(int(current_age), int(retire_age)+1))
    corpus_projection = []

    corpus = 0
    for age in ages:
        corpus = corpus * (1 + return_rate/100) + 500000
        corpus_projection.append(int(corpus))

    df = pd.DataFrame({"Age": ages, "Corpus": corpus_projection})
    st.line_chart(df.set_index("Age"))

# ================= TERM INSURANCE ================= #
elif st.session_state.page == "term":

    st.button("⬅ Back", on_click=go_home)
    st.header("Term Insurance Calculator")

    income = st.number_input("Annual Income (₹)", value=1000000)
    expenses = st.number_input("Annual Expenses (₹)", value=500000)
    years = st.number_input("Years Support Needed", value=20)

    cover = (income - expenses) * years

    st.success(f"Recommended Term Cover: ₹ {int(cover):,}")
