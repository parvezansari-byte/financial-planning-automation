# ============================================================
# FINAL Freedom ULTRA PRO V11.5 PROFESSIONAL POLISH
# Single File Streamlit Financial Planning Super App
# Premium MFD UI • Advanced Planners • CSV + PDF Report
# ============================================================

import streamlit as st
import pandas as pd
import math
from io import BytesIO
from datetime import datetime

# ------------------------------------------------------------
# Optional PDF Support
# ------------------------------------------------------------
PDF_AVAILABLE = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
except Exception:
    PDF_AVAILABLE = False

# ------------------------------------------------------------
# Page Config
# ------------------------------------------------------------
st.set_page_config(
    page_title="Freedom ULTRA PRO V11.5 PROFESSIONAL POLISH",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------
# Premium CSS
# ------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background:
      radial-gradient(circle at 90% 10%, rgba(59,130,246,0.14), transparent 22%),
      radial-gradient(circle at 10% 90%, rgba(34,197,94,0.10), transparent 24%),
      linear-gradient(135deg, #020617 0%, #0f172a 42%, #111827 100%);
    color: #ffffff;
}
.block-container {
    max-width: 1500px;
    padding-top: 0.8rem;
    padding-bottom: 2rem;
}
.hero {
    background: linear-gradient(135deg, rgba(59,130,246,0.16), rgba(34,197,94,0.12), rgba(236,72,153,0.08));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 22px;
    margin-bottom: 14px;
    box-shadow: 0 16px 42px rgba(0,0,0,0.28);
}
.ribbon, .section-card, .kpi-card, .tile-card, .report-box {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.16);
}
.ribbon { padding: 14px; margin-bottom: 12px; }
.section-card { padding: 16px; margin-bottom: 14px; }
.kpi-card { padding: 14px; min-height: 110px; }
.tile-card { padding: 14px; min-height: 150px; }
.report-box { padding: 16px; margin-top: 16px; }
.stButton > button {
    width: 100%;
    border-radius: 12px;
    font-weight: 700;
    border: 1px solid rgba(255,255,255,0.08);
    background: linear-gradient(135deg, rgba(34,197,94,0.18), rgba(59,130,246,0.18));
    color: white;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def fmt(x):
    x = float(x)
    if abs(x) >= 1e7:
        return f"₹{x/1e7:,.2f} Cr"
    if abs(x) >= 1e5:
        return f"₹{x/1e5:,.2f} L"
    return f"₹{x:,.0f}"


def safe_div(a, b):
    return a / b if b not in [0, None] else 0


def sip_future_value(pmt, r, years):
    r = r / 100 / 12
    n = int(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return pmt * n
    return pmt * (((1 + r) ** n - 1) / r) * (1 + r)


def lumpsum_future_value(pv, r, years):
    return pv * ((1 + r / 100) ** years)


def emi(p, r, y):
    r = r / 100 / 12
    n = int(y * 12)
    if n <= 0:
        return 0
    if r == 0:
        return p / n
    return p * r * (1 + r) ** n / ((1 + r) ** n - 1)


def goal_future_cost(cost, infl, years):
    return cost * ((1 + infl / 100) ** years)


def required_sip(goal, r, years):
    r = r / 100 / 12
    n = int(years * 12)
    if n <= 0:
        return goal
    if r == 0:
        return goal / n
    factor = (((1 + r) ** n - 1) / r) * (1 + r)
    return goal / factor


def swp_duration(corpus, monthly, annual_return):
    r = annual_return / 100 / 12
    if monthly <= 0:
        return float('inf')
    if r == 0:
        return corpus / monthly
    if monthly <= corpus * r:
        return float('inf')
    try:
        n = -math.log(1 - (corpus * r / monthly)) / math.log(1 + r)
        return n
    except Exception:
        return 0


def retirement_corpus(monthly_expense, infl, years_to_ret, post_ret_return, years_in_ret):
    expense_at_ret = monthly_expense * ((1 + infl / 100) ** years_to_ret)
    annual_expense = expense_at_ret * 12
    real_return = ((1 + post_ret_return / 100) / (1 + infl / 100)) - 1
    if abs(real_return) < 1e-9:
        corpus = annual_expense * years_in_ret
    else:
        corpus = annual_expense * (1 - (1 + real_return) ** (-years_in_ret)) / real_return
    return corpus, expense_at_ret


def stepup_sip_fv(monthly_sip, annual_return, years, stepup):
    r = annual_return / 100 / 12
    total = 0
    for y in range(int(years)):
        sip_y = monthly_sip * ((1 + stepup / 100) ** y)
        months = 12
        if r == 0:
            fv_y = sip_y * months
        else:
            fv_y = sip_y * (((1 + r) ** months - 1) / r) * (1 + r)
        remaining = int((years - y - 1) * 12)
        total += fv_y * ((1 + r) ** max(remaining, 0))
    return total


def basic_tax_old(income):
    taxable = max(income - 50000, 0)
    tax = 0
    slabs = [(250000, 0), (250000, 0.05), (500000, 0.20), (float('inf'), 0.30)]
    rem = taxable
    for amt, rate in slabs:
        use = min(rem, amt)
        tax += use * rate
        rem -= use
        if rem <= 0:
            break
    if taxable <= 500000:
        tax = 0
    return tax * 1.04


def basic_tax_new(income):
    taxable = max(income - 75000, 0)
    slabs = [(400000, 0.0), (400000, 0.05), (400000, 0.10), (400000, 0.15), (400000, 0.20), (float('inf'), 0.30)]
    tax = 0
    rem = taxable
    for amt, rate in slabs:
        use = min(rem, amt)
        tax += use * rate
        rem -= use
        if rem <= 0:
            break
    if taxable <= 1200000:
        tax = 0
    return tax * 1.04


def add_report(module, metric, value, remarks=""):
    st.session_state.report.append({"Module": module, "Metric": metric, "Value": value, "Remarks": remarks})


def report_df():
    return pd.DataFrame(st.session_state.report) if st.session_state.report else pd.DataFrame(columns=["Module", "Metric", "Value", "Remarks"])


def build_pdf(df):
    if not PDF_AVAILABLE:
        return None
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Freedom ULTRA PRO V11.5 PROFESSIONAL POLISH - Client Report", styles['Title']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Client: {st.session_state.client_name}", styles['BodyText']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles['BodyText']))
    story.append(Spacer(1, 10))
    if df.empty:
        story.append(Paragraph("No report items added.", styles['BodyText']))
    else:
        data = [list(df.columns)] + df.astype(str).values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer


def back_button():
    c1, c2 = st.columns([1.2, 8])
    with c1:
        if st.button("⬅️ Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()


def tile(title, desc, key):
    st.markdown(f"<div class='tile-card'><h4>{title}</h4><p style='color:#94a3b8;font-size:12px'>{desc}</p></div>", unsafe_allow_html=True)
    if st.button("Open", key=f"open_{key}"):
        st.session_state.page = key
        st.rerun()

# ------------------------------------------------------------
# Session State
# ------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "report" not in st.session_state:
    st.session_state.report = []
if "client_name" not in st.session_state:
    st.session_state.client_name = "Parvez Alam Ansari"
if "client_age" not in st.session_state:
    st.session_state.client_age = 30
if "client_income" not in st.session_state:
    st.session_state.client_income = 50000.0
if "advisor_notes" not in st.session_state:
    st.session_state.advisor_notes = ""

# ------------------------------------------------------------
# Hero Header
# ------------------------------------------------------------
st.markdown("""
<div class='hero'>
<h1 style='margin:0'>💼 FINAL Freedom ULTRA PRO V11.5 PROFESSIONAL POLISH</h1>
<p style='margin-top:6px;color:#d1d5db'>Premium MFD Financial Planning Super App • Attractive Cards • Advanced Planners • Advisor Notes • CSV + PDF Report</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Top Nav
# ------------------------------------------------------------
nav = st.columns(8)
buttons = [
    ("🏠 Dashboard", "Dashboard"),
    ("💵 Cashflow", "Cashflow"),
    ("📈 Invest", "Invest"),
    ("🎯 Goals", "Goals"),
    ("🛡️ Protection", "Protection"),
    ("🚗 Lifestyle", "Lifestyle"),
    ("📝 Notes", "Notes"),
    ("📄 Reports", "Reports"),
]
for col, (label, page) in zip(nav, buttons):
    with col:
        if st.button(label):
            st.session_state.page = page
            st.rerun()

st.markdown("<div class='ribbon'>", unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
with r1:
    st.session_state.client_name = st.text_input("Client Name", value=st.session_state.client_name)
with r2:
    st.session_state.client_age = st.number_input("Age", 18, 100, value=int(st.session_state.client_age))
with r3:
    st.session_state.client_income = st.number_input("Monthly Income", min_value=0.0, value=float(st.session_state.client_income), step=1000.0)
with r4:
    st.caption(f"Saved Report Items: {len(st.session_state.report)}")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# DASHBOARD
# ============================================================
if st.session_state.page == "Dashboard":
    st.subheader("🏠 Elite Executive Dashboard")

    monthly_expense = 30000.0
    sip_amt = 10000.0
    emi_out = 5000.0
    surplus = st.session_state.client_income - monthly_expense - sip_amt - emi_out
    savings_ratio = ((max(surplus, 0) + sip_amt) / max(st.session_state.client_income, 1)) * 100
    emergency_gap = max(monthly_expense * 6 - 100000, 0)
    insurance_gap = max(st.session_state.client_income * 12 * 15 - 5000000, 0)

    k = st.columns(5)
    cards = [
        ("Client", st.session_state.client_name, f"Age {st.session_state.client_age}"),
        ("Monthly Income", fmt(st.session_state.client_income), "Primary income"),
        ("Net Surplus", fmt(surplus), "After SIP + EMI"),
        ("Savings Ratio", f"{savings_ratio:.1f}%", "Advisor KPI"),
        ("Insurance Gap", fmt(insurance_gap), "Approx. protection gap"),
    ]
    for col, (t, v, s) in zip(k, cards):
        with col:
            st.markdown(f"<div class='kpi-card'><div style='color:#94a3b8'>{t}</div><h3>{v}</h3><div style='color:#cbd5e1;font-size:12px'>{s}</div></div>", unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Action Tiles")
    row1 = st.columns(4)
    with row1[0]: tile("💵 Overall Cashflow", "Income vs outflow master analysis", "Cashflow")
    with row1[1]: tile("📈 Investment Tools", "SIP, Lumpsum, SWP, Step-up SIP", "Invest")
    with row1[2]: tile("🎯 Goal Planning", "Goal, Child, Retirement, FIRE", "Goals")
    with row1[3]: tile("📄 Report Center", "Client summary + CSV + PDF", "Reports")

    st.markdown("### 📊 Dashboard Visuals")
    c1, c2 = st.columns(2)
    with c1:
        cf = pd.DataFrame({"Category": ["Expense", "SIP", "EMI", "Surplus"], "Amount": [monthly_expense, sip_amt, emi_out, max(surplus, 0)]})
        st.bar_chart(cf.set_index("Category"))
    with c2:
        alloc = pd.DataFrame({"Asset": ["Equity", "Debt", "Gold"], "Allocation": [70, 20, 10]})
        st.bar_chart(alloc.set_index("Asset"))

    st.markdown("### 🧩 Module Tiles")
    rows = [
        [("📈 SIP", "Monthly SIP future value", "SIP"), ("💰 Lumpsum", "One-time investment growth", "Lumpsum"), ("💸 SWP", "Withdrawal sustainability", "SWP"), ("📈 Step-up SIP", "Annual SIP increase planner", "StepUp")],
        [("🎯 Goal Planner", "Inflated goal cost + required SIP", "GoalPlanner"), ("👶 Child Planner", "Education / marriage planning", "Child"), ("🧓 Retirement", "Corpus + SIP required", "Retirement"), ("🔥 FIRE", "Financial freedom target", "FIRE")],
        [("🛡️ Insurance", "Term cover and protection", "Protection"), ("🚨 Emergency Fund", "6-12 months reserve planning", "Emergency"), ("📊 Net Worth", "Assets vs liabilities", "NetWorth"), ("🧾 Tax", "Old vs new regime view", "Tax")],
        [("🏦 EMI Planner", "Loan EMI calculator", "EMI"), ("🚗 Car Planner", "Car affordability and EMI", "Car"), ("📱 Gadget Planner", "iPhone / gadget savings", "Gadget"), ("✈️ Vacation Planner", "Travel savings goal", "Vacation")],
    ]
    for row in rows:
        cols = st.columns(4)
        for col, item in zip(cols, row):
            with col:
                tile(item[0], item[1], item[2])

# ============================================================
# CASHFLOW
# ============================================================
elif st.session_state.page == "Cashflow":
    back_button()
    st.header("💵 Overall Cashflow Master")
    i1, i2, i3, i4 = st.columns(4)
    salary = i1.number_input("Salary Income", value=50000.0, step=1000.0)
    business = i2.number_input("Business Income", value=0.0, step=1000.0)
    rental = i3.number_input("Rental Income", value=0.0, step=1000.0)
    other = i4.number_input("Other Income", value=5000.0, step=500.0)

    e1, e2, e3, e4, e5 = st.columns(5)
    fixed = e1.number_input("Fixed Expenses", value=20000.0, step=1000.0)
    variable = e2.number_input("Variable Expenses", value=10000.0, step=1000.0)
    emi_out = e3.number_input("EMI", value=5000.0, step=1000.0)
    insurance = e4.number_input("Insurance", value=3000.0, step=500.0)
    sip = e5.number_input("SIP / Investments", value=10000.0, step=1000.0)

    total_income = salary + business + rental + other
    total_outflow = fixed + variable + emi_out + insurance + sip
    surplus = total_income - total_outflow
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Income", fmt(total_income))
    c2.metric("Total Outflow", fmt(total_outflow))
    c3.metric("Surplus", fmt(surplus))
    c4.metric("Savings Ratio", f"{((max(surplus,0)+sip)/max(total_income,1))*100:.1f}%")
    if st.button("Add Cashflow to Report"):
        add_report("Cashflow", "Monthly Surplus", fmt(surplus), "Overall cashflow master")
        st.success("Added to report")

# ============================================================
# INVESTMENT HUB
# ============================================================
elif st.session_state.page == "Invest":
    back_button()
    st.header("📈 Investment Calculators")
    tabs = st.tabs(["SIP", "Lumpsum", "SWP", "Step-up SIP"])

    with tabs[0]:
        sip_amt = st.number_input("Monthly SIP", value=10000.0, step=500.0)
        r = st.number_input("Expected Return %", value=12.0, step=0.1)
        y = st.number_input("Years", value=15.0, step=1.0)
        fv = sip_future_value(sip_amt, r, y)
        st.metric("Future Value", fmt(fv))
        if st.button("Add SIP to Report"):
            add_report("SIP", "Future Value", fmt(fv), f"{fmt(sip_amt)}/month")
            st.success("Added")

    with tabs[1]:
        l = st.number_input("Lumpsum Investment", value=500000.0, step=10000.0)
        r2 = st.number_input("Return %", value=12.0, step=0.1, key="lump_r")
        y2 = st.number_input("Years", value=10.0, step=1.0, key="lump_y")
        fv2 = lumpsum_future_value(l, r2, y2)
        st.metric("Future Value", fmt(fv2))
        if st.button("Add Lumpsum to Report"):
            add_report("Lumpsum", "Future Value", fmt(fv2), f"{fmt(l)} one-time")
            st.success("Added")

    with tabs[2]:
        corpus = st.number_input("Current Corpus", value=10000000.0, step=100000.0)
        swp_amt = st.number_input("Monthly SWP", value=50000.0, step=1000.0)
        swp_ret = st.number_input("Return %", value=8.0, step=0.1, key="swp_ret")
        months = swp_duration(corpus, swp_amt, swp_ret)
        years = months / 12 if months != float('inf') else float('inf')
        st.metric("Sustainability", "Sustainable" if years == float('inf') else f"{years:.2f} Years")
        if st.button("Add SWP to Report"):
            add_report("SWP", "Duration", "Sustainable" if years == float('inf') else f"{years:.2f} Years")
            st.success("Added")

    with tabs[3]:
        base_sip = st.number_input("Starting SIP", value=10000.0, step=500.0)
        stepup = st.number_input("Annual Step-up %", value=10.0, step=1.0)
        ret = st.number_input("Expected Return %", value=12.0, step=0.1, key="step_ret")
        yrs = st.number_input("Years", value=15.0, step=1.0, key="step_yrs")
        fv3 = stepup_sip_fv(base_sip, ret, int(yrs), stepup)
        st.metric("Future Value", fmt(fv3))
        if st.button("Add Step-up SIP to Report"):
            add_report("Step-up SIP", "Future Value", fmt(fv3))
            st.success("Added")

# Dashboard tile redirects
elif st.session_state.page in ["SIP", "Lumpsum", "SWP", "StepUp"]:
    st.session_state.page = "Invest"
    st.rerun()

# ============================================================
# GOALS HUB
# ============================================================
elif st.session_state.page == "Goals":
    back_button()
    st.header("🎯 Goal Planning Suite")
    tabs = st.tabs(["Goal Planner", "Child Planner", "Retirement", "FIRE"])

    with tabs[0]:
        cost = st.number_input("Current Goal Cost", value=2000000.0, step=10000.0)
        infl = st.number_input("Inflation %", value=7.0, step=0.1)
        years = st.number_input("Years to Goal", value=10.0, step=1.0)
        ret = st.number_input("Expected Return %", value=12.0, step=0.1)
        future = goal_future_cost(cost, infl, years)
        sip_req = required_sip(future, ret, years)
        c1, c2 = st.columns(2)
        c1.metric("Future Goal Cost", fmt(future))
        c2.metric("Required SIP", fmt(sip_req))
        if st.button("Add Goal Planner to Report"):
            add_report("Goal Planner", "Required SIP", fmt(sip_req), f"Target {fmt(future)}")
            st.success("Added")

    with tabs[1]:
        child_age = st.number_input("Child Age", 0, 30, value=5)
        goal_age = st.number_input("Goal Age", 1, 35, value=18)
        current_cost = st.number_input("Current Education / Marriage Cost", value=2500000.0, step=10000.0)
        infl2 = st.number_input("Inflation %", value=8.0, step=0.1, key="child_infl")
        ret2 = st.number_input("Expected Return %", value=12.0, step=0.1, key="child_ret")
        years2 = max(goal_age - child_age, 0)
        future2 = goal_future_cost(current_cost, infl2, years2)
        sip2 = required_sip(future2, ret2, years2) if years2 > 0 else future2
        c1, c2 = st.columns(2)
        c1.metric("Future Cost", fmt(future2))
        c2.metric("Required SIP", fmt(sip2))
        if st.button("Add Child Planner to Report"):
            add_report("Child Planner", "Required SIP", fmt(sip2), f"Future cost {fmt(future2)}")
            st.success("Added")

    with tabs[2]:
        age = st.number_input("Current Age", 18, 100, value=30)
        ret_age = st.number_input("Retirement Age", 30, 100, value=60)
        monthly_exp = st.number_input("Monthly Expense Today", value=50000.0, step=1000.0)
        infl3 = st.number_input("Inflation %", value=6.0, step=0.1, key="ret_infl")
        post_ret = st.number_input("Post-Ret Return %", value=7.0, step=0.1)
        pre_ret = st.number_input("Pre-Ret Return %", value=12.0, step=0.1)
        years_in_ret = st.number_input("Years in Retirement", 1, 40, value=25)
        years_to_ret = max(ret_age - age, 0)
        corpus, expense_at_ret = retirement_corpus(monthly_exp, infl3, years_to_ret, post_ret, years_in_ret)
        sip_ret = required_sip(corpus, pre_ret, years_to_ret) if years_to_ret > 0 else corpus
        c1, c2, c3 = st.columns(3)
        c1.metric("Expense at Retirement", fmt(expense_at_ret))
        c2.metric("Required Corpus", fmt(corpus))
        c3.metric("Required SIP", fmt(sip_ret))
        if st.button("Add Retirement to Report"):
            add_report("Retirement", "Required Corpus", fmt(corpus), f"Required SIP {fmt(sip_ret)}")
            st.success("Added")

    with tabs[3]:
        annual_expense = st.number_input("Annual Expense", value=600000.0, step=10000.0)
        swr = st.number_input("Safe Withdrawal Rate %", value=4.0, step=0.1)
        current_corpus = st.number_input("Current Corpus", value=3000000.0, step=10000.0)
        annual_contrib = st.number_input("Annual Contribution", value=300000.0, step=10000.0)
        port_ret = st.number_input("Expected Return %", value=11.0, step=0.1)
        fire_number = annual_expense / (swr / 100)
        years_fire = 0
        corpus_fire = current_corpus
        while corpus_fire < fire_number and years_fire < 100:
            years_fire += 1
            corpus_fire = corpus_fire * (1 + port_ret / 100) + annual_contrib
        c1, c2 = st.columns(2)
        c1.metric("FIRE Number", fmt(fire_number))
        c2.metric("Years to FIRE", str(years_fire) if years_fire < 100 else "100+")
        if st.button("Add FIRE to Report"):
            add_report("FIRE", "FIRE Number", fmt(fire_number), f"Years to FIRE {years_fire}")
            st.success("Added")

elif st.session_state.page in ["GoalPlanner", "Child", "Retirement", "FIRE"]:
    st.session_state.page = "Goals"
    st.rerun()

# ============================================================
# PROTECTION + NET WORTH + TAX + EMERGENCY
# ============================================================
elif st.session_state.page == "Protection":
    back_button()
    st.header("🛡️ Protection Planning")
    tabs = st.tabs(["Insurance", "Emergency Fund", "Net Worth", "Tax"])

    with tabs[0]:
        annual_income = st.number_input("Annual Income", value=800000.0, step=10000.0)
        years_to_work = st.number_input("Years to Work", 1, 50, value=25)
        liabilities = st.number_input("Outstanding Liabilities", value=2000000.0, step=10000.0)
        cover = annual_income * years_to_work + liabilities
        st.metric("Suggested Life Cover", fmt(cover))
        if st.button("Add Insurance to Report"):
            add_report("Insurance", "Suggested Cover", fmt(cover))
            st.success("Added")

    with tabs[1]:
        monthly_exp = st.number_input("Monthly Household Expense", value=50000.0, step=1000.0)
        months = st.slider("Emergency Fund Months", 3, 24, 6)
        current_fund = st.number_input("Current Emergency Fund", value=100000.0, step=5000.0)
        req = monthly_exp * months
        gap = max(req - current_fund, 0)
        c1, c2 = st.columns(2)
        c1.metric("Required Emergency Fund", fmt(req))
        c2.metric("Gap", fmt(gap))
        if st.button("Add Emergency Fund to Report"):
            add_report("Emergency Fund", "Required Fund", fmt(req), f"Gap {fmt(gap)}")
            st.success("Added")

    with tabs[2]:
        a1, a2 = st.columns(2)
        with a1:
            cash = st.number_input("Cash / Bank", value=200000.0, step=5000.0)
            mf = st.number_input("Mutual Funds", value=800000.0, step=10000.0)
            stocks = st.number_input("Stocks", value=300000.0, step=10000.0)
            epf = st.number_input("EPF / PPF / NPS", value=600000.0, step=10000.0)
        with a2:
            real_estate = st.number_input("Real Estate", value=5000000.0, step=100000.0)
            home_loan = st.number_input("Home Loan", value=2500000.0, step=10000.0)
            car_loan = st.number_input("Car Loan", value=300000.0, step=10000.0)
            personal_loan = st.number_input("Personal Loan", value=100000.0, step=5000.0)
        assets = cash + mf + stocks + epf + real_estate
        liab = home_loan + car_loan + personal_loan
        nw = assets - liab
        c1, c2, c3 = st.columns(3)
        c1.metric("Assets", fmt(assets))
        c2.metric("Liabilities", fmt(liab))
        c3.metric("Net Worth", fmt(nw))
        if st.button("Add Net Worth to Report"):
            add_report("Net Worth", "Current Net Worth", fmt(nw))
            st.success("Added")

    with tabs[3]:
        annual_inc = st.number_input("Annual Gross Income", value=600000.0, step=10000.0)
        old_tax = basic_tax_old(annual_inc)
        new_tax = basic_tax_new(annual_inc)
        c1, c2 = st.columns(2)
        c1.metric("Old Regime Tax", fmt(old_tax))
        c2.metric("New Regime Tax", fmt(new_tax))
        st.info("Suggestion: Old Regime may be better" if old_tax < new_tax else "Suggestion: New Regime may be better")
        if st.button("Add Tax to Report"):
            add_report("Tax", "Suggested Regime", "Old" if old_tax < new_tax else "New")
            st.success("Added")

elif st.session_state.page in ["NetWorth", "Tax", "Emergency"]:
    st.session_state.page = "Protection"
    st.rerun()

# ============================================================
# LIFESTYLE PLANNERS
# ============================================================
elif st.session_state.page == "Lifestyle":
    back_button()
    st.header("🚗 Lifestyle Goal Planners")
    tabs = st.tabs(["EMI Planner", "Car Planner", "Gadget Planner", "Vacation Planner"])

    with tabs[0]:
        principal = st.number_input("Loan Amount", value=3000000.0, step=10000.0)
        rate = st.number_input("Interest Rate %", value=9.0, step=0.1)
        years = st.number_input("Tenure (Years)", value=20.0, step=1.0)
        emi_val = emi(principal, rate, years)
        st.metric("Monthly EMI", fmt(emi_val))
        if st.button("Add EMI to Report"):
            add_report("EMI Planner", "Monthly EMI", fmt(emi_val))
            st.success("Added")

    with tabs[1]:
        car_cost = st.number_input("Car Cost", value=1200000.0, step=10000.0)
        down_pct = st.number_input("Down Payment %", value=20.0, step=1.0)
        car_rate = st.number_input("Car Loan Rate %", value=9.0, step=0.1)
        car_years = st.number_input("Tenure (Years)", value=5.0, step=1.0, key="car_yrs")
        down_amt = car_cost * down_pct / 100
        loan_amt = car_cost - down_amt
        car_emi = emi(loan_amt, car_rate, car_years)
        c1, c2 = st.columns(2)
        c1.metric("Down Payment", fmt(down_amt))
        c2.metric("Car EMI", fmt(car_emi))
        if st.button("Add Car Plan to Report"):
            add_report("Car Planner", "Car EMI", fmt(car_emi))
            st.success("Added")

    with tabs[2]:
        gadget_cost = st.number_input("Gadget Cost", value=100000.0, step=1000.0)
        months = st.number_input("Target in Months", value=12)
        years = months / 12
        req = required_sip(gadget_cost, 6.0, years)
        st.metric("Required Monthly Saving", fmt(req))
        if st.button("Add Gadget Plan to Report"):
            add_report("Gadget Planner", "Monthly Saving", fmt(req))
            st.success("Added")

    with tabs[3]:
        trip_cost = st.number_input("Current Trip Cost", value=300000.0, step=5000.0)
        months2 = st.number_input("Trip After Months", value=18)
        future_trip = goal_future_cost(trip_cost, 7.0, months2 / 12)
        req_trip = required_sip(future_trip, 6.0, months2 / 12)
        c1, c2 = st.columns(2)
        c1.metric("Future Trip Cost", fmt(future_trip))
        c2.metric("Required Monthly Saving", fmt(req_trip))
        if st.button("Add Vacation Plan to Report"):
            add_report("Vacation Planner", "Monthly Saving", fmt(req_trip))
            st.success("Added")

elif st.session_state.page in ["EMI", "Car", "Gadget", "Vacation"]:
    st.session_state.page = "Lifestyle"
    st.rerun()

# ============================================================
# ADVISOR NOTES
# ============================================================
elif st.session_state.page == "Notes":
    back_button()
    st.header("📝 Advisor Notes")
    st.session_state.advisor_notes = st.text_area(
        "Enter Advisor Recommendations",
        value=st.session_state.advisor_notes,
        height=280,
        placeholder="Example: Increase SIP by 10% annually, build 6 months emergency fund, add term cover, reduce unsecured debt..."
    )
    st.success("Notes auto-saved in session.")
    if st.button("Add Notes Marker to Report"):
        add_report("Advisor Notes", "Notes Added", "Yes")
        st.success("Added")

# ============================================================
# REPORTS
# ============================================================
elif st.session_state.page == "Reports":
    back_button()
    st.header("📄 Client Report Center")
    df = report_df()
    st.dataframe(df, use_container_width=True)
    st.markdown("<div class='report-box'>", unsafe_allow_html=True)
    st.subheader("Advisor Notes")
    st.write(st.session_state.advisor_notes if st.session_state.advisor_notes else "No advisor notes added yet.")
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if not df.empty:
            st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"), "freedom_ultra_pro_v11_5_report.csv", "text/csv")
    with c2:
        if PDF_AVAILABLE and not df.empty:
            pdf_buffer = build_pdf(df)
            if pdf_buffer:
                st.download_button("⬇️ Download PDF", pdf_buffer, "freedom_ultra_pro_v11_5_report.pdf", "application/pdf")
        elif not PDF_AVAILABLE:
            st.warning("Install reportlab for PDF support")
    with c3:
        if st.button("🧹 Clear Report"):
            st.session_state.report = []
            st.success("Report cleared")
            st.rerun()

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------
st.markdown("---")
st.caption("FINAL Freedom ULTRA PRO V11.5 PROFESSIONAL POLISH • Premium MFD Streamlit Financial Planning Super App • Single File")
