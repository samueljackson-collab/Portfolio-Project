# Runbook — PRJ-CLOUD-001 (AWS Landing Zone with Organizations & SSO)

## Overview

Production operations runbook for AWS Landing Zone implementation with AWS Organizations and Single Sign-On (SSO). This runbook covers multi-account management, user access control, organizational policies, and security best practices for enterprise AWS environments.

**System Components:**
- AWS Organizations (multi-account structure)
- AWS SSO / IAM Identity Center (centralized access management)
- Service Control Policies (SCPs)
- AWS Control Tower (optional governance framework)
- CloudTrail (centralized audit logging)
- AWS Config (compliance monitoring)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **SSO availability** | 99.9% | AWS SSO login success rate |
| **Account provisioning time** | < 30 minutes | Time from request to active account |
| **SCP enforcement** | 100% | Policy violations blocked |
| **User provisioning time** | < 15 minutes | Time from request to access granted |
| **Audit log completeness** | 100% | CloudTrail events captured across all accounts |
| **Compliance drift detection** | < 24 hours | Time to detect non-compliant resources |

---

## Dashboards & Alerts

### AWS Console Access Points

- **Organizations Console:** https://console.aws.amazon.com/organizations/
- **IAM Identity Center (SSO):** https://console.aws.amazon.com/singlesignon/
- **Control Tower (if enabled):** https://console.aws.amazon.com/controltower/
- **CloudTrail:** https://console.aws.amazon.com/cloudtrail/
- **AWS Config:** https://console.aws.amazon.com/config/

#### Quick Health Check
```bash
# Check organization status
aws organizations describe-organization --query 'Organization.[Id,MasterAccountEmail,AvailablePolicyTypes]'

# List all accounts
aws organizations list-accounts \
  --query 'Accounts[*].[Name,Id,Email,Status]' \
  --output table

# Check SSO instance
aws sso-admin list-instances

# Check enabled regions
aws account list-regions --region-opt-status-contains ENABLED ENABLED_BY_DEFAULT

# Check CloudTrail status (in management account)
aws cloudtrail get-trail-status --name organization-trail
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Root account login detected | Immediate | Investigate unauthorized access, rotate credentials |
| **P0** | SCP modification by unauthorized user | Immediate | Review change, rollback if malicious |
| **P0** | SSO service degradation | Immediate | Check AWS Health Dashboard, escalate to AWS Support |
| **P1** | Account provisioning failure | 30 minutes | Investigate error, retry provisioning |
| **P1** | CloudTrail logging stopped | 30 minutes | Restart trail, investigate cause |
| **P1** | AWS Config non-compliance detected | 1 hour | Review resource, remediate or document exception |
| **P2** | High IAM policy changes in 24h | 4 hours | Audit changes, verify legitimacy |
| **P2** | New service enabled in restricted OU | 4 hours | Review service usage, enforce SCP if needed |

#### CloudWatch Alarms Setup

```bash
# Create alarm for root account usage
aws cloudwatch put-metric-alarm \
  --alarm-name "RootAccountUsage" \
  --alarm-description "Alert when root account is used" \
  --metric-name "RootAccountUsage" \
  --namespace "CloudTrailMetrics" \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1 \
  --alarm-actions <SNS_TOPIC_ARN>

# Create alarm for SCP changes
aws cloudwatch put-metric-alarm \
  --alarm-name "SCPPolicyChanges" \
  --alarm-description "Alert on Service Control Policy changes" \
  --metric-name "SCPChanges" \
  --namespace "CloudTrailMetrics" \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1 \
  --alarm-actions <SNS_TOPIC_ARN>

# Create alarm for account creation
aws cloudwatch put-metric-alarm \
  --alarm-name "NewAccountCreated" \
  --alarm-description "Alert when new AWS account is created" \
  --metric-name "AccountCreated" \
  --namespace "Organizations" \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1 \
  --alarm-actions <SNS_TOPIC_ARN>
```

---

## Standard Operations

### Organization Management

#### View Organization Structure

```bash
# Get organization details
aws organizations describe-organization

# List all organizational units
aws organizations list-roots
ROOT_ID=$(aws organizations list-roots --query 'Roots[0].Id' --output text)

aws organizations list-organizational-units-for-parent --parent-id $ROOT_ID

# List all accounts
aws organizations list-accounts --output table

# View account by ID
ACCOUNT_ID="123456789012"
aws organizations describe-account --account-id $ACCOUNT_ID
```

#### Create New AWS Account

```bash
# Create account via Organizations
aws organizations create-account \
  --email "new-account@example.com" \
  --account-name "Development-App1" \
  --role-name "OrganizationAccountAccessRole" \
  --iam-user-access-to-billing ALLOW

# Check account creation status
REQUEST_ID="car-xxxxxxxxxxxxxxxxxxxxxxxx"
aws organizations describe-create-account-status --create-account-request-id $REQUEST_ID

# Wait for completion (typically 5-15 minutes)
while true; do
  STATUS=$(aws organizations describe-create-account-status \
    --create-account-request-id $REQUEST_ID \
    --query 'CreateAccountStatus.State' \
    --output text)
  echo "Account creation status: $STATUS"
  [[ $STATUS == "SUCCEEDED" ]] && break
  [[ $STATUS == "FAILED" ]] && echo "Failed!" && break
  sleep 30
done

# Get new account ID
NEW_ACCOUNT_ID=$(aws organizations describe-create-account-status \
  --create-account-request-id $REQUEST_ID \
  --query 'CreateAccountStatus.AccountId' \
  --output text)

echo "New account created: $NEW_ACCOUNT_ID"
```

#### Move Account to Different OU

```bash
# List OUs to find target OU ID
aws organizations list-organizational-units-for-parent --parent-id $ROOT_ID

# Move account
SOURCE_OU="ou-xxxx-yyyyyyyy"
DEST_OU="ou-xxxx-zzzzzzzz"
ACCOUNT_ID="123456789012"

aws organizations move-account \
  --account-id $ACCOUNT_ID \
  --source-parent-id $SOURCE_OU \
  --destination-parent-id $DEST_OU

# Verify move
aws organizations list-parents --child-id $ACCOUNT_ID
```

#### Close/Remove Account

```bash
# ⚠️ CAUTION: This is irreversible after 90 days

# Step 1: Remove account from organization (returns account to standalone)
ACCOUNT_ID="123456789012"
aws organizations remove-account-from-organization --account-id $ACCOUNT_ID

# Step 2: Close the account permanently
# (Must be done from the MANAGEMENT account, not the member account)
aws organizations close-account --account-id $ACCOUNT_ID

# Note: Account enters 90-day suspension period before permanent deletion
```

### Service Control Policies (SCPs)

#### List All SCPs

```bash
# List all policies
aws organizations list-policies --filter SERVICE_CONTROL_POLICY

# View specific policy
POLICY_ID="p-xxxxxxxx"
aws organizations describe-policy --policy-id $POLICY_ID

# View policy content
aws organizations describe-policy --policy-id $POLICY_ID \
  --query 'Policy.Content' --output text | jq '.'
```

#### Create and Attach SCP

```bash
# Example: Deny S3 Public Access
cat > deny-s3-public-access.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "s3:PutBucketPublicAccessBlock",
        "s3:PutAccountPublicAccessBlock"
      ],
      "Resource": "*",
      "Condition": {
        "Bool": {
          "s3:BlockPublicAcls": "false"
        }
      }
    }
  ]
}
EOF

# Create SCP
aws organizations create-policy \
  --name "DenyS3PublicAccess" \
  --description "Prevent S3 buckets from being made public" \
  --type SERVICE_CONTROL_POLICY \
  --content file://deny-s3-public-access.json

# Get policy ID from output
POLICY_ID="p-xxxxxxxx"

# Attach to OU or account
OU_ID="ou-xxxx-yyyyyyyy"
aws organizations attach-policy --policy-id $POLICY_ID --target-id $OU_ID

# Verify attachment
aws organizations list-policies-for-target --target-id $OU_ID --filter SERVICE_CONTROL_POLICY
```

#### Common SCP Examples

**Deny Region Restriction:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "us-east-1",
            "us-west-2"
          ]
        }
      }
    }
  ]
}
```

**Require MFA for Sensitive Actions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "ec2:TerminateInstances",
        "rds:DeleteDBInstance",
        "s3:DeleteBucket"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

**Deny Root User:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringLike": {
          "aws:PrincipalArn": "arn:aws:iam::*:root"
        }
      }
    }
  ]
}
```

### AWS SSO / IAM Identity Center Management

#### Configure SSO Users and Groups

```bash
# Get SSO instance details
SSO_INSTANCE=$(aws sso-admin list-instances --query 'Instances[0].InstanceArn' --output text)
IDENTITY_STORE_ID=$(aws sso-admin list-instances --query 'Instances[0].IdentityStoreId' --output text)

# List all users
aws identitystore list-users --identity-store-id $IDENTITY_STORE_ID

# Create new user
aws identitystore create-user \
  --identity-store-id $IDENTITY_STORE_ID \
  --user-name "john.doe" \
  --name Formatted="John Doe" GivenName="John" FamilyName="Doe" \
  --display-name "John Doe" \
  --emails Value="john.doe@example.com" Primary=true

# List groups
aws identitystore list-groups --identity-store-id $IDENTITY_STORE_ID

# Create group
aws identitystore create-group \
  --identity-store-id $IDENTITY_STORE_ID \
  --display-name "Developers" \
  --description "Development team access"

# Add user to group
GROUP_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
USER_ID="yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

aws identitystore create-group-membership \
  --identity-store-id $IDENTITY_STORE_ID \
  --group-id $GROUP_ID \
  --member-id UserId=$USER_ID
```

#### Assign SSO Access to Accounts

```bash
# List permission sets
aws sso-admin list-permission-sets --instance-arn $SSO_INSTANCE

# Create custom permission set
aws sso-admin create-permission-set \
  --instance-arn $SSO_INSTANCE \
  --name "DeveloperAccess" \
  --description "Developer access with limited permissions" \
  --session-duration "PT8H"

PERMISSION_SET_ARN=$(aws sso-admin list-permission-sets \
  --instance-arn $SSO_INSTANCE \
  --query 'PermissionSets[?contains(@, `DeveloperAccess`)]' \
  --output text)

# Attach managed policy to permission set
aws sso-admin attach-managed-policy-to-permission-set \
  --instance-arn $SSO_INSTANCE \
  --permission-set-arn $PERMISSION_SET_ARN \
  --managed-policy-arn "arn:aws:iam::aws:policy/PowerUserAccess"

# Assign permission set to user/group for specific account
aws sso-admin create-account-assignment \
  --instance-arn $SSO_INSTANCE \
  --permission-set-arn $PERMISSION_SET_ARN \
  --principal-type GROUP \
  --principal-id $GROUP_ID \
  --target-type AWS_ACCOUNT \
  --target-id "123456789012"

# Check provisioning status
aws sso-admin list-account-assignments \
  --instance-arn $SSO_INSTANCE \
  --account-id "123456789012" \
  --permission-set-arn $PERMISSION_SET_ARN
```

#### Revoke SSO Access

```bash
# Remove account assignment
aws sso-admin delete-account-assignment \
  --instance-arn $SSO_INSTANCE \
  --permission-set-arn $PERMISSION_SET_ARN \
  --principal-type GROUP \
  --principal-id $GROUP_ID \
  --target-type AWS_ACCOUNT \
  --target-id "123456789012"

# Remove user from group
aws identitystore delete-group-membership \
  --identity-store-id $IDENTITY_STORE_ID \
  --membership-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Disable user
aws identitystore update-user \
  --identity-store-id $IDENTITY_STORE_ID \
  --user-id $USER_ID \
  --operations AttributePath="Active",AttributeValue="false"
```

### CloudTrail Organization Trail

#### Create Organization-wide CloudTrail

```bash
# Create S3 bucket for logs (in management account)
BUCKET_NAME="organization-cloudtrail-logs-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Apply bucket policy
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailAclCheck",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::$BUCKET_NAME"
    },
    {
      "Sid": "AWSCloudTrailWrite",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/AWSLogs/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    }
  ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json

# Create organization trail
aws cloudtrail create-trail \
  --name organization-trail \
  --s3-bucket-name $BUCKET_NAME \
  --is-organization-trail \
  --is-multi-region-trail \
  --enable-log-file-validation

# Start logging
aws cloudtrail start-logging --name organization-trail

# Verify trail status
aws cloudtrail get-trail-status --name organization-trail
```

#### Query CloudTrail Logs

```bash
# Search for specific event
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=CreatePolicy \
  --start-time $(date -u -d '24 hours ago' +%s) \
  --max-results 50

# Search for root account usage
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=root \
  --start-time $(date -u -d '7 days ago' +%s)

# Search for failed login attempts (requires CloudWatch Logs)
aws logs filter-log-events \
  --log-group-name /aws/cloudtrail/organization-trail \
  --filter-pattern '{ $.errorCode = "*UnauthorizedOperation" || $.errorCode = "AccessDenied*" }' \
  --start-time $(date -u -d '1 hour ago' +%s)000
```

---

## Incident Response

### P0: Root Account Login Detected

**Immediate Actions (0-5 minutes):**
```bash
# 1. Verify the alert
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=root \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --max-results 10

# 2. Check what actions were performed
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=root \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --query 'Events[*].[EventTime,EventName,Username,SourceIPAddress]' \
  --output table

# 3. Check source IP location
SOURCE_IP="<IP_FROM_ABOVE>"
curl -s "https://ipapi.co/${SOURCE_IP}/json/" | jq '{ip,city,region,country,org}'

# 4. If unauthorized, immediately:
# - Contact AWS Support to lock account
# - Rotate root credentials
# - Enable MFA if not already enabled
# - Review IAM Access Analyzer findings
```

**Investigation (5-30 minutes):**
```bash
# Review all API calls made during root session
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=root \
  --start-time $(date -u -d '24 hours ago' +%s) \
  --query 'Events[*].[EventTime,EventName,EventSource,SourceIPAddress,UserAgent]' \
  --output table

# Check if MFA was used
aws iam get-account-summary | jq '.SummaryMap.AccountMFAEnabled'

# Check for new IAM users/roles created
aws iam list-users --query 'Users[?CreateDate>=`'$(date -u -d '24 hours ago' +%Y-%m-%d)'`]'
aws iam list-roles --query 'Roles[?CreateDate>=`'$(date -u -d '24 hours ago' +%Y-%m-%d)'`]'

# Check for policy changes
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=PutUserPolicy \
  --start-time $(date -u -d '24 hours ago' +%s)
```

**Mitigation:**
```bash
# 1. Force password reset (must be done via AWS Console or Support)
# 2. Delete all access keys
aws iam list-access-keys --user-name root
# (Usually returns empty for root, but check)

# 3. Enable MFA for root account (if not already enabled)
# This must be done via AWS Console

# 4. Set up CloudWatch alarm for future root usage (see Alerts section)

# 5. Review and document incident
cat > incident-root-login-$(date +%Y%m%d).md <<EOF
# Root Account Login Incident

**Date:** $(date)
**Detected By:** CloudWatch Alarm
**Source IP:** $SOURCE_IP
**Location:** <from ipapi.co>

## Timeline
- HH:MM - Alert triggered
- HH:MM - Investigation started
- HH:MM - Actions taken: <list actions>
- HH:MM - Incident closed

## Root Cause
<authorized/unauthorized usage>

## Actions Taken
- [ ] Verified source IP
- [ ] Reviewed API calls
- [ ] Rotated credentials (if needed)
- [ ] Documented legitimate use case

## Preventive Measures
- [ ] Reminded team to use IAM users/SSO
- [ ] Verified MFA enabled
- [ ] Updated runbook
EOF
```

### P0: Unauthorized SCP Modification

**Immediate Actions:**
```bash
# 1. Identify what changed
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=UpdatePolicy \
  --start-time $(date -u -d '1 hour ago' +%s)

aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=AttachPolicy \
  --start-time $(date -u -d '1 hour ago' +%s)

# 2. Get policy details
POLICY_ID="p-xxxxxxxx"
aws organizations describe-policy --policy-id $POLICY_ID

# 3. View current policy content
aws organizations describe-policy --policy-id $POLICY_ID \
  --query 'Policy.Content' --output text | jq '.'

# 4. Compare with previous version (if you have backups)
diff previous-policy.json current-policy.json

# 5. Check who made the change
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=UpdatePolicy \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --query 'Events[*].[EventTime,Username,SourceIPAddress]'
```

**Rollback:**
```bash
# If unauthorized, restore previous policy
aws organizations update-policy \
  --policy-id $POLICY_ID \
  --content file://previous-policy.json

# If malicious policy was attached, detach it
TARGET_ID="ou-xxxx-yyyyyyyy"  # or account ID
aws organizations detach-policy --policy-id $POLICY_ID --target-id $TARGET_ID

# Verify detachment
aws organizations list-policies-for-target --target-id $TARGET_ID --filter SERVICE_CONTROL_POLICY
```

### P1: SSO Login Failures

**Symptoms:**
- Users unable to log in via SSO portal
- "Access Denied" errors
- Users not seeing expected accounts

**Diagnosis:**
```bash
# 1. Check SSO service health
aws sso-admin list-instances

# 2. Verify user exists and is active
aws identitystore list-users \
  --identity-store-id $IDENTITY_STORE_ID \
  --filters AttributePath=UserName,AttributeValue="john.doe"

# 3. Check group memberships
USER_ID="yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
aws identitystore list-group-memberships-for-member \
  --identity-store-id $IDENTITY_STORE_ID \
  --member-id UserId=$USER_ID

# 4. Check account assignments
ACCOUNT_ID="123456789012"
aws sso-admin list-account-assignments \
  --instance-arn $SSO_INSTANCE \
  --account-id $ACCOUNT_ID \
  --permission-set-arn $PERMISSION_SET_ARN

# 5. Check permission set provisioning status
aws sso-admin list-account-assignments-creation-status \
  --instance-arn $SSO_INSTANCE \
  --filter Status=FAILED
```

**Resolution:**
```bash
# If user not in correct group
aws identitystore create-group-membership \
  --identity-store-id $IDENTITY_STORE_ID \
  --group-id $GROUP_ID \
  --member-id UserId=$USER_ID

# If account assignment missing
aws sso-admin create-account-assignment \
  --instance-arn $SSO_INSTANCE \
  --permission-set-arn $PERMISSION_SET_ARN \
  --principal-type USER \
  --principal-id $USER_ID \
  --target-type AWS_ACCOUNT \
  --target-id $ACCOUNT_ID

# If permission set not provisioned
aws sso-admin provision-permission-set \
  --instance-arn $SSO_INSTANCE \
  --permission-set-arn $PERMISSION_SET_ARN \
  --target-type AWS_ACCOUNT \
  --target-id $ACCOUNT_ID

# Wait for provisioning (typically 1-2 minutes)
sleep 120

# Verify user can now access
echo "User should retry login now"
```

---

## Troubleshooting

### Issue: Account Creation Stuck in "IN_PROGRESS"

**Diagnosis:**
```bash
REQUEST_ID="car-xxxxxxxxxxxxxxxxxxxxxxxx"
aws organizations describe-create-account-status --create-account-request-id $REQUEST_ID

# Check for common issues:
# 1. Email already in use
# 2. Organization limits reached
# 3. Billing information incomplete
```

**Resolution:**
```bash
# Check organization limits
aws service-quotas get-service-quota \
  --service-code organizations \
  --quota-code L-0E14C5F3  # Max accounts

# If stuck for >30 minutes, contact AWS Support
aws support create-case \
  --subject "Account creation stuck" \
  --service-code "organizations" \
  --severity-code "urgent" \
  --category-code "other" \
  --communication-body "Account creation request $REQUEST_ID stuck in IN_PROGRESS for >30 minutes"
```

### Issue: SCP Not Enforcing as Expected

**Diagnosis:**
```bash
# 1. Verify SCP is attached to correct target
TARGET_ID="ou-xxxx-yyyyyyyy"
aws organizations list-policies-for-target --target-id $TARGET_ID --filter SERVICE_CONTROL_POLICY

# 2. Check policy precedence (FullAWSAccess policy may override)
aws organizations list-policies-for-target --target-id $TARGET_ID --filter SERVICE_CONTROL_POLICY \
  --query 'Policies[*].[Name,Id]'

# 3. Verify SCP syntax
POLICY_ID="p-xxxxxxxx"
aws organizations describe-policy --policy-id $POLICY_ID \
  --query 'Policy.Content' --output text | jq '.'

# 4. Test SCP using IAM Policy Simulator
aws iam simulate-custom-policy \
  --policy-input-list file://scp-policy.json \
  --action-names "ec2:TerminateInstances" \
  --resource-arns "*"
```

**Resolution:**
```bash
# Detach conflicting policy (e.g., FullAWSAccess)
aws organizations detach-policy \
  --policy-id "p-FullAWSAccess" \
  --target-id $TARGET_ID

# Update SCP to correct syntax
aws organizations update-policy \
  --policy-id $POLICY_ID \
  --content file://corrected-policy.json

# Wait 60 seconds for policy propagation
sleep 60

# Test again
```

### Issue: CloudTrail Not Logging Events

**Diagnosis:**
```bash
# Check trail status
aws cloudtrail get-trail-status --name organization-trail

# Check if logging is enabled
aws cloudtrail get-trail-status --name organization-trail \
  --query 'IsLogging'

# Check for recent log files
BUCKET_NAME=$(aws cloudtrail get-trail --name organization-trail \
  --query 'Trail.S3BucketName' --output text)

aws s3 ls s3://$BUCKET_NAME/AWSLogs/ --recursive | tail -10

# Check CloudTrail service health
aws health describe-events \
  --filter services=CLOUDTRAIL \
  --query 'events[*].[eventTypeCode,eventDescription[0].latestDescription]'
```

**Resolution:**
```bash
# Start logging
aws cloudtrail start-logging --name organization-trail

# Verify bucket permissions
aws s3api get-bucket-policy --bucket $BUCKET_NAME

# Update bucket policy if needed (see CloudTrail setup section)

# Check CloudWatch integration (if logs going to CloudWatch)
LOG_GROUP_ARN=$(aws cloudtrail get-trail --name organization-trail \
  --query 'Trail.CloudWatchLogsLogGroupArn' --output text)

aws logs describe-log-groups --log-group-name-prefix /aws/cloudtrail/

# Create new trail if current one is broken
aws cloudtrail delete-trail --name organization-trail
# Then recreate (see setup section)
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check for failed account provisioning requests
aws organizations list-create-account-status \
  --states FAILED \
  --query 'CreateAccountStatuses[*].[RequestedTimestamp,AccountName,FailureReason]' \
  --output table

# Check for active CloudWatch alarms
aws cloudwatch describe-alarms --state-value ALARM

# Review recent root account usage (should be zero)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=root \
  --start-time $(date -u -d '24 hours ago' +%s) \
  --max-results 10

# Check SSO service health
aws sso-admin list-instances | jq -e '.Instances | length > 0' || echo "SSO unhealthy"
```

### Weekly Tasks
```bash
# Review all SCP changes
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=UpdatePolicy \
  --start-time $(date -u -d '7 days ago' +%s) \
  --query 'Events[*].[EventTime,Username,EventName]' \
  --output table

# Review new account creations
aws organizations list-accounts \
  --query 'Accounts[?JoinedTimestamp>=`'$(date -u -d '7 days ago' +%Y-%m-%d)'`]' \
  --output table

# Audit SSO permission set assignments
for ACCOUNT in $(aws organizations list-accounts --query 'Accounts[*].Id' --output text); do
  echo "Account: $ACCOUNT"
  aws sso-admin list-account-assignments \
    --instance-arn $SSO_INSTANCE \
    --account-id $ACCOUNT \
    --output table
done

# Check for AWS Config non-compliance
aws configservice describe-compliance-by-config-rule \
  --compliance-types NON_COMPLIANT \
  --query 'ComplianceByConfigRules[*].[ConfigRuleName,Compliance.ComplianceType]' \
  --output table
```

### Monthly Tasks
```bash
# Review and update SCPs
# - Check for new AWS services that need restriction
# - Review exceptions and adjust policies

# Audit all SSO users
aws identitystore list-users \
  --identity-store-id $IDENTITY_STORE_ID \
  --query 'Users[*].[UserName,DisplayName,Emails[0].Value]' \
  --output table

# Remove inactive users (last login >90 days)
# This requires custom scripting or third-party tool

# Review and rotate credentials
# - Ensure no long-term access keys in use (SSO-only access)
# - Rotate service account credentials if any exist

# Cost optimization review
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=LINKED_ACCOUNT \
  --output table

# Backup SCPs and organizational structure
mkdir -p backups/$(date +%Y%m%d)
for POLICY_ID in $(aws organizations list-policies --filter SERVICE_CONTROL_POLICY --query 'Policies[*].Id' --output text); do
  aws organizations describe-policy --policy-id $POLICY_ID \
    --query 'Policy.Content' --output text > backups/$(date +%Y%m%d)/$POLICY_ID.json
done
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 24 hours (daily SCP backups)
- **RTO** (Recovery Time Objective): 4 hours (recreate critical SCPs and account structure)

### Backup Strategy

**Daily Backups:**
```bash
# Automated backup script (run daily via cron)
#!/bin/bash
BACKUP_DIR="/backups/organizations/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup all SCPs
for POLICY_ID in $(aws organizations list-policies --filter SERVICE_CONTROL_POLICY --query 'Policies[*].Id' --output text); do
  POLICY_NAME=$(aws organizations describe-policy --policy-id $POLICY_ID --query 'Policy.Name' --output text)
  aws organizations describe-policy --policy-id $POLICY_ID > $BACKUP_DIR/${POLICY_NAME}.json
done

# Backup organizational structure
aws organizations list-roots > $BACKUP_DIR/roots.json
aws organizations list-accounts > $BACKUP_DIR/accounts.json

ROOT_ID=$(aws organizations list-roots --query 'Roots[0].Id' --output text)
aws organizations list-organizational-units-for-parent --parent-id $ROOT_ID > $BACKUP_DIR/ous.json

# Backup SSO configuration
aws sso-admin list-permission-sets --instance-arn $SSO_INSTANCE > $BACKUP_DIR/permission-sets.json

echo "Backup completed: $BACKUP_DIR"
```

### Recovery Procedures

**Scenario: SCP Accidentally Deleted**
```bash
# Restore from backup
POLICY_NAME="DenyS3PublicAccess"
BACKUP_FILE="backups/$(date -d '1 day ago' +%Y%m%d)/${POLICY_NAME}.json"

# Extract policy content and save to temp file to avoid shell expansion issues
jq -r '.Policy.Content' $BACKUP_FILE > /tmp/policy-content.json

# Recreate policy
aws organizations create-policy \
  --name $POLICY_NAME \
  --description "Restored from backup $(date)" \
  --type SERVICE_CONTROL_POLICY \
  --content file:///tmp/policy-content.json

# Cleanup temp file
rm /tmp/policy-content.json

# Reattach to original targets (requires manual identification or backup metadata)
```

---

## Operational Best Practices

### Pre-Change Checklist (SCPs, Account Creation)
- [ ] Change documented in change request
- [ ] Backup of current configuration taken
- [ ] SCP tested in non-production OU first
- [ ] Approval from security team
- [ ] Rollback plan documented
- [ ] Stakeholders notified

### Security Best Practices

**Implemented:**
- ✅ Root account MFA enabled
- ✅ Root account credentials secured in vault
- ✅ CloudTrail enabled organization-wide
- ✅ Service Control Policies for guardrails
- ✅ SSO for centralized access management
- ✅ AWS Config for compliance monitoring

**Recommended:**
- 🔒 Enable AWS GuardDuty organization-wide
- 🔒 Enable AWS Security Hub for central security findings
- 🔒 Use AWS Control Tower for additional governance
- 🔒 Implement CloudFormation StackSets for consistent deployments
- 🔒 Enable S3 Block Public Access at organization level
- 🔒 Require MFA for console access via SCP

---

## Quick Reference

### Most Common Operations
```bash
# List all accounts
aws organizations list-accounts --output table

# Create new account
aws organizations create-account \
  --email "new@example.com" \
  --account-name "NewAccount" \
  --role-name "OrganizationAccountAccessRole"

# View SCPs for account
aws organizations list-policies-for-target --target-id <ACCOUNT_ID> --filter SERVICE_CONTROL_POLICY

# Grant SSO access
aws sso-admin create-account-assignment \
  --instance-arn $SSO_INSTANCE \
  --permission-set-arn $PERMISSION_SET_ARN \
  --principal-type USER \
  --principal-id $USER_ID \
  --target-type AWS_ACCOUNT \
  --target-id $ACCOUNT_ID

# Check recent root usage
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=root \
  --start-time $(date -u -d '24 hours ago' +%s)
```

### Emergency Response
```bash
# P0: Root account login detected
aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=root --start-time $(date -u -d '1 hour ago' +%s)

# P0: Unauthorized SCP change
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=UpdatePolicy --start-time $(date -u -d '1 hour ago' +%s)

# P1: Restore SCP from backup
aws organizations create-policy --name "RestoredPolicy" --type SERVICE_CONTROL_POLICY --content file://backup.json
```

---

## References

### Internal Documentation
- [PRJ-CLOUD-001 README](./README.md)
- [SCP Policy Library](./scps/)
- [SSO Configuration Guide](./docs/sso-setup.md)

### External Resources
- [AWS Organizations Documentation](https://docs.aws.amazon.com/organizations/)
- [IAM Identity Center (SSO) Documentation](https://docs.aws.amazon.com/singlesignon/)
- [Service Control Policies Examples](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_examples.html)
- [AWS Control Tower](https://docs.aws.amazon.com/controltower/)

### Emergency Contacts
- **AWS Support:** https://console.aws.amazon.com/support/
- **On-call rotation:** See internal wiki
- **Slack channels:** #aws-operations, #security-incidents

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Cloud Platform Team
- **Review Schedule:** Quarterly or after major changes
- **Feedback:** Create issue or submit PR with updates
