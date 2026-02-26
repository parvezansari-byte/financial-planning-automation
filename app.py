import streamlit as st
import pandas as pd
import numpy as np
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Image
from reportlab.platypus import TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import io

st.set_page_config(page_title="Premium Wealth Planner", layout="wide")

# =========================================================
# BRAND HEADER
# =========================================================

st.markdown("""
<div style='background:#6A35A3;padding:18px;border-radius:5px'>
<h1 style='color:white;text-align:center;'>Premium Investment & Insurance Planner</h1>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR CLIENT PROFILE
# =========================================================

st.sidebar.header("Client Profile")

client = st.sidebar.text_input("Client Name", "Aditya")
advisor = st.sidebar.text_input("Advisor Name", "Saurabh")

entry_age = st.sidebar.number_input("Entry Age", 18, 65, 30)
ret_age = st.sidebar.number_input("Retirement Age", 45, 75, 60)

annual_income = st.sidebar.number_input("Annual Income (₹)", value=2400000)
annual_expense = st.sidebar.number_input("Annual Expense (₹)", value=915000)

expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0)/100
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0)/100

# =========================================================
# CALCULATIONS
# =========================================================

years_to_ret = ret_age - entry_age

def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

expense_at_ret = future_value(annual_expense, inflation, years_to_ret)
corpus_required = expense_at_ret * 25

# =========================================================
# YEARLY WEALTH TABLE
# =========================================================

sip = st.number_input("Monthly SIP (₹)", value=50000)
stepup = st.number_input("Annual Step-up (%)", value=10.0)/100

wealth_data = []
corpus = 0

for year in range(years_to_ret):
    yearly_sip = sip * 12 * ((1 + stepup) ** year)
    corpus = (corpus + yearly_sip) * (1 + expected_return)
    wealth_data.append([entry_age + year, round(yearly_sip,0), round(corpus,0)])

df = pd.DataFrame(wealth_data, columns=["Age","Yearly SIP","Year End Corpus"])

# =========================================================
# OUTPUT DISPLAY (TABLE STYLE)
# =========================================================

st.markdown("## Retirement Requirement Summary")

summary_df = pd.DataFrame({
    "Metric":["Expense at Retirement","Corpus Required"],
    "Value":[f"₹ {expense_at_ret:,.0f}", f"₹ {corpus_required:,.0f}"]
})

st.table(summary_df)

st.markdown("## Year-wise Wealth Projection")
st.dataframe(df)

# =========================================================
# ADVISOR COMMENTARY ENGINE
# =========================================================

coverage_ratio = df["Year End Corpus"].iloc[-1] / corpus_required

if coverage_ratio >= 1:
    note = "Retirement goal is achievable. Continue disciplined SIP with annual review."
elif coverage_ratio >= 0.75:
    note = "Retirement plan is partially funded. Consider increasing SIP or extending retirement age."
else:
    note = "Significant retirement gap exists. Immediate increase in investments required."

st.markdown("## Advisor Recommendation")
st.info(note)

# =========================================================
# PDF EXPORT
# =========================================================

def create_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=pagesizes.A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Retirement Planning Report for {client}", styles["Heading1"]))
    elements.append(Spacer(1,12))
    elements.append(Paragraph(f"Advisor: {advisor}", styles["Normal"]))
    elements.append(Spacer(1,12))

    table_data = [["Age","Yearly SIP","Year End Corpus"]] + wealth_data
    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.purple),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),0.5,colors.grey)
    ]))

    elements.append(t)
    elements.append(Spacer(1,12))
    elements.append(Paragraph("Advisor Note:", styles["Heading2"]))
    elements.append(Paragraph(note, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

st.markdown("## Export Client Report")

pdf = create_pdf()

st.download_button(
    label="Download Client PDF Report",
    data=pdf,
    file_name="Retirement_Report.pdf",
    mime="application/pdf"
)

# =========================================================
# CLIENT READY EXPORT (EXCEL)
# =========================================================

st.download_button(
    label="Download Wealth Projection (Excel)",
    data=df.to_csv(index=False),
    file_name="wealth_projection.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("Disclaimer: This report is illustrative and not investment advice.")
