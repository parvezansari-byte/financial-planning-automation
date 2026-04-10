# FINAL Freedom ULTRA PRO V22 WEALTHY AI ADVISOR OS SINGLE app.py
# Absolute final AI-powered advisor operating system (single-file Streamlit super app)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import io
from datetime import datetime
from pathlib import Path

# =========================
# PDF SUPPORT
# =========================
PDF_READY = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
except Exception:
    PDF_READY = False

st.set_page_config(page_title="Freedom ULTRA PRO V22 | Wealthy AI Advisor OS", layout="wide", page_icon="💜")

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


def inflation_adjusted_cost(current_cost, inflation, years):
    return current_cost * ((1 + inflation / 100) ** years)


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


def lifestyle_yearwise_table(current_cost, inflation, years, ret):
    rows = []
    for yr in range(1, years + 1):
        goal_val = inflation_adjusted_cost(current_cost, inflation, yr)
        sip_need = required_sip_for_goal(goal_val, ret, yr)
        rows.append({"Year": yr, "Projected Goal Value (₹)": round(goal_val, 2), "Required SIP (₹)": round(sip_need, 2)})
    return pd.DataFrame(rows)


def ai_recommendation(risk, goal_target, goal_years, exp_return):
    req_sip = required_sip_for_goal(goal_target, exp_return, goal_years)
    if risk == "Conservative":
        mf_mix = "Large Cap + Hybrid + Short Duration Debt"
    elif risk == "Moderate":
        mf_mix = "Flexi Cap + Large & Mid Cap + Balanced Advantage"
    else:
        mf_mix = "Flexi Cap + Mid Cap + Index + Tactical Debt"
    return req_sip, mf_mix


def client_health_score(surplus, insurance_gap, goal_gap):
    score = 100
    if surplus <= 0:
        score -= 35
    elif surplus < 120000:
        score -= 15
    if insurance_gap > 0:
        score -= 25
    if goal_gap > 0:
        score -= 25
    if score >= 80:
        band = "Excellent"
    elif score >= 60:
        band = "Good"
    elif score >= 40:
        band = "Needs Attention"
    else:
        band = "Critical"
    return max(score, 0), band


def top_nav_button(label, target):
    if st.button(label, key=f"top_{target}"):
        st.session_state.module = target

# =========================
# SESSION STATE
# =========================
for key, default in {
    "module": "Dashboard",
    "clients": [],
    "leads": [],
    "followups": [],
    "snapshots": [],
    "annual_reviews": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# =========================
# STYLING
# =========================
st.markdown("""
<style>
.block-container {padding-top: 0.35rem; padding-bottom: 2rem;}
[data-testid="stSidebar"] {background: linear-gradient(180deg, #040611 0%, #0b1020 42%, #1e1b4b 100%);}    
.hero {
    background: linear-gradient(135deg, #030712 0%, #111827 18%, #1e1b4b 52%, #4c1d95 72%, #7c3aed 100%);
    border-radius: 30px; padding: 18px 24px; margin-bottom: 10px;
    border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 20px 48px rgba(0,0,0,0.34);
}
.hero-title {font-size: 2.35rem; font-weight: 900; color: #faf5ff;}
.hero-sub {color: #e5e7eb; font-size: 0.96rem;}
.kpi-card {
    background: linear-gradient(135deg, rgba(17,24,39,0.92), rgba(76,29,149,0.88));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 12px 14px;
    margin-bottom: 8px;
}
.kpi-title {color:#c4b5fd; font-size:0.82rem; font-weight:700;}
.kpi-value {color:#ffffff; font-size:1.35rem; font-weight:900;}
.section-strip {
    background: linear-gradient(90deg, rgba(30,27,75,0.95), rgba(76,29,149,0.95));
    padding: 10px 14px; border-radius: 16px; margin-bottom: 10px;
    border: 1px solid rgba(255,255,255,0.06);
}
div.stButton > button {
    width: 100%; border-radius: 14px; padding: 0.72rem 0.85rem; font-weight: 800;
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
# SIDEBAR NAVIGATION
# =========================
st.sidebar.title("Freedom ULTRA PRO V22")
st.sidebar.caption("WEALTHY AI ADVISOR OS")

nav = {
    "AI Advisor OS": ["Dashboard", "AI Client Summary Generator", "AI Recommendation Engine", "AI Meeting Notes Generator", "AI Proposal Text Builder", "Client Health Score", "Portfolio Review Checklist", "Annual Review Tracker", "Client Database Master", "Client Session Manager", "Export Center"],
    "CRM Command Center": ["Lead Scoring Dashboard", "Follow-Up Tracker", "Meeting Status Tracker", "One-Click Client Recommendation", "Boardroom Client Summary", "Advisor Meeting Script", "Printable Client Proposal Screen"],
    "Core": ["Client Onboarding Master", "Client Profile", "Net Worth Tracker", "Risk Profiler", "Asset Allocation Dashboard", "Risk-to-Product Mapper", "Client Recommendation Snapshot Vault"],
    "Investments": ["SIP vs Lumpsum Comparator", "Normal SIP vs Step-Up SIP Chart", "SIP Calculator", "Lumpsum Calculator", "SWP Calculator", "SWP Year-wise Depletion Chart", "Step-Up SIP Planner"],
    "Life Goals": ["Family Goals Master Dashboard", "Advanced Goal Prioritization Engine", "Goal Planner", "Goal Funding Gap Analyzer", "Retirement Planner", "Retirement Year-wise Accumulation Table", "Retirement Shortfall Analyzer", "Child Education Planner", "Marriage Planner", "Travel Planner", "Car Purchase Planner", "iPhone Purchase Planner"],
    "Protection & PDF": ["AMC-wise Recommendation Bucket", "Insurance Need Analysis", "Insurance PDF Report", "Client Fact Find Form PDF", "Client Meeting Executive Summary PDF", "Master Combined Proposal PDF", "Goal PDF Report", "Retirement PDF Report"],
    "Business": ["Cashflow Planner", "EMI / Loan Planner", "MFD CRM Lead Tracker", "AUM Projection", "Client Proposal Generator"],
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
    st.markdown('<div class="hero-title">FINAL Freedom ULTRA PRO V22</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Wealthy AI Advisor OS • Final AI-powered advisor operating system • CRM + planning + client conversion</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-strip"><b>⚡ Quick Access AI Tabs</b></div>', unsafe_allow_html=True)
q1, q2, q3, q4, q5, q6 = st.columns(6)
with q1: top_nav_button("🏠 Dashboard", "Dashboard")
with q2: top_nav_button("🤖 AI Summary", "AI Client Summary Generator")
with q3: top_nav_button("🧠 AI Recommend", "AI Recommendation Engine")
with q4: top_nav_button("❤️ Health Score", "Client Health Score")
with q5: top_nav_button("📋 Annual Review", "Annual Review Tracker")
with q6: top_nav_button("🗂️ Database", "Client Database Master")

st.divider()

# =========================
# DASHBOARD
# =========================
if module == "Dashboard":
    total_clients = len(st.session_state.clients)
    total_leads = len(st.session_state.leads)
    total_followups = len(st.session_state.followups)
    total_reviews = len(st.session_state.annual_reviews)
    total_pipeline = sum([x.get("Potential AUM", 0) for x in st.session_state.leads]) if st.session_state.leads else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown('<div class="kpi-card"><div class="kpi-title">CLIENTS</div><div class="kpi-value">%s</div></div>' % total_clients, unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="kpi-card"><div class="kpi-title">LEADS</div><div class="kpi-value">%s</div></div>' % total_leads, unsafe_allow_html=True)
    with k3:
        st.markdown('<div class="kpi-card"><div class="kpi-title">FOLLOW-UPS / REVIEWS</div><div class="kpi-value">%s / %s</div></div>' % (total_followups, total_reviews), unsafe_allow_html=True)
    with k4:
        st.markdown('<div class="kpi-card"><div class="kpi-title">PIPELINE AUM</div><div class="kpi-value">%s</div></div>' % fmt_inr(total_pipeline), unsafe_allow_html=True)

    st.success("V22 AI Advisor OS is ready: AI summary, AI recommendations, AI notes, AI proposal builder, health score, annual reviews, and full CRM.")

# =========================
# AI MODULES
# =========================
elif module == "AI Client Summary Generator":
    st.subheader("🤖 AI Client Summary Generator")
    name = st.text_input("Client Name", "Premium Client")
    age = st.number_input("Age", 18, 100, 35)
    annual_income = st.number_input("Annual Income (₹)", 0.0, 1e10, 1800000.0, 50000.0)
    annual_expense = st.number_input("Annual Expense (₹)", 0.0, 1e10, 900000.0, 50000.0)
    networth = st.number_input("Net Worth (₹)", 0.0, 1e10, 5000000.0, 100000.0)
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    surplus = max(annual_income - annual_expense, 0)
    summary = f"{name}, age {age}, has annual income of {fmt_inr(annual_income)} and annual expense of {fmt_inr(annual_expense)}, creating annual surplus of {fmt_inr(surplus)}. Current net worth is {fmt_inr(networth)}. Primary focus is {goal}. Overall profile suggests a structured long-term advisory roadmap with protection, goal-based investing, and annual review discipline."
    st.text_area("AI Client Summary", summary, height=180)

elif module == "AI Recommendation Engine":
    st.subheader("🧠 AI Recommendation Engine")
    risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    goal_target = st.number_input("Primary Goal Corpus (₹)", 0.0, 1e10, 7500000.0, 100000.0)
    goal_years = int(st.number_input("Years to Goal", 1, 60, 10))
    exp_return = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    req_sip, mf_mix = ai_recommendation(risk, goal_target, goal_years, exp_return)
    reco = f"Recommended strategy: Build a disciplined SIP of {fmt_inr(req_sip)} for {goal_years} years, aligned to a {risk.lower()} profile. Suggested MF allocation mix: {mf_mix}. Conduct annual review and step-up SIP where feasible."
    st.text_area("AI Recommendation", reco, height=180)
    st.metric("Required SIP", fmt_inr(req_sip))

elif module == "AI Meeting Notes Generator":
    st.subheader("📝 AI Meeting Notes Generator")
    client = st.text_input("Client Name", "Premium Client")
    agenda = st.text_input("Meeting Agenda", "Goal planning, insurance review, retirement roadmap")
    concerns = st.text_area("Client Concerns", "Wants disciplined investment plan, worried about retirement corpus and protection gaps.")
    notes = f"Meeting Notes for {client}: Discussed agenda around {agenda}. Key concerns captured: {concerns}. Advisor recommended structured goal-based investing, insurance gap analysis, and annual review process. Next step: share proposal and follow-up within 3 working days."
    st.text_area("AI Meeting Notes", notes, height=220)

elif module == "AI Proposal Text Builder":
    st.subheader("📄 AI Proposal Text Builder")
    client = st.text_input("Client Name", "Premium Client")
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    sip = st.number_input("Suggested SIP (₹)", 0.0, 1e8, 50000.0, 5000.0)
    cover = st.number_input("Suggested Life Cover (₹)", 0.0, 1e10, 25000000.0, 100000.0)
    proposal = f"Dear {client}, based on our discussion, we recommend beginning a structured financial plan focused on {goal}. Suggested monthly SIP is {fmt_inr(sip)} and recommended life cover is {fmt_inr(cover)}. This plan should be reviewed annually and enhanced via step-up contributions as income grows."
    st.text_area("AI Proposal Text", proposal, height=220)

elif module == "Client Health Score":
    st.subheader("❤️ Client Health Score")
    annual_income = st.number_input("Annual Income (₹)", 0.0, 1e10, 1800000.0, 50000.0)
    annual_expense = st.number_input("Annual Expense (₹)", 0.0, 1e10, 900000.0, 50000.0)
    insurance_gap = st.number_input("Insurance Gap (₹)", 0.0, 1e10, 2000000.0, 100000.0)
    goal_gap = st.number_input("Goal Funding Gap (₹)", 0.0, 1e10, 1500000.0, 100000.0)
    surplus = max(annual_income - annual_expense, 0)
    score, band = client_health_score(surplus, insurance_gap, goal_gap)
    st.metric("Client Health Score", f"{score}/100")
    st.success(f"Health Band: {band}")

elif module == "Portfolio Review Checklist":
    st.subheader("📑 Portfolio Review Checklist")
    checks = [
        "Asset allocation aligned to risk profile",
        "Insurance cover adequate",
        "Emergency fund maintained",
        "Goal SIPs active and on track",
        "Retirement corpus reviewed",
        "Tax-saving allocation reviewed",
        "Nomination / KYC / FATCA updated",
        "Annual step-up SIP discussed",
    ]
    for item in checks:
        st.checkbox(item)

elif module == "Annual Review Tracker":
    st.subheader("📋 Annual Review Tracker")
    c1, c2, c3 = st.columns(3)
    client_name = c1.text_input("Client Name")
    review_date = c2.date_input("Review Date")
    status = c3.selectbox("Status", ["Scheduled", "Completed", "Rescheduled"])
    note = st.text_input("Review Note")
    if st.button("💾 Save Annual Review"):
        st.session_state.annual_reviews.append({"Client": client_name, "Review Date": str(review_date), "Status": status, "Note": note})
        st.success("Annual review saved")
    if st.session_state.annual_reviews:
        st.dataframe(pd.DataFrame(st.session_state.annual_reviews), use_container_width=True)

# =========================
# CRM / DATABASE
# =========================
elif module == "Client Database Master":
    st.subheader("🗂️ Client Database Master")
    if st.session_state.clients:
        df = pd.DataFrame(st.session_state.clients)
        search = st.text_input("Search Client Name")
        if search and "name" in df.columns:
            df = df[df["name"].astype(str).str.contains(search, case=False, na=False)]
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No client profiles saved yet. Use Client Onboarding Master.")

elif module == "Client Session Manager":
    st.subheader("🗂️ Client Session Manager")
    if st.session_state.clients:
        st.dataframe(pd.DataFrame(st.session_state.clients), use_container_width=True)
    else:
        st.warning("No client profiles saved yet.")

elif module == "Lead Scoring Dashboard":
    st.subheader("🔥 Lead Scoring Dashboard")
    if st.session_state.leads:
        df = pd.DataFrame(st.session_state.leads)
        def score_row(row):
            stage_score = {"New": 20, "Contacted": 40, "Meeting Done": 65, "Proposal Shared": 85, "Converted": 100, "Lost": 0}.get(row.get("Stage", "New"), 20)
            aum = row.get("Potential AUM", 0)
            aum_score = 30 if aum >= 2000000 else (20 if aum >= 1000000 else (10 if aum >= 500000 else 5))
            total = min(stage_score + aum_score, 100)
            temp = "Hot" if total >= 80 else ("Warm" if total >= 50 else "Cold")
            return pd.Series([total, temp])
        df[["Lead Score", "Temperature"]] = df.apply(score_row, axis=1)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No leads available. Add leads in MFD CRM Lead Tracker.")

elif module == "Follow-Up Tracker":
    st.subheader("📞 Follow-Up Tracker")
    c1, c2, c3, c4 = st.columns(4)
    client_name = c1.text_input("Client / Lead Name")
    followup_date = c2.date_input("Follow-Up Date")
    priority = c3.selectbox("Priority", ["High", "Medium", "Low"])
    status = c4.selectbox("Status", ["Pending", "Done", "Rescheduled"])
    note = st.text_input("Follow-Up Note")
    if st.button("💾 Save Follow-Up"):
        st.session_state.followups.append({"Name": client_name, "Date": str(followup_date), "Priority": priority, "Status": status, "Note": note})
        st.success("Follow-up saved")
    if st.session_state.followups:
        st.dataframe(pd.DataFrame(st.session_state.followups), use_container_width=True)

elif module == "Meeting Status Tracker":
    st.subheader("📋 Meeting Status Tracker")
    if st.session_state.leads:
        df = pd.DataFrame(st.session_state.leads)
        summary = df["Stage"].value_counts().reset_index()
        summary.columns = ["Stage", "Count"]
        st.dataframe(summary, use_container_width=True)
    else:
        st.warning("No leads yet.")

elif module == "Client Recommendation Snapshot Vault":
    st.subheader("📸 Client Recommendation Snapshot Vault")
    c1, c2, c3, c4 = st.columns(4)
    client_name = c1.text_input("Client Name")
    risk = c2.selectbox("Risk", ["Conservative", "Moderate", "Aggressive"])
    sip = c3.number_input("Suggested SIP (₹)", 0.0, 1e8, 25000.0, 1000.0)
    note = c4.text_input("Snapshot Note")
    if st.button("💾 Save Recommendation Snapshot"):
        st.session_state.snapshots.append({"Client": client_name, "Risk": risk, "Suggested SIP": sip, "Note": note, "Saved At": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        st.success("Snapshot saved")
    if st.session_state.snapshots:
        st.dataframe(pd.DataFrame(st.session_state.snapshots), use_container_width=True)

# =========================
# CORE / INVESTMENTS / GOALS / BUSINESS
# =========================
elif module == "Client Onboarding Master":
    st.subheader("📝 Client Onboarding Master")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Client Name")
    age = c1.number_input("Age", 18, 100, 35)
    city = c1.text_input("City")
    mobile = c2.text_input("Mobile")
    email = c2.text_input("Email")
    occupation = c2.text_input("Occupation")
    annual_income = c3.number_input("Annual Income (₹)", 0.0, 1e9, 1200000.0, 50000.0)
    annual_expense = c3.number_input("Annual Expense (₹)", 0.0, 1e9, 600000.0, 50000.0)
    networth = st.number_input("Current Net Worth (₹)", 0.0, 1e10, 2500000.0, 100000.0)
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    surplus = max(annual_income - annual_expense, 0)
    st.info(f"Annual Investable Surplus: {fmt_inr(surplus)}")
    if st.button("💾 Save Full Onboarding"):
        st.session_state.clients.append({"name": name, "age": age, "city": city, "mobile": mobile, "email": email, "occupation": occupation, "annual_income": annual_income, "annual_expense": annual_expense, "surplus": surplus, "networth": networth, "goal": goal})
        st.success("Full client onboarding saved")

elif module == "Client Profile":
    st.subheader("👤 Client Profile")
    st.info("Use Client Onboarding Master for full save workflow.")

elif module == "Net Worth Tracker":
    st.subheader("📊 Net Worth Tracker")
    equity = st.number_input("Equity / MF (₹)", 0.0, 1e10, 500000.0, 50000.0)
    debt = st.number_input("Debt / FD / Bonds (₹)", 0.0, 1e10, 300000.0, 50000.0)
    cash = st.number_input("Cash / Bank (₹)", 0.0, 1e10, 200000.0, 50000.0)
    property_val = st.number_input("Property Value (₹)", 0.0, 1e10, 3000000.0, 100000.0)
    gold = st.number_input("Gold / Other Assets (₹)", 0.0, 1e10, 200000.0, 50000.0)
    loans = st.number_input("Loans / Liabilities (₹)", 0.0, 1e10, 1500000.0, 100000.0)
    total_assets = equity + debt + cash + property_val + gold
    st.metric("Net Worth", fmt_inr(total_assets - loans))

elif module == "Risk Profiler":
    st.subheader("⚖️ Risk Profiler")
    score = sum([st.slider("Investment Horizon", 1, 10, 6), st.slider("Reaction to Market Fall", 1, 10, 5), st.slider("Return Preference", 1, 10, 6), st.slider("Market Experience", 1, 10, 4), st.slider("Income Stability", 1, 10, 7)])
    if score <= 20: profile = "Conservative"
    elif score <= 35: profile = "Moderate"
    else: profile = "Aggressive"
    st.metric("Risk Score", score)
    st.success(f"Risk Profile: {profile}")

elif module == "Asset Allocation Dashboard":
    st.subheader("🧠 Asset Allocation Dashboard")
    age = st.number_input("Client Age", 18, 100, 35)
    risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    eq = max(100 - age, 20) if risk == "Moderate" else (max(100 - age - 20, 10) if risk == "Conservative" else min(max(110 - age, 40), 85))
    st.metric("Recommended Equity %", f"{eq}%")
    st.metric("Recommended Debt %", f"{100 - eq}%")

elif module == "Risk-to-Product Mapper":
    st.subheader("🧭 Risk-to-Product Mapper")
    risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    mapping = {
        "Conservative": ["Liquid Fund", "Short Duration Debt Fund", "Hybrid Conservative Fund", "Large Cap Fund"],
        "Moderate": ["Large Cap Fund", "Flexi Cap Fund", "Balanced Advantage Fund", "Large & Mid Cap Fund"],
        "Aggressive": ["Flexi Cap Fund", "Mid Cap Fund", "Index Fund", "Aggressive Hybrid / Tactical Debt"],
    }
    for p in mapping[risk]: st.write(f"- {p}")

elif module == "SIP vs Lumpsum Comparator":
    st.subheader("📊 SIP vs Lumpsum Comparator")
    sip_amt = st.number_input("Monthly SIP (₹)", 0.0, 1e8, 10000.0, 1000.0)
    lump_amt = st.number_input("Lumpsum (₹)", 0.0, 1e10, 1200000.0, 10000.0)
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    years = int(st.number_input("Years", 1, 60, 10))
    st.metric("SIP Future Value", fmt_inr(future_value_sip(sip_amt, ret, years)))
    st.metric("Lumpsum Future Value", fmt_inr(future_value_lumpsum(lump_amt, ret, years)))

elif module == "Normal SIP vs Step-Up SIP Chart":
    st.subheader("📈 Normal SIP vs Step-Up SIP Chart")
    sip_amt = st.number_input("Monthly SIP (₹)", 0.0, 1e8, 10000.0, 1000.0)
    years = int(st.number_input("Years", 1, 60, 15))
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    stepup = st.number_input("Annual Step-Up (%)", 0.0, 50.0, 10.0, 1.0)
    normal = [future_value_sip(sip_amt, ret, y) for y in range(1, years + 1)]
    step = []
    corpus = 0
    yearly_sip = sip_amt * 12
    for _ in range(1, years + 1):
        corpus = (corpus + yearly_sip) * (1 + ret / 100)
        step.append(corpus)
        yearly_sip *= (1 + stepup / 100)
    fig, ax = plt.subplots(); ax.plot(range(1, years + 1), normal, label="Normal SIP"); ax.plot(range(1, years + 1), step, label="Step-Up SIP"); ax.legend(); st.pyplot(fig)

elif module == "SIP Calculator":
    st.subheader("📈 SIP Calculator")
    sip_amt = st.number_input("Monthly SIP (₹)", 0.0, 1e8, 10000.0, 1000.0)
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    years = int(st.number_input("Years", 1, 60, 10))
    fv = future_value_sip(sip_amt, ret, years); invested = sip_amt * 12 * years
    st.metric("Total Invested", fmt_inr(invested)); st.metric("Current Value", fmt_inr(fv)); st.metric("Gain", fmt_inr(fv - invested))

elif module == "Lumpsum Calculator":
    st.subheader("💰 Lumpsum Calculator")
    amt = st.number_input("Investment Amount (₹)", 0.0, 1e10, 100000.0, 10000.0)
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    years = int(st.number_input("Years", 1, 60, 10))
    fv = future_value_lumpsum(amt, ret, years)
    st.metric("Current Value", fmt_inr(fv)); st.metric("Gain", fmt_inr(fv - amt))

elif module == "SWP Calculator":
    st.subheader("🏦 SWP Calculator")
    corpus = st.number_input("Corpus (₹)", 0.0, 1e10, 5000000.0, 100000.0)
    ret = st.number_input("Expected Return (%)", 0.0, 30.0, 8.0, 0.5)
    years = int(st.number_input("Withdrawal Years", 1, 60, 20))
    st.metric("Suggested Monthly SWP", fmt_inr(swp_monthly(corpus, ret, years)))

elif module == "SWP Year-wise Depletion Chart":
    st.subheader("📉 SWP Year-wise Depletion Chart")
    corpus = st.number_input("Starting Corpus (₹)", 0.0, 1e10, 5000000.0, 100000.0)
    ret = st.number_input("Expected Return (%)", 0.0, 30.0, 8.0, 0.5)
    years = int(st.number_input("Years", 1, 60, 20))
    monthly_withdrawal = st.number_input("Monthly Withdrawal (₹)", 0.0, 1e8, 40000.0, 1000.0)
    annual_withdrawal = monthly_withdrawal * 12
    balances = []; bal = corpus
    for y in range(1, years + 1):
        bal = max((bal * (1 + ret / 100)) - annual_withdrawal, 0)
        balances.append({"Year": y, "Corpus Balance (₹)": round(bal, 2)})
    st.dataframe(pd.DataFrame(balances), use_container_width=True)

elif module == "Step-Up SIP Planner":
    st.subheader("🚀 Step-Up SIP Planner")
    goal = st.number_input("Target Corpus (₹)", 0.0, 1e10, 10000000.0, 100000.0)
    years = int(st.number_input("Years", 1, 60, 15))
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    stepup = st.number_input("Annual Step-Up (%)", 0.0, 50.0, 10.0, 1.0)
    st.metric("Starting Monthly SIP Required", fmt_inr(annual_stepup_sip(goal, ret, years, stepup)))

elif module == "Family Goals Master Dashboard":
    st.subheader("👨‍👩‍👧‍👦 Family Goals Master Dashboard")
    vals = [st.number_input("Child Education Goal (₹)", 0.0, 1e10, 2500000.0, 100000.0), st.number_input("Marriage Goal (₹)", 0.0, 1e10, 1500000.0, 100000.0), st.number_input("Retirement Goal (₹)", 0.0, 1e10, 30000000.0, 500000.0)]
    st.metric("Total Family Goal Corpus", fmt_inr(sum(vals)))

elif module == "Advanced Goal Prioritization Engine":
    st.subheader("🎯 Advanced Goal Prioritization Engine")
    annual_surplus = st.number_input("Annual Investable Surplus (₹)", 0.0, 1e10, 600000.0, 50000.0)
    essential = st.number_input("Essential Goals Corpus (₹)", 0.0, 1e10, 3000000.0, 100000.0)
    st.info(f"Priority: Essential > Important > Luxury | Years to cover essential: {(essential / annual_surplus) if annual_surplus > 0 else 0:.2f}")

elif module == "Goal Planner":
    st.subheader("🎯 Goal Planner")
    current_cost = st.number_input("Current Cost (₹)", 0.0, 1e10, 1000000.0, 50000.0)
    years = int(st.number_input("Years to Goal", 1, 60, 10))
    inflation = st.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    future_goal = inflation_adjusted_cost(current_cost, inflation, years)
    st.metric("Future Goal Value", fmt_inr(future_goal)); st.metric("Required SIP", fmt_inr(required_sip_for_goal(future_goal, ret, years)))

elif module == "Goal Funding Gap Analyzer":
    st.subheader("🎯 Goal Funding Gap Analyzer")
    current_cost = st.number_input("Current Goal Cost (₹)", 0.0, 1e10, 1000000.0, 50000.0)
    current_investment = st.number_input("Current Monthly SIP (₹)", 0.0, 1e8, 10000.0, 1000.0)
    years = int(st.number_input("Years to Goal", 1, 60, 10))
    inflation = st.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    future_goal = inflation_adjusted_cost(current_cost, inflation, years)
    current_plan_value = future_value_sip(current_investment, ret, years)
    st.metric("Funding Gap", fmt_inr(max(future_goal - current_plan_value, 0)))

elif module == "Retirement Planner":
    st.subheader("👴 Retirement Planner")
    current_age = int(st.number_input("Current Age", 18, 80, 30))
    retire_age = int(st.number_input("Retirement Age", current_age + 1, 90, 60))
    monthly_exp = st.number_input("Current Monthly Expense (₹)", 0.0, 1e8, 50000.0, 5000.0)
    inflation = st.number_input("Inflation (%)", 0.0, 20.0, 6.0, 0.5)
    pre_ret_return = st.number_input("Pre-Retirement Return (%)", 0.0, 50.0, 12.0, 0.5)
    years_to_ret = retire_age - current_age
    corpus_needed = (monthly_exp * ((1 + inflation / 100) ** years_to_ret)) * 12 * 25
    st.metric("Retirement Corpus Needed", fmt_inr(corpus_needed)); st.metric("Monthly SIP Needed", fmt_inr(required_sip_for_goal(corpus_needed, pre_ret_return, years_to_ret)))

elif module == "Retirement Year-wise Accumulation Table":
    st.subheader("📅 Retirement Year-wise Accumulation Table")
    current_age = int(st.number_input("Current Age", 18, 80, 30))
    retire_age = int(st.number_input("Retirement Age", current_age + 1, 90, 60))
    monthly_sip = st.number_input("Monthly Retirement SIP (₹)", 0.0, 1e8, 25000.0, 1000.0)
    ret = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    years_to_ret = retire_age - current_age
    rows = [{"Year": yr, "Invested Value (₹)": round(monthly_sip * 12 * yr, 2), "Projected Corpus (₹)": round(future_value_sip(monthly_sip, ret, yr), 2)} for yr in range(1, years_to_ret + 1)]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif module == "Retirement Shortfall Analyzer":
    st.subheader("👴 Retirement Shortfall Analyzer")
    st.info("Use Retirement Planner + Retirement Year-wise Accumulation Table for gap analysis workflow.")

elif module == "Child Education Planner":
    st.subheader("🎓 Child Education Planner")
    st.dataframe(lifestyle_yearwise_table(st.number_input("Current Education Cost (₹)", 0.0, 1e10, 2500000.0, 100000.0), int(st.number_input("Years Left", 1, 30, 10)), st.number_input("Education Inflation (%)", 0.0, 20.0, 8.0, 0.5), st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)), use_container_width=True)

elif module == "Marriage Planner":
    st.subheader("💍 Marriage Planner")
    st.dataframe(lifestyle_yearwise_table(st.number_input("Current Marriage Cost (₹)", 0.0, 1e10, 1500000.0, 100000.0), int(st.number_input("Years Left", 1, 40, 8)), st.number_input("Inflation (%)", 0.0, 20.0, 7.0, 0.5), st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)), use_container_width=True)

elif module == "Travel Planner":
    st.subheader("✈️ Travel Planner")
    st.dataframe(lifestyle_yearwise_table(st.number_input("Current Trip Cost (₹)", 0.0, 1e10, 300000.0, 25000.0), int(st.number_input("Years Left", 1, 20, 3)), st.number_input("Travel Inflation (%)", 0.0, 20.0, 6.0, 0.5), st.number_input("Expected Return (%)", 0.0, 50.0, 10.0, 0.5)), use_container_width=True)

elif module == "Car Purchase Planner":
    st.subheader("🚗 Car Purchase Planner")
    st.dataframe(lifestyle_yearwise_table(st.number_input("Current Car Cost (₹)", 0.0, 1e10, 1200000.0, 50000.0), int(st.number_input("Years Left", 1, 20, 4)), st.number_input("Car Inflation (%)", 0.0, 20.0, 6.0, 0.5), st.number_input("Expected Return (%)", 0.0, 50.0, 10.0, 0.5)), use_container_width=True)

elif module == "iPhone Purchase Planner":
    st.subheader("📱 iPhone Purchase Planner")
    st.dataframe(lifestyle_yearwise_table(st.number_input("Current iPhone Cost (₹)", 0.0, 1e6, 100000.0, 5000.0), int(st.number_input("Years Left", 1, 10, 2)), st.number_input("Price Increase (%)", 0.0, 20.0, 5.0, 0.5), st.number_input("Expected Return (%)", 0.0, 50.0, 8.0, 0.5)), use_container_width=True)

elif module == "AMC-wise Recommendation Bucket":
    st.subheader("🏦 AMC-wise Recommendation Bucket")
    risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    st.write(f"Indicative AMC bucket for {risk}: use category suitability + due diligence before final recommendation.")

elif module == "Insurance Need Analysis":
    st.subheader("🛡️ Insurance Need Analysis")
    annual_income = st.number_input("Annual Income (₹)", 0.0, 1e10, 1200000.0, 50000.0)
    liabilities = st.number_input("Outstanding Liabilities (₹)", 0.0, 1e10, 2000000.0, 100000.0)
    goals = st.number_input("Future Goal Corpus Needed (₹)", 0.0, 1e10, 3000000.0, 100000.0)
    existing_cover = st.number_input("Existing Life Cover (₹)", 0.0, 1e10, 1000000.0, 100000.0)
    recommended_cover = annual_income * 15 + liabilities + goals
    st.metric("Recommended Life Cover", fmt_inr(recommended_cover)); st.metric("Insurance Gap", fmt_inr(max(recommended_cover - existing_cover, 0)))

elif module in ["Insurance PDF Report", "Client Fact Find Form PDF", "Client Meeting Executive Summary PDF", "Goal PDF Report", "Retirement PDF Report"]:
    st.subheader(f"📄 {module}")
    pdf = build_pdf_bytes(module.upper(), [f"{module} generated from V22 app"])
    if pdf:
        st.download_button(f"📄 Download {module}", data=pdf, file_name=f"{module.lower().replace(' ', '_')}.pdf", mime="application/pdf")

elif module == "Master Combined Proposal PDF":
    st.subheader("📄 Master Combined Proposal PDF")
    client_name = st.text_input("Client Name", "Premium Client")
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    sip = st.number_input("Suggested Monthly SIP (₹)", 0.0, 1e8, 50000.0, 5000.0)
    cover = st.number_input("Suggested Life Cover (₹)", 0.0, 1e10, 25000000.0, 100000.0)
    pdf = build_pdf_bytes("WEALTHY MASTER COMBINED PROPOSAL", [f"Client Name: {client_name}", f"Primary Goal: {goal}", f"Suggested SIP: {fmt_inr(sip)}", f"Suggested Life Cover: {fmt_inr(cover)}"])
    if pdf:
        st.download_button("📄 Download Master Combined Proposal PDF", data=pdf, file_name="wealthy_master_combined_proposal.pdf", mime="application/pdf")

elif module == "Cashflow Planner":
    st.subheader("💸 Cashflow Planner")
    monthly_income = st.number_input("Monthly Income (₹)", 0.0, 1e8, 100000.0, 5000.0)
    monthly_expense = st.number_input("Monthly Expense (₹)", 0.0, 1e8, 60000.0, 5000.0)
    emi_amt = st.number_input("Monthly EMI (₹)", 0.0, 1e8, 15000.0, 1000.0)
    st.metric("Monthly Free Cashflow", fmt_inr(monthly_income - monthly_expense - emi_amt))

elif module == "EMI / Loan Planner":
    st.subheader("🏠 EMI / Loan Planner")
    principal = st.number_input("Loan Amount (₹)", 0.0, 1e10, 1000000.0, 50000.0)
    rate = st.number_input("Interest Rate (%)", 0.0, 30.0, 9.0, 0.25)
    years = int(st.number_input("Tenure (Years)", 1, 40, 5))
    st.metric("Monthly EMI", fmt_inr(emi(principal, rate, years)))

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
        st.dataframe(pd.DataFrame(st.session_state.leads), use_container_width=True)

elif module == "AUM Projection":
    st.subheader("💼 AUM Projection")
    current_aum = st.number_input("Current AUM (₹)", 0.0, 1e12, 50000000.0, 1000000.0)
    monthly_new_sip = st.number_input("Monthly New SIP Book (₹)", 0.0, 1e10, 500000.0, 50000.0)
    growth = st.number_input("Annual Growth (%)", 0.0, 50.0, 10.0, 0.5)
    years = int(st.number_input("Projection Years", 1, 30, 5))
    aum = current_aum
    for _ in range(years):
        aum = aum * (1 + growth / 100) + (monthly_new_sip * 12)
    st.metric("Projected AUM", fmt_inr(aum))

elif module == "Client Proposal Generator":
    st.subheader("🧾 Client Proposal Generator")
    client_name = st.text_input("Client Name", "Premium Client")
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    monthly_commitment = st.number_input("Suggested Monthly Investment (₹)", 0.0, 1e8, 50000.0, 5000.0)
    proposal = f"Client {client_name} is recommended to begin a disciplined investment journey focused on {goal}. Suggested monthly commitment is {fmt_inr(monthly_commitment)}."
    st.text_area("Proposal Note", proposal, height=180)

elif module == "Printable Client Proposal Screen":
    st.subheader("🖨️ Printable Client Proposal Screen")
    client_name = st.text_input("Client Name", "Premium Client")
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    sip = st.number_input("Suggested SIP (₹)", 0.0, 1e8, 50000.0, 5000.0)
    cover = st.number_input("Suggested Life Cover (₹)", 0.0, 1e10, 25000000.0, 100000.0)
    st.markdown(f"### Client: {client_name}")
    st.markdown(f"**Primary Goal:** {goal}")
    st.markdown(f"**Suggested Monthly SIP:** {fmt_inr(sip)}")
    st.markdown(f"**Suggested Life Cover:** {fmt_inr(cover)}")

elif module == "One-Click Client Recommendation":
    st.subheader("✨ One-Click Client Recommendation")
    risk = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
    goal_target = st.number_input("Primary Goal Corpus (₹)", 0.0, 1e10, 7500000.0, 100000.0)
    goal_years = int(st.number_input("Years to Goal", 1, 60, 10))
    exp_return = st.number_input("Expected Return (%)", 0.0, 50.0, 12.0, 0.5)
    req_sip, mf_mix = ai_recommendation(risk, goal_target, goal_years, exp_return)
    st.write(f"**Suggested MF Mix:** {mf_mix}"); st.write(f"**Required SIP:** {fmt_inr(req_sip)}")

elif module == "Boardroom Client Summary":
    st.subheader("🏛️ Boardroom Client Summary")
    annual_income = st.number_input("Annual Income (₹)", 0.0, 1e10, 1800000.0, 50000.0)
    annual_expense = st.number_input("Annual Expense (₹)", 0.0, 1e10, 900000.0, 50000.0)
    networth = st.number_input("Current Net Worth (₹)", 0.0, 1e10, 5000000.0, 100000.0)
    st.metric("Annual Surplus", fmt_inr(max(annual_income - annual_expense, 0))); st.metric("Net Worth", fmt_inr(networth))

elif module == "Advisor Meeting Script":
    st.subheader("🎤 Advisor Meeting Script")
    client_name = st.text_input("Client Name", "Premium Client")
    goal = st.text_input("Primary Goal", "Retirement + Wealth Creation")
    script = f"Good morning {client_name}. Today we review your financial position, goals, risk profile and build a complete roadmap for {goal}, with protection, investment and retirement discipline."
    st.text_area("Advisor Script", script, height=180)

elif module == "Export Center":
    st.subheader("📤 Export Center")
    export_data = {"generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "clients": st.session_state.clients, "leads": st.session_state.leads, "followups": st.session_state.followups, "snapshots": st.session_state.snapshots, "annual_reviews": st.session_state.annual_reviews}
    json_str = json.dumps(export_data, indent=2)
    st.download_button("⬇️ Download Session Data (JSON)", data=json_str, file_name="wealthy_freedom_v22_export.json", mime="application/json")
    st.code(json_str[:5000])

st.divider()
st.caption("Wealthy | FINAL Freedom ULTRA PRO V22 WEALTHY AI ADVISOR OS SINGLE app.py • AI summary • AI recommendation • AI notes • AI proposal text • Health score • Portfolio review • Annual review tracker • Install: pip install streamlit pandas matplotlib reportlab")
