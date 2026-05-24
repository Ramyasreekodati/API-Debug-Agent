import plotly.express as px
import pandas as pd


def generate_status_histogram(df: pd.DataFrame):
    """Create a histogram of HTTP status codes."""
    fig = px.histogram(df, x="status", nbins=20, title="Status Code Distribution")
    fig.update_layout(bargap=0.1)
    return fig


def generate_endpoint_error_bar(df: pd.DataFrame):
    """Bar chart of error counts per endpoint."""
    error_df = df[df["status"] >= 400]
    if error_df.empty:
        return None
    counts = error_df["endpoint"].value_counts().reset_index()
    counts.columns = ["endpoint", "error_count"]
    fig = px.bar(counts, x="endpoint", y="error_count", title="Errors per Endpoint")
    return fig


def generate_latency_box(df: pd.DataFrame):
    """Box plot of latency distribution."""
    fig = px.box(df, y="latency_ms", title="Latency Distribution (ms)")
    return fig
