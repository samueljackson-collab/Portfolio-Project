# COMPREHENSIVE REMEDIATION PLAN

# ================================

# Portfolio Project - Critical Issues & Fixes

# Generated: 2024-11-07

## OVERVIEW

This document provides **step-by-step fixes** for all issues identified in the code quality report.

**Total Issues:** 24 (6 Critical, 4 High, 10 Medium, 4 Low)
**Estimated Fix Time:** 25-30 hours total
**Critical Fixes Time:** 2 hours

---

## PHASE 1: CRITICAL FIXES (2 Hours - DO FIRST)

### 🔴 FIX #1: Terraform Missing Variables (60 minutes)

**Files to Modify:**

1. `terraform/variables.tf`
2. `terraform/main.tf`

**Step 1: Add Missing Variables to variables.tf**

```bash
cd /home/user/Portfolio-Project/terraform
```

Add to `variables.tf`:

```hcl
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.aws_region))
    error_message = "Must be a valid AWS region format (e.g., us-east-1)"
  }
}

variable "project_tag" {
  description = "Project tag for resource naming and cost allocation"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_tag))
    error_message = "Project tag must be lowercase alphanumeric with hyphens only"
  }
}
```

**Step 2: Create terraform.tfvars.example**

Create `terraform/terraform.tfvars.example`:

```hcl
# Copy this file to terraform.tfvars and fill in your values
# Do NOT commit terraform.tfvars to git (it's in .gitignore)

aws_region  = "us-east-1"
project_tag = "portfolio-project"

# Database configuration
db_name            = "portfoliodb"
db_username        = "admin"
# db_password set via TF_VAR_db_password environment variable

# Network configuration
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

# Application configuration
app_name           = "portfolio-app"
app_port           = 3000
app_desired_count  = 2
```

**Step 3: Verify Variables Are Used Correctly**

```bash
# Test variable references
grep -n "var.aws_region\|var.project_tag" terraform/main.tf

# Expected: Should find multiple references with correct syntax
```

---

### 🔴 FIX #2: Terraform Missing S3 Bucket Resource (10 minutes)

**File:** `terraform/main.tf`

Add this resource before the outputs section:

```hcl
# S3 bucket for application assets
resource "aws_s3_bucket" "app_assets" {
  bucket = "${var.project_tag}-app-assets-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_tag}-app-assets"
      Purpose = "Application static assets and uploads"
    }
  )
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 bucket public access block (security)
resource "aws_s3_bucket_public_access_block" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

---

### 🔴 FIX #3: Terraform Fix Output Block Structure (20 minutes)

**Current Problem:** Outputs are in main.tf with incorrect structure

**Solution: Create Proper outputs.tf**

Create `terraform/outputs.tf`:

```hcl
# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = module.vpc.public_subnet_ids
}

# Database Outputs
output "db_endpoint" {
  description = "Database endpoint"
  value       = module.database.db_endpoint
  sensitive   = true
}

output "db_name" {
  description = "Database name"
  value       = module.database.db_name
}

# Application Outputs
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.ecs_application.alb_dns_name
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs_application.cluster_name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = module.ecs_application.service_name
}

# S3 Outputs
output "app_assets_bucket_name" {
  description = "Name of the S3 bucket for application assets"
  value       = aws_s3_bucket.app_assets.id
}

output "app_assets_bucket_arn" {
  description = "ARN of the S3 bucket for application assets"
  value       = aws_s3_bucket.app_assets.arn
}

# Monitoring Outputs
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = module.ecs_application.log_group_name
}
```

**Then remove lines 150-170 from main.tf** (the malformed output block)

---

### 🔴 FIX #4: Fix deploy.sh Syntax Error (5 minutes)

**File:** `scripts/deploy.sh`
**Line:** 13

**Current (BROKEN):**

```bash
tf=terraform fmt -recursive
```

**Fixed:**

```bash
terraform fmt -recursive
```

**Full corrected section:**

```bash
echo "Formatting Terraform code..."
terraform fmt -recursive

echo "Initializing Terraform..."
terraform init

echo "Validating configuration..."
terraform validate

if [ $? -ne 0 ]; then
  echo "❌ Terraform validation failed"
  exit 1
fi
```

---

### 🔴 FIX #5: Externalize AlertManager Secrets (30 minutes)

**File:** `projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml`

**Step 1: Create Environment Variable Template**

Create `projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/.env.example`:

```bash
# AlertManager Environment Variables
# Copy to .env and fill in real values

# Email Configuration
ALERTMANAGER_SMTP_HOST=smtp.gmail.com
ALERTMANAGER_SMTP_PORT=587
ALERTMANAGER_SMTP_FROM=alerts@example.com
ALERTMANAGER_SMTP_USERNAME=alerts@example.com
ALERTMANAGER_SMTP_PASSWORD=your-app-specific-password

# Slack Configuration
ALERTMANAGER_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# PagerDuty Configuration
ALERTMANAGER_PAGERDUTY_SERVICE_KEY=your-pagerduty-integration-key
```

**Step 2: Update alertmanager.yml to Use Environment Variables**

Replace secrets section in `alertmanager.yml`:

```yaml
global:
  smtp_from: '{{ env "ALERTMANAGER_SMTP_FROM" }}'
  smtp_smarthost: '{{ env "ALERTMANAGER_SMTP_HOST" }}:{{ env "ALERTMANAGER_SMTP_PORT" }}'
  smtp_auth_username: '{{ env "ALERTMANAGER_SMTP_USERNAME" }}'
  smtp_auth_password: '{{ env "ALERTMANAGER_SMTP_PASSWORD" }}'
  smtp_require_tls: true

  slack_api_url: '{{ env "ALERTMANAGER_SLACK_WEBHOOK" }}'

# For PagerDuty receiver (line 55-57):
receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '{{ env "ALERTMANAGER_PAGERDUTY_SERVICE_KEY" }}'
        description: 'Critical alert from {{ .GroupLabels.alertname }}'
```

**Step 3: Update Docker Compose to Pass Environment Variables**

In `docker-compose-full-stack.yml`, update alertmanager service:

```yaml
alertmanager:
  image: prom/alertmanager:latest
  env_file:
    - ./alertmanager/.env  # Add this line
  environment:
    - ALERTMANAGER_SMTP_HOST=${ALERTMANAGER_SMTP_HOST}
    - ALERTMANAGER_SMTP_PASSWORD=${ALERTMANAGER_SMTP_PASSWORD}
    # ... other vars
```

---

### 🔴 FIX #6: Configure Backend (15 minutes)

**File:** `terraform/backend.tf`

**Step 1: Create Backend Setup Script**

Create `terraform/setup-backend.sh`:

```bash
#!/bin/bash
# Terraform Backend Setup Script
# This script helps configure the S3 backend for Terraform state

set -e

echo "==================================================="
echo " Terraform Backend Configuration"
echo "==================================================="
echo ""

# Prompt for values
read -p "Enter S3 bucket name for tfstate: " BUCKET_NAME
read -p "Enter AWS region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}
read -p "Enter DynamoDB table name for state locking: " TABLE_NAME

# Validate inputs
if [ -z "$BUCKET_NAME" ] || [ -z "$TABLE_NAME" ]; then
  echo "❌ Error: Bucket name and table name are required"
  exit 1
fi

echo ""
echo "Configuration:"
echo "  Bucket: $BUCKET_NAME"
echo "  Region: $AWS_REGION"
echo "  Table: $TABLE_NAME"
echo ""
read -p "Create backend configuration? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
  echo "Aborted"
  exit 0
fi

# Update backend.tf
cat > backend.tf <<EOF
terraform {
  backend "s3" {
    bucket         = "$BUCKET_NAME"
    key            = "portfolio/terraform.tfstate"
    region         = "$AWS_REGION"
    dynamodb_table = "$TABLE_NAME"
    encrypt        = true
  }
}
EOF

echo "✓ backend.tf updated"

# Create S3 bucket
echo "Creating S3 bucket..."
aws s3api create-bucket \
  --bucket "$BUCKET_NAME" \
  --region "$AWS_REGION" \
  $([ "$AWS_REGION" != "us-east-1" ] && echo "--create-bucket-configuration LocationConstraint=$AWS_REGION")

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket "$BUCKET_NAME" \
  --versioning-configuration Status=Enabled

echo "✓ S3 bucket created and versioning enabled"

# Create DynamoDB table
echo "Creating DynamoDB table..."
aws dynamodb create-table \
  --table-name "$TABLE_NAME" \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region "$AWS_REGION"

echo "✓ DynamoDB table created"

echo ""
echo "==================================================="
echo "✓ Backend configuration complete!"
echo "==================================================="
echo ""
echo "Next steps:"
echo "  1. Review backend.tf"
echo "  2. Run: terraform init"
echo "  3. Commit backend.tf to git"
echo ""
```

Make executable:

```bash
chmod +x terraform/setup-backend.sh
```

---

## PHASE 2: HIGH SEVERITY FIXES (5 Hours)

### 🟠 FIX #7: IAM Policy Placeholders (15 minutes)

**File:** `terraform/iam/github_actions_ci_policy.json`

**Step 1: Create Template Processing Script**

Create `terraform/iam/configure-iam-policy.sh`:

```bash
#!/bin/bash
# Configure IAM policy template

set -e

echo "Configuring GitHub Actions IAM Policy..."

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Prompt for values
read -p "Enter tfstate S3 bucket name: " BUCKET_NAME
read -p "Enter DynamoDB table name: " TABLE_NAME

# Process template
sed "s/REPLACE_TFSTATE_BUCKET/$BUCKET_NAME/g" \
    github_actions_ci_policy.json.template | \
sed "s/REPLACE_ACCOUNT_ID/$ACCOUNT_ID/g" | \
sed "s/REPLACE_DDB_TABLE/$TABLE_NAME/g" \
    > github_actions_ci_policy.json

echo "✓ Policy configured: github_actions_ci_policy.json"
echo ""
echo "To create in AWS:"
echo "  aws iam create-policy \\"
echo "    --policy-name GitHubActionsCI \\"
echo "    --policy-document file://github_actions_ci_policy.json"
```

**Step 2: Rename current file to template:**

```bash
cd terraform/iam
mv github_actions_ci_policy.json github_actions_ci_policy.json.template
```

---

### 🟠 FIX #8: AlertManager Template Variable (2 minutes)

**File:** `projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml`

**Line 66 - Change from:**

```yaml
*Instance:* {{ .GroupLabels.alertname }}
```

**To:**

```yaml
*Instance:* {{ .GroupLabels.instance }}
```

---

### 🟠 FIX #9: Environment Configuration (30 minutes)

**Already completed in FIX #5** - Created .env.example files

**Additional: Create Master .env.example in Repository Root**

Create `/home/user/Portfolio-Project/.env.example`:

```bash
# Portfolio Project - Master Environment Configuration
# ====================================================
# Copy to .env and fill in your values
# NEVER commit .env to git (it's in .gitignore)

# ===================
# AWS Configuration
# ===================
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
TF_VAR_aws_region=us-east-1
TF_VAR_project_tag=portfolio-project

# ===================
# Database
# ===================
TF_VAR_db_password=CHANGE_ME_STRONG_PASSWORD_32_CHARS
POSTGRES_PASSWORD=CHANGE_ME_STRONG_PASSWORD_32_CHARS

# ===================
# Monitoring
# ===================
GRAFANA_ADMIN_PASSWORD=CHANGE_ME_ADMIN_PASSWORD
ALERTMANAGER_SMTP_PASSWORD=CHANGE_ME_SMTP_APP_PASSWORD
ALERTMANAGER_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# ===================
# Services
# ===================
WIKIJS_DB_PASSWORD=CHANGE_ME_PASSWORD
HOMEASSISTANT_API_TOKEN=CHANGE_ME_TOKEN

# For complete configuration, see:
#   - projects/06-homelab/PRJ-HOME-002/assets/configs/example.env
#   - projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/.env.example
```

---

### 🟠 FIX #10: Lambda Error Handling (20 minutes)

**File:** `projects/03-cybersecurity/PRJ-CYB-BLUE-001/lambda/log_transformer.py`

**Replace lines 68-75 with:**

```python
except json.JSONDecodeError as e:
    logger.error(
        f"JSON parse error in record {record['recordId']}: {str(e)}",
        extra={
            'record_id': record['recordId'],
            'error_type': 'JSONDecodeError',
            'data_sample': record['data'][:100]  # First 100 chars
        }
    )
    output_records.append({
        'recordId': record['recordId'],
        'result': 'ProcessingFailed',
        'data': record['data']
    })

except KeyError as e:
    logger.warning(
        f"Missing required field {str(e)} in record {record['recordId']}",
        extra={
            'record_id': record['recordId'],
            'error_type': 'MissingField',
            'missing_field': str(e)
        }
    )
    # Depending on field, might want to use default value instead of failing
    output_records.append({
        'recordId': record['recordId'],
        'result': 'ProcessingFailed',
        'data': record['data']
    })

except Exception as e:
    logger.error(
        f"Unexpected error processing record {record['recordId']}: {str(e)}",
        extra={
            'record_id': record['recordId'],
            'error_type': type(e).__name__,
            'error_message': str(e)
        },
        exc_info=True  # Include full traceback
    )
    output_records.append({
        'recordId': record['recordId'],
        'result': 'ProcessingFailed',
        'data': record['data']
    })
```

---

## PHASE 3: MEDIUM SEVERITY FIXES (8 Hours)

### 🟡 FIX #11-14: Type Hints, Validation, Health Checks

**Due to length, these are documented in separate files:**

- See `REMEDIATION_PHASE3.md` for medium severity fixes
- See `REMEDIATION_PHASE4.md` for low severity fixes

---

## TESTING CHECKLIST

After applying fixes, run these tests:

### Terraform Validation

```bash
cd terraform
terraform init
terraform validate
terraform plan
```

### Python Syntax

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest tests/
```

### YAML Validation

```bash
yamllint projects/01-sde-devops/PRJ-SDE-002/assets/**/*.yml
```

### Docker Compose

```bash
docker-compose -f projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml config
```

### Shell Scripts

```bash
shellcheck scripts/*.sh
```

---

## IMPLEMENTATION ORDER

1. **Day 1 (2 hours):** Complete Phase 1 (all critical fixes)
2. **Day 2 (3 hours):** Complete Phase 2 High #7-9
3. **Day 3 (2 hours):** Complete Phase 2 High #10
4. **Week 2:** Complete Phase 3 (medium severity)
5. **Week 3:** Complete Phase 4 (low severity)
6. **Week 4:** Add integration tests and CI/CD

---

## SUCCESS CRITERIA

After Phase 1 fixes:

- ✅ Terraform validates successfully
- ✅ All Python scripts have valid syntax
- ✅ No secrets in version control
- ✅ deploy.sh executes without errors
- ✅ Backend is configurable

After All Phases:

- ✅ All 24 issues resolved
- ✅ Full test suite passes
- ✅ Complete CI/CD pipeline
- ✅ Production-ready configuration
- ✅ Comprehensive documentation

---

## NEED HELP?

For each fix, you can:

1. Follow the step-by-step instructions above
2. Use the provided code snippets
3. Run the test commands to verify
4. Check the CODE_QUALITY_REPORT.md for context

**Estimated Total Time:**

- Phase 1 (Critical): 2 hours ← **DO THIS FIRST**
- Phase 2 (High): 5 hours
- Phase 3 (Medium): 8 hours
- Phase 4 (Low): 4 hours
- **Total: 19 hours** for production-ready portfolio

---

**Last Updated:** 2024-11-07
**Next Review:** After Phase 1 completion
