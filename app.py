import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Freedom MFD Planner",
    page_icon="💼",
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
    margin-bottom: 16px;
}
.brand-bar {
    background: linear-gradient(90deg, #0f172a, #1e3a8a);
    color: white;
    padding: 12px 16px;
    border-radius: 14px;
    margin-bottom: 16px;
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
.small-note {
    color: #64748b;
    font-size: 13px;
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
st.markdown('<div class="main-title">💼 Freedom MFD Business Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Mutual Fund Distributor | Client Onboarding • SIP Proposal • Retirement • Protection • EMI • Tax • Advisor Summary</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-bar">Freedom Advisory Desk • Goal-Based Planning • SIP First Approach • Client-Centric Recommendations</div>', unsafe_allow_html=True)

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
# SIDEBAR - ADVISOR / CLIENT INPUTS
# =========================================================
st.sidebar.header("🏢 Advisor / Client Setup")

advisor_name = st.sidebar.text_input("Advisor / MFD Name", "Freedom Advisory")
branch_name = st.sidebar.text_input("Branch / Location", "Bengaluru")
client_name = st.sidebar.text_input("Client Name", "Freedom Client")
mobile_no = st.sidebar.text_input("Client Mobile", "9999999999")

st.sidebar.markdown("---")
st.sidebar.header("👤 Client Profile")

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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🏠 Client Dashboard",
    "🧾 Onboarding",
    "🎯 SIP Proposal",
    "📈 SIP vs Lumpsum",
    "🏖 Retirement Proposal",
    "🛡 Protection Review",
    "🏦 EMI & Cashflow",
    "🧾 Tax Snapshot",
    "📋 MFD Summary"
])

# =========================================================
# TAB 1 - CLIENT DASHBOARD
# =========================================================
with tab1:
    st.markdown('<div class="section-title">Client Financial Dashboard</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Monthly Income", format_inr(monthly_income))
    c2.metric("Monthly Expenses", format_inr(monthly_expenses))
    c3.metric("Monthly Surplus", format_inr(monthly_surplus))
    c4.metric("Savings Ratio", f"{savings_ratio:.1f}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Existing Savings", format_inr(existing_savings))
    c6.metric("Existing Investments", format_inr(existing_investments))
    c7.metric("Liabilities", format_inr(liabilities))
    c8.metric("Net Worth", format_inr(net_worth))

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        health_df = pd.DataFrame({
            "Metric": [
                "Savings Ratio",
                "Expense Ratio",
                "Emergency Fund Need",
                "Life Cover Gap",
                "Health Cover Gap",
                "Net Worth"
            ],
            "Value": [
                f"{savings_ratio:.1f}%",
                f"{expense_ratio:.1f}%",
                format_inr(recommended_emergency_fund),
                format_inr(life_cover_gap),
                format_inr(health_cover_gap),
                format_inr(net_worth)
            ]
        })
        st.dataframe(health_df, use_container_width=True, hide_index=True)

    with col2:
        cashflow_df = pd.DataFrame({
            "Amount": [monthly_income, monthly_expenses, max(monthly_surplus, 0)]
        }, index=["Income", "Expenses", "Surplus"])
        st.bar_chart(cashflow_df, use_container_width=True)

    st.markdown("---")
    r1, r2 = st.columns(2)
    r1.metric("Risk Score", f"{risk_score}/100")
    r2.metric("Derived Investor Style", derived_risk_category)

# =========================================================
# TAB 2 - ONBOARDING
# =========================================================
with tab2:
    st.markdown('<div class="section-title">Client Onboarding Snapshot</div>', unsafe_allow_html=True)

    onboarding_df = pd.DataFrame({
        "Field": [
            "Advisor / MFD",
            "Branch / Location",
            "Client Name",
            "Client Mobile",
            "Age",
            "Retirement Age",
            "Dependents",
            "Declared Risk Profile",
            "Derived Investor Style"
        ],
        "Value": [
            advisor_name,
            branch_name,
            client_name,
            mobile_no,
            age,
            retirement_age,
            dependents,
            risk_profile,
            derived_risk_category
        ]
    })

    st.dataframe(onboarding_df, use_container_width=True, hide_index=True)

    st.info("Use this section as a first-meeting onboarding sheet before proposal discussion.")

# =========================================================
# TAB 3 - SIP PROPOSAL
# =========================================================
with tab3:
    st.markdown('<div class="section-title">Goal-Based SIP Proposal</div>', unsafe_allow_html=True)

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
    g1.metric("Current Cost", format_inr(current_goal_cost))
    g2.metric("Future Goal Value", format_inr(inflated_goal_value))
    g3.metric("Monthly SIP Needed", format_inr(goal_sip))
    g4.metric("Lumpsum Needed Today", format_inr(goal_lumpsum))

    st.markdown("---")

    if monthly_surplus > 0:
        sip_affordability = safe_ratio(goal_sip, monthly_surplus)
    else:
        sip_affordability = 0.0

    p1, p2 = st.columns(2)
    p1.metric("SIP as % of Monthly Surplus", f"{sip_affordability:.1f}%")
    p2.metric("Available Monthly Surplus", format_inr(max(monthly_surplus, 0)))

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
# TAB 4 - SIP VS LUMPSUM
# =========================================================
with tab4:
    st.markdown('<div class="section-title">SIP vs Lumpsum Comparison</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        target_corpus = st.number_input("Target Corpus (₹)", min_value=10000, max_value=500000000, value=5000000, step=50000)
    with col2:
        invest_years = st.slider("Investment Horizon (Years)", 1, 40, 15)
    with col3:
        invest_return = st.slider("Expected Return (%)", 1, 20, 12, key="compare_return")

    sip_needed = calculate_sip(target_corpus, invest_return, invest_years)
    lumpsum_needed = calculate_lumpsum_required(target_corpus, invest_return, invest_years)

    s1, s2, s3 = st.columns(3)
    s1.metric("Target Corpus", format_inr(target_corpus))
    s2.metric("Monthly SIP", format_inr(sip_needed))
    s3.metric("Lumpsum Today", format_inr(lumpsum_needed))

    year_range = list(range(1, invest_years + 1))
    sip_growth = [future_value_of_sip(sip_needed, invest_return, y) for y in year_range]
    lumpsum_growth = [future_value_of_lumpsum(lumpsum_needed, invest_return, y) for y in year_range]

    compare_df = pd.DataFrame({
        "Year": year_range,
        "SIP Future Value": sip_growth,
        "Lumpsum Future Value": lumpsum_growth
    })

    c1, c2 = st.columns(2)
    with c1:
        st.line_chart(compare_df.set_index("Year"), use_container_width=True)
    with c2:
        show_df = compare_df.copy()
        show_df["SIP Future Value"] = show_df["SIP Future Value"].apply(format_inr)
        show_df["Lumpsum Future Value"] = show_df["Lumpsum Future Value"].apply(format_inr)
        st.dataframe(show_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 5 - RETIREMENT PROPOSAL
# =========================================================
with tab5:
    st.markdown('<div class="section-title">Retirement Proposal</div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Years to Retirement", f"{years_to_retirement} Years")
    r2.metric("Expense at Retirement", format_inr(expense_at_retirement))
    r3.metric("Corpus Needed", format_inr(ret_corpus))
    r4.metric("Retirement SIP", format_inr(retirement_sip))

    st.markdown("---")

    ret_df = pd.DataFrame({
        "Metric": [
            "Current Age",
            "Retirement Age",
            "Life Expectancy",
            "Years to Retirement",
            "Years Post Retirement",
            "Current Assets",
            "Future Value of Existing Assets",
            "Additional Corpus Needed",
            "Retirement SIP Required"
        ],
        "Value": [
            age,
            retirement_age,
            life_expectancy,
            years_to_retirement,
            years_post_retirement,
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
        }, index=["Existing Asset Future Value", "New Corpus Required"])
        st.bar_chart(corpus_df, use_container_width=True)

# =========================================================
# TAB 6 - PROTECTION REVIEW
# =========================================================
with tab6:
    st.markdown('<div class="section-title">Protection Review (Insurance Need Analysis)</div>', unsafe_allow_html=True)

    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Recommended Life Cover", format_inr(recommended_life_cover))
    i2.metric("Existing Life Cover", format_inr(existing_life_cover))
    i3.metric("Life Cover Gap", format_inr(life_cover_gap))
    i4.metric("Emergency Fund Target", format_inr(recommended_emergency_fund))

    i5, i6, i7 = st.columns(3)
    i5.metric("Recommended Health Cover", format_inr(recommended_health_cover))
    i6.metric("Existing Health Cover", format_inr(existing_health_cover))
    i7.metric("Health Cover Gap", format_inr(health_cover_gap))

    protection_df = pd.DataFrame({
        "Protection Area": [
            "Life Insurance Need",
            "Existing Life Cover",
            "Life Cover Gap",
            "Health Cover Suggestion",
            "Existing Health Cover",
            "Health Cover Gap",
            "Emergency Fund Need"
        ],
        "Amount": [
            format_inr(recommended_life_cover),
            format_inr(existing_life_cover),
            format_inr(life_cover_gap),
            format_inr(recommended_health_cover),
            format_inr(existing_health_cover),
            format_inr(health_cover_gap),
            format_inr(recommended_emergency_fund)
        ]
    })
    st.dataframe(protection_df, use_container_width=True, hide_index=True)

    st.warning("Protection recommendations are indicative and must be aligned with policy features, underwriting, age, disclosures, exclusions and actual client suitability.")

# =========================================================
# TAB 7 - EMI & CASHFLOW
# =========================================================
with tab7:
    st.markdown('<div class="section-title">EMI & Cashflow Review</div>', unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)
    with e1:
        loan_amount = st.number_input("Loan Amount (₹)", min_value=10000, max_value=500000000, value=2500000, step=50000)
    with e2:
        loan_rate = st.slider("Loan Interest Rate (%)", 1, 20, 9)
    with e3:
        loan_years = st.slider("Loan Tenure (Years)", 1, 30, 10)

    emi, total_interest, total_payment = emi_calculator(loan_amount, loan_rate, loan_years)
    emi_to_income = safe_ratio(emi, monthly_income)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monthly EMI", format_inr(emi))
    m2.metric("Total Interest", format_inr(total_interest))
    m3.metric("Total Payment", format_inr(total_payment))
    m4.metric("EMI / Income Ratio", f"{emi_to_income:.1f}%")

    emi_df = pd.DataFrame({
        "Amount": [loan_amount, total_interest, total_payment]
    }, index=["Principal", "Total Interest", "Total Payment"])
    st.bar_chart(emi_df, use_container_width=True)

# =========================================================
# TAB 8 - TAX SNAPSHOT
# =========================================================
with tab8:
    st.markdown('<div class="section-title">Tax Snapshot (Indicative)</div>', unsafe_allow_html=True)

    t1, t2 = st.columns(2)
    with t1:
        tax_annual_income = st.number_input("Annual Gross Income (₹)", min_value=0, max_value=50000000, value=int(annual_income), step=50000)
    with t2:
        old_regime_deductions = st.number_input("Old Regime Eligible Deductions (₹)", min_value=0, max_value=5000000, value=150000, step=10000)

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
        "Taxable Income": [old_taxable, new_taxable],
        "Estimated Tax": [old_tax, new_tax]
    })

    c1, c2 = st.columns(2)
    with c1:
        show_df = tax_df.copy()
        show_df["Taxable Income"] = show_df["Taxable Income"].apply(format_inr)
        show_df["Estimated Tax"] = show_df["Estimated Tax"].apply(format_inr)
        st.dataframe(show_df, use_container_width=True, hide_index=True)
    with c2:
        st.bar_chart(tax_df[["Regime", "Estimated Tax"]].set_index("Regime"), use_container_width=True)

    st.success(f"Indicative tax difference: {format_inr(tax_saved)}")
    st.info("This is a basic planning snapshot only. Final tax should be validated with current rules and a qualified CA/tax professional.")

# =========================================================
# TAB 9 - MFD SUMMARY
# =========================================================
with tab9:
    st.markdown('<div class="section-title">MFD Proposal Summary (Client Meeting Ready)</div>', unsafe_allow_html=True)

    allocation_df = pd.DataFrame({
        "Asset Class": list(suggested_allocation.keys()),
        "Suggested Allocation (%)": list(suggested_allocation.values())
    })

    st.markdown("### 🎯 Suggested Allocation")
    st.dataframe(allocation_df, use_container_width=True, hide_index=True)

    recommendations = []

    if savings_ratio < 20:
        recommendations.append("Increase monthly savings ratio to 20%+ through disciplined SIP commitments.")
    else:
        recommendations.append("Current savings discipline is healthy. Continue SIP-led long-term investing.")

    if goal_sip > 0:
        recommendations.append(f"Start goal-based SIP of approximately {format_inr(goal_sip)} for {goal_name}.")
    if retirement_sip > 0:
        recommendations.append(f"Start/continue retirement SIP of approximately {format_inr(retirement_sip)}.")
    if life_cover_gap > 0:
        recommendations.append(f"Review life cover gap of around {format_inr(life_cover_gap)}.")
    if health_cover_gap > 0:
        recommendations.append(f"Review health cover enhancement of around {format_inr(health_cover_gap)}.")
    recommendations.append(f"Indicative tax comparison currently favors {best_regime}.")
    recommendations.append(f"Recommended investor positioning appears {derived_risk_category}, subject to suitability and risk profiling norms.")

    summary_text = f"""
FREEDOM MFD CLIENT PROPOSAL SUMMARY

Advisor / MFD: {advisor_name}
Branch / Location: {branch_name}

CLIENT DETAILS
- Client Name: {client_name}
- Mobile: {mobile_no}
- Age: {age}
- Retirement Age: {retirement_age}
- Dependents: {dependents}

RISK PROFILE
- Declared Risk Profile: {risk_profile}
- Derived Investor Style: {derived_risk_category}
- Risk Score: {risk_score}/100

CASH FLOW
- Monthly Income: {format_inr(monthly_income)}
- Monthly Expenses: {format_inr(monthly_expenses)}
- Monthly Surplus: {format_inr(monthly_surplus)}
- Savings Ratio: {savings_ratio:.1f}%
- Net Worth: {format_inr(net_worth)}

GOAL SIP PROPOSAL
- Goal: {goal_name}
- Current Goal Cost: {format_inr(current_goal_cost)}
- Future Goal Value: {format_inr(inflated_goal_value)}
- Monthly SIP Required: {format_inr(goal_sip)}
- Lumpsum Required Today: {format_inr(goal_lumpsum)}

RETIREMENT PROPOSAL
- Retirement Corpus Needed: {format_inr(ret_corpus)}
- Future Value of Existing Assets: {format_inr(future_existing_assets)}
- Additional Corpus Needed: {format_inr(additional_corpus_needed)}
- Retirement SIP Required: {format_inr(retirement_sip)}

PROTECTION REVIEW
- Recommended Life Cover: {format_inr(recommended_life_cover)}
- Existing Life Cover: {format_inr(existing_life_cover)}
- Life Cover Gap: {format_inr(life_cover_gap)}
- Recommended Health Cover: {format_inr(recommended_health_cover)}
- Existing Health Cover: {format_inr(existing_health_cover)}
- Health Cover Gap: {format_inr(health_cover_gap)}
- Emergency Fund Need: {format_inr(recommended_emergency_fund)}

EMI REVIEW
- Loan Amount: {format_inr(loan_amount)}
- EMI: {format_inr(emi)}
- EMI / Income Ratio: {emi_to_income:.1f}%

TAX SNAPSHOT
- Old Regime Tax: {format_inr(old_tax)}
- New Regime Tax: {format_inr(new_tax)}
- Better Regime (Indicative): {best_regime}

SUGGESTED ALLOCATION
- Equity: {suggested_allocation.get("Equity", 0)}%
- Debt: {suggested_allocation.get("Debt", 0)}%
- Gold: {suggested_allocation.get("Gold", 0)}%
- Cash: {suggested_allocation.get("Cash", 0)}%
"""

    st.text_area("Freedom Proposal Summary", summary_text, height=500)

    st.markdown("### ✅ Advisor Recommendations")
    for idx, rec in enumerate(recommendations, start=1):
        st.write(f"{idx}. {rec}")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    '<div class="footer-note">⚠️ Disclaimer: This tool is for educational and business presentation purposes only. It is not investment advice, insurance advice, tax advice, or a regulated recommendation. Final suitability must be based on full risk profiling, product suitability, disclosure standards, taxation, underwriting, and applicable regulatory requirements.</div>',
    unsafe_allow_html=True
)
