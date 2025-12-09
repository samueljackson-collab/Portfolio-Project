#!/bin/bash
###############################################################################
# Monitoring Stack Health Check Script
# Purpose: Comprehensive health validation and testing
###############################################################################
#
# Usage: ./health-check.sh [--verbose]
#
# Checks:
#   - Service container status
#   - Service health endpoints
#   - Prometheus scrape targets
#   - Prometheus TSDB status
#   - Alert rules evaluation
#   - Alertmanager configuration
#   - Grafana datasources
#   - Loki log ingestion
#   - Network connectivity
#
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verbose mode
VERBOSE=false
[ "${1:-}" = "--verbose" ] && VERBOSE=true

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

###############################################################################
# LOGGING FUNCTIONS
###############################################################################

log_check() {
    ((TOTAL_CHECKS++))
    echo -e "${BLUE}[CHECK]${NC} $*"
}

log_pass() {
    ((PASSED_CHECKS++))
    echo -e "${GREEN}  ✓${NC} $*"
}

log_fail() {
    ((FAILED_CHECKS++))
    echo -e "${RED}  ✗${NC} $*"
}

log_warn() {
    ((WARNING_CHECKS++))
    echo -e "${YELLOW}  ⚠${NC} $*"
}

log_verbose() {
    $VERBOSE && echo -e "    ${NC}$*"
}

###############################################################################
# CHECK FUNCTIONS
###############################################################################

check_container_running() {
    local container=$1
    local name=$2

    log_check "Container: $name"

    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$container")
        log_pass "Running (status: $status)"
        return 0
    else
        log_fail "Not running"
        return 1
    fi
}

check_container_health() {
    local container=$1
    local name=$2

    log_check "Health: $name"

    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")

    case "$health" in
        healthy)
            log_pass "Healthy"
            return 0
            ;;
        unhealthy)
            log_fail "Unhealthy"
            local failures=$(docker inspect --format='{{.State.Health.FailingStreak}}' "$container")
            log_verbose "Failing streak: $failures"
            return 1
            ;;
        starting)
            log_warn "Still starting"
            return 1
            ;;
        none)
            log_warn "No health check configured"
            return 0
            ;;
        *)
            log_fail "Unknown health status: $health"
            return 1
            ;;
    esac
}

check_http_endpoint() {
    local url=$1
    local name=$2
    local expected_code=${3:-200}

    log_check "HTTP Endpoint: $name"

    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$response" = "$expected_code" ]; then
        log_pass "Responding (HTTP $response)"
        return 0
    else
        log_fail "Not responding properly (HTTP $response, expected $expected_code)"
        return 1
    fi
}

check_prometheus_targets() {
    log_check "Prometheus: Scrape Targets"

    local api_url="http://localhost:9090/api/v1/targets"
    local response=$(curl -s "$api_url" 2>/dev/null || echo "{}")

    local total_targets=$(echo "$response" | jq -r '.data.activeTargets | length' 2>/dev/null || echo "0")
    local up_targets=$(echo "$response" | jq -r '.data.activeTargets | map(select(.health=="up")) | length' 2>/dev/null || echo "0")
    local down_targets=$((total_targets - up_targets))

    if [ "$total_targets" -eq 0 ]; then
        log_fail "No targets configured"
        return 1
    elif [ "$down_targets" -eq 0 ]; then
        log_pass "All $total_targets targets UP"
        return 0
    else
        log_warn "$down_targets of $total_targets targets DOWN"

        if $VERBOSE; then
            echo "$response" | jq -r '.data.activeTargets[] | select(.health!="up") | "    - \(.labels.job) (\(.lastError))"' 2>/dev/null || true
        fi
        return 1
    fi
}

check_prometheus_tsdb() {
    log_check "Prometheus: TSDB Status"

    local api_url="http://localhost:9090/api/v1/status/tsdb"
    local response=$(curl -s "$api_url" 2>/dev/null || echo "{}")

    local head_chunks=$(echo "$response" | jq -r '.data.headStats.numSeries' 2>/dev/null || echo "0")

    if [ "$head_chunks" -gt 0 ]; then
        log_pass "TSDB operational ($head_chunks series in memory)"
        log_verbose "Time series being tracked"
        return 0
    else
        log_warn "TSDB empty (no data ingested yet)"
        return 1
    fi
}

check_prometheus_rules() {
    log_check "Prometheus: Alert Rules"

    local api_url="http://localhost:9090/api/v1/rules"
    local response=$(curl -s "$api_url" 2>/dev/null || echo "{}")

    local total_rules=$(echo "$response" | jq -r '.data.groups[].rules | length' 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")

    if [ "$total_rules" -gt 0 ]; then
        log_pass "$total_rules alert rules loaded"

        if $VERBOSE; then
            local firing=$(echo "$response" | jq -r '.data.groups[].rules[] | select(.state=="firing") | .name' 2>/dev/null | wc -l)
            [ "$firing" -gt 0 ] && log_verbose "$firing alerts currently firing"
        fi
        return 0
    else
        log_warn "No alert rules loaded"
        return 1
    fi
}

check_alertmanager_status() {
    log_check "Alertmanager: Status"

    local api_url="http://localhost:9093/api/v2/status"
    local response=$(curl -s "$api_url" 2>/dev/null || echo "{}")

    local version=$(echo "$response" | jq -r '.versionInfo.version' 2>/dev/null || echo "unknown")

    if [ "$version" != "unknown" ] && [ "$version" != "null" ]; then
        log_pass "Operational (version: $version)"
        return 0
    else
        log_fail "Not responding properly"
        return 1
    fi
}

check_alertmanager_receivers() {
    log_check "Alertmanager: Receivers"

    local config_url="http://localhost:9093/api/v2/status"
    local response=$(curl -s "$config_url" 2>/dev/null || echo "{}")

    # Note: Alertmanager API doesn't expose receiver count directly
    # This is a basic connectivity check
    if echo "$response" | jq -e '.uptime' &>/dev/null; then
        log_pass "Configuration loaded"
        return 0
    else
        log_warn "Cannot verify receiver configuration"
        return 1
    fi
}

check_grafana_health() {
    log_check "Grafana: Health"

    local api_url="http://localhost:3000/api/health"
    local response=$(curl -s "$api_url" 2>/dev/null || echo "{}")

    local database=$(echo "$response" | jq -r '.database' 2>/dev/null || echo "unknown")

    if [ "$database" = "ok" ]; then
        log_pass "Healthy (database: ok)"
        return 0
    else
        log_fail "Database connection issue"
        return 1
    fi
}

check_grafana_datasources() {
    log_check "Grafana: Datasources"

    # Use anonymous access or would need credentials
    local api_url="http://localhost:3000/api/datasources"

    # This requires authentication, so we check if provisioning worked
    # by checking if Grafana is responding to datasources endpoint
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$api_url" 2>/dev/null || echo "000")

    if [ "$response" = "401" ] || [ "$response" = "200" ]; then
        log_pass "Provisioning active (needs auth to verify)"
        log_verbose "Login to Grafana to verify: http://localhost:3000"
        return 0
    else
        log_fail "Datasources endpoint not responding (HTTP $response)"
        return 1
    fi
}

check_loki_ready() {
    log_check "Loki: Ready Status"

    local ready_url="http://localhost:3100/ready"
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$ready_url" 2>/dev/null || echo "000")

    if [ "$response" = "200" ]; then
        log_pass "Ready for queries"
        return 0
    else
        log_fail "Not ready (HTTP $response)"
        return 1
    fi
}

check_loki_ingestion() {
    log_check "Loki: Log Ingestion"

    # Query Loki for recent logs
    local query_url="http://localhost:3100/loki/api/v1/query_range"
    local query='{job=~".+"}'
    local response=$(curl -s -G "$query_url" --data-urlencode "query=$query" --data-urlencode "limit=1" 2>/dev/null || echo "{}")

    local result_count=$(echo "$response" | jq -r '.data.result | length' 2>/dev/null || echo "0")

    if [ "$result_count" -gt 0 ]; then
        log_pass "Receiving logs ($result_count streams found)"
        return 0
    else
        log_warn "No logs ingested yet (may take a few minutes)"
        return 1
    fi
}

check_promtail_targets() {
    log_check "Promtail: Scrape Targets"

    local targets_url="http://localhost:9080/targets"
    local response=$(curl -s "$targets_url" 2>/dev/null || echo "{}")

    # Check if we got a valid response
    if echo "$response" | jq -e '.activeTargets' &>/dev/null; then
        local target_count=$(echo "$response" | jq -r '.activeTargets | length' 2>/dev/null || echo "0")
        log_pass "Monitoring $target_count log sources"
        return 0
    else
        log_warn "Cannot fetch target status"
        return 1
    fi
}

check_node_exporter_metrics() {
    log_check "Node Exporter: Metrics"

    local metrics_url="http://localhost:9100/metrics"

    # Just check if metrics endpoint responds
    if curl -s "$metrics_url" | head -n 1 | grep -q "^# HELP"; then
        log_pass "Exporting system metrics"
        return 0
    else
        log_fail "Metrics endpoint not responding"
        return 1
    fi
}

check_cadvisor_metrics() {
    log_check "cAdvisor: Container Metrics"

    local metrics_url="http://localhost:8080/metrics"

    # Check if cAdvisor metrics are available
    if curl -s "$metrics_url" | head -n 1 | grep -q "^# HELP"; then
        log_pass "Exporting container metrics"
        return 0
    else
        log_fail "Metrics endpoint not responding"
        return 1
    fi
}

check_disk_space() {
    log_check "System: Disk Space"

    local disk_usage=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')

    if [ "$disk_usage" -lt 80 ]; then
        log_pass "Sufficient space (${disk_usage}% used)"
        return 0
    elif [ "$disk_usage" -lt 90 ]; then
        log_warn "Disk usage high (${disk_usage}% used)"
        return 1
    else
        log_fail "Disk space critical (${disk_usage}% used)"
        return 1
    fi
}

###############################################################################
# SUMMARY FUNCTIONS
###############################################################################

print_summary() {
    echo
    echo "═══════════════════════════════════════════════════════════"
    echo "Health Check Summary"
    echo "═══════════════════════════════════════════════════════════"
    echo

    local pass_pct=0
    [ $TOTAL_CHECKS -gt 0 ] && pass_pct=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

    echo -e "  Total Checks:   $TOTAL_CHECKS"
    echo -e "  ${GREEN}Passed:${NC}         $PASSED_CHECKS"
    echo -e "  ${RED}Failed:${NC}         $FAILED_CHECKS"
    echo -e "  ${YELLOW}Warnings:${NC}       $WARNING_CHECKS"
    echo
    echo -e "  Success Rate:   ${pass_pct}%"
    echo

    if [ $FAILED_CHECKS -eq 0 ] && [ $WARNING_CHECKS -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed - Monitoring stack is healthy!${NC}"
        return 0
    elif [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${YELLOW}⚠ Some warnings detected - Review output above${NC}"
        return 0
    else
        echo -e "${RED}✗ Some checks failed - Please investigate${NC}"
        return 1
    fi
}

###############################################################################
# MAIN EXECUTION
###############################################################################

main() {
    echo "═══════════════════════════════════════════════════════════"
    echo "Monitoring Stack - Health Check"
    echo "═══════════════════════════════════════════════════════════"
    echo
    echo "Starting comprehensive health validation..."
    echo
    $VERBOSE && echo "Verbose mode: ON"
    echo

    # Container checks
    check_container_running "monitoring-prometheus" "Prometheus"
    check_container_running "monitoring-grafana" "Grafana"
    check_container_running "monitoring-loki" "Loki"
    check_container_running "monitoring-promtail" "Promtail"
    check_container_running "monitoring-alertmanager" "Alertmanager"
    check_container_running "monitoring-node-exporter" "Node Exporter"
    check_container_running "monitoring-cadvisor" "cAdvisor"
    echo

    # Health checks
    check_container_health "monitoring-prometheus" "Prometheus"
    check_container_health "monitoring-grafana" "Grafana"
    check_container_health "monitoring-loki" "Loki"
    check_container_health "monitoring-promtail" "Promtail"
    check_container_health "monitoring-alertmanager" "Alertmanager"
    echo

    # Endpoint checks
    check_http_endpoint "http://localhost:9090/-/healthy" "Prometheus API"
    check_http_endpoint "http://localhost:3000/api/health" "Grafana API"
    check_http_endpoint "http://localhost:3100/ready" "Loki API"
    check_http_endpoint "http://localhost:9093/-/healthy" "Alertmanager API"
    echo

    # Functional checks
    check_prometheus_targets
    check_prometheus_tsdb
    check_prometheus_rules
    echo

    check_alertmanager_status
    check_alertmanager_receivers
    echo

    check_grafana_health
    check_grafana_datasources
    echo

    check_loki_ready
    check_loki_ingestion
    echo

    check_promtail_targets
    echo

    check_node_exporter_metrics
    check_cadvisor_metrics
    echo

    # System checks
    check_disk_space
    echo

    # Print summary
    print_summary
}

# Run main
main
exit_code=$?

echo
echo "═══════════════════════════════════════════════════════════"
echo "Access Points:"
echo "  Grafana:      http://localhost:3000"
echo "  Prometheus:   http://localhost:9090"
echo "  Alertmanager: http://localhost:9093"
echo "═══════════════════════════════════════════════════════════"

exit $exit_code
