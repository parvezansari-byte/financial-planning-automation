import streamlit as st
import pandas as pd
import numpy as np

# =============================================
# PAGE CONFIG
# =============================================
st.set_page_config(page_title="Freedom", layout="wide")

# =============================================
# DARK THEME
# =============================================
st.markdown("""
<style>

.stApp{
background-color:#0F172A;
}

.header-box{
background:linear-gradient(90deg,#1E3A8A,#0EA5E9);
padding:25px;
border-radius:14px;
text-align:center;
color:white;
font-size:42px;
font-weight:700;
}

.subtitle{
text-align:center;
color:#93C5FD;
font-size:18px;
margin-bottom:25px;
}

.stButton > button{
background:linear-gradient(90deg,#2563EB,#0EA5E9);
color:white;
border-radius:8px;
height:45px;
font-weight:600;
border:none;
}

thead tr th{
background-color:#2563EB !important;
color:white !important;
}

tbody tr td{
color:#E2E8F0 !important;
}

tbody tr:nth-child(even){
background-color:#111827 !important;
}

section[data-testid="stSidebar"]{
background-color:#111827;
}

label{
color:#CBD5E1 !important;
}

</style>
""", unsafe_allow_html=True)

# =============================================
# NAVIGATION
# =============================================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page

# =============================================
# HEADER
# =============================================
st.markdown('<div class="header-box">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Integrated Wealth Planning Platform</div>', unsafe_allow_html=True)
st.markdown("---")

# =============================================
# SIDEBAR
# =============================================
st.sidebar.header("Client Profile")

current_age = st.sidebar.number_input("Current Age",25,70,30)

inflation = st.sidebar.number_input("Inflation (%)",0.0,15.0,6.0)/100

expected_return = st.sidebar.number_input("Expected Return (%)",0.0,20.0,12.0)/100

# =============================================
# FUNCTIONS
# =============================================
def future_value(pv,rate,years):
    return pv*(1+rate)**years

def sip_required(target,rate,years):
    if years<=0:
        return 0
    return target/(((1+rate)**years-1)/rate)

# =============================================
# HOME
# =============================================
if st.session_state.page=="home":

    col1,col2,col3 = st.columns(3)

    with col1:
        st.button("SIP Calculator",on_click=lambda:go("sip"))
        st.button("Children Planner",on_click=lambda:go("children"))

    with col2:
        st.button("SWP Calculator",on_click=lambda:go("swp"))
        st.button("Retirement Planner",on_click=lambda:go("retirement"))

    with col3:
        st.button("Term Insurance",on_click=lambda:go("term"))
        st.button("Cashflow Planner",on_click=lambda:go("cashflow"))

# =============================================
# SIP CALCULATOR
# =============================================
if st.session_state.page=="sip":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Monthly SIP (₹)",value=5000)

    years = st.number_input("Investment Years",value=10)

    corpus=0

    table=[]

    for y in range(years):

        yearly = monthly_sip*12

        corpus = (corpus+yearly)*(1+expected_return)

        invested = yearly*(y+1)

        table.append([y+1,invested,round(corpus,0)])

    df = pd.DataFrame(table,columns=["Year","Total Invested","Corpus Value"])

    st.dataframe(df,use_container_width=True)

    st.success(f"Final Corpus : ₹ {corpus:,.0f}")

# =============================================
# SWP CALCULATOR
# =============================================
if st.session_state.page=="swp":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("SWP Calculator")

    corpus = st.number_input("Initial Corpus (₹)",value=10000000)

    start_age = st.number_input("Withdrawal Start Age",30,90,60)

    end_age = st.number_input("Withdrawal End Age",40,100,80)

    withdrawal = st.number_input("Withdrawal Per Year (₹)",value=1200000)

    balance=corpus

    rows=[]

    for age in range(start_age,end_age):

        balance = balance*(1+expected_return)-withdrawal

        rows.append([age,withdrawal,round(balance,0)])

        if balance<=0:
            break

    df = pd.DataFrame(rows,columns=["Age","Withdrawal Per Year","Year End Corpus"])

    st.dataframe(df,use_container_width=True)

# =============================================
# CHILDREN PLANNER PRO
# =============================================
if st.session_state.page=="children":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("Children Planner")

    num_children = st.number_input("Number of Children",1,4,1)

    results=[]

    for c in range(num_children):

        st.markdown(f"### Child {c+1}")

        child_age = st.number_input("Child Age",0,18,2,key=f"childage{c}")

        goals = {
        "10th Board":15,
        "12th Board":17,
        "Graduation":21,
        "Masters":24,
        "Marriage":28
        }

        for goal,goal_age in goals.items():

            cost_today = st.number_input(
            f"{goal} Cost Today (₹)",
            value=2000000,
            key=f"{goal}{c}")

            years = goal_age-child_age

            if years>0:

                future_cost = future_value(cost_today,inflation,years)

                sip = sip_required(future_cost,expected_return,years)

                monthly_sip = sip/12

                lumpsum = future_cost/((1+expected_return)**years)

                simulations=200

                success=0

                for s in range(simulations):

                    corpus=0

                    for y in range(years):

                        yearly = monthly_sip*12

                        random_return = np.random.normal(expected_return,0.15)

                        corpus=(corpus+yearly)*(1+random_return)

                    if corpus>=future_cost:
                        success+=1

                probability = round((success/simulations)*100)

                results.append([
                f"Child {c+1}",
                goal,
                goal_age,
                round(future_cost),
                round(monthly_sip),
                round(lumpsum),
                probability
                ])

    df = pd.DataFrame(results,columns=[
    "Child",
    "Goal",
    "Goal Age",
    "Future Cost",
    "Monthly SIP Required",
    "Lumpsum Required Today",
    "Success Probability %"
    ])

    st.dataframe(df,use_container_width=True)

    total_sip = df["Monthly SIP Required"].sum()

    st.success(f"Total SIP Required : ₹ {total_sip:,.0f}")

# =============================================
# RETIREMENT PLANNER
# =============================================
if st.session_state.page=="retirement":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("Retirement Planner")

    retirement_age = st.number_input("Retirement Age",50,75,60)

    life_expectancy = st.number_input("Plan Till Age",70,100,90)

    monthly_expense = st.number_input("Current Monthly Expense",value=50000)

    years_to_ret = retirement_age-current_age

    retirement_years = life_expectancy-retirement_age

    expense_at_ret = monthly_expense*12*((1+inflation)**years_to_ret)

    required_corpus = expense_at_ret*retirement_years

    st.success(f"Required Retirement Corpus : ₹ {required_corpus:,.0f}")

# =============================================
# TERM INSURANCE
# =============================================
if st.session_state.page=="term":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("Term Insurance Calculator")

    income = st.number_input("Annual Income",value=2400000)

    retirement_age = st.number_input("Retirement Age",45,75,60)

    years_left = retirement_age-current_age

    cover = income*years_left

    st.success(f"Recommended Cover : ₹ {cover:,.0f}")

# =============================================
# CASHFLOW PLANNER
# =============================================
if st.session_state.page=="cashflow":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("Personal Cashflow Statement")

    st.markdown("### Cash Inflows")

    salary = st.number_input("Salary",value=0)

    side_income = st.number_input("Side Income",value=0)

    investment_income = st.number_input("Investment Income",value=0)

    other_income = st.number_input("Other Income",value=0)

    inflow = salary+side_income+investment_income+other_income

    st.markdown("### Expenses")

    rent = st.number_input("Rent/Mortgage",value=0)

    utilities = st.number_input("Utilities",value=0)

    groceries = st.number_input("Groceries",value=0)

    transport = st.number_input("Transportation",value=0)

    insurance = st.number_input("Insurance",value=0)

    investments = st.number_input("Investments",value=0)

    outflow = rent+utilities+groceries+transport+insurance+investments

    net = inflow-outflow

    data = {
    "Category":["Total Inflow","Total Outflow","Net Cashflow"],
    "Amount":[inflow,outflow,net]
    }

    df = pd.DataFrame(data)

    st.table(df)

    if net>0:
        st.success(f"Monthly Surplus : ₹ {net:,.0f}")
    else:
        st.error("You are in deficit")

st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration Only")
