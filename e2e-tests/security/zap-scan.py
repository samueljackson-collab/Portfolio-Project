#!/usr/bin/env python3
"""Automate OWASP ZAP baseline scan."""
from __future__ import annotations

import argparse
import time

from zapv2 import ZAPv2

parser = argparse.ArgumentParser()
parser.add_argument("--target", default="http://localhost:8000")
parser.add_argument("--apikey", default="changeme")
args = parser.parse_args()

zap = ZAPv2(apikey=args.apikey)
print("Spidering target...")
zap.urlopen(args.target)
zap.spider.scan(args.target)
while int(zap.spider.status()) < 100:
    time.sleep(1)

print("Running active scan...")
zap.ascan.scan(args.target)
while int(zap.ascan.status()) < 100:
    time.sleep(1)

alerts = zap.core.alerts(baseurl=args.target)
print(f"Scan complete with {len(alerts)} alerts")
