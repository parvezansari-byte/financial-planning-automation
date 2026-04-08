# FINAL Freedom ULTRA PRO V14.1 WEALTHY BLACKSTONE PRIVATE BANK FULL CLEAN SINGLE app.py
# Clean rebuilt single-file Streamlit app (stable version)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import io
from datetime import datetime
from pathlib import Path

# PDF support
PDF_READY = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
except Exception:
    PDF_READY = False

st.set_page_config(page_title="Freedom ULTRA PRO V14.1 | Wealthy Blackstone Private Bank", layout="wide", page_icon="💜")

# =========================
# HELPERS
# =========================
def fmt_inr(x):
    try:
        return f"₹{float(x):,.2f}"
    except Exception:
        return f"₹{x}"


def future_value_sip(monthly_investment, annual_return, years):
    r = annual_return / 12 / 100
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return monthly_investment * n
    return monthly_investment * (((1 + r) ** n - 1) / r) * (1 + r)


def future_value_lumpsum(amount, annual_return, years):
    return amount * ((1 + annual_return / 100) ** years)


def emi(principal, annual_rate, years):
    r = annual_rate / 12 / 100
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return principal / n
    return principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)


def swp_monthly(corpus, annual_return, years):
    r = annual_return / 12 / 100
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return corpus / n
    return corpus * r / (1 - (1 + r) ** (-n))


def required_sip_for_goal(goal_amount, annual_return, years):
    r = annual_return / 12 / 100
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return goal_amount / n
    denom = (((1 + r) ** n - 1) / r) * (1 + r)
    return goal_amount / denom if denom != 0 else 0


def required_lumpsum_for_goal(goal_amount, annual_return, years):
    if years <= 0:
        return goal_amount
    return goal_amount / ((1 + annual_return / 100) ** years)


def annual_stepup_sip(target_amount, annual_return, years, stepup_pct):
    low, high = 0, max(target_amount, 1000)
    r = annual_return / 12 / 100
    months = int(years * 12)

    def fv(base):
        total = 0
        sip = base
        for m in range(1, months + 1):
            if m > 1 and (m - 1) % 12 == 0:
                sip *= (1 + stepup_pct / 100)
            remain = months - m + 1
            total += sip * ((1 + r) ** remain)
        return total

    for _ in range(80):
        mid = (low + high) / 2
        if fv(mid) >= target_amount:
            high = mid
        else:
            low = mid
    return high


def inflation_adjusted_cost(current_cost, inflation, years):
    return current_cost * ((1 + inflation / 100) ** years)


def build_pdf_bytes(title, lines):
    if not PDF_READY:
        return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCenter", parent=styles["Title"], alignment=TA_CENTER, fontSize=18, leading=22, spaceAfter=12)
    body = styles["BodyText"]
    story = [Paragraph(title, title_style), Spacer(1, 8)]
    for line in lines:
        story.append(Paragraph(str(line).replace("\n", "<br/>"), body))
        story.append(Spacer(1, 6))
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# =========================
# SESSION
# =========================
if "module" not in st.session_state:
    st.session_state.module = "Dashboard"
if "clients" not in st.session_state:
    st.session_state.clients = []
if "leads" not in st.session_state:
    st.session_state.leads = []

# =========================
# THEME
# =========================
st.markdown("""
<style>
.block-container {padding-top: 0.5rem; padding-bottom: 2rem;}
[data-testid="stSidebar"] {background: linear-gradient(180deg, #0b1020 0%, #111827 40%, #1e1b4b 100%);}    
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #111827 20%, #312e81 60%, #7c3aed 100%);
    border-radius: 28px; padding: 18px 24px; margin-bottom: 14px;
    border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 16px 36px rgba(0,0,0,0.28);
}
.hero-title {font-size: 2.4rem; font-weight: 900; color: #faf5ff;}
.hero-sub {color: #e5e7eb; font-size: 0.95rem;}
div.stButton > button {
    width: 100%; border-radius: 14px; padding: 0.7rem 0.8rem; font-weight: 800;
    background: linear-gradient(135deg, #4c1d95, #6d28d9); color: white;
    border: 1px solid rgba(139,92,246,0.35);
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGO
# =========================
logo_candidates = [Path("wealthy_logo.png"), Path("logo.png"), Path("image.png"), Path("/mnt/data/image.png")]
logo_path = next((p for p in logo_candidates if p.exists()), None)
if logo_path:
    st.sidebar.image(str(logo_path), use_container_width=True)
else:
    st.sidebar.markdown("## 💜 Wealthy")

# =========================
# NAV
# =========================
st.sidebar.title("Freedom ULTRA PRO V14.1")
st.sidebar.caption("WEALTHY BLACKSTONE PRIVATE BANK")

nav = {
    "Private Bank": ["Dashboard", "One-Click Client Recommendation", "Boardroom Client Summary", "Advisor Meeting Script", "Export Center"],
    "Core": ["Client Profile", "Net Worth Tracker", "Risk Profiler"],
    "Investments": ["SIP Calculator", "Lumpsum Calculator", "SWP Calculator", "Step-Up SIP Planner"],
    "Planning": ["Goal Planner", "Retirement Planner", "EMI / Loan Planner"],
    "Business": ["MFD CRM Lead Tracker", "AUM Projection"],
}
for grp, items in nav.items():
    st.sidebar.markdown(f"### {grp}")
    for item in items:
        if st.sidebar.button(item, key=f"nav_{item}"):
            st.session_state.module = item

module = st.session_state.module

# =========================
# HEADER
# =========================
col1, col2 = st.columns([1, 5])
with col1:
    if logo_path:
        st.image(str(logo_path), use_container_width=True)
with col2:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">FINAL Freedom ULTRA PRO V14.1</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Wealthy Blackstone Private Bank • Full Clean Rebuild • Year-wise Tables • Real PDF Reports</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# =========================
# DASHBOARD
# =========================
if module == "Dashboard":
    a, b, c, d = st.columns(4)
    a.metric("Version", "V14.1")
    b.metric("Brand", "Wealthy")
    c.metric("Modules", "15+")
    d.metric("PDF", "READY" if PDF_READY else "Install reportlab")
    st.success("Wealthy Blackstone Private Bank is ready for premium client meetings.")

# =========================
# CORE
# =========================
elif module == "Client Profile":
    st.subheader("👤 Client Profile")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Client Name")
    age = c1.number_input("Age", 18, 100, 35)
    city = c1.text_input("City")
    mobile = c2.text_input("Mobile")
    email = c2.text_input("Email")
    occupation = c2.text_input("Occupation")
    annual_income = c3.number_input("Annual Income (₹)", 0.0, 100000000.0, 1200000.0, 50000.0)
    annual_expense = c3.number_input("Annual Expense (₹)", 0.0, 100000000.0, 600000.0, 50000.0)
    surplus = max(annual_income - annual_expense, 0)
    st.info(f"Annual Investable Surplus: {fmt_inr(surplus)}")
    if st.button("💾 Save Client"):
        st.session_state.clients.append({"name": name, "age": age, "city": city, "mobile": mobile, "email": email, "occupation": occupation, "annual_income": annual_income, "annual_expense": annual_expense, "surplus": surplus})
        st.success("Client saved in session")
    if st.session_state.clients:
        st.dataframe(pd.DataFrame(st.session_state.clients), use_container_width=True)

elif module == "Net Worth Tracker":
    st.subheader("📊 Net Worth Tracker")
    c1, c2 = st.columns(2)
    equity = c1.number_input("Equity / MF (₹)", 0.0, 1e10, 500000.0, 50000.0)
    debt = c1.number_input("Debt / FD / Bonds (₹)", 0.0, 1e10, 300000.0, 50000.0)
    cash = c1.number_input("Cash / Bank (₹)", 0.0, 1e10, 200000.0, 50000.0)
    property_val = c2.number_input("Property Value (₹)", 0.0, 1e10, 3000000.0, 100000.0)
    gold = c2.number_input("Gold / Other Assets (₹)", 0.0, 1e10, 200000.0, 50000.0)
    loans = c2.number_input("Loans / Liabilities (₹)", 0.0, 1e10, 1500000.0, 100000.0)
    total_assets = equity + debt + cash + property_val + gold
    networth = total_assets - loans
    a, b, c = st.columns(3)
    a.metric("Assets", fmt_inr(total_assets))
    b.metric("Liabilities", fmt_inr(loans))
    c.metric("Net Worth", fmt_inr(networth))

elif module == "Risk Profiler":
    st.subheader("⚖️ Risk Profiler")
    score = sum([
        st.slider("Investment Horizon", 1, 10, 6),
        st.slider("Reaction to Market Fall", 1, 10, 5),
        st.slider("Return Preference", 1, 10, 6),
        st.slider("Market Experience", 1, 10, 4),
        st.slider("Income Stability", 1, 10, 7),
    ])
    if score <= 20:
        profile = "Conservative"
    elif score <= 35:
        profile = "Moderate"
    else:
        profile = "Aggressive"
    st.metric("Risk Score", score)
    st.success(f"Risk Profile: {profile}")

# =========================
# INVESTMENTS
# =========================
elif module == "SIP Calculator":
    st.subheader("📈 SIP Calculator")
    c1, c2, c3 = st.columns(3)
    sip_amt = c1.number_input("Monthly SIP (₹)", 0.0, 1e8, 10000.0, 1000.0)
    ret = c2.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    years = int(c3.number_input("Years", 1, 60, 10))
    fv = future_value_sip(sip_amt, ret, years)
    invested = sip_amt * 12 * years
    a, b, c = st.columns(3)
    a.metric("Total Invested", fmt_inr(invested))
    b.metric("Current Value", fmt_inr(fv))
    c.metric("Gain", fmt_inr(fv - invested))
    rows = []
    for yr in range(1, years + 1):
        inv = sip_amt * 12 * yr
        val = future_value_sip(sip_amt, ret, yr)
        rows.append({"Year": yr, "Invested Value (₹)": round(inv, 2), "Current Value (₹)": round(val, 2), "Gain (₹)": round(val - inv, 2)})
    st.markdown("### 📅 Year-wise SIP Growth Table")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif module == "Lumpsum Calculator":
    st.subheader("💰 Lumpsum Calculator")
    c1, c2, c3 = st.columns(3)
    amt = c1.number_input("Investment Amount (₹)", 0.0, 1e10, 100000.0, 10000.0)
    ret = c2.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    years = int(c3.number_input("Years", 1, 60, 10))
    fv = future_value_lumpsum(amt, ret, years)
    a, b = st.columns(2)
    a.metric("Current Value", fmt_inr(fv))
    b.metric("Gain", fmt_inr(fv - amt))
    rows = []
    for yr in range(1, years + 1):
        val = future_value_lumpsum(amt, ret, yr)
        rows.append({"Year": yr, "Invested Value (₹)": round(amt, 2), "Current Value (₹)": round(val, 2), "Gain (₹)": round(val - amt, 2)})
    st.markdown("### 📅 Year-wise Lumpsum Growth Table")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif module == "SWP Calculator":
    st.subheader("🏦 SWP Calculator")
    c1, c2, c3 = st.columns(3)
    corpus = c1.number_input("Corpus (₹)", 0.0, 1e10, 5000000.0, 100000.0)
    ret = c2.number_input("Expected Return (%)", 0.0, 30.0, 8.0, 0.5)
    years = int(c3.number_input("Withdrawal Years", 1, 60, 20))
    monthly = swp_monthly(corpus, ret, years)
    st.metric("Suggested Monthly SWP", fmt_inr(monthly))
    balance = corpus
    rows = []
    annual_withdrawal = monthly * 12
    for yr in range(1, years + 1):
        opening = balance
        growth = opening * (ret / 100)
        closing = max(opening + growth - annual_withdrawal, 0)
        rows.append({"Year": yr, "Opening Corpus (₹)": round(opening, 2), "Annual Withdrawal (₹)": round(annual_withdrawal, 2), "Closing Corpus (₹)": round(closing, 2)})
        balance = closing
    st.markdown("### 📉 Year-wise SWP Depletion Table")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif module == "Step-Up SIP Planner":
    st.subheader("🚀 Step-Up SIP Planner")
    c1, c2, c3, c4 = st.columns(4)
    goal = c1.number_input("Target Corpus (₹)", 0.0, 1e10, 10000000.0, 100000.0)
    years = int(c2.number_input("Years", 1, 60, 15))
    ret = c3.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    stepup = c4.number_input("Annual Step-Up (%)", 0.0, 50.0, 10.0, 1.0)
    start_sip = annual_stepup_sip(goal, ret, years, stepup)
    st.metric("Starting Monthly SIP Required", fmt_inr(start_sip))
    corpus = 0
    yearly_sip = start_sip * 12
    total_inv = 0
    rows = []
    for yr in range(1, years + 1):
        total_inv += yearly_sip
        corpus = (corpus + yearly_sip) * (1 + ret / 100)
        rows.append({"Year": yr, "Annual Invested (₹)": round(yearly_sip, 2), "Total Invested (₹)": round(total_inv, 2), "Current Value (₹)": round(corpus, 2), "Gain (₹)": round(corpus - total_inv, 2)})
        yearly_sip *= (1 + stepup / 100)
    st.markdown("### 📈 Year-wise Step-Up SIP Growth Table")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

# =========================
# PLANNING
# =========================
elif module == "Goal Planner":
    st.subheader("🎯 Goal Planner")
    c1, c2, c3, c4 = st.columns(4)
    current_cost = c1.number_input("Current Cost (₹)", 0.0, 1e10, 1000000.0, 50000.0)
    years = int(c2.number_input("Years to Goal", 1, 60, 10))
    inflation = c3.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    ret = c4.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    future_goal = inflation_adjusted_cost(current_cost, inflation, years)
    req_sip = required_sip_for_goal(future_goal, ret, years)
    a, b, c = st.columns(3)
    a.metric("Future Goal Value", fmt_inr(future_goal))
    b.metric("Required SIP", fmt_inr(req_sip))
    c.metric("Required Lumpsum", fmt_inr(required_lumpsum_for_goal(future_goal, ret, years)))
    rows = []
    for yr in range(1, years + 1):
        gv = inflation_adjusted_cost(current_cost, inflation, yr)
        sip = required_sip_for_goal(gv, ret, yr)
        rows.append({"Year": yr, "Goal Value (₹)": round(gv, 2), "Required SIP (₹/month)": round(sip, 2)})
    st.markdown("### 🗺️ Year-wise Goal Roadmap")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif module == "Retirement Planner":
    st.subheader("👴 Retirement Planner")
    c1, c2, c3 = st.columns(3)
    current_age = int(c1.number_input("Current Age", 18, 80, 30))
    retire_age = int(c2.number_input("Retirement Age", current_age + 1, 90, 60))
    monthly_exp = c3.number_input("Current Monthly Expense (₹)", 0.0, 1e8, 50000.0, 5000.0)
    inflation = st.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    pre_ret_return = st.number_input("Pre-Retirement Return (%)", 0.0, 50.0, 12.0, 0.5)
    years_to_ret = retire_age - current_age
    future_monthly_exp = monthly_exp * ((1 + inflation / 100) ** years_to_ret)
    corpus_needed = future_monthly_exp * 12 * 25
    sip_required = required_sip_for_goal(corpus_needed, pre_ret_return, years_to_ret)
    a, b, c = st.columns(3)
    a.metric("Monthly Expense @ Retirement", fmt_inr(future_monthly_exp))
    b.metric("Retirement Corpus Needed", fmt_inr(corpus_needed))
    c.metric("Monthly SIP Needed", fmt_inr(sip_required))
    corpus = 0
    annual_sip = sip_required * 12
    total_inv = 0
    rows = []
    for yr in range(1, years_to_ret + 1):
        total_inv += annual_sip
        corpus = (corpus + annual_sip) * (1 + pre_ret_return / 100)
        rows.append({"Age": current_age + yr, "Year": yr, "Total Invested (₹)": round(total_inv, 2), "Current Value (₹)": round(corpus, 2), "Gain (₹)": round(corpus - total_inv, 2)})
    st.markdown("### 🏦 Year-wise Retirement Accumulation Table")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif module == "EMI / Loan Planner":
    st.subheader("🏠 EMI / Loan Planner")
    c1, c2, c3 = st.columns(3)
    principal = c1.number_input("Loan Amount (₹)", 0.0, 1e10, 1000000.0, 50000.0)
    rate = c2.number_input("Interest Rate (%)", 0.0, 30.0, 9.0, 0.25)
    years = int(c3.number_input("Tenure (Years)", 1, 40, 5))
    monthly_emi = emi(principal, rate, years)
    total = monthly_emi * years * 12
    a, b, c = st.columns(3)
    a.metric("Monthly EMI", fmt_inr(monthly_emi))
    b.metric("Total Payment", fmt_inr(total))
    c.metric("Total Interest", fmt_inr(total - principal))

# =========================
# BUSINESS
# =========================
elif module == "MFD CRM Lead Tracker":
    st.subheader("📞 MFD CRM Lead Tracker")
    c1, c2, c3 = st.columns(3)
    lead_name = c1.text_input("Lead Name")
    source = c1.selectbox("Lead Source", ["Referral", "Walk-in", "Digital", "AMC", "Partner", "Other"])
    stage = c2.selectbox("Lead Stage", ["New", "Contacted", "Meeting Done", "Proposal Shared", "Converted", "Lost"])
    potential_aum = c2.number_input("Potential AUM (₹)", 0.0, 1e10, 500000.0, 50000.0)
    next_action = c3.text_input("Next Action")
    if st.button("💾 Save Lead"):
        st.session_state.leads.append({"Lead": lead_name, "Source": source, "Stage": stage, "Potential AUM": potential_aum, "Next Action": next_action})
        st.success("Lead saved")
    if st.session_state.leads:
        df = pd.DataFrame(st.session_state.leads)
        st.dataframe(df, use_container_width=True)
        st.metric("Pipeline AUM", fmt_inr(df["Potential AUM"].sum()))

elif module == "AUM Projection":
    st.subheader("💼 AUM Projection")
    c1, c2, c3, c4 = st.columns(4)
    current_aum = c1.number_input("Current AUM (₹)", 0.0, 1e12, 50000000.0, 1000000.0)
    monthly_new_sip = c2.number_input("Monthly New SIP Book (₹)", 0.0, 1e10, 500000.0, 50000.0)
    growth = c3.number_input("Annual Growth (%)", 0.0, 50.0, 10.0, 0.5)
    years = int(c4.number_input("Projection Years", 1, 30, 5))
    aum = current_aum
    for _ in range(years):
        aum = aum * (1 + growth / 100) + (monthly_new_sip * 12)
    st.metric("Projected AUM", fmt_inr(aum))
    st.metric("Indicative 0.8% Trail", fmt_inr(aum * 0.008))

# =========================
# PRIVATE BANK MODULES
# =========================
elif module == "One-Click Client Recommendation":
    st.subheader("✨ One-Click Client Recommendation")
    c1, c2, c3 = st.columns(3)
    client_name = c1.text_input("Client Name", "Premium Client")
    risk = c1.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    annual_income = c2.number_input("Annual Income (₹)", 0.0, 1e10, 1800000.0, 50000.0)
    annual_expense = c2.number_input("Annual Expense (₹)", 0.0, 1e10, 900000.0, 50000.0)
    goal_target = c3.number_input("Primary Goal Corpus (₹)", 0.0, 1e10, 7500000.0, 100000.0)
    goal_years = int(c3.number_input("Years to Goal", 1, 60, 10))
    exp_return = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    annual_surplus = max(annual_income - annual_expense, 0)
    req_sip = required_sip_for_goal(goal_target, exp_return, goal_years)
    mf_mix = "Large Cap + Hybrid" if risk == "Conservative" else ("Flexi Cap + Large & Mid Cap" if risk == "Moderate" else "Flexi Cap + Mid Cap + Index")
    st.write(f"**Suggested MF Mix:** {mf_mix}")
    st.write(f"**Required SIP:** {fmt_inr(req_sip)}")
    st.write(f"**Annual Surplus:** {fmt_inr(annual_surplus)}")
    lines = [
        f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        f"Client Name: {client_name}",
        f"Risk Profile: {risk}",
        f"Annual Income: {fmt_inr(annual_income)}",
        f"Annual Expense: {fmt_inr(annual_expense)}",
        f"Annual Surplus: {fmt_inr(annual_surplus)}",
        f"Primary Goal Corpus: {fmt_inr(goal_target)}",
        f"Years to Goal: {goal_years}",
        f"Required SIP: {fmt_inr(req_sip)}",
        f"Suggested MF Mix: {mf_mix}",
    ]
    pdf = build_pdf_bytes("WEALTHY CLIENT RECOMMENDATION REPORT", lines)
    if pdf:
        st.download_button("📄 Download Real PDF Recommendation Report", data=pdf, file_name=f"wealthy_recommendation_{client_name.replace(' ','_')}.pdf", mime="application/pdf")

elif module == "Boardroom Client Summary":
    st.subheader("🏛️ Boardroom Client Summary")
    client_name = st.text_input("Client Name", "Premium Client")
    annual_income = st.number_input("Annual Income (₹)", 0.0, 1e10, 1800000.0, 50000.0)
    annual_expense = st.number_input("Annual Expense (₹)", 0.0, 1e10, 900000.0, 50000.0)
    networth = st.number_input("Current Net Worth (₹)", 0.0, 1e10, 5000000.0, 100000.0)
    annual_surplus = max(annual_income - annual_expense, 0)
    a, b, c = st.columns(3)
    a.metric("Annual Surplus", fmt_inr(annual_surplus))
    b.metric("Net Worth", fmt_inr(networth))
    c.metric("Date", datetime.now().strftime('%d-%b-%Y'))

elif module == "Advisor Meeting Script":
    st.subheader("🎤 Advisor Meeting Script")
    client_name = st.text_input("Client Name", "Premium Client")
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    script = f"Good morning {client_name}. Today we review your income, expenses, net worth, risk profile and create a goal-linked plan for {goal}. We will close protection gaps, align SIP strategy, and set a disciplined long-term wealth roadmap."
    st.text_area("Advisor Script", script, height=180)

elif module == "Export Center":
    st.subheader("📤 Export Center")
    export_data = {"generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "clients": st.session_state.clients, "leads": st.session_state.leads}
    json_str = json.dumps(export_data, indent=2)
    st.download_button("⬇️ Download Session Data (JSON)", data=json_str, file_name="wealthy_freedom_v14_1_export.json", mime="application/json")
    st.code(json_str[:5000])

st.divider()
st.caption("Wealthy | FINAL Freedom ULTRA PRO V14.1 WEALTHY BLACKSTONE PRIVATE BANK FULL CLEAN SINGLE app.py • Full clean rebuild • SIP + Lumpsum + SWP + Step-Up SIP + Goal + Retirement year-wise tables added • Install: pip install streamlit pandas matplotlib reportlab")
