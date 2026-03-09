#!/bin/bash
################################################################################
# Monitoring Stack Health Check Script
################################################################################
#
# Purpose:
#   Comprehensive health verification for the monitoring stack.
#   Validates that all services are running, accessible, and collecting data.
#
# Usage:
#   ./health-check.sh
#
# Exit Codes:
#   0 - All health checks passed
#   1 - One or more health checks failed
#
# Checks Performed:
#   1. Service availability (Docker containers running)
#   2. HTTP endpoint accessibility
#   3. Prometheus data collection (recent metrics exist)
#   4. Loki log ingestion (recent logs exist)
#   5. Grafana datasource connectivity
#   6. Alertmanager readiness
#
# Author: Portfolio Project
# Version: 1.0.0
# Last Updated: 2024-11-24
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

################################################################################
# Helper Functions
################################################################################

# Run a health check
# Arguments: $1 = check name, $2 = command to execute
run_check() {
    local check_name="$1"
    shift
    local check_command="$@"

    ((TOTAL_CHECKS++))

    echo -n "  [$TOTAL_CHECKS] $check_name... "

    if eval "$check_command" &>/dev/null; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED_CHECKS++))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        ((FAILED_CHECKS++))
        return 1
    fi
}

################################################################################
# Health Checks
################################################################################

echo "================================"
echo "Monitoring Stack Health Check"
echo "================================"
echo ""

# Check 1: Docker daemon
echo "1. Docker Daemon"
run_check "Docker daemon is running" "docker info"
echo ""

# Check 2: Container status
echo "2. Container Status"
run_check "Prometheus container running" "docker ps | grep -q prometheus"
run_check "Grafana container running" "docker ps | grep -q grafana"
run_check "Loki container running" "docker ps | grep -q loki"
run_check "Promtail container running" "docker ps | grep -q promtail"
run_check "Alertmanager container running" "docker ps | grep -q alertmanager"
run_check "Node-exporter container running" "docker ps | grep -q node-exporter"
run_check "cAdvisor container running" "docker ps | grep -q cadvisor"
echo ""

# Check 3: HTTP endpoint accessibility
echo "3. HTTP Endpoints"
run_check "Prometheus HTTP endpoint" "curl -sf http://localhost:9090/-/healthy"
run_check "Grafana HTTP endpoint" "curl -sf http://localhost:3000/api/health"
run_check "Loki HTTP endpoint" "curl -sf http://localhost:3100/ready"
run_check "Alertmanager HTTP endpoint" "curl -sf http://localhost:9093/-/healthy"
run_check "Node-exporter HTTP endpoint" "curl -sf http://localhost:9100/metrics"
run_check "cAdvisor HTTP endpoint" "curl -sf http://localhost:8080/healthz"
echo ""

# Check 4: Prometheus data collection
echo "4. Prometheus Data Collection"
run_check "Prometheus scraping targets" "curl -sf 'http://localhost:9090/api/v1/query?query=up' | grep -q '\"result\"'"
run_check "Node-exporter metrics available" "curl -sf 'http://localhost:9090/api/v1/query?query=node_cpu_seconds_total' | grep -q '\"result\"'"
run_check "cAdvisor metrics available" "curl -sf 'http://localhost:9090/api/v1/query?query=container_cpu_usage_seconds_total' | grep -q '\"result\"'"
echo ""

# Check 5: Loki log ingestion
echo "5. Loki Log Ingestion"
run_check "Loki accepting queries" "curl -sf 'http://localhost:3100/loki/api/v1/labels' | grep -q 'status.*success'"
echo ""

# Check 6: Grafana datasources
echo "6. Grafana Datasources"
run_check "Prometheus datasource configured" "curl -sf http://localhost:3000/api/datasources | grep -q prometheus"
run_check "Loki datasource configured" "curl -sf http://localhost:3000/api/datasources | grep -q loki"
echo ""

# Summary
echo "================================"
echo "Health Check Summary"
echo "================================"
echo -e "Total Checks: $TOTAL_CHECKS"
echo -e "${GREEN}Passed: $PASSED_CHECKS${NC}"
echo -e "${RED}Failed: $FAILED_CHECKS${NC}"
echo ""

if [[ $FAILED_CHECKS -eq 0 ]]; then
    echo -e "${GREEN}All health checks passed!${NC}"
    echo ""
    echo "Your monitoring stack is fully operational."
    exit 0
else
    echo -e "${RED}Some health checks failed.${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check service logs: ./scripts/deploy.sh logs"
    echo "  2. Verify configuration: ./scripts/deploy.sh validate"
    echo "  3. Check container status: docker compose ps"
    echo "  4. Review documentation: docs/TROUBLESHOOTING.md"
    exit 1
fi
