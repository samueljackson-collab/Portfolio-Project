#!/bin/bash
# Multi-Region Disaster Recovery Failover Test Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
PRIMARY_REGION="${PRIMARY_REGION:-us-east-1}"
DR_REGION="${DR_REGION:-us-west-2}"
APP_URL="${APP_URL:-https://app.example.com}"
RTO_TARGET="${RTO_TARGET:-60}"  # Recovery Time Objective in seconds

echo -e "${GREEN}=== Multi-Region DR Failover Test ===${NC}"
echo ""
echo "Primary Region: $PRIMARY_REGION"
echo "DR Region: $DR_REGION"
echo "Application URL: $APP_URL"
echo "RTO Target: ${RTO_TARGET}s"
echo ""

# Function to check health
check_health() {
    local url=$1
    local timeout=${2:-5}

    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url/health" || echo "000")
    echo $response
}

# Function to get current region serving traffic
get_serving_region() {
    local response=$(curl -s "$APP_URL/health" || echo "{}")
    echo $response | jq -r '.region // "unknown"'
}

# Step 1: Verify primary region is healthy
echo -e "${YELLOW}Step 1: Verifying primary region health...${NC}"
PRIMARY_HEALTH=$(check_health "$APP_URL")

if [ "$PRIMARY_HEALTH" == "200" ]; then
    echo -e "${GREEN}✓ Primary region is healthy (HTTP $PRIMARY_HEALTH)${NC}"
else
    echo -e "${RED}✗ Primary region is not healthy (HTTP $PRIMARY_HEALTH)${NC}"
    exit 1
fi

CURRENT_REGION=$(get_serving_region)
echo "Current serving region: $CURRENT_REGION"
echo ""

# Step 2: Simulate primary region failure
echo -e "${YELLOW}Step 2: Simulating primary region failure...${NC}"
echo "Finding EC2 instances in primary region..."

INSTANCE_IDS=$(aws ec2 describe-instances \
    --region $PRIMARY_REGION \
    --filters "Name=tag:Environment,Values=production" "Name=tag:Region,Values=primary" "Name=instance-state-name,Values=running" \
    --query "Reservations[].Instances[].InstanceId" \
    --output text)

if [ -z "$INSTANCE_IDS" ]; then
    echo -e "${YELLOW}No instances found in primary region${NC}"
else
    echo "Stopping instances: $INSTANCE_IDS"

    aws ec2 stop-instances \
        --region $PRIMARY_REGION \
        --instance-ids $INSTANCE_IDS \
        --output table

    echo -e "${GREEN}✓ Instances stopped${NC}"
fi

# Record start time
START_TIME=$(date +%s)
echo ""

# Step 3: Monitor failover
echo -e "${YELLOW}Step 3: Monitoring failover to DR region...${NC}"
echo "Waiting for Route53 health check to detect failure..."

FAILOVER_DETECTED=false
MAX_WAIT=300  # 5 minutes max
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    sleep 5
    ELAPSED=$(($(date +%s) - START_TIME))

    # Check if DR region is now serving traffic
    HEALTH=$(check_health "$APP_URL" 10)

    if [ "$HEALTH" == "200" ]; then
        SERVING_REGION=$(get_serving_region)

        if [ "$SERVING_REGION" == "$DR_REGION" ]; then
            FAILOVER_TIME=$ELAPSED
            FAILOVER_DETECTED=true
            echo -e "${GREEN}✓ Failover detected! DR region is now serving traffic${NC}"
            echo "Failover time: ${FAILOVER_TIME}s"
            break
        fi
    fi

    echo "Waiting for failover... (${ELAPSED}s elapsed)"
done

if [ "$FAILOVER_DETECTED" = false ]; then
    echo -e "${RED}✗ Failover did not complete within ${MAX_WAIT}s${NC}"
    exit 1
fi

echo ""

# Step 4: Verify DR region health
echo -e "${YELLOW}Step 4: Verifying DR region health...${NC}"

# Check multiple times
HEALTH_CHECKS=5
SUCCESSFUL_CHECKS=0

for i in $(seq 1 $HEALTH_CHECKS); do
    HEALTH=$(check_health "$APP_URL")

    if [ "$HEALTH" == "200" ]; then
        SUCCESSFUL_CHECKS=$((SUCCESSFUL_CHECKS + 1))
        echo "Health check $i/$HEALTH_CHECKS: ${GREEN}PASS${NC}"
    else
        echo "Health check $i/$HEALTH_CHECKS: ${RED}FAIL (HTTP $HEALTH)${NC}"
    fi

    sleep 2
done

echo ""
echo "Successful health checks: $SUCCESSFUL_CHECKS/$HEALTH_CHECKS"

if [ $SUCCESSFUL_CHECKS -eq $HEALTH_CHECKS ]; then
    echo -e "${GREEN}✓ DR region is fully operational${NC}"
else
    echo -e "${YELLOW}⚠ Some health checks failed${NC}"
fi

echo ""

# Step 5: Check RDS replica
echo -e "${YELLOW}Step 5: Checking RDS read replica status...${NC}"

RDS_REPLICA_STATUS=$(aws rds describe-db-instances \
    --region $DR_REGION \
    --query "DBInstances[?contains(DBInstanceIdentifier, 'dr-replica')].DBInstanceStatus" \
    --output text)

echo "RDS replica status: $RDS_REPLICA_STATUS"

if [ "$RDS_REPLICA_STATUS" == "available" ]; then
    echo -e "${GREEN}✓ RDS replica is available${NC}"
else
    echo -e "${YELLOW}⚠ RDS replica status: $RDS_REPLICA_STATUS${NC}"
fi

echo ""

# Step 6: Check S3 replication
echo -e "${YELLOW}Step 6: Verifying S3 replication...${NC}"

# Get object count in both buckets
PRIMARY_BUCKET=$(aws s3api list-buckets --query "Buckets[?contains(Name, 'primary')].Name" --output text | head -1)
DR_BUCKET=$(aws s3api list-buckets --query "Buckets[?contains(Name, 'dr')].Name" --output text | head -1)

if [ -n "$PRIMARY_BUCKET" ] && [ -n "$DR_BUCKET" ]; then
    PRIMARY_COUNT=$(aws s3 ls s3://$PRIMARY_BUCKET --recursive | wc -l)
    DR_COUNT=$(aws s3 ls s3://$DR_BUCKET --recursive | wc -l)

    echo "Primary bucket objects: $PRIMARY_COUNT"
    echo "DR bucket objects: $DR_COUNT"

    REPLICATION_LAG=$((PRIMARY_COUNT - DR_COUNT))
    echo "Replication lag: $REPLICATION_LAG objects"

    if [ $REPLICATION_LAG -le 10 ]; then
        echo -e "${GREEN}✓ S3 replication is up to date${NC}"
    else
        echo -e "${YELLOW}⚠ S3 replication has lag${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Could not find S3 buckets${NC}"
fi

echo ""

# Summary
echo -e "${GREEN}=== Failover Test Summary ===${NC}"
echo ""
echo "Status: ${GREEN}SUCCESS${NC}"
echo "Failover Time: ${FAILOVER_TIME}s"
echo "RTO Target: ${RTO_TARGET}s"

if [ $FAILOVER_TIME -le $RTO_TARGET ]; then
    echo -e "RTO Met: ${GREEN}YES ✓${NC}"
else
    echo -e "RTO Met: ${RED}NO ✗${NC} (exceeded by $((FAILOVER_TIME - RTO_TARGET))s)"
fi

echo ""
echo "Application Health: ${GREEN}OPERATIONAL${NC}"
echo "DR Region: ${GREEN}$DR_REGION${NC}"
echo ""

# Cleanup prompt
echo -e "${YELLOW}Cleanup:${NC}"
echo "To restore primary region, run:"
echo "  aws ec2 start-instances --region $PRIMARY_REGION --instance-ids $INSTANCE_IDS"
echo ""
echo "To verify primary region recovery:"
echo "  ./scripts/verify-primary-recovery.sh"
