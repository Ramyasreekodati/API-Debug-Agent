import streamlit as st
import pandas as pd
from agents.lower.log_parser import parse_logs

def generate_ai_insight(df: pd.DataFrame) -> str:
    """Placeholder for AI-driven incident analysis.
    In a real implementation this would call an LLM with the log data.
    Here we return a summary based on simple heuristics.
    """
    if df.empty:
        return "No data to analyze."
    total = len(df)
    errors = df.get('error_code').notna().sum() if 'error_code' in df.columns else 0
    error_rate = (errors / total) * 100 if total else 0
    top_endpoints = df['endpoint'].value_counts().head(3) if 'endpoint' in df.columns else pd.Series()
    summary = (
        f"**Log Summary**\n"
        f"- Total requests: {total}\n"
        f"- Total errors: {errors} ({error_rate:.1f}% error rate)\n"
    )
    if not top_endpoints.empty:
        summary += "- Top endpoints:\n"
        for ep, cnt in top_endpoints.items():
            summary += f"  - {ep}: {cnt} requests\n"
    return summary


def main():
    st.title("🤖 AI Incident Report")
    # Ensure a log file has been uploaded
    if 'uploaded_path' not in st.session_state:
        st.warning("Please upload a log file on the Overview page first.")
        return
    # Load or re‑parse DataFrame
    if 'df' in st.session_state:
        df = st.session_state['df']
    else:
        df = parse_logs(st.session_state['uploaded_path'])
        st.session_state['df'] = df
    # Generate and display AI insight
    insight = generate_ai_insight(df)
    st.markdown(insight)
    # Optional expandable raw data view
    with st.expander("Show raw parsed logs"):
        st.dataframe(df)
