import streamlit as st
import os
from pathlib import Path
import pandas as pd
from auth.auth import login
login()

# Load custom CSS
css_path = Path(__file__).parents[1] / "static" / "styles.css"
if css_path.is_file():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Simple sidebar navigation (optional if using Streamlit pages)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Metrics", "AI Report", "Settings"])

# Route to selected page (import lazily)
if page == "Overview":
    from pages import _01_overview as page_mod
elif page == "Metrics":
    from pages import _02_metrics as page_mod
elif page == "AI Report":
    from pages import _03_ai_report as page_mod
else:
    from pages import _04_settings as page_mod

page_mod.main()
