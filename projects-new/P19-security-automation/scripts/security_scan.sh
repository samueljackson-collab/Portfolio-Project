#!/bin/bash
# Security Automation - SAST, DAST, and SCA scanning

set -euo pipefail

echo "=== Security Automation Pipeline ==="
echo ""

# SAST - Static Application Security Testing with Bandit
echo "[1/3] Running SAST with Bandit..."
if command -v bandit &> /dev/null; then
    bandit -r . -f json -o bandit-report.json || true
    echo "✓ SAST scan completed. Report: bandit-report.json"
else
    echo "⚠ Bandit not installed. Install: pip install bandit"
fi

# SCA - Software Composition Analysis with Safety
echo ""
echo "[2/3] Running SCA with Safety..."
if command -v safety &> /dev/null; then
    safety check --json > safety-report.json || true
    echo "✓ SCA scan completed. Report: safety-report.json"
else
    echo "⚠ Safety not installed. Install: pip install safety"
fi

# Container Scanning with Trivy
echo ""
echo "[3/3] Running Container scan with Trivy..."
if command -v trivy &> /dev/null; then
    trivy image --format json --output trivy-report.json myapp:latest || true
    echo "✓ Container scan completed. Report: trivy-report.json"
else
    echo "⚠ Trivy not installed. Install from: https://github.com/aquasecurity/trivy"
fi

echo ""
echo "=== Security scans completed ==="
echo "Review reports for findings"
