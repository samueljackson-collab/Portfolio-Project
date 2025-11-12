"""Simulate stream processing by aggregating sample events."""
from __future__ import annotations

import json
from collections import Counter

SAMPLE_EVENTS = [
    {"project": "mlops", "status": "success"},
    {"project": "mlops", "status": "success"},
    {"project": "chatbot", "status": "failure"},
]

if __name__ == "__main__":
    counts = Counter(event["status"] for event in SAMPLE_EVENTS)
    print(json.dumps(counts, indent=2))
