import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Freedom CRM + MFD Conversion App",
    page_icon="📈",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}
.sub-title {
    font-size: 15px;
    color: #475569;
    margin-bottom: 14px;
}
.brand-bar {
    background: linear-gradient(90deg, #0f172a, #1e3a8a);
    color: white;
    padding: 12px 16px;
    border-radius: 14px;
    margin-bottom: 14px;
    font-size: 14px;
    font-weight: 600;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
    margin-top: 8px;
    margin-bottom: 10px;
}
.footer-note {
    color: #64748b;
    font-size: 13px;
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">📈 Freedom CRM + MFD Conversion App</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Lead Pipeline • Conversion Scoring • SIP Sales • Retirement • Protection • Referral • RM Dashboard • Monthly Target Review</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-bar">Freedom Advisory CRM Desk • Prospect to Client Conversion • SIP First Growth • Referral-Led Expansion</div>', unsafe_allow_html=True)

# =========================================================
# HELPER FUNCTIONS
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

def future_value_of_sip(monthly_sip, annual_return, years):
    n = years * 12
    r = annual_return / 100 / 12
    if n <= 0:
        return 0.0
    if r == 0:
        return monthly_sip * n
    return max(monthly_sip * (((1 + r) ** n - 1) / r), 0.0)

def future_value_of_lumpsum(present_value, annual_return, years):
    return present_value * ((1 + annual_return / 100) ** years)

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
    else:
        return "🔵 Cold Lead"

def get_conversion_probability(score):
    if score >= 85:
        return "Very High"
    elif score >= 70:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"

# =========================================================
# SIDEBAR - CRM + CLIENT INPUTS
# =========================================================
st.sidebar.header("🏢 Freedom CRM Setup")

advisor_name = st.sidebar.text_input("Advisor / MFD Name", "Freedom Advisory")
branch_name = st.sidebar.text_input("Branch / Location", "Bengaluru")
rm_name = st.sidebar.text_input("Relationship Manager", "Parvez")

st.sidebar.markdown("---")
st.sidebar.header("📞 Lead Details")

meeting_type = st.sidebar.selectbox("Meeting Type", ["New Lead", "Follow-up", "Second Meeting", "SIP Upgrade", "Retirement Review", "Protection Review"])
lead_source = st.sidebar.selectbox("Lead Source", ["Referral", "Walk-in", "Existing Client", "Digital", "Corporate Reference", "Other"])
lead_stage = st.sidebar.selectbox("Lead Stage", ["Prospect", "Qualified", "Proposal Shared", "Negotiation", "Converted"])
follow_up_status = st.sidebar.selectbox("Follow-up Status", ["Pending", "Today", "This Week", "Completed"])
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
expense_ratio = safe_ratio(monthly_expenses, monthly_income)
net_worth = existing_savings + existing_investments - liabilities

years_to_retirement = max(retirement_age - age, 0)
years_post_retirement = max(life_expectancy - retirement_age, 1)

ret_corpus, expense_at_retirement = retirement_corpus_needed(
    monthly_expenses,
    inflation_rate,
    years_to_retirement,
    years_post_retirement,
    retirement_return_post
)

current_total_assets = existing_savings + existing_investments
future_existing_assets = current_total_assets * ((1 + retirement_return_pre / 100) ** years_to_retirement) if years_to_retirement > 0 else current_total_assets
additional_corpus_needed = max(ret_corpus - future_existing_assets, 0.0)
retirement_sip = calculate_sip(additional_corpus_needed, retirement_return_pre, years_to_retirement) if years_to_retirement > 0 else 0.0

recommended_life_cover = calculate_life_cover(
    monthly_expenses, 15, liabilities, current_total_assets, annual_income
)
life_cover_gap = max(recommended_life_cover - existing_life_cover, 0.0)

recommended_emergency_fund = monthly_expenses * 6
recommended_health_cover = max(500000.0, annual_income * 0.5)
health_cover_gap = max(recommended_health_cover - existing_health_cover, 0.0)

risk_score, derived_risk_category = risk_score_from_inputs(age, monthly_surplus, monthly_income, risk_profile)
suggested_allocation = get_allocation(derived_risk_category)

# CRM scoring
lead_score = 0
if lead_source == "Referral":
    lead_score += 25
elif lead_source == "Existing Client":
    lead_score += 20
elif lead_source == "Corporate Reference":
    lead_score += 18
elif lead_source == "Walk-in":
    lead_score += 12
elif lead_source == "Digital":
    lead_score += 10
else:
    lead_score += 8

stage_map = {
    "Prospect": 10,
    "Qualified": 25,
    "Proposal Shared": 45,
    "Negotiation": 65,
    "Converted": 100
}
lead_score += stage_map.get(lead_stage, 0)

if follow_up_status == "Completed":
    lead_score += 10
elif follow_up_status == "Today":
    lead_score += 8
elif follow_up_status == "This Week":
    lead_score += 5
else:
    lead_score += 2

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

# Goal proposal defaults
goal_name_default = "Wealth Creation"
current_goal_cost_default = 1000000
goal_years_default = 10
inflated_goal_value_default = future_value_with_inflation(current_goal_cost_default, inflation_rate, goal_years_default)
goal_sip_default = calculate_sip(inflated_goal_value_default, goal_return, goal_years_default)

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "🎯 CRM Dashboard",
    "📞 Lead Tracker",
    "👤 Client Onboarding",
    "📈 SIP Conversion",
    "🏖 Retirement Conversion",
    "🛡 Cross-Sell Engine",
    "📋 RM Follow-up Desk",
    "🎯 Target Tracker",
    "🤝 Referral Tracker",
    "📊 Business Snapshot",
    "🧾 Final Conversion Summary"
])

# =========================================================
# TAB 1 - CRM DASHBOARD
# =========================================================
with tab1:
    st.markdown('<div class="section-title">CRM Conversion Dashboard</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lead Score", f"{lead_score}/100")
    c2.metric("Lead Temperature", lead_temperature)
    c3.metric("Conversion Probability", conversion_probability)
    c4.metric("Lead Stage", lead_stage)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Monthly Surplus", format_inr(monthly_surplus))
    c6.metric("SIP Conversion Score", f"{sip_conversion_score}/100")
    c7.metric("Cross-Sell Score", f"{cross_sell_score}/100")
    c8.metric("Risk Category", derived_risk_category)

    crm_df = pd.DataFrame({
        "Score": [lead_score, sip_conversion_score, cross_sell_score, risk_score]
    }, index=["Lead Score", "SIP Conversion", "Cross-Sell", "Risk Score"])
    st.bar_chart(crm_df, use_container_width=True)

# =========================================================
# TAB 2 - LEAD TRACKER
# =========================================================
with tab2:
    st.markdown('<div class="section-title">Lead Tracker</div>', unsafe_allow_html=True)

    lead_df = pd.DataFrame({
        "Field": [
            "Meeting Type", "Lead Source", "Lead Stage", "Follow-up Status",
            "Days Since Last Meeting", "Client Name", "Mobile", "City"
        ],
        "Value": [
            meeting_type, lead_source, lead_stage, follow_up_status,
            days_since_last_meeting, client_name, mobile_no, city_name
        ]
    })
    st.dataframe(lead_df, use_container_width=True, hide_index=True)

    if lead_stage == "Prospect":
        st.warning("Next Action: Qualify the lead and schedule discovery discussion.")
    elif lead_stage == "Qualified":
        st.info("Next Action: Present goal-based need analysis and start SIP discussion.")
    elif lead_stage == "Proposal Shared":
        st.info("Next Action: Follow-up within 48 hours and handle objections.")
    elif lead_stage == "Negotiation":
        st.success("Next Action: Push for closure, onboarding documents, and first SIP mandate.")
    else:
        st.success("Client already converted. Focus on SIP upgrade, cross-sell and referrals.")

# =========================================================
# TAB 3 - CLIENT ONBOARDING
# =========================================================
with tab3:
    st.markdown('<div class="section-title">Client Onboarding Snapshot</div>', unsafe_allow_html=True)

    onboarding_df = pd.DataFrame({
        "Field": [
            "Advisor / MFD", "Relationship Manager", "Branch", "Client Name", "Mobile",
            "Age", "Retirement Age", "Dependents", "Declared Risk", "Derived Risk"
        ],
        "Value": [
            advisor_name, rm_name, branch_name, client_name, mobile_no,
            age, retirement_age, dependents, risk_profile, derived_risk_category
        ]
    })
    st.dataframe(onboarding_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 4 - SIP CONVERSION
# =========================================================
with tab4:
    st.markdown('<div class="section-title">SIP Conversion Proposal</div>', unsafe_allow_html=True)

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

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Current SIP", format_inr(existing_sip))
    s2.metric("Goal SIP Pitch", format_inr(goal_sip))
    s3.metric("Retirement SIP Pitch", format_inr(retirement_sip))
    s4.metric("Total SIP Opportunity", format_inr(total_sip_pitch))

    s5, s6 = st.columns(2)
    s5.metric("Future Goal Value", format_inr(inflated_goal_value))
    s6.metric("Lumpsum Alternative", format_inr(goal_lumpsum))

    years_list = list(range(1, goal_years + 1))
    projected_values = [future_value_with_inflation(current_goal_cost, inflation_rate, y) for y in years_list]
    goal_df = pd.DataFrame({
        "Year": years_list,
        "Projected Goal Value": projected_values
    })

    c1, c2 = st.columns(2)
    with c1:
        st.line_chart(goal_df.set_index("Year"), use_container_width=True)
    with c2:
        show_df = goal_df.copy()
        show_df["Projected Goal Value"] = show_df["Projected Goal Value"].apply(format_inr)
        st.dataframe(show_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 5 - RETIREMENT CONVERSION
# =========================================================
with tab5:
    st.markdown('<div class="section-title">Retirement Conversion Proposal</div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Years to Retirement", f"{years_to_retirement} Years")
    r2.metric("Retirement Corpus", format_inr(ret_corpus))
    r3.metric("Expense at Retirement", format_inr(expense_at_retirement))
    r4.metric("Retirement SIP", format_inr(retirement_sip))

    ret_df = pd.DataFrame({
        "Metric": [
            "Current Total Assets", "Future Value of Existing Assets",
            "Additional Corpus Needed", "Retirement SIP Required"
        ],
        "Value": [
            format_inr(current_total_assets),
            format_inr(future_existing_assets),
            format_inr(additional_corpus_needed),
            format_inr(retirement_sip)
        ]
    })

    c1, c2 = st.columns(2)
    with c1:
        st.dataframe(ret_df, use_container_width=True, hide_index=True)
    with c2:
        corpus_df = pd.DataFrame({
            "Amount": [future_existing_assets, additional_corpus_needed]
        }, index=["Existing Asset FV", "New Retirement Corpus"])
        st.bar_chart(corpus_df, use_container_width=True)

# =========================================================
# TAB 6 - CROSS SELL ENGINE
# =========================================================
with tab6:
    st.markdown('<div class="section-title">Protection Cross-Sell Engine</div>', unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Recommended Life Cover", format_inr(recommended_life_cover))
    p2.metric("Life Cover Gap", format_inr(life_cover_gap))
    p3.metric("Recommended Health Cover", format_inr(recommended_health_cover))
    p4.metric("Health Cover Gap", format_inr(health_cover_gap))

    p5, p6 = st.columns(2)
    p5.metric("Emergency Fund Need", format_inr(recommended_emergency_fund))
    p6.metric("Cross-Sell Score", f"{cross_sell_score}/100")

    protection_df = pd.DataFrame({
        "Opportunity": [
            "Life Cover Gap", "Health Cover Gap", "Emergency Fund Need", "Liabilities"
        ],
        "Amount": [
            life_cover_gap, health_cover_gap, recommended_emergency_fund, liabilities
        ]
    })
    st.bar_chart(protection_df.set_index("Opportunity"), use_container_width=True)

# =========================================================
# TAB 7 - RM FOLLOW-UP DESK
# =========================================================
with tab7:
    st.markdown('<div class="section-title">RM Follow-up Desk</div>', unsafe_allow_html=True)

    next_action = ""
    if lead_stage == "Prospect":
        next_action = "Schedule discovery call and understand client goals."
    elif lead_stage == "Qualified":
        next_action = "Share SIP proposal and book next meeting within 2 days."
    elif lead_stage == "Proposal Shared":
        next_action = "Call within 48 hours, address objections, close first SIP."
    elif lead_stage == "Negotiation":
        next_action = "Push for onboarding docs, mandate, KYC and first transaction."
    else:
        next_action = "Focus on SIP top-up, cross-sell, retention and referrals."

    followup_df = pd.DataFrame({
        "Item": [
            "Lead Stage", "Follow-up Status", "Days Since Last Meeting",
            "Next Best Action", "Lead Temperature", "Conversion Probability"
        ],
        "Value": [
            lead_stage, follow_up_status, days_since_last_meeting,
            next_action, lead_temperature, conversion_probability
        ]
    })
    st.dataframe(followup_df, use_container_width=True, hide_index=True)

    st.success(f"RM Action: {next_action}")

# =========================================================
# TAB 8 - TARGET TRACKER
# =========================================================
with tab8:
    st.markdown('<div class="section-title">Monthly Target Tracker</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        monthly_sip_target = st.number_input("Monthly SIP Target (₹)", min_value=10000, max_value=10000000, value=500000, step=10000)
    with col2:
        monthly_sip_achieved = st.number_input("SIP Achieved This Month (₹)", min_value=0, max_value=10000000, value=150000, step=10000)
    with col3:
        clients_converted = st.number_input("Clients Converted This Month", min_value=0, max_value=1000, value=3, step=1)

    target_balance = max(monthly_sip_target - monthly_sip_achieved, 0)
    achievement_pct = safe_ratio(monthly_sip_achieved, monthly_sip_target)

    t1, t2, t3 = st.columns(3)
    t1.metric("SIP Target", format_inr(monthly_sip_target))
    t2.metric("SIP Achieved", format_inr(monthly_sip_achieved))
    t3.metric("Achievement %", f"{achievement_pct:.1f}%")

    target_df = pd.DataFrame({
        "Amount": [monthly_sip_target, monthly_sip_achieved, target_balance]
    }, index=["Target", "Achieved", "Balance"])
    st.bar_chart(target_df, use_container_width=True)

# =========================================================
# TAB 9 - REFERRAL TRACKER
# =========================================================
with tab9:
    st.markdown('<div class="section-title">Referral Tracker</div>', unsafe_allow_html=True)

    referral_target = st.number_input("Referral Target", min_value=1, max_value=100, value=5, step=1)
    referral_achieved = st.number_input("Referrals Achieved", min_value=0, max_value=100, value=2, step=1)
    referral_balance = max(referral_target - referral_achieved, 0)

    rf1, rf2, rf3 = st.columns(3)
    rf1.metric("Referral Target", referral_target)
    rf2.metric("Achieved", referral_achieved)
    rf3.metric("Balance", referral_balance)

    referral_script = f"""
Thank you {client_name} for your trust.

At Freedom Advisory, we help families start disciplined investing, protection planning and long-term wealth creation.

If you know 2-3 friends, family members or colleagues who may benefit from financial planning, I would truly appreciate an introduction.

Current Referral Status:
- Target: {referral_target}
- Achieved: {referral_achieved}
- Balance: {referral_balance}
"""
    st.text_area("Referral Script", referral_script, height=220)

# =========================================================
# TAB 10 - BUSINESS SNAPSHOT
# =========================================================
with tab10:
    st.markdown('<div class="section-title">Business Snapshot</div>', unsafe_allow_html=True)

    total_sip_opportunity = existing_sip + goal_sip_default + retirement_sip
    total_protection_opportunity = life_cover_gap + health_cover_gap
    total_business_opportunity = total_sip_opportunity + total_protection_opportunity

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("SIP Opportunity", format_inr(total_sip_opportunity))
    b2.metric("Protection Opportunity", format_inr(total_protection_opportunity))
    b3.metric("Total Business Opportunity", format_inr(total_business_opportunity))
    b4.metric("Clients Converted", clients_converted)

    biz_df = pd.DataFrame({
        "Amount": [
            total_sip_opportunity,
            total_protection_opportunity,
            monthly_sip_achieved,
            monthly_sip_target
        ]
    }, index=[
        "Current Lead Opportunity",
        "Protection Opportunity",
        "Monthly SIP Achieved",
        "Monthly SIP Target"
    ])
    st.bar_chart(biz_df, use_container_width=True)

# =========================================================
# TAB 11 - FINAL CONVERSION SUMMARY
# =========================================================
with tab11:
    st.markdown('<div class="section-title">Final CRM + Conversion Summary</div>', unsafe_allow_html=True)

    allocation_df = pd.DataFrame({
        "Asset Class": list(suggested_allocation.keys()),
        "Suggested Allocation (%)": list(suggested_allocation.values())
    })
    st.markdown("### 🎯 Suggested Allocation")
    st.dataframe(allocation_df, use_container_width=True, hide_index=True)

    # Use actual goal tab values if visited, else defaults
    try:
        final_goal_name = goal_name
        final_goal_value = inflated_goal_value
        final_goal_sip = goal_sip
        final_goal_lumpsum = goal_lumpsum
        final_total_sip_pitch = existing_sip + goal_sip + retirement_sip
    except:
        final_goal_name = goal_name_default
        final_goal_value = inflated_goal_value_default
        final_goal_sip = goal_sip_default
        final_goal_lumpsum = calculate_lumpsum_required(inflated_goal_value_default, goal_return, goal_years_default)
        final_total_sip_pitch = existing_sip + goal_sip_default + retirement_sip

    recommendations = []

    if lead_score >= 75:
        recommendations.append("High-priority lead. Push for conversion in current meeting cycle.")
    elif lead_score >= 50:
        recommendations.append("Warm lead. Strong follow-up within 48 hours recommended.")
    else:
        recommendations.append("Cold lead. Build trust, educate, and schedule structured follow-up.")

    recommendations.append(f"Primary SIP opportunity around {format_inr(final_total_sip_pitch)} including existing + goal + retirement.")
    recommendations.append(f"Goal-based SIP for {final_goal_name}: approx {format_inr(final_goal_sip)}.")
    recommendations.append(f"Retirement SIP opportunity: approx {format_inr(retirement_sip)}.")

    if life_cover_gap > 0:
        recommendations.append(f"Life cover cross-sell opportunity: {format_inr(life_cover_gap)}.")
    if health_cover_gap > 0:
        recommendations.append(f"Health cover cross-sell opportunity: {format_inr(health_cover_gap)}.")

    recommendations.append(f"Monthly target achievement currently at {achievement_pct:.1f}%.")
    recommendations.append(f"Ask for at least 2-3 referrals after successful proposal discussion.")
    recommendations.append(f"Lead temperature is {lead_temperature} with {conversion_probability} conversion probability.")

    summary_text = f"""
FREEDOM CRM + MFD CONVERSION SUMMARY

BUSINESS
- Advisor / MFD: {advisor_name}
- RM: {rm_name}
- Branch: {branch_name}

LEAD PROFILE
- Meeting Type: {meeting_type}
- Lead Source: {lead_source}
- Lead Stage: {lead_stage}
- Follow-up Status: {follow_up_status}
- Days Since Last Meeting: {days_since_last_meeting}
- Lead Score: {lead_score}/100
- Lead Temperature: {lead_temperature}
- Conversion Probability: {conversion_probability}

CLIENT DETAILS
- Client Name: {client_name}
- Mobile: {mobile_no}
- City: {city_name}
- Age: {age}
- Retirement Age: {retirement_age}
- Dependents: {dependents}
- Declared Risk Profile: {risk_profile}
- Derived Risk Category: {derived_risk_category}
- Risk Score: {risk_score}/100

FINANCIALS
- Monthly Income: {format_inr(monthly_income)}
- Monthly Expenses: {format_inr(monthly_expenses)}
- Monthly Surplus: {format_inr(monthly_surplus)}
- Savings Ratio: {savings_ratio:.1f}%
- Existing SIP: {format_inr(existing_sip)}
- Net Worth: {format_inr(net_worth)}

SIP CONVERSION
- Goal: {final_goal_name}
- Future Goal Value: {format_inr(final_goal_value)}
- Goal SIP: {format_inr(final_goal_sip)}
- Goal Lumpsum: {format_inr(final_goal_lumpsum)}
- Retirement SIP: {format_inr(retirement_sip)}
- Total SIP Pitch: {format_inr(final_total_sip_pitch)}
- SIP Conversion Score: {sip_conversion_score}/100

RETIREMENT
- Retirement Corpus Needed: {format_inr(ret_corpus)}
- Future Value of Existing Assets: {format_inr(future_existing_assets)}
- Additional Corpus Needed: {format_inr(additional_corpus_needed)}

CROSS-SELL
- Recommended Life Cover: {format_inr(recommended_life_cover)}
- Life Cover Gap: {format_inr(life_cover_gap)}
- Recommended Health Cover: {format_inr(recommended_health_cover)}
- Health Cover Gap: {format_inr(health_cover_gap)}
- Cross-Sell Score: {cross_sell_score}/100

TARGETS
- Monthly SIP Target: {format_inr(monthly_sip_target)}
- Monthly SIP Achieved: {format_inr(monthly_sip_achieved)}
- Achievement %: {achievement_pct:.1f}%
- Clients Converted This Month: {clients_converted}

REFERRALS
- Referral Target: {referral_target}
- Referral Achieved: {referral_achieved}
- Referral Balance: {referral_balance}

SUGGESTED ALLOCATION
- Equity: {suggested_allocation.get("Equity", 0)}%
- Debt: {suggested_allocation.get("Debt", 0)}%
- Gold: {suggested_allocation.get("Gold", 0)}%
- Cash: {suggested_allocation.get("Cash", 0)}%
"""
    st.text_area("Freedom CRM Conversion Summary", summary_text, height=650)

    st.markdown("### ✅ RM / Advisor Action Plan")
    for idx, rec in enumerate(recommendations, start=1):
        st.write(f"{idx}. {rec}")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    '<div class="footer-note">⚠️ Disclaimer: This tool is for business presentation, client engagement and planning support only. It is not investment advice, insurance advice, tax advice or a regulated recommendation. Final suitability must be based on complete risk profiling, product suitability, disclosures, underwriting, taxation and applicable regulations.</div>',
    unsafe_allow_html=True
)
