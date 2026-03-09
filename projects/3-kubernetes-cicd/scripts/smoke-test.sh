#!/bin/bash
#
# Smoke Test Script for K8s CI/CD Demo Application
#
# This script performs basic health and functionality checks after deployment.
# It's designed to be run as part of the CI/CD pipeline or manually.
#
# Usage:
#   ./smoke-test.sh [BASE_URL]
#
# Example:
#   ./smoke-test.sh https://k8s-demo.example.com
#   ./smoke-test.sh http://localhost:8080

set -e

# Configuration
BASE_URL="${1:-http://localhost:8080}"
MAX_RETRIES=5
RETRY_DELAY=5
TIMEOUT=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

echo "=============================================="
echo "  K8s CI/CD Demo - Smoke Tests"
echo "=============================================="
echo "Target: ${BASE_URL}"
echo "Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# Function to make HTTP request with retries
http_request() {
    local url="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    local expected_status="${4:-200}"
    local retry=0

    while [ $retry -lt $MAX_RETRIES ]; do
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                -H "Content-Type: application/json" \
                -d "$data" \
                --max-time "$TIMEOUT" \
                "$url" 2>/dev/null || echo "000")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                --max-time "$TIMEOUT" \
                "$url" 2>/dev/null || echo "000")
        fi

        status_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')

        if [ "$status_code" = "$expected_status" ]; then
            echo "$body"
            return 0
        fi

        retry=$((retry + 1))
        if [ $retry -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}Retry $retry/$MAX_RETRIES in ${RETRY_DELAY}s...${NC}" >&2
            sleep $RETRY_DELAY
        fi
    done

    echo "HTTP $status_code" >&2
    return 1
}

# Function to run a test
run_test() {
    local test_name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="${4:-}"
    local expected_status="${5:-200}"
    local expected_content="${6:-}"

    echo -n "Testing: ${test_name}... "

    result=$(http_request "$url" "$method" "$data" "$expected_status" 2>&1)
    status=$?

    if [ $status -eq 0 ]; then
        if [ -n "$expected_content" ]; then
            if echo "$result" | grep -q "$expected_content"; then
                echo -e "${GREEN}PASSED${NC}"
                TESTS_PASSED=$((TESTS_PASSED + 1))
                return 0
            else
                echo -e "${RED}FAILED${NC} (content mismatch)"
                echo "  Expected: $expected_content"
                echo "  Got: $result"
                TESTS_FAILED=$((TESTS_FAILED + 1))
                return 1
            fi
        else
            echo -e "${GREEN}PASSED${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            return 0
        fi
    else
        echo -e "${RED}FAILED${NC} ($result)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================
# Health Check Tests
# ============================================
echo ""
echo "--- Health Checks ---"

run_test "Health endpoint" \
    "${BASE_URL}/health" \
    "GET" "" "200" "healthy"

run_test "Readiness endpoint" \
    "${BASE_URL}/ready" \
    "GET" "" "200" "ready"

# ============================================
# API v1 Status Tests
# ============================================
echo ""
echo "--- API v1 Status ---"

run_test "Status endpoint" \
    "${BASE_URL}/api/v1/status" \
    "GET" "" "200" "operational"

run_test "Config endpoint" \
    "${BASE_URL}/api/v1/config" \
    "GET" "" "200" "config"

# ============================================
# Basic API Tests
# ============================================
echo ""
echo "--- Basic API ---"

run_test "Home endpoint" \
    "${BASE_URL}/" \
    "GET" "" "200" "Hello"

run_test "Info endpoint" \
    "${BASE_URL}/api/info" \
    "GET" "" "200" "version"

run_test "Echo endpoint" \
    "${BASE_URL}/api/echo" \
    "POST" '{"test": "data"}' "200" "received"

# ============================================
# Metrics Tests
# ============================================
echo ""
echo "--- Metrics ---"

run_test "Prometheus metrics" \
    "${BASE_URL}/metrics" \
    "GET" "" "200" "app_uptime_seconds"

# ============================================
# Error Handling Tests
# ============================================
echo ""
echo "--- Error Handling ---"

run_test "404 handling" \
    "${BASE_URL}/nonexistent" \
    "GET" "" "404" "Not Found"

# ============================================
# Summary
# ============================================
echo ""
echo "=============================================="
echo "  Test Summary"
echo "=============================================="
echo -e "Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Failed: ${RED}${TESTS_FAILED}${NC}"
echo "Total:  $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}SMOKE TESTS FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}ALL SMOKE TESTS PASSED${NC}"
    exit 0
fi
