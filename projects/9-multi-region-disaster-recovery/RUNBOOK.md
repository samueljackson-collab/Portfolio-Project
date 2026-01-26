# Runbook — Project 9 (Multi-Region Disaster Recovery Automation)

## Overview

Production operations runbook for the Multi-Region Disaster Recovery platform. This runbook covers failover procedures, replication monitoring, health checks, DR drills, and recovery operations for a resilient multi-region AWS architecture.

**System Components:**
- Primary Region (us-east-1): Active workloads
- Secondary Region (us-west-2): Standby/read replicas
- Route53: Latency-based and failover routing
- Aurora Global Database: Cross-region replication
- S3 Cross-Region Replication: Object storage sync
- EKS Clusters: Application tier (both regions)
- AWS Systems Manager: Automation runbooks
- CloudWatch: Health checks and monitoring
- Lambda: Automated failover orchestration

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **RTO (Recovery Time Objective)** | < 15 minutes | Time from failure → full service restoration |
| **RPO (Recovery Point Objective)** | < 30 seconds | Maximum acceptable data loss |
| **Replication lag** | < 1 second | Aurora global database lag |
| **Health check success rate** | 99.9% | Route53 health check pass rate |
| **DR drill success rate** | 100% | Monthly DR drill completion without issues |
| **Failover success rate** | 99% | Automated failover completion rate |
| **Cross-region latency** | < 100ms | Inter-region communication latency |

---

## Dashboards & Alerts

### Dashboards

#### Multi-Region Health Dashboard
```bash
# Check overall system health
./scripts/multi_region_health.sh

# Expected output:
# Primary Region (us-east-1): HEALTHY
# Secondary Region (us-west-2): HEALTHY
# Aurora Replication Lag: 0.5s
# S3 Replication: UP TO DATE
# Route53 Health Checks: ALL PASSING

# View CloudWatch dashboard
aws cloudwatch get-dashboard --dashboard-name MultiRegionDR --region us-east-1
```

#### Aurora Replication Dashboard
```bash
# Check Aurora global cluster status
aws rds describe-global-clusters --region us-east-1

# Check replication lag
aws rds describe-db-clusters \
  --db-cluster-identifier prod-cluster-us-west-2 \
  --region us-west-2 \
  --query 'DBClusters[0].GlobalWriteForwardingStatus'

# Monitor metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name AuroraGlobalDBReplicationLag \
  --dimensions Name=DBClusterIdentifier,Value=prod-cluster \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum \
  --region us-east-1
```

#### Route53 Health Check Dashboard
```bash
# List health checks
aws route53 list-health-checks

# Check health check status
for health_check in $(aws route53 list-health-checks --query 'HealthChecks[*].Id' --output text); do
  echo "Health Check: $health_check"
  aws route53 get-health-check-status --health-check-id $health_check
done

# View health check history
aws cloudwatch get-metric-statistics \
  --namespace AWS/Route53 \
  --metric-name HealthCheckStatus \
  --dimensions Name=HealthCheckId,Value=abc123 \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average \
  --region us-east-1
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Primary region complete failure | Immediate | Execute automated failover |
| **P0** | Aurora replication broken | Immediate | Investigate and restore replication |
| **P1** | Replication lag > 5 seconds | 5 minutes | Check network, investigate cause |
| **P1** | Route53 health checks failing | 5 minutes | Investigate endpoints, consider failover |
| **P2** | Secondary region degraded | 15 minutes | Investigate, ensure ready for failover |
| **P2** | S3 replication delayed | 15 minutes | Check replication rules and metrics |
| **P3** | Increased cross-region latency | 30 minutes | Monitor, investigate if sustained |

#### Alert Queries

```bash
# Check replication lag
REPLICATION_LAG=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name AuroraGlobalDBReplicationLag \
  --dimensions Name=DBClusterIdentifier,Value=prod-cluster \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Maximum \
  --region us-east-1 \
  --query 'Datapoints[0].Maximum' --output text)

if (( $(echo "$REPLICATION_LAG > 5" | bc -l) )); then
  echo "ALERT: High replication lag: ${REPLICATION_LAG}s"
fi

# Check Route53 health
UNHEALTHY=$(aws route53 list-health-checks --query 'HealthChecks[?HealthCheckConfig.Type==`HTTPS`].Id' --output text | \
  while read hc; do
    aws route53 get-health-check-status --health-check-id $hc --query 'HealthCheckObservations[0].StatusReport.Status' --output text
  done | grep -c "Failure")

if [ $UNHEALTHY -gt 0 ]; then
  echo "ALERT: $UNHEALTHY health checks failing"
fi
```

---

## Standard Operations

### Health Check Operations

#### Verify System Health
```bash
# Comprehensive health check script
./scripts/health_check_all.sh

# Manual verification
# 1. Check primary region
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --region us-east-1 \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name]'

# 2. Check secondary region
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --region us-west-2 \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name]'

# 3. Check EKS clusters
kubectl config use-context arn:aws:eks:us-east-1:123456789:cluster/prod-primary
kubectl get nodes
kubectl get pods -A

kubectl config use-context arn:aws:eks:us-west-2:123456789:cluster/prod-secondary
kubectl get nodes
kubectl get pods -A

# 4. Test application endpoints
curl -f https://app.example.com/health || echo "Primary endpoint failed"
curl -f https://dr.app.example.com/health || echo "Secondary endpoint failed"
```

#### Monitor Replication Status
```bash
# Aurora replication status
aws rds describe-db-clusters \
  --db-cluster-identifier prod-cluster-us-west-2 \
  --region us-west-2 \
  --query 'DBClusters[0].[Status,ReplicationSourceIdentifier]'

# S3 replication status
aws s3api get-bucket-replication \
  --bucket production-data \
  --region us-east-1

# Check replication metrics
aws s3api list-objects-v2 \
  --bucket production-data \
  --region us-east-1 \
  --query 'Contents | length()'

aws s3api list-objects-v2 \
  --bucket production-data-replica \
  --region us-west-2 \
  --query 'Contents | length()'

# EBS snapshot replication
aws ec2 describe-snapshots \
  --owner-ids self \
  --filters "Name=status,Values=completed" \
  --region us-west-2
```

### Failover Operations

#### Automated Failover (Emergency)
```bash
# Trigger automated failover via Systems Manager
aws ssm start-automation-execution \
  --document-name "DR-Failover-Primary-to-Secondary" \
  --parameters '{"TargetRegion": ["us-west-2"], "NotificationEmail": ["ops@example.com"]}' \
  --region us-east-1

# Get execution ID
EXECUTION_ID=$(aws ssm start-automation-execution ... --query 'AutomationExecutionId' --output text)

# Monitor execution
watch -n 5 "aws ssm describe-automation-executions \
  --filters Key=ExecutionId,Values=$EXECUTION_ID \
  --region us-east-1 \
  --query 'AutomationExecutionMetadataList[0].[AutomationExecutionStatus,CurrentStepName]'"

# Wait for completion
aws ssm wait automation-execution-status-success \
  --filters Key=ExecutionId,Values=$EXECUTION_ID \
  --region us-east-1

# Verify failover
./scripts/verify_failover.sh
```

#### Manual Failover (Controlled)
```bash
# Step 1: Pre-failover checks
./scripts/preflight_checks.sh

# Step 2: Announce maintenance window
./scripts/send_notification.sh "DR Failover Test starting at $(date)"

# Step 3: Stop writes to primary Aurora cluster (optional for zero data loss)
aws rds failover-db-cluster \
  --db-cluster-identifier prod-cluster \
  --region us-east-1

# Step 4: Promote secondary Aurora cluster to primary
aws rds remove-from-global-cluster \
  --global-cluster-identifier global-prod-cluster \
  --db-cluster-identifier arn:aws:rds:us-west-2:123456789:cluster:prod-cluster-us-west-2 \
  --region us-west-2

# Step 5: Update Route53 to point to secondary region
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch file://failover-dns-change.json

# Example failover-dns-change.json:
cat > failover-dns-change.json << 'EOF'
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "app.example.com",
      "Type": "A",
      "SetIdentifier": "Primary",
      "Failover": "PRIMARY",
      "AliasTarget": {
        "HostedZoneId": "Z2FDTNDATAQYW2",
        "DNSName": "dr-alb-us-west-2.us-west-2.elb.amazonaws.com",
        "EvaluateTargetHealth": true
      }
    }
  }]
}
EOF

# Step 6: Scale up secondary region EKS
kubectl config use-context arn:aws:eks:us-west-2:123456789:cluster/prod-secondary
kubectl scale deployment --all --replicas=3 -n production

# Step 7: Verify failover
curl -f https://app.example.com/health
./scripts/smoke_tests.sh

# Step 8: Monitor for issues
./scripts/monitor_post_failover.sh --duration 3600
```

#### Fallback (Return to Primary)
```bash
# Step 1: Verify primary region is healthy
./scripts/health_check_region.sh --region us-east-1

# Step 2: Recreate Aurora global cluster
aws rds create-global-cluster \
  --global-cluster-identifier global-prod-cluster \
  --source-db-cluster-identifier arn:aws:rds:us-west-2:123456789:cluster:prod-cluster-us-west-2 \
  --region us-west-2

# Step 3: Add primary region back as secondary
aws rds create-db-cluster \
  --db-cluster-identifier prod-cluster \
  --engine aurora-postgresql \
  --global-cluster-identifier global-prod-cluster \
  --region us-east-1

# Step 4: Wait for replication to catch up
while true; do
  LAG=$(aws cloudwatch get-metric-statistics \
    --namespace AWS/RDS \
    --metric-name AuroraGlobalDBReplicationLag \
    --dimensions Name=DBClusterIdentifier,Value=prod-cluster \
    --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Maximum \
    --region us-east-1 \
    --query 'Datapoints[0].Maximum' --output text)

  echo "Replication lag: ${LAG}s"
  if (( $(echo "$LAG < 2" | bc -l) )); then
    echo "Replication caught up"
    break
  fi
  sleep 30
done

# Step 5: Failover back to primary
# Repeat manual failover steps, but in reverse (us-west-2 → us-east-1)
```

### DR Drill Operations

#### Monthly DR Drill Procedure
```bash
# Script for monthly DR drill
cat > scripts/monthly_dr_drill.sh << 'EOF'
#!/bin/bash
set -e

DRILL_LOG="dr_drills/drill-$(date +%Y%m%d-%H%M).log"
mkdir -p dr_drills

echo "===== DR Drill Started at $(date) =====" | tee $DRILL_LOG

# 1. Document current state
echo "Documenting current state..." | tee -a $DRILL_LOG
./scripts/snapshot_current_state.sh >> $DRILL_LOG

# 2. Pre-drill health checks
echo "Running pre-drill health checks..." | tee -a $DRILL_LOG
./scripts/preflight_checks.sh >> $DRILL_LOG 2>&1

# 3. Start timer
START_TIME=$(date +%s)

# 4. Trigger failover
echo "Triggering failover to secondary region..." | tee -a $DRILL_LOG
aws ssm start-automation-execution \
  --document-name "DR-Failover-Primary-to-Secondary" \
  --parameters '{"TargetRegion": ["us-west-2"]}' \
  --region us-east-1 | tee -a $DRILL_LOG

EXECUTION_ID=$(aws ssm describe-automation-executions ... --query 'AutomationExecutionMetadataList[0].AutomationExecutionId' --output text)

# 5. Wait for completion
echo "Waiting for failover completion..." | tee -a $DRILL_LOG
aws ssm wait automation-execution-status-success \
  --filters Key=ExecutionId,Values=$EXECUTION_ID \
  --region us-east-1

# 6. Calculate RTO
END_TIME=$(date +%s)
RTO=$((END_TIME - START_TIME))
echo "RTO: ${RTO} seconds ($(($RTO / 60)) minutes)" | tee -a $DRILL_LOG

# 7. Verify failover
echo "Verifying failover..." | tee -a $DRILL_LOG
./scripts/verify_failover.sh >> $DRILL_LOG 2>&1

# 8. Run smoke tests
echo "Running smoke tests..." | tee -a $DRILL_LOG
./scripts/smoke_tests.sh >> $DRILL_LOG 2>&1

# 9. Document results
echo "===== DR Drill Completed at $(date) =====" | tee -a $DRILL_LOG
echo "Target RTO: 900 seconds (15 minutes)" | tee -a $DRILL_LOG
echo "Actual RTO: ${RTO} seconds" | tee -a $DRILL_LOG

if [ $RTO -lt 900 ]; then
  echo "Status: PASS ✓" | tee -a $DRILL_LOG
else
  echo "Status: FAIL - RTO exceeded target" | tee -a $DRILL_LOG
fi

# 10. Fallback to primary
echo "Initiating fallback to primary region..." | tee -a $DRILL_LOG
./scripts/fallback_to_primary.sh >> $DRILL_LOG 2>&1

# 11. Generate report
python scripts/generate_dr_report.py --log $DRILL_LOG --output dr_drills/report-$(date +%Y%m%d).html

echo "DR drill completed. Report: dr_drills/report-$(date +%Y%m%d).html" | tee -a $DRILL_LOG
EOF

chmod +x scripts/monthly_dr_drill.sh
```

#### Execute DR Drill
```bash
# Run monthly drill
./scripts/monthly_dr_drill.sh

# Or use scheduled automation
# Create EventBridge rule for monthly execution
aws events put-rule \
  --name monthly-dr-drill \
  --schedule-expression "cron(0 3 1 * ? *)" \
  --state ENABLED \
  --region us-east-1

aws events put-targets \
  --rule monthly-dr-drill \
  --targets "Id=1,Arn=arn:aws:ssm:us-east-1:123456789:automation-definition/DR-Drill,RoleArn=arn:aws:iam::123456789:role/EventsRole" \
  --region us-east-1
```

### Replication Management

#### Monitor Replication Lag
```bash
# Real-time lag monitoring
watch -n 5 'aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name AuroraGlobalDBReplicationLag \
  --dimensions Name=DBClusterIdentifier,Value=prod-cluster \
  --start-time $(date -u -d "5 minutes ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Maximum \
  --region us-east-1 \
  --query "Datapoints[0].Maximum"'
```

#### Fix Broken Replication
```bash
# If Aurora replication breaks
# 1. Check cluster status
aws rds describe-global-clusters --region us-east-1

# 2. Check for errors
aws rds describe-db-clusters \
  --db-cluster-identifier prod-cluster-us-west-2 \
  --region us-west-2

# 3. Remove and re-add to global cluster
aws rds remove-from-global-cluster \
  --global-cluster-identifier global-prod-cluster \
  --db-cluster-identifier arn:aws:rds:us-west-2:123456789:cluster:prod-cluster-us-west-2 \
  --region us-west-2

aws rds modify-db-cluster \
  --db-cluster-identifier prod-cluster-us-west-2 \
  --region us-west-2 \
  --apply-immediately

# 4. Recreate as secondary
aws rds create-db-cluster \
  --db-cluster-identifier prod-cluster-us-west-2-new \
  --engine aurora-postgresql \
  --global-cluster-identifier global-prod-cluster \
  --region us-west-2

# 5. Verify replication restored
aws rds describe-db-clusters \
  --db-cluster-identifier prod-cluster-us-west-2-new \
  --region us-west-2 \
  --query 'DBClusters[0].GlobalWriteForwardingStatus'
```

---

## Incident Response

### Detection

**Automated Detection:**
- Route53 health check failures
- Aurora replication lag alerts
- CloudWatch alarms for regional outages
- Lambda-based health monitoring

**Manual Detection:**
```bash
# Check for regional issues
aws health describe-events \
  --filter eventTypeCategories=issue,accountSpecific \
  --region us-east-1

# Test primary region
curl -f https://app.example.com/health || echo "Primary region unhealthy"

# Test secondary region
curl -f https://dr.app.example.com/health || echo "Secondary region unhealthy"

# Check AWS status
curl https://status.aws.amazon.com/
```

### Triage

#### Severity Classification

### P0: Primary Region Complete Failure
- All services in primary region unavailable
- Cannot reach any primary endpoints
- Multiple health checks failing

### P1: Partial Primary Region Failure
- Some services degraded in primary region
- Elevated error rates
- Replication lag > 10 seconds

### P2: Secondary Region Issues
- Secondary region degraded but primary healthy
- Replication delayed but functional
- DR drill failures

### P3: Warning State
- Elevated latency between regions
- Minor replication delays
- Individual health check failures

### Incident Response Procedures

#### P0: Primary Region Complete Failure

**Immediate Actions (0-5 minutes):**
```bash
# 1. Confirm primary region failure
./scripts/verify_region_failure.sh --region us-east-1

# 2. Check AWS Service Health Dashboard
aws health describe-events --region us-east-1

# 3. Notify stakeholders
./scripts/send_incident_notification.sh \
  --severity P0 \
  --message "Primary region failure detected, initiating failover"

# 4. Trigger automated failover
aws ssm start-automation-execution \
  --document-name "DR-Failover-Primary-to-Secondary" \
  --parameters '{"TargetRegion": ["us-west-2"], "Emergency": ["true"]}' \
  --region us-west-2  # Note: Execute from secondary region

# 5. Monitor failover progress
EXECUTION_ID=$(aws ssm describe-automation-executions ... --query 'AutomationExecutionMetadataList[0].AutomationExecutionId' --output text)
watch -n 10 "aws ssm describe-automation-executions --filters Key=ExecutionId,Values=$EXECUTION_ID --region us-west-2"
```

**Validation (5-15 minutes):**
```bash
# 1. Verify DNS failover
dig app.example.com +short
nslookup app.example.com

# 2. Test application endpoints
curl -f https://app.example.com/health
curl -f https://app.example.com/api/status

# 3. Verify Aurora promotion
aws rds describe-db-clusters \
  --db-cluster-identifier prod-cluster-us-west-2 \
  --region us-west-2 \
  --query 'DBClusters[0].[Status,ReplicationSourceIdentifier]'

# 4. Check EKS workloads
kubectl config use-context arn:aws:eks:us-west-2:123456789:cluster/prod-secondary
kubectl get pods -A
kubectl get svc -A

# 5. Run smoke tests
./scripts/smoke_tests.sh --region us-west-2
```

**Post-Failover Monitoring (15+ minutes):**
```bash
# Monitor application metrics
./scripts/monitor_post_failover.sh --duration 3600

# Check for errors
kubectl logs -n production -l app=web --since=15m | grep ERROR

# Monitor Aurora performance
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBClusterIdentifier,Value=prod-cluster-us-west-2 \
  --start-time $(date -u -d '15 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum \
  --region us-west-2
```

#### P1: High Replication Lag

**Investigation:**
```bash
# 1. Check current lag
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name AuroraGlobalDBReplicationLag \
  --dimensions Name=DBClusterIdentifier,Value=prod-cluster \
  --start-time $(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Maximum \
  --region us-east-1

# 2. Check network connectivity
aws ec2 describe-vpc-peering-connections --region us-east-1

# 3. Check Aurora metrics
aws rds describe-db-clusters \
  --db-cluster-identifier prod-cluster \
  --region us-east-1 \
  --query 'DBClusters[0].[Status,ClusterCreateTime]'

# 4. Check for heavy write load
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name WriteIOPS \
  --dimensions Name=DBClusterIdentifier,Value=prod-cluster \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum \
  --region us-east-1
```

**Mitigation:**
```bash
# Option 1: Scale up Aurora secondary
aws rds modify-db-cluster \
  --db-cluster-identifier prod-cluster-us-west-2 \
  --region us-west-2 \
  --apply-immediately

# Option 2: Reduce write load on primary
kubectl scale deployment write-heavy-app --replicas=2 -n production

# Option 3: Optimize queries causing lag
# Identify slow queries
aws rds describe-db-log-files \
  --db-instance-identifier prod-cluster-instance-1 \
  --region us-east-1

# Option 4: Increase replication capacity
aws rds add-db-cluster-parameter-group \
  --db-cluster-parameter-group-name custom-replication \
  --region us-east-1
```

#### P1: Route53 Health Checks Failing

**Investigation:**
```bash
# 1. Check which health checks are failing
for hc in $(aws route53 list-health-checks --query 'HealthChecks[*].Id' --output text); do
  STATUS=$(aws route53 get-health-check-status --health-check-id $hc --query 'HealthCheckObservations[0].StatusReport.Status' --output text)
  if [ "$STATUS" == "Failure" ]; then
    echo "Health check $hc is failing"
    aws route53 get-health-check --health-check-id $hc
  fi
done

# 2. Test endpoints directly
curl -v https://app.example.com/health
curl -v https://dr.app.example.com/health

# 3. Check load balancer health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789:targetgroup/prod-tg/abc123 \
  --region us-east-1
```

**Mitigation:**
```bash
# If application issue, restart pods
kubectl rollout restart deployment/web -n production

# If load balancer issue, deregister/register targets
aws elbv2 deregister-targets --target-group-arn <arn> --targets Id=<instance-id> --region us-east-1
aws elbv2 register-targets --target-group-arn <arn> --targets Id=<instance-id> --region us-east-1

# If health check misconfigured, update
aws route53 update-health-check \
  --health-check-id abc123 \
  --health-threshold 3 \
  --failure-threshold 3

# If persistent, trigger failover
./scripts/failover_to_secondary.sh
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# DR Incident Report

**Date:** $(date)
**Severity:** P0
**Duration:** 12 minutes
**Affected Component:** Primary region (us-east-1)

## Timeline
- 10:00: Primary region health checks failed
- 10:02: Confirmed AWS regional issue
- 10:03: Triggered automated failover
- 10:08: Secondary region promoted to primary
- 10:10: DNS failover completed
- 10:12: Service fully restored in us-west-2

## Root Cause
AWS regional outage in us-east-1 affecting EC2 and RDS services

## Action Items
- [x] Failover executed successfully
- [x] Service restored within RTO target
- [ ] Review and optimize failover automation
- [ ] Update monitoring thresholds
- [ ] Conduct post-incident review

## Recovery Metrics
- RTO Target: 15 minutes
- Actual RTO: 12 minutes ✓
- RPO Target: 30 seconds
- Actual RPO: ~5 seconds ✓

EOF

# Generate detailed metrics report
python scripts/generate_incident_metrics.py \
  --start "2025-11-10T10:00:00" \
  --end "2025-11-10T10:12:00" \
  > incidents/metrics-$(date +%Y%m%d-%H%M).html
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Replication Lag Increasing

**Symptoms:**
```bash
$ aws cloudwatch get-metric-statistics ... AuroraGlobalDBReplicationLag
Replication lag: 15.3 seconds (increasing)
```

**Diagnosis:**
```bash
# Check network connectivity
aws ec2 describe-vpc-peering-connections --region us-east-1

# Check Aurora CPU/memory
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBClusterIdentifier,Value=prod-cluster-us-west-2 \
  --region us-west-2

# Check for blocking transactions
psql -h prod-cluster-us-west-2.cluster-xxx.us-west-2.rds.amazonaws.com -U admin -d prod -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

**Solution:**
```bash
# Scale up secondary cluster
aws rds modify-db-instance \
  --db-instance-identifier prod-cluster-us-west-2-instance-1 \
  --db-instance-class db.r6g.2xlarge \
  --apply-immediately \
  --region us-west-2

# Or add read replica to distribute load
aws rds create-db-instance \
  --db-instance-identifier prod-cluster-us-west-2-instance-2 \
  --db-instance-class db.r6g.xlarge \
  --engine aurora-postgresql \
  --db-cluster-identifier prod-cluster-us-west-2 \
  --region us-west-2
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Morning health check
./scripts/multi_region_health.sh

# Check replication status
./scripts/check_replication.sh

# Review Route53 health checks
for hc in $(aws route53 list-health-checks --query 'HealthChecks[*].Id' --output text); do
  aws route53 get-health-check-status --health-check-id $hc
done

# Check for AWS service issues
aws health describe-events --region us-east-1
aws health describe-events --region us-west-2
```

### Monthly Tasks

```bash
# Execute DR drill
./scripts/monthly_dr_drill.sh

# Review and update runbooks
git pull
# Update procedures based on drill results

# Test backup restoration
./scripts/test_backup_restore.sh

# Review RTO/RPO metrics
python scripts/analyze_rto_rpo.py --month $(date +%Y-%m)

# Update disaster recovery documentation
vim docs/dr_procedures.md
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO**: < 30 seconds (Aurora global replication)
- **RTO**: < 15 minutes (automated failover)

### Backup Strategy

```bash
# Automated backups configured via Terraform
# - Aurora automated backups: 7 days retention
# - EBS snapshots: Daily, replicated to secondary region
# - S3 cross-region replication: Continuous
```

---

## Quick Reference Card

### Most Common Operations

```bash
# Check system health
./scripts/multi_region_health.sh

# Trigger failover
aws ssm start-automation-execution --document-name "DR-Failover-Primary-to-Secondary"

# Check replication lag
aws cloudwatch get-metric-statistics --metric-name AuroraGlobalDBReplicationLag

# Run DR drill
./scripts/monthly_dr_drill.sh

# Fallback to primary
./scripts/fallback_to_primary.sh
```

### Emergency Response

```bash
# P0: Primary region down
aws ssm start-automation-execution --document-name "DR-Failover-Primary-to-Secondary" --region us-west-2

# P1: High replication lag
aws rds modify-db-instance --db-instance-class db.r6g.2xlarge --apply-immediately

# P1: Health checks failing
kubectl rollout restart deployment/web -n production
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Infrastructure Team
- **Review Schedule:** Quarterly or after DR events
- **Feedback:** Create issue or submit PR with updates
