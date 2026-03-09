# Report Templates

## Workflow Execution Report
**Generated:** Weekly (Monday 9am UTC)
**Audience:** Data Engineering, Operations

**Metrics:**
- Total workflows executed: [count]
- Success rate: [percentage]
- Average execution duration: [seconds]
- P95 execution duration: [seconds]
- Failed workflows (by error type):
  - Validation errors: [count]
  - Transformation errors: [count]
  - Throttling errors: [count]
  - Timeout errors: [count]
- DLQ message count: [count]
- Files processed: [count]
- Data volume processed: [GB]

**Top 5 Longest Executions:**
| Execution ID | Duration | File Size | Error? |
|--------------|----------|-----------|--------|
| exec-001     | 45s      | 500MB     | No     |

**Actions:**
- [ ] Review DLQ messages (if >10)
- [ ] Investigate P95 duration increase (if >baseline +20%)
- [ ] Optimize slow transformations (if >30s average)

---

## Weekly Operations Report
**Generated:** Weekly (Friday 5pm UTC)
**Audience:** Engineering Manager, SRE

**Availability:**
- Uptime: [percentage] (target: 99.9%)
- Incidents: [count]
  - P1 (service down): [count]
  - P2 (degraded): [count]

**Performance:**
- Lambda cold start rate: [percentage]
- DynamoDB throttling events: [count]
- S3 5xx errors: [count]

**Cost:**
- Total spend: $[amount]
  - Lambda: $[amount] ([percentage])
  - Step Functions: $[amount] ([percentage])
  - S3: $[amount] ([percentage])
  - DynamoDB: $[amount] ([percentage])
- Variance from budget: [+/- percentage]

**Security:**
- CloudTrail events reviewed: [count]
- IAM policy changes: [count]
- KMS key usage: [count encryptions/decryptions]
- Failed auth attempts: [count]

**Operational Debt:**
- DLQ messages pending review: [count]
- CloudWatch Logs retention overdue: [count log groups]
- Outdated Lambda runtimes: [count functions]

**Action Items:**
- [ ] Address cost variance if >10%
- [ ] Update Lambda runtimes (Python 3.8 EOL)
- [ ] Review and clear DLQ backlog

---

## Change/Release Report
**Generated:** Per deployment
**Audience:** Change Advisory Board, Stakeholders

**Deployment Details:**
- Date/Time: [ISO timestamp]
- Deployer: [name/email]
- Deployment Method: SAM deploy / GitHub Actions
- Environment: dev / staging / prod
- Git Commit: [SHA]

**Changes:**
- Lambda functions updated: [list]
- Step Functions definition changed: [yes/no]
- IAM policies modified: [yes/no]
- DynamoDB schema changed: [yes/no]
- New dependencies: [list]

**Testing:**
- Unit tests: [pass/fail] ([count] tests)
- Integration tests: [pass/fail]
- Smoke tests post-deploy: [pass/fail]

**Rollback Plan:**
- Previous version: [commit SHA or version tag]
- Rollback command: `sam deploy --template-file .aws-sam/build/template.yaml --config-file samconfig-rollback.toml`
- Estimated rollback time: <5 minutes

**Monitoring:**
- CloudWatch dashboard: [URL]
- Alarm status: All green / [count] alarms in ALARM state
- Error rate (first 30 min post-deploy): [percentage]

**Approvals:**
- Code review: [reviewer names]
- Security review: [yes/no - required for IAM/encryption changes]
- Load test: [yes/no - required for compute changes]

---

## Cost Optimization Watch Report
**Generated:** Monthly (1st of month)
**Audience:** FinOps, Engineering

**Cost by Service:**
| Service | Current Month | Last Month | Change | Optimization Opportunities |
|---------|---------------|------------|--------|----------------------------|
| Lambda  | $X            | $Y         | +Z%    | Right-size memory, ARM64   |
| Step Functions | $X     | $Y         | +Z%    | Batch small jobs           |
| DynamoDB | $X           | $Y         | +Z%    | Switch to on-demand        |
| S3      | $X            | $Y         | +Z%    | Intelligent Tiering        |

**Top 10 Costliest Resources:**
1. Lambda function: transform-handler ($X, 5M invocations)
2. DynamoDB table: etl-metadata ($Y, 10M writes)

**Waste Identified:**
- Idle DynamoDB provisioned capacity: $[amount]/month
- S3 objects in Standard tier >30 days: [count], estimated savings $[amount] if Glacier
- Over-provisioned Lambda memory: Functions with <50% memory utilization

**Recommendations:**
1. Migrate DynamoDB to on-demand (save ~$X/month)
2. Enable S3 Intelligent Tiering (save ~$Y/month)
3. Reduce transform-handler memory from 1024MB to 512MB (save ~$Z/month)
4. Implement Step Functions Express Workflows for jobs <5min (save ~$W/month)

**Actions Taken:**
- [x] Enabled S3 lifecycle policy for raw bucket (implemented 2024-11-15)
- [ ] Reduce Lambda memory allocations (pending benchmarking)

**Tracking:**
- Cost allocation tags applied: [percentage of resources]
- Budget alerts configured: [yes/no]
- Current spend vs budget: [percentage]
