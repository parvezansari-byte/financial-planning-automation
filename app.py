# Freedom V3 PRO Wealthy-style final app.py
# Single-file Streamlit app (client-facing, no charts, no plotly)

import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
from io import BytesIO

try:
    import pdfplumber
    PDF_OK = True
except Exception:
    PDF_OK = False

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Freedom V3 PRO", layout="wide")

# =====================================================
# WEALTHY-STYLE THEME
# =====================================================
st.markdown("""
<style>
.stApp {
    background: #F5F1E8;
    color: #1F2937;
}
section[data-testid="stSidebar"] {
    background: #F3EEE4;
}

.main-title {
    background: linear-gradient(90deg, #6D28D9, #7C3AED);
    padding: 22px;
    border-radius: 0px;
    text-align: center;
    color: white;
    font-size: 40px;
    font-weight: 800;
    border: 2px solid #2D1B69;
}
.sub-title {
    background: #0B2A6B;
    color: white;
    text-align: center;
    padding: 8px;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 12px;
}
.prepared-line {
    font-style: italic;
    color: #374151;
    margin: 8px 0 12px 0;
}

.wealthy-box {
    border: 2px solid #1F2937;
    background: white;
    margin-bottom: 14px;
}
.wealthy-header {
    background: #C4B5FD;
    color: #111827;
    text-align: center;
    font-weight: 800;
    font-size: 22px;
    padding: 8px;
    border-bottom: 2px solid #1F2937;
}
.wealthy-subheader {
    background: #E9D5FF;
    color: #111827;
    text-align: center;
    font-weight: 700;
    padding: 6px;
    border-bottom: 1px solid #1F2937;
}

.stButton > button {
    width: 100%;
    height: 52px;
    border-radius: 6px;
    border: 1px solid #1F2937;
    background: #C4B5FD;
    color: #111827;
    font-weight: 700;
    box-shadow: none;
}
.stButton > button:hover {
    background: #A78BFA;
    color: #111827;
}

.stDownloadButton > button {
    width: 100%;
    height: 46px;
    border-radius: 6px;
    border: 1px solid #1F2937;
    background: #86EFAC;
    color: #111827;
    font-weight: 800;
}

label, .stMarkdown, .stText, .stCaption, p, div {
    color: #111827 !important;
}

[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 2px solid #1F2937;
    border-radius: 0px;
    padding: 10px;
}

thead tr th {
    background-color: #C4B5FD !important;
    color: #111827 !important;
    border: 1px solid #1F2937 !important;
}

tbody tr td {
    color: #111827 !important;
    border: 1px solid #D1D5DB !important;
    background: #FFFFFF !important;
}

hr {
    border: none;
    border-top: 2px solid #D1D5DB;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page_name):
    st.session_state.page = page_name

def back_button():
    st.button("< Back to Index", on_click=lambda: go("home"))

# =====================================================
# HELPERS
# =====================================================
def fmt(x):
    try:
        return f"₹ {x:,.0f}"
    except Exception:
        return "₹ 0"

def future_value(pv, rate, years):
    return pv * ((1 + rate) ** max(years, 0))

def lumpsum_required(target, annual_return, years):
    if years <= 0:
        return target
    return target / ((1 + annual_return) ** years)

def monthly_sip_required(target, annual_rate, years):
    months = int(max(years, 0) * 12)
    if months <= 0:
        return 0
    r = annual_rate / 12
    if r <= 0:
        return target / months
    factor = ((1 + r) ** months - 1) / r
    return target / factor if factor > 0 else 0

def monthly_sip_required_stepup(target, annual_return, years, step_up):
    months = int(max(years, 0) * 12)
    if months <= 0:
        return 0
    r = annual_return / 12
    low, high = 0, max(target, 1)
    for _ in range(80):
        mid = (low + high) / 2
        corpus = 0
        sip = mid
        for m in range(1, months + 1):
            corpus = corpus * (1 + r) + sip
            if m % 12 == 0:
                sip *= (1 + step_up)
        if corpus >= target:
            high = mid
        else:
            low = mid
    return high

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
    except Exception:
        return np.nan

def normalize_txn_type(x):
    x = str(x).lower().strip()
    buy = ["purchase", "sip", "systematic investment", "switch in", "stp in", "allotment", "buy", "investment", "additional purchase"]
    sell = ["redemption", "switch out", "sell", "withdrawal", "swp", "stp out", "redeem"]
    current = ["current value", "market value", "current market value", "valuation"]
    for k in buy:
        if k in x:
            return "Purchase"
    for k in sell:
        if k in x:
            return "Redemption"
    for k in current:
        if k in x:
            return "Current Value"
    return "Unknown"

def advisor_note(title, lines):
    st.markdown('<div class="wealthy-box">', unsafe_allow_html=True)
    st.markdown('<div class="wealthy-subheader">Automatic Advisor Notes</div>', unsafe_allow_html=True)
    st.markdown(f"**{title}**")
    for line in lines:
        st.write(f"• {line}")
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown('<div class="main-title">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Investment & Insurance Planner</div>', unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.header("Client Profile")
client_name = st.sidebar.text_input("Client Name", "Aditya")
advisor_name = st.sidebar.text_input("Advisor Name", "Saurabh")
current_age = st.sidebar.number_input("Current Age", 18, 80, 30)
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 20.0, 6.0) / 100
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 25.0, 12.0) / 100

# =====================================================
# HOME PAGE
# =====================================================
if st.session_state.page == "home":
    st.markdown('<div class="wealthy-box"><div class="wealthy-header">Freedom Planner Index</div></div>', unsafe_allow_html=True)

    cinfo1, cinfo2 = st.columns(2)
    with cinfo1:
        st.info(f"Client Name: {client_name}")
    with cinfo2:
        st.info(f"Distributor Name: {advisor_name}")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("SIP & Lumpsum Calculator", on_click=lambda: go("sip"))
        st.button("Future Planning for Children", on_click=lambda: go("children"))
        st.button("Cashflow Planner", on_click=lambda: go("cashflow"))
        st.button("Car Purchase Planner", on_click=lambda: go("car"))
        st.button("Portfolio Allocation", on_click=lambda: go("portfolio"))
    with c2:
        st.button("SWP Calculator", on_click=lambda: go("swp"))
        st.button("Retirement Planner", on_click=lambda: go("retirement"))
        st.button("House Planning", on_click=lambda: go("house"))
        st.button("Net Worth Dashboard", on_click=lambda: go("networth"))
        st.button("Goal Feasibility", on_click=lambda: go("goal"))
    with c3:
        st.button("SIP + SWP Planner", on_click=lambda: go("sip_swp"))
        st.button("Term Insurance Calculator", on_click=lambda: go("term"))
        st.button("iPhone Purchase Planner", on_click=lambda: go("iphone"))
        st.button("Portfolio Rebalancing", on_click=lambda: go("rebalance"))
        st.button("Retirement Monte Carlo", on_click=lambda: go("mc_retirement"))

    st.markdown("---")
    st.caption("Disclaimer: Result or output of these calculators are for representational purpose only. Check with an expert before taking any financial decision.")

# =====================================================
# SIP & LUMPSUM CALCULATOR
# =====================================================
if st.session_state.page == "sip":
    back_button()
    st.markdown(f'<div class="prepared-line">Prepared for {client_name} by {advisor_name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="wealthy-box"><div class="wealthy-header">SIP & Lumpsum Calculator</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="wealthy-box"><div class="wealthy-subheader">Check the corpus you can build</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### SIP")
        monthly_sip = st.number_input("Monthly SIP (₹)", 0, 100000000, 5000)
        years = st.number_input("Investment Period (Years)", 1, 60, 20)
        sip_return = st.number_input("Expected Return for SIP (%)", 0.0, 30.0, float(expected_return * 100)) / 100
        step_up = st.number_input("Annual Step-up (%)", 0.0, 50.0, 10.0) / 100

        corpus = 0
        total_invested = 0
        current_sip = monthly_sip
        rows = []
        for y in range(1, years + 1):
            yearly_invested = 0
            for _ in range(12):
                corpus = corpus * (1 + sip_return / 12) + current_sip
                total_invested += current_sip
                yearly_invested += current_sip
            gain = corpus - total_invested
            rows.append([y, round(current_sip, 0), round(yearly_invested, 0), round(total_invested, 0), round(gain, 0), round(corpus, 0)])
            current_sip *= (1 + step_up)

        sip_df = pd.DataFrame(rows, columns=["Year", "Monthly SIP (₹)", "Yearly Invested (₹)", "Total Invested (₹)", "Total Gain (₹)", "Year End Corpus (₹)"])

        st.metric("Invested", fmt(total_invested))
        st.metric("Final Value", fmt(corpus))
        st.metric("Absolute Gain", f"{((corpus-total_invested)/total_invested*100 if total_invested>0 else 0):.2f}%")

    with c2:
        st.markdown("### Lumpsum")
        lumpsum_amt = st.number_input("Investment Amount (₹)", 0, 1000000000, 1000000)
        lumpsum_return = st.number_input("Expected Return for Lumpsum (%)", 0.0, 30.0, 12.0) / 100
        lumpsum_years = st.number_input("Investment Period in Years", 1, 60, 7)
        final_lumpsum = future_value(lumpsum_amt, lumpsum_return, lumpsum_years)
        st.metric("Invested", fmt(lumpsum_amt))
        st.metric("Final Value", fmt(final_lumpsum))
        st.metric("Absolute Gain", f"{((final_lumpsum-lumpsum_amt)/lumpsum_amt*100 if lumpsum_amt>0 else 0):.2f}%")

    st.markdown('<div class="wealthy-box"><div class="wealthy-subheader">Yearly Wealth Table</div></div>', unsafe_allow_html=True)
    st.dataframe(sip_df, use_container_width=True)
    advisor_note("SIP Recommendation", ["Step-up SIP materially improves long-term corpus.", "If cashflow allows, increasing SIP by 10% yearly is ideal.", "Use this module for disciplined long-term goal building."])

# =====================================================
# SWP CALCULATOR PRO
# =====================================================
if st.session_state.page == "swp":
    back_button()
    st.markdown(f'<div class="prepared-line">Prepared for {client_name} by {advisor_name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="wealthy-box"><div class="wealthy-header">SWP Calculator</div></div>', unsafe_allow_html=True)

    initial_corpus = st.number_input("Current Corpus (₹)", 0, 1000000000, 10000000)
    entry_age = st.number_input("Current Age", 18, 100, current_age)
    pre_return = st.number_input("Expected Return before Withdrawal Phase (%)", 0.0, 25.0, 12.0) / 100
    withdrawal_start_age = st.number_input("Withdrawal Starts at Age", entry_age, 110, 60)
    withdrawal_end_age = st.number_input("Withdrawal Ends at Age", withdrawal_start_age, 110, 80)
    yearly_withdrawal = st.number_input("Withdrawal Per Year (₹)", 0, 100000000, 1200000)
    yearly_increase = st.number_input("Yearly Increase in Withdrawal (%)", 0.0, 25.0, 5.0) / 100
    withdrawal_return = st.number_input("Expected Return in Withdrawal Phase (%)", 0.0, 25.0, 10.0) / 100
    inflation_adjusted = st.selectbox("Inflation Adjusted Withdrawal?", ["No", "Yes"])
    monte_runs = st.number_input("Monte Carlo Runs", 100, 5000, 500, step=100)

    balance = initial_corpus
    rows = []

    for age in range(entry_age, withdrawal_start_age):
        opening = balance
        balance = balance * (1 + pre_return)
        rows.append([age, round(opening, 0), 0, round(balance, 0)])

    curr_wd = yearly_withdrawal
    for age in range(withdrawal_start_age, withdrawal_end_age + 1):
        opening = balance
        if inflation_adjusted == "Yes":
            eff_wd = curr_wd * ((1 + inflation) ** (age - withdrawal_start_age))
        else:
            eff_wd = curr_wd
        balance = balance * (1 + withdrawal_return) - eff_wd
        rows.append([age, round(opening, 0), round(eff_wd, 0), round(balance, 0)])
        curr_wd *= (1 + yearly_increase)
        if balance <= 0:
            break

    swp_df = pd.DataFrame(rows, columns=["Age", "Opening Corpus (₹)", "Withdrawal Per Year (₹)", "Year End Corpus (₹)"])
    swr = (yearly_withdrawal / initial_corpus * 100) if initial_corpus > 0 else 0

    # Monte Carlo
    np.random.seed(42)
    survived = 0
    for _ in range(monte_runs):
        mc_bal = initial_corpus
        mc_wd = yearly_withdrawal
        for age in range(entry_age, withdrawal_start_age):
            mc_bal = mc_bal * (1 + np.random.normal(pre_return, 0.08))
        ok = True
        for age in range(withdrawal_start_age, withdrawal_end_age + 1):
            eff = mc_wd * ((1 + inflation) ** (age - withdrawal_start_age)) if inflation_adjusted == "Yes" else mc_wd
            mc_bal = mc_bal * (1 + np.random.normal(withdrawal_return, 0.08)) - eff
            mc_wd *= (1 + yearly_increase)
            if mc_bal <= 0:
                ok = False
                break
        if ok:
            survived += 1
    survival = survived / monte_runs * 100 if monte_runs > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Final Corpus", fmt(max(balance, 0)))
    with k2:
        st.metric("Safe Withdrawal Rate", f"{swr:.2f}%")
    with k3:
        st.metric("Survival Probability", f"{survival:.1f}%")
    with k4:
        st.metric("Withdrawal Till Age", str(swp_df['Age'].iloc[-1] if len(swp_df) else entry_age))

    st.dataframe(swp_df, use_container_width=True)
    advisor_note("SWP Recommendation", ["If survival probability is below 85%, reduce withdrawal or delay start age.", "Inflation-adjusted withdrawal gives a more realistic retirement view.", "Keep SWR near 3.5%–5.0% for stability depending on asset mix."])

# =====================================================
# SIP + SWP PLANNER
# =====================================================
if st.session_state.page == "sip_swp":
    back_button()
    st.markdown(f'<div class="prepared-line">Prepared for {client_name} by {advisor_name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="wealthy-box"><div class="wealthy-header">SIP + SWP Planner</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        sip_age = st.number_input("Current Age", 18, 100, 30)
        sip_till_age = st.number_input("SIP to Continue Till Age", sip_age + 1, 100, 40)
        sip_amt = st.number_input("Monthly SIP Amount (₹)", 0, 100000000, 50000)
        sip_ret = st.number_input("Expected Return During SIP (%)", 0.0, 25.0, 13.0) / 100
        sip_step = st.number_input("Annual Step-up (%)", 0.0, 50.0, 10.0) / 100
    with c2:
        swp_start_age = st.number_input("SWP Start Age", sip_till_age, 110, 40)
        swp_amt = st.number_input("Monthly Withdrawal Amount (₹)", 0, 100000000, 150000)
        swp_step = st.number_input("Yearly Increase in Withdrawal (%)", 0.0, 25.0, 8.0) / 100
        swp_ret = st.number_input("Expected Return in Withdrawal Phase (%)", 0.0, 25.0, 9.0) / 100

    corpus = 0
    monthly = sip_amt
    rows = []
    for age in range(sip_age, sip_till_age):
        opening = corpus
        yearly_invested = 0
        for _ in range(12):
            corpus = corpus * (1 + sip_ret / 12) + monthly
            yearly_invested += monthly
        rows.append([age, round(opening,0), round(monthly,0), round(yearly_invested,0), 0, 0, round(corpus,0)])
        monthly *= (1 + sip_step)

    swp_monthly = swp_amt
    for age in range(swp_start_age, 111):
        opening = corpus
        yearly_wd = swp_monthly * 12
        for _ in range(12):
            corpus = corpus * (1 + swp_ret / 12) - swp_monthly
        rows.append([age, round(opening,0), 0, 0, round(swp_monthly,0), round(yearly_wd,0), round(corpus,0)])
        swp_monthly *= (1 + swp_step)
        if corpus <= 0:
            break

    df = pd.DataFrame(rows, columns=["Age", "Year Beginning Corpus (₹)", "SIP Monthly (₹)", "SIP Yearly (₹)", "SWP Monthly (₹)", "SWP Yearly (₹)", "Year End Corpus (₹)"])
    st.metric("You can withdraw till age", str(df['Age'].iloc[-1] if len(df) else swp_start_age))
    st.metric("Corpus left at final age", fmt(max(corpus,0)))
    st.dataframe(df, use_container_width=True)

# =====================================================
# CHILDREN PLANNER PRO
# =====================================================
if st.session_state.page == "children":
    back_button()
    st.markdown(f'<div class="prepared-line">Prepared for {client_name} by {advisor_name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="wealthy-box"><div class="wealthy-header">Future Planning for Children</div></div>', unsafe_allow_html=True)

    num_children = st.number_input("How many children you have", 1, 4, 1)
    all_rows = []
    total_sip = 0
    total_lump = 0

    goal_defaults = [
        ("10th Board", 15, 300000),
        ("12th Board", 17, 500000),
        ("Graduation", 21, 2000000),
        ("Masters", 24, 2500000),
        ("Marriage", 28, 3000000),
    ]

    for i in range(1, num_children + 1):
        st.markdown(f"### Child {i}")
        child_name = st.text_input(f"Child {i} Name", f"Child {i}", key=f"child_name_{i}")
        child_age = st.number_input(f"Child {i} Age", 0, 25, 2, key=f"child_age_{i}")

        for goal_name, default_age, default_cost in goal_defaults:
            c1, c2 = st.columns(2)
            with c1:
                goal_age = st.number_input(f"{goal_name} Age - {child_name}", child_age, 40, default_age, key=f"{goal_name}_age_{i}")
            with c2:
                goal_cost = st.number_input(f"{goal_name} Cost Today (₹) - {child_name}", 0, 100000000, default_cost, key=f"{goal_name}_cost_{i}")

            years_left = max(goal_age - child_age, 0)
            future_cost = future_value(goal_cost, inflation, years_left)
            sip_req = monthly_sip_required(future_cost, expected_return, years_left)
            lump_req = lumpsum_required(future_cost, expected_return, years_left)
            prob = 97 if years_left >= 10 else (90 if years_left >= 5 else 75)

            all_rows.append([child_name, goal_name, goal_age, round(future_cost,0), round(sip_req,0), round(lump_req,0), prob])
            total_sip += sip_req
            total_lump += lump_req

    child_df = pd.DataFrame(all_rows, columns=["Child", "Goal", "Goal Age", "Future Cost (₹)", "Monthly SIP Required (₹)", "Lumpsum Required Today (₹)", "Success Probability %"])
    st.metric("Total SIP Required", fmt(total_sip))
    st.metric("Total Lumpsum Required Today", fmt(total_lump))
    st.dataframe(child_df, use_container_width=True)
    advisor_note("Children Planning Recommendation", ["Create separate folios or buckets for each child goal.", "Education and marriage goals should not be mixed with retirement assets.", "Review this plan every 12 months and increase SIP as income rises."])

# =====================================================
# RETIREMENT PLANNER
# =====================================================
if st.session_state.page == "retirement":
    back_button()
    st.markdown(f'<div class="prepared-line">Prepared for {client_name} by {advisor_name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="wealthy-box"><div class="wealthy-header">Retirement Planner</div></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        my_age = st.number_input("My Age (Years)", 18, 80, current_age)
    with c2:
        retire_age = st.number_input("I want to retire at age", my_age + 1, 80, 50)
    with c3:
        plan_till = st.number_input("I want to plan till age", retire_age + 1, 100, 90)

    st.markdown("### Expense Details")
    e1, e2, e3 = st.columns(3)
    with e1:
        monthly_exp = st.number_input("Monthly Expenses (₹)", 0, 100000000, 60000)
    with e2:
        yearly_one_time = st.number_input("One-time Yearly Expenses (₹)", 0, 100000000, 125000)
    with e3:
        retire_infl = st.number_input("Inflation for Expenses (%)", 0.0, 20.0, 7.0) / 100

    st.markdown("### Retirement Assets")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        eq = st.number_input("Equity + NPS (₹)", 0, 1000000000, 1000000)
    with a2:
        debt = st.number_input("Debt + PPF + EPF (₹)", 0, 1000000000, 1000000)
    with a3:
        real_estate = st.number_input("Real Estate (₹)", 0, 1000000000, 0)
    with a4:
        gold = st.number_input("Gold (₹)", 0, 1000000000, 0)

    total_corpus = eq + debt + real_estate + gold
    curr_sip = st.number_input("Current Monthly SIP + NPS (₹)", 0, 100000000, 57500)
    curr_step = st.number_input("Current Annual Step-up (%)", 0.0, 50.0, 8.0) / 100
    post_ret_return = st.number_input("Post Retirement Expected Return (%)", 0.0, 20.0, 8.0) / 100

    years_to_ret = retire_age - my_age
    ret_years = plan_till - retire_age
    annual_exp_today = monthly_exp * 12 + yearly_one_time
    expense_at_ret = annual_exp_today * ((1 + retire_infl) ** years_to_ret)

    future_existing = total_corpus * ((1 + expected_return) ** years_to_ret)
    sip_future = 0
    sip_now = curr_sip
    for y in range(1, years_to_ret + 1):
        for _ in range(12):
            sip_future = sip_future * (1 + expected_return / 12) + sip_now
        sip_now *= (1 + curr_step)

    total_future_assets = future_existing + sip_future

    if post_ret_return > retire_infl:
        required_corpus = expense_at_ret * ((1 - ((1 + retire_infl) / (1 + post_ret_return)) ** ret_years) / (post_ret_return - retire_infl))
    else:
        required_corpus = expense_at_ret * ret_years

    gap = max(required_corpus - total_future_assets, 0)
    additional_sip = monthly_sip_required_stepup(gap, expected_return, years_to_ret, 0.05)

    summary = pd.DataFrame({
        "Metric": ["Total Retirement Corpus Required", "Current Investments Will Provide", "Future SIP + Existing Will Provide", "Additional Corpus to be Built", "SIP with 5% Annual Step-up"],
        "Value": [fmt(required_corpus), fmt(future_existing), fmt(total_future_assets), fmt(gap), fmt(additional_sip)]
    })
    st.table(summary)

    # Post retirement wealth table
    bal = total_future_assets
    rows = []
    exp = expense_at_ret
    for age in range(retire_age, plan_till + 1):
        opening = bal
        bal = bal * (1 + post_ret_return) - exp
        rows.append([age, round(opening,0), round(exp,0), round(bal,0)])
        exp *= (1 + retire_infl)
        if bal <= 0:
            break
    ret_df = pd.DataFrame(rows, columns=["Age", "Year Beginning Balance (₹)", "Year Expense (₹)", "Year End Balance (₹)"])
    st.dataframe(ret_df, use_container_width=True)
    advisor_note("Retirement Recommendation", ["Protect retirement corpus from child goals and lifestyle upgrades.", "Increase SIP annually with income growth to reduce future gap.", "Review retirement inflation assumptions carefully for medical and lifestyle costs."])

# =====================================================
# TERM INSURANCE
# =====================================================
if st.session_state.page == "term":
    back_button()
    st.markdown(f'<div class="prepared-line">Prepared for {client_name} by {advisor_name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="wealthy-box"><div class="wealthy-header">Term Insurance Calculator</div></div>', unsafe_allow_html=True)

    curr_age = st.number_input("Current Age (Years)", 18, 80, current_age)
    coverage_till = st.number_input("Coverage till Age (Years)", curr_age + 1, 100, 90)
    curr_monthly_income = st.number_input("Current Monthly Income (₹)", 0, 100000000, 200000)
    curr_monthly_expense = st.number_input("Current Monthly Expenses (₹)", 0, 100000000, 50000)
    infl = st.number_input("Applicable Inflation (%)", 0.0, 20.0, 6.0) / 100
    liabilities = st.number_input("Outstanding Liabilities (₹)", 0, 1000000000, 0)
    existing_cover = st.number_input("Existing Cover (₹)", 0, 1000000000, 0)

    years_left = coverage_till - curr_age
    annual_surplus = max((curr_monthly_income - curr_monthly_expense) * 12, 0)
    hlv = annual_surplus * years_left
    recommended_cover = max(hlv + liabilities - existing_cover, 0)

    st.success(f"You should have a term cover of {fmt(recommended_cover)}")
    advisor_note("Insurance Recommendation", ["Term plan is a protection product, not an investment product.", "Buying early reduces premium and locks insurability.", "Reassess cover after major life events like marriage, children, or large loans."])

# =====================================================
# CASHFLOW PLANNER
# =====================================================
if st.session_state.page == "cashflow":
    back_button()
    st.markdown(f'<div class="prepared-line">Prepared for {client_name} by {advisor_name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="wealthy-box"><div class="wealthy-header">Cashflow Planner</div></div>', unsafe_allow_html=True)

    st.markdown("### CASH INFLOWS")
    salary = st.number_input("Salary/Wages (After-Tax)", 0, 100000000, 1000000)
    side = st.number_input("Side Hustle / Freelance", 0, 100000000, 0)
    inv_income = st.number_input("Investment Income (Dividends, Interest)", 0, 100000000, 0)
    other_inc = st.number_input("Other Income (Rental, Tax Refund)", 0, 100000000, 0)
    total_inflow = salary + side + inv_income + other_inc

    st.markdown("### CASH OUTFLOWS - Fixed Expenses")
    rent = st.number_input("Rent / Mortgage", 0, 100000000, 300000)
    utilities = st.number_input("Utilities (Gas, Water, Electricity, Internet)", 0, 100000000, 60000)
    debt = st.number_input("Debt Payments (Student Loans, Car Loans)", 0, 100000000, 0)
    insurance = st.number_input("Insurance (Health, Life, Auto)", 0, 100000000, 50000)
    childcare = st.number_input("Childcare / Alimony", 0, 100000000, 0)

    st.markdown("### CASH OUTFLOWS - Variable Expenses")
    groceries = st.number_input("Groceries", 0, 100000000, 120000)
    dining = st.number_input("Dining Out / Entertainment", 0, 100000000, 60000)
    transport = st.number_input("Transportation / Fuel", 0, 100000000, 50000)
    shopping = st.number_input("Shopping / Subscriptions", 0, 100000000, 50000)

    st.markdown("### CASH OUTFLOWS - Savings & Investments")
    emergency = st.number_input("Emergency Fund Savings", 0, 100000000, 50000)
    retirement_contrib = st.number_input("Retirement Contributions (IRA / 401k / NPS / EPF)", 0, 100000000, 100000)
    investments = st.number_input("Investments (Stocks, Mutual Funds, Crypto)", 0, 100000000, 150000)

    total_outflow = rent + utilities + debt + insurance + childcare + groceries + dining + transport + shopping + emergency + retirement_contrib + investments
    net_cf = total_inflow - total_outflow

    cashflow_df = pd.DataFrame([
        ["CASH INFLOWS", "Salary/Wages (After-Tax)", salary],
        ["CASH INFLOWS", "Side Hustle / Freelance", side],
        ["CASH INFLOWS", "Investment Income (Dividends, Interest)", inv_income],
        ["CASH INFLOWS", "Other Income (Rental, Tax Refund)", other_inc],
        ["CASH INFLOWS", "Total Inflow (A)", total_inflow],
        ["FIXED EXPENSES", "Rent / Mortgage", rent],
        ["FIXED EXPENSES", "Utilities", utilities],
        ["FIXED EXPENSES", "Debt Payments", debt],
        ["FIXED EXPENSES", "Insurance", insurance],
        ["FIXED EXPENSES", "Childcare / Alimony", childcare],
        ["VARIABLE EXPENSES", "Groceries", groceries],
        ["VARIABLE EXPENSES", "Dining Out / Entertainment", dining],
        ["VARIABLE EXPENSES", "Transportation / Fuel", transport],
        ["VARIABLE EXPENSES", "Shopping / Subscriptions", shopping],
        ["SAVINGS & INVESTMENTS", "Emergency Fund Savings", emergency],
        ["SAVINGS & INVESTMENTS", "Retirement Contributions", retirement_contrib],
        ["SAVINGS & INVESTMENTS", "Investments", investments],
        ["TOTAL OUTFLOW", "Total Outflow (B)", total_outflow],
        ["NET CASH FLOW", "Total Inflow (A) – Total Outflow (B)", net_cf],
    ], columns=["Category", "Item", "Amount (₹)"])

    st.dataframe(cashflow_df, use_container_width=True)
    st.metric("Net Cash Flow", fmt(net_cf))
    advisor_note("Cashflow Recommendation", ["Positive cashflow should be directed toward goals and emergency reserve.", "Track lifestyle inflation yearly.", "Keep fixed obligations controlled to protect investing capacity."])

# =====================================================
# CAR PURCHASE
# =====================================================
if st.session_state.page == "car":
    back_button()
    st.subheader("Car Purchase Planner")
    car_cost = st.number_input("Car Cost Today (₹)", 0, 100000000, 1500000)
    down = st.number_input("Down Payment Available (₹)", 0, 100000000, 300000)
    after = st.number_input("Purchase After (Years)", 1, 20, 3)
    future_car = future_value(car_cost, inflation, after)
    gap = max(future_car - down, 0)
    sip_need = monthly_sip_required(gap, expected_return, after)
    lump_need = lumpsum_required(gap, expected_return, after)
    st.table(pd.DataFrame({"Metric": ["Future Car Cost", "Funding Gap", "Monthly SIP Required", "Lumpsum Required Today"], "Value": [fmt(future_car), fmt(gap), fmt(sip_need), fmt(lump_need)]}))

# =====================================================
# HOUSE PLANNING
# =====================================================
if st.session_state.page == "house":
    back_button()
    st.subheader("House Planning")
    house_cost = st.number_input("House Cost Today (₹)", 0, 1000000000, 10000000)
    available = st.number_input("Available Down Payment (₹)", 0, 1000000000, 2000000)
    after = st.number_input("Buy House After (Years)", 1, 30, 5)
    future_house = future_value(house_cost, inflation, after)
    target_down = future_house * 0.20
    gap = max(target_down - available, 0)
    sip_need = monthly_sip_required(gap, expected_return, after)
    st.table(pd.DataFrame({"Metric": ["Future House Cost", "20% Down Payment Target", "Down Payment Gap", "Monthly SIP Required"], "Value": [fmt(future_house), fmt(target_down), fmt(gap), fmt(sip_need)]}))

# =====================================================
# iPHONE PURCHASE
# =====================================================
if st.session_state.page == "iphone":
    back_button()
    st.subheader("iPhone Purchase Planner")
    cost = st.number_input("iPhone Cost Today (₹)", 0, 1000000, 80000)
    months = st.number_input("Buy After (Months)", 1, 60, 12)
    existing = st.number_input("Existing Savings (₹)", 0, 1000000, 10000)
    monthly_infl = (1 + inflation) ** (1/12) - 1
    future_cost = cost * ((1 + monthly_infl) ** months)
    gap = max(future_cost - existing, 0)
    r = expected_return / 12
    sip_need = gap / (((1 + r) ** months - 1) / r) if r > 0 and months > 0 else (gap / months if months > 0 else gap)
    st.table(pd.DataFrame({"Metric": ["Future iPhone Cost", "Funding Gap", "Monthly SIP Required"], "Value": [fmt(future_cost), fmt(gap), fmt(sip_need)]}))

# =====================================================
# PORTFOLIO ALLOCATION
# =====================================================
if st.session_state.page == "portfolio":
    back_button()
    st.subheader("Portfolio Allocation")
    total = st.number_input("Total Investible Corpus (₹)", 0, 1000000000, 10000000)
    risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    if risk == "Conservative":
        eq, debt, gold = 30, 60, 10
    elif risk == "Moderate":
        eq, debt, gold = 60, 30, 10
    else:
        eq, debt, gold = 75, 15, 10
    df = pd.DataFrame({"Asset Class": ["Equity", "Debt", "Gold"], "Allocation %": [eq, debt, gold], "Amount (₹)": [total*eq/100, total*debt/100, total*gold/100]})
    st.dataframe(df, use_container_width=True)

# =====================================================
# NET WORTH DASHBOARD
# =====================================================
if st.session_state.page == "networth":
    back_button()
    st.subheader("Net Worth Dashboard")
    mf = st.number_input("Mutual Funds (₹)", 0, 1000000000, 2000000)
    equity = st.number_input("Direct Equity (₹)", 0, 1000000000, 1000000)
    re_asset = st.number_input("Real Estate (₹)", 0, 10000000000, 5000000)
    cash = st.number_input("Cash / Bank (₹)", 0, 1000000000, 500000)
    home_loan = st.number_input("Home Loan (₹)", 0, 1000000000, 0)
    car_loan = st.number_input("Car Loan (₹)", 0, 1000000000, 0)
    other = st.number_input("Other Loans (₹)", 0, 1000000000, 0)
    assets = mf + equity + re_asset + cash
    liabilities = home_loan + car_loan + other
    nw = assets - liabilities
    st.metric("Total Assets", fmt(assets))
    st.metric("Total Liabilities", fmt(liabilities))
    st.metric("Net Worth", fmt(nw))

# =====================================================
# GOAL FEASIBILITY
# =====================================================
if st.session_state.page == "goal":
    back_button()
    st.subheader("Goal Feasibility Dashboard")
    target = st.number_input("Goal Target Amount (₹)", 0, 1000000000, 5000000)
    years = st.number_input("Years to Goal", 1, 40, 10)
    existing = st.number_input("Existing Corpus for Goal (₹)", 0, 1000000000, 500000)
    sip = st.number_input("Current Monthly SIP for Goal (₹)", 0, 100000000, 20000)
    proj = future_value(existing, expected_return, years)
    temp = proj
    for _ in range(years * 12):
        temp = temp * (1 + expected_return / 12) + sip
    shortfall = target - temp
    feas = temp / target * 100 if target > 0 else 0
    st.table(pd.DataFrame({"Metric": ["Goal Target", "Projected Value", "Funding Shortfall / Surplus", "Goal Feasibility %"], "Value": [fmt(target), fmt(temp), fmt(shortfall), f"{feas:.1f}%"]}))

# =====================================================
# PORTFOLIO REBALANCING
# =====================================================
if st.session_state.page == "rebalance":
    back_button()
    st.subheader("Portfolio Rebalancing Engine")
    cur_eq = st.number_input("Current Equity (₹)", 0, 1000000000, 600000)
    cur_debt = st.number_input("Current Debt (₹)", 0, 1000000000, 300000)
    cur_gold = st.number_input("Current Gold (₹)", 0, 1000000000, 100000)
    total = cur_eq + cur_debt + cur_gold
    tgt_eq = st.number_input("Target Equity %", 0, 100, 60)
    tgt_debt = st.number_input("Target Debt %", 0, 100, 30)
    tgt_gold = st.number_input("Target Gold %", 0, 100, 10)
    df = pd.DataFrame({
        "Asset Class": ["Equity", "Debt", "Gold"],
        "Current Amount (₹)": [cur_eq, cur_debt, cur_gold],
        "Target Amount (₹)": [total*tgt_eq/100, total*tgt_debt/100, total*tgt_gold/100]
    })
    df["Buy / Sell (₹)"] = df["Target Amount (₹)"] - df["Current Amount (₹)"]
    st.dataframe(df, use_container_width=True)

# =====================================================
# RETIREMENT MONTE CARLO
# =====================================================
if st.session_state.page == "mc_retirement":
    back_button()
    st.subheader("Retirement Monte Carlo Survival Simulator")
    corpus = st.number_input("Retirement Corpus (₹)", 0, 10000000000, 30000000)
    withdrawal = st.number_input("Annual Withdrawal (₹)", 0, 1000000000, 1200000)
    years = st.number_input("Retirement Years", 1, 50, 30)
    runs = st.number_input("Simulation Runs", 100, 5000, 1000, step=100)
    np.random.seed(123)
    success = 0
    for _ in range(runs):
        bal = corpus
        wd = withdrawal
        ok = True
        for _y in range(years):
            bal = bal * (1 + np.random.normal(expected_return, 0.12)) - wd
            wd *= (1 + inflation)
            if bal <= 0:
                ok = False
                break
        if ok:
            success += 1
    st.metric("Retirement Survival Probability", f"{(success/runs*100 if runs>0 else 0):.1f}%")

# =====================================================
# DEFAULT
# =====================================================
valid_pages = ["home", "sip", "swp", "sip_swp", "children", "retirement", "term", "cashflow", "car", "house", "iphone", "portfolio", "networth", "goal", "rebalance", "mc_retirement"]
if st.session_state.page not in valid_pages:
    st.session_state.page = "home"

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Freedom Wealth Platform | For Illustration / Advisory Discussion Purpose Only")
