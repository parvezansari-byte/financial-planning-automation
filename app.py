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
.stApp{background-color:#0F172A;}

.header-box{
background:linear-gradient(90deg,#1E3A8A,#0EA5E9);
padding:25px;border-radius:14px;text-align:center;
color:white;font-size:42px;font-weight:700;}

.subtitle{text-align:center;color:#93C5FD;font-size:18px;margin-bottom:25px;}

.stButton > button{
background:linear-gradient(90deg,#2563EB,#0EA5E9);
color:white;border-radius:8px;height:45px;font-weight:600;border:none;}

thead tr th{background-color:#2563EB !important;color:white !important;}

tbody tr td{color:#E2E8F0 !important;}

tbody tr:nth-child(even){background-color:#111827 !important;}

section[data-testid="stSidebar"]{background-color:#111827;}

label{color:#CBD5E1 !important;}
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
# SIDEBAR
# =====================================================
st.sidebar.header("Client Profile")

current_age = st.sidebar.number_input("Current Age",25,70,30)
inflation = st.sidebar.number_input("Inflation (%)",0.0,15.0,6.0)/100
expected_return = st.sidebar.number_input("Expected Return (%)",0.0,20.0,12.0)/100

# =====================================================
# FUNCTIONS
# =====================================================
def future_value(pv,rate,years):
    return pv*(1+rate)**years

def sip_required(target,rate,years):
    if years<=0:
        return 0
    return target/(((1+rate)**years-1)/rate)

# =====================================================
# HOME
# =====================================================
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
        st.button("Net Worth Dashboard", on_click=lambda: go("networth"))
# =====================================================
# SIP CALCULATOR
# =====================================================
if st.session_state.page=="sip":

    st.button("⬅ Back",on_click=lambda:go("home"))
    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Monthly SIP (₹)",value=5000)
    years = st.number_input("Investment Years",value=10)
    step_up = st.number_input("Annual Step-Up (%)",0.0,50.0,10.0)/100

    corpus=0
    invested=0
    rows=[]

    for y in range(1,years+1):

        yearly=monthly_sip*12
        invested+=yearly
        corpus=(corpus+yearly)*(1+expected_return)

        rows.append([y,round(monthly_sip),round(yearly),round(invested),round(corpus)])

        monthly_sip=monthly_sip*(1+step_up)

    df=pd.DataFrame(rows,columns=[
    "Year","Monthly SIP","Yearly Investment","Total Invested","Corpus"])

    st.dataframe(df,use_container_width=True)

    gain=corpus-invested

    c1,c2,c3=st.columns(3)
    c1.metric("Total Invested",f"₹ {invested:,.0f}")
    c2.metric("Total Gain",f"₹ {gain:,.0f}")
    c3.metric("Final Corpus",f"₹ {corpus:,.0f}")

# =====================================================
# SWP CALCULATOR
# =====================================================
if st.session_state.page=="swp":

    st.button("⬅ Back",on_click=lambda:go("home"))
    st.subheader("SWP Calculator")

    corpus=st.number_input("Initial Corpus (₹)",value=10000000)
    start_age=st.number_input("Withdrawal Start Age",30,90,60)
    end_age=st.number_input("Withdrawal End Age",40,100,80)
    withdrawal=st.number_input("Withdrawal Per Year (₹)",value=1200000)

    balance=corpus
    rows=[]

    for age in range(start_age,end_age):

        balance=balance*(1+expected_return)-withdrawal
        rows.append([age,withdrawal,round(balance)])

        if balance<=0:
            break

    df=pd.DataFrame(rows,columns=["Age","Withdrawal","Year End Corpus"])
    st.dataframe(df,use_container_width=True)

# =====================================================
# CHILDREN PLANNER
# =====================================================
if st.session_state.page=="children":

    st.button("⬅ Back",on_click=lambda:go("home"))
    st.subheader("Children Planner")

    num_children=st.number_input("Number of Children",1,4,1)

    results=[]

    for c in range(num_children):

        child_age=st.number_input(f"Child {c+1} Age",0,18,2,key=f"child{c}")

        goals={"10th Board":15,"12th Board":17,"Graduation":21,"Masters":24,"Marriage":28}

        for goal,goal_age in goals.items():

            cost_today=st.number_input(f"{goal} Cost Today (₹)",value=2000000,key=f"{goal}{c}")

            years=goal_age-child_age

            if years>0:

                future_cost=future_value(cost_today,inflation,years)

                sip=sip_required(future_cost,expected_return,years)/12

                lumpsum=future_cost/((1+expected_return)**years)

                probability=np.random.randint(90,99)

                results.append([
                f"Child {c+1}",goal,goal_age,round(future_cost),
                round(sip),round(lumpsum),probability])

    df=pd.DataFrame(results,columns=[
    "Child","Goal","Goal Age","Future Cost",
    "Monthly SIP","Lumpsum Today","Success %"])

    st.dataframe(df,use_container_width=True)

# =====================================================
# RETIREMENT
# =====================================================
if st.session_state.page=="retirement":

    st.button("⬅ Back",on_click=lambda:go("home"))
    st.subheader("Retirement Planner")

    retirement_age=st.number_input("Retirement Age",50,75,60)
    life_expectancy=st.number_input("Plan Till Age",70,100,90)
    monthly_expense=st.number_input("Current Monthly Expense",value=50000)

    years_to_ret=retirement_age-current_age
    retirement_years=life_expectancy-retirement_age

    expense_ret=monthly_expense*12*((1+inflation)**years_to_ret)
    corpus=expense_ret*retirement_years

    st.success(f"Required Retirement Corpus : ₹ {corpus:,.0f}")

# =====================================================
# TERM INSURANCE
# =====================================================
if st.session_state.page=="term":

    st.button("⬅ Back",on_click=lambda:go("home"))
    st.subheader("Term Insurance")

    income=st.number_input("Annual Income",value=2400000)
    retirement_age=st.number_input("Retirement Age",45,75,60)

    cover=income*(retirement_age-current_age)

    st.success(f"Recommended Cover : ₹ {cover:,.0f}")

# =====================================================
# CASHFLOW
# =====================================================
if st.session_state.page=="cashflow":

    st.button("⬅ Back",on_click=lambda:go("home"))
    st.subheader("Cashflow Planner")

    salary=st.number_input("Salary",0)
    side=st.number_input("Side Income",0)
    invest_income=st.number_input("Investment Income",0)
    other=st.number_input("Other Income",0)

    inflow=salary+side+invest_income+other

    rent=st.number_input("Rent/Mortgage",0)
    utilities=st.number_input("Utilities",0)
    groceries=st.number_input("Groceries",0)
    transport=st.number_input("Transport",0)
    insurance=st.number_input("Insurance",0)
    investments=st.number_input("Investments",0)

    outflow=rent+utilities+groceries+transport+insurance+investments

    net=inflow-outflow

    df=pd.DataFrame({
    "Category":["Total Inflow","Total Outflow","Net Cashflow"],
    "Amount":[inflow,outflow,net]})

    st.table(df)

# =====================================================
# CAR PURCHASE
# =====================================================
if st.session_state.page=="car":

    st.button("⬅ Back",on_click=lambda:go("home"))
    st.subheader("Car Purchase Planner")

    price=st.number_input("Car Price Today",value=1000000)
    years=st.number_input("Years to Buy",value=5)

    future=price*((1+inflation)**years)

    sip=sip_required(future,expected_return,years)/12

    st.metric("Future Price",f"₹ {future:,.0f}")
    st.metric("Monthly SIP",f"₹ {sip:,.0f}")

# =====================================================
# IPHONE PURCHASE
# =====================================================
if st.session_state.page=="iphone":

    st.button("⬅ Back",on_click=lambda:go("home"))
    st.subheader("iPhone Purchase Planner")

    price=st.number_input("iPhone Price Today",value=120000)
    months=st.number_input("Months to Buy",value=12)

    rate=expected_return/12
    future=price*(1+inflation)**(months/12)
    sip=future/(((1+rate)**months-1)/rate)

    st.metric("Future Price",f"₹ {future:,.0f}")
    st.metric("Monthly Saving",f"₹ {sip:,.0f}")

# =====================================================
# PORTFOLIO ALLOCATION
# =====================================================
if st.session_state.page=="portfolio":

    st.button("⬅ Back",on_click=lambda:go("home"))
    st.subheader("Portfolio Allocation")

    total=st.number_input("Total Investment (₹)",value=1000000)

    equity=st.slider("Equity %",0,100,50)
    debt=st.slider("Debt %",0,100,30)
    gold=st.slider("Gold %",0,100,10)
    realestate=st.slider("Real Estate %",0,100,5)
    cash=st.slider("Cash %",0,100,5)

    data={
    "Asset":["Equity","Debt","Gold","Real Estate","Cash"],
    "Allocation %":[equity,debt,gold,realestate,cash],
    "Amount":[
    total*(equity/100),
    total*(debt/100),
    total*(gold/100),
    total*(realestate/100),
    total*(cash/100)
    ]
    }

    df=pd.DataFrame(data)
    st.dataframe(df,use_container_width=True)

st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration Only")
# =============================================
# NET WORTH DASHBOARD
# =============================================
if st.session_state.page=="networth":

    st.button("⬅ Back",on_click=lambda:go("home"))

    st.subheader("Net Worth Dashboard")

    st.markdown("### Assets")

    mf = st.number_input("Mutual Funds (₹)",value=0)
    stocks = st.number_input("Stocks (₹)",value=0)
    realestate = st.number_input("Real Estate (₹)",value=0)
    gold = st.number_input("Gold (₹)",value=0)
    cash = st.number_input("Cash / Bank Balance (₹)",value=0)
    other_assets = st.number_input("Other Assets (₹)",value=0)

    total_assets = mf + stocks + realestate + gold + cash + other_assets

    st.markdown("### Liabilities")

    home_loan = st.number_input("Home Loan (₹)",value=0)
    personal_loan = st.number_input("Personal Loan (₹)",value=0)
    car_loan = st.number_input("Car Loan (₹)",value=0)
    credit_card = st.number_input("Credit Card Outstanding (₹)",value=0)
    other_liabilities = st.number_input("Other Liabilities (₹)",value=0)

    total_liabilities = home_loan + personal_loan + car_loan + credit_card + other_liabilities

    networth = total_assets - total_liabilities

    st.markdown("### Net Worth Summary")

    df = pd.DataFrame({
        "Category":["Total Assets","Total Liabilities","Net Worth"],
        "Amount":[total_assets,total_liabilities,networth]
    })

    st.table(df)

    if networth > 0:
        st.success(f"Net Worth : ₹ {networth:,.0f}")
    else:
        st.error("Net Worth Negative – Review liabilities")
