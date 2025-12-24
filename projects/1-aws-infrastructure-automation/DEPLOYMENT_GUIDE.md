# Project 1: AWS Infrastructure Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the AWS infrastructure automation project using Terraform, AWS CDK, or Pulumi.

## Architecture

The infrastructure creates a production-ready AWS environment with:

- **VPC**: Multi-AZ network with public, private, and database subnets
- **EKS**: Managed Kubernetes cluster (v1.28) with autoscaling node groups
- **RDS**: PostgreSQL 15 database with automated backups and performance insights
- **Networking**: NAT Gateway, Internet Gateway, Route Tables
- **Security**: Security groups, IAM roles, encryption at rest

## Prerequisites

### 1. AWS Account Setup

- AWS account with appropriate permissions
- IAM user with admin access (or specific permissions for VPC, EKS, RDS)
- AWS CLI installed and configured
- AWS credentials configured (`aws configure`)

### 2. Terraform Backend Setup

Before deploying, create the Terraform backend infrastructure:

```bash
# Create S3 bucket for Terraform state
aws s3api create-bucket \
  --bucket portfolio-tf-state \
  --region us-west-2 \
  --create-bucket-configuration LocationConstraint=us-west-2

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket portfolio-tf-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket portfolio-tf-state \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name portfolio-tf-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-west-2
```

### 3. Tools Installation

#### Terraform
```bash
# macOS
brew install terraform

# Linux
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform
```

#### AWS CLI
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 4. Environment Variables

Set up required environment variables:

```bash
# AWS credentials (if not using AWS CLI profiles)
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# Database credentials (required)
export TF_VAR_db_username="portfolio_admin"
export TF_VAR_db_password="$(openssl rand -base64 32)"
```

## Deployment Options

### Option 1: Terraform (Recommended)

#### Development Environment

```bash
cd projects/1-aws-infrastructure-automation

# Deploy to dev environment
./scripts/deploy-terraform.sh dev
```

The script will:
1. Initialize Terraform with S3 backend
2. Validate configuration
3. Create execution plan
4. Apply changes with auto-approval

#### Production Environment

```bash
# Deploy to production (with additional safety checks)
./scripts/deploy-terraform.sh production
```

Production deployment includes:
- Multi-AZ NAT Gateways for high availability
- RDS deletion protection enabled
- 7-day backup retention
- Performance insights enabled

#### Manual Deployment

If you prefer manual control:

```bash
cd terraform

# Initialize
terraform init -backend-config=backend.hcl

# Validate
terraform validate

# Plan
terraform plan -var-file=dev.tfvars -out=plan.tfplan

# Review the plan carefully
terraform show plan.tfplan

# Apply
terraform apply plan.tfplan

# Get outputs
terraform output
```

### Option 2: AWS CDK

```bash
cd cdk

# Install dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap aws://ACCOUNT-ID/us-west-2

# Deploy
./scripts/deploy-cdk.sh dev
```

### Option 3: Pulumi

```bash
cd pulumi

# Install dependencies
pip install -r requirements.txt

# Login to Pulumi backend
pulumi login

# Select stack
pulumi stack select dev

# Deploy
./scripts/deploy-pulumi.sh dev
```

## Post-Deployment

### 1. Verify Deployment

```bash
# Check VPC
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=portfolio"

# Check EKS cluster
aws eks describe-cluster --name portfolio-dev

# Check RDS instance
aws rds describe-db-instances --db-instance-identifier portfolio-dev
```

### 2. Configure kubectl

```bash
# Update kubeconfig
aws eks update-kubeconfig --name portfolio-dev --region us-west-2

# Verify connection
kubectl get nodes
kubectl get pods --all-namespaces
```

### 3. Database Connection

```bash
# Get RDS endpoint
terraform output -raw rds_endpoint

# Connect to database (from within VPC)
psql -h <RDS_ENDPOINT> -U portfolio_admin -d portfolio
```

### 4. Monitor Resources

```bash
# EKS cluster health
aws eks describe-cluster --name portfolio-dev --query 'cluster.status'

# RDS instance status
aws rds describe-db-instances \
  --db-instance-identifier portfolio-dev \
  --query 'DBInstances[0].DBInstanceStatus'

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=portfolio-dev \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

## Cost Optimization

### Development Environment

Estimated monthly cost: **$150-200**

- VPC: Free
- EKS: $72/month (control plane)
- EC2 (3x t3.medium spot): ~$30-40/month
- RDS (db.t3.medium): ~$40-50/month
- NAT Gateway: ~$30/month
- Data transfer: ~$10/month

### Production Environment

Estimated monthly cost: **$400-500**

- VPC: Free
- EKS: $72/month
- EC2 (3x t3.medium, 50% spot): ~$80-100/month
- RDS (db.t3.medium, Multi-AZ): ~$80-100/month
- NAT Gateways (3x for HA): ~$90/month
- Data transfer: ~$30/month
- Backups: ~$20/month

### Cost Reduction Tips

1. **Use Spot Instances**: Already configured (50% on-demand, 50% spot)
2. **Right-size Resources**: Start with t3.medium, adjust based on metrics
3. **Single NAT Gateway for Dev**: Already configured (`single_nat_gateway = true` for dev)
4. **RDS Storage Autoscaling**: Configured with max 100GB
5. **Delete Dev When Not Needed**: Use `terraform destroy` for dev environments

## Maintenance

### Updates

```bash
# Update Terraform modules
terraform init -upgrade

# Update EKS cluster version
# Edit main.tf: cluster_version = "1.29"
terraform plan -var-file=dev.tfvars
terraform apply

# Update RDS engine
# Edit main.tf: engine_version = "15.5"
terraform plan -var-file=dev.tfvars
terraform apply
```

### Backups

RDS automated backups are configured:
- Backup window: 03:00-04:00 UTC
- Retention: 7 days
- Maintenance window: Monday 04:00-05:00 UTC

Manual snapshot:
```bash
aws rds create-db-snapshot \
  --db-instance-identifier portfolio-dev \
  --db-snapshot-identifier portfolio-dev-manual-$(date +%Y%m%d)
```

## Disaster Recovery

### RDS Point-in-Time Recovery

```bash
# Restore to specific time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier portfolio-dev \
  --target-db-instance-identifier portfolio-dev-restored \
  --restore-time 2025-11-10T10:00:00Z
```

### EKS Cluster Backup

```bash
# Backup cluster configuration
aws eks describe-cluster --name portfolio-dev > cluster-backup.json

# Backup kubectl resources
kubectl get all --all-namespaces -o yaml > k8s-backup.yaml
```

## Teardown

### Destroy Infrastructure

```bash
# Development
cd terraform
terraform destroy -var-file=dev.tfvars -auto-approve

# Or using script
cd ..
./scripts/deploy-terraform.sh dev destroy
```

**Warning**: Production environments have deletion protection enabled. You must first:

1. Disable RDS deletion protection:
```bash
aws rds modify-db-instance \
  --db-instance-identifier portfolio-production \
  --no-deletion-protection
```

2. Then run destroy:
```bash
terraform destroy -var-file=production.tfvars
```

## Troubleshooting

### Issue: EKS cluster creation timeout

**Solution**: EKS cluster creation can take 15-20 minutes. Increase Terraform timeout if needed.

### Issue: RDS connection failures

**Checklist**:
- Verify security group allows connection from source
- Check RDS is in correct subnet (database subnet)
- Verify credentials are correct
- Ensure connecting from within VPC or using VPN

### Issue: Terraform state locked

**Solution**:
```bash
# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

### Issue: Out of IP addresses

**Solution**: VPC CIDR provides:
- /16 = 65,536 IPs total
- 3 public subnets (/24 each) = 768 IPs
- 3 private subnets (/24 each) = 768 IPs
- 3 database subnets (/24 each) = 768 IPs

If exhausted, expand subnet CIDRs or add additional subnets.

## Security Considerations

1. **Encryption**:
   - RDS: Encryption at rest enabled
   - S3 state bucket: Server-side encryption enabled
   - EKS: Secrets encryption with KMS (recommended to add)

2. **Network Security**:
   - Database in private subnets (no internet access)
   - EKS nodes in private subnets
   - Security groups restrict access

3. **IAM**:
   - Use least-privilege IAM roles
   - Enable MFA for production deployments
   - Rotate credentials regularly

4. **Monitoring**:
   - CloudWatch metrics enabled
   - RDS Performance Insights enabled
   - Consider adding CloudTrail for audit logs

## CI/CD Integration

GitHub Actions workflow is configured at `.github/workflows/terraform.yml`:

- **On PR**: Validates and plans Terraform changes
- **On merge to main**: Automatically applies changes
- **Security scanning**: tfsec scans for security issues

## Next Steps

After infrastructure deployment:

1. **Deploy Applications**: Use EKS cluster for Projects 3-5
2. **Setup Monitoring**: Deploy Project 23 (Prometheus/Grafana)
3. **Database Migration**: Use Project 2 for database operations
4. **CI/CD**: Configure Project 3 for application deployments
5. **Security**: Implement Project 4 (DevSecOps) scanning

## Support

For issues or questions:
- Check Terraform docs: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Review AWS docs: https://docs.aws.amazon.com/
- GitHub Issues: File bug reports in repository

## Changelog

- **2025-11-10**: Initial deployment guide
- **2025-11-10**: Added cost estimates and troubleshooting section
