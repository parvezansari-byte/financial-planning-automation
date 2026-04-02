import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Freedom Financial Planner Ultra Pro",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}
.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 2px;
}
.sub-title {
    font-size: 15px;
    color: #475569;
    margin-bottom: 16px;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
    margin-top: 8px;
    margin-bottom: 10px;
}
.card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px;
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
st.markdown('<div class="main-title">💰 Freedom Financial Planner — ULTRA PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Streamlit Cloud Safe | Goal Planning • SIP • Lumpsum • Retirement • Insurance • EMI • Tax • Risk Profile • Advisor Summary</div>', unsafe_allow_html=True)

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

    sip = future_value * r / denominator
    return max(sip, 0.0)

def future_value_of_sip(monthly_sip, annual_return, years):
    n = years * 12
    r = annual_return / 100 / 12

    if n <= 0:
        return 0.0
    if r == 0:
        return monthly_sip * n

    fv = monthly_sip * (((1 + r) ** n - 1) / r)
    return max(fv, 0.0)

def calculate_lumpsum_required(future_value, annual_return, years):
    if years <= 0:
        return future_value
    rate = annual_return / 100
    return future_value / ((1 + rate) ** years)

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
    age_score = 0
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

    savings_ratio = safe_ratio(monthly_surplus, monthly_income)
    savings_score = 0
    if savings_ratio >= 30:
        savings_score = 30
    elif savings_ratio >= 20:
        savings_score = 24
    elif savings_ratio >= 10:
        savings_score = 16
    else:
        savings_score = 8

    profile_score_map = {"Low": 15, "Moderate": 25, "High": 35}
    profile_score = profile_score_map.get(risk_profile, 20)

    total = age_score + savings_score + profile_score
    total = max(min(total, 100), 0)

    if total >= 75:
        category = "Aggressive"
    elif total >= 50:
        category = "Balanced"
    else:
        category = "Conservative"

    return total, category

# =========================================================
# SIDEBAR INPUTS
# =========================================================
st.sidebar.header("👤 Client Profile")

client_name = st.sidebar.text_input("Client Name", "Freedom Client")
age = st.sidebar.number_input("Current Age", min_value=18, max_value=80, value=30, step=1)
retirement_age = st.sidebar.number_input("Retirement Age", min_value=40, max_value=80, value=60, step=1)

monthly_income = st.sidebar.number_input("Monthly Income (₹)", min_value=10000, max_value=5000000, value=80000, step=5000)
monthly_expenses = st.sidebar.number_input("Monthly Expenses (₹)", min_value=5000, max_value=5000000, value=45000, step=5000)

existing_savings = st.sidebar.number_input("Existing Savings (₹)", min_value=0, max_value=100000000, value=300000, step=10000)
existing_investments = st.sidebar.number_input("Existing Investments (₹)", min_value=0, max_value=100000000, value=500000, step=10000)
liabilities = st.sidebar.number_input("Total Liabilities / Loans (₹)", min_value=0, max_value=100000000, value=200000, step=10000)

dependents = st.sidebar.number_input("Number of Dependents", min_value=0, max_value=10, value=2, step=1)
risk_profile = st.sidebar.selectbox("Declared Risk Profile", ["Low", "Moderate", "High"])

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
annual_expenses = monthly_expenses * 12

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

retirement_sip = calculate_sip(
    additional_corpus_needed,
    retirement_return_pre,
    years_to_retirement
) if years_to_retirement > 0 else 0.0

recommended_life_cover = calculate_life_cover(
    monthly_expenses,
    15,
    liabilities,
    current_total_assets,
    annual_income
)

recommended_emergency_fund = monthly_expenses * 6
recommended_health_cover = max(500000.0, annual_income * 0.5)

risk_score, derived_risk_category = risk_score_from_inputs(age, monthly_surplus, monthly_income, risk_profile)

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏠 Dashboard",
    "🎯 Goal Planner",
    "📈 SIP vs Lumpsum",
    "🏖 Retirement",
    "🛡 Insurance",
    "🏦 EMI Planner",
    "🧾 Tax Planner",
    "📋 Advisor Summary"
])

# =========================================================
# TAB 1 - DASHBOARD
# =========================================================
with tab1:
    st.markdown('<div class="section-title">Client Financial Dashboard</div>', unsafe_allow_html=True)
    st.write(f"Client: **{client_name}**")

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

    if savings_ratio >= 30:
        savings_status = "Excellent"
    elif savings_ratio >= 20:
        savings_status = "Good"
    elif savings_ratio >= 10:
        savings_status = "Needs Improvement"
    else:
        savings_status = "Critical"

    colA, colB = st.columns(2)

    with colA:
        st.markdown("### 📌 Financial Health Summary")
        summary_df = pd.DataFrame({
            "Metric": [
                "Savings Ratio",
                "Expense Ratio",
                "Emergency Fund Need",
                "Retirement Corpus Need",
                "Recommended Life Cover",
                "Net Worth"
            ],
            "Value": [
                f"{savings_ratio:.1f}%",
                f"{expense_ratio:.1f}%",
                format_inr(recommended_emergency_fund),
                format_inr(ret_corpus),
                format_inr(recommended_life_cover),
                format_inr(net_worth)
            ]
        })
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.info(f"📍 Savings Health Status: **{savings_status}**")

    with colB:
        st.markdown("### 📈 Monthly Cash Flow")
        cashflow_df = pd.DataFrame({
            "Amount": [monthly_income, monthly_expenses, max(monthly_surplus, 0)]
        }, index=["Income", "Expenses", "Surplus"])
        st.bar_chart(cashflow_df, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🎯 Risk Assessment")
    r1, r2 = st.columns(2)
    r1.metric("Risk Score", f"{risk_score}/100")
    r2.metric("Derived Risk Category", derived_risk_category)

# =========================================================
# TAB 2 - GOAL PLANNER
# =========================================================
with tab2:
    st.markdown('<div class="section-title">Goal-Based Planning</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        goal_name = st.selectbox(
            "Select Goal",
            [
                "Emergency Fund",
                "Child Education",
                "Marriage",
                "House Purchase",
                "Car Purchase",
                "Vacation",
                "Custom Goal"
            ]
        )

    with col2:
        current_goal_cost = st.number_input(
            "Current Goal Cost (₹)",
            min_value=10000,
            max_value=100000000,
            value=1000000,
            step=50000
        )

    with col3:
        goal_years = st.slider("Years to Goal", 1, 40, 10)

    inflated_goal_value = future_value_with_inflation(current_goal_cost, inflation_rate, goal_years)
    goal_sip = calculate_sip(inflated_goal_value, goal_return, goal_years)
    goal_lumpsum = calculate_lumpsum_required(inflated_goal_value, goal_return, goal_years)

    g1, g2, g3 = st.columns(3)
    g1.metric("Current Goal Cost", format_inr(current_goal_cost))
    g2.metric("Future Goal Value", format_inr(inflated_goal_value))
    g3.metric("Required SIP", format_inr(goal_sip))

    g4, g5 = st.columns(2)
    g4.metric("Required Lumpsum Today", format_inr(goal_lumpsum))
    g5.metric("Years to Goal", f"{goal_years} Years")

    st.markdown("---")

    years_list = list(range(1, goal_years + 1))
    projected_values = [future_value_with_inflation(current_goal_cost, inflation_rate, y) for y in years_list]

    goal_growth_df = pd.DataFrame({
        "Year": years_list,
        "Projected Goal Value": projected_values
    })

    gx, gy = st.columns(2)

    with gx:
        st.markdown("### 📈 Goal Growth with Inflation")
        chart_df = goal_growth_df.set_index("Year")
        st.line_chart(chart_df, use_container_width=True)

    with gy:
        st.markdown("### 📋 Projection Table")
        display_goal_df = goal_growth_df.copy()
        display_goal_df["Projected Goal Value"] = display_goal_df["Projected Goal Value"].apply(format_inr)
        st.dataframe(display_goal_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 3 - SIP VS LUMPSUM
# =========================================================
with tab3:
    st.markdown('<div class="section-title">SIP vs Lumpsum Comparison</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        target_corpus = st.number_input("Target Corpus (₹)", min_value=10000, max_value=500000000, value=5000000, step=50000)
    with col2:
        invest_years = st.slider("Investment Horizon (Years)", 1, 40, 15)
    with col3:
        invest_return = st.slider("Expected Return (%)", 1, 20, 12, key="sip_lump_return")

    sip_needed = calculate_sip(target_corpus, invest_return, invest_years)
    lumpsum_needed = calculate_lumpsum_required(target_corpus, invest_return, invest_years)

    s1, s2, s3 = st.columns(3)
    s1.metric("Target Corpus", format_inr(target_corpus))
    s2.metric("Monthly SIP Needed", format_inr(sip_needed))
    s3.metric("Lumpsum Needed Today", format_inr(lumpsum_needed))

    st.markdown("---")

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
        st.markdown("### 📈 Growth Comparison")
        chart_df = compare_df.set_index("Year")
        st.line_chart(chart_df, use_container_width=True)
    with c2:
        st.markdown("### 📋 Comparison Table")
        display_df = compare_df.copy()
        display_df["SIP Future Value"] = display_df["SIP Future Value"].apply(format_inr)
        display_df["Lumpsum Future Value"] = display_df["Lumpsum Future Value"].apply(format_inr)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 4 - RETIREMENT
# =========================================================
with tab4:
    st.markdown('<div class="section-title">Retirement Planning</div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Years to Retirement", f"{years_to_retirement} Years")
    r2.metric("Expense at Retirement", format_inr(expense_at_retirement))
    r3.metric("Corpus Needed", format_inr(ret_corpus))
    r4.metric("Retirement SIP", format_inr(retirement_sip))

    st.markdown("---")

    colr1, colr2 = st.columns(2)

    with colr1:
        retirement_summary = pd.DataFrame({
            "Metric": [
                "Current Age",
                "Retirement Age",
                "Life Expectancy",
                "Years to Retirement",
                "Years Post Retirement",
                "Current Total Assets",
                "Future Value of Existing Assets",
                "Additional Corpus Needed",
                "Required Monthly SIP"
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
        st.dataframe(retirement_summary, use_container_width=True, hide_index=True)

    with colr2:
        st.markdown("### 📊 Retirement Corpus Split")
        corpus_df = pd.DataFrame({
            "Amount": [future_existing_assets, additional_corpus_needed]
        }, index=["Future Existing Assets", "Additional Corpus Needed"])
        st.bar_chart(corpus_df, use_container_width=True)

# =========================================================
# TAB 5 - INSURANCE
# =========================================================
with tab5:
    st.markdown('<div class="section-title">Insurance & Protection Planning</div>', unsafe_allow_html=True)

    i1, i2, i3 = st.columns(3)
    i1.metric("Recommended Life Cover", format_inr(recommended_life_cover))
    i2.metric("Recommended Health Cover", format_inr(recommended_health_cover))
    i3.metric("Emergency Fund Target", format_inr(recommended_emergency_fund))

    st.markdown("---")

    insurance_df = pd.DataFrame({
        "Protection Area": [
            "Life Insurance Need",
            "Health Insurance Suggestion",
            "Emergency Fund Requirement",
            "Liability Protection",
            "Family Dependency Protection"
        ],
        "Recommended Amount / View": [
            format_inr(recommended_life_cover),
            format_inr(recommended_health_cover),
            format_inr(recommended_emergency_fund),
            format_inr(liabilities),
            f"{dependents} Dependents"
        ]
    })

    st.dataframe(insurance_df, use_container_width=True, hide_index=True)

    st.warning("This is a planning estimate only. Final suitability depends on actual policy terms, underwriting, age, liabilities, existing cover and client profile.")

# =========================================================
# TAB 6 - EMI PLANNER
# =========================================================
with tab6:
    st.markdown('<div class="section-title">EMI Planner</div>', unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)
    with e1:
        loan_amount = st.number_input("Loan Amount (₹)", min_value=10000, max_value=500000000, value=2500000, step=50000)
    with e2:
        loan_rate = st.slider("Loan Interest Rate (%)", 1, 20, 9)
    with e3:
        loan_years = st.slider("Loan Tenure (Years)", 1, 30, 10)

    emi, total_interest, total_payment = emi_calculator(loan_amount, loan_rate, loan_years)

    em1, em2, em3 = st.columns(3)
    em1.metric("Monthly EMI", format_inr(emi))
    em2.metric("Total Interest", format_inr(total_interest))
    em3.metric("Total Payment", format_inr(total_payment))

    st.markdown("---")

    emi_df = pd.DataFrame({
        "Value": [loan_amount, total_interest, total_payment]
    }, index=["Principal", "Total Interest", "Total Payment"])
    st.bar_chart(emi_df, use_container_width=True)

# =========================================================
# TAB 7 - TAX PLANNER
# =========================================================
with tab7:
    st.markdown('<div class="section-title">Basic Tax Planner (Indicative)</div>', unsafe_allow_html=True)

    t1, t2 = st.columns(2)
    with t1:
        tax_annual_income = st.number_input("Annual Gross Income (₹)", min_value=0, max_value=50000000, value=int(annual_income), step=50000)
    with t2:
        old_regime_deductions = st.number_input("Eligible Deductions for Old Regime (₹)", min_value=0, max_value=5000000, value=150000, step=10000)

    old_taxable, old_tax = tax_regime_old(tax_annual_income, old_regime_deductions)
    new_taxable, new_tax = tax_regime_new(tax_annual_income)

    best_regime = "Old Regime" if old_tax < new_tax else "New Regime"
    tax_saved = abs(old_tax - new_tax)

    tx1, tx2, tx3 = st.columns(3)
    tx1.metric("Old Regime Tax", format_inr(old_tax))
    tx2.metric("New Regime Tax", format_inr(new_tax))
    tx3.metric("Better Option", best_regime)

    st.markdown("---")

    tax_df = pd.DataFrame({
        "Regime": ["Old Regime", "New Regime"],
        "Taxable Income": [old_taxable, new_taxable],
        "Estimated Tax": [old_tax, new_tax]
    })

    display_tax_df = tax_df.copy()
    display_tax_df["Taxable Income"] = display_tax_df["Taxable Income"].apply(format_inr)
    display_tax_df["Estimated Tax"] = display_tax_df["Estimated Tax"].apply(format_inr)

    c1, c2 = st.columns(2)
    with c1:
        st.dataframe(display_tax_df, use_container_width=True, hide_index=True)
        st.success(f"Indicative tax difference between regimes: {format_inr(tax_saved)}")
    with c2:
        tax_chart_df = tax_df[["Regime", "Estimated Tax"]].set_index("Regime")
        st.bar_chart(tax_chart_df, use_container_width=True)

    st.info("This is a simplified estimator for planning use only. Final tax should be verified with latest rules and a qualified tax advisor/CA.")

# =========================================================
# TAB 8 - ADVISOR SUMMARY
# =========================================================
with tab8:
    st.markdown('<div class="section-title">Advisor Summary (Client Ready)</div>', unsafe_allow_html=True)

    recommendations = []

    if savings_ratio < 20:
        recommendations.append("Increase monthly savings ratio to at least 20%+ for stronger long-term planning.")
    else:
        recommendations.append("Savings ratio is healthy. Continue disciplined investing.")

    if existing_savings < recommended_emergency_fund:
        recommendations.append("Build emergency fund before taking aggressive market exposure.")
    else:
        recommendations.append("Emergency reserve is reasonably aligned with current expense level.")

    if retirement_sip > 0:
        recommendations.append(f"Start or continue retirement SIP of around {format_inr(retirement_sip)} per month.")
    else:
        recommendations.append("Existing assets may be sufficient for current retirement assumptions.")

    recommendations.append(f"Review life cover need near {format_inr(recommended_life_cover)}.")
    recommendations.append(f"Maintain or enhance health cover near {format_inr(recommended_health_cover)}.")
    recommendations.append(f"Use {best_regime} as currently better under this basic tax estimate.")
    recommendations.append(f"Derived investor style appears {derived_risk_category}. Ensure product suitability before execution.")

    st.success("Use this summary during client discussion or internal advisory review.")

    summary_text = f"""
Client Name: {client_name}

BASIC PROFILE
- Age: {age}
- Retirement Age: {retirement_age}
- Dependents: {dependents}
- Declared Risk Profile: {risk_profile}
- Derived Risk Category: {derived_risk_category}
- Risk Score: {risk_score}/100

CASH FLOW
- Monthly Income: {format_inr(monthly_income)}
- Monthly Expenses: {format_inr(monthly_expenses)}
- Monthly Surplus: {format_inr(monthly_surplus)}
- Savings Ratio: {savings_ratio:.1f}%
- Net Worth: {format_inr(net_worth)}

GOAL PLANNING
- Selected Goal: {goal_name}
- Current Goal Cost: {format_inr(current_goal_cost)}
- Future Goal Value: {format_inr(inflated_goal_value)}
- Goal SIP Required: {format_inr(goal_sip)}
- Goal Lumpsum Required Today: {format_inr(goal_lumpsum)}

RETIREMENT
- Years to Retirement: {years_to_retirement}
- Retirement Corpus Needed: {format_inr(ret_corpus)}
- Future Value of Existing Assets: {format_inr(future_existing_assets)}
- Additional Corpus Needed: {format_inr(additional_corpus_needed)}
- Retirement SIP Required: {format_inr(retirement_sip)}

PROTECTION
- Recommended Life Cover: {format_inr(recommended_life_cover)}
- Recommended Health Cover: {format_inr(recommended_health_cover)}
- Emergency Fund Target: {format_inr(recommended_emergency_fund)}

EMI
- Loan Amount: {format_inr(loan_amount)}
- EMI: {format_inr(emi)}
- Total Interest: {format_inr(total_interest)}

TAX (BASIC)
- Old Regime Tax: {format_inr(old_tax)}
- New Regime Tax: {format_inr(new_tax)}
- Better Regime (Indicative): {best_regime}
"""

    st.markdown("### 📋 Client Discussion Summary")
    st.text_area("Advisor Summary Text", summary_text, height=420)

    st.markdown("### ✅ Key Recommendations")
    for idx, rec in enumerate(recommendations, start=1):
        st.write(f"{idx}. {rec}")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    '<div class="footer-note">⚠️ Disclaimer: This tool is for educational and planning purposes only. It is not investment advice, insurance advice, tax advice, or a regulated recommendation. Final financial planning should consider risk profiling, product suitability, taxation, inflation, underwriting, current regulations, and client-specific facts.</div>',
    unsafe_allow_html=True
)
