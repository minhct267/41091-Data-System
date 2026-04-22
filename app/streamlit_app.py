import streamlit as st

st.set_page_config(
    page_title="Tutorial Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

with st.sidebar:
    if st.button("Refresh cached data", use_container_width=True):
        st.cache_data.clear()
        st.toast("Cache cleared. Pages will re-query the database on next load.")

pages = [
    st.Page("dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True),
    st.Page("visualizations.py", title="Visualizations", icon=":material/insights:"),
]

st.navigation(pages).run()
