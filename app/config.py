from __future__ import annotations

import os

import plotly.express as px
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True), override=False)

SCHEMA: str = (os.getenv("SQL_SCHEMA") or "dbo").strip()

FACT_TABLE: str = "Total_Pay_Fact"

DIM_TABLES: dict[str, str] = {
    "staff": "Staff_dim",
    "date": "Date_dim",
    "department": "Department_dim",
    "job": "MaintenanceJob_dim",
    "travel": "TravelAllowancePolicy_dim",
    "weather": "WeatherAllowancePolicy_dim",
    "holiday": "Holiday_dim",
}

MONTH_ORDER: list[str] = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

COLOR_PALETTE = px.colors.qualitative.Set2
PLOTLY_TEMPLATE: str = "plotly_white"


def qualified(table: str):
    return f"[{SCHEMA}].[{table}]"
