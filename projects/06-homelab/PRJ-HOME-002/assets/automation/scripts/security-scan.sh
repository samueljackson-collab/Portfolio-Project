#!/bin/bash
# Security Vulnerability Scanner
set -euo pipefail

echo "Running security scans..."
for host in 192.168.40.{10..12} 192.168.40.{25,30,35,40}; do
    echo "Scanning $host..."
    nmap -sV --script vuln $host -oN /tmp/scan-$host.txt
done
echo "Security scans complete. Results in /tmp/"
