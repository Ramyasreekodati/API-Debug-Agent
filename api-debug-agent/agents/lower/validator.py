import re
from typing import List, Tuple

def validate_log_line(line: str) -> Tuple[bool, str]:
    """Validate a single log line.

    Returns a tuple (is_valid, error_message). If valid, error_message is empty.
    Checks:
    - Timestamp format ``YYYY-MM-DD HH:MM:SS``
    - Level is ONE of INFO, ERROR, WARNING, DEBUG
    - Status is an integer (e.g., 200, 404, 500)
    - Latency ends with ``ms``
    """
    line = line.strip()
    if not line:
        return False, "Empty line"
    parts = line.split(maxsplit=5)
    if len(parts) < 5:
        return False, "Insufficient parts"
    timestamp, _, level, _, status = parts[:5]
    # Timestamp format
    if not re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", timestamp):
        return False, f"Invalid timestamp '{timestamp}'"
    if level not in {"INFO", "ERROR", "WARNING", "DEBUG"}:
        return False, f"Unknown level '{level}'"
    if not status.isdigit():
        return False, f"Status not numeric '{status}'"
    # Latency check (optional, if present)
    if len(parts) > 5:
        latency_part = parts[5]
        if not re.search(r"\d+ms", latency_part):
            return False, f"Latency missing or malformed in '{latency_part}'"
    return True, ""

def filter_valid_logs(lines: List[str]) -> List[str]:
    """Return only lines that pass :func:`validate_log_line`.
    Invalid lines are silently dropped.
    """
    valid = []
    for line in lines:
        ok, _ = validate_log_line(line)
        if ok:
            valid.append(line)
    return valid
