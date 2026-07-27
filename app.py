import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Break-Even Analysis Calculator", layout="wide")
st.title("Break-Even Analysis Calculator")

with st.form("bea_form"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        P = st.number_input("Selling price per unit (P)", min_value=0.01, value=100.0, step=1.0)
    with c2:
        VC = st.number_input("Variable cost per unit (VC)", min_value=0.0, value=40.0, step=1.0)
    with c3:
        FC = st.number_input("Fixed costs (FC)", min_value=0.0, value=12000.0, step=100.0)
    with c4:
        Q_target = st.number_input("Target quantity (Q_target)", min_value=0.0, value=300.0, step=10.0)

    currency = st.text_input("Currency symbol (optional)", value="₹")
    submitted = st.form_submit_button("Calculate")

if submitted:
    CM = P - VC
    if CM <= 0:
        st.error("Contribution Margin (P - VC) must be > 0. With current inputs, break-even is not achievable.")
        st.stop()

    CMR = CM / P
    Q_BE = FC / CM
    R_BE = Q_BE * P
    profit_target = CM * Q_target - FC

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Contribution Margin (CM)", f"{currency}{CM:,.2f}")
    k2.metric("CM Ratio (CMR)", f"{CMR*100:,.2f}%")
    k3.metric("BEP (Units)", f"{Q_BE:,.2f}")
    k4.metric("BEP Revenue", f"{currency}{R_BE:,.2f}")
    k5.metric("Profit/Loss at Target", f"{currency}{profit_target:,.2f}")

    # Build chart data
    max_q = max(Q_target, Q_BE) * 1.2
    max_q = max(10, float(max_q))
    Q = np.linspace(0, max_q, 80)

    df = pd.DataFrame({
        "Quantity": Q,
        "Revenue": P * Q,
        "Total Cost": FC + VC * Q,
        "Fixed Cost": np.full_like(Q, FC),
    })

    base = alt.Chart(df).encode(
        x=alt.X("Quantity:Q", title="Quantity (Units)"),
        y=alt.Y("value:Q", title=f"Value ({currency})")
    )

    lines = base.transform_fold(
        ["Revenue", "Total Cost", "Fixed Cost"],
        as_=["Metric", "value"]
    ).mark_line().encode(
        color=alt.Color("Metric:N", legend=alt.Legend(title=""))
    )

    be_point = alt.Chart(pd.DataFrame({
        "Quantity": [Q_BE],
        "Value": [R_BE]
    })).mark_point(filled=True, size=80, color="red").encode(
        x="Quantity:Q",
        y=alt.Y("Value:Q", title=f"Value ({currency})")
    )

    st.subheader("Break-even chart")
    st.altair_chart(lines + be_point, use_container_width=True)

    st.subheader("Interpretation")
    st.write(f"- Break-even occurs at **{Q_BE:,.2f} units** (revenue **{currency}{R_BE:,.2f}**).")
    st.write(f"- At the target volume **{Q_target:,.2f} units**, expected profit/loss is **{currency}{profit_target:,.2f}**.")
    st.write("- Above break-even, revenue grows faster than total cost, so profit increases.")