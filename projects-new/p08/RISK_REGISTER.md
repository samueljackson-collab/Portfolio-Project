# Risk Register

## Risk Assessment Scale
- **Likelihood:** 1=Rare (<5%), 2=Unlikely (5-25%), 3=Possible (25-50%), 4=Likely (50-75%), 5=Almost Certain (>75%)
- **Impact:** 1=Negligible, 2=Minor, 3=Moderate, 4=Major, 5=Severe
- **Risk Score:** Likelihood × Impact (1-6=Low, 7-15=Medium, 16-25=High)

---

## Operational Risks

### RISK-001: Lambda Concurrent Execution Limit Exceeded
**Category:** Operational - Availability
**Description:** Traffic spike causes Lambda invocations to exceed account-level concurrency limit (default 1000), resulting in throttling and failed Step Functions executions.

**Likelihood:** 3 (Possible - observed during Black Friday-like events)
**Impact:** 4 (Major - data processing SLA breach, customer impact)
**Risk Score:** 12 (Medium)

**Mitigation:**
- [x] Request AWS Support to increase account limit from 1000 to 5000
- [x] Set reserved concurrency per Lambda function (ingest:200, validate:150, transform:300, output:200)
- [x] CloudWatch alarm triggers at 80% of concurrency limit
- [x] DLQ captures dropped events for replay
- [ ] Implement SQS queue buffer for traffic smoothing (backlog tolerance: 1 hour)

**Owner:** Data Engineering Lead
**Review Date:** 2025-01-15
**Status:** Mitigated (controls in place, residual risk: Low score 6)

---

### RISK-002: DynamoDB TTL Deletion Causing Query Failures
**Category:** Operational - Data Integrity
**Description:** DynamoDB TTL expires metadata items after 180 days, but downstream reports/dashboards query historical metadata, resulting in incomplete audit trail and compliance gaps.

**Likelihood:** 4 (Likely - TTL enabled, deletions automated)
**Impact:** 3 (Moderate - reporting gaps, potential compliance violation)
**Risk Score:** 12 (Medium)

**Mitigation:**
- [x] DynamoDB point-in-time recovery enabled (35-day window)
- [ ] Export expired items to S3 via DynamoDB Streams before TTL deletion (long-term archive)
- [x] Document retention policy in compliance wiki (180-day metadata retention approved by legal)
- [ ] Update dashboard queries to handle missing metadata gracefully (show "expired" instead of error)

**Owner:** Data Governance Team
**Review Date:** 2025-02-01
**Status:** Partially Mitigated (residual risk: Medium score 8)

---

### RISK-003: S3 Event Loop from EventBridge Misconfiguration
**Category:** Operational - Cost/Availability
**Description:** EventBridge rule accidentally triggers on processed bucket, causing output Lambda to create files that re-trigger workflows, leading to exponential execution growth and runaway costs ($10k+ bill).

**Likelihood:** 2 (Unlikely - testing catches most misconfigurations)
**Impact:** 5 (Severe - service outage, financial damage, potential account suspension)
**Risk Score:** 10 (Medium)

**Mitigation:**
- [x] EventBridge rule pattern explicitly restricts to `raw-data-bucket` (excludes processed)
- [x] CloudWatch alarm auto-disables rule if ExecutionsStarted >500/min
- [x] AWS Budgets alert at 200% of monthly spend → auto-stop via Lambda
- [x] Integration tests validate event pattern in CI/CD
- [ ] Implement circuit breaker in ingest Lambda (abort if >1000 executions in 5 min)

**Owner:** Data Engineering Lead
**Review Date:** 2025-01-10
**Status:** Mitigated (residual risk: Low score 4)

---

### RISK-004: Lambda Cold Start Latency Breaching SLA
**Category:** Operational - Performance
**Description:** VPC Lambda ENI attachment adds 1-3s cold start latency; if cold start rate >30%, p95 end-to-end latency exceeds 30s SLA.

**Likelihood:** 3 (Possible - observed during low-traffic periods with idle scale-down)
**Impact:** 3 (Moderate - SLA breach, customer complaints)
**Risk Score:** 9 (Medium)

**Mitigation:**
- [x] Lambda provisioned concurrency for critical functions (5 warm instances for ingest/transform)
- [x] CloudWatch alarm monitors cold start rate (threshold: >30%)
- [ ] Evaluate public Lambda (no VPC) if security requirements allow (removes ENI latency)
- [x] Package optimization: Reduce Lambda deployment size from 50MB to 20MB (faster download)
- [ ] Implement keep-warm ping via EventBridge scheduled rule (invoke Lambda every 5 min)

**Owner:** Data Engineering Team
**Review Date:** 2025-01-20
**Status:** Partially Mitigated (residual risk: Medium score 6)

---

## Security Risks

### RISK-005: PII Leakage in CloudWatch Logs
**Category:** Security - Confidentiality
**Description:** Developer accidentally logs PII (names, emails, SSNs) in CloudWatch Logs, leading to GDPR/CCPA violation and potential $50M fine.

**Likelihood:** 4 (Likely - human error, observed in past incidents)
**Impact:** 5 (Severe - regulatory fine, reputational damage, customer lawsuits)
**Risk Score:** 20 (High)

**Mitigation:**
- [x] CloudWatch Logs encrypted with KMS CMK (restrict decrypt to SecOps)
- [ ] Log sanitization library enforced in Lambda code (redact PII regex before logging)
- [x] IAM policy restricts CloudWatch Logs read access (developers no prod access)
- [x] Pre-commit hook scans code for potential PII logging patterns
- [ ] Quarterly DLP scan of CloudWatch Logs for PII (AWS Macie)
- [x] Developer training on PII handling (annual compliance course)

**Owner:** Security Team
**Review Date:** 2025-01-05
**Status:** Partially Mitigated (residual risk: Medium score 12)

---

### RISK-006: Compromised IAM Credentials Leading to Data Exfiltration
**Category:** Security - Confidentiality
**Description:** Attacker steals AWS access keys (leaked in GitHub, phishing, insider threat), accesses S3 raw/processed buckets, downloads all customer data.

**Likelihood:** 3 (Possible - credential leaks occur industry-wide)
**Impact:** 5 (Severe - data breach, regulatory fines, customer trust loss)
**Risk Score:** 15 (Medium)

**Mitigation:**
- [x] No long-lived access keys (IAM roles with STS temporary credentials only)
- [x] MFA required for console access and CLI operations
- [x] S3 access logging to detect unusual download patterns (CloudWatch anomaly detection)
- [x] IAM Access Analyzer detects publicly accessible resources
- [x] Secret scanning in CI/CD (TruffleHog, git-secrets)
- [x] CloudTrail logs all API calls with IP address and user identity
- [ ] Implement S3 Access Points with separate IAM policies per use case

**Owner:** Security Team
**Review Date:** 2025-01-15
**Status:** Mitigated (residual risk: Medium score 9)

---

### RISK-007: Supply Chain Attack via Compromised Python Dependency
**Category:** Security - Integrity
**Description:** Attacker compromises PyPI package (e.g., malicious version of `requests` or `pandas`), Lambda installs backdoored package, exfiltrates data or pivots to other AWS resources.

**Likelihood:** 2 (Unlikely - but increasing industry trend)
**Impact:** 5 (Severe - full pipeline compromise, data theft, account takeover)
**Risk Score:** 10 (Medium)

**Mitigation:**
- [x] Pin exact dependency versions in `requirements.txt` (e.g., `pandas==2.0.3`)
- [x] Snyk/Dependabot vulnerability scanning in CI/CD (blocks deployment if critical CVE)
- [ ] SBOM (Software Bill of Materials) generation via Syft
- [ ] Lambda layer signature verification with Cosign
- [x] Network egress restricted (VPC Lambda with no NAT Gateway, can't exfiltrate to internet)
- [ ] Vendor security review for critical dependencies (pandas, boto3)

**Owner:** Security Team
**Review Date:** 2025-02-01
**Status:** Partially Mitigated (residual risk: Medium score 8)

---

### RISK-008: KMS Key Deletion Rendering Data Unrecoverable
**Category:** Security - Availability
**Description:** Accidental or malicious deletion of KMS CMK used for S3/DynamoDB encryption causes permanent data loss (encrypted data cannot be decrypted).

**Likelihood:** 1 (Rare - requires admin privileges + 30-day waiting period)
**Impact:** 5 (Severe - complete data loss, business continuity failure)
**Risk Score:** 5 (Low)

**Mitigation:**
- [x] KMS key deletion requires 30-day waiting period (time to detect and cancel)
- [x] CloudWatch alarm on `ScheduleKeyDeletion` API call → PagerDuty P1
- [x] IAM policy denies `kms:ScheduleKeyDeletion` for all roles except KMS admin (MFA required)
- [x] Automated daily KMS key health check (verify key status is `Enabled`)
- [x] S3 bucket versioning + replication to secondary region (decrypt with replica key if primary deleted)

**Owner:** Security Team
**Review Date:** 2025-03-01
**Status:** Mitigated (residual risk: Very Low score 2)

---

## Data Quality Risks

### RISK-009: Schema Drift in Upstream Data Source Breaking Validation
**Category:** Data Quality - Integrity
**Description:** Upstream system changes JSON schema (adds required field, changes data type) without notice, causing 100% validation failures and data processing halted.

**Likelihood:** 4 (Likely - upstream teams change schemas without coordination)
**Impact:** 4 (Major - zero data throughput, downstream systems starved, SLA breach)
**Risk Score:** 16 (High)

**Mitigation:**
- [x] JSON Schema validation in validate Lambda with version tracking
- [ ] Schema registry (AWS Glue Schema Registry or Confluent) for centralized management
- [ ] Backward compatibility testing: New schema version must validate old data
- [x] DLQ captures failed validation messages for manual review
- [ ] Upstream SLA requires 2-week notice for breaking schema changes (documented in contract)
- [x] Canary deployment: Route 10% traffic to new schema version, monitor error rate

**Owner:** Data Engineering Lead + Upstream Team Liaison
**Review Date:** 2025-01-10
**Status:** Partially Mitigated (residual risk: Medium score 12)

---

### RISK-010: Duplicate File Processing from S3 Eventual Consistency
**Category:** Data Quality - Integrity
**Description:** S3 eventual consistency causes same file to trigger multiple EventBridge events, leading to duplicate processing and inflated metrics/analytics.

**Likelihood:** 2 (Unlikely - S3 strong read-after-write consistency since Dec 2020)
**Impact:** 3 (Moderate - incorrect analytics, customer overcharging)
**Risk Score:** 6 (Low)

**Mitigation:**
- [x] DynamoDB idempotency table (track processed file S3 object key + version ID)
- [x] Ingest Lambda checks idempotency table before processing (skip if duplicate)
- [x] S3 versioning enabled (use version ID in idempotency key)
- [ ] End-to-end integration test simulates S3 eventual consistency (localstack)

**Owner:** Data Engineering Team
**Review Date:** 2025-02-15
**Status:** Mitigated (residual risk: Very Low score 2)

---

## Cost Risks

### RISK-011: Unexpected Cost Spike from Traffic Surge
**Category:** Cost - Financial
**Description:** Viral event or bot traffic causes 10x surge in S3 uploads, triggering excessive Lambda/Step Functions executions and $5k+ unexpected bill.

**Likelihood:** 3 (Possible - observed during product launches)
**Impact:** 4 (Major - budget overrun, finance escalation)
**Risk Score:** 12 (Medium)

**Mitigation:**
- [x] AWS Budgets alert at 80%/100%/150% of monthly spend
- [x] CloudWatch alarm on daily cost (threshold: >$200/day)
- [ ] Auto-pause EventBridge rule if daily cost exceeds $500 (Lambda-triggered mitigation)
- [x] Reserved Lambda concurrency limits blast radius (max 500 concurrent executions)
- [ ] Rate limiting on S3 upload endpoint (e.g., API Gateway in front of S3 presigned URLs)

**Owner:** FinOps Team
**Review Date:** 2025-01-20
**Status:** Partially Mitigated (residual risk: Medium score 8)

---

### RISK-012: Over-Provisioned Lambda Memory Wasting Budget
**Category:** Cost - Waste
**Description:** Lambda functions allocated 1024MB memory but only use 300MB average, wasting $100+/month (cost proportional to memory allocation).

**Likelihood:** 4 (Likely - default memory often not optimized)
**Impact:** 2 (Minor - waste but not catastrophic)
**Risk Score:** 8 (Medium)

**Mitigation:**
- [x] Quarterly Lambda memory optimization review (CloudWatch Logs Insights query for actual memory usage)
- [x] AWS Compute Optimizer recommendations enabled (suggests right-sized memory)
- [ ] Automated memory tuning via AWS Lambda Power Tuning tool
- [x] CloudWatch dashboard tracks memory utilization % per function

**Owner:** Data Engineering Lead
**Review Date:** 2025-01-30
**Status:** Partially Mitigated (residual risk: Low score 4)

---

## Compliance Risks

### RISK-013: Data Retention Policy Violation (GDPR Right to Erasure)
**Category:** Compliance - Legal
**Description:** Customer requests data deletion (GDPR Art. 17), but data persists in S3 versioning, DynamoDB, CloudWatch Logs, and backups beyond 30-day SLA, leading to €20M fine.

**Likelihood:** 3 (Possible - GDPR requests increasing)
**Impact:** 5 (Severe - regulatory fine, litigation)
**Risk Score:** 15 (Medium)

**Mitigation:**
- [x] S3 lifecycle policy deletes old versions after 90 days
- [x] DynamoDB TTL auto-expires items after 180 days
- [x] CloudWatch Logs retention 30 days (compliance logs 365 days)
- [ ] Data deletion API endpoint for customer requests (searches all data stores, deletes within 30 days)
- [ ] Quarterly audit of retention policies (verify no data exceeds limits)
- [x] Legal review of retention SLAs (30-day deletion documented in privacy policy)

**Owner:** Legal/Compliance Team
**Review Date:** 2025-01-15
**Status:** Partially Mitigated (residual risk: Medium score 9)

---

### RISK-014: Insufficient Audit Trail for SOC 2 Compliance
**Category:** Compliance - Audit
**Description:** CloudTrail logs not comprehensive (missing S3 data events, Lambda invocations), failing SOC 2 audit requirement for "who accessed what, when."

**Likelihood:** 2 (Unlikely - CloudTrail configured, but gaps possible)
**Impact:** 4 (Major - SOC 2 certification delayed/denied, customer trust loss)
**Risk Score:** 8 (Medium)

**Mitigation:**
- [x] CloudTrail data events enabled for all S3 buckets (logs PutObject/GetObject with user identity)
- [x] CloudTrail logs delivered to S3 with 365-day retention + versioning
- [x] CloudTrail log file integrity validation enabled (detect tampering)
- [x] CloudWatch Logs captures all Lambda invocations
- [ ] Monthly audit log review (sample 100 API calls, verify user attribution)
- [ ] Annual SOC 2 Type II audit with external auditor

**Owner:** Compliance Team
**Review Date:** 2025-02-01
**Status:** Mitigated (residual risk: Low score 4)

---

## Summary Dashboard

| Risk ID | Category | Description | Likelihood | Impact | Score | Status |
|---------|----------|-------------|------------|--------|-------|--------|
| RISK-001 | Operational | Lambda concurrency limit | 3 | 4 | 12 | Mitigated (6) |
| RISK-002 | Operational | DynamoDB TTL deletion | 4 | 3 | 12 | Partial (8) |
| RISK-003 | Operational | S3 event loop | 2 | 5 | 10 | Mitigated (4) |
| RISK-004 | Operational | Lambda cold start latency | 3 | 3 | 9 | Partial (6) |
| RISK-005 | Security | PII leakage in logs | 4 | 5 | 20 | Partial (12) |
| RISK-006 | Security | IAM credential compromise | 3 | 5 | 15 | Mitigated (9) |
| RISK-007 | Security | Supply chain attack | 2 | 5 | 10 | Partial (8) |
| RISK-008 | Security | KMS key deletion | 1 | 5 | 5 | Mitigated (2) |
| RISK-009 | Data Quality | Schema drift | 4 | 4 | 16 | Partial (12) |
| RISK-010 | Data Quality | Duplicate processing | 2 | 3 | 6 | Mitigated (2) |
| RISK-011 | Cost | Traffic surge cost spike | 3 | 4 | 12 | Partial (8) |
| RISK-012 | Cost | Over-provisioned memory | 4 | 2 | 8 | Partial (4) |
| RISK-013 | Compliance | GDPR retention violation | 3 | 5 | 15 | Partial (9) |
| RISK-014 | Compliance | SOC 2 audit trail gaps | 2 | 4 | 8 | Mitigated (4) |

**Top 3 Risks Requiring Immediate Attention:**
1. **RISK-005 (PII Leakage):** Residual score 12 (High) - Implement log sanitization library by 2025-01-15
2. **RISK-009 (Schema Drift):** Residual score 12 (High) - Onboard upstream teams to schema registry by 2025-02-01
3. **RISK-013 (GDPR Retention):** Residual score 9 (Medium) - Build data deletion API by 2025-03-01

**Review Cadence:**
- **Monthly:** Review top 5 risks, update mitigation status
- **Quarterly:** Full risk register review, re-assess likelihood/impact based on incidents
- **Annually:** External audit of risk management process (SOC 2 requirement)
