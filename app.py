import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Freedom Financial Planner",
    page_icon="💰",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 5px;
}
.sub-title {
    font-size: 16px;
    color: #475569;
    margin-bottom: 20px;
}
.footer-note {
    color: #64748b;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">💰 Freedom Financial Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Single-file financial planning dashboard for Goal Planning, SIP, Retirement, Insurance & Net Worth</div>', unsafe_allow_html=True)

# ---------------- HELPER FUNCTIONS ----------------
def format_inr(value):
    return f"₹{value:,.0f}"

def calculate_sip(future_value, annual_return, years):
    n = years * 12
    r = annual_return / 100 / 12
    if n <= 0:
        return 0
    if r == 0:
        return future_value / n
    sip = future_value * r / (((1 + r) ** n - 1))
    return sip

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

    return corpus, monthly_expense_at_retirement

def calculate_life_cover(monthly_expense, years_support, liabilities_amt, existing_assets, annual_income):
    family_expense_need = monthly_expense * 12 * years_support
    income_replacement = annual_income * 10
    return max(family_expense_need + liabilities_amt + income_replacement - existing_assets, 0)

# ---------------- SIDEBAR INPUTS ----------------
st.sidebar.header("👤 Client Profile")

client_name = st.sidebar.text_input("Client Name", "Freedom Client")
age = st.sidebar.number_input("Current Age", min_value=18, max_value=80, value=30)
retirement_age = st.sidebar.number_input("Retirement Age", min_value=40, max_value=80, value=60)

monthly_income = st.sidebar.number_input("Monthly Income (₹)", min_value=10000, max_value=5000000, value=80000, step=5000)
monthly_expenses = st.sidebar.number_input("Monthly Expenses (₹)", min_value=5000, max_value=5000000, value=45000, step=5000)

existing_savings = st.sidebar.number_input("Existing Savings (₹)", min_value=0, max_value=100000000, value=300000, step=10000)
existing_investments = st.sidebar.number_input("Existing Investments (₹)", min_value=0, max_value=100000000, value=500000, step=10000)
liabilities = st.sidebar.number_input("Total Liabilities / Loans (₹)", min_value=0, max_value=100000000, value=200000, step=10000)

dependents = st.sidebar.number_input("Number of Dependents", min_value=0, max_value=10, value=2)

risk_profile = st.sidebar.selectbox("Risk Profile", ["Low", "Moderate", "High"])

st.sidebar.markdown("---")
st.sidebar.header("📈 Assumptions")
goal_return = st.sidebar.slider("Expected Return for Goals (%)", 1, 20, 12)
inflation_rate = st.sidebar.slider("Inflation Rate (%)", 1, 12, 6)
retirement_return_pre = st.sidebar.slider("Pre-Retirement Return (%)", 1, 20, 12)
retirement_return_post = st.sidebar.slider("Post-Retirement Return (%)", 1, 12, 7)
life_expectancy = st.sidebar.slider("Life Expectancy", 65, 100, 85)

# ---------------- CORE CALCULATIONS ----------------
monthly_surplus = monthly_income - monthly_expenses
annual_income = monthly_income * 12

savings_ratio = (monthly_surplus / monthly_income * 100) if monthly_income > 0 else 0
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
additional_corpus_needed = max(ret_corpus - future_existing_assets, 0)
retirement_sip = calculate_sip(additional_corpus_needed, retirement_return_pre, years_to_retirement) if years_to_retirement > 0 else 0

recommended_life_cover = calculate_life_cover(
    monthly_expenses,
    15,
    liabilities,
    existing_savings + existing_investments,
    annual_income
)

recommended_emergency_fund = monthly_expenses * 6
recommended_health_cover = max(500000, annual_income * 0.5)

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard",
    "🎯 Goal Planner",
    "🏖 Retirement Planner",
    "🛡 Insurance Needs",
    "📊 Net Worth & Allocation"
])

# =========================================================
# TAB 1 - DASHBOARD
# =========================================================
with tab1:
    st.subheader(f"Welcome, {client_name}")

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

    colA, colB = st.columns([1.1, 1])

    with colA:
        st.markdown("### 📌 Financial Health Summary")

        if savings_ratio >= 30:
            savings_status = "Excellent"
        elif savings_ratio >= 20:
            savings_status = "Good"
        elif savings_ratio >= 10:
            savings_status = "Needs Improvement"
        else:
            savings_status = "Critical"

        summary_df = pd.DataFrame({
            "Metric": [
                "Savings Ratio",
                "Emergency Fund Need",
                "Retirement Corpus Need",
                "Recommended Life Cover",
                "Net Worth"
            ],
            "Value": [
                f"{savings_ratio:.1f}%",
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
            "Category": ["Income", "Expenses", "Surplus"],
            "Amount": [monthly_income, monthly_expenses, max(monthly_surplus, 0)]
        })

        fig_cash = px.bar(
            cashflow_df,
            x="Category",
            y="Amount",
            text="Amount",
            title="Monthly Cash Flow Overview"
        )
        fig_cash.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
        fig_cash.update_layout(height=420)
        st.plotly_chart(fig_cash, use_container_width=True)

# =========================================================
# TAB 2 - GOAL PLANNER
# =========================================================
with tab2:
    st.subheader("🎯 Goal-Based Financial Planning")

    col1, col2, col3 = st.columns(3)
    with col1:
        goal_name = st.selectbox("Select Goal", [
            "Emergency Fund",
            "Child Education",
            "Marriage",
            "House Purchase",
            "Car Purchase",
            "Vacation",
            "Custom Goal"
        ])
    with col2:
        current_goal_cost = st.number_input("Current Goal Cost (₹)", min_value=10000, max_value=100000000, value=1000000, step=50000)
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
    growth_values = [future_value_with_inflation(current_goal_cost, inflation_rate, y) for y in years_list]

    goal_growth_df = pd.DataFrame({
        "Year": years_list,
        "Projected Goal Value": growth_values
    })

    colx, coly = st.columns([1, 1])

    with colx:
        fig_goal = px.line(
            goal_growth_df,
            x="Year",
            y="Projected Goal Value",
            markers=True,
            title=f"{goal_name} Value Growth with Inflation"
        )
        st.plotly_chart(fig_goal, use_container_width=True)

    with coly:
        st.dataframe(goal_growth_df.style.format({"Projected Goal Value": "₹{:,.0f}"}), use_container_width=True)

# =========================================================
# TAB 3 - RETIREMENT PLANNER
# =========================================================
with tab3:
    st.subheader("🏖 Retirement Planning")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Years to Retirement", f"{years_to_retirement} Years")
    r2.metric("Expense at Retirement (Monthly)", format_inr(expense_at_retirement))
    r3.metric("Retirement Corpus Needed", format_inr(ret_corpus))
    r4.metric("Required Retirement SIP", format_inr(retirement_sip))

    st.markdown("---")

    colr1, colr2 = st.columns([1.1, 1])

    with colr1:
        retirement_summary = pd.DataFrame({
            "Retirement Metric": [
                "Current Age",
                "Retirement Age",
                "Years to Retirement",
                "Life Expectancy",
                "Years Post Retirement",
                "Current Assets",
                "Future Value of Existing Assets",
                "Additional Corpus Needed",
                "Monthly SIP Required"
            ],
            "Value": [
                age,
                retirement_age,
                years_to_retirement,
                life_expectancy,
                years_post_retirement,
                format_inr(current_total_invested),
                format_inr(future_existing_assets),
                format_inr(additional_corpus_needed),
                format_inr(retirement_sip)
            ]
        })

        st.dataframe(retirement_summary, use_container_width=True, hide_index=True)

    with colr2:
        corpus_df = pd.DataFrame({
            "Source": ["Future Existing Assets", "Additional Corpus Needed"],
            "Amount": [future_existing_assets, additional_corpus_needed]
        })

        fig_corpus = px.pie(
            corpus_df,
            names="Source",
            values="Amount",
            title="Retirement Corpus Composition"
        )
        st.plotly_chart(fig_corpus, use_container_width=True)

# =========================================================
# TAB 4 - INSURANCE NEEDS
# =========================================================
with tab4:
    st.subheader("🛡 Insurance & Protection Planning")

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

    st.info("📌 This is a planning estimate. Final insurance suitability should be checked as per actual policy, underwriting, age, liabilities, and existing cover.")

# =========================================================
# TAB 5 - NET WORTH & ALLOCATION
# =========================================================
with tab5:
    st.subheader("📊 Net Worth & Asset Allocation")

    allocation_map = {
        "Low": {"Equity": 30, "Debt": 50, "Gold": 10, "Cash": 10},
        "Moderate": {"Equity": 50, "Debt": 30, "Gold": 10, "Cash": 10},
        "High": {"Equity": 70, "Debt": 15, "Gold": 10, "Cash": 5}
    }

    alloc = allocation_map[risk_profile]

    coln1, coln2 = st.columns([1, 1])

    with coln1:
        networth_df = pd.DataFrame({
            "Category": ["Savings", "Investments", "Liabilities"],
            "Amount": [existing_savings, existing_investments, liabilities]
        })

        fig_net = px.bar(
            networth_df,
            x="Category",
            y="Amount",
            text="Amount",
            title="Assets vs Liabilities"
        )
        fig_net.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
        fig_net.update_layout(height=420)
        st.plotly_chart(fig_net, use_container_width=True)

    with coln2:
        alloc_df = pd.DataFrame({
            "Asset Class": list(alloc.keys()),
            "Allocation (%)": list(alloc.values())
        })

        fig_alloc = px.pie(
            alloc_df,
            names="Asset Class",
            values="Allocation (%)",
            title=f"Suggested Allocation ({risk_profile} Risk)"
        )
        st.plotly_chart(fig_alloc, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 Suggested Asset Allocation Table")
    st.dataframe(alloc_df, use_container_width=True, hide_index=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown(
    '<div class="footer-note">⚠️ Disclaimer: This tool is for educational and planning purposes only. It is not investment advice. Actual financial planning should consider risk profiling, product suitability, taxation, inflation, underwriting, and regulatory compliance.</div>',
    unsafe_allow_html=True
)
