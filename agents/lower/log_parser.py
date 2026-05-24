import pandas as pd
import re
from typing import List


def parse_logs(file_path: str) -> pd.DataFrame:
    """Parse API log lines into a Pandas DataFrame.

    Expected log format:
        <date> <time> <LEVEL> <endpoint> <status> <latency>ms [optional message]
    Example:
        2026-05-23 10:01:25 ERROR /payment 500 3200ms Database timeout
    """
    logs: List[dict] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # split first 5 whitespace‑separated parts, rest is message
            parts = line.split(maxsplit=5)
            if len(parts) < 5:
                continue
            date, time, level, endpoint, status = parts[:5]
            # latency includes "ms"
            latency_part = parts[5] if len(parts) > 5 else ""
            # latency may be followed by a message; extract leading number
            latency_match = re.match(r"(\d+)ms", latency_part)
            latency = int(latency_match.group(1)) if latency_match else None
            # optional message after latency
            message = latency_part[latency_match.end():].strip() if latency_match and latency_match.end() < len(latency_part) else ""
            logs.append({
                "timestamp": f"{date} {time}",
                "level": level,
                "endpoint": endpoint,
                "status": int(status),
                "latency_ms": latency,
                "message": message,
            })
    df = pd.DataFrame(logs)
    # Ensure proper dtypes
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df
