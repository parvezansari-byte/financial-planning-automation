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
# SIDEBAR GLOBAL SETTINGS
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
    invested = 0
    table = []

    for y in range(1, years+1):
        yearly = monthly_sip * 12
        invested += yearly
        corpus = (corpus + yearly) * (1 + expected_return)
        table.append([y, yearly, invested, round(corpus,0)])

    df = pd.DataFrame(table,
        columns=["Year","Yearly Investment","Total Invested","Year End Corpus"]
    )

    st.dataframe(df, use_container_width=True)
    st.success(f"Final Corpus: ₹ {corpus:,.0f}")

# =====================================================
# SWP CALCULATOR
# =====================================================
if st.session_state.page == "swp":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Advanced SWP")

    corpus = st.number_input("Initial Corpus (₹)", value=10000000)
    start_age = st.number_input("Withdrawal Start Age", min_value=current_age, value=60)
    end_age = st.number_input("Withdrawal End Age", min_value=start_age+1, value=85)
    withdrawal = st.number_input("Initial Withdrawal Per Year (₹)", value=1200000)
    withdrawal_inflation = st.number_input("Withdrawal Inflation (%)", value=6.0)/100

    balance = corpus
    table = []

    for age in range(start_age, end_age+1):
        balance = balance * (1 + expected_return)
        balance -= withdrawal
        table.append([age, round(withdrawal,0), round(balance,0)])
        withdrawal *= (1 + withdrawal_inflation)
        if balance <= 0:
            break

    df = pd.DataFrame(table,
        columns=["Age","Withdrawal","Year End Corpus"]
    )

    st.dataframe(df, use_container_width=True)

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

# =====================================================
# PRO CHILDREN PLANNER
# =====================================================
if st.session_state.page == "children":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Children Financial Planning (Pro)")

    num_children = st.number_input("Number of Children", 1, 4, 1)

    education_inflation = st.number_input(
        "Education Inflation (%)", 0.0, 20.0, 10.0
    ) / 100

    marriage_inflation = st.number_input(
        "Marriage Inflation (%)", 0.0, 20.0, 8.0
    ) / 100

    step_up = st.number_input(
        "Annual SIP Step Up (%)", 0.0, 20.0, 10.0
    ) / 100

    results = []

    for c in range(num_children):

        st.markdown(f"### Child {c+1}")

        child_age = st.number_input(
            f"Child {c+1} Current Age",
            0, 18, 2,
            key=f"childage{c}"
        )

        goals = {
            "10th Board": (15, education_inflation),
            "12th Board": (17, education_inflation),
            "Graduation": (21, education_inflation),
            "Masters": (24, education_inflation),
            "Marriage": (28, marriage_inflation)
        }

        for goal, (goal_age, infl) in goals.items():

            cost_today = st.number_input(
                f"{goal} Cost Today (₹) Child {c+1}",
                value=2000000,
                key=f"{goal}_{c}"
            )

            years = goal_age - child_age

            if years > 0:

                future_cost = cost_today * ((1 + infl) ** years)

                sip = sip_required(
                    future_cost,
                    expected_return,
                    years
                )

                monthly_sip = sip / 12

                # Monte Carlo Probability
                simulations = 500
                success = 0

                for _ in range(simulations):

                    corpus = 0

                    for y in range(years):

                        yearly_sip = monthly_sip * 12 * ((1+step_up)**y)

                        random_return = np.random.normal(
                            expected_return,
                            0.15
                        )

                        corpus = (corpus + yearly_sip) * (1 + random_return)

                    if corpus >= future_cost:
                        success += 1

                probability = round((success/simulations)*100)

                results.append([
                    f"Child {c+1}",
                    goal,
                    goal_age,
                    round(future_cost),
                    round(monthly_sip),
                    probability
                ])

    df = pd.DataFrame(
        results,
        columns=[
            "Child",
            "Goal",
            "Goal Age",
            "Future Cost (₹)",
            "Monthly SIP Required (₹)",
            "Success Probability %"
        ]
    )

    st.dataframe(df, use_container_width=True)

    total_sip = df["Monthly SIP Required (₹)"].sum()

    st.success(f"Total Monthly SIP Needed: ₹ {total_sip:,.0f}")

# =====================================================
# TERM INSURANCE
# =====================================================
if st.session_state.page == "term":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance")

    income = st.number_input("Annual Income (₹)", value=2400000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)

    years_left = retirement_age - current_age
    cover = income * years_left

    st.success(f"Recommended Cover: ₹ {cover:,.0f}")

# =====================================================
# HOUSE PLANNING
# =====================================================
if st.session_state.page == "house":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("House Planning")

    house_cost = st.number_input("House Cost Today (₹)", value=10000000)
    years = st.number_input("Years to Buy", value=5)

    future_house_cost = house_cost * ((1 + inflation) ** years)
    st.success(f"Future House Cost: ₹ {future_house_cost:,.0f}")

# =====================================================
# CASHFLOW PLANNER (STRUCTURED + PROJECTION)
# =====================================================
if st.session_state.page == "cashflow":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Detailed Cashflow Planner")

    plan_till_age = st.number_input("Plan Till Age", 50, 100, 85)

    # INFLOWS
    salary = st.number_input("Salary / Wages", value=0)
    side_income = st.number_input("Side Income", value=0)
    investment_income = st.number_input("Investment Income", value=0)
    other_income = st.number_input("Other Income", value=0)

    total_inflow = salary + side_income + investment_income + other_income

    # OUTFLOWS
    rent = st.number_input("Rent / Mortgage", value=0)
    utilities = st.number_input("Utilities", value=0)
    debt = st.number_input("Debt Payments", value=0)
    insurance = st.number_input("Insurance", value=0)
    groceries = st.number_input("Groceries", value=0)
    dining = st.number_input("Dining / Entertainment", value=0)
    savings = st.number_input("Savings & Investments", value=0)

    total_outflow = rent + utilities + debt + insurance + groceries + dining + savings

    net_cashflow = total_inflow - total_outflow

    summary = pd.DataFrame({
        "Category":["Total Inflow","Total Outflow","Net Cashflow"],
        "Amount":[total_inflow,total_outflow,net_cashflow]
    })

    st.dataframe(summary, use_container_width=True)

    years = plan_till_age - current_age
    corpus = 0
    projection = []

    for i in range(1, years+1):
        inflow_adj = total_inflow * ((1 + inflation) ** i)
        outflow_adj = total_outflow * ((1 + inflation) ** i)
        surplus = inflow_adj - outflow_adj
        corpus = corpus * (1 + expected_return)
        corpus += surplus

        projection.append([
            current_age+i,
            round(surplus,0),
            round(corpus,0)
        ])

    df_projection = pd.DataFrame(projection,
        columns=["Age","Net Surplus","Projected Corpus"]
    )

    st.dataframe(df_projection, use_container_width=True)

    st.success(f"Projected Corpus at Age {plan_till_age}: ₹ {corpus:,.0f}")

st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration Only")
