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
# HOME PAGE
# =============================================
if st.session_state.page=="home":

    col1,col2,col3 = st.columns(3)

    with col1:
        st.button("SIP Calculator",on_click=lambda:go("sip"))
        st.button("Children Planner",on_click=lambda:go("children"))
        st.button("Car Purchase Planner",on_click=lambda:go("car"))

    with col2:
        st.button("SWP Calculator",on_click=lambda:go("swp"))
        st.button("Retirement Planner",on_click=lambda:go("retirement"))
        st.button("iPhone Purchase Planner",on_click=lambda:go("iphone"))

    with col3:
    st.button("Term Insurance",on_click=lambda:go("term"))
    st.button("Cashflow Planner",on_click=lambda:go("cashflow"))
    st.button("Portfolio Allocation",on_click=lambda:go("portfolio"))

# =============================================
# SIP CALCULATOR
# =============================================
if st.session_state.page=="sip":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Monthly SIP (₹)",value=5000)

    years = st.number_input("Investment Years",value=10)

    step_up = st.number_input("Annual Step-Up (%)",0.0,50.0,10.0)/100

    corpus = 0
    invested = 0
    table=[]

    for y in range(1,years+1):

        yearly_sip = monthly_sip*12

        invested += yearly_sip

        corpus = (corpus + yearly_sip)*(1+expected_return)

        table.append([
            y,
            round(monthly_sip,0),
            round(yearly_sip,0),
            round(invested,0),
            round(corpus,0)
        ])

        monthly_sip = monthly_sip*(1+step_up)

    df = pd.DataFrame(
        table,
        columns=[
            "Year",
            "Monthly SIP",
            "Yearly Investment",
            "Total Invested",
            "Year End Corpus"
        ]
    )

    st.dataframe(df,use_container_width=True)

    gain = corpus-invested

    c1,c2,c3 = st.columns(3)

    c1.metric("Total Invested",f"₹ {invested:,.0f}")
    c2.metric("Total Gain",f"₹ {gain:,.0f}")
    c3.metric("Final Corpus",f"₹ {corpus:,.0f}")

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

                probability = np.random.randint(90,99)

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

    corpus = expense_at_ret*retirement_years

    st.success(f"Required Retirement Corpus : ₹ {corpus:,.0f}")

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

    st.subheader("Personal Cashflow Planner")

    salary = st.number_input("Salary",0)
    side_income = st.number_input("Side Income",0)
    investment_income = st.number_input("Investment Income",0)
    other_income = st.number_input("Other Income",0)

    inflow = salary+side_income+investment_income+other_income

    rent = st.number_input("Rent/Mortgage",0)
    utilities = st.number_input("Utilities",0)
    groceries = st.number_input("Groceries",0)
    transport = st.number_input("Transport",0)
    insurance = st.number_input("Insurance",0)
    investments = st.number_input("Investments",0)

    outflow = rent+utilities+groceries+transport+insurance+investments

    net = inflow-outflow

    df = pd.DataFrame({
    "Category":["Total Inflow","Total Outflow","Net Cashflow"],
    "Amount":[inflow,outflow,net]
    })

    st.table(df)

# =============================================
# CAR PURCHASE PLANNER
# =============================================
if st.session_state.page=="car":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("Car Purchase Planner 🚗")

    car_price = st.number_input("Car Price Today",value=1000000)

    years = st.number_input("Years to Buy Car",value=5)

    future_price = car_price*((1+inflation)**years)

    sip = sip_required(future_price,expected_return,years)/12

    st.metric("Future Price",f"₹ {future_price:,.0f}")

    st.metric("Monthly SIP Required",f"₹ {sip:,.0f}")

# =============================================
# IPHONE PURCHASE PLANNER
# =============================================
if st.session_state.page=="iphone":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("iPhone Purchase Planner 📱")

    iphone_price = st.number_input("iPhone Price Today",value=120000)

    months = st.number_input("Months to Buy",value=12)

    rate = expected_return/12

    future_price = iphone_price*(1+inflation)**(months/12)

    sip = future_price/(((1+rate)**months-1)/rate)

    st.metric("Future Price",f"₹ {future_price:,.0f}")

    st.metric("Monthly Saving Needed",f"₹ {sip:,.0f}")

st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration Only")
# =============================================
# PORTFOLIO ALLOCATION
# =============================================
if st.session_state.page=="portfolio":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("Portfolio Allocation")

    total_investment = st.number_input("Total Investment Amount (₹)",value=1000000)

    st.markdown("### Asset Allocation (%)")

    equity_pct = st.slider("Equity %",0,100,50)
    debt_pct = st.slider("Debt %",0,100,30)
    gold_pct = st.slider("Gold %",0,100,10)
    realestate_pct = st.slider("Real Estate %",0,100,5)
    cash_pct = st.slider("Cash / Liquid %",0,100,5)

    total_pct = equity_pct+debt_pct+gold_pct+realestate_pct+cash_pct

    if total_pct != 100:
        st.warning(f"Allocation Total = {total_pct}% (should be 100%)")

    equity_amt = total_investment*(equity_pct/100)
    debt_amt = total_investment*(debt_pct/100)
    gold_amt = total_investment*(gold_pct/100)
    realestate_amt = total_investment*(realestate_pct/100)
    cash_amt = total_investment*(cash_pct/100)

    data = {
    "Asset Class":[
    "Equity",
    "Debt",
    "Gold",
    "Real Estate",
    "Cash / Liquid"
    ],

    "Allocation %":[
    equity_pct,
    debt_pct,
    gold_pct,
    realestate_pct,
    cash_pct
    ],

    "Amount (₹)":[
    equity_amt,
    debt_amt,
    gold_amt,
    realestate_amt,
    cash_amt
    ]
    }

    df = pd.DataFrame(data)

    st.dataframe(df,use_container_width=True)
