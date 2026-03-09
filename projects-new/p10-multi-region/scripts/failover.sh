#!/bin/bash
# Multi-Region Failover Script
# Simulates and validates failover between primary and secondary regions

set -euo pipefail

# Configuration
PRIMARY_REGION="${PRIMARY_REGION:-us-east-1}"
SECONDARY_REGION="${SECONDARY_REGION:-us-west-2}"
HOSTED_ZONE_ID="${HOSTED_ZONE_ID:-Z1234567890ABC}"
RECORD_NAME="${RECORD_NAME:-app.example.com}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_health() {
    local region=$1
    local health_check_id=$2

    log_info "Checking health for $region..."

    status=$(aws route53 get-health-check-status \
        --health-check-id "$health_check_id" \
        --query 'HealthCheckObservations[0].StatusReport.Status' \
        --output text)

    echo "$status"
}

get_current_primary() {
    log_info "Getting current primary endpoint..."

    current=$(aws route53 list-resource-record-sets \
        --hosted-zone-id "$HOSTED_ZONE_ID" \
        --query "ResourceRecordSets[?Name=='${RECORD_NAME}.'].SetIdentifier" \
        --output text | grep -i primary || echo "")

    if [ -z "$current" ]; then
        log_error "Could not determine current primary"
        exit 1
    fi

    echo "$current"
}

simulate_primary_failure() {
    log_warn "Simulating primary region failure..."
    log_warn "This will disable the primary health check!"

    read -p "Are you sure you want to continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^yes$ ]]; then
        log_info "Aborted."
        exit 0
    fi

    # Get primary health check ID
    health_check_id=$(aws route53 list-health-checks \
        --query "HealthChecks[?HealthCheckConfig.FullyQualifiedDomainName=='primary-alb-${PRIMARY_REGION}.elb.amazonaws.com'].Id" \
        --output text)

    if [ -z "$health_check_id" ]; then
        log_error "Could not find primary health check"
        exit 1
    fi

    # Disable primary health check
    aws route53 update-health-check \
        --health-check-id "$health_check_id" \
        --disabled \
        > /dev/null

    log_info "Primary health check disabled: $health_check_id"
    log_info "Waiting for DNS failover (this may take up to 60 seconds)..."

    sleep 60

    log_info "Failover initiated successfully"
}

verify_failover() {
    log_info "Verifying failover to secondary region..."

    # Test DNS resolution
    resolved_ip=$(dig +short "$RECORD_NAME" | head -1)

    if [ -z "$resolved_ip" ]; then
        log_error "DNS resolution failed"
        exit 1
    fi

    log_info "DNS resolves to: $resolved_ip"

    # Test HTTP endpoint
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "https://${RECORD_NAME}/health" || echo "000")

    if [ "$http_code" == "200" ]; then
        log_info "✅ Failover successful! Secondary region is serving traffic."
        log_info "HTTP Status: $http_code"
    else
        log_error "❌ Failover failed! HTTP Status: $http_code"
        exit 1
    fi
}

restore_primary() {
    log_info "Restoring primary region..."

    # Get primary health check ID
    health_check_id=$(aws route53 list-health-checks \
        --query "HealthChecks[?HealthCheckConfig.FullyQualifiedDomainName=='primary-alb-${PRIMARY_REGION}.elb.amazonaws.com'].Id" \
        --output text)

    # Re-enable primary health check
    aws route53 update-health-check \
        --health-check-id "$health_check_id" \
        --no-disabled \
        > /dev/null

    log_info "Primary health check re-enabled: $health_check_id"
    log_info "Waiting for traffic to return to primary (up to 60 seconds)..."

    sleep 60

    log_info "Primary region restored"
}

monitor_replication() {
    log_info "Monitoring cross-region replication..."

    primary_bucket=$(aws s3api list-buckets \
        --query "Buckets[?contains(Name, 'primary')].Name" \
        --output text)

    secondary_bucket=$(aws s3api list-buckets \
        --query "Buckets[?contains(Name, 'secondary')].Name" \
        --output text)

    primary_count=$(aws s3 ls "s3://${primary_bucket}" --recursive --region "$PRIMARY_REGION" | wc -l)
    secondary_count=$(aws s3 ls "s3://${secondary_bucket}" --recursive --region "$SECONDARY_REGION" | wc -l)

    log_info "Primary bucket objects: $primary_count"
    log_info "Secondary bucket objects: $secondary_count"

    if [ "$primary_count" -eq "$secondary_count" ]; then
        log_info "✅ Replication is in sync"
    else
        log_warn "⚠️  Replication lag detected"
    fi
}

# Main menu
case "${1:-help}" in
    check)
        get_current_primary
        ;;
    simulate)
        simulate_primary_failure
        verify_failover
        ;;
    restore)
        restore_primary
        ;;
    monitor)
        monitor_replication
        ;;
    full-drill)
        log_info "Starting full DR drill..."
        get_current_primary
        simulate_primary_failure
        verify_failover
        monitor_replication
        log_info "DR drill completed. Remember to restore primary when ready."
        ;;
    *)
        echo "Usage: $0 {check|simulate|restore|monitor|full-drill}"
        echo ""
        echo "Commands:"
        echo "  check       - Check current primary region"
        echo "  simulate    - Simulate primary failure and trigger failover"
        echo "  restore     - Restore primary region"
        echo "  monitor     - Monitor cross-region replication status"
        echo "  full-drill  - Execute full DR drill (simulate + verify + monitor)"
        exit 1
        ;;
esac
