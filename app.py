import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Freedom MFD Sales Planner",
    page_icon="🚀",
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
st.markdown('<div class="main-title">🚀 Freedom MFD Sales Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Lead Capture • Client Onboarding • SIP Proposal • Retirement • Insurance Cross-Sell • Tax Snapshot • Referral Growth</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-bar">Freedom Advisory Growth Desk • Goal-Based Sales • SIP First • Client Retention • Referral Engine</div>', unsafe_allow_html=True)

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

def future_value_of_sip(monthly_sip, annual_return, years):
    n = years * 12
    r = annual_return / 100 / 12
    if n <= 0:
        return 0.0
    if r == 0:
        return monthly_sip * n
    return max(monthly_sip * (((1 + r) ** n - 1) / r), 0.0)

def calculate_lumpsum_required(future_value, annual_return, years):
    if years <= 0:
        return future_value
    return future_value / ((1 + annual_return / 100) ** years)

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

# =========================================================
# SIDEBAR - BUSINESS + CLIENT INPUTS
# =========================================================
st.sidebar.header("🏢 Freedom MFD Setup")

advisor_name = st.sidebar.text_input("Advisor / MFD Name", "Freedom Advisory")
branch_name = st.sidebar.text_input("Branch / Location", "Bengaluru")
rm_name = st.sidebar.text_input("Relationship Manager", "Parvez")
meeting_type = st.sidebar.selectbox("Meeting Type", ["New Lead", "Existing Client Review", "SIP Upgrade", "Retirement Review", "Insurance Review"])

st.sidebar.markdown("---")
st.sidebar.header("👤 Lead / Client Details")

client_name = st.sidebar.text_input("Client Name", "Freedom Client")
mobile_no = st.sidebar.text_input("Client Mobile", "9999999999")
city_name = st.sidebar.text_input("City", "Bengaluru")
lead_source = st.sidebar.selectbox("Lead Source", ["Referral", "Walk-in", "Existing Client", "Digital", "Corporate Reference", "Other"])

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

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "🎯 Sales Dashboard",
    "🧾 Lead Capture",
    "👤 Client Onboarding",
    "📈 SIP Proposal",
    "🏖 Retirement Proposal",
    "🛡 Insurance Cross-Sell",
    "🏦 EMI Review",
    "🧾 Tax Snapshot",
    "🤝 Referral Engine",
    "📋 Final Sales Summary"
])

# =========================================================
# TAB 1 - SALES DASHBOARD
# =========================================================
with tab1:
    st.markdown('<div class="section-title">Sales Opportunity Dashboard</div>', unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Monthly Surplus", format_inr(monthly_surplus))
    d2.metric("Existing SIP", format_inr(existing_sip))
    d3.metric("Retirement SIP Potential", format_inr(retirement_sip))
    d4.metric("Life Cover Gap", format_inr(life_cover_gap))

    d5, d6, d7, d8 = st.columns(4)
    d5.metric("Health Cover Gap", format_inr(health_cover_gap))
    d6.metric("Net Worth", format_inr(net_worth))
    d7.metric("Risk Score", f"{risk_score}/100")
    d8.metric("Investor Style", derived_risk_category)

    st.markdown("---")

    sales_potential = existing_sip + retirement_sip
    protection_potential = life_cover_gap + health_cover_gap

    s1, s2, s3 = st.columns(3)
    s1.metric("Potential SIP Upgrade", format_inr(sales_potential))
    s2.metric("Protection Opportunity", format_inr(protection_potential))
    s3.metric("Lead Source", lead_source)

    sales_df = pd.DataFrame({
        "Amount": [
            max(monthly_surplus, 0),
            existing_sip,
            retirement_sip,
            life_cover_gap,
            health_cover_gap
        ]
    }, index=[
        "Monthly Surplus",
        "Existing SIP",
        "Retirement SIP",
        "Life Cover Gap",
        "Health Cover Gap"
    ])
    st.bar_chart(sales_df, use_container_width=True)

# =========================================================
# TAB 2 - LEAD CAPTURE
# =========================================================
with tab2:
    st.markdown('<div class="section-title">Lead Capture Sheet</div>', unsafe_allow_html=True)

    lead_df = pd.DataFrame({
        "Field": [
            "Meeting Type",
            "Lead Source",
            "Advisor / MFD",
            "Relationship Manager",
            "Branch / Location",
            "Client Name",
            "Mobile Number",
            "City",
            "Age",
            "Declared Risk Profile"
        ],
        "Value": [
            meeting_type,
            lead_source,
            advisor_name,
            rm_name,
            branch_name,
            client_name,
            mobile_no,
            city_name,
            age,
            risk_profile
        ]
    })

    st.dataframe(lead_df, use_container_width=True, hide_index=True)

    st.info("Use this as your first-level lead qualification page during prospect meetings.")

# =========================================================
# TAB 3 - CLIENT ONBOARDING
# =========================================================
with tab3:
    st.markdown('<div class="section-title">Client Onboarding Snapshot</div>', unsafe_allow_html=True)

    onboarding_df = pd.DataFrame({
        "Field": [
            "Client Name",
            "Mobile",
            "City",
            "Age",
            "Retirement Age",
            "Dependents",
            "Monthly Income",
            "Monthly Expenses",
            "Monthly Surplus",
            "Savings Ratio",
            "Existing SIP"
        ],
        "Value": [
            client_name,
            mobile_no,
            city_name,
            age,
            retirement_age,
            dependents,
            format_inr(monthly_income),
            format_inr(monthly_expenses),
            format_inr(monthly_surplus),
            f"{savings_ratio:.1f}%",
            format_inr(existing_sip)
        ]
    })

    st.dataframe(onboarding_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 4 - SIP PROPOSAL
# =========================================================
with tab4:
    st.markdown('<div class="section-title">Goal-Based SIP Sales Proposal</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        goal_name = st.selectbox("Select Goal", [
            "Emergency Fund",
            "Child Education",
            "Marriage",
            "House Purchase",
            "Car Purchase",
            "Vacation",
            "Wealth Creation",
            "Custom Goal"
        ])

    with col2:
        current_goal_cost = st.number_input("Current Goal Cost (₹)", min_value=10000, max_value=500000000, value=1000000, step=50000)

    with col3:
        goal_years = st.slider("Years to Goal", 1, 40, 10)

    inflated_goal_value = future_value_with_inflation(current_goal_cost, inflation_rate, goal_years)
    goal_sip = calculate_sip(inflated_goal_value, goal_return, goal_years)
    goal_lumpsum = calculate_lumpsum_required(inflated_goal_value, goal_return, goal_years)

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Current Goal Cost", format_inr(current_goal_cost))
    g2.metric("Future Goal Value", format_inr(inflated_goal_value))
    g3.metric("Required Goal SIP", format_inr(goal_sip))
    g4.metric("Lumpsum Needed Today", format_inr(goal_lumpsum))

    total_sip_pitch = existing_sip + goal_sip + retirement_sip

    st.markdown("---")
    p1, p2, p3 = st.columns(3)
    p1.metric("Current SIP", format_inr(existing_sip))
    p2.metric("Suggested Additional Goal SIP", format_inr(goal_sip))
    p3.metric("Total SIP Pitch (incl. retirement)", format_inr(total_sip_pitch))

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
# TAB 5 - RETIREMENT PROPOSAL
# =========================================================
with tab5:
    st.markdown('<div class="section-title">Retirement Sales Proposal</div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Years to Retirement", f"{years_to_retirement} Years")
    r2.metric("Expense at Retirement", format_inr(expense_at_retirement))
    r3.metric("Retirement Corpus Needed", format_inr(ret_corpus))
    r4.metric("Retirement SIP Pitch", format_inr(retirement_sip))

    st.markdown("---")

    ret_df = pd.DataFrame({
        "Metric": [
            "Current Age",
            "Retirement Age",
            "Life Expectancy",
            "Current Total Assets",
            "Future Value of Existing Assets",
            "Additional Corpus Needed",
            "Retirement SIP Required"
        ],
        "Value": [
            age,
            retirement_age,
            life_expectancy,
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
# TAB 6 - INSURANCE CROSS-SELL
# =========================================================
with tab6:
    st.markdown('<div class="section-title">Insurance Cross-Sell Opportunity</div>', unsafe_allow_html=True)

    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Recommended Life Cover", format_inr(recommended_life_cover))
    i2.metric("Existing Life Cover", format_inr(existing_life_cover))
    i3.metric("Life Cover Gap", format_inr(life_cover_gap))
    i4.metric("Emergency Fund Need", format_inr(recommended_emergency_fund))

    i5, i6, i7 = st.columns(3)
    i5.metric("Recommended Health Cover", format_inr(recommended_health_cover))
    i6.metric("Existing Health Cover", format_inr(existing_health_cover))
    i7.metric("Health Cover Gap", format_inr(health_cover_gap))

    protection_df = pd.DataFrame({
        "Opportunity": [
            "Life Cover Requirement",
            "Existing Life Cover",
            "Life Cover Gap",
            "Health Cover Requirement",
            "Existing Health Cover",
            "Health Cover Gap"
        ],
        "Amount": [
            format_inr(recommended_life_cover),
            format_inr(existing_life_cover),
            format_inr(life_cover_gap),
            format_inr(recommended_health_cover),
            format_inr(existing_health_cover),
            format_inr(health_cover_gap)
        ]
    })
    st.dataframe(protection_df, use_container_width=True, hide_index=True)

    st.warning("Use this page only for need-based discussion and proper suitability. Final policy recommendation must follow underwriting and disclosure norms.")

# =========================================================
# TAB 7 - EMI REVIEW
# =========================================================
with tab7:
    st.markdown('<div class="section-title">EMI & Cashflow Pressure Review</div>', unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)
    with e1:
        loan_amount = st.number_input("Loan Amount (₹)", min_value=10000, max_value=500000000, value=2500000, step=50000)
    with e2:
        loan_rate = st.slider("Loan Interest Rate (%)", 1, 20, 9)
    with e3:
        loan_years = st.slider("Loan Tenure (Years)", 1, 30, 10)

    emi, total_interest, total_payment = emi_calculator(loan_amount, loan_rate, loan_years)
    emi_to_income = safe_ratio(emi, monthly_income)
    post_emi_surplus = monthly_surplus - emi

    em1, em2, em3, em4 = st.columns(4)
    em1.metric("Monthly EMI", format_inr(emi))
    em2.metric("EMI / Income Ratio", f"{emi_to_income:.1f}%")
    em3.metric("Post EMI Surplus", format_inr(post_emi_surplus))
    em4.metric("Total Interest", format_inr(total_interest))

    emi_df = pd.DataFrame({
        "Amount": [loan_amount, total_interest, total_payment]
    }, index=["Principal", "Interest", "Total Payment"])
    st.bar_chart(emi_df, use_container_width=True)

# =========================================================
# TAB 8 - TAX SNAPSHOT
# =========================================================
with tab8:
    st.markdown('<div class="section-title">Tax Snapshot (Indicative Sales Discussion)</div>', unsafe_allow_html=True)

    t1, t2 = st.columns(2)
    with t1:
        tax_annual_income = st.number_input("Annual Gross Income (₹)", min_value=0, max_value=50000000, value=int(annual_income), step=50000)
    with t2:
        old_regime_deductions = st.number_input("Old Regime Deductions (₹)", min_value=0, max_value=5000000, value=150000, step=10000)

    old_taxable, old_tax = tax_regime_old(tax_annual_income, old_regime_deductions)
    new_taxable, new_tax = tax_regime_new(tax_annual_income)

    best_regime = "Old Regime" if old_tax < new_tax else "New Regime"
    tax_saved = abs(old_tax - new_tax)

    tx1, tx2, tx3 = st.columns(3)
    tx1.metric("Old Regime Tax", format_inr(old_tax))
    tx2.metric("New Regime Tax", format_inr(new_tax))
    tx3.metric("Better Option", best_regime)

    tax_df = pd.DataFrame({
        "Regime": ["Old Regime", "New Regime"],
        "Estimated Tax": [old_tax, new_tax]
    })
    st.bar_chart(tax_df.set_index("Regime"), use_container_width=True)
    st.success(f"Indicative tax difference: {format_inr(tax_saved)}")

# =========================================================
# TAB 9 - REFERRAL ENGINE
# =========================================================
with tab9:
    st.markdown('<div class="section-title">Referral Conversation Engine</div>', unsafe_allow_html=True)

    referral_target = st.number_input("Referral Target (No. of Referrals)", min_value=1, max_value=100, value=5, step=1)
    referral_achieved = st.number_input("Referrals Achieved", min_value=0, max_value=100, value=2, step=1)
    referral_balance = max(referral_target - referral_achieved, 0)

    rf1, rf2, rf3 = st.columns(3)
    rf1.metric("Referral Target", referral_target)
    rf2.metric("Referrals Achieved", referral_achieved)
    rf3.metric("Balance to Target", referral_balance)

    referral_df = pd.DataFrame({
        "Count": [referral_target, referral_achieved, referral_balance]
    }, index=["Target", "Achieved", "Balance"])
    st.bar_chart(referral_df, use_container_width=True)

    referral_script = f"""
Thank you {client_name} for your trust and support.

At Freedom Advisory, our goal is to help more families start disciplined financial planning through SIPs, protection and long-term wealth creation.

If you know 2-3 friends, family members or colleagues who may benefit from financial planning, I would be grateful for an introduction.

Current Referral Progress:
- Target: {referral_target}
- Achieved: {referral_achieved}
- Balance: {referral_balance}

Your referral can truly help someone begin the right financial journey.
"""

    st.text_area("Referral Conversation Script", referral_script, height=220)

# =========================================================
# TAB 10 - FINAL SALES SUMMARY
# =========================================================
with tab10:
    st.markdown('<div class="section-title">Final Freedom MFD Sales Summary</div>', unsafe_allow_html=True)

    allocation_df = pd.DataFrame({
        "Asset Class": list(suggested_allocation.keys()),
        "Suggested Allocation (%)": list(suggested_allocation.values())
    })

    st.markdown("### 🎯 Suggested Allocation")
    st.dataframe(allocation_df, use_container_width=True, hide_index=True)

    total_sip_pitch = existing_sip + goal_sip + retirement_sip
    total_protection_gap = life_cover_gap + health_cover_gap

    recommendations = []

    if monthly_surplus > 0:
        recommendations.append(f"Available monthly surplus of {format_inr(monthly_surplus)} can support structured SIP planning.")
    else:
        recommendations.append("Cashflow is tight. Start with emergency reserve and budget correction before aggressive SIP pitch.")

    recommendations.append(f"Current SIP is {format_inr(existing_sip)}. Proposed total SIP opportunity is around {format_inr(total_sip_pitch)}.")
    recommendations.append(f"Goal-based SIP for {goal_name}: approx {format_inr(goal_sip)} per month.")
    recommendations.append(f"Retirement SIP opportunity: approx {format_inr(retirement_sip)} per month.")

    if life_cover_gap > 0:
        recommendations.append(f"Life cover gap exists: approx {format_inr(life_cover_gap)}.")
    if health_cover_gap > 0:
        recommendations.append(f"Health cover enhancement opportunity: approx {format_inr(health_cover_gap)}.")

    recommendations.append(f"Indicative tax comparison currently favors {best_regime}.")
    recommendations.append(f"Derived investor style: {derived_risk_category}. Recommended allocation should follow suitability and product selection norms.")
    recommendations.append("Request at least 2-3 quality referrals after successful proposal discussion.")

    summary_text = f"""
FREEDOM MFD SALES SUMMARY

BUSINESS DETAILS
- Advisor / MFD: {advisor_name}
- Relationship Manager: {rm_name}
- Branch / Location: {branch_name}
- Meeting Type: {meeting_type}

LEAD DETAILS
- Client Name: {client_name}
- Mobile: {mobile_no}
- City: {city_name}
- Lead Source: {lead_source}

CLIENT PROFILE
- Age: {age}
- Retirement Age: {retirement_age}
- Dependents: {dependents}
- Declared Risk Profile: {risk_profile}
- Derived Investor Style: {derived_risk_category}
- Risk Score: {risk_score}/100

CASH FLOW
- Monthly Income: {format_inr(monthly_income)}
- Monthly Expenses: {format_inr(monthly_expenses)}
- Monthly Surplus: {format_inr(monthly_surplus)}
- Savings Ratio: {savings_ratio:.1f}%
- Net Worth: {format_inr(net_worth)}

SIP SALES OPPORTUNITY
- Existing SIP: {format_inr(existing_sip)}
- Goal: {goal_name}
- Current Goal Cost: {format_inr(current_goal_cost)}
- Future Goal Value: {format_inr(inflated_goal_value)}
- Goal SIP Required: {format_inr(goal_sip)}
- Retirement SIP Opportunity: {format_inr(retirement_sip)}
- Total SIP Pitch: {format_inr(total_sip_pitch)}

RETIREMENT PROPOSAL
- Retirement Corpus Needed: {format_inr(ret_corpus)}
- Future Value of Existing Assets: {format_inr(future_existing_assets)}
- Additional Corpus Needed: {format_inr(additional_corpus_needed)}

PROTECTION CROSS-SELL
- Recommended Life Cover: {format_inr(recommended_life_cover)}
- Existing Life Cover: {format_inr(existing_life_cover)}
- Life Cover Gap: {format_inr(life_cover_gap)}
- Recommended Health Cover: {format_inr(recommended_health_cover)}
- Existing Health Cover: {format_inr(existing_health_cover)}
- Health Cover Gap: {format_inr(health_cover_gap)}
- Total Protection Opportunity: {format_inr(total_protection_gap)}

EMI REVIEW
- Loan Amount: {format_inr(loan_amount)}
- EMI: {format_inr(emi)}
- EMI / Income Ratio: {emi_to_income:.1f}%
- Post EMI Surplus: {format_inr(post_emi_surplus)}

TAX SNAPSHOT
- Old Regime Tax: {format_inr(old_tax)}
- New Regime Tax: {format_inr(new_tax)}
- Better Regime (Indicative): {best_regime}

REFERRAL STATUS
- Referral Target: {referral_target}
- Referrals Achieved: {referral_achieved}
- Balance: {referral_balance}

SUGGESTED ALLOCATION
- Equity: {suggested_allocation.get("Equity", 0)}%
- Debt: {suggested_allocation.get("Debt", 0)}%
- Gold: {suggested_allocation.get("Gold", 0)}%
- Cash: {suggested_allocation.get("Cash", 0)}%
"""

    st.text_area("Freedom Sales Summary", summary_text, height=560)

    st.markdown("### ✅ Action Plan for This Client")
    for idx, rec in enumerate(recommendations, start=1):
        st.write(f"{idx}. {rec}")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    '<div class="footer-note">⚠️ Disclaimer: This tool is for educational, business presentation and client discussion purposes only. It is not investment advice, insurance advice, tax advice or a regulated recommendation. Final suitability must be based on complete risk profiling, product suitability, disclosures, underwriting, taxation and applicable regulatory requirements.</div>',
    unsafe_allow_html=True
)
