#!/usr/bin/env bash
set -euo pipefail

# Smoke Test Script - Enterprise Portfolio Demo Stack
# Tests all services in the Docker Compose demo environment

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Helper functions
log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test service health
test_service() {
    local service=$1
    local url=$2
    local expected_code=${3:-200}

    log_test "Testing $service at $url"

    if curl -sf -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_code"; then
        log_pass "$service is healthy (HTTP $expected_code)"
        return 0
    else
        log_fail "$service is not responding correctly"
        return 1
    fi
}

# Test container status
test_container() {
    local container=$1

    log_test "Checking container: $container"

    if docker compose -f compose.demo.yml ps "$container" | grep -q "Up"; then
        log_pass "Container $container is running"
        return 0
    else
        log_fail "Container $container is not running"
        return 1
    fi
}

# Main test suite
main() {
    echo ""
    echo "============================================"
    echo "  Enterprise Portfolio - Smoke Tests"
    echo "============================================"
    echo ""

    # Check if Docker Compose stack is running
    log_test "Checking if Docker Compose stack is running..."
    if ! docker compose -f compose.demo.yml ps > /dev/null 2>&1; then
        log_fail "Docker Compose stack is not running"
        log_warn "Run: docker compose -f compose.demo.yml up -d"
        exit 1
    fi

    # Wait for services to be ready
    log_test "Waiting for services to initialize..."
    sleep 5

    echo ""
    echo "--- Container Health Checks ---"
    echo ""

    # Test all containers
    test_container "portfolio-prometheus" || true
    test_container "portfolio-grafana" || true
    test_container "portfolio-loki" || true
    test_container "portfolio-node-exporter" || true
    test_container "portfolio-cadvisor" || true
    test_container "portfolio-alertmanager" || true

    echo ""
    echo "--- HTTP Health Checks ---"
    echo ""

    # Test service endpoints
    test_service "Prometheus" "http://localhost:9090/-/healthy" || true
    test_service "Prometheus Targets" "http://localhost:9090/api/v1/targets" || true
    test_service "Grafana" "http://localhost:3001/api/health" || true
    test_service "Loki" "http://localhost:3100/ready" || true
    test_service "Node Exporter" "http://localhost:9100/metrics" || true
    test_service "cAdvisor" "http://localhost:8080/healthz" || true
    test_service "Alertmanager" "http://localhost:9093/-/healthy" || true

    echo ""
    echo "--- Prometheus Scrape Targets ---"
    echo ""

    log_test "Checking Prometheus scrape targets..."
    TARGETS=$(curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets | length')
    if [ "$TARGETS" -gt 0 ]; then
        log_pass "Prometheus is scraping $TARGETS targets"
    else
        log_fail "Prometheus has no active targets"
    fi

    echo ""
    echo "--- Grafana Datasources ---"
    echo ""

    log_test "Checking Grafana datasources..."
    DATASOURCES=$(curl -s -u admin:admin http://localhost:3001/api/datasources | jq '. | length')
    if [ "$DATASOURCES" -gt 0 ]; then
        log_pass "Grafana has $DATASOURCES datasource(s) configured"
    else
        log_fail "Grafana has no datasources configured"
    fi

    echo ""
    echo "--- Metrics Verification ---"
    echo ""

    log_test "Querying sample metrics from Prometheus..."
    UP_METRICS=$(curl -s "http://localhost:9090/api/v1/query?query=up" | jq -r '.data.result | length')
    if [ "$UP_METRICS" -gt 0 ]; then
        log_pass "Prometheus has $UP_METRICS 'up' metrics"
    else
        log_fail "Prometheus has no metrics"
    fi

    echo ""
    echo "============================================"
    echo "  Test Summary"
    echo "============================================"
    echo ""
    echo -e "Passed: ${GREEN}$PASSED${NC}"
    echo -e "Failed: ${RED}$FAILED${NC}"
    echo ""

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        echo ""
        echo "Services are accessible at:"
        echo "  - Prometheus:   http://localhost:9090"
        echo "  - Grafana:      http://localhost:3001 (admin/admin)"
        echo "  - Alertmanager: http://localhost:9093"
        echo "  - cAdvisor:     http://localhost:8080"
        echo ""
        exit 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check container logs: docker compose -f compose.demo.yml logs [service]"
        echo "  2. Restart services: docker compose -f compose.demo.yml restart"
        echo "  3. Check Docker resources: docker stats"
        echo ""
        exit 1
    fi
}

# Run tests
main "$@"
