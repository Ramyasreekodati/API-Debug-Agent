import os
import json
import urllib.request
from typing import List, Dict

# Load all Google API keys from the environment (prefixed with GOOGLE_API_KEY_)
def _load_google_keys() -> List[str]:
    keys = []
    for i in range(1, 10):  # up to 9 keys
        key = os.getenv(f'GOOGLE_API_KEY_{i}')
        if key:
            keys.append(key)
    return keys

_GOOGLE_KEYS = _load_google_keys()

def _pick_key() -> str:
    """Select a Google API key (simple random choice)."""
    if not _GOOGLE_KEYS:
        raise RuntimeError('No Google API keys found in environment')
    return _GOOGLE_KEYS[0]  # use the first key for API calls

def _call_entity_analysis(log_text: str, api_key: str) -> List[Dict[str, any]]:
    """Call Google Cloud Natural Language API to extract entities.
    Returns a list of entity dicts as returned by the API.
    """
    url = f"https://language.googleapis.com/v1/documents:analyzeEntities?key={api_key}"
    payload = {
        "document": {"type": "PLAIN_TEXT", "content": log_text},
        "encodingType": "UTF8"
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        resp_data = json.loads(resp.read().decode('utf-8'))
    return resp_data.get('entities', [])

def enrich_logs(log_text: str) -> Dict[str, any]:
    """Enrich logs using Google Cloud NL entity extraction.
    Returns a dict containing keyword counts, detected entities, and the API key used.
    """
    # Simple keyword count (same as placeholder)
    keywords = ['timeout', 'database', 'gateway', 'error', 'exception', 'failed']
    counts = {kw: log_text.lower().count(kw) for kw in keywords}
    # Call Google NL for richer entity extraction (may fail gracefully)
    try:
        api_key = _pick_key()
        entities_raw = _call_entity_analysis(log_text, api_key)
        detected_entities = [e.get('name') for e in entities_raw]
    except Exception:
        # Fallback to keyword list if API call fails
        detected_entities = []
        api_key = _pick_key() if _GOOGLE_KEYS else ''
    return {
        'keyword_counts': counts,
        'detected_entities': detected_entities,
        'selected_google_key': api_key[:8] + '...'
    }
