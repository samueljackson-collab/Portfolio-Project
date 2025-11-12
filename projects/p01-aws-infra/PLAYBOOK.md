# Playbook — P01 (AWS Infrastructure Automation)

## Plays

---

## Play: Deploy Stack (Dev/Stage/Prod)

### Preconditions
- [ ] Change request approved
- [ ] CloudFormation template validated (`make validate`)
- [ ] Parameters file reviewed (e.g., `params/dev.json`)
- [ ] Rollback plan documented
- [ ] Announcement in Slack #infrastructure (for prod)

### Commands

#### Development
```bash
export AWS_REGION=us-east-1
export STACK_NAME=my-infra-dev
export ENVIRONMENT=dev

# Dry-run (create change set)
make changeset STACK_NAME=$STACK_NAME TEMPLATE=infra/vpc-rds.yaml PARAMS=params/dev.json

# Review change set output, then deploy
make deploy-dev STACK_NAME=$STACK_NAME
```

#### Staging
```bash
export STACK_NAME=my-infra-stage
export ENVIRONMENT=stage

make deploy-stage STACK_NAME=$STACK_NAME
```

#### Production
```bash
export STACK_NAME=my-infra-prod
export ENVIRONMENT=prod

# Requires manual approval (change advisory board)
make deploy-prod STACK_NAME=$STACK_NAME

# Monitor deployment
watch -n 5 'aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].StackStatus"'
```

### Post-Deployment
- [ ] Verify stack status: `aws cloudformation describe-stacks --stack-name <name>`
- [ ] Run smoke tests: `make smoke-test`
- [ ] Check RDS connectivity: `psql -h <rds-endpoint> -U admin -d mydb -c "SELECT 1;"`
- [ ] Update CHANGELOG.md
- [ ] Close change request ticket

---

## Play: Patch & Rotate Secrets

### Steps

#### 1. Generate new DB password
```bash
NEW_PASSWORD=$(openssl rand -base64 32)
```

#### 2. Update Secrets Manager
```bash
aws secretsmanager update-secret \
  --secret-id /myapp/prod/db-password \
  --secret-string "$NEW_PASSWORD"
```

#### 3. Trigger RDS password update
```bash
aws rds modify-db-instance \
  --db-instance-identifier my-db-prod \
  --master-user-password "$NEW_PASSWORD" \
  --apply-immediately
```

#### 4. Verify application connectivity
```bash
# Check app logs for DB connection errors
kubectl logs -n myapp deployment/api --tail=50 | grep -i "database"
```

#### 5. Document rotation
```bash
echo "$(date -u): Rotated DB password for my-db-prod" >> docs/secret-rotation-log.txt
```

---

## Play: Scale-Test / Chaos Drill

### Steps

#### 1. Announce in Slack
```
🔧 Chaos drill starting: forcing RDS Multi-AZ failover (ETA: 2 minutes downtime)
Environment: staging
Time: 2024-MM-DD HH:MM UTC
```

#### 2. Execute failover
```bash
./scripts/dr-drill.sh failover --db-instance-id my-db-stage
```

#### 3. Monitor application metrics
```bash
# Watch API error rate
watch -n 2 'curl -s https://api-stage.example.com/metrics | grep http_requests_total'

# Check RDS status
watch -n 5 'aws rds describe-db-instances --db-instance-identifier my-db-stage --query "DBInstances[0].DBInstanceStatus"'
```

#### 4. Measure recovery time
- **Start time**: When failover initiated
- **End time**: When application health checks pass
- **RTO target**: < 2 minutes

#### 5. Document results
Create entry in `docs/chaos-drills/YYYY-MM-DD-rds-failover.md`:
```markdown
# RDS Multi-AZ Failover Drill — 2024-MM-DD

## Summary
- **Environment**: Staging
- **Start**: 14:00:00 UTC
- **End**: 14:01:45 UTC
- **Actual RTO**: 1m 45s (within target)
- **Issues**: None

## Observations
- Application reconnected automatically
- No manual intervention required
- Monitoring alerts fired correctly
```

---

## Play: Cost Review

### Steps

#### 1. Generate cost report
```bash
# Last 30 days, grouped by service
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  > reports/cost-$(date +%Y-%m).json
```

#### 2. Analyze top spending services
```bash
cat reports/cost-$(date +%Y-%m).json | jq '.ResultsByTime[0].Groups[] | {Service: .Keys[0], Cost: .Metrics.UnblendedCost.Amount}' | sort -k2 -rn | head -10
```

#### 3. Identify optimization opportunities
- **RDS**: Unused instances in dev/stage (stop when not in use)
- **NAT Gateways**: Consolidate to single AZ for non-prod
- **Snapshots**: Delete old manual snapshots (>90 days)

#### 4. Create cost optimization tickets
Example:
```
Title: [Cost] Stop dev RDS instances during weekends
Description: Dev RDS runs 24/7 but only used Mon-Fri 9-5.
Action: Implement Lambda to stop/start on schedule.
Estimated savings: $120/month
```

#### 5. Monthly cost review meeting
- Present top 5 spending services
- Discuss optimization actions taken
- Set cost targets for next month
