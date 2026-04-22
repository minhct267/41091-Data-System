import charts
import streamlit as st
from config import MONTH_ORDER
from data_loader import load_fact_joined

st.title("Visualizations")

df = load_fact_joined()

if df.empty:
    st.warning("No fact rows found.")
    st.stop()

st.sidebar.header("Filters")

months_present = [m for m in MONTH_ORDER if m in df["month_name"].unique()]
selected_months = st.sidebar.multiselect(
    "Month", months_present, default=months_present,
)

work_types = sorted(df["work_type"].dropna().unique())
selected_work_types = st.sidebar.multiselect(
    "Work type", work_types, default=work_types,
)

vehicles = sorted(df["vehicle_type"].dropna().unique())
selected_vehicles = st.sidebar.multiselect(
    "Vehicle", vehicles, default=vehicles,
)

weathers = sorted(df["weather"].dropna().unique())
selected_weather = st.sidebar.multiselect(
    "Weather", weathers, default=weathers,
)

filtered = df[
    df["month_name"].isin(selected_months)
    & df["work_type"].isin(selected_work_types)
    & df["vehicle_type"].isin(selected_vehicles)
    & df["weather"].isin(selected_weather)
]

if filtered.empty:
    st.info("No records match the current filters.")
    st.stop()

left, right = st.columns(2)
with left:
    st.subheader("Pay Share by Job Type")
    st.plotly_chart(charts.donut_pay_by_job_type(filtered), use_container_width=True)
with right:
    st.subheader("Avg Travel Allowance by Vehicle Type")
    st.plotly_chart(
        charts.bar_avg_allowance_by_vehicle(filtered), use_container_width=True,
    )

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Avg Pay by Weather x Temperature")
    st.plotly_chart(
        charts.heatmap_pay_by_weather_temp(filtered), use_container_width=True,
    )
with right:
    st.subheader("Holiday vs Non-Holiday Pay")
    st.plotly_chart(charts.bar_holiday_vs_non(filtered), use_container_width=True)

st.divider()
st.subheader("Travel Distance vs Travel Allowance")
st.plotly_chart(
    charts.scatter_distance_vs_travel_allowance(filtered), use_container_width=True,
)
