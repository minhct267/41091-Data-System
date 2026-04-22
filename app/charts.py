from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import COLOR_PALETTE, MONTH_ORDER, PLOTLY_TEMPLATE


@dataclass
class Kpis:
    total_pay: float
    total_jobs: int
    avg_pay: float
    total_hours: float
    total_distance: float


def kpi_metrics(df: pd.DataFrame):
    return Kpis(
        total_pay=float(df["total_pay"].sum()),
        total_jobs=int(len(df)),
        avg_pay=float(df["total_pay"].mean()) if len(df) else 0.0,
        total_hours=float(df["work_hours"].sum()),
        total_distance=float(df["travel_distance"].sum()),
    )


def _style(fig: go.Figure, *, show_legend: bool = True):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        showlegend=show_legend,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def bar_pay_by_month(df: pd.DataFrame):
    data = (
        df.groupby("month_name", as_index=False)["total_pay"].sum()
    )
    fig = px.bar(
        data,
        x="month_name",
        y="total_pay",
        color="month_name",
        color_discrete_sequence=COLOR_PALETTE,
        category_orders={"month_name": MONTH_ORDER},
        labels={"month_name": "Month", "total_pay": "Total Pay ($)"},
    )
    fig.update_layout(xaxis_tickangle=-30)
    return _style(fig, show_legend=False)


def bar_pay_by_department(df: pd.DataFrame):
    data = (
        df.groupby("department", as_index=False)["total_pay"]
          .sum().sort_values("total_pay", ascending=False)
    )
    fig = px.bar(
        data,
        x="department",
        y="total_pay",
        color="department",
        color_discrete_sequence=COLOR_PALETTE,
        labels={"department": "Department", "total_pay": "Total Pay ($)"},
    )
    return _style(fig, show_legend=False)


def hbar_pay_by_staff(df: pd.DataFrame):
    data = (
        df.groupby("staff_name", as_index=False)["total_pay"]
          .sum().sort_values("total_pay", ascending=True)
    )
    fig = px.bar(
        data,
        x="total_pay",
        y="staff_name",
        orientation="h",
        color="staff_name",
        color_discrete_sequence=COLOR_PALETTE,
        labels={"staff_name": "Staff", "total_pay": "Total Pay ($)"},
    )
    return _style(fig, show_legend=False)


def stacked_pay_composition(df: pd.DataFrame, group_by: str = "department"):
    components = {
        "work_payment": "Work Payment",
        "travel_allowance_amount": "Travel Allowance",
        "weather_allowance_amount": "Weather Allowance",
    }
    data = (
        df.groupby(group_by, as_index=False)[list(components)].sum()
    )
    melted = data.melt(
        id_vars=group_by,
        value_vars=list(components),
        var_name="component",
        value_name="amount",
    )
    melted["component"] = melted["component"].map(components)

    category_orders = None
    if group_by == "month_name":
        category_orders = {"month_name": MONTH_ORDER}

    fig = px.bar(
        melted,
        x=group_by,
        y="amount",
        color="component",
        barmode="stack",
        color_discrete_sequence=COLOR_PALETTE,
        category_orders=category_orders,
        labels={group_by: group_by.replace("_", " ").title(), "amount": "Amount ($)"},
    )
    fig.update_layout(xaxis_tickangle=-30)
    return _style(fig)


def donut_pay_by_job_type(df: pd.DataFrame):
    data = (
        df.groupby("work_type", as_index=False)["total_pay"]
          .sum().sort_values("total_pay", ascending=False)
    )
    fig = px.pie(
        data,
        names="work_type",
        values="total_pay",
        hole=0.45,
        color_discrete_sequence=COLOR_PALETTE,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _style(fig)


def bar_avg_allowance_by_vehicle(df: pd.DataFrame):
    data = (
        df.groupby("vehicle_type", as_index=False)
          .agg(avg_allowance=("travel_allowance_amount", "mean"),
               jobs=("payment_id", "count"))
          .sort_values("avg_allowance", ascending=False)
    )
    fig = px.bar(
        data,
        x="vehicle_type",
        y="avg_allowance",
        color="vehicle_type",
        color_discrete_sequence=COLOR_PALETTE,
        hover_data={"jobs": True},
        labels={
            "vehicle_type": "Vehicle Type",
            "avg_allowance": "Avg Travel Allowance ($)",
        },
    )
    return _style(fig, show_legend=False)


def heatmap_pay_by_weather_temp(df: pd.DataFrame):
    pivot = (
        df.pivot_table(
            index="weather",
            columns="temperature",
            values="total_pay",
            aggfunc="mean",
        )
        .round(2)
    )
    fig = px.imshow(
        pivot,
        text_auto=".2f",
        color_continuous_scale="Blues",
        aspect="auto",
        labels=dict(x="Temperature", y="Weather", color="Avg Pay ($)"),
    )
    return _style(fig)


def bar_holiday_vs_non(df: pd.DataFrame):
    data = (
        df.groupby("is_holiday", as_index=False)
          .agg(total_pay=("total_pay", "sum"),
               jobs=("payment_id", "count"),
               avg_pay=("total_pay", "mean"))
    )
    fig = px.bar(
        data,
        x="is_holiday",
        y="total_pay",
        color="is_holiday",
        color_discrete_sequence=COLOR_PALETTE,
        hover_data={"jobs": True, "avg_pay": ":.2f"},
        labels={"is_holiday": "Is Holiday", "total_pay": "Total Pay ($)"},
    )
    return _style(fig, show_legend=False)


def scatter_distance_vs_travel_allowance(df: pd.DataFrame):
    fig = px.scatter(
        df,
        x="travel_distance",
        y="travel_allowance_amount",
        color="vehicle_type",
        size="work_hours",
        hover_data=["staff_name", "work_type"],
        color_discrete_sequence=COLOR_PALETTE,
        labels={
            "travel_distance": "Travel Distance (km)",
            "travel_allowance_amount": "Travel Allowance ($)",
            "vehicle_type": "Vehicle Type",
        },
    )
    return _style(fig)
