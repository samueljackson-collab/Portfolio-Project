#!/bin/bash
# Service Health Check Script
set -euo pipefail

SERVICES=(
    "192.168.40.35:53:Pi-hole DNS"
    "192.168.40.25:443:FreeIPA"
    "192.168.40.40:443:Nginx"
    "192.168.40.30:514:Syslog"
)

for svc in "${SERVICES[@]}"; do
    IFS=':' read -r ip port name <<< "$svc"
    if timeout 2 bash -c "echo > /dev/tcp/$ip/$port" 2>/dev/null; then
        echo "✓ $name ($ip:$port) - OK"
    else
        echo "✗ $name ($ip:$port) - FAILED"
    fi
done
