import pandas as pd
import plotly.express as px
from typing import Tuple, Dict


def compute_metrics(df: pd.DataFrame) -> Dict[str, any]:
    """Calculate key metrics from the parsed log DataFrame.

    Returns a dictionary with:
        total_requests, total_errors, error_rate, avg_latency, most_failing_endpoint
    """
    total_requests = len(df)
    error_mask = df["status"] >= 400
    total_errors = error_mask.sum()
    error_rate = (total_errors / total_requests) * 100 if total_requests else 0
    avg_latency = df["latency_ms"].mean()
    # most failing endpoint based on error count
    if total_errors:
        failing_counts = df[error_mask]["endpoint"].value_counts()
        most_failing_endpoint = failing_counts.idxmax()
    else:
        most_failing_endpoint = None
    return {
        "total_requests": total_requests,
        "total_errors": int(total_errors),
        "error_rate": round(error_rate, 2),
        "avg_latency": round(avg_latency, 2) if pd.notnull(avg_latency) else None,
        "most_failing_endpoint": most_failing_endpoint,
    }


def create_status_histogram(df: pd.DataFrame):
    fig = px.histogram(df, x="status", nbins=20, title="Status Code Distribution")
    fig.update_layout(bargap=0.1)
    return fig


def create_endpoint_error_bar(df: pd.DataFrame):
    error_df = df[df["status"] >= 400]
    if error_df.empty:
        return None
    counts = error_df["endpoint"].value_counts().reset_index()
    counts.columns = ["endpoint", "error_count"]
    fig = px.bar(counts, x="endpoint", y="error_count", title="Errors per Endpoint")
    return fig



def create_status_pie(df: pd.DataFrame):
    """Create a pie chart showing distribution of HTTP status codes."""
    fig = px.pie(df, names="status", title="Status Code Distribution")
    fig.update_traces(textinfo="percent+label")
    return fig


def create_latency_box(df: pd.DataFrame):
    """Box plot for latency distribution."""
    fig = px.box(df, y="latency_ms", title="Latency Distribution (ms)")
    return fig


def detect_top_issues(df: pd.DataFrame) -> list:
    """Detect common issues based on logs.
    Returns list of issue strings.
    """
    issues = []
    # Timeout spikes: latency > 2000ms
    timeout_spikes = df[df["latency_ms"] > 2000]
    if not timeout_spikes.empty:
        issues.append("Database timeout spikes")
    # Gateway failures: status >= 502
    gateway_failures = df[df["status"] >= 502]
    if not gateway_failures.empty:
        issues.append("API gateway instability")
    # Elevated latency overall (avg > 1000ms)
    if df["latency_ms"].mean() > 1000:
        issues.append("Elevated latency")
    # Repeated failures in payment services
    if "endpoint" in df.columns:
        payment_errors = df[(df["endpoint"].str.contains("payment", case=False)) & (df["status"] >= 400)]
        if not payment_errors.empty:
            issues.append("Repeated failures in payment services")
    return issues
