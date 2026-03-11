# Freedom Ultra Pro - Single File Streamlit App
# NOTE: Full app.py created in canvas for easier copy/edit.
# If you want, I can now keep updating this exact file module-by-module.

import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO
from datetime import datetime

# Optional imports
try:
    import pdfplumber
    PDF_OK = True
except Exception:
    PDF_OK = False

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Freedom Ultra Pro", layout="wide")

# =============================
# THEME
# =============================
st.markdown("""
<style>
.stApp { background: #0B1220; }
.header-box {
    background: linear-gradient(90deg,#1d4ed8,#0ea5e9);
    padding: 20px; border-radius: 16px; text-align:center; color:white;
    font-size: 40px; font-weight: 800;
}
.subtitle { text-align:center; color:#bfdbfe; margin-bottom:18px; }
.stButton > button {
    width: 100%; height: 46px; border-radius: 10px; border:none;
    background: linear-gradient(90deg,#2563eb,#06b6d4); color:white; font-weight:700;
    margin-bottom:8px;
}
section[data-testid="stSidebar"] { background:#111827; }
label, .stMarkdown, .stText, .stCaption { color:#e5e7eb !important; }
[data-testid="metric-container"] {
    background:#111827; border:1px solid #1f2937; border-radius:12px; padding:8px;
}
thead tr th { background:#2563eb !important; color:white !important; }
</style>
""", unsafe_allow_html=True)

# =============================
# STATE
# =============================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page

# =============================
# HELPERS
# =============================
def fmt(x):
    return f"₹ {x:,.0f}"

def future_value(pv, rate, years):
    return pv * ((1 + rate) ** max(years, 0))

def monthly_sip_required(target, annual_rate, years):
    months = int(max(years, 0) * 12)
    if months <= 0:
        return 0
    r = annual_rate / 12
    if r <= 0:
        return target / months
    factor = ((1 + r) ** months - 1) / r
    return target / factor if factor > 0 else 0

def xnpv(rate, cashflows):
    if len(cashflows) < 1:
        return 0
    t0 = cashflows[0][0]
    return sum(cf / ((1 + rate) ** ((dt - t0).days / 365.0)) for dt, cf in cashflows)

def xirr(cashflows):
    if len(cashflows) < 2:
        return None
    low, high = -0.9999, 10.0
    for _ in range(200):
        mid = (low + high) / 2
        val = xnpv(mid, cashflows)
        if abs(val) < 1e-6:
            return mid
        if val > 0:
            low = mid
        else:
            high = mid
    return mid

def clean_amount(x):
    x = str(x).replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "").strip()
    x = re.sub(r"[^0-9.\-]", "", x)
    try:
        return float(x)
    except:
        return np.nan

def normalize_txn_type(x):
    x = str(x).lower().strip()
    buy = ["purchase","sip","systematic investment","switch in","stp in","allotment","buy","investment","additional purchase"]
    sell = ["redemption","switch out","sell","withdrawal","swp","stp out","redeem"]
    current = ["current value","market value","current market value","valuation"]
    for k in buy:
        if k in x: return "Purchase"
    for k in sell:
        if k in x: return "Redemption"
    for k in current:
        if k in x: return "Current Value"
    return "Unknown"

# =============================
# HEADER / SIDEBAR
# =============================
st.markdown('<div class="header-box">Freedom Ultra Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Integrated Wealth Planning & Mutual Fund Advisory Platform</div>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("Client Profile")
current_age = st.sidebar.number_input("Current Age", 18, 80, 30)
inflation = st.sidebar.number_input("General Inflation (%)", 0.0, 20.0, 6.0) / 100
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 25.0, 12.0) / 100

# =============================
# HOME
# =============================
if st.session_state.page == "home":
    st.subheader("Advisor Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.button("SIP Calculator", on_click=lambda: go("sip"))
        st.button("Children Planner", on_click=lambda: go("children"))
        st.button("Car Purchase Planner", on_click=lambda: go("car"))
        st.button("House Planning", on_click=lambda: go("house"))
    with c2:
        st.button("SWP Calculator", on_click=lambda: go("swp"))
        st.button("Retirement Planner", on_click=lambda: go("retirement"))
        st.button("Term Insurance", on_click=lambda: go("term"))
        st.button("Cashflow Planner", on_click=lambda: go("cashflow"))
    with c3:
        st.button("Portfolio Allocation", on_click=lambda: go("portfolio"))
        st.button("Net Worth Dashboard", on_click=lambda: go("networth"))
        st.button("Goal Feasibility", on_click=lambda: go("goal"))
        st.button("Portfolio Rebalancing", on_click=lambda: go("rebalance"))
    with c4:
        st.button("Retirement Monte Carlo", on_click=lambda: go("mc_retirement"))
        st.button("MF Portfolio + XIRR", on_click=lambda: go("mf_xirr"))
        st.button("CAS PDF + XIRR", on_click=lambda: go("cas_pdf"))

# =============================
# SIP
# =============================
if st.session_state.page == "sip":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SIP Calculator")
    sip = st.number_input("Starting Monthly SIP (₹)", 0, 10_000_000, 5000)
    years = st.number_input("Investment Years", 1, 50, 10)
    step_up = st.number_input("Annual Step-Up (%)", 0.0, 50.0, 10.0) / 100
    corpus = invested = 0
    rows = []
    curr = sip
    for y in range(1, years + 1):
        yearly = curr * 12
        invested += yearly
        corpus = (corpus + yearly) * (1 + expected_return)
        rows.append([y, round(curr), round(yearly), round(invested), round(corpus)])
        curr *= (1 + step_up)
    df = pd.DataFrame(rows, columns=["Year","Monthly SIP","Yearly Investment","Total Invested","Year End Corpus"])
    st.dataframe(df, use_container_width=True)
    g = corpus - invested
    a,b,c = st.columns(3)
    a.metric("Total Invested", fmt(invested))
    b.metric("Total Gain", fmt(g))
    c.metric("Final Corpus", fmt(corpus))

# =============================
# SWP
# =============================
if st.session_state.page == "swp":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("SWP Calculator")
    initial_corpus = st.number_input("Initial Corpus (₹)", 0, 1_000_000_000, 10_000_000)
    entry_age = st.number_input("Entry Age", 18, 90, max(30, current_age))
    start_age = st.number_input("Withdrawal Start Age", entry_age, 95, max(60, entry_age))
    end_age = st.number_input("Withdrawal End Age", start_age + 1, 100, min(90, start_age + 20))
    annual_withdrawal = st.number_input("Withdrawal Per Year (₹)", 0, 100_000_000, 1_200_000)
    withdrawal_infl = st.number_input("Annual Withdrawal Increase (%)", 0.0, 15.0, 6.0) / 100
    swp_return = st.number_input("Expected Return During SWP (%)", 0.0, 20.0, 8.0) / 100
    years_before = max(0, start_age - entry_age)
    corpus_start = initial_corpus * ((1 + swp_return) ** years_before)
    bal = corpus_start
    wd = annual_withdrawal
    rows = []
    for age in range(start_age, end_age + 1):
        open_bal = bal
        growth = open_bal * swp_return
        close_bal = max(0, open_bal + growth - wd)
        rows.append([age, round(open_bal), round(growth), round(wd), round(close_bal)])
        bal = close_bal
        wd *= (1 + withdrawal_infl)
        if bal <= 0:
            break
    st.dataframe(pd.DataFrame(rows, columns=["Age","Opening Corpus","Growth","Withdrawal","Closing Corpus"]), use_container_width=True)
    a,b,c = st.columns(3)
    a.metric("Corpus at SWP Start", fmt(corpus_start))
    b.metric("Years Before SWP", years_before)
    c.metric("End Corpus", fmt(bal))

# =============================
# CHILDREN
# =============================
if st.session_state.page == "children":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Children Planner Pro")
    num_children = st.number_input("Number of Children", 1, 4, 1)
    edu_infl = st.number_input("Education Inflation (%)", 0.0, 20.0, 10.0) / 100
    mar_infl = st.number_input("Marriage Inflation (%)", 0.0, 20.0, 8.0) / 100
    results = []
    for i in range(num_children):
        st.markdown(f"### Child {i+1}")
        child_age = st.number_input(f"Child {i+1} Current Age", 0, 18, 2, key=f"ca{i}")
        goals = {
            "10th": (15, edu_infl),
            "12th": (17, edu_infl),
            "Graduation": (21, edu_infl),
            "Masters": (24, edu_infl),
            "Marriage": (28, mar_infl),
        }
        for goal, (goal_age, gi) in goals.items():
            cost = st.number_input(f"{goal} Cost Today (₹) - Child {i+1}", 0, 100_000_000, 2_000_000, key=f"{goal}{i}")
            yrs = goal_age - child_age
            if yrs > 0:
                fv = future_value(cost, gi, yrs)
                sip_req = monthly_sip_required(fv, expected_return, yrs)
                lump = fv / ((1 + expected_return) ** yrs)
                results.append([f"Child {i+1}", goal, goal_age, round(fv), round(sip_req), round(lump)])
    if results:
        df = pd.DataFrame(results, columns=["Child","Goal","Goal Age","Future Cost","Monthly SIP Required","Lumpsum Required Today"])
        st.dataframe(df, use_container_width=True)

# =============================
# RETIREMENT
# =============================
if st.session_state.page == "retirement":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Planner")
    retirement_age = st.number_input("Retirement Age", 45, 75, 60)
    life_expectancy = st.number_input("Plan Till Age", 70, 100, 90)
    years_to_ret = max(0, retirement_age - current_age)
    retirement_years = max(1, life_expectancy - retirement_age)
    rent = st.number_input("Rent", 0, 1_000_000, 0)
    grocery = st.number_input("Groceries + Medicine", 0, 1_000_000, 30000)
    utilities = st.number_input("Utilities", 0, 1_000_000, 5000)
    discretionary = st.number_input("Discretionary", 0, 1_000_000, 10000)
    vehicle = st.number_input("Vehicle", 0, 1_000_000, 10000)
    annual_expense = (rent + grocery + utilities + discretionary + vehicle) * 12
    equity = st.number_input("Current Equity Corpus (₹)", 0, 1_000_000_000, 1_000_000)
    debt = st.number_input("Current Debt Corpus (₹)", 0, 1_000_000_000, 1_000_000)
    corpus = equity + debt
    fv_existing = future_value(corpus, expected_return, years_to_ret)
    exp_ret = future_value(annual_expense, inflation, years_to_ret)
    post_ret_return = st.number_input("Post Retirement Return (%)", 0.0, 15.0, 8.0) / 100
    if post_ret_return > inflation:
        req = exp_ret * ((1 - ((1 + inflation)/(1 + post_ret_return)) ** retirement_years) / (post_ret_return - inflation))
    else:
        req = exp_ret * retirement_years
    gap = max(0, req - fv_existing)
    sip_req = monthly_sip_required(gap, expected_return, years_to_ret)
    st.table(pd.DataFrame({"Metric":["Annual Expense Today","Expense at Retirement","FV of Existing Corpus","Required Corpus","Retirement Gap","Required Monthly SIP"],
                           "Value":[fmt(annual_expense),fmt(exp_ret),fmt(fv_existing),fmt(req),fmt(gap),fmt(sip_req)]}))

# =============================
# TERM
# =============================
if st.session_state.page == "term":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Term Insurance Calculator")
    annual_income = st.number_input("Annual Income (₹)", 0, 100_000_000, 2_400_000)
    retirement_age = st.number_input("Retirement Age", 45, 75, 60, key="term_ret")
    liabilities = st.number_input("Outstanding Liabilities (₹)", 0, 1_000_000_000, 0)
    existing_cover = st.number_input("Existing Insurance Cover (₹)", 0, 1_000_000_000, 0)
    years_left = max(0, retirement_age - current_age)
    income_repl = annual_income * years_left
    cover = max(0, income_repl + liabilities - existing_cover)
    st.success(f"Recommended Additional Cover: {fmt(cover)}")

# =============================
# CASHFLOW
# =============================
if st.session_state.page == "cashflow":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Cashflow Planner")
    plan_till_age = st.number_input("Plan Till Age", 50, 100, 85)
    salary = st.number_input("Salary / Wages", 0, 100_000_000, 0)
    side = st.number_input("Side Hustle / Freelance", 0, 100_000_000, 0)
    inv_inc = st.number_input("Investment Income", 0, 100_000_000, 0)
    other = st.number_input("Other Income", 0, 100_000_000, 0)
    inflow = salary + side + inv_inc + other
    rent = st.number_input("Rent / Mortgage", 0, 100_000_000, 0, key="cf_rent")
    utilities = st.number_input("Utilities", 0, 100_000_000, 0, key="cf_util")
    debt = st.number_input("Debt Payments", 0, 100_000_000, 0, key="cf_debt")
    insurance = st.number_input("Insurance", 0, 100_000_000, 0, key="cf_ins")
    childcare = st.number_input("Childcare / Alimony", 0, 100_000_000, 0)
    groceries = st.number_input("Groceries", 0, 100_000_000, 0)
    dining = st.number_input("Dining / Entertainment", 0, 100_000_000, 0)
    transport = st.number_input("Transportation / Fuel", 0, 100_000_000, 0)
    shopping = st.number_input("Shopping / Subscriptions", 0, 100_000_000, 0)
    emergency = st.number_input("Emergency Fund Savings", 0, 100_000_000, 0)
    retire_contrib = st.number_input("Retirement Contributions", 0, 100_000_000, 0)
    investments = st.number_input("Investments", 0, 100_000_000, 0)
    outflow = sum([rent,utilities,debt,insurance,childcare,groceries,dining,transport,shopping,emergency,retire_contrib,investments])
    net = inflow - outflow
    st.table(pd.DataFrame({"Category":["Total Inflow (A)","Total Outflow (B)","Net Cash Flow"],"Amount":[fmt(inflow),fmt(outflow),fmt(net)]}))

# =============================
# CAR / HOUSE
# =============================
if st.session_state.page in ["car", "house"]:
    st.button("⬅ Back", on_click=lambda: go("home"))
    title = "Car Purchase Planner" if st.session_state.page == "car" else "House Planning"
    st.subheader(title)
    default_val = 1_000_000 if st.session_state.page == "car" else 10_000_000
    price = st.number_input("Price Today (₹)", 0, 1_000_000_000, default_val)
    years = st.number_input("Years to Goal", 1, 30, 5)
    goal_infl = st.number_input("Goal Inflation (%)", 0.0, 15.0, 6.0) / 100
    fv = future_value(price, goal_infl, years)
    sip_req = monthly_sip_required(fv, expected_return, years)
    lump = fv / ((1 + expected_return) ** years)
    a,b,c = st.columns(3)
    a.metric("Future Price", fmt(fv))
    b.metric("Required Monthly SIP", fmt(sip_req))
    c.metric("Lumpsum Required Today", fmt(lump))

# =============================
# PORTFOLIO / NETWORTH / GOAL / REBALANCE / MC
# =============================
if st.session_state.page == "portfolio":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Portfolio Allocation")
    total = st.number_input("Total Investment Amount (₹)", 0, 1_000_000_000, 1_000_000)
    eq = st.slider("Equity %", 0, 100, 50)
    debt = st.slider("Debt %", 0, 100, 30)
    gold = st.slider("Gold %", 0, 100, 10)
    re = st.slider("Real Estate %", 0, 100, 5)
    cash = st.slider("Cash %", 0, 100, 5)
    st.dataframe(pd.DataFrame({"Asset":["Equity","Debt","Gold","Real Estate","Cash"],"% ":[eq,debt,gold,re,cash],"Amount":[total*eq/100,total*debt/100,total*gold/100,total*re/100,total*cash/100]}), use_container_width=True)

if st.session_state.page == "networth":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Net Worth Dashboard")
    assets = sum([
        st.number_input("Mutual Funds (₹)",0,1_000_000_000,0),
        st.number_input("Stocks (₹)",0,1_000_000_000,0),
        st.number_input("Real Estate (₹)",0,1_000_000_000,0),
        st.number_input("Gold (₹)",0,1_000_000_000,0),
        st.number_input("Cash / Bank (₹)",0,1_000_000_000,0),
    ])
    liab = sum([
        st.number_input("Home Loan (₹)",0,1_000_000_000,0),
        st.number_input("Personal Loan (₹)",0,1_000_000_000,0),
        st.number_input("Car Loan (₹)",0,1_000_000_000,0),
        st.number_input("Credit Card Outstanding (₹)",0,1_000_000_000,0),
    ])
    st.success(f"Net Worth: {fmt(assets - liab)}")

if st.session_state.page == "goal":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Goal Feasibility Dashboard")
    n = st.number_input("Number of Goals", 1, 10, 3)
    rows = []
    for i in range(n):
        name = st.text_input(f"Goal Name {i+1}", f"Goal {i+1}", key=f"g{i}")
        target = st.number_input(f"Target Amount (₹) - {name}", 0, 1_000_000_000, 1_000_000, key=f"gt{i}")
        years = st.number_input(f"Years to Goal - {name}", 1, 50, 10, key=f"gy{i}")
        exist = st.number_input(f"Existing Investment (₹) - {name}", 0, 1_000_000_000, 0, key=f"ge{i}")
        gi = st.number_input(f"Goal Inflation (%) - {name}", 0.0, 20.0, 6.0, key=f"gi{i}") / 100
        ft = future_value(target, gi, years)
        fe = future_value(exist, expected_return, years)
        gap = max(0, ft - fe)
        sip_req = monthly_sip_required(gap, expected_return, years)
        rows.append([name, round(ft), round(fe), round(gap), round(sip_req)])
    st.dataframe(pd.DataFrame(rows, columns=["Goal","Future Target","Future Value Existing","Funding Gap","Required Monthly SIP"]), use_container_width=True)

if st.session_state.page == "rebalance":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Portfolio Rebalancing")
    total = st.number_input("Total Portfolio Value (₹)", 0, 1_000_000_000, 1_000_000)
    ce, cd, cg, cc = st.slider("Current Equity %",0,100,60), st.slider("Current Debt %",0,100,25), st.slider("Current Gold %",0,100,10), st.slider("Current Cash %",0,100,5)
    te, td, tg, tc = st.slider("Target Equity %",0,100,50), st.slider("Target Debt %",0,100,30), st.slider("Target Gold %",0,100,10), st.slider("Target Cash %",0,100,10)
    rows=[]
    for a,cp,tp in zip(["Equity","Debt","Gold","Cash"],[ce,cd,cg,cc],[te,td,tg,tc]):
        ca = total*cp/100; ta = total*tp/100; d = ta-ca
        rows.append([a,cp,tp,round(ca),round(ta),round(d),"Buy" if d>0 else "Sell" if d<0 else "No Change"])
    st.dataframe(pd.DataFrame(rows, columns=["Asset","Current %","Target %","Current Amount","Target Amount","Diff","Action"]), use_container_width=True)

if st.session_state.page == "mc_retirement":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Retirement Monte Carlo")
    initial = st.number_input("Initial Retirement Corpus (₹)", 0, 1_000_000_000, 50_000_000)
    retirement_age = st.number_input("Retirement Start Age", 45, 80, 60, key="mc_ret")
    life = st.number_input("Plan Till Age", 70, 100, 90, key="mc_life")
    exp = st.number_input("Annual Expense Today (₹)", 0, 100_000_000, 1_200_000)
    post_inf = st.number_input("Post Retirement Inflation (%)", 0.0, 15.0, 6.0) / 100
    mean = st.number_input("Expected Return After Retirement (%)", 0.0, 20.0, 8.0) / 100
    std = st.number_input("Volatility (%)", 0.0, 50.0, 12.0) / 100
    sims = st.number_input("Simulations", 100, 5000, 1000, step=100)
    years = max(1, life - retirement_age)
    success = 0
    for _ in range(sims):
        c = initial; e = exp
        for _y in range(years):
            r = np.random.normal(mean, std)
            c = c * (1 + r) - e
            e *= (1 + post_inf)
            if c <= 0:
                c = 0; break
        if c > 0: success += 1
    success_rate = success / sims * 100
    st.success(f"Retirement Success Probability: {success_rate:.1f}%")

# =============================
# MF CSV/EXCEL + XIRR
# =============================
if st.session_state.page == "mf_xirr":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Mutual Fund Portfolio Upload + XIRR")
    up = st.file_uploader("Upload CSV or Excel", type=["csv","xlsx"], key="mfup")
    if up is not None:
        try:
            df = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
            st.dataframe(df, use_container_width=True)
            cols = {c.lower().strip(): c for c in df.columns}
            # expected standard columns for simplicity
            req = ["date","fund name","transaction type","amount"]
            if not all(r in cols for r in req):
                st.error("Use columns: Date, Fund Name, Transaction Type, Amount")
            else:
                sdf = pd.DataFrame()
                sdf["Date"] = pd.to_datetime(df[cols["date"]], errors="coerce")
                sdf["Fund Name"] = df[cols["fund name"]].astype(str)
                sdf["Transaction Type"] = df[cols["transaction type"]].astype(str).apply(normalize_txn_type)
                sdf["Amount"] = pd.to_numeric(df[cols["amount"]], errors="coerce")
                sdf = sdf.dropna()
                rows = []
                for fund in sdf["Fund Name"].unique():
                    fdf = sdf[sdf["Fund Name"] == fund]
                    pur = fdf[fdf["Transaction Type"] == "Purchase"]["Amount"].sum()
                    red = fdf[fdf["Transaction Type"] == "Redemption"]["Amount"].sum()
                    cv = st.number_input(f"Current Value - {fund}", 0.0, 1e12, 0.0, key=f"cv_{fund}")
                    cfs = []
                    for _, r in fdf.iterrows():
                        cfs.append((r["Date"], -r["Amount"] if r["Transaction Type"] == "Purchase" else r["Amount"]))
                    if cv > 0:
                        cfs.append((pd.Timestamp.today().normalize(), cv))
                    irr = xirr(cfs)
                    rows.append([fund, round(pur), round(red), round(cv), round(cv + red - pur), round(irr*100,2) if irr is not None else "N/A"])
                st.dataframe(pd.DataFrame(rows, columns=["Fund Name","Fund-wise Purchase","Fund-wise Redemption","Current Value","Profit/Loss","XIRR %"]), use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

# =============================
# CAS PDF + XIRR
# =============================
if st.session_state.page == "cas_pdf":
    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("CAMS / KFintech PDF CAS Parser + XIRR")
    if not PDF_OK:
        st.error("pdfplumber not installed. Add pdfplumber to requirements.txt")
    else:
        pdf = st.file_uploader("Upload CAS PDF", type=["pdf"], key="caspdf")
        if pdf is not None:
            try:
                text = []
                with pdfplumber.open(BytesIO(pdf.read())) as p:
                    for pg in p.pages:
                        t = pg.extract_text()
                        if t:
                            text.append(t)
                text = "\n".join(text)
                st.text_area("Extracted Text Preview", text[:3000], height=200)
                lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
                date_pat = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")
                amt_pat = re.compile(r"[-]?\d[\d,]*\.?\d*")
                current_scheme = None
                txns = []
                for line in lines:
                    low = line.lower()
                    if any(k in low for k in ["fund","scheme","plan","growth","direct","regular"]) and not date_pat.search(line) and len(line) > 10:
                        current_scheme = line
                    if date_pat.search(line):
                        ttype = normalize_txn_type(line)
                        if ttype in ["Purchase","Redemption"] and current_scheme:
                            d = date_pat.search(line).group(0)
                            nums = [clean_amount(n) for n in amt_pat.findall(line)]
                            nums = [n for n in nums if pd.notna(n)]
                            amt = max(nums) if nums else np.nan
                            if pd.notna(amt):
                                txns.append([d, current_scheme, ttype, amt, line])
                if not txns:
                    st.error("No transactions detected. Use CSV/Excel parser if needed.")
                else:
                    df = pd.DataFrame(txns, columns=["Date","Fund Name","Transaction Type","Amount","Raw Line"])
                    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
                    df = df.dropna(subset=["Date","Amount"])
                    st.dataframe(df, use_container_width=True)
                    funds = sorted(df["Fund Name"].unique())
                    rows = []
                    for fund in funds:
                        fdf = df[df["Fund Name"] == fund]
                        pur = fdf[fdf["Transaction Type"] == "Purchase"]["Amount"].sum()
                        red = fdf[fdf["Transaction Type"] == "Redemption"]["Amount"].sum()
                        cv = st.number_input(f"Current Value - {fund}", 0.0, 1e12, 0.0, key=f"pcv_{fund}")
                        cfs = []
                        for _, r in fdf.iterrows():
                            cfs.append((r["Date"], -r["Amount"] if r["Transaction Type"] == "Purchase" else r["Amount"]))
                        if cv > 0:
                            cfs.append((pd.Timestamp.today().normalize(), cv))
                        irr = xirr(cfs)
                        rows.append([fund, round(pur), round(red), round(cv), round(cv + red - pur), round(irr*100,2) if irr is not None else "N/A"])
                    st.dataframe(pd.DataFrame(rows, columns=["Fund Name","Fund-wise Purchase","Fund-wise Redemption","Current Value","Profit/Loss","XIRR %"]), use_container_width=True)
            except Exception as e:
                st.error(f"PDF parse error: {e}")

st.markdown("---")
st.caption("Freedom Ultra Pro | Single-file advisor platform")
