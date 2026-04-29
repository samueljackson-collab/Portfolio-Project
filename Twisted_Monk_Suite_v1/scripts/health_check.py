#!/usr/bin/env python3
"""Simple script to check API health."""

import os
import sys
from typing import Tuple

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def check_health() -> Tuple[bool, str]:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        return True, f"Healthy: redis={data.get('redis')} shopify={data.get('shopify')}"
    except Exception as exc:  # noqa: BLE001
        return False, f"Health check failed: {exc}"


def main() -> None:
    success, message = check_health()
    print(message)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
