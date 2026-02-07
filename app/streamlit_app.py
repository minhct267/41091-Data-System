import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================================================================
# Page config
# ==========================================================================
st.set_page_config(
    page_title="Maintenance Contractor Payment Dashboard",
    page_icon="wrench",
    layout="wide",
)

COLOR_PALETTE = px.colors.qualitative.Set2
PLOTLY_TEMPLATE = "plotly_white"

EXPECTED_CSV_COLUMNS = [
    "Date", "Staff_ID", "Staff_Name", "Contact_Phone", "Home_Address",
    "Email_Address", "Department_Name", "Department_Location", "Front_Desk_Phone",
    "Maintenance_Job_ID", "Maintenance_Job_TypeCode", "Maintenance_Job_Desc",
    "IsHoliday", "HourRate", "Travel_Policy_ID", "Vehicle_Type", "Allowance_Per_Km",
    "Weather_Policy_Key", "Weather", "Temperature", "Weather_Allowance",
    "Maintenance_Hours", "Length_of_Travel", "Weather_Condition",
]

# ==========================================================================
# Database connection
# ==========================================================================

@st.cache_resource
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]
        + ";DATABASE="
        + st.secrets["database"]
        + ";UID="
        + st.secrets["username"]
        + ";PWD="
        + st.secrets["password"]
    )


conn = init_connection()


# ==========================================================================
# Data loading helpers
# ==========================================================================

@st.cache_data(ttl=600)
def load_dashboard_data():
    """Load the full joined fact + dimension data (cached 10 min)."""
    query = """
    SELECT
        f.Payment_ID,
        d.Date_Text, d.Month_Name, d.Month_Number, d.Year,
        s.Staff_ID, s.Name AS Staff_Name, s.Department AS Staff_Department,
        dep.Department_Name, dep.Department_Location,
        j.Maintenance_Job_ID, j.Maintenance_Job_TypeCode, j.Maintenance_Job_Desc,
        j.HourRate, j.IsHoliday,
        t.Vehicle_Type, t.Allowance_Per_Km,
        w.Weather, w.Temperature, w.Weather_Allowance,
        f.Maintenance_Hours, f.HolidayPayment,
        f.Length_of_Travel, f.Travel_Allowance_Amount,
        f.Weather_Condition, f.Weather_Allowance_Amount,
        f.Total_Amount_Paid
    FROM mdw.fact_Maintenance_Contractor_Payment f
    JOIN mdw.dim_Date d ON f.Date_Key = d.Date_Key
    JOIN mdw.dim_Staff s ON f.Staff_Key = s.Staff_Key
    JOIN mdw.dim_Department dep ON f.Department_Key = dep.Department_Key
    JOIN mdw.dim_Maintenance_Job j ON f.Maintenance_Job_Key = j.Maintenance_Job_Key
    JOIN mdw.dim_Travel_Allowance_Policy t
        ON f.Travel_Allowance_Policy_Key = t.Travel_Allowance_Policy_Key
    JOIN mdw.dim_Weather_Allowance_Policy w
        ON f.Weather_Allowance_Policy_Key = w.Weather_Allowance_Policy_Key
    """
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame.from_records(rows, columns=columns)


def query_table(table_name, key_column):
    """Return a DataFrame from a dimension table."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM mdw.{table_name}")
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame.from_records(rows, columns=cols)


def get_max_key(table_name, key_column):
    """Get the current max surrogate key from a table."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT ISNULL(MAX({key_column}), 0) FROM mdw.{table_name}")
        return cur.fetchone()[0]


# ==========================================================================
# ETL functions
# ==========================================================================

def upsert_dim_date(df_csv, progress_cb=None):
    """Parse dates from CSV, insert new entries into dim_Date."""
    existing = query_table("dim_Date", "Date_Key")
    existing_texts = set(existing["Date_Text"].tolist()) if not existing.empty else set()

    dates = df_csv["Date"].unique()
    new_rows = []
    for d in dates:
        dt = datetime.strptime(d.strip(), "%d/%m/%Y")
        date_text = dt.strftime("%d/%m/%Y")
        if date_text in existing_texts:
            continue
        new_rows.append({
            "Date_Text": date_text,
            "Day_Name": dt.strftime("%A"),
            "Month_Name": dt.strftime("%B"),
            "Month_Number": dt.month,
            "Year": dt.year,
            "IsHoliday_NSW": 0,
            "IsHoliday_VIC": 0,
            "IsHoliday_QLD": 0,
        })

    if new_rows:
        max_key = get_max_key("dim_Date", "Date_Key")
        with conn.cursor() as cur:
            for i, row in enumerate(new_rows):
                key = max_key + i + 1
                cur.execute(
                    """INSERT INTO mdw.dim_Date
                       (Date_Key, Date_Text, Day_Name, Month_Name, Month_Number, Year,
                        IsHoliday_NSW, IsHoliday_VIC, IsHoliday_QLD)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    key, row["Date_Text"], row["Day_Name"], row["Month_Name"],
                    row["Month_Number"], row["Year"],
                    row["IsHoliday_NSW"], row["IsHoliday_VIC"], row["IsHoliday_QLD"],
                )
            conn.commit()
    if progress_cb:
        progress_cb(f"dim_Date: {len(new_rows)} new date(s) inserted")
    return len(new_rows)


def upsert_dim_staff(df_csv, progress_cb=None):
    """Insert new staff records by Staff_ID."""
    existing = query_table("dim_Staff", "Staff_Key")
    existing_ids = set(existing["Staff_ID"].tolist()) if not existing.empty else set()

    staff_df = df_csv.drop_duplicates(subset=["Staff_ID"])
    new_rows = staff_df[~staff_df["Staff_ID"].isin(existing_ids)]

    if not new_rows.empty:
        max_key = get_max_key("dim_Staff", "Staff_Key")
        with conn.cursor() as cur:
            for i, (_, row) in enumerate(new_rows.iterrows()):
                key = max_key + i + 1
                cur.execute(
                    """INSERT INTO mdw.dim_Staff
                       (Staff_Key, Staff_ID, Name, Contact_Phone, Home_Address,
                        Email_Address, Department)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    key, row["Staff_ID"], row["Staff_Name"], row["Contact_Phone"],
                    row["Home_Address"], row["Email_Address"], row["Department_Name"],
                )
            conn.commit()
    if progress_cb:
        progress_cb(f"dim_Staff: {len(new_rows)} new staff member(s) inserted")
    return len(new_rows)


def upsert_dim_department(df_csv, progress_cb=None):
    """Insert new departments by Department_Name."""
    existing = query_table("dim_Department", "Department_Key")
    existing_names = set(existing["Department_Name"].tolist()) if not existing.empty else set()

    dept_df = df_csv.drop_duplicates(subset=["Department_Name"])
    new_rows = dept_df[~dept_df["Department_Name"].isin(existing_names)]

    if not new_rows.empty:
        max_key = get_max_key("dim_Department", "Department_Key")
        with conn.cursor() as cur:
            for i, (_, row) in enumerate(new_rows.iterrows()):
                key = max_key + i + 1
                cur.execute(
                    """INSERT INTO mdw.dim_Department
                       (Department_Key, Department_Name, Department_Location, Front_Desk_Phone)
                       VALUES (?, ?, ?, ?)""",
                    key, row["Department_Name"], row["Department_Location"],
                    row["Front_Desk_Phone"],
                )
            conn.commit()
    if progress_cb:
        progress_cb(f"dim_Department: {len(new_rows)} new department(s) inserted")
    return len(new_rows)


def upsert_dim_maintenance_job(df_csv, progress_cb=None):
    """Insert new maintenance jobs by Maintenance_Job_ID."""
    existing = query_table("dim_Maintenance_Job", "Maintenance_Job_Key")
    existing_ids = set(existing["Maintenance_Job_ID"].tolist()) if not existing.empty else set()

    job_df = df_csv.drop_duplicates(subset=["Maintenance_Job_ID"])
    new_rows = job_df[~job_df["Maintenance_Job_ID"].isin(existing_ids)]

    if not new_rows.empty:
        max_key = get_max_key("dim_Maintenance_Job", "Maintenance_Job_Key")
        with conn.cursor() as cur:
            for i, (_, row) in enumerate(new_rows.iterrows()):
                key = max_key + i + 1
                cur.execute(
                    """INSERT INTO mdw.dim_Maintenance_Job
                       (Maintenance_Job_Key, Maintenance_Job_ID, Maintenance_Job_TypeCode,
                        Maintenance_Job_Desc, IsHoliday, HourRate)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    key, row["Maintenance_Job_ID"], row["Maintenance_Job_TypeCode"],
                    row["Maintenance_Job_Desc"], int(row["IsHoliday"]),
                    float(row["HourRate"]),
                )
            conn.commit()
    if progress_cb:
        progress_cb(f"dim_Maintenance_Job: {len(new_rows)} new job type(s) inserted")
    return len(new_rows)


def upsert_dim_travel_policy(df_csv, progress_cb=None):
    """Insert new travel allowance policies by Travel_Policy_ID."""
    existing = query_table("dim_Travel_Allowance_Policy", "Travel_Allowance_Policy_Key")
    existing_ids = (
        set(existing["Travel_Allowance_Policy_ID"].tolist())
        if not existing.empty else set()
    )

    tp_df = df_csv.drop_duplicates(subset=["Travel_Policy_ID"])
    new_rows = tp_df[~tp_df["Travel_Policy_ID"].isin(existing_ids)]

    if not new_rows.empty:
        max_key = get_max_key("dim_Travel_Allowance_Policy", "Travel_Allowance_Policy_Key")
        with conn.cursor() as cur:
            for i, (_, row) in enumerate(new_rows.iterrows()):
                key = max_key + i + 1
                cur.execute(
                    """INSERT INTO mdw.dim_Travel_Allowance_Policy
                       (Travel_Allowance_Policy_Key, Travel_Allowance_Policy_ID,
                        Vehicle_Type, Allowance_Per_Km)
                       VALUES (?, ?, ?, ?)""",
                    key, row["Travel_Policy_ID"], row["Vehicle_Type"],
                    float(row["Allowance_Per_Km"]),
                )
            conn.commit()
    if progress_cb:
        progress_cb(f"dim_Travel_Allowance_Policy: {len(new_rows)} new policy(ies) inserted")
    return len(new_rows)


def upsert_dim_weather_policy(df_csv, progress_cb=None):
    """Insert new weather allowance policies by Weather_Policy_Key."""
    existing = query_table("dim_Weather_Allowance_Policy", "Weather_Allowance_Policy_Key")
    existing_keys = (
        set(existing["Policy_Key"].tolist())
        if not existing.empty else set()
    )

    wp_df = df_csv.drop_duplicates(subset=["Weather_Policy_Key"])
    new_rows = wp_df[~wp_df["Weather_Policy_Key"].isin(existing_keys)]

    if not new_rows.empty:
        max_key = get_max_key("dim_Weather_Allowance_Policy", "Weather_Allowance_Policy_Key")
        with conn.cursor() as cur:
            for i, (_, row) in enumerate(new_rows.iterrows()):
                key = max_key + i + 1
                cur.execute(
                    """INSERT INTO mdw.dim_Weather_Allowance_Policy
                       (Weather_Allowance_Policy_Key, Policy_Key, Weather,
                        Temperature, Weather_Allowance)
                       VALUES (?, ?, ?, ?, ?)""",
                    key, row["Weather_Policy_Key"], row["Weather"],
                    float(row["Temperature"]), float(row["Weather_Allowance"]),
                )
            conn.commit()
    if progress_cb:
        progress_cb(f"dim_Weather_Allowance_Policy: {len(new_rows)} new policy(ies) inserted")
    return len(new_rows)


def lookup_dimension_keys(df_csv):
    """After all dimensions are upserted, look up surrogate keys for each row."""
    # Load all dimension tables
    dim_date = query_table("dim_Date", "Date_Key")
    dim_staff = query_table("dim_Staff", "Staff_Key")
    dim_dept = query_table("dim_Department", "Department_Key")
    dim_job = query_table("dim_Maintenance_Job", "Maintenance_Job_Key")
    dim_travel = query_table("dim_Travel_Allowance_Policy", "Travel_Allowance_Policy_Key")
    dim_weather = query_table("dim_Weather_Allowance_Policy", "Weather_Allowance_Policy_Key")

    # Build lookup dicts
    date_lookup = dict(zip(dim_date["Date_Text"], dim_date["Date_Key"]))
    staff_lookup = dict(zip(dim_staff["Staff_ID"], dim_staff["Staff_Key"]))
    dept_lookup = dict(zip(dim_dept["Department_Name"], dim_dept["Department_Key"]))
    job_lookup = dict(zip(dim_job["Maintenance_Job_ID"], dim_job["Maintenance_Job_Key"]))
    travel_lookup = dict(zip(
        dim_travel["Travel_Allowance_Policy_ID"],
        dim_travel["Travel_Allowance_Policy_Key"],
    ))
    weather_lookup = dict(zip(
        dim_weather["Policy_Key"],
        dim_weather["Weather_Allowance_Policy_Key"],
    ))

    # Resolve keys for each row
    df = df_csv.copy()
    df["Date_Text"] = df["Date"].str.strip()
    df["Date_Key"] = df["Date_Text"].map(date_lookup)
    df["Staff_Key"] = df["Staff_ID"].map(staff_lookup)
    df["Department_Key"] = df["Department_Name"].map(dept_lookup)
    df["Maintenance_Job_Key"] = df["Maintenance_Job_ID"].map(job_lookup)
    df["Travel_Allowance_Policy_Key"] = df["Travel_Policy_ID"].map(travel_lookup)
    df["Weather_Allowance_Policy_Key"] = df["Weather_Policy_Key"].map(weather_lookup)

    return df


def calculate_measures(df):
    """Calculate derived measure columns for the fact table."""
    df["Maintenance_Hours"] = pd.to_numeric(df["Maintenance_Hours"], errors="coerce")
    df["HourRate"] = pd.to_numeric(df["HourRate"], errors="coerce")
    df["Length_of_Travel"] = pd.to_numeric(df["Length_of_Travel"], errors="coerce")
    df["Allowance_Per_Km"] = pd.to_numeric(df["Allowance_Per_Km"], errors="coerce")
    df["Weather_Allowance"] = pd.to_numeric(df["Weather_Allowance"], errors="coerce")
    df["IsHoliday"] = pd.to_numeric(df["IsHoliday"], errors="coerce")

    base_pay = df["Maintenance_Hours"] * df["HourRate"]
    df["HolidayPayment"] = (base_pay * 0.5 * df["IsHoliday"]).round(2)
    df["Travel_Allowance_Amount"] = (df["Length_of_Travel"] * df["Allowance_Per_Km"]).round(2)
    df["Weather_Allowance_Amount"] = df["Weather_Allowance"].round(2)
    df["Total_Amount_Paid"] = (
        base_pay + df["HolidayPayment"]
        + df["Travel_Allowance_Amount"]
        + df["Weather_Allowance_Amount"]
    ).round(2)

    return df


def insert_fact_rows(df, progress_cb=None):
    """Insert new rows into the fact table. Returns count of rows inserted."""
    max_id = get_max_key("fact_Maintenance_Contractor_Payment", "Payment_ID")

    key_cols = [
        "Date_Key", "Maintenance_Job_Key", "Staff_Key", "Department_Key",
        "Travel_Allowance_Policy_Key", "Weather_Allowance_Policy_Key",
    ]
    # Check for any unresolved keys
    for col in key_cols:
        if df[col].isna().any():
            bad_count = df[col].isna().sum()
            raise ValueError(f"Could not resolve {bad_count} row(s) for {col}. Check your CSV data.")

    inserted = 0
    with conn.cursor() as cur:
        for i, (_, row) in enumerate(df.iterrows()):
            payment_id = max_id + i + 1
            cur.execute(
                """INSERT INTO mdw.fact_Maintenance_Contractor_Payment
                   (Payment_ID, Date_Key, Maintenance_Job_Key, Staff_Key,
                    Department_Key, Travel_Allowance_Policy_Key,
                    Weather_Allowance_Policy_Key, Maintenance_Hours, HolidayPayment,
                    Length_of_Travel, Travel_Allowance_Amount, Weather_Condition,
                    Weather_Allowance_Amount, Total_Amount_Paid)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                payment_id,
                int(row["Date_Key"]),
                int(row["Maintenance_Job_Key"]),
                int(row["Staff_Key"]),
                int(row["Department_Key"]),
                int(row["Travel_Allowance_Policy_Key"]),
                int(row["Weather_Allowance_Policy_Key"]),
                float(row["Maintenance_Hours"]),
                float(row["HolidayPayment"]),
                float(row["Length_of_Travel"]),
                float(row["Travel_Allowance_Amount"]),
                str(row["Weather_Condition"]),
                float(row["Weather_Allowance_Amount"]),
                float(row["Total_Amount_Paid"]),
            )
            inserted += 1
        conn.commit()

    if progress_cb:
        progress_cb(f"fact_Maintenance_Contractor_Payment: {inserted} new row(s) inserted")
    return inserted


def detect_duplicates(df_csv):
    """
    Detect rows in the CSV that are likely duplicates of existing fact records.
    Uses a composite of (Date, Staff_ID, Maintenance_Job_ID) as a natural dedup key.
    Returns (unique_df, duplicate_df).
    """
    query = """
    SELECT d.Date_Text, s.Staff_ID, j.Maintenance_Job_ID
    FROM mdw.fact_Maintenance_Contractor_Payment f
    JOIN mdw.dim_Date d ON f.Date_Key = d.Date_Key
    JOIN mdw.dim_Staff s ON f.Staff_Key = s.Staff_Key
    JOIN mdw.dim_Maintenance_Job j ON f.Maintenance_Job_Key = j.Maintenance_Job_Key
    """
    with conn.cursor() as cur:
        cur.execute(query)
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
    existing_combos = pd.DataFrame.from_records(rows, columns=cols)

    if existing_combos.empty:
        return df_csv, pd.DataFrame()

    existing_set = set(
        zip(existing_combos["Date_Text"], existing_combos["Staff_ID"],
            existing_combos["Maintenance_Job_ID"])
    )

    df_csv["_dedup_key"] = list(zip(
        df_csv["Date"].str.strip(), df_csv["Staff_ID"], df_csv["Maintenance_Job_ID"]
    ))
    is_dup = df_csv["_dedup_key"].isin(existing_set)
    unique_df = df_csv[~is_dup].drop(columns=["_dedup_key"])
    dup_df = df_csv[is_dup].drop(columns=["_dedup_key"])

    return unique_df, dup_df


# ==========================================================================
# Page: Dashboard
# ==========================================================================

def page_dashboard():
    st.title("Maintenance Contractor Payment Dashboard")
    st.caption("Data sourced from Azure SQL Database -- schema **mdw**")

    df_raw = load_dashboard_data()

    if df_raw.empty:
        st.warning("No data found in the database. Upload data using the **Upload Data** page.")
        return

    # Ensure numeric types
    numeric_cols = [
        "Maintenance_Hours", "HolidayPayment", "Length_of_Travel",
        "Travel_Allowance_Amount", "Weather_Allowance_Amount", "Total_Amount_Paid",
        "HourRate", "Allowance_Per_Km",
    ]
    for col in numeric_cols:
        if col in df_raw.columns:
            df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

    df_raw["Base_Work_Payment"] = (
        df_raw["Total_Amount_Paid"]
        - df_raw["Travel_Allowance_Amount"]
        - df_raw["Weather_Allowance_Amount"]
        - df_raw["HolidayPayment"]
    )

    # --- Sidebar filters ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Dashboard Filters")

    departments = sorted(df_raw["Department_Name"].dropna().unique())
    selected_departments = st.sidebar.multiselect(
        "Department", departments, default=departments
    )
    staff_names = sorted(df_raw["Staff_Name"].dropna().unique())
    selected_staff = st.sidebar.multiselect(
        "Staff", staff_names, default=staff_names
    )
    years = sorted(df_raw["Year"].dropna().unique())
    selected_years = st.sidebar.multiselect(
        "Year", years, default=years
    )
    job_types = sorted(df_raw["Maintenance_Job_TypeCode"].dropna().unique())
    selected_job_types = st.sidebar.multiselect(
        "Job Type", job_types, default=job_types
    )

    df = df_raw[
        (df_raw["Department_Name"].isin(selected_departments))
        & (df_raw["Staff_Name"].isin(selected_staff))
        & (df_raw["Year"].isin(selected_years))
        & (df_raw["Maintenance_Job_TypeCode"].isin(selected_job_types))
    ].copy()

    if df.empty:
        st.info("No records match the current filters. Adjust the sidebar to see data.")
        return

    # --- KPI Metrics ---
    st.divider()
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_paid = df["Total_Amount_Paid"].sum()
    total_records = len(df)
    avg_payment = df["Total_Amount_Paid"].mean()
    total_hours = df["Maintenance_Hours"].sum()

    kpi1.metric("Total Payments", f"${total_paid:,.2f}")
    kpi2.metric("Total Records", f"{total_records:,}")
    kpi3.metric("Avg Payment / Job", f"${avg_payment:,.2f}")
    kpi4.metric("Total Maintenance Hours", f"{total_hours:,.1f} hrs")

    # --- Row 2 ---
    st.divider()
    r2l, r2r = st.columns(2)

    with r2l:
        st.subheader("Total Payment by Department")
        dept_data = (
            df.groupby("Department_Name", as_index=False)["Total_Amount_Paid"]
            .sum().sort_values("Total_Amount_Paid", ascending=False)
        )
        fig = px.bar(dept_data, x="Department_Name", y="Total_Amount_Paid",
                     color="Department_Name", color_discrete_sequence=COLOR_PALETTE,
                     template=PLOTLY_TEMPLATE,
                     labels={"Department_Name": "Department", "Total_Amount_Paid": "Total ($)"})
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with r2r:
        st.subheader("Total Payment by Month")
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]
        month_data = (
            df.groupby(["Year", "Month_Name", "Month_Number"], as_index=False)
            ["Total_Amount_Paid"].sum().sort_values(["Year", "Month_Number"])
        )
        month_data["Year"] = month_data["Year"].astype(str)
        fig = px.bar(month_data, x="Month_Name", y="Total_Amount_Paid", color="Year",
                     barmode="group", color_discrete_sequence=COLOR_PALETTE,
                     template=PLOTLY_TEMPLATE,
                     category_orders={"Month_Name": month_order},
                     labels={"Month_Name": "Month", "Total_Amount_Paid": "Total ($)"})
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    # --- Row 3 ---
    st.divider()
    r3l, r3r = st.columns(2)

    with r3l:
        st.subheader("Total Payment by Staff")
        staff_data = (
            df.groupby("Staff_Name", as_index=False)["Total_Amount_Paid"]
            .sum().sort_values("Total_Amount_Paid", ascending=True)
        )
        fig = px.bar(staff_data, x="Total_Amount_Paid", y="Staff_Name", orientation="h",
                     color="Staff_Name", color_discrete_sequence=COLOR_PALETTE,
                     template=PLOTLY_TEMPLATE,
                     labels={"Staff_Name": "Staff", "Total_Amount_Paid": "Total ($)"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with r3r:
        st.subheader("Payment Breakdown by Job Type")
        job_data = (
            df.groupby("Maintenance_Job_TypeCode", as_index=False)["Total_Amount_Paid"]
            .sum().sort_values("Total_Amount_Paid", ascending=False)
        )
        fig = px.pie(job_data, names="Maintenance_Job_TypeCode", values="Total_Amount_Paid",
                     hole=0.4, color_discrete_sequence=COLOR_PALETTE, template=PLOTLY_TEMPLATE)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    # --- Row 4 ---
    st.divider()
    r4l, r4r = st.columns(2)

    with r4l:
        st.subheader("Payment Composition by Department")
        comp_data = (
            df.groupby("Department_Name", as_index=False)[
                ["Base_Work_Payment", "Travel_Allowance_Amount",
                 "Weather_Allowance_Amount", "HolidayPayment"]
            ].sum()
        )
        comp_melted = comp_data.melt(
            id_vars="Department_Name",
            value_vars=["Base_Work_Payment", "Travel_Allowance_Amount",
                         "Weather_Allowance_Amount", "HolidayPayment"],
            var_name="Component", value_name="Amount",
        )
        label_map = {
            "Base_Work_Payment": "Base Work",
            "Travel_Allowance_Amount": "Travel Allowance",
            "Weather_Allowance_Amount": "Weather Allowance",
            "HolidayPayment": "Holiday Payment",
        }
        comp_melted["Component"] = comp_melted["Component"].map(label_map)
        fig = px.bar(comp_melted, x="Department_Name", y="Amount", color="Component",
                     barmode="stack", color_discrete_sequence=COLOR_PALETTE,
                     template=PLOTLY_TEMPLATE,
                     labels={"Department_Name": "Department", "Amount": "Amount ($)"})
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with r4r:
        st.subheader("Travel Allowance by Vehicle Type")
        veh_data = (
            df.groupby("Vehicle_Type", as_index=False)["Travel_Allowance_Amount"]
            .sum().sort_values("Travel_Allowance_Amount", ascending=False)
        )
        fig = px.bar(veh_data, x="Vehicle_Type", y="Travel_Allowance_Amount",
                     color="Vehicle_Type", color_discrete_sequence=COLOR_PALETTE,
                     template=PLOTLY_TEMPLATE,
                     labels={"Vehicle_Type": "Vehicle Type", "Travel_Allowance_Amount": "Total ($)"})
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    # --- Raw Data ---
    st.divider()
    with st.expander("View Raw Data", expanded=False):
        display_cols = [
            "Payment_ID", "Date_Text", "Month_Name", "Year",
            "Staff_Name", "Department_Name",
            "Maintenance_Job_TypeCode", "Maintenance_Job_Desc",
            "Vehicle_Type", "Weather_Condition",
            "Maintenance_Hours", "HolidayPayment",
            "Length_of_Travel", "Travel_Allowance_Amount",
            "Weather_Allowance_Amount", "Total_Amount_Paid",
        ]
        available_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available_cols], use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(df):,} records")


# ==========================================================================
# Page: Upload Data
# ==========================================================================

def page_upload():
    st.title("Upload Payment Data")
    st.caption("Upload a CSV file to extract, transform, and load data into the data warehouse.")

    # --- Instructions ---
    with st.expander("CSV Format Requirements", expanded=False):
        st.markdown("The CSV file must contain **exactly** these columns:")
        st.code(", ".join(EXPECTED_CSV_COLUMNS), language=None)
        st.markdown("""
**Column notes:**
- **Date**: format `dd/mm/yyyy`
- **IsHoliday**: `0` or `1`
- **HourRate, Allowance_Per_Km, Temperature, Weather_Allowance**: numeric values
- **Maintenance_Hours, Length_of_Travel**: numeric values

Sample files are provided in the `sample_data/` folder.
        """)

    # --- File uploader ---
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is None:
        st.info("Upload a CSV file to get started.")
        return

    # --- Parse CSV ---
    try:
        df_csv = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        return

    # --- Validate columns ---
    missing_cols = set(EXPECTED_CSV_COLUMNS) - set(df_csv.columns)
    extra_cols = set(df_csv.columns) - set(EXPECTED_CSV_COLUMNS)

    if missing_cols:
        st.error(f"Missing required columns: **{', '.join(sorted(missing_cols))}**")
        return

    if extra_cols:
        st.warning(f"Extra columns will be ignored: {', '.join(sorted(extra_cols))}")

    df_csv = df_csv[EXPECTED_CSV_COLUMNS]

    # --- Preview ---
    st.subheader("Data Preview")
    st.dataframe(df_csv, use_container_width=True, hide_index=True)
    st.caption(f"{len(df_csv)} row(s) in file")

    # --- Deduplication check ---
    st.subheader("Deduplication Check")
    unique_df, dup_df = detect_duplicates(df_csv)

    if not dup_df.empty:
        st.warning(
            f"**{len(dup_df)}** row(s) already exist in the database "
            f"(matched by Date + Staff_ID + Maintenance_Job_ID) and will be **skipped**."
        )
        with st.expander("View duplicate rows", expanded=False):
            st.dataframe(dup_df, use_container_width=True, hide_index=True)

    if unique_df.empty:
        st.info("All rows in this file are duplicates. Nothing to upload.")
        return

    st.success(f"**{len(unique_df)}** new row(s) will be processed and uploaded.")

    # --- Summary of new dimension data ---
    st.subheader("New Data Summary")
    col_a, col_b, col_c = st.columns(3)

    existing_staff = query_table("dim_Staff", "Staff_Key")
    existing_staff_ids = set(existing_staff["Staff_ID"].tolist()) if not existing_staff.empty else set()
    new_staff = unique_df[~unique_df["Staff_ID"].isin(existing_staff_ids)]["Staff_ID"].nunique()
    col_a.metric("New Staff", new_staff)

    existing_dept = query_table("dim_Department", "Department_Key")
    existing_dept_names = set(existing_dept["Department_Name"].tolist()) if not existing_dept.empty else set()
    new_dept = unique_df[~unique_df["Department_Name"].isin(existing_dept_names)]["Department_Name"].nunique()
    col_b.metric("New Departments", new_dept)

    existing_jobs = query_table("dim_Maintenance_Job", "Maintenance_Job_Key")
    existing_job_ids = set(existing_jobs["Maintenance_Job_ID"].tolist()) if not existing_jobs.empty else set()
    new_jobs = unique_df[~unique_df["Maintenance_Job_ID"].isin(existing_job_ids)]["Maintenance_Job_ID"].nunique()
    col_c.metric("New Job Types", new_jobs)

    # --- Confirm upload ---
    st.divider()
    if st.button("Confirm & Upload to Database", type="primary", use_container_width=True):
        status_container = st.container()
        progress_bar = st.progress(0)
        messages = []

        def log_msg(msg):
            messages.append(msg)
            status_container.text("\n".join(messages))

        try:
            # Step 1-6: Upsert dimensions
            log_msg("Step 1/7: Upserting dim_Date...")
            upsert_dim_date(unique_df, log_msg)
            progress_bar.progress(15)

            log_msg("Step 2/7: Upserting dim_Staff...")
            upsert_dim_staff(unique_df, log_msg)
            progress_bar.progress(28)

            log_msg("Step 3/7: Upserting dim_Department...")
            upsert_dim_department(unique_df, log_msg)
            progress_bar.progress(42)

            log_msg("Step 4/7: Upserting dim_Maintenance_Job...")
            upsert_dim_maintenance_job(unique_df, log_msg)
            progress_bar.progress(55)

            log_msg("Step 5/7: Upserting dim_Travel_Allowance_Policy...")
            upsert_dim_travel_policy(unique_df, log_msg)
            progress_bar.progress(68)

            log_msg("Step 6/7: Upserting dim_Weather_Allowance_Policy...")
            upsert_dim_weather_policy(unique_df, log_msg)
            progress_bar.progress(80)

            # Step 7: Lookup keys, calculate measures, insert fact
            log_msg("Step 7/7: Looking up keys, calculating measures, inserting fact rows...")
            keyed_df = lookup_dimension_keys(unique_df)
            keyed_df = calculate_measures(keyed_df)
            rows_inserted = insert_fact_rows(keyed_df, log_msg)
            progress_bar.progress(100)

            # Clear dashboard cache
            load_dashboard_data.clear()

            st.balloons()
            st.success(
                f"ETL completed successfully! "
                f"**{rows_inserted}** payment record(s) uploaded to the database."
            )

        except Exception as e:
            st.error(f"ETL failed: {e}")


# ==========================================================================
# Sidebar navigation
# ==========================================================================

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Upload Data"], label_visibility="collapsed")

if page == "Dashboard":
    page_dashboard()
else:
    page_upload()
