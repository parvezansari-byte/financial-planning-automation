import streamlit as st
import pandas as pd
import numpy as np

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(page_title="Freedom", layout="wide")

# ======================================================
# SKY BLUE THEME
# ======================================================

st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #F0F9FF;
}

/* Freedom Header */
.freedom-title {
    background: linear-gradient(90deg, #38BDF8, #0EA5E9);
    padding: 22px;
    border-radius: 14px;
    text-align: center;
    color: white;
    font-size: 44px;
    font-weight: 700;
    letter-spacing: 1px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
}

/* Subtitle */
.subtitle {
    text-align:center;
    font-size:20px;
    color:#0369A1;
    margin-top:8px;
    margin-bottom:20px;
}

/* Card */
.card {
    background-color: white;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

/* Buttons */
.stButton > button {
    background-color: #0EA5E9;
    color: white;
    border-radius: 8px;
    height: 45px;
    font-weight: 600;
}

/* DataFrame text */
[data-testid="stDataFrame"] {
    color: #1E293B !important;
}

/* Table header */
thead tr th {
    background-color: #38BDF8 !important;
    color: white !important;
    font-weight: 600 !important;
}

/* Table cells */
tbody tr td {
    color: #0F172A !important;
    font-weight: 500;
}

/* Alternate rows */
tbody tr:nth-child(even) {
    background-color: #E0F2FE !important;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# SESSION STATE
# ======================================================

if "page" not in st.session_state:
    st.session_state.page = "index"

def go(page):
    st.session_state.page = page

# ======================================================
# HEADER
# ======================================================

st.markdown('<div class="freedom-title">Freedom</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Investment & Insurance Planner</div>', unsafe_allow_html=True)
st.markdown("---")

# ======================================================
# SIDEBAR GLOBAL FILTERS
# ======================================================

st.sidebar.header("Client Profile")

entry_age = st.sidebar.number_input("Entry Age", 18, 65, 27)
expected_return = st.sidebar.number_input("Expected Return (%)", 0.0, 20.0, 12.0)/100
inflation = st.sidebar.number_input("Inflation (%)", 0.0, 15.0, 6.0)/100

# ======================================================
# COMMON FUNCTIONS
# ======================================================

def future_value(pv, rate, years):
    return pv * (1 + rate) ** years

# ======================================================
# INDEX PAGE
# ======================================================

if st.session_state.page == "index":

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("SIP & Lumpsum Calculator"):
            go("sip")
        if st.button("Future Planning for Children"):
            go("children")

    with col2:
        if st.button("SWP Calculator"):
            go("swp")
        if st.button("Retirement Planner"):
            go("retirement")

    with col3:
        if st.button("SIP + SWP Planner"):
            go("sip_swp")
        if st.button("Term Insurance Calculator"):
            go("term")

# ======================================================
# SIP CALCULATOR
# ======================================================

if st.session_state.page == "sip":

    st.button("⬅ Back", on_click=lambda: go("index"))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("SIP Calculator")

    monthly_sip = st.number_input("Monthly SIP (₹)", value=5000)
    years = st.number_input("Investment Years", value=8)
    stepup = st.number_input("Annual Step-up (%)", value=10.0)/100

    corpus = 0
    table = []

    for y in range(years):
        yearly_sip = monthly_sip * 12 * ((1 + stepup)**y)
        corpus = (corpus + yearly_sip) * (1 + expected_return)

        table.append([
            y + 1,
            entry_age + y,
            round(yearly_sip, 0),
            round(corpus, 0)
        ])

    df = pd.DataFrame(table, columns=["No.", "Age", "Yearly SIP", "Year End Corpus"])

    st.dataframe(df, use_container_width=True)

    st.success(f"Final Corpus: ₹ {corpus:,.0f}")

    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# SIMPLE PLACEHOLDER FOR OTHER MODULES
# ======================================================

if st.session_state.page == "children":
    st.button("⬅ Back", on_click=lambda: go("index"))
    st.info("Children Planning Module Coming Soon")

if st.session_state.page == "swp":
    st.button("⬅ Back", on_click=lambda: go("index"))
    st.info("SWP Module Coming Soon")

if st.session_state.page == "retirement":
    st.button("⬅ Back", on_click=lambda: go("index"))
    st.info("Retirement Planner Coming Soon")

if st.session_state.page == "sip_swp":
    st.button("⬅ Back", on_click=lambda: go("index"))
    st.info("SIP + SWP Planner Coming Soon")

if st.session_state.page == "term":
    st.button("⬅ Back", on_click=lambda: go("index"))
    st.info("Term Insurance Calculator Coming Soon")

st.markdown("---")
st.caption("Disclaimer: This planner is for illustration purposes only.")
