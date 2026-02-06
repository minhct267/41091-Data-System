import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Maintenance Contractor Payment Dashboard",
    page_icon="wrench",
    layout="wide",
)

# Consistent color palette
COLOR_PALETTE = px.colors.qualitative.Set2
PLOTLY_TEMPLATE = "plotly_white"

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

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


@st.cache_data(ttl=600)
def load_data():
    """Load the full joined fact + dimension data (cached for 10 min)."""
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


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df_raw = load_data()

if df_raw.empty:
    st.warning("No data found in the database. Please check the data warehouse.")
    st.stop()

# Ensure numeric types
numeric_cols = [
    "Maintenance_Hours", "HolidayPayment", "Length_of_Travel",
    "Travel_Allowance_Amount", "Weather_Allowance_Amount", "Total_Amount_Paid",
    "HourRate", "Allowance_Per_Km",
]
for col in numeric_cols:
    if col in df_raw.columns:
        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

# Compute base work payment (Total - Travel - Weather - Holiday)
df_raw["Base_Work_Payment"] = (
    df_raw["Total_Amount_Paid"]
    - df_raw["Travel_Allowance_Amount"]
    - df_raw["Weather_Allowance_Amount"]
    - df_raw["HolidayPayment"]
)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.title("Filters")

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

# Apply filters
df = df_raw[
    (df_raw["Department_Name"].isin(selected_departments))
    & (df_raw["Staff_Name"].isin(selected_staff))
    & (df_raw["Year"].isin(selected_years))
    & (df_raw["Maintenance_Job_TypeCode"].isin(selected_job_types))
].copy()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("Maintenance Contractor Payment Dashboard")
st.caption("Data sourced from Azure SQL Database — schema **mdw**")

if df.empty:
    st.info("No records match the current filters. Adjust the sidebar to see data.")
    st.stop()

# ---------------------------------------------------------------------------
# Row 1 — KPI Metrics
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Row 2 — Payment by Department | Payment by Month
# ---------------------------------------------------------------------------
st.divider()
row2_left, row2_right = st.columns(2)

with row2_left:
    st.subheader("Total Payment by Department")
    dept_data = (
        df.groupby("Department_Name", as_index=False)["Total_Amount_Paid"]
        .sum()
        .sort_values("Total_Amount_Paid", ascending=False)
    )
    fig_dept = px.bar(
        dept_data,
        x="Department_Name",
        y="Total_Amount_Paid",
        color="Department_Name",
        color_discrete_sequence=COLOR_PALETTE,
        template=PLOTLY_TEMPLATE,
        labels={"Department_Name": "Department", "Total_Amount_Paid": "Total ($)"},
    )
    fig_dept.update_layout(showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig_dept, use_container_width=True)

with row2_right:
    st.subheader("Total Payment by Month")
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    month_data = (
        df.groupby(["Year", "Month_Name", "Month_Number"], as_index=False)["Total_Amount_Paid"]
        .sum()
        .sort_values(["Year", "Month_Number"])
    )
    month_data["Year"] = month_data["Year"].astype(str)
    fig_month = px.bar(
        month_data,
        x="Month_Name",
        y="Total_Amount_Paid",
        color="Year",
        barmode="group",
        color_discrete_sequence=COLOR_PALETTE,
        template=PLOTLY_TEMPLATE,
        category_orders={"Month_Name": month_order},
        labels={"Month_Name": "Month", "Total_Amount_Paid": "Total ($)", "Year": "Year"},
    )
    fig_month.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig_month, use_container_width=True)

# ---------------------------------------------------------------------------
# Row 3 — Payment by Staff | Payment by Job Type
# ---------------------------------------------------------------------------
st.divider()
row3_left, row3_right = st.columns(2)

with row3_left:
    st.subheader("Total Payment by Staff")
    staff_data = (
        df.groupby("Staff_Name", as_index=False)["Total_Amount_Paid"]
        .sum()
        .sort_values("Total_Amount_Paid", ascending=True)
    )
    fig_staff = px.bar(
        staff_data,
        x="Total_Amount_Paid",
        y="Staff_Name",
        orientation="h",
        color="Staff_Name",
        color_discrete_sequence=COLOR_PALETTE,
        template=PLOTLY_TEMPLATE,
        labels={"Staff_Name": "Staff", "Total_Amount_Paid": "Total ($)"},
    )
    fig_staff.update_layout(showlegend=False)
    st.plotly_chart(fig_staff, use_container_width=True)

with row3_right:
    st.subheader("Payment Breakdown by Job Type")
    job_data = (
        df.groupby("Maintenance_Job_TypeCode", as_index=False)["Total_Amount_Paid"]
        .sum()
        .sort_values("Total_Amount_Paid", ascending=False)
    )
    fig_job = px.pie(
        job_data,
        names="Maintenance_Job_TypeCode",
        values="Total_Amount_Paid",
        hole=0.4,
        color_discrete_sequence=COLOR_PALETTE,
        template=PLOTLY_TEMPLATE,
    )
    fig_job.update_traces(textposition="inside", textinfo="percent+label")
    fig_job.update_layout(showlegend=True)
    st.plotly_chart(fig_job, use_container_width=True)

# ---------------------------------------------------------------------------
# Row 4 — Payment Composition | Travel Allowance by Vehicle Type
# ---------------------------------------------------------------------------
st.divider()
row4_left, row4_right = st.columns(2)

with row4_left:
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
        var_name="Component",
        value_name="Amount",
    )
    label_map = {
        "Base_Work_Payment": "Base Work",
        "Travel_Allowance_Amount": "Travel Allowance",
        "Weather_Allowance_Amount": "Weather Allowance",
        "HolidayPayment": "Holiday Payment",
    }
    comp_melted["Component"] = comp_melted["Component"].map(label_map)
    fig_comp = px.bar(
        comp_melted,
        x="Department_Name",
        y="Amount",
        color="Component",
        barmode="stack",
        color_discrete_sequence=COLOR_PALETTE,
        template=PLOTLY_TEMPLATE,
        labels={"Department_Name": "Department", "Amount": "Amount ($)"},
    )
    fig_comp.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig_comp, use_container_width=True)

with row4_right:
    st.subheader("Travel Allowance by Vehicle Type")
    vehicle_data = (
        df.groupby("Vehicle_Type", as_index=False)["Travel_Allowance_Amount"]
        .sum()
        .sort_values("Travel_Allowance_Amount", ascending=False)
    )
    fig_vehicle = px.bar(
        vehicle_data,
        x="Vehicle_Type",
        y="Travel_Allowance_Amount",
        color="Vehicle_Type",
        color_discrete_sequence=COLOR_PALETTE,
        template=PLOTLY_TEMPLATE,
        labels={"Vehicle_Type": "Vehicle Type", "Travel_Allowance_Amount": "Total ($)"},
    )
    fig_vehicle.update_layout(showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig_vehicle, use_container_width=True)

# ---------------------------------------------------------------------------
# Row 5 — Raw Data Table
# ---------------------------------------------------------------------------
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
