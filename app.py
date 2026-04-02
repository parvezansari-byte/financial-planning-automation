import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Freedom ULTRA PRO",
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
# SESSION STATE
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================================================
# LOGIN SCREEN
# =========================================================
if not st.session_state.logged_in:
    st.markdown('<div class="main-title">🚀 Freedom ULTRA PRO</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Premium CRM + MFD Conversion + Client Master + RM Dashboard</div>', unsafe_allow_html=True)
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
st.markdown('<div class="main-title">🚀 Freedom ULTRA PRO</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Login • Lead Master • Client Segmentation • SIP Conversion • Retirement • Protection • RM Leaderboard • CSV Reports</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="brand-bar">Freedom Advisory ULTRA PRO Desk • Premium Business OS for MFD / Advisor Growth</div>',
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

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("🏢 Freedom ULTRA PRO Setup")

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

# CRM Scoring
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
    "🎯 ULTRA Dashboard",
    "📞 Lead Master",
    "📂 Client Master Upload",
    "👥 Client Segmentation",
    "📈 SIP Proposal",
    "🏖 Retirement",
    "🛡 Protection",
    "🏦 EMI + Tax",
    "🏆 RM Leaderboard",
    "🎯 Targets + Reports",
    "🧾 Final ULTRA Summary"
])

# =========================================================
# TAB 1 - DASHBOARD
# =========================================================
with tab1:
    st.markdown('<div class="section-title">ULTRA PRO Business Dashboard</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lead Temperature", lead_temperature)
    c2.metric("Conversion Probability", conversion_probability)
    c3.metric("Retirement SIP", format_inr(retirement_sip))
    c4.metric("Protection Gap", format_inr(life_cover_gap + health_cover_gap))

    dash_df = pd.DataFrame({
        "Score": [lead_score, sip_conversion_score, cross_sell_score, risk_score]
    }, index=["Lead", "SIP", "Cross-Sell", "Risk"])
    st.bar_chart(dash_df, use_container_width=True)

    overview_df = pd.DataFrame({
        "Metric": [
            "Monthly Income", "Monthly Expenses", "Monthly Surplus", "Existing SIP",
            "Net Worth", "Client Segment", "Risk Category"
        ],
        "Value": [
            format_inr(monthly_income), format_inr(monthly_expenses), format_inr(monthly_surplus),
            format_inr(existing_sip), format_inr(net_worth), client_segment, derived_risk_category
        ]
    })
    st.dataframe(overview_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 2 - LEAD MASTER
# =========================================================
with tab2:
    st.markdown('<div class="section-title">Lead Master Entry</div>', unsafe_allow_html=True)

    lead_master_df = pd.DataFrame({
        "Field": [
            "Advisor / MFD", "RM", "Meeting Type", "Lead Source", "Lead Stage",
            "Follow-up Status", "Days Since Last Meeting", "Client Name", "Mobile",
            "City", "Lead Score", "Lead Temperature", "Conversion Probability"
        ],
        "Value": [
            advisor_name, rm_name, meeting_type, lead_source, lead_stage,
            follow_up_status, days_since_last_meeting, client_name, mobile_no,
            city_name, lead_score, lead_temperature, conversion_probability
        ]
    })

    st.dataframe(lead_master_df, use_container_width=True, hide_index=True)

    lead_csv = lead_master_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Lead Master CSV",
        data=lead_csv,
        file_name="freedom_lead_master.csv",
        mime="text/csv"
    )

# =========================================================
# TAB 3 - CLIENT MASTER UPLOAD
# =========================================================
with tab3:
    st.markdown('<div class="section-title">Client Master CSV Upload</div>', unsafe_allow_html=True)
    st.info("Upload a CSV file of your client master. Example columns: Client Name, Mobile, City, SIP, Income, Segment")

    uploaded_file = st.file_uploader("Upload Client Master CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            st.success("CSV uploaded successfully.")
            st.dataframe(uploaded_df, use_container_width=True)

            st.download_button(
                "⬇️ Download Uploaded CSV Copy",
                data=uploaded_df.to_csv(index=False).encode("utf-8"),
                file_name="uploaded_client_master_copy.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    else:
        sample_df = pd.DataFrame({
            "Client Name": ["Client A", "Client B", "Client C"],
            "Mobile": ["9999999991", "9999999992", "9999999993"],
            "City": ["Bengaluru", "Mumbai", "Delhi"],
            "SIP": [5000, 12000, 25000],
            "Income": [80000, 150000, 350000],
            "Segment": ["Emerging", "Growth", "Premium"]
        })
        st.dataframe(sample_df, use_container_width=True)

# =========================================================
# TAB 4 - CLIENT SEGMENTATION
# =========================================================
with tab4:
    st.markdown('<div class="section-title">Client Segmentation Engine</div>', unsafe_allow_html=True)

    seg1, seg2, seg3, seg4 = st.columns(4)
    seg1.metric("Client Segment", client_segment)
    seg2.metric("Risk Category", derived_risk_category)
    seg3.metric("SIP Score", f"{sip_conversion_score}/100")
    seg4.metric("Cross-Sell Score", f"{cross_sell_score}/100")

    segment_strategy = {
        "Premium": "Focus on wealth creation, retirement, PMS-style positioning (without mis-selling), family office feel, and premium retention.",
        "Growth": "Focus on SIP scale-up, goal planning, retirement buckets, tax optimization discussion and protection review.",
        "Emerging": "Focus on disciplined SIP start, emergency fund, term + health gap, and referral-based trust building.",
        "Starter": "Focus on budgeting, emergency reserve, small SIP start and long-term habit creation."
    }

    segment_df = pd.DataFrame({
        "Area": [
            "Client Segment",
            "Suggested Strategy",
            "Investor Style",
            "Suggested Allocation"
        ],
        "Value": [
            client_segment,
            segment_strategy.get(client_segment, "Goal-based planning"),
            derived_risk_category,
            f"Equity {suggested_allocation['Equity']}% | Debt {suggested_allocation['Debt']}% | Gold {suggested_allocation['Gold']}% | Cash {suggested_allocation['Cash']}%"
        ]
    })
    st.dataframe(segment_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 5 - SIP PROPOSAL
# =========================================================
with tab5:
    st.markdown('<div class="section-title">ULTRA PRO SIP Proposal</div>', unsafe_allow_html=True)

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
# TAB 6 - RETIREMENT
# =========================================================
with tab6:
    st.markdown('<div class="section-title">ULTRA PRO Retirement Proposal</div>', unsafe_allow_html=True)

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
# TAB 7 - PROTECTION
# =========================================================
with tab7:
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
# TAB 8 - EMI + TAX
# =========================================================
with tab8:
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
# TAB 9 - RM LEADERBOARD
# =========================================================
with tab9:
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
        file_name="freedom_rm_leaderboard.csv",
        mime="text/csv"
    )

# =========================================================
# TAB 10 - TARGETS + REPORTS
# =========================================================
with tab10:
    st.markdown('<div class="section-title">Monthly Targets + Reports</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        monthly_sip_target = st.number_input("Monthly SIP Target (₹)", min_value=10000, max_value=10000000, value=500000, step=10000)
    with c2:
        monthly_sip_achieved = st.number_input("SIP Achieved This Month (₹)", min_value=0, max_value=10000000, value=150000, step=10000)
    with c3:
        clients_converted = st.number_input("Clients Converted This Month", min_value=0, max_value=1000, value=3, step=1)

    achievement_pct = safe_ratio(monthly_sip_achieved, monthly_sip_target)
    target_balance = max(monthly_sip_target - monthly_sip_achieved, 0)

    t1, t2, t3 = st.columns(3)
    t1.metric("Target", format_inr(monthly_sip_target))
    t2.metric("Achieved", format_inr(monthly_sip_achieved))
    t3.metric("Achievement %", f"{achievement_pct:.1f}%")

    target_df = pd.DataFrame({
        "Metric": ["Monthly SIP Target", "Monthly SIP Achieved", "Balance", "Clients Converted"],
        "Value": [monthly_sip_target, monthly_sip_achieved, target_balance, clients_converted]
    })
    st.dataframe(target_df, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download Monthly Target Report CSV",
        data=target_df.to_csv(index=False).encode("utf-8"),
        file_name="freedom_monthly_target_report.csv",
        mime="text/csv"
    )

# =========================================================
# TAB 11 - FINAL SUMMARY
# =========================================================
with tab11:
    st.markdown('<div class="section-title">Final ULTRA PRO Summary</div>', unsafe_allow_html=True)

    # Safe defaults if SIP tab not touched
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

    allocation_df = pd.DataFrame({
        "Asset Class": list(suggested_allocation.keys()),
        "Suggested Allocation (%)": list(suggested_allocation.values())
    })
    st.dataframe(allocation_df, use_container_width=True, hide_index=True)

    final_summary_df = pd.DataFrame({
        "Field": [
            "Advisor / MFD", "RM", "Client Name", "City", "Client Segment",
            "Lead Score", "Lead Temperature", "Conversion Probability",
            "Monthly Income", "Monthly Expenses", "Monthly Surplus", "Net Worth",
            "Existing SIP", "Goal", "Goal SIP", "Retirement SIP",
            "Life Cover Gap", "Health Cover Gap", "Monthly SIP Target", "Monthly SIP Achieved"
        ],
        "Value": [
            advisor_name, rm_name, client_name, city_name, client_segment,
            lead_score, lead_temperature, conversion_probability,
            format_inr(monthly_income), format_inr(monthly_expenses), format_inr(monthly_surplus), format_inr(net_worth),
            format_inr(existing_sip), final_goal_name, format_inr(final_goal_sip), format_inr(retirement_sip),
            format_inr(life_cover_gap), format_inr(health_cover_gap), format_inr(monthly_sip_target), format_inr(monthly_sip_achieved)
        ]
    })

    st.dataframe(final_summary_df, use_container_width=True, hide_index=True)

    summary_text = f"""
FREEDOM ULTRA PRO SUMMARY

BUSINESS
- Advisor / MFD: {advisor_name}
- RM: {rm_name}
- Branch: {branch_name}

LEAD
- Meeting Type: {meeting_type}
- Lead Source: {lead_source}
- Lead Stage: {lead_stage}
- Follow-up Status: {follow_up_status}
- Lead Score: {lead_score}/100
- Lead Temperature: {lead_temperature}
- Conversion Probability: {conversion_probability}

CLIENT
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

TARGETS
- Monthly SIP Target: {format_inr(monthly_sip_target)}
- Monthly SIP Achieved: {format_inr(monthly_sip_achieved)}
- Achievement %: {achievement_pct:.1f}%
- Clients Converted: {clients_converted}
"""
    st.text_area("ULTRA PRO Summary", summary_text, height=700)

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
    recommendations.append("Use CSV downloads for lead master, target report and RM review.")

    st.markdown("### ✅ ULTRA PRO Action Plan")
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
