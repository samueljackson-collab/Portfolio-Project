#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="${1:-10.0.1.10}"
PING_COUNT="${PING_COUNT:-10}"
MTU_SIZE="${MTU_SIZE:-1400}"

echo "===================================="
echo "Hybrid Network Connectivity Test"
echo "===================================="
echo "Remote host: $REMOTE_HOST"
echo "Ping count: $PING_COUNT"
echo "MTU size: $MTU_SIZE"
echo

# Test 1: ICMP reachability
echo "[Test 1] ICMP Ping Test"
if ping -c "$PING_COUNT" "$REMOTE_HOST" > /dev/null 2>&1; then
    echo "✓ Host reachable via ICMP"
    avg_latency=$(ping -c "$PING_COUNT" "$REMOTE_HOST" | tail -1 | awk -F '/' '{print $5}')
    echo "  Average latency: ${avg_latency} ms"
else
    echo "✗ Host unreachable"
    exit 1
fi

echo

# Test 2: MTU Path Discovery
echo "[Test 2] MTU Path Discovery"
if ping -M do -s "$MTU_SIZE" -c 3 "$REMOTE_HOST" > /dev/null 2>&1; then
    echo "✓ MTU $MTU_SIZE supported (no fragmentation)"
else
    echo "⚠ MTU $MTU_SIZE may cause fragmentation"
fi

echo

# Test 3: TCP connectivity (SSH port)
echo "[Test 3] TCP Connectivity (port 22)"
if timeout 5 bash -c "cat < /dev/null > /dev/tcp/$REMOTE_HOST/22" 2>/dev/null; then
    echo "✓ TCP port 22 reachable"
else
    echo "⚠ TCP port 22 unreachable (may be firewalled)"
fi

echo

echo "===================================="
echo "Connectivity Test Complete"
echo "===================================="
