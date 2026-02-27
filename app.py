# =====================================================
# CASHFLOW PLANNER
# =====================================================
if st.session_state.page == "cashflow":

    st.button("⬅ Back", on_click=lambda: go("home"))
    st.subheader("Comprehensive Cashflow Planner")

    plan_till_age = st.number_input("Plan Till Age", 60, 100, 85)
    annual_income = st.number_input("Annual Income (₹)", value=1800000)
    annual_expense = st.number_input("Annual Expense (₹)", value=900000)
    sip = st.number_input("Annual Investment (₹)", value=300000)

    corpus = st.number_input("Current Corpus (₹)", value=1000000)

    table = []
    balance = corpus

    for age in range(current_age, plan_till_age + 1):

        surplus = annual_income - annual_expense - sip
        balance = (balance + sip) * (1 + expected_return)

        table.append([
            age,
            annual_income,
            annual_expense,
            sip,
            surplus,
            round(balance,0)
        ])

    df = pd.DataFrame(table, columns=[
        "Age",
        "Income (₹)",
        "Expense (₹)",
        "Investment (₹)",
        "Net Surplus (₹)",
        "Year End Corpus (₹)"
    ])

    st.dataframe(df, use_container_width=True)

    # Interactive Chart
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Age"],
        y=df["Year End Corpus (₹)"],
        mode='lines',
        name="Corpus Growth"
    ))

    fig.add_trace(go.Bar(
        x=df["Age"],
        y=df["Net Surplus (₹)"],
        name="Net Surplus"
    ))

    fig.update_layout(
        title="Cashflow & Wealth Projection",
        template="plotly_dark",
        xaxis_title="Age",
        yaxis_title="₹ Value"
    )

    st.plotly_chart(fig, use_container_width=True)

    final_balance = df["Year End Corpus (₹)"].iloc[-1]

    if final_balance > 0:
        st.success(f"Final Wealth at Age {plan_till_age}: ₹ {final_balance:,.0f}")
    else:
        st.error("⚠ Wealth depletes before target age")
