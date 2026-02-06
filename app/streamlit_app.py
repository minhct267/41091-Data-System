import streamlit as st
import pyodbc
import pandas as pd


st.set_page_config(page_title="Azure SQL Database Explorer", layout="wide")
st.title("Azure SQL Database Explorer")


# Initialize connection.
# Uses st.cache_resource to only run once.
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


# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
    return columns, rows


# Query mdw.dim_Department
st.header("mdw.dim_Department")

columns, rows = run_query("SELECT * FROM mdw.dim_Department")
df = pd.DataFrame.from_records(rows, columns=columns)

st.dataframe(df, use_container_width=True)
st.caption(f"Total rows: {len(df)}")
