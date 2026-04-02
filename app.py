import streamlit as st
import pandas as pd
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Freedom ULTRA PRO V2",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# PREMIUM DARK CSS
# =========================================================
st.markdown("""
<style>
:root {
    --bg: #0b1220;
    --panel: #111827;
    --panel2: #0f172a;
    --border: #243244;
    --text: #e5e7eb;
    --muted: #94a3b8;
    --gold: #f59e0b;
    --gold2: #fbbf24;
    --green: #10b981;
    --red: #ef4444;
    --blue: #2563eb;
}
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0b1220 0%, #0f172a 100%);
    color: var(--text);
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1c 0%, #111827 100%);
    border-right: 1px solid var(--border);
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}
.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 4px;
}
.sub-title {
    font-size: 15px;
    color: var(--muted);
    margin-bottom: 14px;
}
.brand-bar {
    background: linear-gradient(90deg, rgba(245,158,11,0.15), rgba(37,99,235,0.15));
    border: 1px solid rgba(245,158,11,0.25);
    color: #f8fafc;
    padding: 14px 18px;
    border-radius: 16px;
    margin-bottom: 16px;
    font-size: 14px;
    font-weight: 600;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 8px;
    margin-bottom: 12px;
}
.kpi {
    background: linear-gradient(180deg, rgba(17,24,39,0.95), rgba(15,23,42,0.95));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 12px 14px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.22);
}
.small-label {
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
}
.kpi-sub {
    font-size: 12px;
    color: var(--gold2);
}
.footer-note {
    color: var(--muted);
    font-size: 13px;
    margin-top: 15px;
}
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(17,24,39,0.95), rgba(15,23,42,0.95));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 10px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.20);
}
div[data-testid="stMetric"] label {
    color: var(--muted) !important;
}
div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--border);
}
div.stButton > button {
    background: linear-gradient(90deg, #f59e0b, #fbbf24);
    color: #111827;
    font-weight: 700;
    border-radius: 12px;
    border: none;
}
hr {
    border-color: rgba(148,163,184,0.15);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE INIT
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "lead_db" not in st.session_state:
    st.session_state.lead_db = pd.DataFrame([
        {
            "Lead ID": "L001",
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Client Name": "Rahul Sharma",
            "Mobile": "9999999991",
            "City": "Bengaluru",
            "Lead Source": "Referral",
            "Lead Stage": "Qualified",
            "Follow-up Status": "Today",
            "Monthly Income": 120000,
            "Monthly Surplus": 35000,
            "Lead Score": 78,
            "Lead Temperature": "🔥 Hot Lead"
        },
        {
            "Lead ID": "L002",
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Client Name": "Amit Verma",
            "Mobile": "9999999992",
            "City": "Mumbai",
            "Lead Source": "Digital",
            "Lead Stage": "Prospect",
            "Follow-up Status": "Pending",
            "Monthly Income": 70000,
            "Monthly Surplus": 15000,
            "Lead Score": 46,
            "Lead Temperature": "🔵 Cold Lead"
        }
    ])

if "client_db" not in st.session_state:
    st.session_state.client_db = pd.DataFrame([
        {
            "Client ID": "C001",
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Client Name": "Sneha Patel",
            "Mobile": "9999999993",
            "City": "Delhi",
            "Segment": "Growth",
            "Risk Category": "Balanced",
            "Monthly SIP": 12000,
            "Net Worth": 2800000
        },
        {
            "Client ID": "C002",
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Client Name": "Karan Mehta",
            "Mobile": "9999999994",
            "City": "Hyderabad",
            "Segment": "Premium",
            "Risk Category": "Aggressive",
            "Monthly SIP": 30000,
            "Net Worth": 12500000
        }
    ])

# =========================================================
# LOGIN SCREEN
# =========================================================
if not st.session_state.logged_in:
    st.markdown('<div class="main-title">🚀 Freedom ULTRA PRO V2</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Persistent CRM • Lead Master • Client Master • Search • Filter • Delete • MIS Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-bar">Login to access your premium advisory workspace</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown("### 🔐 Advisor Login")
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="freedom123")
        if st.button("Login"):
            if username == "admin" and password == "freedom123":
                st.session_state.logged_in = True
                st.success("Login successful. Please continue.")
                st.rerun()
            else:
                st.error("Invalid username or password.")
        st.info("Demo login credentials: admin / freedom123")
    st.stop()

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">🚀 Freedom ULTRA PRO V2</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Persistent CRM • Add Lead • Add Client • Search • Filter • Delete • SIP Conversion • Reports</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="brand-bar">Freedom Advisory ULTRA PRO V2 • Business Operating System for MFD / Advisor Growth</div>',
    unsafe_allow_html=True
)

# =========================================================
# HELPERS
# =========================================================
def format_inr(value):
    try:
        return f"₹{float(value):,.0f}"
    except:
        return "₹0"

def safe_ratio(a, b):
    if b == 0:
        return 0.0
    return (a / b) * 100

def future_value_with_inflation(current_value, inflation, years):
    return current_value * ((1 + inflation / 100) ** years)

def calculate_sip(future_value, annual_return, years):
    n = years * 12
    r = annual_return / 100 / 12
    if n <= 0:
        return 0.0
    if r == 0:
        return future_value / n
    denominator = ((1 + r) ** n - 1)
    if denominator == 0:
        return 0.0
    return max(future_value * r / denominator, 0.0)

def calculate_lumpsum_required(future_value, annual_return, years):
    if years <= 0:
        return future_value
    return future_value / ((1 + annual_return / 100) ** years)

def retirement_corpus_needed(monthly_expense_today, inflation, years_to_retire, years_post_retirement, post_ret_return):
    monthly_expense_at_retirement = monthly_expense_today * ((1 + inflation / 100) ** years_to_retire)
    annual_expense_at_retirement = monthly_expense_at_retirement * 12
    real_return = ((1 + post_ret_return / 100) / (1 + inflation / 100)) - 1

    if real_return <= 0:
        corpus = annual_expense_at_retirement * years_post_retirement
    else:
        corpus = annual_expense_at_retirement * ((1 - (1 + real_return) ** (-years_post_retirement)) / real_return)

    return max(corpus, 0.0), max(monthly_expense_at_retirement, 0.0)

def calculate_life_cover(monthly_expense, years_support, liabilities_amt, existing_assets, annual_income):
    family_expense_need = monthly_expense * 12 * years_support
    income_replacement = annual_income * 10
    cover = family_expense_need + liabilities_amt + income_replacement - existing_assets
    return max(cover, 0.0)

def emi_calculator(principal, annual_rate, years):
    n = years * 12
    r = annual_rate / 100 / 12
    if n <= 0:
        return 0.0, 0.0, 0.0
    if r == 0:
        emi = principal / n
        total_payment = emi * n
        total_interest = total_payment - principal
        return max(emi, 0.0), max(total_interest, 0.0), max(total_payment, 0.0)

    emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
    total_payment = emi * n
    total_interest = total_payment - principal
    return max(emi, 0.0), max(total_interest, 0.0), max(total_payment, 0.0)

def tax_regime_old(annual_income, deductions):
    taxable = max(annual_income - deductions, 0)
    tax = 0.0

    if taxable <= 250000:
        tax = 0
    elif taxable <= 500000:
        tax = (taxable - 250000) * 0.05
    elif taxable <= 1000000:
        tax = 12500 + (taxable - 500000) * 0.20
    else:
        tax = 112500 + (taxable - 1000000) * 0.30

    cess = tax * 0.04
    total_tax = tax + cess

    if taxable <= 500000:
        total_tax = 0.0

    return max(taxable, 0.0), max(total_tax, 0.0)

def tax_regime_new(annual_income):
    taxable = max(annual_income, 0)
    slabs = [
        (400000, 0.00),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
    ]

    tax = 0.0
    prev_limit = 0.0

    for limit, rate in slabs:
        if taxable > limit:
            tax += (limit - prev_limit) * rate
            prev_limit = limit
        else:
            tax += (taxable - prev_limit) * rate
            prev_limit = taxable
            break

    if taxable > 2400000:
        tax += (taxable - 2400000) * 0.30

    cess = tax * 0.04
    total_tax = tax + cess

    if taxable <= 1200000:
        total_tax = 0.0

    return max(taxable, 0.0), max(total_tax, 0.0)

def risk_score_from_inputs(age, monthly_surplus, monthly_income, risk_profile):
    if age <= 30:
        age_score = 30
    elif age <= 40:
        age_score = 24
    elif age <= 50:
        age_score = 18
    elif age <= 60:
        age_score = 12
    else:
        age_score = 6

    sr = safe_ratio(monthly_surplus, monthly_income)
    if sr >= 30:
        savings_score = 30
    elif sr >= 20:
        savings_score = 24
    elif sr >= 10:
        savings_score = 16
    else:
        savings_score = 8

    profile_map = {"Low": 15, "Moderate": 25, "High": 35}
    profile_score = profile_map.get(risk_profile, 20)

    total = max(min(age_score + savings_score + profile_score, 100), 0)

    if total >= 75:
        category = "Aggressive"
    elif total >= 50:
        category = "Balanced"
    else:
        category = "Conservative"

    return total, category

def get_allocation(category):
    allocation_map = {
        "Conservative": {"Equity": 30, "Debt": 50, "Gold": 10, "Cash": 10},
        "Balanced": {"Equity": 55, "Debt": 25, "Gold": 10, "Cash": 10},
        "Aggressive": {"Equity": 75, "Debt": 10, "Gold": 10, "Cash": 5}
    }
    return allocation_map.get(category, allocation_map["Balanced"])

def get_lead_temperature(score):
    if score >= 75:
        return "🔥 Hot Lead"
    elif score >= 50:
        return "🟡 Warm Lead"
    return "🔵 Cold Lead"

def get_conversion_probability(score):
    if score >= 85:
        return "Very High"
    elif score >= 70:
        return "High"
    elif score >= 50:
        return "Medium"
    return "Low"

def get_client_segment(monthly_income, monthly_surplus, net_worth):
    if monthly_income >= 300000 or net_worth >= 10000000:
        return "Premium"
    elif monthly_income >= 100000 or net_worth >= 2500000:
        return "Growth"
    elif monthly_surplus > 0:
        return "Emerging"
    return "Starter"

def next_lead_id():
    count = len(st.session_state.lead_db) + 1
    return f"L{str(count).zfill(3)}"

def next_client_id():
    count = len(st.session_state.client_db) + 1
    return f"C{str(count).zfill(3)}"

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("🏢 Freedom ULTRA PRO V2 Setup")

advisor_name = st.sidebar.text_input("Advisor / MFD Name", "Freedom Advisory")
branch_name = st.sidebar.text_input("Branch / Location", "Bengaluru")
rm_name = st.sidebar.text_input("Relationship Manager", "Parvez")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("📞 Lead Details")

meeting_type = st.sidebar.selectbox(
    "Meeting Type",
    ["New Lead", "Follow-up", "Second Meeting", "SIP Upgrade", "Retirement Review", "Protection Review"]
)
lead_source = st.sidebar.selectbox(
    "Lead Source",
    ["Referral", "Walk-in", "Existing Client", "Digital", "Corporate Reference", "Other"]
)
lead_stage = st.sidebar.selectbox(
    "Lead Stage",
    ["Prospect", "Qualified", "Proposal Shared", "Negotiation", "Converted"]
)
follow_up_status = st.sidebar.selectbox(
    "Follow-up Status",
    ["Pending", "Today", "This Week", "Completed"]
)
days_since_last_meeting = st.sidebar.number_input("Days Since Last Meeting", min_value=0, max_value=365, value=3, step=1)

st.sidebar.markdown("---")
st.sidebar.header("👤 Client Details")

client_name = st.sidebar.text_input("Client Name", "Freedom Client")
mobile_no = st.sidebar.text_input("Client Mobile", "9999999999")
city_name = st.sidebar.text_input("City", "Bengaluru")

age = st.sidebar.number_input("Current Age", min_value=18, max_value=80, value=30, step=1)
retirement_age = st.sidebar.number_input("Retirement Age", min_value=40, max_value=80, value=60, step=1)
dependents = st.sidebar.number_input("Dependents", min_value=0, max_value=10, value=2, step=1)
risk_profile = st.sidebar.selectbox("Declared Risk Profile", ["Low", "Moderate", "High"])

st.sidebar.markdown("---")
st.sidebar.header("💰 Financial Inputs")

monthly_income = st.sidebar.number_input("Monthly Income (₹)", min_value=10000, max_value=5000000, value=80000, step=5000)
monthly_expenses = st.sidebar.number_input("Monthly Expenses (₹)", min_value=5000, max_value=5000000, value=45000, step=5000)
existing_savings = st.sidebar.number_input("Existing Savings (₹)", min_value=0, max_value=100000000, value=300000, step=10000)
existing_investments = st.sidebar.number_input("Existing Investments (₹)", min_value=0, max_value=100000000, value=500000, step=10000)
liabilities = st.sidebar.number_input("Total Liabilities / Loans (₹)", min_value=0, max_value=100000000, value=200000, step=10000)
existing_sip = st.sidebar.number_input("Existing SIP (₹/month)", min_value=0, max_value=500000, value=5000, step=500)
existing_life_cover = st.sidebar.number_input("Existing Life Cover (₹)", min_value=0, max_value=500000000, value=1000000, step=50000)
existing_health_cover = st.sidebar.number_input("Existing Health Cover (₹)", min_value=0, max_value=50000000, value=500000, step=50000)

st.sidebar.markdown("---")
st.sidebar.header("📈 Planning Assumptions")

goal_return = st.sidebar.slider("Expected Return for Goals (%)", 1, 20, 12)
inflation_rate = st.sidebar.slider("Inflation Rate (%)", 1, 12, 6)
retirement_return_pre = st.sidebar.slider("Pre-Retirement Return (%)", 1, 20, 12)
retirement_return_post = st.sidebar.slider("Post-Retirement Return (%)", 1, 12, 7)
life_expectancy = st.sidebar.slider("Life Expectancy", 65, 100, 85)

# =========================================================
# CORE CALCULATIONS
# =========================================================
monthly_surplus = monthly_income - monthly_expenses
annual_income = monthly_income * 12
savings_ratio = safe_ratio(monthly_surplus, monthly_income)
net_worth = existing_savings + existing_investments - liabilities

years_to_retirement = max(retirement_age - age, 0)
years_post_retirement = max(life_expectancy - retirement_age, 1)

ret_corpus, expense_at_retirement = retirement_corpus_needed(
    monthly_expenses, inflation_rate, years_to_retirement, years_post_retirement, retirement_return_post
)

current_total_assets = existing_savings + existing_investments
future_existing_assets = current_total_assets * ((1 + retirement_return_pre / 100) ** years_to_retirement) if years_to_retirement > 0 else current_total_assets
additional_corpus_needed = max(ret_corpus - future_existing_assets, 0.0)
retirement_sip = calculate_sip(additional_corpus_needed, retirement_return_pre, years_to_retirement) if years_to_retirement > 0 else 0.0

recommended_life_cover = calculate_life_cover(monthly_expenses, 15, liabilities, current_total_assets, annual_income)
life_cover_gap = max(recommended_life_cover - existing_life_cover, 0.0)

recommended_emergency_fund = monthly_expenses * 6
recommended_health_cover = max(500000.0, annual_income * 0.5)
health_cover_gap = max(recommended_health_cover - existing_health_cover, 0.0)

risk_score, derived_risk_category = risk_score_from_inputs(age, monthly_surplus, monthly_income, risk_profile)
suggested_allocation = get_allocation(derived_risk_category)
client_segment = get_client_segment(monthly_income, monthly_surplus, net_worth)

# CRM scoring
lead_score = 0
lead_score += {"Referral": 25, "Existing Client": 20, "Corporate Reference": 18, "Walk-in": 12, "Digital": 10, "Other": 8}.get(lead_source, 8)
lead_score += {"Prospect": 10, "Qualified": 25, "Proposal Shared": 45, "Negotiation": 65, "Converted": 100}.get(lead_stage, 0)
lead_score += {"Completed": 10, "Today": 8, "This Week": 5, "Pending": 2}.get(follow_up_status, 2)

if days_since_last_meeting <= 3:
    lead_score += 10
elif days_since_last_meeting <= 7:
    lead_score += 7
elif days_since_last_meeting <= 15:
    lead_score += 4
else:
    lead_score += 1

if monthly_surplus >= 30000:
    lead_score += 20
elif monthly_surplus >= 15000:
    lead_score += 14
elif monthly_surplus > 0:
    lead_score += 8
else:
    lead_score += 2

lead_score = max(min(lead_score, 100), 0)
lead_temperature = get_lead_temperature(lead_score)
conversion_probability = get_conversion_probability(lead_score)

sip_conversion_score = 0
if monthly_surplus > 0:
    sip_conversion_score += 30
if existing_sip > 0:
    sip_conversion_score += 20
if lead_source in ["Referral", "Existing Client"]:
    sip_conversion_score += 20
if lead_stage in ["Proposal Shared", "Negotiation", "Converted"]:
    sip_conversion_score += 20
if age <= 45:
    sip_conversion_score += 10
sip_conversion_score = max(min(sip_conversion_score, 100), 0)

cross_sell_score = 0
if life_cover_gap > 0:
    cross_sell_score += 35
if health_cover_gap > 0:
    cross_sell_score += 25
if liabilities > 0:
    cross_sell_score += 15
if dependents > 0:
    cross_sell_score += 15
if existing_life_cover == 0:
    cross_sell_score += 10
cross_sell_score = max(min(cross_sell_score, 100), 0)

# =========================================================
# TOP KPI STRIP
# =========================================================
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(f'<div class="kpi"><div class="small-label">Lead Score</div><div class="kpi-value">{lead_score}/100</div><div class="kpi-sub">{lead_temperature}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi"><div class="small-label">SIP Score</div><div class="kpi-value">{sip_conversion_score}/100</div><div class="kpi-sub">Conversion</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi"><div class="small-label">Cross-Sell</div><div class="kpi-value">{cross_sell_score}/100</div><div class="kpi-sub">Protection</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi"><div class="small-label">Monthly Surplus</div><div class="kpi-value">{format_inr(monthly_surplus)}</div><div class="kpi-sub">Cashflow</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="kpi"><div class="small-label">Client Segment</div><div class="kpi-value">{client_segment}</div><div class="kpi-sub">{derived_risk_category}</div></div>', unsafe_allow_html=True)
with k6:
    st.markdown(f'<div class="kpi"><div class="small-label">Net Worth</div><div class="kpi-value">{format_inr(net_worth)}</div><div class="kpi-sub">{conversion_probability}</div></div>', unsafe_allow_html=True)

st.markdown("")

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "🎯 Dashboard",
    "📞 Lead CRM V2",
    "👥 Client CRM V2",
    "📈 SIP Proposal",
    "🏖 Retirement",
    "🛡 Protection",
    "🏦 EMI + Tax",
    "🏆 RM Leaderboard",
    "📂 CSV Upload",
    "📊 MIS Reports",
    "🧾 Final Summary"
])

# =========================================================
# TAB 1 - DASHBOARD
# =========================================================
with tab1:
    st.markdown('<div class="section-title">ULTRA PRO V2 Business Dashboard</div>', unsafe_allow_html=True)

    total_leads = len(st.session_state.lead_db)
    total_clients = len(st.session_state.client_db)
    hot_leads = len(st.session_state.lead_db[st.session_state.lead_db["Lead Temperature"] == "🔥 Hot Lead"])
    total_client_sip = st.session_state.client_db["Monthly SIP"].sum() if len(st.session_state.client_db) > 0 else 0

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Total Leads", total_leads)
    d2.metric("Total Clients", total_clients)
    d3.metric("Hot Leads", hot_leads)
    d4.metric("Client Book SIP", format_inr(total_client_sip))

    dash_df = pd.DataFrame({
        "Score": [lead_score, sip_conversion_score, cross_sell_score, risk_score]
    }, index=["Lead", "SIP", "Cross-Sell", "Risk"])
    st.bar_chart(dash_df, use_container_width=True)

    pipeline_summary = st.session_state.lead_db.groupby("Lead Stage").size().reset_index(name="Count")
    if len(pipeline_summary) > 0:
        st.markdown("### 📌 Lead Pipeline Summary")
        st.dataframe(pipeline_summary, use_container_width=True, hide_index=True)

# =========================================================
# TAB 2 - LEAD CRM V2
# =========================================================
with tab2:
    st.markdown('<div class="section-title">Lead CRM V2 (Add • Search • Filter • Delete)</div>', unsafe_allow_html=True)

    st.markdown("### ➕ Add New Lead")
    l1, l2, l3, l4 = st.columns(4)
    with l1:
        new_lead_name = st.text_input("Lead Name", key="new_lead_name")
    with l2:
        new_lead_mobile = st.text_input("Lead Mobile", key="new_lead_mobile")
    with l3:
        new_lead_city = st.text_input("Lead City", key="new_lead_city", value="Bengaluru")
    with l4:
        new_lead_source = st.selectbox("Lead Source", ["Referral", "Walk-in", "Existing Client", "Digital", "Corporate Reference", "Other"], key="new_lead_source")

    l5, l6, l7, l8 = st.columns(4)
    with l5:
        new_lead_stage = st.selectbox("Lead Stage", ["Prospect", "Qualified", "Proposal Shared", "Negotiation", "Converted"], key="new_lead_stage")
    with l6:
        new_followup = st.selectbox("Follow-up Status", ["Pending", "Today", "This Week", "Completed"], key="new_followup")
    with l7:
        new_income = st.number_input("Monthly Income (₹)", min_value=0, max_value=5000000, value=50000, step=5000, key="new_income")
    with l8:
        new_surplus = st.number_input("Monthly Surplus (₹)", min_value=-500000, max_value=5000000, value=10000, step=5000, key="new_surplus")

    if st.button("Add Lead"):
        temp_score = 0
        temp_score += {"Referral": 25, "Existing Client": 20, "Corporate Reference": 18, "Walk-in": 12, "Digital": 10, "Other": 8}.get(new_lead_source, 8)
        temp_score += {"Prospect": 10, "Qualified": 25, "Proposal Shared": 45, "Negotiation": 65, "Converted": 100}.get(new_lead_stage, 0)
        temp_score += {"Completed": 10, "Today": 8, "This Week": 5, "Pending": 2}.get(new_followup, 2)
        if new_surplus >= 30000:
            temp_score += 20
        elif new_surplus >= 15000:
            temp_score += 14
        elif new_surplus > 0:
            temp_score += 8
        else:
            temp_score += 2
        temp_score = max(min(temp_score, 100), 0)

        new_row = pd.DataFrame([{
            "Lead ID": next_lead_id(),
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Client Name": new_lead_name if new_lead_name else "Unnamed Lead",
            "Mobile": new_lead_mobile if new_lead_mobile else "",
            "City": new_lead_city,
            "Lead Source": new_lead_source,
            "Lead Stage": new_lead_stage,
            "Follow-up Status": new_followup,
            "Monthly Income": new_income,
            "Monthly Surplus": new_surplus,
            "Lead Score": temp_score,
            "Lead Temperature": get_lead_temperature(temp_score)
        }])

        st.session_state.lead_db = pd.concat([st.session_state.lead_db, new_row], ignore_index=True)
        st.success("Lead added successfully.")

    st.markdown("---")
    st.markdown("### 🔎 Search / Filter Leads")

    s1, s2 = st.columns(2)
    with s1:
        lead_search = st.text_input("Search by Name / Mobile / City", key="lead_search")
    with s2:
        stage_filter = st.selectbox("Filter by Lead Stage", ["All", "Prospect", "Qualified", "Proposal Shared", "Negotiation", "Converted"], key="stage_filter")

    lead_view = st.session_state.lead_db.copy()

    if lead_search:
        search_lower = lead_search.lower()
        lead_view = lead_view[
            lead_view["Client Name"].astype(str).str.lower().str.contains(search_lower) |
            lead_view["Mobile"].astype(str).str.lower().str.contains(search_lower) |
            lead_view["City"].astype(str).str.lower().str.contains(search_lower)
        ]

    if stage_filter != "All":
        lead_view = lead_view[lead_view["Lead Stage"] == stage_filter]

    st.dataframe(lead_view, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download Leads CSV",
        data=st.session_state.lead_db.to_csv(index=False).encode("utf-8"),
        file_name="freedom_leads_v2.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.markdown("### 🗑 Delete Lead")

    if len(st.session_state.lead_db) > 0:
        delete_lead_id = st.selectbox("Select Lead ID to Delete", st.session_state.lead_db["Lead ID"].tolist(), key="delete_lead_id")
        if st.button("Delete Selected Lead"):
            st.session_state.lead_db = st.session_state.lead_db[st.session_state.lead_db["Lead ID"] != delete_lead_id].reset_index(drop=True)
            st.success(f"Lead {delete_lead_id} deleted successfully.")
    else:
        st.info("No leads available to delete.")

# =========================================================
# TAB 3 - CLIENT CRM V2
# =========================================================
with tab3:
    st.markdown('<div class="section-title">Client CRM V2 (Add • Search • Delete)</div>', unsafe_allow_html=True)

    st.markdown("### ➕ Add New Client")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        new_client_name = st.text_input("Client Name", key="new_client_name")
    with c2:
        new_client_mobile = st.text_input("Client Mobile", key="new_client_mobile")
    with c3:
        new_client_city = st.text_input("Client City", key="new_client_city", value="Bengaluru")
    with c4:
        new_client_sip = st.number_input("Monthly SIP (₹)", min_value=0, max_value=5000000, value=5000, step=500, key="new_client_sip")

    c5, c6, c7 = st.columns(3)
    with c5:
        new_client_income = st.number_input("Monthly Income (₹)", min_value=0, max_value=5000000, value=80000, step=5000, key="new_client_income")
    with c6:
        new_client_networth = st.number_input("Net Worth (₹)", min_value=0, max_value=500000000, value=1000000, step=50000, key="new_client_networth")
    with c7:
        new_client_risk = st.selectbox("Risk Category", ["Conservative", "Balanced", "Aggressive"], key="new_client_risk")

    if st.button("Add Client"):
        temp_surplus = max(new_client_income - (new_client_income * 0.6), 0)
        temp_segment = get_client_segment(new_client_income, temp_surplus, new_client_networth)

        new_client_row = pd.DataFrame([{
            "Client ID": next_client_id(),
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Client Name": new_client_name if new_client_name else "Unnamed Client",
            "Mobile": new_client_mobile if new_client_mobile else "",
            "City": new_client_city,
            "Segment": temp_segment,
            "Risk Category": new_client_risk,
            "Monthly SIP": new_client_sip,
            "Net Worth": new_client_networth
        }])

        st.session_state.client_db = pd.concat([st.session_state.client_db, new_client_row], ignore_index=True)
        st.success("Client added successfully.")

    st.markdown("---")
    st.markdown("### 🔎 Search Clients")

    client_search = st.text_input("Search by Name / Mobile / City", key="client_search")

    client_view = st.session_state.client_db.copy()
    if client_search:
        search_lower = client_search.lower()
        client_view = client_view[
            client_view["Client Name"].astype(str).str.lower().str.contains(search_lower) |
            client_view["Mobile"].astype(str).str.lower().str.contains(search_lower) |
            client_view["City"].astype(str).str.lower().str.contains(search_lower)
        ]

    st.dataframe(client_view, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download Clients CSV",
        data=st.session_state.client_db.to_csv(index=False).encode("utf-8"),
        file_name="freedom_clients_v2.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.markdown("### 🗑 Delete Client")

    if len(st.session_state.client_db) > 0:
        delete_client_id = st.selectbox("Select Client ID to Delete", st.session_state.client_db["Client ID"].tolist(), key="delete_client_id")
        if st.button("Delete Selected Client"):
            st.session_state.client_db = st.session_state.client_db[st.session_state.client_db["Client ID"] != delete_client_id].reset_index(drop=True)
            st.success(f"Client {delete_client_id} deleted successfully.")
    else:
        st.info("No clients available to delete.")

# =========================================================
# TAB 4 - SIP PROPOSAL
# =========================================================
with tab4:
    st.markdown('<div class="section-title">ULTRA PRO V2 SIP Proposal</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        goal_name = st.selectbox("Select Goal", [
            "Emergency Fund", "Child Education", "Marriage", "House Purchase",
            "Car Purchase", "Vacation", "Wealth Creation", "Custom Goal"
        ])
    with col2:
        current_goal_cost = st.number_input("Current Goal Cost (₹)", min_value=10000, max_value=500000000, value=1000000, step=50000)
    with col3:
        goal_years = st.slider("Years to Goal", 1, 40, 10)

    inflated_goal_value = future_value_with_inflation(current_goal_cost, inflation_rate, goal_years)
    goal_sip = calculate_sip(inflated_goal_value, goal_return, goal_years)
    goal_lumpsum = calculate_lumpsum_required(inflated_goal_value, goal_return, goal_years)
    total_sip_pitch = existing_sip + goal_sip + retirement_sip

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Future Goal Value", format_inr(inflated_goal_value))
    g2.metric("Goal SIP", format_inr(goal_sip))
    g3.metric("Lumpsum Today", format_inr(goal_lumpsum))
    g4.metric("Total SIP Pitch", format_inr(total_sip_pitch))

    years_list = list(range(1, goal_years + 1))
    projected_values = [future_value_with_inflation(current_goal_cost, inflation_rate, y) for y in years_list]
    goal_df = pd.DataFrame({"Year": years_list, "Projected Goal Value": projected_values})

    c1, c2 = st.columns(2)
    with c1:
        st.line_chart(goal_df.set_index("Year"), use_container_width=True)
    with c2:
        show_df = goal_df.copy()
        show_df["Projected Goal Value"] = show_df["Projected Goal Value"].apply(format_inr)
        st.dataframe(show_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 5 - RETIREMENT
# =========================================================
with tab5:
    st.markdown('<div class="section-title">ULTRA PRO V2 Retirement Proposal</div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Years to Retirement", f"{years_to_retirement} Years")
    r2.metric("Retirement Corpus", format_inr(ret_corpus))
    r3.metric("Expense at Retirement", format_inr(expense_at_retirement))
    r4.metric("Retirement SIP", format_inr(retirement_sip))

    ret_df = pd.DataFrame({
        "Metric": [
            "Current Total Assets",
            "Future Value of Existing Assets",
            "Additional Corpus Needed",
            "Retirement SIP Required"
        ],
        "Value": [
            format_inr(current_total_assets),
            format_inr(future_existing_assets),
            format_inr(additional_corpus_needed),
            format_inr(retirement_sip)
        ]
    })
    st.dataframe(ret_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 6 - PROTECTION
# =========================================================
with tab6:
    st.markdown('<div class="section-title">Protection + Cross-Sell Engine</div>', unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Life Cover Need", format_inr(recommended_life_cover))
    p2.metric("Life Cover Gap", format_inr(life_cover_gap))
    p3.metric("Health Cover Need", format_inr(recommended_health_cover))
    p4.metric("Health Cover Gap", format_inr(health_cover_gap))

    p5, p6 = st.columns(2)
    p5.metric("Emergency Fund Need", format_inr(recommended_emergency_fund))
    p6.metric("Cross-Sell Score", f"{cross_sell_score}/100")

    protection_df = pd.DataFrame({
        "Amount": [life_cover_gap, health_cover_gap, recommended_emergency_fund, liabilities]
    }, index=["Life Gap", "Health Gap", "Emergency Fund", "Liabilities"])
    st.bar_chart(protection_df, use_container_width=True)

# =========================================================
# TAB 7 - EMI + TAX
# =========================================================
with tab7:
    st.markdown('<div class="section-title">EMI + Tax Review</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        loan_amount = st.number_input("Loan Amount (₹)", min_value=10000, max_value=500000000, value=2500000, step=50000)
    with c2:
        loan_rate = st.slider("Loan Interest Rate (%)", 1, 20, 9)
    with c3:
        loan_years = st.slider("Loan Tenure (Years)", 1, 30, 10)

    emi, total_interest, total_payment = emi_calculator(loan_amount, loan_rate, loan_years)
    emi_to_income = safe_ratio(emi, monthly_income)

    e1, e2, e3 = st.columns(3)
    e1.metric("Monthly EMI", format_inr(emi))
    e2.metric("EMI / Income", f"{emi_to_income:.1f}%")
    e3.metric("Total Interest", format_inr(total_interest))

    st.markdown("---")

    t1, t2 = st.columns(2)
    with t1:
        tax_annual_income = st.number_input("Annual Gross Income (₹)", min_value=0, max_value=50000000, value=int(annual_income), step=50000)
    with t2:
        old_regime_deductions = st.number_input("Old Regime Deductions (₹)", min_value=0, max_value=5000000, value=150000, step=10000)

    old_taxable, old_tax = tax_regime_old(tax_annual_income, old_regime_deductions)
    new_taxable, new_tax = tax_regime_new(tax_annual_income)
    best_regime = "Old Regime" if old_tax < new_tax else "New Regime"

    tx1, tx2, tx3 = st.columns(3)
    tx1.metric("Old Regime Tax", format_inr(old_tax))
    tx2.metric("New Regime Tax", format_inr(new_tax))
    tx3.metric("Better Option", best_regime)

# =========================================================
# TAB 8 - RM LEADERBOARD
# =========================================================
with tab8:
    st.markdown('<div class="section-title">RM Leaderboard (Manual Entry)</div>', unsafe_allow_html=True)

    rm_df = pd.DataFrame({
        "RM Name": ["Parvez", "Aman", "Rohit", "Nisha", "Sara"],
        "SIP Achieved (₹)": [250000, 180000, 320000, 210000, 150000],
        "Clients Converted": [5, 3, 6, 4, 2],
        "Referrals": [4, 2, 5, 3, 1]
    })

    rm_df["Leaderboard Score"] = (
        rm_df["SIP Achieved (₹)"] / 10000
        + rm_df["Clients Converted"] * 10
        + rm_df["Referrals"] * 5
    ).round(1)

    rm_df = rm_df.sort_values("Leaderboard Score", ascending=False).reset_index(drop=True)
    rm_df.index = rm_df.index + 1

    st.dataframe(rm_df, use_container_width=True)

    st.download_button(
        "⬇️ Download RM Leaderboard CSV",
        data=rm_df.to_csv(index=False).encode("utf-8"),
        file_name="freedom_rm_leaderboard_v2.csv",
        mime="text/csv"
    )

# =========================================================
# TAB 9 - CSV UPLOAD
# =========================================================
with tab9:
    st.markdown('<div class="section-title">Bulk CSV Upload (Leads / Clients)</div>', unsafe_allow_html=True)

    upload_type = st.selectbox("Select Upload Type", ["Lead Master CSV", "Client Master CSV"])

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            st.success("CSV uploaded successfully.")
            st.dataframe(uploaded_df, use_container_width=True)

            if upload_type == "Lead Master CSV":
                if st.button("Append to Lead CRM"):
                    st.session_state.lead_db = pd.concat([st.session_state.lead_db, uploaded_df], ignore_index=True)
                    st.success("Uploaded data appended to Lead CRM.")
            else:
                if st.button("Append to Client CRM"):
                    st.session_state.client_db = pd.concat([st.session_state.client_db, uploaded_df], ignore_index=True)
                    st.success("Uploaded data appended to Client CRM.")

        except Exception as e:
            st.error(f"Error reading CSV: {e}")

# =========================================================
# TAB 10 - MIS REPORTS
# =========================================================
with tab10:
    st.markdown('<div class="section-title">MIS Reports + Download Center</div>', unsafe_allow_html=True)

    total_leads = len(st.session_state.lead_db)
    total_clients = len(st.session_state.client_db)
    hot_leads = len(st.session_state.lead_db[st.session_state.lead_db["Lead Temperature"] == "🔥 Hot Lead"])
    total_book_sip = st.session_state.client_db["Monthly SIP"].sum() if len(st.session_state.client_db) > 0 else 0
    total_book_networth = st.session_state.client_db["Net Worth"].sum() if len(st.session_state.client_db) > 0 else 0

    mis_df = pd.DataFrame({
        "Metric": [
            "Total Leads",
            "Hot Leads",
            "Total Clients",
            "Client Book SIP",
            "Client Book Net Worth"
        ],
        "Value": [
            total_leads,
            hot_leads,
            total_clients,
            total_book_sip,
            total_book_networth
        ]
    })

    display_mis_df = mis_df.copy()
    display_mis_df.loc[display_mis_df["Metric"] == "Client Book SIP", "Value"] = format_inr(total_book_sip)
    display_mis_df.loc[display_mis_df["Metric"] == "Client Book Net Worth", "Value"] = format_inr(total_book_networth)

    st.dataframe(display_mis_df, use_container_width=True, hide_index=True)

    combined_report = pd.concat([
        st.session_state.lead_db.assign(Record_Type="Lead"),
        st.session_state.client_db.assign(Record_Type="Client")
    ], ignore_index=True, sort=False)

    st.download_button(
        "⬇️ Download Combined MIS CSV",
        data=combined_report.to_csv(index=False).encode("utf-8"),
        file_name="freedom_combined_mis_v2.csv",
        mime="text/csv"
    )

    st.download_button(
        "⬇️ Download Lead CRM CSV",
        data=st.session_state.lead_db.to_csv(index=False).encode("utf-8"),
        file_name="freedom_lead_crm_v2.csv",
        mime="text/csv"
    )

    st.download_button(
        "⬇️ Download Client CRM CSV",
        data=st.session_state.client_db.to_csv(index=False).encode("utf-8"),
        file_name="freedom_client_crm_v2.csv",
        mime="text/csv"
    )

# =========================================================
# TAB 11 - FINAL SUMMARY
# =========================================================
with tab11:
    st.markdown('<div class="section-title">Final ULTRA PRO V2 Summary</div>', unsafe_allow_html=True)

    try:
        final_goal_name = goal_name
        final_goal_value = inflated_goal_value
        final_goal_sip = goal_sip
        final_goal_lumpsum = goal_lumpsum
        final_total_sip_pitch = total_sip_pitch
    except:
        final_goal_name = "Wealth Creation"
        final_goal_value = future_value_with_inflation(1000000, inflation_rate, 10)
        final_goal_sip = calculate_sip(final_goal_value, goal_return, 10)
        final_goal_lumpsum = calculate_lumpsum_required(final_goal_value, goal_return, 10)
        final_total_sip_pitch = existing_sip + final_goal_sip + retirement_sip

    final_summary_df = pd.DataFrame({
        "Field": [
            "Advisor / MFD", "RM", "Client Name", "City", "Client Segment",
            "Lead Score", "Lead Temperature", "Conversion Probability",
            "Monthly Income", "Monthly Expenses", "Monthly Surplus", "Net Worth",
            "Existing SIP", "Goal", "Goal SIP", "Retirement SIP",
            "Life Cover Gap", "Health Cover Gap", "Lead DB Count", "Client DB Count"
        ],
        "Value": [
            advisor_name, rm_name, client_name, city_name, client_segment,
            lead_score, lead_temperature, conversion_probability,
            format_inr(monthly_income), format_inr(monthly_expenses), format_inr(monthly_surplus), format_inr(net_worth),
            format_inr(existing_sip), final_goal_name, format_inr(final_goal_sip), format_inr(retirement_sip),
            format_inr(life_cover_gap), format_inr(health_cover_gap), len(st.session_state.lead_db), len(st.session_state.client_db)
        ]
    })

    st.dataframe(final_summary_df, use_container_width=True, hide_index=True)

    summary_text = f"""
FREEDOM ULTRA PRO V2 SUMMARY

BUSINESS
- Advisor / MFD: {advisor_name}
- RM: {rm_name}
- Branch: {branch_name}

CURRENT LEAD
- Meeting Type: {meeting_type}
- Lead Source: {lead_source}
- Lead Stage: {lead_stage}
- Follow-up Status: {follow_up_status}
- Lead Score: {lead_score}/100
- Lead Temperature: {lead_temperature}
- Conversion Probability: {conversion_probability}

CURRENT CLIENT
- Client Name: {client_name}
- Mobile: {mobile_no}
- City: {city_name}
- Age: {age}
- Retirement Age: {retirement_age}
- Dependents: {dependents}
- Risk Profile: {risk_profile}
- Client Segment: {client_segment}
- Derived Risk: {derived_risk_category}
- Risk Score: {risk_score}/100

FINANCIALS
- Monthly Income: {format_inr(monthly_income)}
- Monthly Expenses: {format_inr(monthly_expenses)}
- Monthly Surplus: {format_inr(monthly_surplus)}
- Savings Ratio: {savings_ratio:.1f}%
- Existing SIP: {format_inr(existing_sip)}
- Net Worth: {format_inr(net_worth)}

SIP PROPOSAL
- Goal: {final_goal_name}
- Future Goal Value: {format_inr(final_goal_value)}
- Goal SIP: {format_inr(final_goal_sip)}
- Goal Lumpsum: {format_inr(final_goal_lumpsum)}
- Retirement SIP: {format_inr(retirement_sip)}
- Total SIP Pitch: {format_inr(final_total_sip_pitch)}

RETIREMENT
- Retirement Corpus: {format_inr(ret_corpus)}
- Future Value of Existing Assets: {format_inr(future_existing_assets)}
- Additional Corpus Needed: {format_inr(additional_corpus_needed)}

PROTECTION
- Recommended Life Cover: {format_inr(recommended_life_cover)}
- Life Cover Gap: {format_inr(life_cover_gap)}
- Recommended Health Cover: {format_inr(recommended_health_cover)}
- Health Cover Gap: {format_inr(health_cover_gap)}
- Emergency Fund Need: {format_inr(recommended_emergency_fund)}

CRM DATABASE
- Total Leads in CRM: {len(st.session_state.lead_db)}
- Total Clients in CRM: {len(st.session_state.client_db)}

MIS
- Client Book SIP: {format_inr(st.session_state.client_db["Monthly SIP"].sum() if len(st.session_state.client_db) > 0 else 0)}
- Client Book Net Worth: {format_inr(st.session_state.client_db["Net Worth"].sum() if len(st.session_state.client_db) > 0 else 0)}
"""
    st.text_area("ULTRA PRO V2 Summary", summary_text, height=720)

    recommendations = []
    if lead_score >= 75:
        recommendations.append("High-priority lead. Push for conversion in current cycle.")
    elif lead_score >= 50:
        recommendations.append("Warm lead. Strong follow-up within 48 hours.")
    else:
        recommendations.append("Cold lead. Build trust and educate before aggressive closure.")

    recommendations.append(f"Client segment is {client_segment}. Use segment-based advisory pitch.")
    recommendations.append(f"Primary SIP opportunity around {format_inr(final_total_sip_pitch)}.")
    recommendations.append(f"Retirement SIP opportunity around {format_inr(retirement_sip)}.")
    if life_cover_gap > 0:
        recommendations.append(f"Life cover cross-sell opportunity: {format_inr(life_cover_gap)}.")
    if health_cover_gap > 0:
        recommendations.append(f"Health cover cross-sell opportunity: {format_inr(health_cover_gap)}.")
    recommendations.append("Use Lead CRM + Client CRM tabs daily for pipeline management.")
    recommendations.append("Download MIS reports weekly for business review.")

    st.markdown("### ✅ ULTRA PRO V2 Action Plan")
    for i, rec in enumerate(recommendations, start=1):
        st.write(f"{i}. {rec}")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    '<div class="footer-note">⚠️ Disclaimer: This tool is for business presentation, client engagement and planning support only. It is not investment advice, insurance advice, tax advice or a regulated recommendation. Final suitability must be based on full risk profiling, product suitability, disclosures, underwriting, taxation and applicable regulations.</div>',
    unsafe_allow_html=True
)
