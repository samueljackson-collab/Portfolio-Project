# Playbook: Promoting Step Functions Workflow to Production

## Pre-Promotion Checklist
- [ ] **Testing:**
  - [ ] All unit tests passing in CI (pytest, 100% of test suite)
  - [ ] Integration tests validated in staging environment
  - [ ] End-to-end test with production-like data volume (>1000 files)
  - [ ] Performance benchmarks meet SLA (p95 latency <30s per file)
  - [ ] Chaos testing completed (Lambda failures, DynamoDB throttling simulated)
- [ ] **Security:**
  - [ ] IAM policies follow least privilege (reviewed by security team)
  - [ ] KMS encryption enabled for all data at rest (S3, DynamoDB, CloudWatch Logs)
  - [ ] VPC endpoints configured (no public internet routing)
  - [ ] CloudTrail data events enabled for S3 raw/processed buckets
  - [ ] Secrets managed via AWS Secrets Manager (no hardcoded credentials)
- [ ] **Monitoring:**
  - [ ] CloudWatch dashboard created with key metrics (success rate, latency, errors, cost)
  - [ ] Alarms configured with SNS/PagerDuty integration (error rate >5%, DLQ depth >10)
  - [ ] X-Ray tracing enabled for all Lambda functions
  - [ ] Log groups retention set (30 days for debug logs, 365 days for audit logs)
- [ ] **Compliance:**
  - [ ] Data retention policies documented (raw 30d, processed 90d, DynamoDB TTL 180d)
  - [ ] PII handling reviewed (no PII in logs, encryption in transit/rest)
  - [ ] Change management ticket approved (CAB review if production)
- [ ] **Documentation:**
  - [ ] Runbooks updated with new error codes and resolution steps
  - [ ] Architecture diagram reflects current state
  - [ ] Deployment README updated with new prerequisites or config changes

## Promotion Steps

### 1. Code Freeze & Final Validation
```bash
# Ensure working directory is clean
git status

# Pull latest changes from main branch
git pull origin main

# Run full test suite locally
pytest tests/ -v --cov=lambda --cov-report=term-missing

# Validate SAM template
sam validate --template template.yaml --lint
```

### 2. Deploy to Staging (Final Verification)
```bash
# Build Lambda functions and package dependencies
sam build --use-container

# Deploy to staging with production-like config
sam deploy \
  --config-file samconfig-staging.toml \
  --no-confirm-changeset \
  --tags Environment=staging GitCommit=$(git rev-parse HEAD)

# Verify deployment
aws stepfunctions list-state-machines \
  --query "stateMachines[?name=='etl-workflow-staging'].stateMachineArn" \
  --output text

# Run smoke tests (upload 10 test files)
./scripts/smoke-test.sh staging
```

### 3. Manual Gate: Review Staging Results
- Open CloudWatch dashboard: `https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=etl-staging`
- Verify:
  - ✅ All smoke test files processed successfully
  - ✅ No errors in Lambda logs (CloudWatch Logs Insights query: `fields @timestamp, @message | filter @message like /ERROR/`)
  - ✅ DynamoDB items created with correct schema
  - ✅ Processed files exist in S3 with expected partitioning

### 4. Production Deployment (Blue/Green Strategy)
```bash
# Create new version of Step Functions workflow (keep old version for rollback)
sam build --use-container

# Deploy to production with blue/green approach
# New workflow gets "-v2" suffix; old workflow remains active
sam deploy \
  --config-file samconfig-prod.toml \
  --parameter-overrides WorkflowSuffix=-v2 \
  --tags Environment=production GitCommit=$(git rev-parse HEAD) Deployer=$(whoami) \
  --no-confirm-changeset

# Verify new workflow deployed
aws stepfunctions describe-state-machine \
  --state-machine-arn arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:etl-workflow-v2
```

### 5. Canary Deployment (Route 10% Traffic)
```bash
# Update EventBridge rule to send 10% of S3 events to new workflow
aws events put-rule \
  --name etl-s3-events-canary \
  --event-pattern '{"source":["aws.s3"],"detail-type":["Object Created"],"detail":{"bucket":{"name":["raw-data-bucket"]}}}' \
  --state ENABLED

aws events put-targets \
  --rule etl-s3-events-canary \
  --targets Id=1,Arn=arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:etl-workflow-v2,RoleArn=ROLE_ARN,Input='{"canary": true, "percentage": 10}'

# Monitor canary for 30 minutes
# Watch for errors, latency spikes, cost anomalies
```

### 6. Monitor Canary Metrics (30-Minute Bake Time)
```bash
# CloudWatch Insights query for v2 error rate
aws logs start-query \
  --log-group-name /aws/lambda/transform-handler \
  --start-time $(date -u -d '30 minutes ago' +%s) \
  --end-time $(date -u +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ and workflowVersion = "v2" | stats count() as ErrorCount'

# Compare v2 vs v1 metrics
# Decision criteria:
# - v2 error rate < v1 error rate + 2%
# - v2 p95 latency < v1 p95 latency + 10%
# - No critical alarms fired
```

### 7. Full Traffic Cutover (If Canary Successful)
```bash
# Update EventBridge rule to route 100% traffic to v2
aws events put-targets \
  --rule etl-s3-events-main \
  --targets Id=1,Arn=arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:etl-workflow-v2,RoleArn=ROLE_ARN

# Disable v1 workflow (keep for emergency rollback)
aws stepfunctions tag-resource \
  --resource-arn arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:etl-workflow \
  --tags Key=Status,Value=Deprecated

# Monitor for 2 hours post-cutover
# Watch: CloudWatch dashboard, PagerDuty, Slack alerts
```

### 8. Post-Deployment Verification
```bash
# Verify 100% traffic on v2
aws cloudwatch get-metric-statistics \
  --namespace AWS/States \
  --metric-name ExecutionsStarted \
  --dimensions Name=StateMachineArn,Value=arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:etl-workflow-v2 \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --period 300 \
  --statistics Sum

# Check for DLQ buildup (should be <10 messages)
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/ACCOUNT_ID/etl-dlq \
  --attribute-names ApproximateNumberOfMessages

# Verify cost within budget (first 24 hours)
# Open AWS Cost Explorer, filter by tag:WorkflowVersion=v2
```

## Rollback Procedure
**Trigger Conditions:**
- Error rate >10% sustained for 10 minutes
- Critical alarm fires (DynamoDB throttling, Lambda timeouts)
- Data integrity issue detected (incorrect transformations)
- P1 incident declared

**Rollback Steps:**
```bash
# Immediate: Redirect traffic back to v1 workflow
aws events put-targets \
  --rule etl-s3-events-main \
  --targets Id=1,Arn=arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:etl-workflow,RoleArn=ROLE_ARN

# Verify v1 receiving traffic (check CloudWatch metrics)
# Investigate v2 issues in parallel (do not block rollback)

# Preserve v2 logs for forensics
aws logs create-export-task \
  --log-group-name /aws/lambda/transform-handler \
  --from $(date -u -d '2 hours ago' +%s)000 \
  --to $(date -u +%s)000 \
  --destination etl-incident-logs-bucket \
  --destination-prefix rollback-$(date +%Y%m%d-%H%M%S)

# Post-mortem: Schedule incident review within 48 hours
```

## Communication Plan
- **T-24 hours:** Email stakeholders (data consumers, downstream teams) with maintenance window
- **T-0 (deployment start):** Post in #data-engineering Slack: "Production deployment in progress, ETA 60 minutes"
- **T+30 min (post-cutover):** Update Slack with status: "Deployment complete, monitoring canary"
- **T+2 hours:** Final update: "Deployment successful, v2 stable" OR "Rolled back to v1, investigating"
- **T+24 hours:** Send deployment summary report (metrics, issues, learnings)

## Success Criteria
- [ ] Zero P1 incidents in first 48 hours
- [ ] Error rate <1% sustained over 7 days
- [ ] P95 latency remains within 10% of baseline
- [ ] Cost variance <5% from forecast
- [ ] No customer complaints related to data quality/timeliness
