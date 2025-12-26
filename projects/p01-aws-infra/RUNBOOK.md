# Runbook — P01 (AWS Infrastructure Automation)

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Stack deployment success rate** | 99% | CloudFormation API success responses |
| **RDS availability** | 99.95% (Multi-AZ) | CloudWatch `DatabaseConnections` > 0 |
| **DR failover time (RTO)** | < 2 minutes | Time from failover initiate → RDS available |
| **Drift detection latency** | < 5 minutes | AWS Config rule evaluation time |

## Dashboards & Alerts

### Dashboards
- **CloudFormation Operations**: [CloudWatch Dashboard](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=InfraOps)
  - Stack creation/update success/failure rates
  - Drift detection findings
  - IAM policy changes

- **RDS Health**: [RDS Dashboard](https://console.aws.amazon.com/rds/home?region=us-east-1)
  - CPU utilization, Free storage, DB connections
  - Multi-AZ failover events

### Alerts (via SNS → PagerDuty)
- **P0**: RDS instance down, Stack rollback failure
- **P1**: High CPU (>80% for 5 min), Storage < 10%
- **P2**: Drift detected, Failed drift remediation

## Standard Operations

### Start/Stop RDS (Non-Prod Only)
```bash
# Stop RDS instance (saves costs in dev/stage)
aws rds stop-db-instance --db-instance-identifier mydb-dev

# Start RDS instance
aws rds start-db-instance --db-instance-identifier mydb-dev
```

### Deploy Stack
```bash
# Development
make deploy-dev STACK_NAME=my-infra-dev

# Staging
make deploy-stage STACK_NAME=my-infra-stage

# Production (requires approval)
make deploy-prod STACK_NAME=my-infra-prod
```

### Update Stack
```bash
# Update with change set (safe preview)
make changeset STACK_NAME=my-infra-dev TEMPLATE=infra/vpc-rds.yaml

# Execute change set after review
aws cloudformation execute-change-set --change-set-name <name> --stack-name my-infra-dev
```

## Incident Response

### Detect
- **PagerDuty alert** → Acknowledge within 5 minutes
- **Slack #incidents** → Create incident thread
- Check:
  - CloudFormation events: `aws cloudformation describe-stack-events --stack-name <name>`
  - RDS status: `aws rds describe-db-instances --db-instance-identifier <id>`

### Triage
1. **Assess impact**: How many services affected? Production or non-prod?
2. **Severity classification**:
   - **P0**: Production outage (RDS down, stack DELETE_FAILED)
   - **P1**: Degraded performance (RDS CPU >90%, deployment failures)
   - **P2**: Non-critical (drift detected, cost anomaly)
3. **Escalate if needed**: P0 → page SRE lead + platform team

### Mitigate
#### RDS Down
```bash
# Check RDS events
aws rds describe-events --source-identifier <db-id> --duration 60

# Force Multi-AZ failover if primary unhealthy
./scripts/dr-drill.sh failover --db-instance-id <db-id>

# Monitor failover progress
watch -n 5 'aws rds describe-db-instances --db-instance-identifier <db-id> --query "DBInstances[0].DBInstanceStatus"'
```

#### Stack Rollback Failure
```bash
# Attempt to continue rollback
aws cloudformation continue-update-rollback --stack-name <name>

# If stuck, manually delete failed resources, then retry
aws cloudformation delete-stack --stack-name <name>
```

### Root Cause
After mitigation:
1. Collect logs: CloudFormation events, CloudTrail API calls, RDS logs
2. Timeline reconstruction: When did drift occur? What triggered failure?
3. Identify root cause: Configuration error? AWS service issue? Automation bug?

### Postmortem Template
See [`docs/postmortem-template.md`](./docs/postmortem-template.md):
- **Incident summary**
- **Timeline** (detection → mitigation → resolution)
- **Root cause**
- **Action items** (prevent recurrence)

## DR & Backups

### RPO/RTO
- **RPO** (Recovery Point Objective): 5 minutes (automated RDS snapshots)
- **RTO** (Recovery Time Objective): 2 minutes (Multi-AZ automatic failover)

### Backup Strategy
- **Automated snapshots**: Daily at 03:00 UTC, retained 7 days
- **Manual snapshots**: Before major changes (pre-deployment)
- **Backup verification**: Monthly restore test in non-prod

### DR Drill Steps
Run monthly (first Friday, 9:00 AM ET):

```bash
# 1. Report current DB target
./scripts/dr-drill.sh report

# 2. Announce in Slack #infrastructure
# "DR drill starting: forcing Multi-AZ failover for <db-id>"

# 3. Execute failover
./scripts/dr-drill.sh failover --db-instance-id <db-id>

# 4. Monitor RDS events
aws rds describe-events --source-identifier <db-id> --duration 10

# 5. Verify application connectivity
curl -f https://api.example.com/healthz || echo "Health check failed"

# 6. Document results in Confluence/Wiki
# - Failover duration, application downtime, issues encountered
```

### Restore from Snapshot
```bash
# List available snapshots
aws rds describe-db-snapshots --db-instance-identifier <db-id>

# Restore to new instance
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier restored-db \
  --db-snapshot-identifier <snapshot-id>
```

## Evidence & Verification

Verification summary: Baseline evidence captured to validate the latest quickstart configuration and document supporting artifacts for audits.

**Evidence artifacts**
- [Screenshot](./docs/evidence/screenshot.svg)
- [Run log](./docs/evidence/run-log.txt)
- [Dashboard export](./docs/evidence/dashboard-export.json)
- [Load test summary](./docs/evidence/load-test-summary.txt)

### Evidence Checklist

| Evidence Item | Location | Status |
| --- | --- | --- |
| Screenshot captured | `docs/evidence/screenshot.svg` | ✅ |
| Run log captured | `docs/evidence/run-log.txt` | ✅ |
| Dashboard export captured | `docs/evidence/dashboard-export.json` | ✅ |
| Load test summary captured | `docs/evidence/load-test-summary.txt` | ✅ |
