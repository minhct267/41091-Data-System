import charts
import streamlit as st
from config import MONTH_ORDER
from data_loader import load_fact_joined

st.title("Dashboard")

df = load_fact_joined()

if df.empty:
    st.warning("No fact rows found.")
    st.stop()

st.sidebar.header("Filters")

months_present = [m for m in MONTH_ORDER if m in df["month_name"].unique()]
selected_months = st.sidebar.multiselect(
    "Month", months_present, default=months_present,
)

departments = sorted(df["department"].dropna().unique())
selected_departments = st.sidebar.multiselect(
    "Department", departments, default=departments,
)

staff = sorted(df["staff_name"].dropna().unique())
selected_staff = st.sidebar.multiselect(
    "Staff", staff, default=staff,
)

filtered = df[
    df["month_name"].isin(selected_months)
    & df["department"].isin(selected_departments)
    & df["staff_name"].isin(selected_staff)
]

if filtered.empty:
    st.info("No records match the current filters.")
    st.stop()

kpis = charts.kpi_metrics(filtered)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Payments", f"${kpis.total_pay:,.2f}")
c2.metric("Total Jobs", f"{kpis.total_jobs:,}")
c3.metric("Avg Pay / Job", f"${kpis.avg_pay:,.2f}")
c4.metric("Total Work Hours", f"{kpis.total_hours:,.1f}")

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Total Pay by Month")
    st.plotly_chart(charts.bar_pay_by_month(filtered), use_container_width=True)
with right:
    st.subheader("Total Pay by Department")
    st.plotly_chart(charts.bar_pay_by_department(filtered), use_container_width=True)

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Total Pay by Staff")
    st.plotly_chart(charts.hbar_pay_by_staff(filtered), use_container_width=True)
with right:
    st.subheader("Payment Composition by Department")
    st.plotly_chart(
        charts.stacked_pay_composition(filtered, group_by="department"),
        use_container_width=True,
    )
