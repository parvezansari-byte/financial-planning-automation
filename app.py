import streamlit as st
import pandas as pd
import numpy as np

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
    background: linear-gradient(90deg,#2563EB,#06B6D4);
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
    if years <= 0 or rate == 0:
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
        st.button("House Planning", on_click=lambda: go("house"))
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
    total_invested = 0
    table = []

    for y in range(1, years + 1):
        yearly = monthly_sip * 12
        total_invested += yearly
        corpus = (corpus + yearly) * (1 + expected_return)
        table.append([y, yearly, total_invested, round(corpus, 0)])

    df = pd.DataFrame(table,
        columns=["Year", "Yearly Investment", "Total Invested", "Year End Corpus"]
    )

    st.dataframe(df, use_container_width=True)
    st.success(f"Total Invested: ₹ {total_invested:,.0f}")
    st.success(f"Final Corpus: ₹ {corpus:,.0f}")

# =====================================================
# ADVANCED SWP
# =====================================================
if st.session_state.page == "swp":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Advanced SWP Retirement Engine")

    corpus = st.number_input("Initial Corpus (₹)", value=10000000)
    withdrawal_start_age = st.number_input("Withdrawal Start Age", min_value=current_age, max_value=100, value=60)
    withdrawal_end_age = st.number_input("Withdrawal End Age", min_value=withdrawal_start_age+1, max_value=100, value=85)
    withdrawal_per_year = st.number_input("Initial Withdrawal Per Year (₹)", value=1200000)
    withdrawal_inflation = st.number_input("Withdrawal Inflation (%)", value=6.0)/100

    balance = corpus
    withdrawal = withdrawal_per_year
    table = []

    for age in range(withdrawal_start_age, withdrawal_end_age+1):

        balance = balance * (1 + expected_return)
        balance -= withdrawal

        table.append([age, round(withdrawal,0), round(balance,0)])
        withdrawal *= (1 + withdrawal_inflation)

        if balance <= 0:
            break

    df = pd.DataFrame(table, columns=["Age","Withdrawal","Year End Corpus"])
    st.dataframe(df, use_container_width=True)

    # SWR
    swr = (withdrawal_per_year / corpus) * 100
    st.write(f"Safe Withdrawal Rate: {swr:.2f}%")

    # Monte Carlo
    simulations = 300
    success = 0
    years = withdrawal_end_age - withdrawal_start_age

    for _ in range(simulations):
        mc_balance = corpus
        mc_withdraw = withdrawal_per_year

        for _ in range(years):
            random_return = np.random.normal(expected_return, 0.15)
            mc_balance = mc_balance * (1 + random_return)
            mc_balance -= mc_withdraw
            mc_withdraw *= (1 + withdrawal_inflation)
            if mc_balance <= 0:
                break

        if mc_balance > 0:
            success += 1

    probability = (success / simulations) * 100
    st.write(f"Survival Probability: {probability:.1f}%")

# =====================================================
# RETIREMENT PLANNER
# =====================================================
if st.session_state.page == "retirement":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Planner")

    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    annual_expense = st.number_input("Annual Expense Today (₹)", value=600000)

    years_to_ret = retirement_age - current_age
    expense_at_ret = annual_expense * ((1 + inflation) ** years_to_ret)
    required_corpus = expense_at_ret * 25

    st.table(pd.DataFrame({
        "Metric":["Expense at Retirement","Required Corpus"],
        "Value":[f"₹ {expense_at_ret:,.0f}",f"₹ {required_corpus:,.0f}"]
    }))

    sip = sip_required(required_corpus, expected_return, years_to_ret)
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
        goal_age = st.number_input(f"Goal Age Child {i+1}", 10, 30, 21, key=f"goal{i}")
        cost = st.number_input(f"Goal Cost (₹) Child {i+1}", value=2000000, key=f"cost{i}")

        years = goal_age - child_age
        future_cost = future_value(cost, inflation, years)
        sip = sip_required(future_cost, expected_return, years)

        summary.append([f"Child {i+1}",goal_age,round(future_cost,0),round(sip/12,0)])

    df = pd.DataFrame(summary, columns=["Child","Goal Age","Future Cost","Monthly SIP Required"])
    st.dataframe(df, use_container_width=True)

# =====================================================
# TERM INSURANCE
# =====================================================
if st.session_state.page == "term":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance")

    annual_income = st.number_input("Annual Income (₹)", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - current_age
    cover = annual_income * years_left

    st.success(f"Recommended Cover: ₹ {cover:,.0f}")

# =====================================================
# HOUSE PLANNING
# =====================================================
if st.session_state.page == "house":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("House Planning")

    house_cost_today = st.number_input("House Cost Today (₹)", value=10000000)
    years_to_buy = st.number_input("Years to Purchase", value=5)
    down_payment_percent = st.number_input("Down Payment (%)", value=20.0)/100
    home_loan_rate = st.number_input("Home Loan Interest Rate (%)", value=8.5)/100
    loan_tenure_years = st.number_input("Loan Tenure (Years)", value=20)

    future_house_cost = house_cost_today * ((1 + inflation) ** years_to_buy)
    down_payment = future_house_cost * down_payment_percent
    sip_needed = sip_required(down_payment, expected_return, years_to_buy)

    loan_amount = future_house_cost - down_payment
    monthly_rate = home_loan_rate/12
    months = loan_tenure_years*12

    if monthly_rate>0:
        emi = loan_amount*monthly_rate*((1+monthly_rate)**months)/(((1+monthly_rate)**months)-1)
    else:
        emi = loan_amount/months

    total_interest = (emi*months) - loan_amount

    st.table(pd.DataFrame({
        "Metric":["Future House Cost","Down Payment","Loan Amount","Monthly EMI","Total Interest"],
        "Value":[
            f"₹ {future_house_cost:,.0f}",
            f"₹ {down_payment:,.0f}",
            f"₹ {loan_amount:,.0f}",
            f"₹ {emi:,.0f}",
            f"₹ {total_interest:,.0f}"
        ]
    }))

    st.success(f"Required Monthly SIP for Down Payment: ₹ {sip_needed/12:,.0f}")

# =====================================================
# CASHFLOW PLANNER
# =====================================================
if st.session_state.page == "cashflow":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Cashflow Planner")

    plan_till_age = st.number_input("Plan Till Age", 50, 100, 85)
    annual_income = st.number_input("Annual Income (₹)", value=1800000)
    annual_expense = st.number_input("Annual Expense (₹)", value=900000)
    annual_investment = st.number_input("Annual Investment (₹)", value=300000)
    current_corpus = st.number_input("Current Corpus (₹)", value=1000000)

    years = plan_till_age - current_age
    corpus = current_corpus
    table = []

    for year in range(1, years+1):
        surplus = annual_income - annual_expense - annual_investment
        corpus = corpus * (1 + expected_return)
        corpus += annual_investment

        table.append([
            current_age + year,
            annual_income,
            annual_expense,
            annual_investment,
            surplus,
            round(corpus,0)
        ])

    df = pd.DataFrame(table,
        columns=["Age","Income","Expense","Investment","Net Surplus","Year End Corpus"]
    )

    st.dataframe(df, use_container_width=True)
    st.success(f"Projected Corpus at Age {plan_till_age}: ₹ {corpus:,.0f}")

st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration Only")
