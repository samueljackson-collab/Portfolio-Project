# Runbook: Disaster Recovery

## Overview

**Severity**: P0
**Recovery Time Objective (RTO)**: 15 minutes
**Recovery Point Objective (RPO)**: 5 minutes
**Related ADRs**: [ADR-008: Deployment Strategy](../adr/README.md) (planned), [ADR-009: Disaster Recovery](../adr/README.md) (planned)

## Disaster Scenarios

1. **Complete Region Failure**: Primary AWS region (us-east-1) unavailable
2. **Database Corruption**: Data integrity compromised
3. **Security Breach**: Complete system compromise requiring rebuild
4. **Data Center Outage**: Physical infrastructure failure
5. **Critical Service Degradation**: Unrecoverable application state

## Pre-Requisites

Before executing DR procedures, verify:

```bash
# Check DR infrastructure health
kubectl --context=dr-cluster get nodes
kubectl --context=dr-cluster get pods -n production

# Verify database replication
aws rds describe-db-instances \
  --db-instance-identifier portfolio-dr-replica \
  --region us-west-2

# Check backup status
aws rds describe-db-snapshots \
  --db-instance-identifier portfolio-prod \
  --query 'DBSnapshots[0]' \
  --region us-east-1

# Verify DNS configuration
dig api.example.com +short
```

## Region Failover Procedure

### Automated Failover Script

```bash
#!/bin/bash
# dr-failover.sh - Execute region failover

set -e

PRIMARY_REGION="us-east-1"
DR_REGION="us-west-2"
HOSTED_ZONE_ID="Z1234567890ABC"
DOMAIN="api.example.com"

echo "======================================"
echo "DISASTER RECOVERY FAILOVER"
echo "======================================"
echo "Primary Region: $PRIMARY_REGION"
echo "DR Region: $DR_REGION"
echo ""
read -p "Are you sure you want to proceed? (type YES): " confirm

if [ "$confirm" != "YES" ]; then
  echo "Failover cancelled"
  exit 1
fi

# Step 1: Update DNS to point to DR region
echo "Step 1: Updating Route53 DNS..."
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "'$DOMAIN'",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z0987654321XYZ",
          "DNSName": "dr-lb.'$DR_REGION'.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'

# Step 2: Promote RDS read replica to master
echo "Step 2: Promoting read replica to master..."
aws rds promote-read-replica \
  --db-instance-identifier portfolio-dr-replica \
  --region $DR_REGION

# Wait for promotion
echo "Waiting for database promotion..."
aws rds wait db-instance-available \
  --db-instance-identifier portfolio-dr-replica \
  --region $DR_REGION

# Step 3: Update application configuration
echo "Step 3: Updating application configuration..."
kubectl config use-context dr-cluster

DB_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier portfolio-dr-replica \
  --region $DR_REGION \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

kubectl set env deployment/app -n production \
  DATABASE_URL="postgres://user:pass@$DB_ENDPOINT:5432/portfolio" \
  AWS_REGION=$DR_REGION

# Step 4: Scale up DR environment
echo "Step 4: Scaling up DR environment..."
kubectl scale deployment/app -n production --replicas=10

# Step 5: Verify health
echo "Step 5: Verifying application health..."
for i in {1..30}; do
  status=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health)
  if [ "$status" = "200" ]; then
    echo "✓ Application healthy in DR region"
    break
  fi
  echo "Waiting for application... ($i/30)"
  sleep 2
done

# Step 6: Enable monitoring
echo "Step 6: Enabling monitoring..."
kubectl apply -f monitoring/dr-alerts.yaml -n production

# Step 7: Send notifications
echo "Step 7: Sending notifications..."
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#incidents",
    "text": "🚨 DR FAILOVER COMPLETE\nRegion: '${DR_REGION}'\nStatus: ACTIVE\nTime: '$(date)'"
  }'

echo ""
echo "======================================"
echo "FAILOVER COMPLETE"
echo "======================================"
echo "Primary Region: $DR_REGION (DR)"
echo "Status: ACTIVE"
echo ""
echo "Next Steps:"
echo "1. Monitor application metrics"
echo "2. Investigate primary region failure"
echo "3. Plan failback when primary restored"
echo "4. Update status page"
```

### Manual Failover Steps

If automation fails, execute manually:

#### 1. DNS Failover (1 minute)

```bash
# Update Route53 to DR region
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://dr-dns-update.json

# Verify DNS propagation
dig api.example.com +short
# Should return DR load balancer IP
```

#### 2. Database Promotion (5 minutes)

```bash
# Promote read replica
aws rds promote-read-replica \
  --db-instance-identifier portfolio-dr-replica \
  --region us-west-2

# Monitor promotion progress
aws rds describe-db-instances \
  --db-instance-identifier portfolio-dr-replica \
  --region us-west-2 \
  --query 'DBInstances[0].DBInstanceStatus'

# Wait until status is "available"
```

#### 3. Application Configuration (2 minutes)

```bash
# Switch to DR cluster
kubectl config use-context dr-cluster

# Update database connection
kubectl set env deployment/app -n production \
  DATABASE_URL="postgres://user:pass@dr-db.us-west-2.rds.amazonaws.com:5432/portfolio"

# Restart pods
kubectl rollout restart deployment/app -n production
```

#### 4. Scale Resources (1 minute)

```bash
# Scale to production capacity
kubectl scale deployment/app -n production --replicas=10

# Enable autoscaling
kubectl autoscale deployment/app -n production \
  --cpu-percent=70 \
  --min=10 \
  --max=30
```

#### 5. Verify Services (3 minutes)

```bash
# Check pod status
kubectl get pods -n production

# Test health endpoint
curl https://api.example.com/health

# Run smoke tests
npm run test:smoke -- --env=dr

# Monitor error rates
curl "http://prometheus:9090/api/v1/query?query=
  rate(http_request_errors_total[5m])"
```

## Database Recovery

### Point-in-Time Recovery

```bash
# Restore to specific timestamp
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier portfolio-prod \
  --target-db-instance-identifier portfolio-restored \
  --restore-time 2024-12-15T10:30:00Z \
  --region us-east-1

# Wait for restoration
aws rds wait db-instance-available \
  --db-instance-identifier portfolio-restored \
  --region us-east-1

# Verify data integrity
psql -h portfolio-restored.xxx.rds.amazonaws.com -U postgres -d portfolio -c "
  SELECT
    COUNT(*) as total_records,
    MAX(created_at) as latest_record
  FROM orders;"
```

### Snapshot Recovery

```bash
# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier portfolio-prod \
  --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime]' \
  --output table

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier portfolio-restored \
  --db-snapshot-identifier portfolio-snapshot-2024-12-15

# Configure restored instance
aws rds modify-db-instance \
  --db-instance-identifier portfolio-restored \
  --db-instance-class db.r5.xlarge \
  --multi-az \
  --apply-immediately
```

## Failback Procedure

Once primary region is restored:

```bash
#!/bin/bash
# dr-failback.sh - Return to primary region

set -e

echo "======================================"
echo "FAILBACK TO PRIMARY REGION"
echo "======================================"

# Step 1: Verify primary region health
echo "Step 1: Verifying primary region..."
kubectl config use-context primary-cluster
kubectl get nodes
kubectl get pods -n production

# Step 2: Sync data from DR to primary
echo "Step 2: Syncing database..."
pg_dump -h dr-db.us-west-2.amazonaws.com -U postgres portfolio | \
  psql -h primary-db.us-east-1.amazonaws.com -U postgres portfolio

# Step 3: Update application in primary
echo "Step 3: Deploying to primary..."
kubectl set env deployment/app -n production \
  DATABASE_URL="postgres://user:pass@primary-db.us-east-1.amazonaws.com:5432/portfolio"

# Step 4: Scale up primary
kubectl scale deployment/app -n production --replicas=10

# Step 5: Update DNS to primary
echo "Step 5: Updating DNS..."
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.example.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z1234567890ABC",
          "DNSName": "primary-lb.us-east-1.elb.amazonaws.com"
        }
      }
    }]
  }'

# Step 6: Monitor primary
echo "Step 6: Monitoring primary region..."
for i in {1..30}; do
  status=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/health)
  if [ "$status" = "200" ]; then
    echo "✓ Primary region healthy"
    break
  fi
  sleep 2
done

# Step 7: Scale down DR (keep warm standby)
kubectl config use-context dr-cluster
kubectl scale deployment/app -n production --replicas=2

echo "======================================"
echo "FAILBACK COMPLETE"
echo "======================================"
```

## Post-Recovery Validation

```bash
# Run comprehensive tests
npm run test:smoke -- --env=production
npm run test:integration -- --env=production

# Verify critical flows
./scripts/verify-critical-paths.sh

# Check data consistency
psql -h primary-db.amazonaws.com -U postgres -d portfolio <<EOF
  SELECT
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM orders) as orders,
    (SELECT COUNT(*) FROM products) as products;
EOF

# Monitor for 1 hour
watch -n 60 'kubectl top pods -n production'
```

## DR Testing Schedule

- **Monthly**: DNS failover drill
- **Quarterly**: Full DR failover exercise
- **Annually**: Complete disaster simulation with all teams

## Communication Templates

### Initial Notification

```
🚨 DISASTER RECOVERY INITIATED

Event: [Description]
Primary Region: us-east-1
DR Region: us-west-2

Status: Failover in progress
ETA: 15 minutes

War Room: [Zoom link]
Incident Commander: @[name]
```

### Completion Notification

```
✅ DISASTER RECOVERY COMPLETE

Failover Duration: [X] minutes
Current Region: us-west-2 (DR)
Status: OPERATIONAL

All services restored and operational.

Next Steps:
- Monitor for issues
- Investigate root cause
- Plan failback to primary

Postmortem: [link]
```

## Related Runbooks

- [Incident Response Framework](./incident-response-framework.md)
- [Security Incident Response](./runbook-security-incident-response.md)

## Additional Resources

- [AWS Disaster Recovery](https://aws.amazon.com/disaster-recovery/)
- [RDS Backup and Restore](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_CommonTasks.BackupRestore.html)

---

**Last Updated**: December 2024
**Last Tested**: December 2024
**Next Test**: March 2025
