import streamlit as st
import pandas as pd
from agents.lower.log_parser import parse_logs
from agents.middle.metrics import compute_metrics


def main():
    st.title("📊 Overview")
    uploaded_file = st.file_uploader("Upload API log file (txt)", type=["txt"]))
    if not uploaded_file:
        st.info("Upload a log file to see metrics.")
        return
    # Save temporarily
    temp_path = f"temp/{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Parse logs and store in session state
    df = parse_logs(temp_path)
    st.session_state['uploaded_path'] = temp_path
    st.session_state['df'] = df
    metrics = compute_metrics(df)
    # Display key cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'>Total Requests<br><b>{metrics.get('total_requests','-')}</b></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'>Total Errors<br><b>{metrics.get('total_errors','-')}</b></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'>Error Rate (%)<br><b>{metrics.get('error_rate','-')}</b></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'>Avg Latency (ms)<br><b>{metrics.get('avg_latency','-')}</b></div>", unsafe_allow_html=True)
