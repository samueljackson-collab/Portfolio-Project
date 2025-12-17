# Runbook — P10 (Multi-Region Architecture)

## Overview

Production operations runbook for AWS multi-region infrastructure. This runbook covers active-passive failover management, Route 53 DNS operations, cross-region RDS replication, disaster recovery procedures, and troubleshooting for global high-availability architecture.

**System Components:**
- Route 53 DNS with health checks and failover policies
- Primary Region (us-east-1): Active deployment
- Secondary Region (us-west-2): Passive/standby deployment
- Cross-region RDS read replicas
- S3 cross-region replication (CRR)
- Application Load Balancers (ALB) in each region
- EC2 Auto Scaling groups
- CloudFormation stack sets for multi-region deployment

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Global availability** | 99.99% | Combined uptime across regions |
| **RTO (Recovery Time Objective)** | < 15 minutes | Time to failover to secondary |
| **RPO (Recovery Point Objective)** | < 5 minutes | RDS replication lag |
| **DNS failover time** | < 60 seconds | Route 53 health check + TTL |
| **RDS replication lag** | < 30 seconds | Average replication delay |
| **S3 replication time** | < 15 minutes | Cross-region replication SLA |
| **Health check success rate** | 99.5% | Route 53 health checks passing |

---

## Dashboards & Alerts

### Dashboards

#### Multi-Region Health Dashboard
```bash
# Check Route 53 health checks
aws route53 list-health-checks --query 'HealthChecks[*].[Id,HealthCheckConfig.FullyQualifiedDomainName,HealthCheckConfig.Type]' --output table

# Check health check status
HEALTH_CHECK_ID="<health-check-id>"
aws route53 get-health-check-status --health-check-id $HEALTH_CHECK_ID

# View current DNS routing
dig @8.8.8.8 example.com +short
```

#### Regional Service Status
```bash
# Primary region (us-east-1)
aws elbv2 describe-target-health \
  --target-group-arn <primary-tg-arn> \
  --region us-east-1

# Secondary region (us-west-2)
aws elbv2 describe-target-health \
  --target-group-arn <secondary-tg-arn> \
  --region us-west-2

# Check Auto Scaling group status
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names primary-asg \
  --region us-east-1 \
  --query 'AutoScalingGroups[0].[DesiredCapacity,MinSize,MaxSize,Instances[].HealthStatus]'
```

#### RDS Replication Dashboard
```bash
# Check primary RDS status
aws rds describe-db-instances \
  --db-instance-identifier primary-db \
  --region us-east-1 \
  --query 'DBInstances[0].[DBInstanceStatus,Endpoint.Address]'

# Check read replica status
aws rds describe-db-instances \
  --db-instance-identifier secondary-db-replica \
  --region us-west-2 \
  --query 'DBInstances[0].[DBInstanceStatus,ReadReplicaSourceDBInstanceIdentifier]'

# Check replication lag
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=secondary-db-replica \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region us-west-2
```

#### S3 Replication Dashboard
```bash
# Check replication status
aws s3api get-bucket-replication \
  --bucket primary-bucket \
  --region us-east-1

# List replicated objects
aws s3api list-objects-v2 \
  --bucket primary-bucket \
  --region us-east-1 \
  --query 'Contents[?ReplicationStatus==`COMPLETED`]' \
  --max-items 10

# Check replication metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name ReplicationLatency \
  --dimensions Name=SourceBucket,Value=primary-bucket Name=DestinationBucket,Value=secondary-bucket \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region us-east-1
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Primary region down | Immediate | Execute failover to secondary |
| **P0** | Both regions down | Immediate | Emergency escalation, all hands |
| **P1** | Health check failing | 5 minutes | Investigate, prepare for failover |
| **P1** | RDS replication lag > 5 min | 15 minutes | Check network, increase instance size |
| **P2** | Secondary region unhealthy | 30 minutes | Fix secondary, ensure DR capability |
| **P2** | S3 replication delayed | 1 hour | Check replication configuration |
| **P3** | Single target unhealthy | 2 hours | Auto Scaling will replace |

#### Alert Queries

**Check primary region health:**
```bash
# Health check status
HEALTH_STATUS=$(aws route53 get-health-check-status \
  --health-check-id $PRIMARY_HEALTH_CHECK_ID \
  --query 'HealthCheckObservations[0].StatusReport.Status' \
  --output text)

[ "$HEALTH_STATUS" != "Success" ] && echo "ALERT: Primary region health check failing"

# ALB target health
UNHEALTHY_TARGETS=$(aws elbv2 describe-target-health \
  --target-group-arn $PRIMARY_TG_ARN \
  --region us-east-1 \
  --query 'TargetHealthDescriptions[?TargetHealth.State!=`healthy`]' \
  --output json | jq length)

[ $UNHEALTHY_TARGETS -gt 0 ] && echo "ALERT: $UNHEALTHY_TARGETS unhealthy targets in primary"
```

**Monitor RDS replication lag:**
```bash
# Get current replication lag
REPLICATION_LAG=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=secondary-db-replica \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region us-west-2 \
  --query 'Datapoints[0].Average' \
  --output text)

# Alert if lag > 300 seconds (5 minutes)
[ "${REPLICATION_LAG%.*}" -gt 300 ] && echo "ALERT: High replication lag: ${REPLICATION_LAG}s"
```

---

## Standard Operations

### Region Management

#### Check Regional Status
```bash
# List all stacks across regions
make list-stacks

# Check primary region
aws cloudformation describe-stacks \
  --region us-east-1 \
  --query 'Stacks[*].[StackName,StackStatus]' \
  --output table

# Check secondary region
aws cloudformation describe-stacks \
  --region us-west-2 \
  --query 'Stacks[*].[StackName,StackStatus]' \
  --output table

# Verify Route 53 configuration
aws route53 list-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --query "ResourceRecordSets[?Type=='A']"
```

#### Deploy to Primary Region
```bash
# Deploy primary infrastructure
make deploy-primary

# Or manually
aws cloudformation deploy \
  --template-file templates/primary-region.yaml \
  --stack-name primary-infrastructure \
  --region us-east-1 \
  --parameter-overrides \
    Environment=production \
    InstanceType=t3.medium \
  --capabilities CAPABILITY_IAM

# Verify deployment
aws cloudformation describe-stacks \
  --stack-name primary-infrastructure \
  --region us-east-1 \
  --query 'Stacks[0].StackStatus'

# Test primary endpoint
curl -I https://$(aws cloudformation describe-stacks \
  --stack-name primary-infrastructure \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text)
```

#### Deploy to Secondary Region
```bash
# Deploy secondary infrastructure (standby)
make deploy-secondary

# Or manually
aws cloudformation deploy \
  --template-file templates/secondary-region.yaml \
  --stack-name secondary-infrastructure \
  --region us-west-2 \
  --parameter-overrides \
    Environment=production \
    InstanceType=t3.medium \
    PrimaryRegion=us-east-1 \
  --capabilities CAPABILITY_IAM

# Verify deployment
aws cloudformation describe-stacks \
  --stack-name secondary-infrastructure \
  --region us-west-2 \
  --query 'Stacks[0].StackStatus'

# Test secondary endpoint (should be in standby)
curl -I https://$(aws cloudformation describe-stacks \
  --stack-name secondary-infrastructure \
  --region us-west-2 \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text)
```

### Failover Operations

#### Manual Failover to Secondary Region

**Pre-Failover Checklist:**
- [ ] Verify secondary region health
- [ ] Check RDS replica is synchronized
- [ ] Confirm S3 replication is current
- [ ] Notify stakeholders of planned failover
- [ ] Document current state

**Failover Execution (10-15 minutes):**
```bash
# 1. Verify secondary region is ready
make check-health REGION=us-west-2

# 2. Promote RDS read replica to master
aws rds promote-read-replica \
  --db-instance-identifier secondary-db-replica \
  --region us-west-2

# Monitor promotion status
watch -n 5 'aws rds describe-db-instances \
  --db-instance-identifier secondary-db-replica \
  --region us-west-2 \
  --query "DBInstances[0].DBInstanceStatus"'

# 3. Update Auto Scaling desired capacity
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name secondary-asg \
  --desired-capacity 3 \
  --region us-west-2

# Wait for instances to be healthy
watch -n 10 'aws elbv2 describe-target-health \
  --target-group-arn $SECONDARY_TG_ARN \
  --region us-west-2 \
  --query "TargetHealthDescriptions[*].TargetHealth.State"'

# 4. Update Route 53 to point to secondary (if manual failover)
# Disable primary health check to trigger automatic failover
aws route53 update-health-check \
  --health-check-id $PRIMARY_HEALTH_CHECK_ID \
  --disabled

# 5. Verify DNS propagation
watch -n 5 'dig @8.8.8.8 example.com +short'

# 6. Test application in secondary region
curl https://example.com/health

# 7. Monitor application logs and metrics
aws logs tail /aws/ec2/application --region us-west-2 --follow
```

**Post-Failover Verification:**
```bash
# Check traffic is going to secondary
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCount \
  --dimensions Name=LoadBalancer,Value=<secondary-alb> \
  --start-time $(date -u -d '15 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region us-west-2

# Verify database is accepting writes
aws rds describe-db-instances \
  --db-instance-identifier secondary-db-replica \
  --region us-west-2 \
  --query 'DBInstances[0].[DBInstanceStatus,ReadReplicaSourceDBInstanceIdentifier]'
```

#### Failback to Primary Region

**Pre-Failback Checklist:**
- [ ] Primary region issue resolved
- [ ] Primary region fully healthy
- [ ] RDS in primary region ready
- [ ] Application tested in primary region
- [ ] Maintenance window scheduled

**Failback Execution (20-30 minutes):**
```bash
# 1. Verify primary region is healthy
make check-health REGION=us-east-1

# 2. Create new RDS read replica in primary (from current master in secondary)
aws rds create-db-instance-read-replica \
  --db-instance-identifier primary-db-new \
  --source-db-instance-identifier arn:aws:rds:us-west-2:$ACCOUNT_ID:db:secondary-db-replica \
  --db-instance-class db.t3.medium \
  --region us-east-1

# Monitor replication lag until < 1 minute
watch -n 30 'aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=primary-db-new \
  --start-time $(date -u -d "5 minutes ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average \
  --region us-east-1 \
  --query "Datapoints[0].Average"'

# 3. Promote new primary RDS instance
aws rds promote-read-replica \
  --db-instance-identifier primary-db-new \
  --region us-east-1

# 4. Update application configuration to point to new primary
# (Update CloudFormation stack or parameter store)

# 5. Scale up primary region Auto Scaling
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name primary-asg \
  --desired-capacity 3 \
  --region us-east-1

# 6. Re-enable primary health check
aws route53 update-health-check \
  --health-check-id $PRIMARY_HEALTH_CHECK_ID \
  --no-disabled

# 7. Verify DNS failback
watch -n 5 'dig @8.8.8.8 example.com +short'

# 8. Monitor traffic shift to primary
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCount \
  --dimensions Name=LoadBalancer,Value=<primary-alb> \
  --start-time $(date -u -d '15 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region us-east-1

# 9. Scale down secondary to standby
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name secondary-asg \
  --desired-capacity 1 \
  --region us-west-2

# 10. Re-establish replication from primary to secondary
aws rds create-db-instance-read-replica \
  --db-instance-identifier secondary-db-replica-new \
  --source-db-instance-identifier arn:aws:rds:us-east-1:$ACCOUNT_ID:db:primary-db-new \
  --db-instance-class db.t3.medium \
  --region us-west-2
```

### Route 53 Operations

#### Update Health Check
```bash
# View health check configuration
aws route53 get-health-check \
  --health-check-id $HEALTH_CHECK_ID

# Update health check interval
aws route53 update-health-check \
  --health-check-id $HEALTH_CHECK_ID \
  --health-check-version 1 \
  --inverted=false \
  --disabled=false

# Change health check threshold
aws route53 update-health-check \
  --health-check-id $HEALTH_CHECK_ID \
  --failure-threshold 3

# Test health check manually
curl -I $(aws route53 get-health-check \
  --health-check-id $HEALTH_CHECK_ID \
  --query 'HealthCheck.HealthCheckConfig.FullyQualifiedDomainName' \
  --output text)
```

#### Update DNS Records
```bash
# List current records
aws route53 list-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --query "ResourceRecordSets[?Name=='example.com.']"

# Update failover record
cat > change-batch.json << 'EOF'
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "example.com",
      "Type": "A",
      "SetIdentifier": "Primary",
      "Failover": "PRIMARY",
      "AliasTarget": {
        "HostedZoneId": "Z35SXDOTRQ7X7K",
        "DNSName": "primary-alb-123.us-east-1.elb.amazonaws.com",
        "EvaluateTargetHealth": true
      },
      "HealthCheckId": "primary-health-check-id"
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://change-batch.json

# Monitor change propagation
CHANGE_ID=$(aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://change-batch.json \
  --query 'ChangeInfo.Id' \
  --output text)

aws route53 get-change --id $CHANGE_ID
```

### RDS Operations

#### Monitor Replication Lag
```bash
# Current replication lag
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=secondary-db-replica \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum \
  --region us-west-2

# Alert if lag exceeds threshold
CURRENT_LAG=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=secondary-db-replica \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region us-west-2 \
  --query 'Datapoints[0].Average' \
  --output text)

echo "Current replication lag: ${CURRENT_LAG}s"
```

#### Create Manual RDS Snapshot
```bash
# Primary region snapshot
aws rds create-db-snapshot \
  --db-instance-identifier primary-db \
  --db-snapshot-identifier primary-manual-$(date +%Y%m%d-%H%M) \
  --region us-east-1

# Copy snapshot to secondary region
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier arn:aws:rds:us-east-1:$ACCOUNT_ID:snapshot:primary-manual-$(date +%Y%m%d-%H%M) \
  --target-db-snapshot-identifier primary-manual-$(date +%Y%m%d-%H%M)-copy \
  --region us-west-2

# List snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier primary-db \
  --region us-east-1
```

---

## Incident Response

### Detection

**Automated Detection:**
- Route 53 health check failures
- CloudWatch alarms for ALB, RDS, EC2
- Replication lag alerts
- Regional service outages

**Manual Detection:**
```bash
# Check overall health
make test-failover

# Test primary endpoint
curl -I https://example.com

# Check health checks
aws route53 get-health-check-status \
  --health-check-id $PRIMARY_HEALTH_CHECK_ID

# Check regional services
aws elbv2 describe-target-health \
  --target-group-arn $PRIMARY_TG_ARN \
  --region us-east-1
```

### Triage

#### Severity Classification

### P0: Primary Region Complete Outage
- Primary region completely unavailable
- All health checks failing in primary
- No healthy targets in primary ALB
- Critical: Execute immediate failover

### P1: Partial Primary Region Degradation
- > 50% of targets unhealthy
- High error rate in primary
- RDS experiencing issues
- Health checks intermittent
- Prepare for failover

### P2: Secondary Region Issues
- Secondary region degraded
- RDS replication lag high
- S3 replication delayed
- DR capability at risk

### P3: Single Component Failure
- Single instance unhealthy
- Individual health check failing
- Minor replication delays

### Incident Response Procedures

#### P0: Primary Region Complete Outage

**Immediate Actions (0-5 minutes):**
```bash
# 1. Confirm primary region outage
make check-health REGION=us-east-1

# 2. Check AWS Service Health Dashboard
# https://health.aws.amazon.com/health/status

# 3. Verify secondary region is healthy
make check-health REGION=us-west-2

# 4. Check if automatic failover occurred
dig @8.8.8.8 example.com +short
aws route53 get-health-check-status --health-check-id $PRIMARY_HEALTH_CHECK_ID

# 5. If automatic failover didn't occur, initiate manual failover
# (See Failover Operations section above)
```

**Execute Failover (5-15 minutes):**
```bash
# See detailed failover procedure in "Manual Failover to Secondary Region" section

# Quick failover checklist:
# 1. Promote RDS read replica
aws rds promote-read-replica \
  --db-instance-identifier secondary-db-replica \
  --region us-west-2

# 2. Scale up secondary Auto Scaling
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name secondary-asg \
  --desired-capacity 3 \
  --region us-west-2

# 3. Force DNS failover (if not automatic)
aws route53 update-health-check \
  --health-check-id $PRIMARY_HEALTH_CHECK_ID \
  --disabled

# 4. Verify application is serving from secondary
curl https://example.com/health
watch -n 5 'dig @8.8.8.8 example.com +short'
```

**Post-Failover Monitoring (15+ minutes):**
```bash
# Monitor secondary region metrics
watch -n 30 'aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --dimensions Name=LoadBalancer,Value=<secondary-alb> \
  --start-time $(date -u -d "10 minutes ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average \
  --region us-west-2'

# Check error rates
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name HTTPCode_Target_5XX_Count \
  --dimensions Name=LoadBalancer,Value=<secondary-alb> \
  --start-time $(date -u -d "15 minutes ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum \
  --region us-west-2

# Monitor database performance
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=secondary-db-replica \
  --start-time $(date -u -d "15 minutes ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average \
  --region us-west-2
```

#### P1: High Replication Lag

**Investigation:**
```bash
# 1. Check current replication lag
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=secondary-db-replica \
  --start-time $(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average,Maximum \
  --region us-west-2

# 2. Check primary database load
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=primary-db \
  --start-time $(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average \
  --region us-east-1

# 3. Check network performance
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name NetworkTransmitThroughput \
  --dimensions Name=DBInstanceIdentifier,Value=primary-db \
  --start-time $(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average \
  --region us-east-1

# 4. Check for long-running transactions
# Connect to primary DB and run:
# SELECT * FROM pg_stat_activity WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';
```

**Mitigation:**
```bash
# Option 1: Scale up RDS instance (if CPU/memory constrained)
aws rds modify-db-instance \
  --db-instance-identifier primary-db \
  --db-instance-class db.t3.large \
  --apply-immediately \
  --region us-east-1

# Option 2: Optimize queries (review slow query log)
# Download slow query log from RDS console

# Option 3: Increase network bandwidth
# Contact AWS Support to check for network issues

# Option 4: Temporary: Accept higher RPO
# Monitor but don't failover unless lag > 30 minutes

# Verify improvement
watch -n 60 'aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=secondary-db-replica \
  --start-time $(date -u -d "5 minutes ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average \
  --region us-west-2 \
  --query "Datapoints[0].Average"'
```

#### P2: Route 53 Health Check Failures

**Investigation:**
```bash
# 1. Get health check details
aws route53 get-health-check-status \
  --health-check-id $HEALTH_CHECK_ID

# 2. Test endpoint directly
ENDPOINT=$(aws route53 get-health-check \
  --health-check-id $HEALTH_CHECK_ID \
  --query 'HealthCheck.HealthCheckConfig.FullyQualifiedDomainName' \
  --output text)

curl -v https://${ENDPOINT}/health

# 3. Check from multiple locations
for resolver in 8.8.8.8 1.1.1.1 208.67.222.222; do
  echo "Testing from $resolver:"
  dig @$resolver $ENDPOINT +short
done

# 4. Check ALB health
aws elbv2 describe-target-health \
  --target-group-arn $TARGET_GROUP_ARN \
  --region us-east-1
```

**Common Causes & Fixes:**

**SSL Certificate Expired:**
```bash
# Check certificate
echo | openssl s_client -connect ${ENDPOINT}:443 2>/dev/null | \
  openssl x509 -noout -dates

# Renew certificate (if using ACM)
aws acm request-certificate \
  --domain-name example.com \
  --validation-method DNS

# Update ALB with new certificate
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --certificates CertificateArn=arn:aws:acm:... \
  --region us-east-1
```

**Health Check Path Wrong:**
```bash
# Update health check path
aws route53 update-health-check \
  --health-check-id $HEALTH_CHECK_ID \
  --resource-path /health

# Verify
curl https://${ENDPOINT}/health
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Multi-Region Failover Incident

**Date:** $(date)
**Severity:** P0
**Duration:** 15 minutes
**Affected Regions:** us-east-1 (primary)

## Timeline
- 14:00: Primary region health checks started failing
- 14:02: Confirmed AWS service outage in us-east-1
- 14:05: Initiated failover to us-west-2
- 14:10: RDS read replica promoted
- 14:12: Auto Scaling scaled up in secondary
- 14:15: Traffic fully shifted to secondary region

## Root Cause
AWS infrastructure issue in us-east-1 availability zones

## Impact
- No user-facing impact (automatic failover worked)
- RPO: 30 seconds (replication lag at time of failover)
- RTO: 15 minutes (actual failover time)

## Action Items
- [x] Failover executed successfully
- [ ] Review and optimize failover automation
- [ ] Update runbook based on lessons learned
- [ ] Conduct failback when primary region restored

EOF

# Update metrics
cat > metrics/failover-$(date +%Y%m%d).json << EOF
{
  "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "event": "region_failover",
  "source_region": "us-east-1",
  "target_region": "us-west-2",
  "rto_minutes": 15,
  "rpo_seconds": 30,
  "automatic": false
}
EOF
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Regional Health Checks
```bash
# Test primary region
make check-health REGION=us-east-1

# Test secondary region
make check-health REGION=us-west-2

# Check both regions
for region in us-east-1 us-west-2; do
  echo "=== $region ==="
  aws elbv2 describe-target-health \
    --target-group-arn $(aws elbv2 describe-target-groups \
      --region $region \
      --query 'TargetGroups[0].TargetGroupArn' \
      --output text) \
    --region $region \
    --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]' \
    --output table
done
```

#### DNS Troubleshooting
```bash
# Check current DNS resolution
dig example.com +short

# Check from multiple DNS servers
for dns in 8.8.8.8 1.1.1.1 208.67.222.222; do
  echo "From $dns:"
  dig @$dns example.com +short
done

# Trace DNS query
dig example.com +trace

# Check TTL
dig example.com | grep -E "^example.com"

# Check all record types
dig example.com ANY
```

#### Cross-Region Network Testing
```bash
# Test connectivity from primary to secondary
# SSH to instance in us-east-1
ping -c 5 <secondary-instance-ip>
traceroute <secondary-instance-ip>

# Test RDS connectivity cross-region
# From primary region instance:
mysql -h <secondary-rds-endpoint> -u admin -p

# Check VPC peering (if configured)
aws ec2 describe-vpc-peering-connections \
  --filters "Name=status-code,Values=active"
```

### Common Issues & Solutions

#### Issue: Automatic failover not triggering

**Symptoms:**
- Primary region down
- Route 53 still pointing to primary
- Health checks show failure but no failover

**Diagnosis:**
```bash
# Check health check configuration
aws route53 get-health-check --health-check-id $PRIMARY_HEALTH_CHECK_ID

# Check DNS record configuration
aws route53 list-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --query "ResourceRecordSets[?Name=='example.com.']"

# Verify health check is associated with DNS record
# Check for "HealthCheckId" in failover record
```

**Solution:**
```bash
# Ensure health check ID is associated with primary DNS record
cat > update-record.json << 'EOF'
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "example.com",
      "Type": "A",
      "SetIdentifier": "Primary",
      "Failover": "PRIMARY",
      "TTL": 60,
      "ResourceRecords": [{"Value": "<primary-ip>"}],
      "HealthCheckId": "<health-check-id>"
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://update-record.json

# Verify failover configuration
aws route53 test-dns-answer \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --record-name example.com \
  --record-type A
```

---

#### Issue: RDS read replica out of sync

**Symptoms:**
- Replication lag > 5 minutes
- Secondary database missing recent data

**Diagnosis:**
```bash
# Check replication status
aws rds describe-db-instances \
  --db-instance-identifier secondary-db-replica \
  --region us-west-2 \
  --query 'DBInstances[0].[DBInstanceStatus,ReadReplicaSourceDBInstanceIdentifier]'

# Check lag metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=secondary-db-replica \
  --start-time $(date -u -d '2 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum \
  --region us-west-2

# Check for replication errors
aws rds describe-events \
  --source-identifier secondary-db-replica \
  --source-type db-instance \
  --region us-west-2
```

**Solution:**
```bash
# Option 1: Wait for replication to catch up
# Monitor lag until acceptable

# Option 2: Increase replica instance size
aws rds modify-db-instance \
  --db-instance-identifier secondary-db-replica \
  --db-instance-class db.t3.large \
  --apply-immediately \
  --region us-west-2

# Option 3: Recreate replica if severely out of sync
# Caution: This increases RPO temporarily

# Delete old replica
aws rds delete-db-instance \
  --db-instance-identifier secondary-db-replica \
  --skip-final-snapshot \
  --region us-west-2

# Create new replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier secondary-db-replica \
  --source-db-instance-identifier arn:aws:rds:us-east-1:$ACCOUNT_ID:db:primary-db \
  --db-instance-class db.t3.medium \
  --region us-west-2
```

---

## Disaster Recovery & Backups

### RPO/RTO Targets

- **RPO** (Recovery Point Objective): < 5 minutes
  - RDS cross-region replication lag target
  - S3 cross-region replication SLA

- **RTO** (Recovery Time Objective): < 15 minutes
  - Time from detection to full failover
  - Includes RDS promotion, Auto Scaling, DNS propagation

### DR Drill Procedure

**Monthly DR Drill (60-90 minutes):**
```bash
# Schedule: First Saturday of month, 9:00 AM ET

# 1. Pre-drill checklist
cat > dr-drill-checklist-$(date +%Y%m%d).md << 'EOF'
# DR Drill Checklist

Date: $(date)
Participants: [List team members]

## Pre-Drill
- [ ] Notify stakeholders of drill
- [ ] Verify secondary region healthy
- [ ] Check RDS replication lag < 1 minute
- [ ] Backup current Route 53 configuration
- [ ] Document current state

## Execution
- [ ] Execute failover to secondary
- [ ] Verify DNS propagation
- [ ] Test application functionality
- [ ] Monitor metrics for anomalies
- [ ] Document issues encountered

## Failback
- [ ] Execute failback to primary
- [ ] Verify primary region serving traffic
- [ ] Re-establish replication
- [ ] Verify all systems normal

## Post-Drill
- [ ] Document RTO/RPO achieved
- [ ] Identify improvements needed
- [ ] Update runbook
- [ ] Schedule follow-up for action items

EOF

# 2. Execute controlled failover
make simulate-outage

# 3. Time the failover process
START_TIME=$(date +%s)

# Execute failover (see Failover Operations section)
# ... failover steps ...

END_TIME=$(date +%s)
ACTUAL_RTO=$((END_TIME - START_TIME))
echo "Achieved RTO: $ACTUAL_RTO seconds"

# 4. Test application in secondary region
curl https://example.com/health
# Run automated tests
make test-prod ENDPOINT=https://example.com

# 5. Execute failback
# (See Failback Operations section)

# 6. Document results
cat >> dr-drill-checklist-$(date +%Y%m%d).md << EOF

## Results
- **Achieved RTO:** ${ACTUAL_RTO} seconds (target: 900 seconds)
- **Achieved RPO:** Measured replication lag at failover time
- **Issues encountered:** [List any issues]
- **Action items:** [List improvements]

EOF
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Check health of both regions
for region in us-east-1 us-west-2; do
  echo "=== Health check: $region ==="
  make check-health REGION=$region
done

# Monitor replication lag
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=secondary-db-replica \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum \
  --region us-west-2

# Verify Route 53 health checks
aws route53 get-health-check-status --health-check-id $PRIMARY_HEALTH_CHECK_ID
aws route53 get-health-check-status --health-check-id $SECONDARY_HEALTH_CHECK_ID
```

#### Weekly Tasks
```bash
# Review CloudWatch alarms
aws cloudwatch describe-alarms \
  --state-value ALARM \
  --region us-east-1

# Check S3 replication metrics
aws s3api get-bucket-replication \
  --bucket primary-bucket \
  --region us-east-1

# Review RDS snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier primary-db \
  --region us-east-1 | \
  jq '.DBSnapshots | sort_by(.SnapshotCreateTime) | reverse | .[0:5]'

# Test failover capability (non-production)
make test-failover
```

#### Monthly Tasks
```bash
# Conduct full DR drill
# (See DR Drill Procedure above)

# Review and update CloudFormation templates
git pull origin main
git diff HEAD~1 templates/

# Rotate credentials
# Update RDS passwords, API keys, etc.

# Review costs across regions
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '1 month ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=REGION
```

---

## Quick Reference

### Common Commands
```bash
# Check health
make check-health

# Deploy to regions
make deploy-primary
make deploy-secondary

# Test failover
make test-failover

# Simulate outage (drill)
make simulate-outage

# Check replication lag
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=secondary-db-replica \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average \
  --region us-west-2
```

### Emergency Response
```bash
# P0: Execute immediate failover
aws rds promote-read-replica \
  --db-instance-identifier secondary-db-replica \
  --region us-west-2

aws autoscaling set-desired-capacity \
  --auto-scaling-group-name secondary-asg \
  --desired-capacity 3 \
  --region us-west-2

aws route53 update-health-check \
  --health-check-id $PRIMARY_HEALTH_CHECK_ID \
  --disabled

# P1: Check health and prepare for failover
make check-health REGION=us-east-1
make check-health REGION=us-west-2

# P2: Fix secondary region issues
# See specific troubleshooting sections
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Infrastructure Engineering Team / SRE Team
- **Review Schedule:** Quarterly or after DR drills/actual failover events
- **Feedback:** Create issue or submit PR with updates
