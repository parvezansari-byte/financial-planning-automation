import streamlit as st
import pandas as pd
from datetime import datetime
import os

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Freedom ULTRA PRO V4",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# FILE PATHS
# =========================================================
LEADS_FILE = "leads.csv"
CLIENTS_FILE = "clients.csv"

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
    max-width: 1550px;
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
.stAlert {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# COLUMN DEFINITIONS
# =========================================================
LEAD_COLUMNS = [
    "Lead ID", "Date", "Client Name", "Mobile", "City", "Lead Source",
    "Lead Stage", "Follow-up Status", "Monthly Income", "Monthly Surplus",
    "Days Since Last Meeting", "Lead Score", "Lead Temperature", "Referral Count"
]

CLIENT_COLUMNS = [
    "Client ID", "Date", "Client Name", "Mobile", "City", "Segment",
    "Risk Category", "Monthly SIP", "Net Worth", "Referred By Lead ID"
]

# =========================================================
# HELPERS - NUMERIC SAFETY
# =========================================================
def to_number(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except:
        return default

def to_int(value, default=0):
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except:
        return default

def format_inr(value):
    return f"₹{to_number(value):,.0f}"

def safe_ratio(a, b):
    b_val = to_number(b)
    if b_val == 0:
        return 0.0
    return (to_number(a) / b_val) * 100

# =========================================================
# HELPERS - FILE SYSTEM
# =========================================================
def create_default_files():
    if not os.path.exists(LEADS_FILE):
        default_leads = pd.DataFrame([
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
                "Days Since Last Meeting": 2,
                "Lead Score": 78,
                "Lead Temperature": "🔥 Hot Lead",
                "Referral Count": 2
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
                "Days Since Last Meeting": 8,
                "Lead Score": 46,
                "Lead Temperature": "🔵 Cold Lead",
                "Referral Count": 0
            }
        ], columns=LEAD_COLUMNS)
        default_leads.to_csv(LEADS_FILE, index=False)

    if not os.path.exists(CLIENTS_FILE):
        default_clients = pd.DataFrame([
            {
                "Client ID": "C001",
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Client Name": "Sneha Patel",
                "Mobile": "9999999993",
                "City": "Delhi",
                "Segment": "Growth",
                "Risk Category": "Balanced",
                "Monthly SIP": 12000,
                "Net Worth": 2800000,
                "Referred By Lead ID": ""
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
                "Net Worth": 12500000,
                "Referred By Lead ID": "L001"
            }
        ], columns=CLIENT_COLUMNS)
        default_clients.to_csv(CLIENTS_FILE, index=False)

def normalize_leads(df):
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=LEAD_COLUMNS)
    temp = df.copy()
    for col in LEAD_COLUMNS:
        if col not in temp.columns:
            if col in ["Monthly Income", "Monthly Surplus", "Days Since Last Meeting", "Lead Score", "Referral Count"]:
                temp[col] = 0
            else:
                temp[col] = ""
    temp = temp[LEAD_COLUMNS]

    # numeric cleanup
    for col in ["Monthly Income", "Monthly Surplus", "Days Since Last Meeting", "Lead Score", "Referral Count"]:
        temp[col] = pd.to_numeric(temp[col], errors="coerce").fillna(0)

    # text cleanup
    for col in ["Lead ID", "Date", "Client Name", "Mobile", "City", "Lead Source", "Lead Stage", "Follow-up Status", "Lead Temperature"]:
        temp[col] = temp[col].astype(str).fillna("")

    return temp

def normalize_clients(df):
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=CLIENT_COLUMNS)
    temp = df.copy()
    for col in CLIENT_COLUMNS:
        if col not in temp.columns:
            if col in ["Monthly SIP", "Net Worth"]:
                temp[col] = 0
            else:
                temp[col] = ""
    temp = temp[CLIENT_COLUMNS]

    for col in ["Monthly SIP", "Net Worth"]:
        temp[col] = pd.to_numeric(temp[col], errors="coerce").fillna(0)

    for col in ["Client ID", "Date", "Client Name", "Mobile", "City", "Segment", "Risk Category", "Referred By Lead ID"]:
        temp[col] = temp[col].astype(str).fillna("")

    return temp

def load_leads():
    try:
        if os.path.exists(LEADS_FILE):
            return normalize_leads(pd.read_csv(LEADS_FILE))
        return pd.DataFrame(columns=LEAD_COLUMNS)
    except:
        return pd.DataFrame(columns=LEAD_COLUMNS)

def load_clients():
    try:
        if os.path.exists(CLIENTS_FILE):
            return normalize_clients(pd.read_csv(CLIENTS_FILE))
        return pd.DataFrame(columns=CLIENT_COLUMNS)
    except:
        return pd.DataFrame(columns=CLIENT_COLUMNS)

def save_leads(df):
    normalize_leads(df).to_csv(LEADS_FILE, index=False)

def save_clients(df):
    normalize_clients(df).to_csv(CLIENTS_FILE, index=False)

# =========================================================
# HELPERS - BUSINESS LOGIC
# =========================================================
def future_value_with_inflation(current_value, inflation, years):
    return to_number(current_value) * ((1 + to_number(inflation) / 100) ** to_number(years))

def calculate_sip(future_value, annual_return, years):
    n = int(to_number(years) * 12)
    r = to_number(annual_return) / 100 / 12
    if n <= 0:
        return 0.0
    if r == 0:
        return to_number(future_value) / n
    denominator = ((1 + r) ** n - 1)
    if denominator == 0:
        return 0.0
    return max(to_number(future_value) * r / denominator, 0.0)

def calculate_lumpsum_required(future_value, annual_return, years):
    years = to_number(years)
    if years <= 0:
        return to_number(future_value)
    return to_number(future_value) / ((1 + to_number(annual_return) / 100) ** years)

def retirement_corpus_needed(monthly_expense_today, inflation, years_to_retire, years_post_retirement, post_ret_return):
    monthly_expense_at_retirement = to_number(monthly_expense_today) * ((1 + to_number(inflation) / 100) ** to_number(years_to_retire))
    annual_expense_at_retirement = monthly_expense_at_retirement * 12
    real_return = ((1 + to_number(post_ret_return) / 100) / (1 + to_number(inflation) / 100)) - 1

    if real_return <= 0:
        corpus = annual_expense_at_retirement * to_number(years_post_retirement)
    else:
        corpus = annual_expense_at_retirement * ((1 - (1 + real_return) ** (-to_number(years_post_retirement))) / real_return)

    return max(corpus, 0.0), max(monthly_expense_at_retirement, 0.0)

def calculate_life_cover(monthly_expense, years_support, liabilities_amt, existing_assets, annual_income):
    family_expense_need = to_number(monthly_expense) * 12 * to_number(years_support)
    income_replacement = to_number(annual_income) * 10
    cover = family_expense_need + to_number(liabilities_amt) + income_replacement - to_number(existing_assets)
    return max(cover, 0.0)

def emi_calculator(principal, annual_rate, years):
    n = int(to_number(years) * 12)
    r = to_number(annual_rate) / 100 / 12
    principal = to_number(principal)
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
    taxable = max(to_number(annual_income) - to_number(deductions), 0)
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
    taxable = max(to_number(annual_income), 0)
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
    age = to_int(age)
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
    score = to_number(score)
    if score >= 75:
        return "🔥 Hot Lead"
    elif score >= 50:
        return "🟡 Warm Lead"
    return "🔵 Cold Lead"

def get_conversion_probability(score):
    score = to_number(score)
    if score >= 85:
        return "Very High"
    elif score >= 70:
        return "High"
    elif score >= 50:
        return "Medium"
    return "Low"

def get_client_segment(monthly_income, monthly_surplus, net_worth):
    monthly_income = to_number(monthly_income)
    monthly_surplus = to_number(monthly_surplus)
    net_worth = to_number(net_worth)

    if monthly_income >= 300000 or net_worth >= 10000000:
        return "Premium"
    elif monthly_income >= 100000 or net_worth >= 2500000:
        return "Growth"
    elif monthly_surplus > 0:
        return "Emerging"
    return "Starter"

def calculate_lead_score(lead_source, lead_stage, follow_up_status, monthly_surplus, days_since_last_meeting=3):
    score = 0
    score += {"Referral": 25, "Existing Client": 20, "Corporate Reference": 18, "Walk-in": 12, "Digital": 10, "Other": 8}.get(lead_source, 8)
    score += {"Prospect": 10, "Qualified": 25, "Proposal Shared": 45, "Negotiation": 65, "Converted": 100}.get(lead_stage, 0)
    score += {"Completed": 10, "Today": 8, "This Week": 5, "Pending": 2}.get(follow_up_status, 2)

    d = to_int(days_since_last_meeting)
    if d <= 3:
        score += 10
    elif d <= 7:
        score += 7
    elif d <= 15:
        score += 4
    else:
        score += 1

    ms = to_number(monthly_surplus)
    if ms >= 30000:
        score += 20
    elif ms >= 15000:
        score += 14
    elif ms > 0:
        score += 8
    else:
        score += 2

    return max(min(score, 100), 0)

def next_lead_id(leads_df):
    if len(leads_df) == 0:
        return "L001"
    try:
        ids = leads_df["Lead ID"].astype(str).str.replace("L", "", regex=False)
        nums = pd.to_numeric(ids, errors="coerce").fillna(0)
        return f"L{str(int(nums.max()) + 1).zfill(3)}"
    except:
        return f"L{str(len(leads_df) + 1).zfill(3)}"

def next_client_id(clients_df):
    if len(clients_df) == 0:
        return "C001"
    try:
        ids = clients_df["Client ID"].astype(str).str.replace("C", "", regex=False)
        nums = pd.to_numeric(ids, errors="coerce").fillna(0)
        return f"C{str(int(nums.max()) + 1).zfill(3)}"
    except:
        return f"C{str(len(clients_df) + 1).zfill(3)}"

# =========================================================
# INIT FILES + SESSION
# =========================================================
create_default_files()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "lead_db" not in st.session_state:
    st.session_state.lead_db = load_leads()

if "client_db" not in st.session_state:
    st.session_state.client_db = load_clients()

# =========================================================
# LOGIN CREDENTIALS (SECRETS SAFE)
# =========================================================
APP_USERNAME = st.secrets.get("APP_USERNAME", "admin")
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "freedom123")

# =========================================================
# LOGIN SCREEN
# =========================================================
if not st.session_state.logged_in:
    st.markdown('<div class="main-title">🚀 Freedom ULTRA PRO V4</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Secrets-safe Login • TRUE CSV DB • Edit • Convert Lead → Client • Follow-up Engine • Referral Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-bar">Login to access your premium advisory workspace</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown("### 🔐 Advisor Login")
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="freedom123")
        if st.button("Login"):
            if username == APP_USERNAME and password == APP_PASSWORD:
                st.session_state.logged_in = True
                st.success("Login successful. Please continue.")
                st.rerun()
            else:
                st.error("Invalid username or password.")

        if "APP_USERNAME" in st.secrets and "APP_PASSWORD" in st.secrets:
            st.info("Secure login active via Streamlit Secrets.")
        else:
            st.info("Demo login active: admin / freedom123")
    st.stop()

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">🚀 Freedom ULTRA PRO V4</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Secrets-safe Login • TRUE CSV Database • Edit • Convert Lead → Client • Referral Tracker • Follow-up Engine</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="brand-bar">Freedom Advisory ULTRA PRO V4 • Production-Style MFD / Advisor Business Operating System</div>',
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("🏢 Freedom ULTRA PRO V4 Setup")

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

lead_score = calculate_lead_score(
    lead_source=lead_source,
    lead_stage=lead_stage,
    follow_up_status=follow_up_status,
    monthly_surplus=monthly_surplus,
    days_since_last_meeting=days_since_last_meeting
)
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "🎯 Dashboard",
    "📞 Lead CRM V4",
    "👥 Client CRM V4",
    "📈 SIP Proposal",
    "🏖 Retirement",
    "🛡 Protection",
    "🏦 EMI + Tax",
    "🏆 RM Leaderboard",
    "📂 CSV Upload",
    "📊 MIS Reports",
    "🧾 Final Summary",
    "⚙️ Admin Tools"
])

# =========================================================
# TAB 1 - DASHBOARD
# =========================================================
with tab1:
    st.markdown('<div class="section-title">ULTRA PRO V4 Business Dashboard</div>', unsafe_allow_html=True)

    lead_db = normalize_leads(st.session_state.lead_db)
    client_db = normalize_clients(st.session_state.client_db)

    total_leads = len(lead_db)
    total_clients = len(client_db)
    hot_leads = len(lead_db[lead_db["Lead Temperature"] == "🔥 Hot Lead"]) if total_leads > 0 else 0
    due_today = len(lead_db[lead_db["Follow-up Status"] == "Today"]) if total_leads > 0 else 0
    total_client_sip = pd.to_numeric(client_db["Monthly SIP"], errors="coerce").fillna(0).sum() if total_clients > 0 else 0
    total_referrals = pd.to_numeric(lead_db["Referral Count"], errors="coerce").fillna(0).sum() if total_leads > 0 else 0

    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("Total Leads", total_leads)
    d2.metric("Total Clients", total_clients)
    d3.metric("Hot Leads", hot_leads)
    d4.metric("Follow-up Today", due_today)
    d5.metric("Referral Count", to_int(total_referrals))

    d6, d7 = st.columns(2)
    d6.metric("Client Book SIP", format_inr(total_client_sip))
    d7.metric("Conversion Rate", f"{safe_ratio(total_clients, total_leads):.1f}%")

    dash_df = pd.DataFrame({
        "Score": [lead_score, sip_conversion_score, cross_sell_score, risk_score]
    }, index=["Lead", "SIP", "Cross-Sell", "Risk"])
    st.bar_chart(dash_df, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        if total_leads > 0:
            pipeline_summary = lead_db.groupby("Lead Stage").size().reset_index(name="Count")
            st.markdown("### 📌 Lead Pipeline Summary")
            st.dataframe(pipeline_summary, use_container_width=True, hide_index=True)

    with c2:
        if total_leads > 0:
            due_today_df = lead_db[lead_db["Follow-up Status"] == "Today"][["Lead ID", "Client Name", "Mobile", "City", "Lead Stage"]]
            st.markdown("### ⏰ Follow-up Due Today")
            if len(due_today_df) > 0:
                st.dataframe(due_today_df, use_container_width=True, hide_index=True)
            else:
                st.info("No follow-up due today.")

# =========================================================
# TAB 2 - LEAD CRM V4
# =========================================================
with tab2:
    st.markdown('<div class="section-title">Lead CRM V4 (Add • Edit • Convert • Delete)</div>', unsafe_allow_html=True)

    # Refresh local references
    st.session_state.lead_db = normalize_leads(st.session_state.lead_db)
    st.session_state.client_db = normalize_clients(st.session_state.client_db)

    # ---------------- ADD LEAD ----------------
    st.markdown("### ➕ Add New Lead")
    l1, l2, l3, l4 = st.columns(4)
    with l1:
        new_lead_name = st.text_input("Lead Name", key="new_lead_name_v4")
    with l2:
        new_lead_mobile = st.text_input("Lead Mobile", key="new_lead_mobile_v4")
    with l3:
        new_lead_city = st.text_input("Lead City", key="new_lead_city_v4", value="Bengaluru")
    with l4:
        new_lead_source = st.selectbox("Lead Source", ["Referral", "Walk-in", "Existing Client", "Digital", "Corporate Reference", "Other"], key="new_lead_source_v4")

    l5, l6, l7, l8, l9, l10 = st.columns(6)
    with l5:
        new_lead_stage = st.selectbox("Lead Stage", ["Prospect", "Qualified", "Proposal Shared", "Negotiation", "Converted"], key="new_lead_stage_v4")
    with l6:
        new_followup = st.selectbox("Follow-up Status", ["Pending", "Today", "This Week", "Completed"], key="new_followup_v4")
    with l7:
        new_income = st.number_input("Monthly Income (₹)", min_value=0, max_value=5000000, value=50000, step=5000, key="new_income_v4")
    with l8:
        new_surplus = st.number_input("Monthly Surplus (₹)", min_value=-500000, max_value=5000000, value=10000, step=5000, key="new_surplus_v4")
    with l9:
        new_days = st.number_input("Days Since Last Meeting", min_value=0, max_value=365, value=3, step=1, key="new_days_v4")
    with l10:
        new_referrals = st.number_input("Referral Count", min_value=0, max_value=1000, value=0, step=1, key="new_referrals_v4")

    if st.button("Add Lead to CSV Database"):
        temp_score = calculate_lead_score(
            lead_source=new_lead_source,
            lead_stage=new_lead_stage,
            follow_up_status=new_followup,
            monthly_surplus=new_surplus,
            days_since_last_meeting=new_days
        )

        new_row = pd.DataFrame([{
            "Lead ID": next_lead_id(st.session_state.lead_db),
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Client Name": new_lead_name if new_lead_name else "Unnamed Lead",
            "Mobile": new_lead_mobile if new_lead_mobile else "",
            "City": new_lead_city,
            "Lead Source": new_lead_source,
            "Lead Stage": new_lead_stage,
            "Follow-up Status": new_followup,
            "Monthly Income": new_income,
            "Monthly Surplus": new_surplus,
            "Days Since Last Meeting": new_days,
            "Lead Score": temp_score,
            "Lead Temperature": get_lead_temperature(temp_score),
            "Referral Count": new_referrals
        }], columns=LEAD_COLUMNS)

        st.session_state.lead_db = pd.concat([st.session_state.lead_db, new_row], ignore_index=True)
        st.session_state.lead_db = normalize_leads(st.session_state.lead_db)
        save_leads(st.session_state.lead_db)
        st.success("Lead added and saved to leads.csv successfully.")

    st.markdown("---")

    # ---------------- SEARCH / FILTER ----------------
    st.markdown("### 🔎 Search / Filter Leads")
    s1, s2, s3 = st.columns(3)
    with s1:
        lead_search = st.text_input("Search by Name / Mobile / City", key="lead_search_v4")
    with s2:
        stage_filter = st.selectbox("Filter by Lead Stage", ["All", "Prospect", "Qualified", "Proposal Shared", "Negotiation", "Converted"], key="stage_filter_v4")
    with s3:
        follow_filter = st.selectbox("Filter by Follow-up", ["All", "Pending", "Today", "This Week", "Completed"], key="follow_filter_v4")

    lead_view = st.session_state.lead_db.copy()

    if lead_search:
        search_lower = lead_search.lower()
        lead_view = lead_view[
            lead_view["Client Name"].astype(str).str.lower().str.contains(search_lower, na=False) |
            lead_view["Mobile"].astype(str).str.lower().str.contains(search_lower, na=False) |
            lead_view["City"].astype(str).str.lower().str.contains(search_lower, na=False)
        ]

    if stage_filter != "All":
        lead_view = lead_view[lead_view["Lead Stage"].astype(str) == stage_filter]

    if follow_filter != "All":
        lead_view = lead_view[lead_view["Follow-up Status"].astype(str) == follow_filter]

    st.dataframe(lead_view, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download Leads CSV",
        data=st.session_state.lead_db.to_csv(index=False).encode("utf-8"),
        file_name="freedom_leads_v4.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # ---------------- EDIT LEAD ----------------
    st.markdown("### ✏️ Edit Lead")
    if len(st.session_state.lead_db) > 0:
        edit_lead_id = st.selectbox("Select Lead ID to Edit", st.session_state.lead_db["Lead ID"].astype(str).tolist(), key="edit_lead_id_v4")
        edit_lead_row = st.session_state.lead_db[st.session_state.lead_db["Lead ID"].astype(str) == str(edit_lead_id)].iloc[0]

        e1, e2, e3, e4 = st.columns(4)
        with e1:
            edit_name = st.text_input("Edit Name", value=str(edit_lead_row["Client Name"]), key="edit_name_v4")
        with e2:
            edit_mobile = st.text_input("Edit Mobile", value=str(edit_lead_row["Mobile"]), key="edit_mobile_v4")
        with e3:
            edit_city = st.text_input("Edit City", value=str(edit_lead_row["City"]), key="edit_city_v4")
        with e4:
            edit_source = st.selectbox("Edit Source", ["Referral", "Walk-in", "Existing Client", "Digital", "Corporate Reference", "Other"],
                                       index=["Referral", "Walk-in", "Existing Client", "Digital", "Corporate Reference", "Other"].index(str(edit_lead_row["Lead Source"])) if str(edit_lead_row["Lead Source"]) in ["Referral", "Walk-in", "Existing Client", "Digital", "Corporate Reference", "Other"] else 0,
                                       key="edit_source_v4")

        e5, e6, e7, e8, e9, e10 = st.columns(6)
        with e5:
            edit_stage = st.selectbox("Edit Stage", ["Prospect", "Qualified", "Proposal Shared", "Negotiation", "Converted"],
                                      index=["Prospect", "Qualified", "Proposal Shared", "Negotiation", "Converted"].index(str(edit_lead_row["Lead Stage"])) if str(edit_lead_row["Lead Stage"]) in ["Prospect", "Qualified", "Proposal Shared", "Negotiation", "Converted"] else 0,
                                      key="edit_stage_v4")
        with e6:
            edit_follow = st.selectbox("Edit Follow-up", ["Pending", "Today", "This Week", "Completed"],
                                       index=["Pending", "Today", "This Week", "Completed"].index(str(edit_lead_row["Follow-up Status"])) if str(edit_lead_row["Follow-up Status"]) in ["Pending", "Today", "This Week", "Completed"] else 0,
                                       key="edit_follow_v4")
        with e7:
            edit_income = st.number_input("Edit Income", min_value=0, max_value=5000000, value=to_int(edit_lead_row["Monthly Income"]), step=5000, key="edit_income_v4")
        with e8:
            edit_surplus = st.number_input("Edit Surplus", min_value=-500000, max_value=5000000, value=to_int(edit_lead_row["Monthly Surplus"]), step=5000, key="edit_surplus_v4")
        with e9:
            edit_days = st.number_input("Edit Days", min_value=0, max_value=365, value=to_int(edit_lead_row["Days Since Last Meeting"]), step=1, key="edit_days_v4")
        with e10:
            edit_referrals = st.number_input("Edit Referral Count", min_value=0, max_value=1000, value=to_int(edit_lead_row["Referral Count"]), step=1, key="edit_referrals_v4")

        if st.button("Update Lead in CSV Database"):
            new_score = calculate_lead_score(edit_source, edit_stage, edit_follow, edit_surplus, edit_days)
            idx = st.session_state.lead_db.index[st.session_state.lead_db["Lead ID"].astype(str) == str(edit_lead_id)][0]

            st.session_state.lead_db.at[idx, "Client Name"] = edit_name
            st.session_state.lead_db.at[idx, "Mobile"] = edit_mobile
            st.session_state.lead_db.at[idx, "City"] = edit_city
            st.session_state.lead_db.at[idx, "Lead Source"] = edit_source
            st.session_state.lead_db.at[idx, "Lead Stage"] = edit_stage
            st.session_state.lead_db.at[idx, "Follow-up Status"] = edit_follow
            st.session_state.lead_db.at[idx, "Monthly Income"] = edit_income
            st.session_state.lead_db.at[idx, "Monthly Surplus"] = edit_surplus
            st.session_state.lead_db.at[idx, "Days Since Last Meeting"] = edit_days
            st.session_state.lead_db.at[idx, "Lead Score"] = new_score
            st.session_state.lead_db.at[idx, "Lead Temperature"] = get_lead_temperature(new_score)
            st.session_state.lead_db.at[idx, "Referral Count"] = edit_referrals

            st.session_state.lead_db = normalize_leads(st.session_state.lead_db)
            save_leads(st.session_state.lead_db)
            st.success(f"Lead {edit_lead_id} updated successfully.")
    else:
        st.info("No leads available to edit.")

    st.markdown("---")

    # ---------------- CONVERT LEAD TO CLIENT ----------------
    st.markdown("### 🔁 Convert Lead → Client")
    if len(st.session_state.lead_db) > 0:
        convertible_ids = st.session_state.lead_db["Lead ID"].astype(str).tolist()
        convert_lead_id = st.selectbox("Select Lead ID to Convert", convertible_ids, key="convert_lead_id_v4")

        lead_row = st.session_state.lead_db[st.session_state.lead_db["Lead ID"].astype(str) == str(convert_lead_id)].iloc[0]

        cv1, cv2, cv3, cv4 = st.columns(4)
        with cv1:
            convert_sip = st.number_input("Converted Monthly SIP (₹)", min_value=0, max_value=5000000, value=5000, step=500, key="convert_sip_v4")
        with cv2:
            convert_networth = st.number_input("Converted Net Worth (₹)", min_value=0, max_value=500000000, value=1000000, step=50000, key="convert_networth_v4")
        with cv3:
            convert_risk = st.selectbox("Risk Category", ["Conservative", "Balanced", "Aggressive"], key="convert_risk_v4")
        with cv4:
            auto_mark_converted = st.checkbox("Auto mark lead as Converted", value=True, key="auto_mark_converted_v4")

        if st.button("Convert Lead to Client"):
            lead_income = to_number(lead_row["Monthly Income"])
            lead_surplus = to_number(lead_row["Monthly Surplus"])
            temp_segment = get_client_segment(lead_income, lead_surplus, convert_networth)

            new_client_row = pd.DataFrame([{
                "Client ID": next_client_id(st.session_state.client_db),
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Client Name": str(lead_row["Client Name"]),
                "Mobile": str(lead_row["Mobile"]),
                "City": str(lead_row["City"]),
                "Segment": temp_segment,
                "Risk Category": convert_risk,
                "Monthly SIP": convert_sip,
                "Net Worth": convert_networth,
                "Referred By Lead ID": str(convert_lead_id)
            }], columns=CLIENT_COLUMNS)

            st.session_state.client_db = pd.concat([st.session_state.client_db, new_client_row], ignore_index=True)
            st.session_state.client_db = normalize_clients(st.session_state.client_db)
            save_clients(st.session_state.client_db)

            if auto_mark_converted:
                idx = st.session_state.lead_db.index[st.session_state.lead_db["Lead ID"].astype(str) == str(convert_lead_id)][0]
                st.session_state.lead_db.at[idx, "Lead Stage"] = "Converted"
                st.session_state.lead_db.at[idx, "Follow-up Status"] = "Completed"
                new_score = calculate_lead_score(
                    st.session_state.lead_db.at[idx, "Lead Source"],
                    "Converted",
                    "Completed",
                    st.session_state.lead_db.at[idx, "Monthly Surplus"],
                    st.session_state.lead_db.at[idx, "Days Since Last Meeting"]
                )
                st.session_state.lead_db.at[idx, "Lead Score"] = new_score
                st.session_state.lead_db.at[idx, "Lead Temperature"] = get_lead_temperature(new_score)
                st.session_state.lead_db = normalize_leads(st.session_state.lead_db)
                save_leads(st.session_state.lead_db)

            st.success(f"Lead {convert_lead_id} converted to client successfully.")
    else:
        st.info("No leads available for conversion.")

    st.markdown("---")

    # ---------------- DELETE LEAD ----------------
    st.markdown("### 🗑 Delete Lead")
    if len(st.session_state.lead_db) > 0:
        delete_lead_id = st.selectbox("Select Lead ID to Delete", st.session_state.lead_db["Lead ID"].astype(str).tolist(), key="delete_lead_id_v4")
        if st.button("Delete Selected Lead from CSV Database"):
            st.session_state.lead_db = st.session_state.lead_db[st.session_state.lead_db["Lead ID"].astype(str) != str(delete_lead_id)].reset_index(drop=True)
            st.session_state.lead_db = normalize_leads(st.session_state.lead_db)
            save_leads(st.session_state.lead_db)
            st.success(f"Lead {delete_lead_id} deleted and leads.csv updated.")
    else:
        st.info("No leads available to delete.")

# =========================================================
# TAB 3 - CLIENT CRM V4
# =========================================================
with tab3:
    st.markdown('<div class="section-title">Client CRM V4 (Add • Edit • Delete)</div>', unsafe_allow_html=True)

    st.session_state.client_db = normalize_clients(st.session_state.client_db)

    # ---------------- ADD CLIENT ----------------
    st.markdown("### ➕ Add New Client")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        new_client_name = st.text_input("Client Name", key="new_client_name_v4")
    with c2:
        new_client_mobile = st.text_input("Client Mobile", key="new_client_mobile_v4")
    with c3:
        new_client_city = st.text_input("Client City", key="new_client_city_v4", value="Bengaluru")
    with c4:
        new_client_sip = st.number_input("Monthly SIP (₹)", min_value=0, max_value=5000000, value=5000, step=500, key="new_client_sip_v4")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        new_client_income = st.number_input("Monthly Income (₹)", min_value=0, max_value=5000000, value=80000, step=5000, key="new_client_income_v4")
    with c6:
        new_client_networth = st.number_input("Net Worth (₹)", min_value=0, max_value=500000000, value=1000000, step=50000, key="new_client_networth_v4")
    with c7:
        new_client_risk = st.selectbox("Risk Category", ["Conservative", "Balanced", "Aggressive"], key="new_client_risk_v4")
    with c8:
        referred_by = st.text_input("Referred By Lead ID (optional)", key="referred_by_v4")

    if st.button("Add Client to CSV Database"):
        temp_surplus = max(new_client_income - (new_client_income * 0.6), 0)
        temp_segment = get_client_segment(new_client_income, temp_surplus, new_client_networth)

        new_client_row = pd.DataFrame([{
            "Client ID": next_client_id(st.session_state.client_db),
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Client Name": new_client_name if new_client_name else "Unnamed Client",
            "Mobile": new_client_mobile if new_client_mobile else "",
            "City": new_client_city,
            "Segment": temp_segment,
            "Risk Category": new_client_risk,
            "Monthly SIP": new_client_sip,
            "Net Worth": new_client_networth,
            "Referred By Lead ID": referred_by.strip()
        }], columns=CLIENT_COLUMNS)

        st.session_state.client_db = pd.concat([st.session_state.client_db, new_client_row], ignore_index=True)
        st.session_state.client_db = normalize_clients(st.session_state.client_db)
        save_clients(st.session_state.client_db)
        st.success("Client added and saved to clients.csv successfully.")

    st.markdown("---")

    # ---------------- SEARCH CLIENTS ----------------
    st.markdown("### 🔎 Search Clients")
    client_search = st.text_input("Search by Name / Mobile / City", key="client_search_v4")

    client_view = st.session_state.client_db.copy()
    if client_search:
        search_lower = client_search.lower()
        client_view = client_view[
            client_view["Client Name"].astype(str).str.lower().str.contains(search_lower, na=False) |
            client_view["Mobile"].astype(str).str.lower().str.contains(search_lower, na=False) |
            client_view["City"].astype(str).str.lower().str.contains(search_lower, na=False)
        ]

    st.dataframe(client_view, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download Clients CSV",
        data=st.session_state.client_db.to_csv(index=False).encode("utf-8"),
        file_name="freedom_clients_v4.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # ---------------- EDIT CLIENT ----------------
    st.markdown("### ✏️ Edit Client")
    if len(st.session_state.client_db) > 0:
        edit_client_id = st.selectbox("Select Client ID to Edit", st.session_state.client_db["Client ID"].astype(str).tolist(), key="edit_client_id_v4")
        edit_client_row = st.session_state.client_db[st.session_state.client_db["Client ID"].astype(str) == str(edit_client_id)].iloc[0]

        ec1, ec2, ec3, ec4 = st.columns(4)
        with ec1:
            ec_name = st.text_input("Edit Client Name", value=str(edit_client_row["Client Name"]), key="ec_name_v4")
        with ec2:
            ec_mobile = st.text_input("Edit Mobile", value=str(edit_client_row["Mobile"]), key="ec_mobile_v4")
        with ec3:
            ec_city = st.text_input("Edit City", value=str(edit_client_row["City"]), key="ec_city_v4")
        with ec4:
            ec_segment = st.selectbox("Edit Segment", ["Starter", "Emerging", "Growth", "Premium"],
                                      index=["Starter", "Emerging", "Growth", "Premium"].index(str(edit_client_row["Segment"])) if str(edit_client_row["Segment"]) in ["Starter", "Emerging", "Growth", "Premium"] else 1,
                                      key="ec_segment_v4")

        ec5, ec6, ec7, ec8 = st.columns(4)
        with ec5:
            ec_risk = st.selectbox("Edit Risk", ["Conservative", "Balanced", "Aggressive"],
                                   index=["Conservative", "Balanced", "Aggressive"].index(str(edit_client_row["Risk Category"])) if str(edit_client_row["Risk Category"]) in ["Conservative", "Balanced", "Aggressive"] else 1,
                                   key="ec_risk_v4")
        with ec6:
            ec_sip = st.number_input("Edit SIP", min_value=0, max_value=5000000, value=to_int(edit_client_row["Monthly SIP"]), step=500, key="ec_sip_v4")
        with ec7:
            ec_nw = st.number_input("Edit Net Worth", min_value=0, max_value=500000000, value=to_int(edit_client_row["Net Worth"]), step=50000, key="ec_nw_v4")
        with ec8:
            ec_ref = st.text_input("Edit Referred By Lead ID", value=str(edit_client_row["Referred By Lead ID"]), key="ec_ref_v4")

        if st.button("Update Client in CSV Database"):
            idx = st.session_state.client_db.index[st.session_state.client_db["Client ID"].astype(str) == str(edit_client_id)][0]
            st.session_state.client_db.at[idx, "Client Name"] = ec_name
            st.session_state.client_db.at[idx, "Mobile"] = ec_mobile
            st.session_state.client_db.at[idx, "City"] = ec_city
            st.session_state.client_db.at[idx, "Segment"] = ec_segment
            st.session_state.client_db.at[idx, "Risk Category"] = ec_risk
            st.session_state.client_db.at[idx, "Monthly SIP"] = ec_sip
            st.session_state.client_db.at[idx, "Net Worth"] = ec_nw
            st.session_state.client_db.at[idx, "Referred By Lead ID"] = ec_ref.strip()

            st.session_state.client_db = normalize_clients(st.session_state.client_db)
            save_clients(st.session_state.client_db)
            st.success(f"Client {edit_client_id} updated successfully.")
    else:
        st.info("No clients available to edit.")

    st.markdown("---")

    # ---------------- DELETE CLIENT ----------------
    st.markdown("### 🗑 Delete Client")
    if len(st.session_state.client_db) > 0:
        delete_client_id = st.selectbox("Select Client ID to Delete", st.session_state.client_db["Client ID"].astype(str).tolist(), key="delete_client_id_v4")
        if st.button("Delete Selected Client from CSV Database"):
            st.session_state.client_db = st.session_state.client_db[st.session_state.client_db["Client ID"].astype(str) != str(delete_client_id)].reset_index(drop=True)
            st.session_state.client_db = normalize_clients(st.session_state.client_db)
            save_clients(st.session_state.client_db)
            st.success(f"Client {delete_client_id} deleted and clients.csv updated.")
    else:
        st.info("No clients available to delete.")

# =========================================================
# TAB 4 - SIP PROPOSAL
# =========================================================
with tab4:
    st.markdown('<div class="section-title">ULTRA PRO V4 SIP Proposal</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="section-title">ULTRA PRO V4 Retirement Proposal</div>', unsafe_allow_html=True)

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
        file_name="freedom_rm_leaderboard_v4.csv",
        mime="text/csv"
    )

# =========================================================
# TAB 9 - CSV UPLOAD
# =========================================================
with tab9:
    st.markdown('<div class="section-title">Bulk CSV Upload (Validated)</div>', unsafe_allow_html=True)

    upload_type = st.selectbox("Select Upload Type", ["Lead Master CSV", "Client Master CSV"], key="upload_type_v4")
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"], key="upload_file_v4")

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            st.success("CSV uploaded successfully.")
            st.dataframe(uploaded_df, use_container_width=True)

            if upload_type == "Lead Master CSV":
                st.info("Missing columns will be auto-filled. Existing extra columns will be ignored.")
                if st.button("Append to Lead CSV Database"):
                    temp_df = normalize_leads(uploaded_df)
                    st.session_state.lead_db = pd.concat([st.session_state.lead_db, temp_df], ignore_index=True)
                    st.session_state.lead_db = normalize_leads(st.session_state.lead_db)
                    save_leads(st.session_state.lead_db)
                    st.success("Uploaded data appended to leads.csv.")
            else:
                st.info("Missing columns will be auto-filled. Existing extra columns will be ignored.")
                if st.button("Append to Client CSV Database"):
                    temp_df = normalize_clients(uploaded_df)
                    st.session_state.client_db = pd.concat([st.session_state.client_db, temp_df], ignore_index=True)
                    st.session_state.client_db = normalize_clients(st.session_state.client_db)
                    save_clients(st.session_state.client_db)
                    st.success("Uploaded data appended to clients.csv.")

        except Exception as e:
            st.error(f"Error reading CSV: {e}")

# =========================================================
# TAB 10 - MIS REPORTS
# =========================================================
with tab10:
    st.markdown('<div class="section-title">MIS Reports + Download Center</div>', unsafe_allow_html=True)

    lead_db = normalize_leads(st.session_state.lead_db)
    client_db = normalize_clients(st.session_state.client_db)

    total_leads = len(lead_db)
    total_clients = len(client_db)
    hot_leads = len(lead_db[lead_db["Lead Temperature"] == "🔥 Hot Lead"]) if total_leads > 0 else 0
    warm_leads = len(lead_db[lead_db["Lead Temperature"] == "🟡 Warm Lead"]) if total_leads > 0 else 0
    cold_leads = len(lead_db[lead_db["Lead Temperature"] == "🔵 Cold Lead"]) if total_leads > 0 else 0
    due_today = len(lead_db[lead_db["Follow-up Status"] == "Today"]) if total_leads > 0 else 0
    converted_leads = len(lead_db[lead_db["Lead Stage"] == "Converted"]) if total_leads > 0 else 0

    total_book_sip = pd.to_numeric(client_db["Monthly SIP"], errors="coerce").fillna(0).sum() if total_clients > 0 else 0
    total_book_networth = pd.to_numeric(client_db["Net Worth"], errors="coerce").fillna(0).sum() if total_clients > 0 else 0
    avg_client_sip = total_book_sip / total_clients if total_clients > 0 else 0
    total_referrals = pd.to_numeric(lead_db["Referral Count"], errors="coerce").fillna(0).sum() if total_leads > 0 else 0

    mis_df = pd.DataFrame({
        "Metric": [
            "Total Leads",
            "Hot Leads",
            "Warm Leads",
            "Cold Leads",
            "Follow-up Today",
            "Converted Leads",
            "Total Clients",
            "Conversion Rate",
            "Client Book SIP",
            "Average Client SIP",
            "Client Book Net Worth",
            "Referral Count"
        ],
        "Value": [
            total_leads,
            hot_leads,
            warm_leads,
            cold_leads,
            due_today,
            converted_leads,
            total_clients,
            f"{safe_ratio(total_clients, total_leads):.1f}%",
            format_inr(total_book_sip),
            format_inr(avg_client_sip),
            format_inr(total_book_networth),
            to_int(total_referrals)
        ]
    })

    st.dataframe(mis_df, use_container_width=True, hide_index=True)

    if total_clients > 0:
        seg_df = client_db.groupby("Segment").size().reset_index(name="Count")
        st.markdown("### 👥 Client Segment Mix")
        st.dataframe(seg_df, use_container_width=True, hide_index=True)

    combined_report = pd.concat([
        lead_db.assign(Record_Type="Lead"),
        client_db.assign(Record_Type="Client")
    ], ignore_index=True, sort=False)

    st.download_button(
        "⬇️ Download Combined MIS CSV",
        data=combined_report.to_csv(index=False).encode("utf-8"),
        file_name="freedom_combined_mis_v4.csv",
        mime="text/csv"
    )

    st.download_button(
        "⬇️ Download Lead CRM CSV",
        data=lead_db.to_csv(index=False).encode("utf-8"),
        file_name="freedom_lead_crm_v4.csv",
        mime="text/csv"
    )

    st.download_button(
        "⬇️ Download Client CRM CSV",
        data=client_db.to_csv(index=False).encode("utf-8"),
        file_name="freedom_client_crm_v4.csv",
        mime="text/csv"
    )

# =========================================================
# TAB 11 - FINAL SUMMARY
# =========================================================
with tab11:
    st.markdown('<div class="section-title">Final ULTRA PRO V4 Summary</div>', unsafe_allow_html=True)

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

    lead_db = normalize_leads(st.session_state.lead_db)
    client_db = normalize_clients(st.session_state.client_db)

    total_client_sip_summary = pd.to_numeric(client_db["Monthly SIP"], errors="coerce").fillna(0).sum() if len(client_db) > 0 else 0
    total_client_nw_summary = pd.to_numeric(client_db["Net Worth"], errors="coerce").fillna(0).sum() if len(client_db) > 0 else 0
    due_today_summary = len(lead_db[lead_db["Follow-up Status"] == "Today"]) if len(lead_db) > 0 else 0

    final_summary_df = pd.DataFrame({
        "Field": [
            "Advisor / MFD", "RM", "Client Name", "City", "Client Segment",
            "Lead Score", "Lead Temperature", "Conversion Probability",
            "Monthly Income", "Monthly Expenses", "Monthly Surplus", "Net Worth",
            "Existing SIP", "Goal", "Goal SIP", "Retirement SIP",
            "Life Cover Gap", "Health Cover Gap", "Lead DB Count", "Client DB Count",
            "Follow-up Due Today", "Client Book SIP"
        ],
        "Value": [
            advisor_name, rm_name, client_name, city_name, client_segment,
            lead_score, lead_temperature, conversion_probability,
            format_inr(monthly_income), format_inr(monthly_expenses), format_inr(monthly_surplus), format_inr(net_worth),
            format_inr(existing_sip), final_goal_name, format_inr(final_goal_sip), format_inr(retirement_sip),
            format_inr(life_cover_gap), format_inr(health_cover_gap), len(lead_db), len(client_db),
            due_today_summary, format_inr(total_client_sip_summary)
        ]
    })

    st.dataframe(final_summary_df, use_container_width=True, hide_index=True)

    summary_text = f"""
FREEDOM ULTRA PRO V4 SUMMARY

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

DATABASE
- Total Leads in leads.csv: {len(lead_db)}
- Total Clients in clients.csv: {len(client_db)}
- Follow-up Due Today: {due_today_summary}

MIS
- Client Book SIP: {format_inr(total_client_sip_summary)}
- Client Book Net Worth: {format_inr(total_client_nw_summary)}
"""
    st.text_area("ULTRA PRO V4 Summary", summary_text, height=720)

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
    recommendations.append("Use Follow-up Today dashboard daily for closure discipline.")
    recommendations.append("Use Convert Lead → Client workflow to keep CRM clean and business-focused.")
    recommendations.append("Keep weekly backup downloads of leads.csv and clients.csv.")

    st.markdown("### ✅ ULTRA PRO V4 Action Plan")
    for i, rec in enumerate(recommendations, start=1):
        st.write(f"{i}. {rec}")

# =========================================================
# TAB 12 - ADMIN TOOLS
# =========================================================
with tab12:
    st.markdown('<div class="section-title">Admin Tools</div>', unsafe_allow_html=True)

    st.info("Use these tools carefully. These actions affect your CSV database files.")

    a1, a2 = st.columns(2)

    with a1:
        if st.button("🔄 Reload CSV Database"):
            st.session_state.lead_db = load_leads()
            st.session_state.client_db = load_clients()
            st.success("CSV files reloaded into app.")

    with a2:
        if st.button("💾 Force Save Current Data"):
            save_leads(st.session_state.lead_db)
            save_clients(st.session_state.client_db)
            st.success("Current app data force-saved to CSV files.")

    st.markdown("---")
    st.markdown("### 🧹 Reset Database to Default Demo Data")

    confirm_reset = st.checkbox("I understand this will overwrite leads.csv and clients.csv")
    if st.button("Reset CSV Database") and confirm_reset:
        if os.path.exists(LEADS_FILE):
            os.remove(LEADS_FILE)
        if os.path.exists(CLIENTS_FILE):
            os.remove(CLIENTS_FILE)

        create_default_files()
        st.session_state.lead_db = load_leads()
        st.session_state.client_db = load_clients()
        st.success("CSV database reset to default demo data.")

    st.markdown("---")
    st.markdown("### 📁 Current Database Files")
    st.write(f"Leads file: `{LEADS_FILE}`")
    st.write(f"Clients file: `{CLIENTS_FILE}`")
    st.write(f"Leads records: {len(st.session_state.lead_db)}")
    st.write(f"Clients records: {len(st.session_state.client_db)}")

    st.markdown("---")
    st.markdown("### 🔐 Login Security Status")
    if "APP_USERNAME" in st.secrets and "APP_PASSWORD" in st.secrets:
        st.success("Secure login is active via Streamlit Secrets.")
    else:
        st.warning("Demo login fallback is active. Add secrets in Streamlit Cloud for production safety.")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    '<div class="footer-note">⚠️ Disclaimer: This tool is for business presentation, client engagement and planning support only. It is not investment advice, insurance advice, tax advice or a regulated recommendation. Final suitability must be based on full risk profiling, product suitability, disclosures, underwriting, taxation and applicable regulations.</div>',
    unsafe_allow_html=True
)
