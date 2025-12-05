#!/usr/bin/env python3
"""
Simple HTTP health probe designed for scheduled execution.

The script is dependency-free and can be invoked directly by cron,
Kubernetes CronJobs, or any CI scheduler. It sends a GET request to the
configured endpoint, records latency, and emits a JSON line that can be
shipped to log aggregation or monitoring tools.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


def probe(url: str, timeout: int, expected_status: int) -> dict:
    """Perform a single HTTP probe and return a structured result."""

    start = time.monotonic()
    status: int | None = None
    error: str | None = None

    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:  # nosec B310
            status = response.getcode()
    except urllib.error.URLError as exc:  # pragma: no cover - thin wrapper
        error = str(exc.reason) if hasattr(exc, "reason") else str(exc)
    except Exception as exc:  # pragma: no cover - safety net for unexpected issues
        error = str(exc)

    latency_ms = round((time.monotonic() - start) * 1000, 2)
    ok = status == expected_status and error is None

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": url,
        "expected_status": expected_status,
        "status": status,
        "latency_ms": latency_ms,
        "ok": ok,
        "error": error,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scheduled HTTP health probe")
    parser.add_argument(
        "--url",
        default=os.getenv("HEALTH_PROBE_URL", "http://localhost:8080/health"),
        help="Endpoint to probe (defaults to HEALTH_PROBE_URL env or http://localhost:8080/health)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.getenv("HEALTH_PROBE_TIMEOUT", "5")),
        help="Request timeout in seconds",
    )
    parser.add_argument(
        "--expected-status",
        type=int,
        default=int(os.getenv("HEALTH_PROBE_EXPECTED_STATUS", "200")),
        help="HTTP status code considered healthy",
    )
    parser.add_argument(
        "--logfile",
        default=os.getenv("HEALTH_PROBE_LOG", ""),
        help="Optional file path to append JSONL results",
    )
    return parser.parse_args()


def emit(result: dict, logfile: str | None) -> None:
    line = json.dumps(result, separators=(",", ":"))
    print(line)

    if logfile:
        with open(logfile, "a", encoding="utf-8") as handle:
            handle.write(f"{line}\n")


def main() -> int:
    args = parse_args()
    result = probe(args.url, args.timeout, args.expected_status)
    emit(result, args.logfile or None)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
