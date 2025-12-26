#!/usr/bin/env python3
"""
Lightweight health probe for the Cloud-Native POC API.

This script is designed to be run on a schedule (cron, systemd timer, or Kubernetes CronJob)
to validate that the application remains healthy over time. It exits non-zero if any endpoint
fails or if latency exceeds a configured threshold, making it suitable for uptime dashboards
or alerting hooks.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class ProbeResult:
    endpoint: str
    status: int | None
    latency_ms: float
    ok: bool
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "status": self.status,
            "latency_ms": round(self.latency_ms, 2),
            "ok": self.ok,
            "error": self.error,
        }


def probe_endpoint(url: str, timeout: float) -> ProbeResult:
    """Call a URL and return a ProbeResult with status and latency."""
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    start = time.monotonic()

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            latency_ms = (time.monotonic() - start) * 1000
            return ProbeResult(endpoint=url, status=response.status, latency_ms=latency_ms, ok=200 <= response.status < 300)
    except urllib.error.HTTPError as exc:  # Server returned a non-2xx response
        latency_ms = (time.monotonic() - start) * 1000
        return ProbeResult(endpoint=url, status=exc.code, latency_ms=latency_ms, ok=False, error=str(exc))
    except urllib.error.URLError as exc:  # Network error
        latency_ms = (time.monotonic() - start) * 1000
        return ProbeResult(endpoint=url, status=None, latency_ms=latency_ms, ok=False, error=str(exc.reason))


def run_probes(base_url: str, endpoints: Iterable[str], timeout: float, max_latency_ms: float) -> List[ProbeResult]:
    results: List[ProbeResult] = []
    for endpoint in endpoints:
        full_url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        result = probe_endpoint(full_url, timeout=timeout)
        # Mark as failed if above latency budget even when status is 2xx
        if result.ok and result.latency_ms > max_latency_ms:
            results.append(ProbeResult(endpoint=result.endpoint, status=result.status, latency_ms=result.latency_ms, ok=False, error=f"Exceeded latency budget ({max_latency_ms} ms)"))
        else:
            results.append(result)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scheduled health probe for the Cloud-Native POC API")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--endpoints", default="/health,/ready", help="Comma-separated list of endpoints to probe")
    parser.add_argument("--timeout", type=float, default=3.0, help="HTTP timeout per request in seconds (default: 3.0)")
    parser.add_argument("--max-latency-ms", type=float, default=800.0, help="Maximum acceptable latency per endpoint (default: 800ms)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON (for logging systems)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    endpoints = [ep.strip() for ep in args.endpoints.split(",") if ep.strip()]

    results = run_probes(base_url=args.base_url, endpoints=endpoints, timeout=args.timeout, max_latency_ms=args.max_latency_ms)
    failures = [result for result in results if not result.ok]

    if args.json:
        payload = {
            "base_url": args.base_url,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "results": [result.to_dict() for result in results],
            "healthy": not failures,
        }
        print(json.dumps(payload, separators=(",", ":")))
    else:
        for result in results:
            status_text = result.status if result.status is not None else "N/A"
            latency = round(result.latency_ms, 2)
            marker = "✅" if result.ok else "❌"
            error_msg = f" error={result.error}" if result.error else ""
            print(f"{marker} {result.endpoint} status={status_text} latency_ms={latency}{error_msg}")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
