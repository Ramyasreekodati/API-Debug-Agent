import re

def clean_log_line(line: str) -> str:
    """Standardize a log line by stripping extra whitespace and normalizing timestamps.

    Returns the cleaned line or an empty string if the line is invalid.
    """
    line = line.strip()
    if not line:
        return ""
    # Replace multiple spaces with a single space
    line = re.sub(r"\s+", " ", line)
    # Ensure timestamp format is ISO-like (YYYY-MM-DD HH:MM:SS)
    # Simple check: first 19 characters should match pattern
    timestamp_candidate = line[:19]
    if not re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", timestamp_candidate):
        # Try to fix common mistake: replace '/' with '-'
        fixed_ts = timestamp_candidate.replace('/', '-')
        if re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", fixed_ts):
            line = fixed_ts + line[19:]
    return line
