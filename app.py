import streamlit as st
import pandas as pd
import numpy as np

# =====================================================
# FREEDOM | FINAL SAFE BUILD
# =====================================================
st.set_page_config(
    page_title="Freedom",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# SESSION STATE
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "home"


def go(page_name):
    st.session_state.page = page_name


def back_button():
    st.button("⬅ Back to Home", on_click=lambda: go("home"), use_container_width=True)


# =====================================================
# THEME
# =====================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background:
        radial-gradient(circle at 85% 10%, rgba(212,175,55,0.18) 0%, rgba(212,175,55,0.02) 20%, transparent 42%),
        radial-gradient(circle at 10% 90%, rgba(120,85,35,0.10) 0%, rgba(120,85,35,0.02) 24%, transparent 46%),
        linear-gradient(135deg, #fcf8ef 0%, #f6ecd6 28%, #ecd8ab 60%, #dfbf79 100%);
    color: #2B1E12;
    background-attachment: fixed;
}
.main .block-container {
    max-width: 95%;
    padding-top: 1.1rem;
    padding-bottom: 2rem;
    padding-left: 1rem;
    padding-right: 1rem;
    background: rgba(255, 250, 240, 0.55);
    border: 1px solid rgba(120, 85, 35, 0.10);
    border-radius: 24px;
    backdrop-filter: blur(6px);
    box-shadow: 0 12px 35px rgba(120, 85, 35, 0.08);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f7edd8 0%, #efddb7 45%, #e4c889 100%);
    border-right: 2px solid #C58B39;
}
section[data-testid="stSidebar"] * { color: #2B1E12 !important; }
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background: linear-gradient(180deg, #fffdf8 0%, #f9f0dc 100%) !important;
    color: #2B1E12 !important;
    border: 1px solid #B8860B !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}
.main-title {
    background: linear-gradient(90deg, #5C3A0A 0%, #8B6B2E 30%, #C58B39 65%, #E5C47A 100%);
    padding: 24px;
    border-radius: 20px;
    text-align: center;
    color: #FFF8ED;
    font-size: 54px;
    font-weight: 800;
    font-family: 'Playfair Display', serif;
    border: 2px solid #D4AF37;
    box-shadow: 0 12px 30px rgba(92, 58, 10, 0.18);
    margin-bottom: 8px;
}
.sub-title {
    background: linear-gradient(90deg, #7B5B20 0%, #B8860B 55%, #D4AF37 100%);
    color: #FFF8ED;
    text-align: center;
    padding: 10px;
    font-size: 18px;
    font-weight: 700;
    border-radius: 12px;
    margin-bottom: 14px;
}
.banner, .panel, .kpi-card {
    background: linear-gradient(180deg, rgba(255,250,240,0.98) 0%, rgba(250,240,220,0.97) 100%);
    border: 1px solid rgba(120, 85, 35, 0.14);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 8px 18px rgba(92, 58, 10, 0.06);
    margin-bottom: 12px;
}
.section-box {
    border: 1px solid rgba(120, 85, 35, 0.14);
    background: linear-gradient(180deg, rgba(255,250,240,0.92) 0%, rgba(250,240,220,0.92) 100%);
    margin-bottom: 14px;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 8px 22px rgba(92, 58, 10, 0.08);
}
.section-header {
    background: linear-gradient(90deg, #8B6B2E 0%, #C58B39 58%, #E5C47A 100%);
    color: #FFF8ED;
    text-align: center;
    font-weight: 800;
    font-size: 22px;
    font-family: 'Playfair Display', serif;
    padding: 12px;
}
.kpi-title { color: #6B4E16; font-size: 15px; font-weight: 700; margin-bottom: 6px; }
.kpi-value { color: #7B5B20; font-size: 24px; font-weight: 800; }
.stButton > button {
    width: 100%; min-height: 54px; border-radius: 14px; border: 1px solid #C58B39;
    background: linear-gradient(145deg, #FFF8ED 0%, #F8E7C5 55%, #E8C989 100%);
    color: #5C3A0A !important; font-weight: 800;
}
[data-testid="metric-container"], [data-testid="stAlert"] {
    background: linear-gradient(180deg, #FFF8ED 0%, #F7E9D0 100%) !important;
    border: 1px solid rgba(120, 85, 35, 0.14) !important;
    border-radius: 14px !important;
}
thead tr th {
    background: linear-gradient(90deg, #8B6B2E 0%, #C58B39 60%, #E5C47A 100%) !important;
    color: #FFF8ED !important;
}
tbody tr td { background: #FFF8ED !important; color: #2B1E12 !important; }
header[data-testid="stHeader"] { background: rgba(0,0,0,0); }
footer { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# HELPERS
# =====================================================
def fmt(x):
    try:
        return f"₹ {x:,.0f}"
    except Exception:
        return "₹ 0"


def future_value(pv, rate, years):
    return pv * ((1 + rate) ** max(years, 0))


def monthly_sip_required(target, annual_rate, years):
    months = int(max(years, 0) * 12)
    if months <= 0:
        return 0
    r = annual_rate / 12
    if r <= 0:
        return target / months
    factor = (((1 + r) ** months - 1) / r) * (1 + r)
    return target / factor if factor > 0 else 0


def lumpsum_required(target, annual_return, years):
    if years <= 0:
        return target
    return target / ((1 + annual_return) ** years)


def emi_calculator(principal, annual_rate, years):
    r = annual_rate / 12
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return principal / n
    return principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)


def kpi_row(items):
    cols = st.columns(len(items))
    for i, (label, value) in enumerate(items):
        with cols[i]:
            st.markdown(
                f"""
                <div class=\"kpi-card\">
                    <div class=\"kpi-title\">{label}</div>
                    <div class=\"kpi-value\">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def advisor_note(title, lines):
    st.markdown('<div class="section-box"><div class="section-header">Advisor Product Notes</div></div>', unsafe_allow_html=True)
    st.markdown(f"**{title}**")
    for line in lines:
        st.write(f"• {line}")


def fetch_scheme_master_amfi():
    try:
        import requests
        resp = requests.get("https://api.mfapi.in/mf", timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                if "schemeCode" in df.columns and "schemeName" in df.columns:
                    df = df.rename(columns={"schemeCode": "Scheme Code", "schemeName": "Scheme Name"})
                    return df, "LIVE"
        return pd.DataFrame(), "FAILED"
    except Exception:
        return pd.DataFrame(), "ERROR"


def fetch_live_nav_amfi(scheme_code):
    try:
        import requests
        resp = requests.get(f"https://api.mfapi.in/mf/{scheme_code}", timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            nav_block = data.get("data", [])
            if nav_block and isinstance(nav_block, list):
                latest = nav_block[0]
                nav_val = float(latest.get("nav", 0)) if latest.get("nav") else None
                nav_date = latest.get("date", "N/A")
                return {"nav": nav_val, "date": nav_date}
        return {"nav": None, "date": "N/A"}
    except Exception:
        return {"nav": None, "date": "N/A"}


# =====================================================
# HEADER
# =====================================================
st.markdown('<div class="main-title">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Mutual Fund Product & Research Analyst Platform</div>', unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.markdown("## Client Profile")
client_name = st.sidebar.text_input("Client Name", "Aditya")
advisor_name = st.sidebar.text_input("Advisor Name", "Parvez")
current_age = st.sidebar.number_input("Current Age", 18, 80, 30)
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 20.0, 6.0) / 100
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 25.0, 12.0) / 100

st.markdown(
    f"""
<div class="banner">
    <b>Prepared for:</b> {client_name} &nbsp;&nbsp; | &nbsp;&nbsp;
    <b>Advisor:</b> {advisor_name} &nbsp;&nbsp; | &nbsp;&nbsp;
    <b>Platform:</b> Product Research & Advisory Interface
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Navigation")
nav_items = [
    ("🏠 Home Dashboard", "home"),
    ("📈 SIP & Lumpsum", "sip"),
    ("💸 SWP Planner", "swp"),
    ("👨‍👩‍👧 Children Planning", "children"),
    ("🛡️ Retirement Planner", "retirement"),
    ("🏦 Fund Research Dashboard", "fund_suggestion"),
    ("💼 Net Worth Dashboard", "networth"),
    ("📊 EMI vs SIP", "emi_vs_sip"),
]
for label, page in nav_items:
    if st.sidebar.button(label, use_container_width=True):
        go(page)

# =====================================================
# HOME
# =====================================================
if st.session_state.page == "home":
    st.markdown('<div class="section-box"><div class="section-header">Freedom Dashboard</div></div>', unsafe_allow_html=True)
    readiness = min(100, max(50, round((expected_return * 100) * 5 + (12 - inflation * 100) * 3)))
    growth_mode = "Growth Strategy" if expected_return >= 0.12 else "Capital Protection"

    kpi_row([
        ("Client", client_name),
        ("Advisor", advisor_name),
        ("Inflation", f"{inflation*100:.1f}%"),
        ("Expected Return", f"{expected_return*100:.1f}%"),
    ])

    st.markdown(
        """
        <div class="panel">
            <div style="font-size:26px; font-weight:800; margin-bottom:6px;">FINAL PRODUCT & ANALYST EDITION</div>
            <div style="font-size:14px; line-height:1.65;">
                Professional mutual fund distributor platform with planning calculators, product research, scheme screening, and client suitability support.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpi_row([
        ("Modules", "8"),
        ("Readiness", f"{readiness}%"),
        ("Mode", growth_mode),
    ])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Planning Tools")
        st.button("SIP & Lumpsum Calculator", on_click=lambda: go("sip"), use_container_width=True)
        st.button("SWP Planner", on_click=lambda: go("swp"), use_container_width=True)
        st.button("Children Planning", on_click=lambda: go("children"), use_container_width=True)
        st.button("Retirement Planner", on_click=lambda: go("retirement"), use_container_width=True)
    with c2:
        st.markdown("### Advisory & Research")
        st.button("Fund Research Dashboard", on_click=lambda: go("fund_suggestion"), use_container_width=True)
        st.button("Net Worth Dashboard", on_click=lambda: go("networth"), use_container_width=True)
        st.button("EMI vs SIP Calculator", on_click=lambda: go("emi_vs_sip"), use_container_width=True)

# =====================================================
# SIP
# =====================================================
if st.session_state.page == "sip":
    back_button()
    st.markdown('<div class="section-box"><div class="section-header">SIP & Lumpsum Calculator</div></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["SIP Planner", "Lumpsum Planner"])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            monthly_sip = st.number_input("Monthly SIP (₹)", 0, 100000000, 5000)
        with c2:
            years = st.number_input("Investment Period (Years)", 1, 60, 20)
        with c3:
            sip_return = st.number_input("Expected Return (%)", 0.0, 30.0, float(expected_return * 100)) / 100
        with c4:
            step_up = st.number_input("Annual Step-up (%)", 0.0, 50.0, 10.0) / 100

        corpus = 0.0
        total_invested = 0.0
        sip_amt = monthly_sip
        for _y in range(years):
            for _m in range(12):
                corpus = corpus * (1 + sip_return / 12) + sip_amt
                total_invested += sip_amt
            sip_amt *= (1 + step_up)

        kpi_row([
            ("Invested", fmt(total_invested)),
            ("Final Value", fmt(corpus)),
            ("Absolute Gain", f"{((corpus-total_invested)/total_invested*100 if total_invested>0 else 0):.2f}%"),
        ])

    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1:
            lumpsum_amt = st.number_input("Investment Amount (₹)", 0, 1000000000, 1000000)
        with c2:
            lumpsum_return = st.number_input("Expected Return for Lumpsum (%)", 0.0, 30.0, 12.0) / 100
        with c3:
            lumpsum_years = st.number_input("Investment Period in Years", 1, 60, 7)
        final_lumpsum = future_value(lumpsum_amt, lumpsum_return, lumpsum_years)
        kpi_row([
            ("Invested", fmt(lumpsum_amt)),
            ("Final Value", fmt(final_lumpsum)),
            ("Absolute Gain", f"{((final_lumpsum-lumpsum_amt)/lumpsum_amt*100 if lumpsum_amt>0 else 0):.2f}%"),
        ])

# =====================================================
# SWP
# =====================================================
if st.session_state.page == "swp":
    back_button()
    st.markdown('<div class="section-box"><div class="section-header">SWP Planner</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        initial_corpus = st.number_input("Current Corpus (₹)", 0, 1000000000, 10000000)
    with c2:
        yearly_withdrawal = st.number_input("Withdrawal Per Year (₹)", 0, 100000000, 1200000)
    with c3:
        withdrawal_return = st.number_input("Expected Return in Withdrawal Phase (%)", 0.0, 25.0, 10.0) / 100

    swr = (yearly_withdrawal / initial_corpus * 100) if initial_corpus > 0 else 0
    indicative_years = int(initial_corpus / yearly_withdrawal) if yearly_withdrawal > 0 else 0
    kpi_row([
        ("Corpus", fmt(initial_corpus)),
        ("Yearly SWP", fmt(yearly_withdrawal)),
        ("SWR", f"{swr:.2f}%"),
        ("Indicative Years", str(indicative_years)),
    ])

# =====================================================
# CHILDREN
# =====================================================
if st.session_state.page == "children":
    back_button()
    st.markdown('<div class="section-box"><div class="section-header">Future Planning for Children</div></div>', unsafe_allow_html=True)
    child_age = st.number_input("Child Age", 0, 25, 5)
    goal_age = st.number_input("Goal Age", child_age, 35, 18)
    goal_cost = st.number_input("Goal Cost Today (₹)", 0, 100000000, 2000000)
    years_left = max(goal_age - child_age, 0)
    future_cost = future_value(goal_cost, inflation, years_left)
    sip_req = monthly_sip_required(future_cost, expected_return, years_left)
    lump_req = lumpsum_required(future_cost, expected_return, years_left)
    kpi_row([
        ("Future Cost", fmt(future_cost)),
        ("Monthly SIP Required", fmt(sip_req)),
        ("Lumpsum Today", fmt(lump_req)),
    ])

# =====================================================
# RETIREMENT
# =====================================================
if st.session_state.page == "retirement":
    back_button()
    st.markdown('<div class="section-box"><div class="section-header">Retirement Planner</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        my_age = st.number_input("Current Age", 18, 80, current_age)
    with c2:
        retire_age = st.number_input("Retirement Age", my_age + 1, 80, 60)
    with c3:
        monthly_exp = st.number_input("Monthly Expense Today (₹)", 0, 100000000, 60000)

    years_to_ret = retire_age - my_age
    annual_exp_today = monthly_exp * 12
    expense_at_ret = annual_exp_today * ((1 + inflation) ** years_to_ret)
    required_corpus = expense_at_ret * 20
    req_sip = monthly_sip_required(required_corpus, expected_return, years_to_ret)
    kpi_row([
        ("Expense at Retirement", fmt(expense_at_ret)),
        ("Target Corpus", fmt(required_corpus)),
        ("Required SIP", fmt(req_sip)),
    ])

# =====================================================
# FUND RESEARCH
# =====================================================
if st.session_state.page == "fund_suggestion":
    back_button()
    st.markdown('<div class="section-box"><div class="section-header">LIVE Mutual Fund Product Research Dashboard</div></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        risk_profile = st.selectbox("Client Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    with c2:
        investment_horizon = st.selectbox("Investment Horizon", ["1-3 Years", "3-5 Years", "5+ Years"])
    with c3:
        sort_by = st.selectbox("Sort Funds By", ["3Y CAGR %", "5Y CAGR %", "1Y %", "AUM (₹ Cr)", "Sharpe", "Latest NAV"])
    with c4:
        nav_source = st.selectbox("NAV Source Mode", ["Static Demo Data", "AMFI/MFAPI Live Fetch"])

    search_text = st.text_input("Search Fund / AMC / Category / Scheme Code", "")

    fund_data = [
        ["120503", "Tata Multi Asset Opportunities Fund", "Tata", "Multi Asset", 18.2, 16.1, 15.4, "Moderate", 0.72, 3800, 11.8, 0.92, 24.87, "2026-03-14", "Diversified core allocation"],
        ["120828", "ICICI Prudential Multi-Asset Fund", "ICICI Prudential", "Multi Asset", 17.4, 15.3, 14.8, "Moderate", 0.88, 42000, 10.9, 0.89, 78.14, "2026-03-14", "Balanced all-weather allocation"],
        ["100046", "HDFC Balanced Advantage Fund", "HDFC", "Dynamic Hybrid", 15.1, 14.2, 13.0, "Moderate", 1.03, 95000, 8.4, 0.76, 512.63, "2026-03-14", "Volatility management"],
        ["122639", "Parag Parikh Flexi Cap Fund", "PPFAS", "Flexi Cap", 20.5, 18.9, 21.2, "Moderate-High", 0.78, 78000, 14.2, 1.04, 82.35, "2026-03-14", "Long-term core growth"],
        ["120323", "Kotak Equity Opportunities Fund", "Kotak", "Large & Mid Cap", 22.0, 19.1, 20.0, "High", 0.74, 21000, 15.8, 1.08, 239.12, "2026-03-14", "Aggressive growth satellite"],
        ["103566", "SBI Short Term Debt Fund", "SBI", "Short Duration Debt", 7.4, 6.9, 6.8, "Low", 0.42, 14000, 2.8, 0.22, 39.84, "2026-03-14", "Stability / short-term parking"],
    ]
    funds_df = pd.DataFrame(
        fund_data,
        columns=["Scheme Code", "Fund Name", "AMC", "Category", "1Y %", "3Y CAGR %", "5Y CAGR %", "Risk", "Expense Ratio %", "AUM (₹ Cr)", "Std Dev %", "Sharpe", "Latest NAV", "NAV Date", "Advisor Role"],
    )

    col_a, col_b = st.columns(2)
    with col_a:
        refresh_live = st.button("🔄 Refresh Live NAV from AMFI/MFAPI", use_container_width=True)
    with col_b:
        import_master = st.button("📥 Import AMFI Scheme Master", use_container_width=True)

    if import_master:
        imported_master_df, import_status = fetch_scheme_master_amfi()
        st.info(f"AMFI Scheme Master Import Status: {import_status}")
        if not imported_master_df.empty:
            st.dataframe(imported_master_df[["Scheme Code", "Scheme Name"]].head(25), use_container_width=True, hide_index=True)

    if nav_source == "AMFI/MFAPI Live Fetch" and refresh_live:
        live_navs = []
        live_dates = []
        for _, row in funds_df.iterrows():
            res = fetch_live_nav_amfi(row["Scheme Code"])
            live_navs.append(res["nav"] if res["nav"] is not None else row["Latest NAV"])
            live_dates.append(res["date"] if res["date"] != "N/A" else row["NAV Date"])
        funds_df["Latest NAV"] = live_navs
        funds_df["NAV Date"] = live_dates
        st.success("Live NAV refresh attempted. Static fallback retained where API data is unavailable.")

    if search_text.strip():
        q = search_text.strip().lower()
        funds_df = funds_df[
            funds_df["Fund Name"].str.lower().str.contains(q)
            | funds_df["AMC"].str.lower().str.contains(q)
            | funds_df["Category"].str.lower().str.contains(q)
            | funds_df["Scheme Code"].astype(str).str.lower().str.contains(q)
        ]

    if risk_profile == "Conservative":
        filtered = funds_df[funds_df["Category"].isin(["Multi Asset", "Dynamic Hybrid", "Short Duration Debt"])]
        model_text = "40% Multi Asset | 35% Dynamic Hybrid | 25% Short Duration Debt"
    elif risk_profile == "Moderate":
        filtered = funds_df[funds_df["Category"].isin(["Multi Asset", "Dynamic Hybrid", "Flexi Cap"])]
        model_text = "35% Multi Asset | 25% Dynamic Hybrid | 40% Flexi Cap"
    else:
        filtered = funds_df[funds_df["Category"].isin(["Flexi Cap", "Large & Mid Cap", "Multi Asset"])]
        model_text = "45% Flexi Cap | 35% Large & Mid Cap | 20% Multi Asset"

    display_df = filtered.copy() if not filtered.empty else funds_df.copy()

    if display_df.empty:
        st.warning("No funds matched the current filters. Please widen the search.")
    else:
        display_df = display_df.sort_values(by=sort_by, ascending=False)
        top_fund = display_df.iloc[0]
        kpi_row([
            ("Top Fund", top_fund["Fund Name"][:18] + "..." if len(top_fund["Fund Name"]) > 18 else top_fund["Fund Name"]),
            ("Latest NAV", f"₹ {top_fund['Latest NAV']:.2f}"),
            ("NAV Date", str(top_fund["NAV Date"])),
            ("Horizon", investment_horizon),
        ])

        st.markdown(
            f"""
            <div class="panel">
                <b>Model Allocation:</b> {model_text}<br>
                <b>Top Research Pick:</b> {top_fund['Fund Name']} ({top_fund['Category']})<br>
                <b>Latest NAV:</b> ₹ {top_fund['Latest NAV']:.2f} as of {top_fund['NAV Date']}<br>
                <b>Platform Mode:</b> Product + Analyst workflow for mutual fund distributors.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### AMC Summary")
        amc_summary = display_df.groupby("AMC").agg(
            Fund_Count=("Fund Name", "count"),
            Avg_3Y_CAGR=("3Y CAGR %", "mean"),
            Avg_5Y_CAGR=("5Y CAGR %", "mean"),
            Total_AUM=("AUM (₹ Cr)", "sum"),
        ).reset_index()
        st.dataframe(amc_summary, use_container_width=True, hide_index=True)

        st.markdown("### Mutual Fund Research Table")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        advisor_note("Fund Research Notes", [
            "This is a safe build with stable Streamlit rendering.",
            "Live NAV fetch includes fallback if API is unavailable.",
            "Built for mutual fund distributor product selection workflow.",
        ])

# =====================================================
# NET WORTH
# =====================================================
if st.session_state.page == "networth":
    back_button()
    st.markdown('<div class="section-box"><div class="section-header">Net Worth Dashboard</div></div>', unsafe_allow_html=True)
    mf = st.number_input("Mutual Funds (₹)", 0, 1000000000, 2000000)
    equity = st.number_input("Direct Equity (₹)", 0, 1000000000, 1000000)
    real_estate = st.number_input("Real Estate (₹)", 0, 10000000000, 5000000)
    cash = st.number_input("Cash / Bank (₹)", 0, 1000000000, 500000)
    liabilities = st.number_input("Total Liabilities (₹)", 0, 1000000000, 0)
    assets = mf + equity + real_estate + cash
    nw = assets - liabilities
    kpi_row([
        ("Assets", fmt(assets)),
        ("Liabilities", fmt(liabilities)),
        ("Net Worth", fmt(nw)),
    ])

# =====================================================
# EMI VS SIP
# =====================================================
if st.session_state.page == "emi_vs_sip":
    back_button()
    st.markdown('<div class="section-box"><div class="section-header">EMI vs SIP Calculator</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        asset_cost = st.number_input("Asset / Loan Amount (₹)", 0, 1000000000, 1000000)
        down_payment = st.number_input("Down Payment (₹)", 0, 1000000000, 200000)
        loan_rate = st.number_input("Loan Interest Rate (%)", 0.0, 25.0, 9.0) / 100
        loan_years = st.number_input("Loan Tenure (Years)", 1, 30, 5)
    with c2:
        sip_return_alt = st.number_input("Expected SIP Return (%)", 0.0, 25.0, 12.0) / 100
        compare_years = st.number_input("Comparison Period (Years)", 1, 30, int(loan_years))
        annual_stepup_alt = st.number_input("SIP Annual Step-up (%)", 0.0, 30.0, 0.0) / 100

    loan_principal = max(asset_cost - down_payment, 0)
    emi = emi_calculator(loan_principal, loan_rate, loan_years)
    sip_corpus = 0.0
    monthly_sip_alt = emi
    months_alt = int(compare_years * 12)
    for m in range(1, months_alt + 1):
        sip_corpus = sip_corpus * (1 + sip_return_alt / 12) + monthly_sip_alt
        if annual_stepup_alt > 0 and m % 12 == 0:
            monthly_sip_alt *= (1 + annual_stepup_alt)
    total_emi_outflow = emi * min(int(loan_years * 12), months_alt)
    wealth_difference = sip_corpus - total_emi_outflow
    kpi_row([
        ("Monthly EMI", fmt(emi)),
        ("Total EMI Outflow", fmt(total_emi_outflow)),
        ("SIP Corpus", fmt(sip_corpus)),
        ("Wealth Gap", fmt(wealth_difference)),
    ])

# =====================================================
# FOOTER
# =====================================================
valid_pages = ["home", "sip", "swp", "children", "retirement", "fund_suggestion", "networth", "emi_vs_sip"]
if st.session_state.page not in valid_pages:
    st.session_state.page = "home"

st.markdown("---")
st.caption("Freedom | Mutual Fund Product & Research Analyst Platform | FINAL SAFE BUILD")
