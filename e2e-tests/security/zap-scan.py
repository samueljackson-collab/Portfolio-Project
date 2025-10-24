#!/usr/bin/env python3
"""Automate an OWASP ZAP scan against the portfolio backend."""

from __future__ import annotations

import argparse
import time

from owasp_zap_v2 import ZAPv2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Base URL of the target application")
    parser.add_argument("--apikey", default="", help="Optional ZAP API key")
    args = parser.parse_args()

    zap = ZAPv2(apikey=args.apikey)
    print(f"Spidering {args.target}")
    scan_id = zap.spider.scan(args.target)
    while int(zap.spider.status(scan_id)) < 100:
        time.sleep(1)
    print("Spider completed")

    print("Starting active scan")
    ascan_id = zap.ascan.scan(args.target)
    while int(zap.ascan.status(ascan_id)) < 100:
        time.sleep(5)
    print("Active scan completed")

    alerts = zap.core.alerts(baseurl=args.target)
    print(f"Found {len(alerts)} alerts")
    for alert in alerts:
        print(f"- {alert['alert']} ({alert['risk']}) -> {alert['url']}")


if __name__ == "__main__":
    main()
