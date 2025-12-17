# Runbook — P19 (Cloud Security Automation)

## Overview

Production operations runbook for automated cloud security compliance and vulnerability management. This runbook covers CIS benchmark compliance, vulnerability scanning, security posture assessment, automated remediation, and incident response for cloud security operations.

**System Components:**

- CIS AWS Foundations Benchmark scanner
- Vulnerability scanning engine
- Security configuration auditor
- IAM analysis and reporting
- Automated remediation scripts
- Compliance report generator
- Security posture dashboard
- Alert and notification system

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Security scan completion rate** | 99% | Scheduled scan success rate |
| **CIS compliance score** | > 90% | Passing checks / Total checks |
| **Vulnerability detection time** | < 1 hour | Time from creation → detection |
| **Critical vulnerability remediation time** | < 4 hours | Detection → fix deployment |
| **False positive rate** | < 5% | False positives / Total findings |
| **Auto-remediation success rate** | 95% | Successful automatic fixes |
| **Report generation time** | < 15 minutes | Scan completion → report ready |

---

## Dashboards & Alerts

### Dashboards

#### Security Compliance Dashboard

```bash
# Run full CIS benchmark scan
make scan-cis

# Check current compliance score
./scripts/compliance-score.sh

# View compliance by category
./scripts/compliance-breakdown.sh | column -t

# List failed checks
./scripts/list-failed-checks.sh

# Show compliance trends
./scripts/compliance-trends.sh --days=30
```

#### Vulnerability Dashboard

```bash
# Run vulnerability scan
make scan-all

# List critical vulnerabilities
./scripts/list-vulnerabilities.sh --severity=CRITICAL

# Show vulnerability by service
./scripts/vulnerabilities-by-service.sh

# Check patching status
./scripts/check-patch-status.sh

# Generate vulnerability report
make generate-report
```

#### Security Posture Dashboard

```bash
# Overall security posture score
./scripts/security-posture-score.sh

# IAM security analysis
./scripts/analyze-iam-security.sh

# Network security assessment
./scripts/analyze-network-security.sh

# Data encryption status
./scripts/check-encryption-status.sh

# Public access review
./scripts/check-public-access.sh
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Critical vulnerability detected | Immediate | Emergency remediation |
| **P0** | Public S3 bucket with sensitive data | Immediate | Block access immediately |
| **P1** | CIS compliance score < 80% | 2 hours | Review and remediate |
| **P1** | High-severity vulnerability | 4 hours | Patch or mitigate |
| **P2** | CIS check failure | 24 hours | Schedule remediation |
| **P2** | Medium vulnerability detected | 48 hours | Plan remediation |
| **P3** | Low vulnerability detected | 1 week | Review and prioritize |

#### Alert Queries

```bash
# Check for critical vulnerabilities
CRITICAL_COUNT=$(./scripts/count-vulnerabilities.sh --severity=CRITICAL)
if [ $CRITICAL_COUNT -gt 0 ]; then
  echo "ALERT: $CRITICAL_COUNT critical vulnerabilities detected"
  ./scripts/list-vulnerabilities.sh --severity=CRITICAL
fi

# Check CIS compliance score
COMPLIANCE_SCORE=$(./scripts/compliance-score.sh --numeric)
if [ $COMPLIANCE_SCORE -lt 80 ]; then
  echo "ALERT: CIS compliance score below threshold: ${COMPLIANCE_SCORE}%"
fi

# Check for public S3 buckets
PUBLIC_BUCKETS=$(aws s3api list-buckets --query 'Buckets[*].Name' --output text | \
  xargs -I {} aws s3api get-bucket-acl --bucket {} | grep -c "AllUsers" || true)
if [ $PUBLIC_BUCKETS -gt 0 ]; then
  echo "ALERT: $PUBLIC_BUCKETS public S3 buckets detected"
fi

# Check for overly permissive IAM policies
PERMISSIVE_POLICIES=$(./scripts/find-permissive-policies.sh | wc -l)
if [ $PERMISSIVE_POLICIES -gt 0 ]; then
  echo "ALERT: $PERMISSIVE_POLICIES overly permissive IAM policies found"
fi
```

---

## Standard Operations

### CIS Benchmark Scanning

#### Run Full CIS Scan

```bash
# Initialize scanner
make setup

# Run complete CIS benchmark scan
make scan-cis

# View scan results
cat reports/cis-scan-$(date +%Y%m%d).json | jq '.summary'

# Generate human-readable report
./scripts/generate-cis-report.sh > reports/cis-report-$(date +%Y%m%d).html

# Open report in browser
xdg-open reports/cis-report-*.html
```

#### Run Specific CIS Sections

```bash
# Scan IAM section only
./scripts/scan-cis.sh --section=1_Identity_and_Access_Management

# Scan logging and monitoring
./scripts/scan-cis.sh --section=3_Logging

# Scan networking
./scripts/scan-cis.sh --section=4_Networking

# Multiple sections
./scripts/scan-cis.sh --sections=1,2,3
```

#### Review Failed Checks

```bash
# List all failed checks
./scripts/list-failed-checks.sh

# Show details for specific check
./scripts/check-details.sh --check-id=1.1

# Show remediation steps
./scripts/show-remediation.sh --check-id=1.1

# Export failed checks
./scripts/list-failed-checks.sh --format=csv > failed-checks.csv
```

### Vulnerability Scanning

#### Run Vulnerability Scans

```bash
# Scan all resources
make scan-all

# Scan specific resource types
./scripts/vuln-scan.sh --resource-type=ec2
./scripts/vuln-scan.sh --resource-type=rds
./scripts/vuln-scan.sh --resource-type=s3

# Scan by tag
./scripts/vuln-scan.sh --tag=Environment=production

# Deep scan (more thorough, slower)
./scripts/vuln-scan.sh --mode=deep
```

#### Analyze Vulnerabilities

```bash
# List all vulnerabilities
./scripts/list-vulnerabilities.sh

# Filter by severity
./scripts/list-vulnerabilities.sh --severity=CRITICAL
./scripts/list-vulnerabilities.sh --severity=HIGH

# Group by resource
./scripts/vulnerabilities-by-resource.sh

# Show CVE details
./scripts/cve-details.sh --cve-id=CVE-2024-1234

# Check if vulnerability is exploitable
./scripts/check-exploitability.sh --cve-id=CVE-2024-1234
```

#### Track Vulnerability Remediation

```bash
# Show remediation status
./scripts/remediation-status.sh

# Mark vulnerability as remediated
./scripts/mark-remediated.sh --vuln-id=VULN-001

# Verify remediation
./scripts/verify-remediation.sh --vuln-id=VULN-001

# Re-scan to confirm fix
./scripts/vuln-scan.sh --resource-id=i-1234567890abcdef0
```

### Security Configuration Audit

#### IAM Security Audit

```bash
# Analyze IAM configuration
./scripts/audit-iam.sh

# Check for unused credentials
./scripts/find-unused-credentials.sh --days=90

# Find overly permissive policies
./scripts/find-permissive-policies.sh

# Check MFA enforcement
./scripts/check-mfa-compliance.sh

# Review access keys rotation
./scripts/check-key-rotation.sh
```

#### Network Security Audit

```bash
# Audit security groups
./scripts/audit-security-groups.sh

# Find overly permissive security groups
./scripts/find-open-security-groups.sh

# Check NACLs
./scripts/audit-nacls.sh

# Review VPC flow logs
./scripts/check-flow-logs.sh

# Scan for public resources
./scripts/find-public-resources.sh
```

#### Encryption Audit

```bash
# Check S3 encryption
./scripts/check-s3-encryption.sh

# Check EBS encryption
./scripts/check-ebs-encryption.sh

# Check RDS encryption
./scripts/check-rds-encryption.sh

# Check encryption in transit
./scripts/check-tls-configuration.sh
```

### Automated Remediation

#### Enable Auto-Remediation

```bash
# Configure auto-remediation
export AUTO_REMEDIATE=true

# Set remediation level (low, medium, high)
export REMEDIATION_LEVEL=medium

# Enable for specific checks only
./scripts/configure-auto-remediation.sh --checks=1.3,1.4,2.1

# Test remediation (dry-run)
./scripts/test-remediation.sh --check-id=1.3 --dry-run
```

#### Manual Remediation

```bash
# Remediate specific check
./scripts/remediate.sh --check-id=1.3

# Remediate all failed checks in section
./scripts/remediate-section.sh --section=1

# Remediate specific vulnerability
./scripts/remediate-vulnerability.sh --vuln-id=VULN-001

# Batch remediation
./scripts/batch-remediate.sh --severity=HIGH --auto-approve
```

#### Verify Remediation

```bash
# Re-run checks after remediation
./scripts/verify-remediation.sh --check-id=1.3

# Full re-scan
make scan-cis

# Compare before/after
diff reports/cis-scan-before.json reports/cis-scan-after.json | \
  jq '.summary'
```

### Compliance Reporting

#### Generate Reports

```bash
# Generate full compliance report
make generate-report

# Generate executive summary
./scripts/generate-executive-summary.sh > reports/executive-summary.pdf

# Generate detailed technical report
./scripts/generate-technical-report.sh > reports/technical-report.html

# Generate trend report
./scripts/generate-trend-report.sh --days=90 > reports/trends.pdf

# Export to different formats
./scripts/generate-report.sh --format=pdf
./scripts/generate-report.sh --format=csv
./scripts/generate-report.sh --format=json
```

#### Schedule Automated Reports

```bash
# Configure daily reports
./scripts/schedule-report.sh --frequency=daily --recipients=security@example.com

# Weekly executive summary
./scripts/schedule-report.sh --frequency=weekly --type=executive --recipients=cto@example.com

# Monthly compliance report
./scripts/schedule-report.sh --frequency=monthly --type=compliance --recipients=compliance@example.com
```

---

## Incident Response

### Detection

**Automated Detection:**

- Critical vulnerability discovered
- CIS compliance failure detected
- Public resource exposure alerts
- Unusual IAM activity
- Security group changes
- Encryption violations

**Manual Detection:**

```bash
# Check for security incidents
./scripts/check-security-incidents.sh

# Review recent security events
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteBucketPolicy \
  --max-results 50

# Check for anomalous activity
./scripts/detect-anomalies.sh --window=24h

# Review failed security checks
./scripts/list-failed-checks.sh --since="24 hours ago"
```

### Triage

#### Severity Classification

**P0: Critical Security Issue**

- Critical vulnerability with active exploits
- Public S3 bucket with PII/sensitive data
- Root account compromise indicators
- Complete encryption failure
- Public database with no authentication

**P1: High Security Risk**

- High-severity vulnerability
- CIS compliance score < 70%
- Overly permissive IAM policy in production
- Disabled CloudTrail logging
- Security group allowing 0.0.0.0/0 to sensitive ports

**P2: Medium Security Risk**

- Medium-severity vulnerability
- CIS check failures (non-critical)
- Unused IAM credentials > 90 days
- Missing encryption on non-critical data
- Flow logs disabled

**P3: Low Security Risk**

- Low-severity vulnerability
- CIS informational findings
- Suboptimal configurations
- Missing tags
- Documentation gaps

### Incident Response Procedures

#### P0: Critical Vulnerability with Active Exploits

**Immediate Actions (0-15 minutes):**

```bash
# 1. Identify affected resources
./scripts/find-vulnerable-resources.sh --cve-id=CVE-2024-CRITICAL

# 2. Isolate affected resources
for instance_id in $(./scripts/find-vulnerable-resources.sh --cve-id=CVE-2024-CRITICAL --output=ids); do
  echo "Isolating $instance_id"
  # Remove from load balancer
  aws elbv2 deregister-targets --target-group-arn <arn> --targets Id=$instance_id

  # Isolate network (emergency security group)
  aws ec2 modify-instance-attribute \
    --instance-id $instance_id \
    --groups sg-isolation-only
done

# 3. Notify security team
./scripts/notify-security-team.sh --severity=P0 --cve=CVE-2024-CRITICAL

# 4. Document incident
./scripts/create-incident.sh --severity=P0 --cve=CVE-2024-CRITICAL
```

**Investigation (15-60 minutes):**

```bash
# Check for exploitation indicators
./scripts/check-exploitation-indicators.sh --cve-id=CVE-2024-CRITICAL

# Review logs for suspicious activity
./scripts/analyze-logs.sh --resources=$(./scripts/find-vulnerable-resources.sh --cve-id=CVE-2024-CRITICAL --output=ids)

# Check lateral movement
./scripts/check-lateral-movement.sh

# Assess blast radius
./scripts/assess-impact.sh --cve-id=CVE-2024-CRITICAL
```

**Remediation (1-4 hours):**

```bash
# Apply emergency patch
./scripts/emergency-patch.sh --cve-id=CVE-2024-CRITICAL

# Or deploy fixed versions
./scripts/deploy-fixed-version.sh --affected-resources=vulnerable-resources.txt

# Verify patch applied
./scripts/verify-patch.sh --cve-id=CVE-2024-CRITICAL

# Re-scan to confirm
./scripts/vuln-scan.sh --cve-id=CVE-2024-CRITICAL

# Restore to production (gradually)
./scripts/restore-to-production.sh --instance-ids=<ids> --gradual
```

#### P0: Public S3 Bucket with Sensitive Data

**Immediate Actions (0-5 minutes):**

```bash
# 1. Identify bucket
BUCKET_NAME=$(./scripts/find-public-buckets.sh | head -1)

# 2. IMMEDIATELY block public access
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# 3. Remove public bucket policy
aws s3api delete-bucket-policy --bucket $BUCKET_NAME

# 4. Remove public ACLs
aws s3api put-bucket-acl --bucket $BUCKET_NAME --acl private

# 5. Verify bucket is now private
aws s3api get-bucket-acl --bucket $BUCKET_NAME
aws s3api get-public-access-block --bucket $BUCKET_NAME
```

**Investigation (5-30 minutes):**

```bash
# Check S3 access logs
aws s3api get-bucket-logging --bucket $BUCKET_NAME

# Analyze access logs
./scripts/analyze-s3-access-logs.sh --bucket=$BUCKET_NAME --since="24 hours ago"

# Identify who made bucket public
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=$BUCKET_NAME \
  --max-results 100 | jq '.Events[] | select(.EventName | contains("PutBucket"))'

# Check what data was accessed
./scripts/check-data-access.sh --bucket=$BUCKET_NAME
```

**Remediation:**

```bash
# Enable S3 access logging if not enabled
aws s3api put-bucket-logging \
  --bucket $BUCKET_NAME \
  --bucket-logging-status file://logging-config.json

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration file://encryption-config.json

# Notify affected parties if data breach confirmed
./scripts/notify-data-breach.sh --bucket=$BUCKET_NAME

# Implement preventive controls
./scripts/enable-bucket-protection.sh --all-buckets
```

#### P1: CIS Compliance Score Below Threshold

**Investigation:**

```bash
# Generate detailed compliance report
./scripts/compliance-report.sh --detailed

# Identify critical failures
./scripts/list-failed-checks.sh --priority=CRITICAL

# Group failures by category
./scripts/group-failures.sh

# Check trend
./scripts/compliance-trends.sh --days=7
```

**Remediation:**

```bash
# Prioritize critical checks
./scripts/prioritize-remediation.sh --output=remediation-plan.txt

# Auto-remediate safe checks
./scripts/batch-remediate.sh --safe-only --auto-approve

# Manual remediation for complex checks
cat remediation-plan.txt | while read check_id; do
  echo "Remediating $check_id"
  ./scripts/show-remediation.sh --check-id=$check_id
  read -p "Proceed with remediation? (y/n) " -n 1 -r
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./scripts/remediate.sh --check-id=$check_id
  fi
done

# Verify compliance improved
make scan-cis
./scripts/compliance-score.sh
```

#### P2: Overly Permissive IAM Policy

**Investigation:**

```bash
# Identify permissive policies
./scripts/find-permissive-policies.sh

# Show policy details
POLICY_ARN=$(./scripts/find-permissive-policies.sh --format=arn | head -1)
aws iam get-policy-version \
  --policy-arn $POLICY_ARN \
  --version-id $(aws iam get-policy --policy-arn $POLICY_ARN --query 'Policy.DefaultVersionId' --output text)

# Check who is affected
aws iam list-entities-for-policy --policy-arn $POLICY_ARN

# Review usage patterns
./scripts/analyze-policy-usage.sh --policy-arn=$POLICY_ARN
```

**Remediation:**

```bash
# Create restricted version
./scripts/create-restricted-policy.sh --policy-arn=$POLICY_ARN --output=restricted-policy.json

# Test restricted policy
aws iam simulate-custom-policy \
  --policy-input-list file://restricted-policy.json \
  --action-names s3:* ec2:* \
  --resource-arns "*"

# Deploy restricted policy
aws iam create-policy-version \
  --policy-arn $POLICY_ARN \
  --policy-document file://restricted-policy.json \
  --set-as-default

# Monitor for issues
./scripts/monitor-policy-impact.sh --policy-arn=$POLICY_ARN --duration=1h
```

### Post-Incident

**After Resolution:**

```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << EOF
# Security Incident Report

**Date:** $(date)
**Severity:** P0
**Duration:** 2 hours
**Type:** Critical Vulnerability

## Timeline
- 10:00: Critical vulnerability CVE-2024-1234 detected
- 10:15: Affected resources isolated
- 10:30: Security team assembled
- 11:00: Emergency patch applied
- 12:00: Resources restored to production
- 12:00: Verification complete

## Root Cause
Unpatched library with critical RCE vulnerability

## Impact
15 EC2 instances temporarily isolated, no evidence of exploitation

## Action Items
- [ ] Implement automated patching for critical vulnerabilities
- [ ] Add vulnerability detection to CI/CD pipeline
- [ ] Enhanced monitoring for exploitation indicators
- [ ] Update incident response procedures

EOF

# Update vulnerability database
./scripts/update-vulnerability-database.sh

# Re-scan to verify fix
make scan-all

# Generate post-incident report
./scripts/generate-incident-report.sh --incident-id=$(date +%Y%m%d-%H%M)
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: False Positive Vulnerability

**Symptoms:**

- Scanner reports vulnerability but resource is not actually affected
- CVE doesn't apply to this configuration
- Vulnerability already mitigated

**Diagnosis:**

```bash
# Review finding details
./scripts/show-finding-details.sh --finding-id=VULN-001

# Check CVE applicability
./scripts/check-cve-applicability.sh --cve-id=CVE-2024-1234 --resource-id=i-123456

# Verify mitigation
./scripts/verify-mitigation.sh --finding-id=VULN-001
```

**Solution:**

```bash
# Mark as false positive
./scripts/mark-false-positive.sh --finding-id=VULN-001 --reason="Not applicable to this configuration"

# Add to exceptions
./scripts/add-exception.sh --finding-id=VULN-001

# Update scanner rules
./scripts/update-scanner-rules.sh --suppress=CVE-2024-1234 --resource-type=ec2
```

---

#### Issue: Scan Timeout or Failure

**Symptoms:**

```bash
$ make scan-cis
Error: Scan timeout after 30 minutes
```

**Diagnosis:**

```bash
# Check scanner logs
tail -100 logs/scanner.log

# Check AWS API rate limits
aws service-quotas list-service-quotas --service-code cloudwatch | grep RateLimit

# Test API connectivity
./scripts/test-api-connectivity.sh
```

**Solution:**

```bash
# Increase timeout
export SCAN_TIMEOUT=3600  # 1 hour

# Split scan into sections
./scripts/scan-cis.sh --section=1
./scripts/scan-cis.sh --section=2
./scripts/scan-cis.sh --section=3

# Use parallel scanning with rate limiting
./scripts/scan-parallel.sh --workers=5 --rate-limit=10
```

---

#### Issue: Auto-Remediation Failed

**Symptoms:**

- Remediation script completed but check still fails
- Error during remediation execution
- Resource in inconsistent state

**Diagnosis:**

```bash
# Check remediation logs
cat logs/remediation-$(date +%Y%m%d).log | grep ERROR

# Verify resource state
./scripts/check-resource-state.sh --resource-id=<id>

# Re-run check manually
./scripts/run-check.sh --check-id=1.3 --verbose
```

**Solution:**

```bash
# Manual remediation
./scripts/show-remediation.sh --check-id=1.3
# Follow manual steps

# Or rollback
./scripts/rollback-remediation.sh --check-id=1.3

# Fix and retry
./scripts/fix-remediation-script.sh --check-id=1.3
./scripts/remediate.sh --check-id=1.3
```

---

#### Issue: High False Positive Rate

**Symptoms:**

- Many findings marked as false positives
- Scanner reporting issues that don't apply
- Excessive alert fatigue

**Solution:**

```bash
# Tune scanner sensitivity
./scripts/tune-scanner.sh --reduce-false-positives

# Update scanner rules based on environment
./scripts/customize-scanner-rules.sh --environment=production

# Implement baseline exceptions
./scripts/create-baseline.sh --output=exceptions.json

# Regular false positive review
./scripts/review-false-positives.sh --weekly
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 day (daily scans + continuous monitoring)
- **RTO** (Recovery Time Objective): 4 hours (critical vulnerability remediation)

### Backup Strategy

**Compliance Data Backups:**

```bash
# Backup scan results
cp -r reports/ backups/reports-$(date +%Y%m%d)/
tar czf backups/reports-$(date +%Y%m%d).tar.gz backups/reports-*/

# Backup configuration
cp -r config/ backups/config-$(date +%Y%m%d)/

# Store in S3
aws s3 sync backups/ s3://security-automation-backups/$(date +%Y/%m/%d)/

# Verify backups
aws s3 ls s3://security-automation-backups/ --recursive | tail -20
```

**Scanner Configuration Backups:**

```bash
# Export scanner configuration
./scripts/export-scanner-config.sh > scanner-config-$(date +%Y%m%d).json

# Export exceptions and baselines
./scripts/export-exceptions.sh > exceptions-$(date +%Y%m%d).json

# Version control
git add config/ reports/ exceptions.json
git commit -m "backup: security scanner config $(date +%Y-%m-%d)"
git push
```

### Disaster Recovery Procedures

#### Scanner System Failure

**Recovery Steps (30-60 minutes):**

```bash
# 1. Restore from backup
aws s3 sync s3://security-automation-backups/latest/ ./

# 2. Reinstall scanner
make setup

# 3. Restore configuration
./scripts/import-scanner-config.sh scanner-config-latest.json
./scripts/import-exceptions.sh exceptions-latest.json

# 4. Verify scanner
make test

# 5. Run validation scan
./scripts/test-scan.sh --sample-resources

# 6. Resume normal operations
make scan-cis
```

#### Compliance Data Loss

**Recovery Steps (15-30 minutes):**

```bash
# 1. Restore reports from backup
aws s3 cp s3://security-automation-backups/latest/reports.tar.gz .
tar xzf reports.tar.gz

# 2. Regenerate missing data
make scan-all
make generate-report

# 3. Verify data integrity
./scripts/verify-scan-data.sh

# 4. Update dashboards
./scripts/update-dashboards.sh
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Run automated security scans
make scan-cis

# Check for critical vulnerabilities
./scripts/check-critical-vulns.sh

# Review new findings
./scripts/list-new-findings.sh --since="24 hours ago"

# Check auto-remediation status
./scripts/check-remediation-status.sh

# Monitor compliance score
./scripts/compliance-score.sh
```

### Weekly Tasks

```bash
# Full vulnerability scan
make scan-all

# Review and update exceptions
./scripts/review-exceptions.sh

# Analyze security trends
./scripts/security-trends.sh --days=7

# Update scanner rules
./scripts/update-scanner-rules.sh

# Generate weekly report
./scripts/generate-weekly-report.sh
```

### Monthly Tasks

```bash
# Comprehensive security audit
./scripts/full-security-audit.sh

# Review and tune scanner
./scripts/tune-scanner.sh

# Update CIS benchmark version
./scripts/update-cis-benchmark.sh

# Conduct false positive review
./scripts/review-false-positives.sh --comprehensive

# Generate executive summary
./scripts/generate-executive-summary.sh
```

### Quarterly Tasks

```bash
# Major scanner updates
./scripts/update-scanner.sh --major

# Review and update security policies
./scripts/review-security-policies.sh

# Conduct penetration testing validation
./scripts/validate-security-controls.sh

# Update incident response procedures
make update-runbook
```

---

## Operational Best Practices

### Pre-Deployment Checklist

- [ ] Scanner configuration validated
- [ ] Baseline exceptions documented
- [ ] Auto-remediation tested in non-prod
- [ ] Alert recipients configured
- [ ] Report templates customized
- [ ] Integration tested

### Security Scanning Best Practices

- **Scan frequency:** Daily for CIS, continuous for vulnerabilities
- **Remediation SLA:** 4 hours for critical, 48 hours for high
- **False positive review:** Weekly minimum
- **Report distribution:** Security team (daily), executives (monthly)
- **Auto-remediation:** Enable for low-risk checks only
- **Exception management:** Review and expire quarterly

---

## Quick Reference

### Most Common Operations

```bash
# Run CIS scan
make scan-cis

# Run vulnerability scan
make scan-all

# Check compliance score
./scripts/compliance-score.sh

# List failed checks
./scripts/list-failed-checks.sh

# Remediate specific check
./scripts/remediate.sh --check-id=1.3

# Generate report
make generate-report

# Check for critical issues
./scripts/check-critical-issues.sh
```

### Emergency Response

```bash
# P0: Critical vulnerability
./scripts/find-vulnerable-resources.sh --cve-id=<CVE>
./scripts/isolate-resources.sh --resource-ids=<ids>
./scripts/emergency-patch.sh --cve-id=<CVE>

# P0: Public S3 bucket
aws s3api put-public-access-block --bucket <name> --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# P1: Low compliance score
./scripts/batch-remediate.sh --safe-only --auto-approve
make scan-cis
```

---

**Document Metadata:**

- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Security Engineering Team
- **Review Schedule:** Quarterly or after security incidents
- **Feedback:** Create issue or submit PR with updates
