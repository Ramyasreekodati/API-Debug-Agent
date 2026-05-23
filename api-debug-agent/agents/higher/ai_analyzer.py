import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Attempt to import OpenAI; if unavailable, provide a mock fallback.
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
import json


def _get_client():
    """Create an OpenAI client using the API key from environment.
    Returns None if the key is missing or the library is unavailable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None
    return OpenAI(api_key=api_key)


def analyze_logs(log_text: str) -> str:
    """Send the raw log text to the LLM and return a concise analysis.

    The prompt asks the model to identify:
      * Root causes of failures
      * Recurring error patterns
      * Performance bottlenecks (high latency)
      * Suggested debugging steps or mitigations
    """
    client = _get_client()
    if client is None:
        # Simple deterministic fallback for demo purposes
        return (
            "**AI analysis not available** – missing OpenAI API key or library.\n"
            "You can still see metrics and charts. To enable AI insights, set the ``OPENAI_API_KEY`` environment variable."
        )

    # Enrich logs using Google API keys (placeholder implementation)
    try:
        from .google_enricher import enrich_logs
        enrichment = enrich_logs(log_text)
        enrichment_str = (
            f"\n\n---\nEnrichment data (Google key used): {enrichment['selected_google_key']}"
            f"\nKeyword counts: {enrichment['keyword_counts']}"
            f"\nDetected entities: {enrichment['detected_entities']}"
        )
    except Exception:
        enrichment_str = ""

    prompt = f"""
    Analyze the following API logs and generate a professional production incident report using EXACTLY the markdown format below:

    # AI Root Cause Analysis Report
    
    ## System Health Summary
    
    ## Critical Findings
    
    ## Probable Root Causes
    
    ## Infrastructure Risks
    
    ## Recommended Engineering Fixes
    
    ## Monitoring Recommendations
    
    ## Incident Severity
    
    Logs:
    {log_text}
    {enrichment_str}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        err_msg = str(e)
        # If quota exceeded, attempt a cheaper model first
        if 'insufficient_quota' in err_msg.lower():
            # Try gpt-3.5-turbo as a lower‑cost alternative
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                )
                return response.choices[0].message.content.strip()
            except Exception:
                # Enhanced fallback analysis with detailed report
                fallback = []
                # Header
                fallback.append("# AI Root Cause Analysis Report")
                # System Health Summary (insufficient evidence for numeric metrics)
                fallback.append("## System Health Summary")
                fallback.append("- Total Requests: Insufficient evidence in logs.")
                fallback.append("- Total Errors: Insufficient evidence in logs.")
                fallback.append("- Error Rate: Insufficient evidence in logs.")
                fallback.append("- Average Latency: Insufficient evidence in logs.")
                # Critical Findings based on keyword counts
                fallback.append("## Critical Findings")
                keyword_counts_str = json.dumps(enrichment.get('keyword_counts', {}), indent=2)
                fallback.append(f"- Keyword frequencies:\n{keyword_counts_str}")
                # Probable Root Causes
                fallback.append("## Probable Root Causes")
                # Analyze common keywords
                keyword_counts = enrichment.get('keyword_counts', {})
                if keyword_counts.get('timeout', 0) > 0:
                    fallback.append("- High occurrence of 'timeout' suggests request timeout issues or slow downstream services.")
                if keyword_counts.get('database', 0) > 0:
                    fallback.append("- Mentions of 'database' indicate possible DB latency or connection problems.")
                if keyword_counts.get('gateway', 0) > 0:
                    fallback.append("- 'gateway' references hint at API gateway instability or upstream dependency failures.")
                if keyword_counts.get('error', 0) > 0:
                    fallback.append("- General 'error' occurrences reflect error responses across endpoints.")
                # Infrastructure Risks
                fallback.append("## Infrastructure Risks")
                fallback.append("- Potential cascading failures if timeout and gateway issues are not mitigated.")
                # Recommended Engineering Fixes
                fallback.append("## Recommended Engineering Fixes")
                fallback.append("- Implement retry and exponential backoff for timeout‑prone calls.")
                fallback.append("- Review database connection pooling and query performance.")
                fallback.append("- Add circuit breakers and health checks around gateway services.")
                # Monitoring Recommendations
                fallback.append("## Monitoring Recommendations")
                fallback.append("- Set alerts for timeout rate > 5% and error rate > 10%.")
                fallback.append("- Track per‑endpoint latency and error metrics.")
                # Incident Severity (simple heuristic)
                fallback.append("## Incident Severity")
                total_errors = keyword_counts.get('error', 0) + keyword_counts.get('failed', 0)
                if total_errors > 20:
                    severity = "HIGH"
                elif total_errors > 10:
                    severity = "MEDIUM"
                else:
                    severity = "LOW"
                fallback.append(f"- Severity: {severity} (based on error keyword frequency).")
                # Append logs and enrichment
                fallback.append("\nLogs:\n")
                fallback.append(log_text)
                if enrichment_str:
                    fallback.append("\nEnrichment:\n")
                    fallback.append(enrichment_str)
                return "\n".join(fallback)
        # Other errors or quota fallback failed
        return f"**AI analysis failed**: {e}"
