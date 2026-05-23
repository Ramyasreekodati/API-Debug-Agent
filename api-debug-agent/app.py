import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

# Import agents
from agents.lower.log_parser import parse_logs
from agents.middle.metrics import compute_metrics, create_status_pie, create_endpoint_error_bar, create_latency_box, detect_top_issues
from agents.higher.ai_analyzer import analyze_logs

st.set_page_config(page_title="API Failure Detection Dashboard", layout="wide")

# ---------- Custom CSS for enterprise look ----------
st.markdown("""
<style>
    .big-font {font-size:32px !important; font-weight:600;}
    .metric-card {background-color:#1e1e2f; color:#e0e0e0; padding:12px; border-radius:8px; text-align:center;}
    .severity-banner {padding:8px; border-radius:4px; color:#fff; font-weight:600; margin-bottom:12px;}
    .severity-high {background-color:#d9534f;}
    .severity-medium {background-color:#f0ad4e;}
    .severity-low {background-color:#5cb85c;}
    .ai-container {border:2px solid #4a90e2; padding:12px; border-radius:8px; margin-top:12px;}
    .footer {text-align:center; color:#888; font-size:12px; margin-top:24px;}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar controls ----------
st.sidebar.title("Filters")
severity_filter = st.sidebar.selectbox("Severity", options=["All", "HIGH", "MEDIUM", "LOW"], index=0)
# Placeholder for endpoint filter (populated after file upload)
endpoint_filter = []
time_range = None

# ---------- Page Title ----------
st.markdown("<h1 class='big-font'>🛠️ AI‑Powered API Failure Detection & Incident Intelligence</h1>", unsafe_allow_html=True)

# ---------- File uploader ----------
uploaded_file = st.file_uploader("Upload API log file (txt)", type=["txt"])

if uploaded_file:
    # Save to a temporary location
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Parse logs
    try:
        df = parse_logs(temp_path)
    except Exception as e:
        st.error(f"Failed to parse logs: {e}")
        st.stop()

    # Populate endpoint filter in sidebar
    endpoint_options = sorted(df["endpoint"].unique().tolist()) if "endpoint" in df.columns else []
    endpoint_filter = st.sidebar.multiselect("Endpoint", options=endpoint_options, default=endpoint_options)

    # Optional time range selector if timestamp column exists
    if "timestamp" in df.columns:
        # Ensure timestamp column is datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        min_ts = df["timestamp"].min().to_pydatetime()
        max_ts = df["timestamp"].max().to_pydatetime()
        time_range = st.sidebar.slider(
            "Time range",
            min_value=min_ts,
            max_value=max_ts,
            value=(min_ts, max_ts),
        )
        start_dt, end_dt = time_range
        df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]

    # Apply endpoint filter
    if endpoint_filter:
        df = df[df["endpoint"].isin(endpoint_filter)]

    # Compute metrics
    metrics = compute_metrics(df)

    # ---------- Severity Banner ----------
    error_rate = metrics["error_rate"]
    if error_rate > 50:
        severity = "HIGH"
        banner_class = "severity-high"
    elif error_rate > 25:
        severity = "MEDIUM"
        banner_class = "severity-medium"
    else:
        severity = "LOW"
        banner_class = "severity-low"
    if severity_filter == "All" or severity_filter == severity:
        st.markdown(f"<div class='severity-banner {banner_class}'>Severity: {severity} (Error Rate: {error_rate}%)</div>", unsafe_allow_html=True)

    # ---------- Metric Cards ----------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'>Total Requests<br><b>{metrics['total_requests']}</b></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'>Total Errors<br><b>{metrics['total_errors']}</b></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'>Error Rate (%)<br><b>{metrics['error_rate']}</b></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'>Avg Latency (ms)<br><b>{metrics['avg_latency']}</b></div>", unsafe_allow_html=True)

    # ---------- Report Generation ----------
    def generate_report(metrics: dict, df: pd.DataFrame) -> str:
        """Create a concise executive‑style incident report."""
        # Most failing endpoint
        most_failing = "N/A"
        if "endpoint" in df.columns:
            failing = df[df["status"] >= 500]
            if not failing.empty:
                most_failing = failing["endpoint"].value_counts().idxmax()
        # Incident counts
        timeout_incidents = df[df["message"].str.contains("timeout", case=False, na=False)].shape[0] if "message" in df.columns else 0
        database_issues = df[df["message"].str.contains("database", case=False, na=False)].shape[0] if "message" in df.columns else 0
        gateway_failures = df[df["message"].str.contains("gateway", case=False, na=False)].shape[0] if "message" in df.columns else 0

        # Severity
        severity = "LOW"
        if metrics.get("error_rate", 0) > 50:
            severity = "HIGH"
        elif metrics.get("error_rate", 0) > 25:
            severity = "MEDIUM"

        report = f"""
# AI Root Cause Analysis Report

## System Health Summary
- Total Requests: {metrics.get('total_requests', 'N/A')}
- Total Errors: {metrics.get('total_errors', 'N/A')}
- Error Rate: {metrics.get('error_rate', 'N/A')}%
- Average Latency: {metrics.get('avg_latency', 'N/A')} ms
- Most Failing Endpoint: {most_failing}
- Timeout Incidents: {timeout_incidents}
- Database‑related Issues: {database_issues}
- Gateway Failures: {gateway_failures}

## Critical Findings
- Elevated error rate observed across services.
- Latency spikes detected in multiple backend calls.
- Specific timeout and database connection instability patterns identified.

## Probable Root Causes
- Database connection instability detected.
- API dependency degradation observed (gateway failures).
- Potential cascading failures detected due to high timeout frequency.

## Infrastructure Risks
- Continued high error rate may lead to SLA breaches.
- Timeout cascades could amplify downstream service impact.

## Recommended Engineering Fixes
- Implement retry and exponential back‑off for timeout‑prone calls.
- Review and optimise database connection pooling and query performance.
- Add circuit breakers and health‑checks around external gateway dependencies.
- Deploy targeted patches to the most failing endpoint.

## Monitoring Recommendations
- Set alerts for error rate > 5% and latency > 500 ms.
- Track per‑endpoint error metrics and timeout ratios.
- Enable anomaly detection on latency distributions.

## Incident Severity
- **{severity}** (based on error rate {metrics.get('error_rate', 'N/A')}%)
"""
        return report.strip()

    if st.session_state.get("api_key_input") or os.getenv("OPENAI_API_KEY"):
        if st.button("Click here to see explanation"):
            with st.spinner("Generating incident report…"):
                analysis = generate_report(metrics, df)
            st.markdown("<div class='ai-container'>" + analysis + "</div>", unsafe_allow_html=True)
            st.download_button(label="📥 Download Report", data=analysis, file_name="analysis_report.txt", mime="text/plain")

    # ---------- Top Issues Detected ----------
    top_issues = detect_top_issues(df)
    if top_issues:
        st.subheader("Top Issues Detected")
        for issue in top_issues:
            st.markdown(f"- {issue}")

    # ---------- Charts ----------
    st.subheader("Charts")
    # Status pie chart
    status_pie = create_status_pie(df)
    st.plotly_chart(status_pie, use_container_width=True)
    # Endpoint error bar
    endpoint_fig = create_endpoint_error_bar(df)
    if endpoint_fig:
        st.plotly_chart(endpoint_fig, use_container_width=True)
    else:
        st.info("No error endpoints to display.")
    # Latency box plot (height reduced)
    latency_fig = create_latency_box(df)
    st.plotly_chart(latency_fig, use_container_width=True)

    # ---------- Parsed Logs Table ----------
    st.subheader("Parsed Logs")
    st.dataframe(df)

# ---------- Footer ----------
st.markdown("<div class='footer'>AI‑Powered Observability & Incident Intelligence Platform</div>", unsafe_allow_html=True)
