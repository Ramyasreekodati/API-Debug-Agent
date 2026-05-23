import os
from openai import OpenAI

def suggest_fixes(root_cause: str) -> str:
    """Generate concrete fix suggestions given a root‑cause description.
    Uses the OpenAI API (key read from .env).
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment")
    client = OpenAI(api_key=api_key)
    prompt = f"You are an expert backend engineer. Based on the following root cause, propose concise, actionable fix steps (max 5 bullet points).\n\nRoot cause:\n{root_cause}\n"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()
