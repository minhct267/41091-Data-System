from __future__ import annotations

import os

import pyodbc
import streamlit as st


def _build_conn_str():
    username = os.getenv("USERNAME_AZURE")
    password = os.getenv("PASSWORD")
    server = os.getenv("SERVER")
    database = os.getenv("DATABASE")

    missing = [
        name for name, value in (
            ("USERNAME_AZURE", username),
            ("PASSWORD", password),
            ("SERVER", server),
            ("DATABASE", database),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Missing required environment variables in .env: "
            + ", ".join(missing)
        )

    host = server.strip()
    if not host.lower().startswith("tcp:"):
        host = f"tcp:{host},1433"

    return (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={host};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=60;"
    )


@st.cache_resource(show_spinner="Connecting to Azure SQL...")
def get_connection():
    return pyodbc.connect(_build_conn_str())
