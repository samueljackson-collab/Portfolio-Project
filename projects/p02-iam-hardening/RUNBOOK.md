# Runbook — P02 (IAM Security Hardening)

## Overview

Production operations runbook for IAM security hardening and compliance monitoring. This runbook covers policy deployment, access analysis, incident response, and troubleshooting for AWS IAM security infrastructure.

**System Components:**
- IAM policies (least-privilege roles)
- AWS IAM Access Analyzer
- Lambda-based compliance scanners
- EventBridge automation
- SNS alerting

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Policy deployment success rate** | 99% | CloudFormation/Terraform apply success |
| **Access Analyzer scan frequency** | Daily | EventBridge trigger execution |
| **Alert delivery time** | < 5 minutes | SNS notification latency |
| **Unused credential detection** | < 90 days old | Lambda scan findings |
| **MFA compliance rate** | 100% for privileged users | IAM credential report analysis |
| **External access findings** | Zero high-severity | Access Analyzer findings count |

---

## Dashboards & Alerts

### Dashboards

#### IAM Security Dashboard
```bash
# Check Access Analyzer findings
aws accessanalyzer list-findings \
  --analyzer-name default-analyzer \
  --filter status=ACTIVE

# Check IAM credential report
aws iam generate-credential-report
aws iam get-credential-report --query 'Content' --output text | base64 -d > iam-creds.csv

# Analyze MFA compliance
awk -F, '$4=="false" && $1!="<root_account>" {print $1}' iam-creds.csv
```

#### Policy Compliance Dashboard
```bash
# List all IAM policies
aws iam list-policies --scope Local

# Check policy versions
aws iam list-policy-versions --policy-arn <policy-arn>

# Check attached entities
aws iam list-entities-for-policy --policy-arn <policy-arn>
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | External access to critical resource | Immediate | Revoke access, investigate |
| **P1** | MFA not enforced on admin role | 30 minutes | Enable MFA enforcement |
| **P1** | Overly permissive policy deployed | 1 hour | Review and tighten policy |
| **P2** | Unused credentials > 90 days | 24 hours | Disable inactive credentials |
| **P3** | Policy validation warning | 48 hours | Review and fix policy syntax |

#### Alert Queries

**High-Severity External Access:**
```bash
aws accessanalyzer list-findings \
  --analyzer-name default-analyzer \
  --filter '{
    "status": {"eq": ["ACTIVE"]},
    "resourceType": {"eq": ["AWS::S3::Bucket", "AWS::IAM::Role"]},
    "isPublic": {"eq": [true]}
  }'
```

**Unused Credentials:**
```bash
# Find users with unused passwords (>90 days)
aws iam get-credential-report --query 'Content' --output text | \
  base64 -d | \
  awk -F, 'NR>1 && $5!="N/A" && $5!="no_information" {
    cmd="date -d \""$5"\" +%s 2>/dev/null"
    cmd | getline last_used
    close(cmd)
    now=systime()
    days_unused=(now-last_used)/86400
    if(days_unused>90) print $1" - "$5" ("int(days_unused)" days)"
  }'
```

---

## Standard Operations

### Policy Management

#### Deploy New IAM Policy
```bash
# 1. Validate policy syntax
make validate-policies

# 2. Review policy changes
make policy-diff POLICY=policies/new-developer-role.json

# 3. Simulate policy permissions
make simulate \
  POLICY=policies/new-developer-role.json \
  ACTION=s3:PutObject \
  RESOURCE=arn:aws:s3:::prod-bucket/*

# Expected: Denied (developers shouldn't write to prod)

# 4. Deploy policy
aws iam create-policy \
  --policy-name DeveloperRole \
  --policy-document file://policies/new-developer-role.json

# 5. Attach to role
aws iam attach-role-policy \
  --role-name developer \
  --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/DeveloperRole

# 6. Verify attachment
aws iam list-attached-role-policies --role-name developer
```

#### Update Existing Policy
```bash
# 1. Create new policy version
aws iam create-policy-version \
  --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/DeveloperRole \
  --policy-document file://policies/updated-developer-role.json \
  --set-as-default

# 2. Verify new version is active
aws iam get-policy-version \
  --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/DeveloperRole \
  --version-id v2

# 3. Test with IAM Policy Simulator
# Go to: https://policysim.aws.amazon.com/
```

#### Rollback Policy
```bash
# List policy versions
aws iam list-policy-versions \
  --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/DeveloperRole

# Set previous version as default
aws iam set-default-policy-version \
  --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/DeveloperRole \
  --version-id v1

# Delete problematic version
aws iam delete-policy-version \
  --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/DeveloperRole \
  --version-id v2
```

### Access Analyzer Operations

#### Run Manual Scan
```bash
# Trigger immediate scan
aws accessanalyzer start-resource-scan \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:${AWS_ACCOUNT_ID}:analyzer/default-analyzer \
  --resource-arn arn:aws:s3:::my-bucket
```

#### Review Findings
```bash
# List all active findings
aws accessanalyzer list-findings \
  --analyzer-name default-analyzer \
  --filter status=ACTIVE \
  --output table

# Get finding details
aws accessanalyzer get-finding \
  --analyzer-name default-analyzer \
  --id <finding-id>

# Archive resolved finding
aws accessanalyzer update-findings \
  --analyzer-name default-analyzer \
  --ids <finding-id> \
  --status ARCHIVED
```

### MFA Enforcement

#### Enable MFA on User
```bash
# Check current MFA status
aws iam list-mfa-devices --user-name john.doe

# Create virtual MFA device
aws iam create-virtual-mfa-device \
  --virtual-mfa-device-name john-doe-mfa \
  --outfile qr-code.png \
  --bootstrap-method QRCodePNG

# User scans QR code and provides two consecutive codes
aws iam enable-mfa-device \
  --user-name john.doe \
  --serial-number arn:aws:iam::${AWS_ACCOUNT_ID}:mfa/john-doe-mfa \
  --authentication-code-1 123456 \
  --authentication-code-2 789012
```

#### Enforce MFA in Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}
    }
  }]
}
```

---

## Incident Response

### P0: External Access to Critical Resource

**Immediate Actions (0-5 minutes):**
```bash
# 1. Get finding details
aws accessanalyzer get-finding \
  --analyzer-name default-analyzer \
  --id <finding-id> > finding-details.json

# 2. Identify affected resource
RESOURCE_ARN=$(jq -r '.finding.resource' finding-details.json)

# 3. Emergency: Block public access (S3 example)
if [[ $RESOURCE_ARN == arn:aws:s3:::* ]]; then
  BUCKET_NAME=$(echo $RESOURCE_ARN | cut -d: -f6)
  aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration \
      BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
fi

# 4. Notify security team
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:${AWS_ACCOUNT_ID}:security-alerts \
  --subject "P0: External access detected - ${RESOURCE_ARN}" \
  --message "External access finding: $(cat finding-details.json)"
```

**Investigation (5-30 minutes):**
```bash
# Check CloudTrail for recent changes
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=$RESOURCE_ARN \
  --max-results 50 \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S)

# Identify who made the change
# Check policy history
aws iam list-policy-versions --policy-arn <policy-arn>
```

**Remediation:**
```bash
# Update bucket policy to remove public access
aws s3api delete-bucket-policy --bucket $BUCKET_NAME

# Or update IAM policy
aws iam delete-policy-version \
  --policy-arn <policy-arn> \
  --version-id <bad-version>

# Archive finding after remediation
aws accessanalyzer update-findings \
  --analyzer-name default-analyzer \
  --ids <finding-id> \
  --status ARCHIVED
```

### P1: Overly Permissive Policy

**Investigation:**
```bash
# Review policy document
aws iam get-policy-version \
  --policy-arn <policy-arn> \
  --version-id <version-id>

# Check what actions are too broad
# Look for: Action: "*", Resource: "*", wildcards
```

**Remediation:**
```bash
# Create restricted version
cat > policies/restricted-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:ListBucket"
    ],
    "Resource": [
      "arn:aws:s3:::allowed-bucket",
      "arn:aws:s3:::allowed-bucket/*"
    ]
  }]
}
EOF

# Deploy restricted policy
make deploy-policies POLICY=policies/restricted-policy.json
```

### P2: Unused Credentials Detected

**Investigation:**
```bash
# Generate credential report
aws iam generate-credential-report
aws iam get-credential-report --query 'Content' --output text | base64 -d > creds.csv

# Find unused credentials
awk -F, 'NR>1 {
  if($5!="N/A" && $5!="no_information") {
    print $1","$5","$9  # user, password_last_used, access_key_1_last_used
  }
}' creds.csv | grep -v $(date -d '90 days ago' +%Y-%m-%d)
```

**Remediation:**
```bash
# Disable unused access keys
aws iam update-access-key \
  --user-name inactive-user \
  --access-key-id AKIAIOSFODNN7EXAMPLE \
  --status Inactive

# Or delete access key
aws iam delete-access-key \
  --user-name inactive-user \
  --access-key-id AKIAIOSFODNN7EXAMPLE

# Disable password login
aws iam delete-login-profile --user-name inactive-user
```

---

## Troubleshooting

### Common Issues

#### Issue: Access Denied when assuming role

**Diagnosis:**
```bash
# Check role trust policy
aws iam get-role --role-name target-role | jq '.Role.AssumeRolePolicyDocument'

# Check if MFA is required
# Look for: "aws:MultiFactorAuthPresent": "true"

# Verify user can assume role
aws sts assume-role \
  --role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/target-role \
  --role-session-name test-session
```

**Solution:**
```bash
# If MFA required, provide MFA token
aws sts assume-role \
  --role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/target-role \
  --role-session-name test-session \
  --serial-number arn:aws:iam::${AWS_ACCOUNT_ID}:mfa/user-mfa \
  --token-code 123456

# If trust policy incorrect, update it
aws iam update-assume-role-policy \
  --role-name target-role \
  --policy-document file://trust-policy.json
```

---

#### Issue: Policy too large (exceeds 6,144 characters)

**Solution:**
```bash
# Split into multiple managed policies
# Or use inline policies (max 10 per role)
# Or use AWS managed policies as building blocks
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Review Access Analyzer findings
aws accessanalyzer list-findings \
  --analyzer-name default-analyzer \
  --filter status=ACTIVE

# Check for new unused credentials
make check-unused-credentials
```

### Weekly Tasks
```bash
# Review all IAM policies
aws iam list-policies --scope Local

# Audit policy attachments
./scripts/audit-policy-attachments.sh

# Review credential report
aws iam get-credential-report
```

### Monthly Tasks
```bash
# Rotate access keys
./scripts/rotate-access-keys.sh

# Review and update policies
# Remove unused policies
aws iam list-policies --scope Local --only-attached false

# Conduct access review
# Verify all role assignments are still needed
```

---

## Quick Reference

### Common Commands
```bash
# List policies
aws iam list-policies --scope Local

# Validate policy
make validate-policies

# Deploy policy
make deploy-policies POLICY=policies/my-policy.json

# Check findings
aws accessanalyzer list-findings --analyzer-name default-analyzer

# Generate credential report
aws iam generate-credential-report && aws iam get-credential-report
```

### Emergency Response
```bash
# P0: Block public S3 access
aws s3api put-public-access-block --bucket <bucket> \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# P1: Disable compromised credentials
aws iam delete-access-key --user-name <user> --access-key-id <key>

# P2: Rollback policy
aws iam set-default-policy-version --policy-arn <arn> --version-id <previous-version>
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Security Engineering Team
- **Review Schedule:** Quarterly or after security incidents
- **Feedback:** Submit PR with updates

## Evidence & Verification

Verification summary: Evidence artifacts captured on 2025-11-14 to validate the quickstart configuration and document audit-ready supporting files.

**Evidence artifacts**
- Screenshot stored externally.
- [Run log](./docs/evidence/run-log.txt)
- [Dashboard export](./docs/evidence/dashboard-export.json)
- [Load test summary](./docs/evidence/load-test-summary.txt)

### Evidence Checklist

| Evidence Item | Location | Status |
| --- | --- | --- |
| Screenshot captured | Stored externally | ✅ |
| Run log captured | `docs/evidence/run-log.txt` | ✅ |
| Dashboard export captured | `docs/evidence/dashboard-export.json` | ✅ |
| Load test summary captured | `docs/evidence/load-test-summary.txt` | ✅ |
