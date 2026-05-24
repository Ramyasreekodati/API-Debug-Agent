import os
import json
from openai import OpenAI

# Load OpenAI key from .env (or environment)
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise EnvironmentError("OPENAI_API_KEY not set in environment")
client = OpenAI(api_key=openai_key)

def get_root_cause(log_text: str) -> str:
    """Generate a concise root‑cause explanation for the given API logs.

    Parameters
    ----------
    log_text: str
        The raw logs as a single string.
    Returns
    -------
    str
        A short paragraph describing the most likely causes of failures.
    """
    prompt = f"""
    Analyze the following API logs and provide a concise root‑cause analysis. Highlight the most common error types, failing endpoints, and any patterns indicating underlying issues (e.g., database timeouts, service overload, misconfiguration).

    Logs:
    {log_text}
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()
