from __future__ import annotations

import pandas as pd
import streamlit as st
from config import DIM_TABLES, FACT_TABLE, qualified
from db import get_connection


def _query(sql: str):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame.from_records(
        [tuple(r) for r in rows], columns=columns,
    )


@st.cache_data(ttl=600, show_spinner="Loading fact + dimensions from Azure SQL...")
def load_fact_joined():
    f = qualified(FACT_TABLE)
    s = qualified(DIM_TABLES["staff"])
    d = qualified(DIM_TABLES["date"])
    dep = qualified(DIM_TABLES["department"])
    j = qualified(DIM_TABLES["job"])
    t = qualified(DIM_TABLES["travel"])
    w = qualified(DIM_TABLES["weather"])
    h = qualified(DIM_TABLES["holiday"])

    query = f"""
    SELECT
        f.[Total_Pay_Fact_id] AS payment_id,
        s.[Natural Key Staff ID] AS staff_natural_id,
        s.[Name] AS staff_name,
        s.[Email] AS staff_email,
        d.[date] AS month_name,
        dep.[Department] AS department,
        j.[work type] AS work_type,
        t.[vehicle type] AS vehicle_type,
        t.[travelallowanceRate] AS travel_allowance_rate,
        w.[weather] AS weather,
        w.[temperature] AS temperature,
        w.[weatehr allowance] AS weather_allowance_rate,
        h.[isholiday] AS is_holiday,
        f.[work hours] AS work_hours,
        f.[travel distance] AS travel_distance,
        f.[job hourly] AS hourly_rate,
        f.[work payment] AS work_payment,
        f.[travel allowance amount] AS travel_allowance_amount,
        f.[weather allowance amount] AS weather_allowance_amount,
        f.[total pay this job] AS total_pay
    FROM {f} f
    LEFT JOIN {s} s ON f.[Staff_id] = s.[Staff_id]
    LEFT JOIN {d} d ON f.[Date_id] = d.[Date_id]
    LEFT JOIN {dep} dep ON f.[Department_id] = dep.[Department_id]
    LEFT JOIN {j} j ON f.[MaintenanceJob_id] = j.[MaintenanceJob_id]
    LEFT JOIN {t} t ON f.[TravelAllowancePolicy_id] = t.[TravelAllowancePolicy_id]
    LEFT JOIN {w} w ON f.[WeatherAllowancePolicy_id] = w.[WeatherAllowancePolicy_id]
    LEFT JOIN {h} h ON f.[Holiday_id] = h.[Holiday_id]
    """

    df = _query(query)

    numeric_cols = [
        "work_hours", "travel_distance", "hourly_rate",
        "work_payment", "travel_allowance_amount",
        "weather_allowance_amount", "total_pay",
        "travel_allowance_rate", "weather_allowance_rate",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


@st.cache_data(ttl=600, show_spinner=False)
def load_dim(key: str):
    if key == "fact":
        table = FACT_TABLE
    else:
        if key not in DIM_TABLES:
            raise KeyError(
                f"Unknown table key '{key}'. "
                f"Valid keys: 'fact', {list(DIM_TABLES)}"
            )
        table = DIM_TABLES[key]

    return _query(f"SELECT * FROM {qualified(table)}")
