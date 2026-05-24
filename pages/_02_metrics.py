import streamlit as st
import pandas as pd
from agents.lower.log_parser import parse_logs
from agents.middle.metrics import compute_metrics

def main():
    st.title("📈 Metrics")
    # Ensure a log file has been uploaded
    if 'uploaded_path' not in st.session_state:
        st.warning("Please upload a log file on the Overview page first.")
        return
    # Load DataFrame from session state or re-parse if missing
    if 'df' in st.session_state:
        df = st.session_state['df']
    else:
        df = parse_logs(st.session_state['uploaded_path'])
        st.session_state['df'] = df
    # Compute metrics
    metrics = compute_metrics(df)
    # Show detailed tables and charts
    st.subheader("Requests Over Time")
    if not df.empty:
        # Convert timestamp column to datetime if present
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            time_series = df.groupby(pd.Grouper(key='timestamp', freq='5T')).size().reset_index(name='requests')
            st.line_chart(time_series.rename(columns={"timestamp": "index"}).set_index('index'))
        else:
            st.info("Timestamp column not found; cannot plot time series.")
    st.subheader("Error Heatmap")
    if 'error_code' in df.columns:
        heat_data = df.pivot_table(index='endpoint', columns='error_code', aggfunc='size', fill_value=0)
        st.write(heat_data)
    else:
        st.info("Error code column not found; no heatmap available.")
    st.subheader("Top Endpoints")
    if 'endpoint' in df.columns:
        top_endpoints = df['endpoint'].value_counts().head(10)
        st.bar_chart(top_endpoints)
    else:
        st.info("Endpoint column not found; cannot display top endpoints.")
