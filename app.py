# FREEDOM ULTRA PRO V7 - SINGLE FILE WITH WEALTHY LOGO
# Streamlit single-file app with integrated logo support

import streamlit as st
import math
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Freedom ULTRA PRO V7", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
def fmt_inr(x):
    try:
        return f"₹{x:,.2f}"
    except:
        return f"₹{x}"


def future_value_sip(monthly_investment, annual_return, years):
    r = annual_return / 12 / 100
    n = years * 12
    if r == 0:
        return monthly_investment * n
    return monthly_investment * (((1 + r) ** n - 1) / r) * (1 + r)


def future_value_lumpsum(amount, annual_return, years):
    return amount * ((1 + annual_return / 100) ** years)


def emi(principal, annual_rate, years):
    r = annual_rate / 12 / 100
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)


def swp_monthly(corpus, annual_return, years):
    r = annual_return / 12 / 100
    n = years * 12
    if r == 0:
        return corpus / n
    return corpus * r / (1 - (1 + r) ** (-n))


def required_sip_for_goal(goal_amount, annual_return, years):
    r = annual_return / 12 / 100
    n = years * 12
    if r == 0:
        return goal_amount / n
    return goal_amount / ((((1 + r) ** n - 1) / r) * (1 + r))

# -----------------------------
# Theme CSS
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 0.8rem;}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
}
.main-wrap {
    background: linear-gradient(135deg, #0f172a, #111827, #1e1b4b);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 18px 22px;
    margin-bottom: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}
.main-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #c4b5fd;
    margin-bottom: 0.1rem;
}
.sub-title {
    color: #cbd5e1;
    font-size: 0.95rem;
}
.logo-box {
    background: rgba(255,255,255,0.04);
    border-radius: 18px;
    padding: 10px;
    border: 1px solid rgba(255,255,255,0.06);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Logo Handling
# -----------------------------
# Put your logo file in same folder as app.py with name: wealthy_logo.png
# OR keep the provided absolute path if running in this environment
logo_candidates = [
    Path("wealthy_logo.png"),
    Path("logo.png"),
    Path("image.png"),
    Path("/mnt/data/image.png"),
]

logo_path = None
for p in logo_candidates:
    if p.exists():
        logo_path = p
        break

# -----------------------------
# Sidebar
# -----------------------------
if logo_path:
    st.sidebar.image(str(logo_path), use_container_width=True)
else:
    st.sidebar.markdown("## 💜 Wealthy")

st.sidebar.title("Freedom ULTRA PRO V7")
module = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "SIP Calculator",
        "Lumpsum Calculator",
        "SWP Calculator",
        "EMI / Loan Planner",
        "Goal Planner",
        "Retirement Planner",
        "Insurance Need",
        "Child Education Planner",
        "Marriage Planner",
        "Travel Planner",
        "Car Purchase Planner",
        "iPhone Purchase Planner",
        "Cashflow Planner",
    ],
)

# -----------------------------
# Header with Logo
# -----------------------------
col_logo, col_head = st.columns([1, 4])
with col_logo:
    if logo_path:
        st.markdown('<div class="logo-box">', unsafe_allow_html=True)
        st.image(str(logo_path), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
with col_head:
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">Freedom ULTRA PRO V7</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Professional Financial Planning Super App • Single File Version • Wealthy Branded UI</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# -----------------------------
# Modules
# -----------------------------
if module == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Modules", "14")
    with c2:
        st.metric("Version", "V7")
    with c3:
        st.metric("Brand", "Wealthy")
    with c4:
        st.metric("Date", datetime.now().strftime("%d-%b-%Y"))

    st.success("Welcome to Wealthy branded Freedom ULTRA PRO V7.")
    st.markdown("### Included Features")
    st.write("- SIP, Lumpsum, SWP")
    st.write("- EMI / Car / iPhone purchase planning")
    st.write("- Goal, Child, Marriage, Retirement, Travel")
    st.write("- Insurance need analysis")
    st.write("- Monthly cashflow planning")

elif module == "SIP Calculator":
    st.subheader("📈 SIP Calculator")
    c1, c2, c3 = st.columns(3)
    with c1:
        sip_amt = st.number_input("Monthly SIP (₹)", min_value=0.0, value=10000.0, step=1000.0)
    with c2:
        ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
    with c3:
        years = st.number_input("Years", min_value=1, value=10, step=1)

    fv = future_value_sip(sip_amt, ret, years)
    invested = sip_amt * years * 12
    gain = fv - invested

    a, b, c = st.columns(3)
    a.metric("Total Invested", fmt_inr(invested))
    b.metric("Estimated Value", fmt_inr(fv))
    c.metric("Wealth Gain", fmt_inr(gain))

elif module == "Lumpsum Calculator":
    st.subheader("💰 Lumpsum Calculator")
    amt = st.number_input("Investment Amount (₹)", min_value=0.0, value=100000.0, step=10000.0)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5, key="ls_ret")
    years = st.number_input("Years", min_value=1, value=10, step=1, key="ls_year")
    fv = future_value_lumpsum(amt, ret, years)
    st.metric("Future Value", fmt_inr(fv))

elif module == "SWP Calculator":
    st.subheader("🏦 SWP Calculator")
    corpus = st.number_input("Corpus (₹)", min_value=0.0, value=5000000.0, step=100000.0)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=8.0, step=0.5, key="swp_ret")
    years = st.number_input("Withdrawal Years", min_value=1, value=20, step=1, key="swp_year")
    monthly = swp_monthly(corpus, ret, years)
    st.metric("Suggested Monthly SWP", fmt_inr(monthly))

elif module == "EMI / Loan Planner":
    st.subheader("🏠 EMI / Loan Planner")
    principal = st.number_input("Loan Amount (₹)", min_value=0.0, value=1000000.0, step=50000.0)
    rate = st.number_input("Interest Rate (%)", min_value=0.0, value=9.0, step=0.25)
    years = st.number_input("Tenure (Years)", min_value=1, value=5, step=1, key="emi_year")
    monthly_emi = emi(principal, rate, years)
    total_payment = monthly_emi * years * 12
    total_interest = total_payment - principal
    x, y, z = st.columns(3)
    x.metric("Monthly EMI", fmt_inr(monthly_emi))
    y.metric("Total Payment", fmt_inr(total_payment))
    z.metric("Total Interest", fmt_inr(total_interest))

elif module == "Goal Planner":
    st.subheader("🎯 Goal Planner")
    goal_name = st.text_input("Goal Name", "Dream Goal")
    goal_amt = st.number_input("Future Goal Amount (₹)", min_value=0.0, value=1000000.0, step=50000.0)
    years = st.number_input("Years to Goal", min_value=1, value=10, step=1, key="goal_year")
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5, key="goal_ret")
    sip_req = required_sip_for_goal(goal_amt, ret, years)
    st.success(f"Required monthly SIP for {goal_name}: {fmt_inr(sip_req)}")

elif module == "Retirement Planner":
    st.subheader("👴 Retirement Planner")
    current_age = st.number_input("Current Age", min_value=18, max_value=80, value=30)
    retire_age = st.number_input("Retirement Age", min_value=current_age+1, max_value=90, value=60)
    monthly_exp = st.number_input("Current Monthly Expense (₹)", min_value=0.0, value=50000.0, step=5000.0)
    inflation = st.number_input("Inflation (%)", min_value=0.0, value=6.0, step=0.5)
    post_ret_return = st.number_input("Post-Retirement Return (%)", min_value=0.0, value=8.0, step=0.5)
    life_expectancy = st.number_input("Life Expectancy", min_value=retire_age+1, max_value=100, value=85)

    years_to_ret = retire_age - current_age
    retirement_years = life_expectancy - retire_age
    future_monthly_exp = monthly_exp * ((1 + inflation/100) ** years_to_ret)
    corpus_needed = swp_monthly(1, post_ret_return, retirement_years)
    required_corpus = future_monthly_exp / corpus_needed if corpus_needed != 0 else 0

    st.metric("Monthly Expense at Retirement", fmt_inr(future_monthly_exp))
    st.metric("Approx Retirement Corpus Needed", fmt_inr(required_corpus))

elif module == "Insurance Need":
    st.subheader("🛡️ Insurance Need Analysis")
    annual_income = st.number_input("Annual Income (₹)", min_value=0.0, value=1200000.0, step=50000.0)
    liabilities = st.number_input("Outstanding Liabilities (₹)", min_value=0.0, value=2000000.0, step=50000.0)
    existing_cover = st.number_input("Existing Life Cover (₹)", min_value=0.0, value=1000000.0, step=50000.0)
    suggested_cover = max((annual_income * 15) + liabilities - existing_cover, 0)
    st.metric("Suggested Total Life Cover", fmt_inr(suggested_cover))

elif module == "Child Education Planner":
    st.subheader("🎓 Child Education Planner")
    current_cost = st.number_input("Current Education Cost (₹)", min_value=0.0, value=2000000.0, step=100000.0)
    years = st.number_input("Years Left", min_value=1, value=15, step=1, key="child_year")
    inflation = st.number_input("Education Inflation (%)", min_value=0.0, value=10.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5, key="child_ret")
    future_cost = current_cost * ((1 + inflation/100) ** years)
    sip_req = required_sip_for_goal(future_cost, ret, years)
    st.metric("Future Education Cost", fmt_inr(future_cost))
    st.metric("Required SIP", fmt_inr(sip_req))

elif module == "Marriage Planner":
    st.subheader("💍 Marriage Planner")
    current_cost = st.number_input("Current Marriage Budget (₹)", min_value=0.0, value=1500000.0, step=100000.0)
    years = st.number_input("Years Left", min_value=1, value=10, step=1, key="marriage_year")
    inflation = st.number_input("Marriage Inflation (%)", min_value=0.0, value=8.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5, key="marriage_ret")
    future_cost = current_cost * ((1 + inflation/100) ** years)
    sip_req = required_sip_for_goal(future_cost, ret, years)
    st.metric("Future Marriage Cost", fmt_inr(future_cost))
    st.metric("Required SIP", fmt_inr(sip_req))

elif module == "Travel Planner":
    st.subheader("✈️ Travel Planner")
    budget = st.number_input("Current Travel Budget (₹)", min_value=0.0, value=300000.0, step=10000.0)
    years = st.number_input("Years Left", min_value=1, value=3, step=1, key="travel_year")
    inflation = st.number_input("Travel Inflation (%)", min_value=0.0, value=7.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=10.0, step=0.5, key="travel_ret")
    future_cost = budget * ((1 + inflation/100) ** years)
    sip_req = required_sip_for_goal(future_cost, ret, years)
    st.metric("Future Travel Budget", fmt_inr(future_cost))
    st.metric("Required SIP", fmt_inr(sip_req))

elif module == "Car Purchase Planner":
    st.subheader("🚗 Car Purchase Planner")
    car_price = st.number_input("Current Car Price (₹)", min_value=0.0, value=1200000.0, step=50000.0)
    down_payment_pct = st.slider("Down Payment %", 0, 100, 20)
    years_to_buy = st.number_input("Years to Buy", min_value=1, value=3, step=1, key="car_buy_year")
    inflation = st.number_input("Car Inflation (%)", min_value=0.0, value=6.0, step=0.5)
    ret = st.number_input("Expected Return (%)", min_value=0.0, value=10.0, step=0.5, key="car_ret")
    future_price = car_price * ((1 + inflation/100) ** years_to_buy)
    down_payment = future_price * down_payment_pct / 100
    sip_req = required_sip_for_goal(down_payment, ret, years_to_buy)
    st.metric("Estimated Future Car Price", fmt_inr(future_price))
    st.metric("Target Down Payment", fmt_inr(down_payment))
    st.metric("Required SIP for Down Payment", fmt_inr(sip_req))

elif module == "iPhone Purchase Planner":
    st.subheader("📱 iPhone Purchase Planner")
    iphone_price = st.number_input("Current iPhone Price (₹)", min_value=0.0, value=80000.0, step=5000.0)
    months = st.number_input("Months to Buy", min_value=1, value=12, step=1)
    inflation = st.number_input("Price Increase (%)", min_value=0.0, value=5.0, step=0.5)
    future_price = iphone_price * ((1 + inflation/100) ** (months/12))
    monthly_save = future_price / months
    st.metric("Estimated Future Price", fmt_inr(future_price))
    st.metric("Monthly Saving Needed", fmt_inr(monthly_save))

elif module == "Cashflow Planner":
    st.subheader("💸 Monthly Cashflow Planner")
    income = st.number_input("Monthly Income (₹)", min_value=0.0, value=100000.0, step=5000.0)
    fixed = st.number_input("Fixed Expenses (₹)", min_value=0.0, value=40000.0, step=5000.0)
    variable = st.number_input("Variable Expenses (₹)", min_value=0.0, value=20000.0, step=5000.0)
    emi_amt = st.number_input("EMIs (₹)", min_value=0.0, value=10000.0, step=5000.0)
    invest = st.number_input("Investments / SIP (₹)", min_value=0.0, value=15000.0, step=5000.0)

    total_outflow = fixed + variable + emi_amt + invest
    surplus = income - total_outflow
    savings_rate = (invest / income * 100) if income else 0

    a, b, c = st.columns(3)
    a.metric("Total Outflow", fmt_inr(total_outflow))
    b.metric("Monthly Surplus", fmt_inr(surplus))
    c.metric("Investment Rate", f"{savings_rate:.2f}%")

st.divider()
st.caption("Wealthy | Freedom ULTRA PRO V7 • Single-file app.py with logo support. Place logo as wealthy_logo.png in same folder for deployment.")
