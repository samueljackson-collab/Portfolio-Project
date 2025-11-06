# SIEM Pipeline Deployment Guide

Complete step-by-step guide for deploying the AWS SIEM pipeline infrastructure.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Deployment Steps](#deployment-steps)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Cost Optimization](#cost-optimization)
- [Cleanup](#cleanup)

---

## Prerequisites

### Required Tools

- **Terraform** >= 1.6.0
- **AWS CLI** >= 2.x configured with credentials
- **Python** >= 3.9 (for Lambda function testing)
- **Bash** shell (for packaging scripts)
- **zip** utility

### AWS Account Requirements

- Active AWS account with appropriate permissions
- IAM user/role with permissions for:
  - OpenSearch Service
  - Kinesis Firehose
  - Lambda
  - VPC and networking
  - GuardDuty
  - CloudTrail
  - SNS
  - CloudWatch Logs
  - IAM role creation

### Network Prerequisites

Choose one of the following options:

**Option 1: Use Existing VPC** (Recommended)
- VPC ID
- 2-3 private subnet IDs across different AZs
- VPC CIDR block

**Option 2: Use Default VPC**
- AWS default VPC will be used automatically
- Not recommended for production

**Option 3: Create New VPC**
- Terraform will create a new VPC
- Configure CIDR blocks in variables

---

## Pre-Deployment Checklist

### 1. Clone Repository

```bash
git clone <repository-url>
cd projects/03-cybersecurity/PRJ-CYB-BLUE-001
```

### 2. Review Architecture

Read the [README.md](README.md) to understand:
- System architecture
- Data flow
- Component responsibilities
- Security model

### 3. Gather Required Information

- [ ] VPC ID (if using existing VPC)
- [ ] Subnet IDs (2-3 private subnets across AZs)
- [ ] Email address for security alerts
- [ ] Desired AWS region
- [ ] OpenSearch master password (strong, 8+ characters)
- [ ] Environment name (dev, staging, prod)

### 4. Verify AWS Credentials

```bash
aws sts get-caller-identity
```

Expected output shows your account ID, user ARN, and user ID.

### 5. Check for Existing Service-Linked Roles

```bash
aws iam get-role --role-name AWSServiceRoleForAmazonOpenSearchService 2>/dev/null
```

If this role exists, set `create_service_linked_role = false` in your tfvars.

---

## Deployment Steps

### Step 1: Package Lambda Function

Navigate to the Lambda directory and run the packaging script:

```bash
cd lambda
./package.sh
```

Expected output:
```
================================================
Lambda Deployment Package Builder
================================================
Step 1: Cleaning up old package...
Step 2: Creating temporary directory...
Step 3: Copying Lambda function...
Step 4: No requirements.txt found (using Lambda runtime packages)
Step 5: Creating ZIP package...
Step 6: Cleaning up temporary files...
================================================
✅ Package created successfully!
================================================
Package: log_transformer.zip
Size: 5.2K
```

Verify the package was created:
```bash
ls -lh log_transformer.zip
unzip -l log_transformer.zip
```

**Optional: Run Tests**

```bash
# Install test dependencies
pip install pytest boto3

# Run tests
pytest test_log_transformer.py -v
```

### Step 2: Configure Terraform Variables

Navigate to infrastructure directory:

```bash
cd ../infrastructure
```

Copy the example configuration:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```bash
nano terraform.tfvars
# or
vim terraform.tfvars
```

**Minimum required changes:**

```hcl
# General Configuration
project_name = "siem"
environment  = "dev"
aws_region   = "us-east-1"  # Your preferred region

# Network Configuration (Option 1: Existing VPC)
create_vpc      = false
use_default_vpc = false
vpc_id          = "vpc-0123456789abcdef"  # YOUR VPC ID
subnet_ids      = [
  "subnet-0abc123",  # AZ 1 private subnet
  "subnet-0def456",  # AZ 2 private subnet
  "subnet-0ghi789"   # AZ 3 private subnet
]

# Security (CRITICAL: Change these!)
opensearch_master_password = "YourStrongPassword123!"  # CHANGE ME!

# Alerting
alert_email = "security-team@yourcompany.com"  # CHANGE ME!

# Lambda Package Path
lambda_zip_path = "../lambda/log_transformer.zip"
```

**For Development/Testing:**

```hcl
# Cost-optimized configuration (~$30-50/month)
opensearch_instance_type   = "t3.small.search"
opensearch_instance_count  = 1
opensearch_zone_awareness  = false
opensearch_az_count        = 1
enable_guardduty           = true
enable_cloudtrail          = false  # Optional for dev
log_retention_days         = 3
```

**For Production:**

```hcl
# High availability configuration (~$200-400/month)
opensearch_instance_type    = "t3.medium.search"
opensearch_instance_count   = 3
opensearch_zone_awareness   = true
opensearch_az_count         = 3
opensearch_dedicated_master = true
opensearch_master_type      = "t3.small.search"
opensearch_master_count     = 3
opensearch_ebs_size         = 50
enable_guardduty            = true
enable_cloudtrail           = true
log_retention_days          = 30
```

### Step 3: Initialize Terraform

```bash
terraform init
```

Expected output:
```
Initializing modules...
Initializing the backend...
Initializing provider plugins...
- Installing hashicorp/aws v~> 5.0...
Terraform has been successfully initialized!
```

### Step 4: Plan Deployment

Review the infrastructure changes:

```bash
terraform plan -out=tfplan
```

Review the output carefully:
- Count of resources to be created
- OpenSearch domain configuration
- Kinesis Firehose setup
- Lambda function deployment
- GuardDuty and CloudTrail enablement
- SNS topic and subscriptions
- CloudWatch alarms

**Expected resource count:** ~40-60 resources depending on configuration

### Step 5: Deploy Infrastructure

Apply the Terraform plan:

```bash
terraform apply tfplan
```

**Deployment time:** 15-25 minutes (OpenSearch domain creation takes ~15 minutes)

You'll see progress for:
1. VPC resources (if creating new VPC)
2. Security groups and IAM roles
3. CloudWatch log groups
4. Lambda function
5. Kinesis Firehose delivery stream
6. **OpenSearch domain** (longest step ~15 minutes)
7. GuardDuty detector
8. CloudTrail trail
9. SNS topic and subscriptions
10. CloudWatch alarms

### Step 6: Capture Outputs

After successful deployment, save the outputs:

```bash
terraform output > deployment-outputs.txt
```

Key outputs include:
- OpenSearch Dashboard URL
- OpenSearch API endpoint
- Kinesis Firehose delivery stream name
- Lambda function ARN
- SNS topic ARN
- All CloudWatch log group names

---

## Post-Deployment Configuration

### Step 1: Confirm SNS Email Subscription

Check your email for SNS subscription confirmation:

1. Look for email from `AWS Notifications`
2. Subject: `AWS Notification - Subscription Confirmation`
3. Click the confirmation link

**Verify subscription:**

```bash
aws sns list-subscriptions-by-topic \
  --topic-arn $(terraform output -raw sns_topic_arn)
```

Status should be `Confirmed` (not `PendingConfirmation`).

### Step 2: Access OpenSearch Dashboards

Get the dashboard URL:

```bash
terraform output opensearch_dashboard_url
```

**If using VPC deployment (recommended):**

You need to access from within the VPC. Options:

**Option A: VPN/Direct Connect**
- Use your existing VPN connection to the VPC

**Option B: EC2 Bastion Host**
```bash
# Launch EC2 instance in public subnet
# SSH with port forwarding
ssh -L 9200:opensearch-endpoint:443 ec2-user@bastion-ip

# Access locally
open https://localhost:9200/_dashboards
```

**Option C: AWS Systems Manager Session Manager**
```bash
aws ssm start-session --target <instance-id> \
  --document-name AWS-StartPortForwardingSession \
  --parameters "portNumber=443,localPortNumber=9200"
```

**Login credentials:**
- Username: `admin` (or your configured master user)
- Password: (OpenSearch master password from terraform.tfvars)

### Step 3: Create Index Pattern

1. Navigate to **Management** → **Stack Management**
2. Click **Index Patterns**
3. Click **Create index pattern**
4. Enter index pattern: `security-events*`
5. Select time field: `@timestamp`
6. Click **Create index pattern**

### Step 4: Import Dashboards

Create pre-built dashboards for security monitoring:

**Dashboard 1: GuardDuty Findings**

1. Navigate to **Dashboard** → **Create dashboard**
2. Add visualizations:
   - **Severity breakdown** (pie chart): `severity.keyword`
   - **Findings over time** (line chart): `@timestamp` + count
   - **Top finding types** (bar chart): `finding_type.keyword`
   - **Affected resources** (table): `resource_type`, `resource_id`

**Dashboard 2: CloudTrail Activity**

1. Create new dashboard
2. Add visualizations:
   - **API calls over time** (line chart): `@timestamp` + count
   - **Top users** (bar chart): `user.keyword`
   - **Event types** (pie chart): `event_name.keyword`
   - **Error events** (table): filter `error_code` exists

**Dashboard 3: VPC Flow Logs**

1. Create new dashboard
2. Add visualizations:
   - **Traffic volume** (area chart): `@timestamp` + sum of `bytes`
   - **Top source IPs** (bar chart): `source_ip.keyword`
   - **Top destination ports** (bar chart): `destination_port`
   - **Rejected connections** (table): filter `action = "REJECT"`

### Step 5: Configure Alerts

Create alerts for critical security events:

**Alert 1: Critical GuardDuty Findings**

1. Navigate to **Alerting** → **Monitors**
2. Click **Create monitor**
3. Configure:
   - **Method**: Per query monitor
   - **Index**: `security-events*`
   - **Query**:
     ```json
     {
       "query": {
         "bool": {
           "must": [
             {"term": {"log_source": "guardduty"}},
             {"terms": {"severity": ["critical", "high"]}}
           ]
         }
       }
     }
     ```
   - **Trigger condition**: IS ABOVE 0
   - **Action**: Send SNS notification

**Alert 2: Unauthorized API Calls**

1. Create new monitor
2. Query for CloudTrail unauthorized errors:
   ```json
   {
     "query": {
       "bool": {
         "must": [
           {"term": {"log_source": "cloudtrail"}},
           {"term": {"error_code.keyword": "UnauthorizedOperation"}}
         ]
       }
     }
   }
   ```
3. Trigger when count > 5 in 5 minutes

**Alert 3: Unusual Network Traffic**

1. Create new monitor for VPC Flow Logs
2. Query for high traffic volume or port scanning patterns

---

## Verification

### Verify Log Ingestion

**1. Check Kinesis Firehose Metrics**

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Firehose \
  --metric-name IncomingRecords \
  --dimensions Name=DeliveryStreamName,Value=$(terraform output -raw firehose_delivery_stream_name) \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**2. Check Lambda Function Invocations**

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=$(terraform output -raw lambda_function_name) \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**3. Query OpenSearch for Events**

```bash
# Get the OpenSearch endpoint
OPENSEARCH_ENDPOINT=$(terraform output -raw opensearch_endpoint)

# Count documents (replace with your password)
curl -u admin:YourPassword123! \
  https://$OPENSEARCH_ENDPOINT/security-events/_count
```

**4. Verify GuardDuty is Active**

```bash
aws guardduty list-detectors
aws guardduty get-detector --detector-id <detector-id>
```

Status should be `ENABLED`.

**5. Check CloudTrail Logging**

```bash
aws cloudtrail get-trail-status \
  --name $(terraform output -raw cloudtrail_trail_name)
```

`IsLogging` should be `true`.

### Generate Test Events

**Test GuardDuty Detection:**

```bash
# This will trigger a GuardDuty finding (SSH brute force simulation)
# WARNING: Only run in test/dev environment!
aws ec2 describe-instances --region us-east-1 \
  --filters "Name=tag:TestGuardDuty,Values=true"
```

GuardDuty findings appear in ~15 minutes.

**Test CloudTrail Logging:**

```bash
# Any AWS API call will be logged
aws s3 ls
aws ec2 describe-vpcs
```

Events should appear in OpenSearch within 1-2 minutes.

---

## Troubleshooting

### Issue: OpenSearch Domain Status is Red

**Symptoms:**
- Dashboard shows cluster health as red
- Cannot index documents

**Solutions:**

1. **Check cluster health:**
   ```bash
   curl -u admin:password https://opensearch-endpoint/_cluster/health?pretty
   ```

2. **Review CloudWatch logs:**
   ```bash
   aws logs tail /aws/opensearch/siem-dev/application --follow
   ```

3. **Verify subnet configuration:**
   - Ensure subnets are in different AZs
   - Check subnet has available IP addresses

4. **Check security group:**
   - Verify port 443 is open from VPC CIDR

### Issue: Lambda Function Errors

**Symptoms:**
- Kinesis Firehose shows processing errors
- Logs not appearing in OpenSearch

**Solutions:**

1. **Check Lambda logs:**
   ```bash
   aws logs tail /aws/lambda/siem-dev-log-transformer --follow
   ```

2. **Verify Lambda has VPC access:**
   - Check ENI creation in CloudWatch logs
   - Ensure subnet has NAT Gateway for internet access

3. **Test Lambda function:**
   ```bash
   aws lambda invoke \
     --function-name $(terraform output -raw lambda_function_name) \
     --payload file://test-event.json \
     response.json
   ```

4. **Validate Lambda package:**
   ```bash
   cd lambda
   unzip -l log_transformer.zip
   ```

### Issue: No Logs Appearing in OpenSearch

**Symptoms:**
- OpenSearch index is empty
- Zero documents in `security-events` index

**Solutions:**

1. **Check log source configuration:**
   - Verify GuardDuty is enabled and generating findings
   - Verify CloudTrail is logging events
   - Check VPC Flow Logs are enabled

2. **Verify CloudWatch subscription filters:**
   ```bash
   aws logs describe-subscription-filters \
     --log-group-name /aws/guardduty/findings
   ```

3. **Check Firehose delivery:**
   ```bash
   aws firehose describe-delivery-stream \
     --delivery-stream-name $(terraform output -raw firehose_delivery_stream_name)
   ```

4. **Review Firehose error logs:**
   ```bash
   aws logs tail /aws/kinesisfirehose/siem-dev-siem-stream --follow
   ```

### Issue: SNS Email Not Received

**Symptoms:**
- No subscription confirmation email
- No alert emails

**Solutions:**

1. **Check SNS topic subscriptions:**
   ```bash
   aws sns list-subscriptions-by-topic \
     --topic-arn $(terraform output -raw sns_topic_arn)
   ```

2. **Verify email address:**
   - Check for typos in terraform.tfvars
   - Check spam/junk folder

3. **Manually subscribe:**
   ```bash
   aws sns subscribe \
     --topic-arn $(terraform output -raw sns_topic_arn) \
     --protocol email \
     --notification-endpoint your-email@example.com
   ```

4. **Test SNS topic:**
   ```bash
   aws sns publish \
     --topic-arn $(terraform output -raw sns_topic_arn) \
     --message "Test alert from SIEM pipeline"
   ```

### Issue: High Costs

**Symptoms:**
- AWS bill higher than expected

**Solutions:**

1. **Review OpenSearch instance type:**
   - Use t3.small.search for dev/test (~$25/month)
   - Reduce instance count for non-prod

2. **Optimize log retention:**
   - Reduce CloudWatch log retention (3-7 days for dev)
   - Configure index lifecycle management in OpenSearch

3. **Disable unused log sources:**
   - Set `enable_cloudtrail = false` if not needed
   - Disable VPC Flow Logs for dev environments

4. **Check CloudWatch Logs ingestion:**
   ```bash
   aws logs describe-log-groups --query 'logGroups[*].[logGroupName,storedBytes]' --output table
   ```

---

## Cost Optimization

### Development Environment

**Target: ~$30-50/month**

```hcl
# terraform.tfvars
opensearch_instance_type   = "t3.small.search"
opensearch_instance_count  = 1
opensearch_zone_awareness  = false
opensearch_ebs_size        = 20
enable_guardduty           = true
enable_cloudtrail          = false
log_retention_days         = 3
firehose_buffer_interval   = 900  # 15 minutes
```

**Cost breakdown:**
- OpenSearch: $25/month
- Kinesis Firehose: $5/month
- Lambda: $1-2/month
- CloudWatch: $3-5/month
- GuardDuty: $5-10/month

### Production Environment

**Target: ~$200-400/month**

```hcl
# terraform.tfvars
opensearch_instance_type    = "t3.medium.search"
opensearch_instance_count   = 3
opensearch_zone_awareness   = true
opensearch_dedicated_master = true
opensearch_ebs_size         = 50
enable_guardduty            = true
enable_cloudtrail           = true
log_retention_days          = 30
firehose_buffer_interval    = 300  # 5 minutes
```

### Cost Monitoring

Set up billing alerts:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name siem-monthly-cost-alert \
  --alarm-description "Alert when SIEM costs exceed $100" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold
```

---

## Cleanup

### Full Teardown

To completely remove all infrastructure:

```bash
# Navigate to infrastructure directory
cd infrastructure

# Destroy all resources
terraform destroy
```

**Review the destruction plan carefully!** This will delete:
- OpenSearch domain (all data will be lost)
- Kinesis Firehose delivery stream
- Lambda function
- CloudWatch log groups (all logs will be lost)
- GuardDuty detector
- CloudTrail trail
- SNS topic

**Estimated destruction time:** 10-15 minutes

### Partial Cleanup (Keep Data)

To preserve logs while removing compute resources:

1. **Export OpenSearch data:**
   ```bash
   # Create snapshot before destroying
   # (Configure S3 bucket for snapshots first)
   ```

2. **Modify Terraform to exclude data resources:**
   ```hcl
   # Add lifecycle block to log groups
   lifecycle {
     prevent_destroy = true
   }
   ```

3. **Destroy compute resources only:**
   ```bash
   terraform destroy -target=module.kinesis_firehose
   terraform destroy -target=aws_lambda_function.log_transformer
   ```

### Cost Verification

After destruction, verify no resources remain:

```bash
# Check OpenSearch domains
aws opensearch list-domain-names

# Check Kinesis streams
aws firehose list-delivery-streams

# Check Lambda functions
aws lambda list-functions | grep siem

# Check CloudWatch log groups
aws logs describe-log-groups --log-group-name-prefix /aws/opensearch/siem
```

---

## Additional Resources

### AWS Documentation

- [OpenSearch Service Best Practices](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp.html)
- [Kinesis Firehose Documentation](https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html)
- [GuardDuty User Guide](https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html)
- [CloudTrail User Guide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)

### Security Best Practices

1. **Rotate OpenSearch credentials regularly**
2. **Enable MFA for AWS account**
3. **Use AWS Secrets Manager for sensitive values**
4. **Configure OpenSearch index lifecycle management**
5. **Enable S3 bucket versioning for backups**
6. **Review GuardDuty findings daily**
7. **Set up automated responses for critical alerts**

### Performance Tuning

1. **Adjust Firehose buffer size/interval** based on log volume
2. **Tune OpenSearch shard configuration** for large datasets
3. **Configure Lambda reserved concurrency** for high-volume scenarios
4. **Enable OpenSearch UltraWarm** for cost-effective long-term storage

---

## Support

For issues or questions:

1. Review [README.md](README.md) for architecture details
2. Check [Troubleshooting](#troubleshooting) section above
3. Review AWS service health dashboard
4. Open GitHub issue with detailed error logs

**Emergency Contact:**
- Security incidents: Follow your organization's incident response plan
- Infrastructure issues: Contact DevOps/Platform team

---

**Deployment Guide Version:** 1.0
**Last Updated:** 2025-11
**Terraform Version:** >= 1.6.0
**AWS Provider Version:** ~> 5.0
