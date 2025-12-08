#!/usr/bin/env python3
"""
Scheduled health probe for the cloud-native PoC service.

Runs a GET request against the configured health endpoint and exits non-zero
if the response is not HTTP 200 or latency exceeds the SLA threshold.
"""
from __future__ import annotations
import os
import sys
import time
import urllib.request

DEFAULT_URL = os.getenv("PROBE_URL", "http://localhost:8080/healthz")
MAX_LATENCY_MS = int(os.getenv("MAX_LATENCY_MS", "500"))
TIMEOUT = int(os.getenv("PROBE_TIMEOUT", "5"))

def probe(url: str) -> None:
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
            status = response.getcode()
            latency_ms = (time.perf_counter() - start) * 1000
            if status != 200:
                raise RuntimeError(f"Health check failed with status {status}")
            if latency_ms > MAX_LATENCY_MS:
                raise RuntimeError(
                    f"Health check latency {latency_ms:.2f}ms exceeded threshold {MAX_LATENCY_MS}ms"
                )
            print(f"health_probe OK: status={status}, latency_ms={latency_ms:.2f}")
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"health_probe failed for {url}: {exc}") from exc

def main() -> int:
    try:
        probe(DEFAULT_URL)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(exc, file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
