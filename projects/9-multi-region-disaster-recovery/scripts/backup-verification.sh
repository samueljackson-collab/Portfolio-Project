#!/bin/bash
# Automated Backup Verification Script for Multi-Region DR

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PRIMARY_REGION="${PRIMARY_REGION:-us-east-1}"
SECONDARY_REGION="${SECONDARY_REGION:-us-west-2}"
LOG_FILE="backup-verification-$(date +%Y%m%d-%H%M%S).log"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Verify RDS snapshots
verify_rds_snapshots() {
    log "Verifying RDS snapshots..."

    # Get latest snapshot in primary region
    PRIMARY_SNAPSHOT=$(aws rds describe-db-snapshots \
        --region "$PRIMARY_REGION" \
        --query 'DBSnapshots | sort_by(@, &SnapshotCreateTime)[-1].DBSnapshotIdentifier' \
        --output text)

    if [ "$PRIMARY_SNAPSHOT" = "None" ] || [ -z "$PRIMARY_SNAPSHOT" ]; then
        error "No RDS snapshots found in primary region"
        return 1
    fi

    success "Found latest snapshot: $PRIMARY_SNAPSHOT"

    # Verify snapshot is recent (within last 24 hours)
    SNAPSHOT_TIME=$(aws rds describe-db-snapshots \
        --region "$PRIMARY_REGION" \
        --db-snapshot-identifier "$PRIMARY_SNAPSHOT" \
        --query 'DBSnapshots[0].SnapshotCreateTime' \
        --output text)

    SNAPSHOT_AGE_HOURS=$(( ( $(date +%s) - $(date -d "$SNAPSHOT_TIME" +%s) ) / 3600 ))

    if [ "$SNAPSHOT_AGE_HOURS" -gt 24 ]; then
        warn "Snapshot is ${SNAPSHOT_AGE_HOURS} hours old (> 24 hours)"
    else
        success "Snapshot age: ${SNAPSHOT_AGE_HOURS} hours (acceptable)"
    fi

    # Verify snapshot status
    SNAPSHOT_STATUS=$(aws rds describe-db-snapshots \
        --region "$PRIMARY_REGION" \
        --db-snapshot-identifier "$PRIMARY_SNAPSHOT" \
        --query 'DBSnapshots[0].Status' \
        --output text)

    if [ "$SNAPSHOT_STATUS" != "available" ]; then
        error "Snapshot status is $SNAPSHOT_STATUS (expected: available)"
        return 1
    fi

    success "Snapshot status: $SNAPSHOT_STATUS"

    # Verify cross-region copy exists
    SECONDARY_SNAPSHOT=$(aws rds describe-db-snapshots \
        --region "$SECONDARY_REGION" \
        --query "DBSnapshots[?contains(DBSnapshotIdentifier, '$(echo $PRIMARY_SNAPSHOT | cut -d':' -f2)')].DBSnapshotIdentifier | [0]" \
        --output text)

    if [ "$SECONDARY_SNAPSHOT" = "None" ] || [ -z "$SECONDARY_SNAPSHOT" ]; then
        warn "No cross-region snapshot copy found in secondary region"
    else
        success "Cross-region snapshot exists: $SECONDARY_SNAPSHOT"
    fi

    return 0
}

# Verify S3 replication
verify_s3_replication() {
    log "Verifying S3 replication..."

    # Get primary bucket
    PRIMARY_BUCKET=$(aws s3api list-buckets \
        --region "$PRIMARY_REGION" \
        --query "Buckets[?contains(Name, 'primary')].Name | [0]" \
        --output text)

    if [ "$PRIMARY_BUCKET" = "None" ] || [ -z "$PRIMARY_BUCKET" ]; then
        error "No primary S3 bucket found"
        return 1
    fi

    success "Primary bucket: $PRIMARY_BUCKET"

    # Check replication configuration
    REPLICATION_STATUS=$(aws s3api get-bucket-replication \
        --bucket "$PRIMARY_BUCKET" \
        --region "$PRIMARY_REGION" \
        --query 'ReplicationConfiguration.Rules[0].Status' \
        --output text 2>/dev/null || echo "None")

    if [ "$REPLICATION_STATUS" != "Enabled" ]; then
        error "S3 replication is not enabled"
        return 1
    fi

    success "S3 replication status: $REPLICATION_STATUS"

    # Get replica bucket
    REPLICA_BUCKET=$(aws s3api get-bucket-replication \
        --bucket "$PRIMARY_BUCKET" \
        --region "$PRIMARY_REGION" \
        --query 'ReplicationConfiguration.Rules[0].Destination.Bucket' \
        --output text | cut -d':' -f6)

    success "Replica bucket: $REPLICA_BUCKET"

    # Compare object counts
    PRIMARY_COUNT=$(aws s3 ls s3://"$PRIMARY_BUCKET"/ --recursive --region "$PRIMARY_REGION" | wc -l)
    REPLICA_COUNT=$(aws s3 ls s3://"$REPLICA_BUCKET"/ --recursive --region "$SECONDARY_REGION" | wc -l)

    log "Primary bucket object count: $PRIMARY_COUNT"
    log "Replica bucket object count: $REPLICA_COUNT"

    REPLICATION_PERCENTAGE=$(awk "BEGIN {printf \"%.2f\", ($REPLICA_COUNT / $PRIMARY_COUNT) * 100}")

    if (( $(echo "$REPLICATION_PERCENTAGE < 95" | bc -l) )); then
        warn "Replication percentage: ${REPLICATION_PERCENTAGE}% (< 95%)"
    else
        success "Replication percentage: ${REPLICATION_PERCENTAGE}%"
    fi

    return 0
}

# Verify Route53 health checks
verify_health_checks() {
    log "Verifying Route53 health checks..."

    # List health checks
    HEALTH_CHECKS=$(aws route53 list-health-checks \
        --query 'HealthChecks[*].Id' \
        --output text)

    if [ -z "$HEALTH_CHECKS" ]; then
        error "No health checks found"
        return 1
    fi

    success "Found $(echo $HEALTH_CHECKS | wc -w) health check(s)"

    # Check each health check status
    for HC_ID in $HEALTH_CHECKS; do
        HC_STATUS=$(aws route53 get-health-check-status \
            --health-check-id "$HC_ID" \
            --query 'HealthCheckObservations[0].StatusReport.Status' \
            --output text)

        if [ "$HC_STATUS" != "Success" ]; then
            error "Health check $HC_ID status: $HC_STATUS"
        else
            success "Health check $HC_ID status: $HC_STATUS"
        fi
    done

    return 0
}

# Test restore capability (dry run)
test_restore() {
    log "Testing restore capability (dry run)..."

    # Verify IAM permissions
    log "Checking IAM permissions..."

    aws sts get-caller-identity > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        success "IAM credentials valid"
    else
        error "IAM credentials invalid or expired"
        return 1
    fi

    # Check if we can describe instances
    aws ec2 describe-instances --region "$SECONDARY_REGION" --max-results 1 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        success "Can access EC2 in secondary region"
    else
        warn "Cannot access EC2 in secondary region"
    fi

    # Check if we can describe RDS instances
    aws rds describe-db-instances --region "$SECONDARY_REGION" --max-results 1 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        success "Can access RDS in secondary region"
    else
        warn "Cannot access RDS in secondary region"
    fi

    log "Restore capability verified (dry run complete)"
    return 0
}

# Generate report
generate_report() {
    log "Generating verification report..."

    REPORT_FILE="backup-verification-report-$(date +%Y%m%d-%H%M%S).json"

    cat > "$REPORT_FILE" <<EOF
{
  "verification_time": "$(date -Iseconds)",
  "primary_region": "$PRIMARY_REGION",
  "secondary_region": "$SECONDARY_REGION",
  "results": {
    "rds_snapshots": "$(grep -c 'RDS.*SUCCESS' $LOG_FILE || echo 0)",
    "s3_replication": "$(grep -c 'S3.*SUCCESS' $LOG_FILE || echo 0)",
    "health_checks": "$(grep -c 'Health check.*SUCCESS' $LOG_FILE || echo 0)",
    "restore_test": "$(grep -c 'Restore capability verified' $LOG_FILE || echo 0)"
  },
  "errors": $(grep -c ERROR $LOG_FILE || echo 0),
  "warnings": $(grep -c WARNING $LOG_FILE || echo 0),
  "log_file": "$LOG_FILE"
}
EOF

    success "Report generated: $REPORT_FILE"
    cat "$REPORT_FILE"
}

# Main execution
main() {
    log "========================================"
    log "Starting Multi-Region Backup Verification"
    log "Primary Region: $PRIMARY_REGION"
    log "Secondary Region: $SECONDARY_REGION"
    log "========================================"

    FAILED=0

    verify_rds_snapshots || FAILED=$((FAILED + 1))
    echo ""

    verify_s3_replication || FAILED=$((FAILED + 1))
    echo ""

    verify_health_checks || FAILED=$((FAILED + 1))
    echo ""

    test_restore || FAILED=$((FAILED + 1))
    echo ""

    generate_report

    log "========================================"
    if [ $FAILED -eq 0 ]; then
        success "All verification checks passed!"
        log "Log file: $LOG_FILE"
        exit 0
    else
        error "$FAILED verification check(s) failed"
        log "Log file: $LOG_FILE"
        exit 1
    fi
}

# Run main function
main
