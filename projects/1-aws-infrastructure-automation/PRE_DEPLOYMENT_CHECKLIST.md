# Pre-Deployment Checklist: Project 1 - AWS Infrastructure

## Purpose

This checklist ensures all prerequisites are met before deploying AWS infrastructure. Complete each section before running deployment scripts.

## 🔐 AWS Account Setup

- [ ] AWS account created and accessible
- [ ] Billing alerts configured
- [ ] Cost budget set (recommended: $200/month for dev)
- [ ] Root account MFA enabled
- [ ] IAM admin user created (not using root)
- [ ] IAM user MFA enabled

## 🛠️ Development Environment

- [ ] **Terraform installed** (>= 1.4)
  ```bash
  terraform version
  ```

- [ ] **AWS CLI installed** (>= 2.0)
  ```bash
  aws --version
  ```

- [ ] **kubectl installed** (>= 1.28)
  ```bash
  kubectl version --client
  ```

- [ ] **jq installed** (for JSON parsing)
  ```bash
  jq --version
  ```

## 🔑 AWS Credentials

- [ ] AWS credentials configured
  ```bash
  aws configure
  # OR
  export AWS_ACCESS_KEY_ID="..."
  export AWS_SECRET_ACCESS_KEY="..."
  export AWS_DEFAULT_REGION="us-west-2"
  ```

- [ ] Test AWS connectivity
  ```bash
  aws sts get-caller-identity
  ```

- [ ] Verify IAM permissions
  ```bash
  # Should show your account ID and user ARN
  aws iam get-user
  ```

## 📦 Terraform Backend Infrastructure

- [ ] **S3 bucket created**: `portfolio-tf-state`
  ```bash
  aws s3api head-bucket --bucket portfolio-tf-state 2>/dev/null
  echo $?  # Should return 0 if exists
  ```

- [ ] **Bucket versioning enabled**
  ```bash
  aws s3api get-bucket-versioning --bucket portfolio-tf-state
  # Should show: "Status": "Enabled"
  ```

- [ ] **Bucket encryption enabled**
  ```bash
  aws s3api get-bucket-encryption --bucket portfolio-tf-state
  # Should show AES256 encryption
  ```

- [ ] **DynamoDB table created**: `portfolio-tf-locks`
  ```bash
  aws dynamodb describe-table --table-name portfolio-tf-locks
  # Should return table details
  ```

### Quick Setup Script

If backend infrastructure doesn't exist, run:

```bash
# Set variables
BUCKET="portfolio-tf-state"
TABLE="portfolio-tf-locks"
REGION="us-west-2"

# Create S3 bucket
aws s3api create-bucket \
  --bucket $BUCKET \
  --region $REGION \
  --create-bucket-configuration LocationConstraint=$REGION

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket $BUCKET \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket $BUCKET \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket $BUCKET \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Create DynamoDB table
aws dynamodb create-table \
  --table-name $TABLE \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION

echo "✅ Backend infrastructure created successfully"
```

## 🔒 Database Credentials

- [ ] **Database username set**
  ```bash
  export TF_VAR_db_username="portfolio_admin"
  echo $TF_VAR_db_username  # Verify it's set
  ```

- [ ] **Database password generated** (strong, 32+ characters)
  ```bash
  # Generate secure password
  export TF_VAR_db_password="$(openssl rand -base64 32)"

  # Save to secure location (1Password, AWS Secrets Manager, etc.)
  echo $TF_VAR_db_password > .db_password
  chmod 600 .db_password

  # Add to .gitignore
  echo ".db_password" >> .gitignore
  ```

- [ ] **Credentials backed up** (stored in password manager)

## 📋 Environment Configuration

- [ ] **Environment selected** (dev, staging, production)
  ```bash
  ENVIRONMENT="dev"
  echo $ENVIRONMENT
  ```

- [ ] **Terraform variables file exists**
  ```bash
  ls -la terraform/${ENVIRONMENT}.tfvars
  ```

- [ ] **Review variable values**
  ```bash
  cat terraform/${ENVIRONMENT}.tfvars
  ```

## 🌐 Network Planning

- [ ] **VPC CIDR reviewed** (default: 10.0.0.0/16)
- [ ] **No CIDR conflicts** with existing networks
- [ ] **Availability zones confirmed** (default: us-west-2a, us-west-2b, us-west-2c)
- [ ] **Subnet design reviewed**:
  - Public: 10.0.101.0/24, 10.0.102.0/24, 10.0.103.0/24
  - Private: 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24
  - Database: 10.0.201.0/24, 10.0.202.0/24, 10.0.203.0/24

## 💰 Cost Awareness

- [ ] **Estimated costs reviewed** (~$150-200/month for dev)
- [ ] **Billing alerts configured** in AWS Console
  - Alert at $50
  - Alert at $100
  - Alert at $150

- [ ] **Cost tags confirmed** in Terraform
  ```terraform
  tags = {
    Environment = "dev"
    Project     = "portfolio"
    ManagedBy   = "terraform"
  }
  ```

- [ ] **Understand teardown process** (to stop costs)
  ```bash
  terraform destroy -var-file=dev.tfvars
  ```

## 🔍 Pre-Deployment Validation

- [ ] **Clone repository**
  ```bash
  cd projects/1-aws-infrastructure-automation
  ```

- [ ] **Review Terraform files**
  ```bash
  # Check main configuration
  cat terraform/main.tf

  # Check variables
  cat terraform/variables.tf

  # Check outputs
  cat terraform/outputs.tf
  ```

- [ ] **Terraform initialization test**
  ```bash
  cd terraform
  terraform init -backend-config=backend.hcl
  ```

- [ ] **Terraform validation**
  ```bash
  terraform validate
  # Should return: "Success! The configuration is valid."
  ```

- [ ] **Terraform format check**
  ```bash
  terraform fmt -check
  # Should return clean (no changes needed)
  ```

## 🧪 GitHub Actions CI/CD

- [ ] **Workflow file exists**
  ```bash
  cat .github/workflows/terraform.yml
  ```

- [ ] **GitHub Secrets configured** (if using CI/CD):
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `TF_VAR_db_username`
  - `TF_VAR_db_password`

## 🎯 Resource Quotas

- [ ] **Check AWS service quotas**
  ```bash
  # VPC quota
  aws service-quotas get-service-quota \
    --service-code vpc \
    --quota-code L-F678F1CE

  # EKS clusters quota
  aws service-quotas get-service-quota \
    --service-code eks \
    --quota-code L-1194D53C

  # RDS instances quota
  aws service-quotas get-service-quota \
    --service-code rds \
    --quota-code L-7B6409FD
  ```

- [ ] **Sufficient quota available**:
  - VPCs: Need 1 (quota typically 5)
  - EKS clusters: Need 1 (quota typically 100)
  - RDS instances: Need 1 (quota typically 40)

## 📝 Documentation

- [ ] **DEPLOYMENT_GUIDE.md reviewed**
  ```bash
  cat DEPLOYMENT_GUIDE.md
  ```

- [ ] **README.md reviewed**
  ```bash
  cat README.md
  ```

- [ ] **Deployment command ready**
  ```bash
  # For development
  ./scripts/deploy-terraform.sh dev

  # For production
  ./scripts/deploy-terraform.sh production
  ```

## ⚡ Final Pre-Flight Checks

- [ ] **All team members notified** (if shared AWS account)
- [ ] **Deployment window scheduled** (allow 30-45 minutes)
- [ ] **Rollback plan understood**
  ```bash
  terraform destroy -var-file=dev.tfvars
  ```

- [ ] **Monitoring ready**:
  - AWS Console open
  - CloudWatch dashboard ready
  - Terminal ready for logs

- [ ] **Support contacts available**:
  - AWS Support plan checked
  - Team chat available
  - Documentation bookmarked

## 🚀 Ready to Deploy?

If all checkboxes above are checked, you're ready to proceed:

```bash
# Set environment
cd projects/1-aws-infrastructure-automation

# Verify prerequisites one more time
./scripts/validate.sh

# Deploy
./scripts/deploy-terraform.sh dev

# Monitor deployment
# This will take approximately 20-30 minutes
# - VPC: ~2 minutes
# - EKS: ~15-20 minutes
# - RDS: ~10-15 minutes
```

## 📊 Post-Deployment Verification

After deployment completes:

- [ ] **VPC created**
  ```bash
  aws ec2 describe-vpcs --filters "Name=tag:Project,Values=portfolio"
  ```

- [ ] **EKS cluster running**
  ```bash
  aws eks describe-cluster --name portfolio-dev --query 'cluster.status'
  # Should return: "ACTIVE"
  ```

- [ ] **RDS instance available**
  ```bash
  aws rds describe-db-instances \
    --db-instance-identifier portfolio-dev \
    --query 'DBInstances[0].DBInstanceStatus'
  # Should return: "available"
  ```

- [ ] **kubectl configured**
  ```bash
  aws eks update-kubeconfig --name portfolio-dev --region us-west-2
  kubectl get nodes
  # Should show 3 nodes in Ready state
  ```

- [ ] **Database accessible** (from bastion or VPN)
  ```bash
  # Get endpoint
  terraform output -raw rds_endpoint

  # Test connection (requires network access)
  pg_isready -h <RDS_ENDPOINT> -U portfolio_admin
  ```

- [ ] **Resources tagged correctly**
  ```bash
  # Check tags
  aws resourcegroupstaggingapi get-resources \
    --tag-filters Key=Project,Values=portfolio
  ```

## 🆘 Troubleshooting

If deployment fails:

1. **Check Terraform output** for specific error
2. **Review CloudWatch logs** for EKS and RDS
3. **Verify credentials** are still valid
4. **Check AWS service health**: https://status.aws.amazon.com/
5. **Review Terraform state**:
   ```bash
   terraform show
   terraform state list
   ```
6. **Refer to DEPLOYMENT_GUIDE.md** troubleshooting section

## 📞 Emergency Rollback

If critical issues occur:

```bash
# Destroy infrastructure
cd terraform
terraform destroy -var-file=dev.tfvars

# Confirm destruction
# Type: yes
```

**Note**: S3 state bucket and DynamoDB table will remain for state preservation.

---

**Checklist completed**: __________ (Date)
**Deployed by**: __________ (Name)
**Environment**: __________ (dev/staging/production)
**Deployment duration**: __________ (minutes)
**Status**: ☐ Success  ☐ Partial  ☐ Failed
