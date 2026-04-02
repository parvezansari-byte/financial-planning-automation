import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Freedom Financial Planner",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}
.sub-title {
    font-size: 16px;
    color: #475569;
    margin-bottom: 20px;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
    margin-top: 10px;
    margin-bottom: 10px;
}
.small-note {
    font-size: 13px;
    color: #64748b;
}
.footer-note {
    color: #64748b;
    font-size: 13px;
    margin-top: 15px;
}
.card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">💰 Freedom Financial Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Streamlit Cloud Safe | Single-file financial planning dashboard for Goal Planning, SIP, Retirement, Insurance & Net Worth</div>', unsafe_allow_html=True)

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def format_inr(value):
    try:
        return f"₹{float(value):,.0f}"
    except:
        return "₹0"

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

def future_value_with_inflation(current_value, inflation, years):
    return current_value * ((1 + inflation / 100) ** years)

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

def safe_ratio(a, b):
    if b == 0:
        return 0.0
    return (a / b) * 100

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
risk_profile = st.sidebar.selectbox("Risk Profile", ["Low", "Moderate", "High"])

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

current_total_invested = existing_savings + existing_investments
future_existing_assets = current_total_invested * ((1 + retirement_return_pre / 100) ** years_to_retirement) if years_to_retirement > 0 else current_total_invested
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
    existing_savings + existing_investments,
    annual_income
)

recommended_emergency_fund = monthly_expenses * 6
recommended_health_cover = max(500000.0, annual_income * 0.5)

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Dashboard",
    "🎯 Goal Planner",
    "🏖 Retirement",
    "🛡 Insurance",
    "📊 Net Worth",
    "🧾 Advisor Summary"
])

# =========================================================
# TAB 1 - DASHBOARD
# =========================================================
with tab1:
    st.markdown('<div class="section-title">Welcome Dashboard</div>', unsafe_allow_html=True)
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

    g1, g2, g3 = st.columns(3)
    g1.metric("Current Goal Cost", format_inr(current_goal_cost))
    g2.metric("Future Goal Value", format_inr(inflated_goal_value))
    g3.metric("Required Monthly SIP", format_inr(goal_sip))

    st.markdown("---")

    years_list = list(range(1, goal_years + 1))
    projected_values = [future_value_with_inflation(current_goal_cost, inflation_rate, y) for y in years_list]

    goal_growth_df = pd.DataFrame({
        "Year": years_list,
        "Projected Goal Value": projected_values
    })

    gx, gy = st.columns(2)

    with gx:
        st.markdown("### 📈 Goal Value Growth")
        chart_df = goal_growth_df.set_index("Year")
        st.line_chart(chart_df, use_container_width=True)

    with gy:
        st.markdown("### 📋 Goal Projection Table")
        display_goal_df = goal_growth_df.copy()
        display_goal_df["Projected Goal Value"] = display_goal_df["Projected Goal Value"].apply(format_inr)
        st.dataframe(display_goal_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB 3 - RETIREMENT
# =========================================================
with tab3:
    st.markdown('<div class="section-title">Retirement Planning</div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Years to Retirement", f"{years_to_retirement} Years")
    r2.metric("Expense at Retirement", format_inr(expense_at_retirement))
    r3.metric("Corpus Needed", format_inr(ret_corpus))
    r4.metric("Required Monthly SIP", format_inr(retirement_sip))

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
                format_inr(current_total_invested),
                format_inr(future_existing_assets),
                format_inr(additional_corpus_needed),
                format_inr(retirement_sip)
            ]
        })
        st.dataframe(retirement_summary, use_container_width=True, hide_index=True)

    with colr2:
        st.markdown("### 📊 Corpus Split")
        corpus_df = pd.DataFrame({
            "Amount": [future_existing_assets, additional_corpus_needed]
        }, index=["Future Existing Assets", "Additional Corpus Needed"])
        st.bar_chart(corpus_df, use_container_width=True)

# =========================================================
# TAB 4 - INSURANCE
# =========================================================
with tab4:
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
# TAB 5 - NET WORTH & ALLOCATION
# =========================================================
with tab5:
    st.markdown('<div class="section-title">Net Worth & Suggested Allocation</div>', unsafe_allow_html=True)

    allocation_map = {
        "Low": {"Equity": 30, "Debt": 50, "Gold": 10, "Cash": 10},
        "Moderate": {"Equity": 50, "Debt": 30, "Gold": 10, "Cash": 10},
        "High": {"Equity": 70, "Debt": 15, "Gold": 10, "Cash": 5}
    }

    alloc = allocation_map[risk_profile]

    coln1, coln2 = st.columns(2)

    with coln1:
        st.markdown("### 📈 Assets vs Liabilities")
        networth_df = pd.DataFrame({
            "Amount": [existing_savings, existing_investments, liabilities]
        }, index=["Savings", "Investments", "Liabilities"])
        st.bar_chart(networth_df, use_container_width=True)

        st.markdown("### 📋 Net Worth Summary")
        nw_df = pd.DataFrame({
            "Item": ["Savings", "Investments", "Liabilities", "Net Worth"],
            "Value": [
                format_inr(existing_savings),
                format_inr(existing_investments),
                format_inr(liabilities),
                format_inr(net_worth)
            ]
        })
        st.dataframe(nw_df, use_container_width=True, hide_index=True)

    with coln2:
        st.markdown(f"### 🎯 Suggested Allocation ({risk_profile})")
        alloc_df = pd.DataFrame({
            "Asset Class": list(alloc.keys()),
            "Allocation (%)": list(alloc.values())
        })
        st.dataframe(alloc_df, use_container_width=True, hide_index=True)

        alloc_chart_df = alloc_df.set_index("Asset Class")
        st.bar_chart(alloc_chart_df, use_container_width=True)

# =========================================================
# TAB 6 - ADVISOR SUMMARY
# =========================================================
with tab6:
    st.markdown('<div class="section-title">Advisor Summary (Client Ready)</div>', unsafe_allow_html=True)

    st.success("Use this section as a quick client discussion summary.")

    recommendation_lines = []

    if savings_ratio < 20:
        recommendation_lines.append("Increase monthly savings ratio to at least 20%+.")
    else:
        recommendation_lines.append("Current savings discipline is healthy. Continue consistent investing.")

    if recommended_emergency_fund > existing_savings:
        recommendation_lines.append("Build emergency reserve first before taking aggressive investment exposure.")
    else:
        recommendation_lines.append("Emergency reserve appears reasonable based on current monthly expenses.")

    if retirement_sip > 0:
        recommendation_lines.append(f"Start/continue retirement SIP of approximately {format_inr(retirement_sip)} per month.")
    else:
        recommendation_lines.append("Existing assets may already be sufficient for current retirement assumptions.")

    recommendation_lines.append(f"Review life cover requirement around {format_inr(recommended_life_cover)}.")
    recommendation_lines.append(f"Maintain or review health cover near {format_inr(recommended_health_cover)}.")
    recommendation_lines.append(f"Suggested asset allocation for {risk_profile} risk profile should be followed with product suitability checks.")

    summary_text = f"""
Client Name: {client_name}

1. Monthly Income: {format_inr(monthly_income)}
2. Monthly Expenses: {format_inr(monthly_expenses)}
3. Monthly Surplus: {format_inr(monthly_surplus)}
4. Savings Ratio: {savings_ratio:.1f}%
5. Net Worth: {format_inr(net_worth)}

Goal Planning:
- Example Goal Value Today: {format_inr(current_goal_cost)}
- Future Goal Value: {format_inr(inflated_goal_value)}
- Required Goal SIP: {format_inr(goal_sip)}

Retirement Planning:
- Years to Retirement: {years_to_retirement}
- Retirement Corpus Needed: {format_inr(ret_corpus)}
- Retirement SIP Needed: {format_inr(retirement_sip)}

Protection Planning:
- Recommended Life Cover: {format_inr(recommended_life_cover)}
- Recommended Health Cover: {format_inr(recommended_health_cover)}
- Emergency Fund Target: {format_inr(recommended_emergency_fund)}
"""

    st.markdown("### 📋 Client Snapshot")
    st.text_area("Client Summary", summary_text, height=320)

    st.markdown("### ✅ Advisor Recommendations")
    for idx, line in enumerate(recommendation_lines, start=1):
        st.write(f"{idx}. {line}")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    '<div class="footer-note">⚠️ Disclaimer: This tool is for educational and planning purposes only. It is not investment advice. Final financial planning should consider risk profiling, suitability, taxation, inflation, underwriting, product features, and regulatory compliance.</div>',
    unsafe_allow_html=True
)
