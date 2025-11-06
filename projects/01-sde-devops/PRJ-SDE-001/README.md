# AWS RDS PostgreSQL Infrastructure (PRJ-SDE-001)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Terraform](https://img.shields.io/badge/Terraform-1.6+-purple.svg)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-PostgreSQL_RDS-orange.svg)](https://aws.amazon.com/)

> **Production-ready Infrastructure as Code for AWS RDS PostgreSQL deployments with safety-first defaults**

**Author:** [Sam Jackson](https://www.linkedin.com/in/sams-jackson) | **Role:** System Development Engineer, Cloud Infrastructure
**Status:** 🟢 Production Ready | **Project ID:** PRJ-SDE-001

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [CI/CD Workflow](#cicd-workflow)
- [Configuration Guide](#configuration-guide)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

### Problem Statement

Organizations deploying AWS infrastructure manually through the console face critical challenges:

- **Configuration Drift:** Environments diverge from documented standards
- **Security Gaps:** Inconsistent security group rules, exposed resources, weak encryption
- **No Audit Trail:** Changes are undocumented and untracked
- **Slow Deployments:** Manual provisioning takes hours and is error-prone
- **Disaster Recovery:** No reliable way to recreate infrastructure from scratch

### Solution

This Terraform configuration provides **production-grade AWS RDS PostgreSQL infrastructure** with:

1. **Safety-First Defaults:** Multi-AZ enabled, deletion protection, final snapshots, and encryption by default
2. **Modular Architecture:** Reusable Terraform modules following DRY principles
3. **Security Hardening:** Private subnets, least-privilege security groups, encrypted storage
4. **Automated CI/CD:** GitHub Actions workflow with terraform plan, security scanning, and cost estimation
5. **Comprehensive Documentation:** Deployment guides, security policies, and troubleshooting resources

### Key Capabilities

- ✅ **RDS PostgreSQL Deployment:** Production-ready Multi-AZ database with automated backups
- ✅ **Safety Controls:** Deletion protection enabled, final snapshots created, maintenance windows enforced
- ✅ **Security Baseline:** Private subnets, security group isolation, AES-256 encryption at rest
- ✅ **CloudWatch Monitoring:** CPU, storage, and connection alarms with SNS notification support
- ✅ **CI/CD Automation:** Automated validation, security scanning, terraform plan on PRs
- ✅ **Cost Estimation:** Infracost integration for budget visibility

### Target Roles

This project demonstrates capabilities for:

- ☁️ **Cloud Engineer:** Terraform module development, AWS resource provisioning, CI/CD integration
- 🏗️ **Solutions Architect:** Security architecture, high availability design, cost optimization
- 🛠️ **System Development Engineer:** Infrastructure automation, operational excellence, documentation
- 🔐 **DevOps Engineer:** GitOps workflows, deployment automation, monitoring integration

---

## Architecture

### Infrastructure Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  AWS Account                                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  VPC (User-Provided or Default)                       │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │  Private Subnets (Multi-AZ)                  │    │  │
│  │  │  ┌────────────────────────────────────────┐  │    │  │
│  │  │  │  RDS PostgreSQL 15.4                   │  │    │  │
│  │  │  │  ├─ Instance: db.t3.small (default)    │  │    │  │
│  │  │  │  ├─ Storage: 20GB → 100GB (autoscale)  │  │    │  │
│  │  │  │  ├─ Encryption: AES-256 (KMS)          │  │    │  │
│  │  │  │  ├─ Multi-AZ: Enabled (HA)             │  │    │  │
│  │  │  │  ├─ Backups: 7-day retention           │  │    │  │
│  │  │  │  ├─ Deletion Protection: Enabled       │  │    │  │
│  │  │  │  └─ Final Snapshot: Auto-created       │  │    │  │
│  │  │  └────────────────────────────────────────┘  │    │  │
│  │  │                                               │    │  │
│  │  │  Security Group (app-sg)                     │    │  │
│  │  │  ├─ Ingress: Port 5432 from app tier ONLY   │    │  │
│  │  │  ├─ No public access (0.0.0.0/0 blocked)    │    │  │
│  │  │  └─ Egress: Allow outbound                  │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  CloudWatch Alarms                                          │
│  ├─ CPU Utilization > 80%                                   │
│  ├─ Free Storage < 2GB                                      │
│  └─ Database Connections > 80                               │
└─────────────────────────────────────────────────────────────┘

CI/CD Pipeline (GitHub Actions)
┌──────────────────────────────────────────────┐
│ 1. Validate → terraform fmt, validate        │
│ 2. Security Scan → tfsec                     │
│ 3. Plan (PR) → terraform plan + comment      │
│ 4. Cost Estimation → Infracost               │
│ 5. Apply (main) → terraform apply            │
└──────────────────────────────────────────────┘
```

### Security Architecture

**Defense-in-Depth Layers:**

1. **Network Isolation:**
   - Database in private subnets (or default VPC for testing)
   - No public IP addresses assigned
   - Security groups whitelist specific source groups

2. **Encryption:**
   - At rest: AES-256 via AWS KMS
   - In transit: TLS 1.2+ enforced for client connections
   - Backups: Encrypted snapshots with same KMS key

3. **Access Control:**
   - IAM roles for Terraform execution (least privilege)
   - Database credentials via environment variables (AWS Secrets Manager recommended)
   - Security group rules explicitly define allowed sources

4. **Data Protection:**
   - Automated daily backups (7-day retention default)
   - Final snapshot creation on database termination (enabled by default)
   - Deletion protection enabled by default
   - Multi-AZ deployment enabled by default

5. **Monitoring:**
   - CloudWatch alarms for CPU, storage, and connections
   - SNS notification support (configure alarm_actions)
   - VPC Flow Logs for network traffic analysis (optional)

---

## Features

### ✨ Core Capabilities

| Feature | Status | Description |
|---------|--------|-------------|
| **RDS PostgreSQL** | 🟢 Complete | Production-ready database with PostgreSQL 15.4 |
| **Multi-AZ HA** | 🟢 Enabled | Default high availability with automatic failover |
| **Deletion Protection** | 🟢 Enabled | Prevents accidental database deletion by default |
| **Final Snapshots** | 🟢 Enabled | Auto-creates snapshot before destroy by default |
| **Storage Encryption** | 🟢 Enabled | AES-256 encryption at rest (always on) |
| **Automated Backups** | 🟢 Complete | 7-day retention with point-in-time recovery |
| **Storage Autoscaling** | 🟢 Complete | Grows from 20GB to 100GB automatically |
| **CloudWatch Alarms** | 🟢 Complete | CPU, storage, and connection monitoring |
| **Security Groups** | 🟢 Complete | Least-privilege ingress rules |
| **CI/CD Workflow** | 🟢 Complete | GitHub Actions with validation and security scanning |

### 🔐 Safety Features (Production-Ready Defaults)

#### Critical Safety Controls

**1. Deletion Protection (Default: ENABLED)**
```hcl
# Production-safe default: Prevents accidental database deletion
db_deletion_protection = true

# Requires explicit override to destroy database
# Override only for ephemeral dev environments: db_deletion_protection = false
```

**2. Final Snapshot Protection (Default: ENABLED)**
```hcl
# Production-safe default: Always create final snapshot on destroy
db_skip_final_snapshot = false

# Prevents accidental data loss
# Override only when explicitly desired: db_skip_final_snapshot = true
```

**3. Multi-AZ High Availability (Default: ENABLED)**
```hcl
# Production-safe default: Automatic failover to standby instance
db_multi_az = true

# RPO: ~5 minutes | RTO: ~2 minutes (AWS managed)
# Override for non-prod to save costs: db_multi_az = false
```

**4. Maintenance Windows (Default: USE WINDOWS)**
```hcl
# Production-safe default: Apply changes during maintenance windows
db_apply_immediately = false

# Prevents unexpected downtime during business hours
# Override for dev/testing: db_apply_immediately = true
```

**5. Storage Encryption (Always Enabled)**
```hcl
# AES-256 encryption at rest (non-configurable, always enabled)
storage_encrypted = true

# Uses AWS-managed or customer-managed KMS keys
```

**6. Automated Backups**
```hcl
# Daily automated backups with 7-day retention
backup_retention_period = 7

# Configurable from 0-35 days based on compliance requirements
```

### 📊 Operational Features

- **Autoscaling Storage:** Automatically grows from 20GB to 100GB (configurable)
- **Auto Minor Version Upgrades:** Security patches applied during maintenance window
- **Configurable Apply Timing:** Choose immediate or scheduled maintenance window
- **Comprehensive Tagging:** Project, environment, managed-by tags for cost allocation
- **Sensitive Variable Protection:** Passwords marked `sensitive` in Terraform output

---

## Quick Start

### Prerequisites

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Terraform** | ≥ 1.6.0 | Infrastructure provisioning | [Download](https://www.terraform.io/downloads) |
| **AWS CLI** | ≥ 2.x | AWS API interactions | [Install Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) |
| **Git** | ≥ 2.x | Version control | [Get Git](https://git-scm.com/downloads) |

### AWS Requirements

- AWS account with permissions for: EC2, VPC, RDS, IAM
- Existing VPC with subnets (or will use default VPC)
- (Optional) S3 bucket + DynamoDB table for remote state backend

**Estimated Cost (Development Environment):**
- RDS db.t3.small (Multi-AZ): ~$70/month
- Storage (20GB): ~$5/month
- Backups: ~$3/month
- **Total:** ~$78/month

**Estimated Cost (Non-Production, Single-AZ):**
- RDS db.t3.small (Single-AZ): ~$35/month
- Storage (20GB): ~$5/month
- Backups: ~$3/month
- **Total:** ~$43/month

---

### Installation Steps

#### 1. Clone Repository

```bash
git clone https://github.com/samueljackson-collab/Portfolio-Project.git
cd Portfolio-Project/projects/01-sde-devops/PRJ-SDE-001/infrastructure
```

#### 2. Configure AWS Credentials

```bash
# Option A: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"

# Option B: AWS CLI profile
aws configure --profile terraform
export AWS_PROFILE=terraform
```

#### 3. Create Variable File

**⚠️ CRITICAL:** Never commit `terraform.tfvars` to version control!

```bash
# Copy example template
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
vim terraform.tfvars
```

**Example Development Configuration (terraform.tfvars):**
```hcl
# Project Configuration
project_name = "myapp"
environment  = "dev"

# AWS Region
aws_region = "us-east-1"

# Database Credentials
# ⚠️ Use AWS Secrets Manager in production!
db_username = "dbadmin"
db_password = "ChangeMe_SecurePassword123!"

# Instance Configuration
db_instance_class        = "db.t3.small"
db_allocated_storage     = 20
db_max_allocated_storage = 100
db_engine_version        = "15.4"

# Cost Savings for Dev (⚠️ Not production-safe!)
db_multi_az              = false  # Single-AZ for dev/test
db_deletion_protection   = false  # Allow easy cleanup
db_skip_final_snapshot   = true   # Skip snapshot for dev
db_apply_immediately     = true   # Apply changes immediately

# Backups
db_backup_retention_days = 1  # Minimal backups for dev
```

**Example Production Configuration (terraform.tfvars):**
```hcl
# Project Configuration
project_name = "myapp"
environment  = "prod"

# AWS Region
aws_region = "us-east-1"

# Database Credentials (from AWS Secrets Manager!)
db_username = "dbadmin"
db_password = var.db_password  # Retrieved from secrets manager

# Instance Configuration
db_instance_class        = "db.r6g.large"  # Production sizing
db_allocated_storage     = 100
db_max_allocated_storage = 500
db_engine_version        = "15.4"

# Production Safety Settings (defaults are already safe!)
db_multi_az              = true   # High availability
db_deletion_protection   = true   # Prevent accidental deletion
db_skip_final_snapshot   = false  # Always create final snapshot
db_apply_immediately     = false  # Use maintenance windows

# Backups
db_backup_retention_days = 14  # 2-week retention for compliance
```

#### 4. Initialize Terraform

```bash
# Initialize backend (downloads providers, sets up state)
terraform init

# Validate configuration syntax
terraform validate

# Format code to canonical style
terraform fmt -recursive
```

#### 5. Plan and Review

```bash
# Generate execution plan
terraform plan -out=tfplan

# ⚠️ CRITICAL: Review plan output carefully!
# Check:
# - Resource counts (create/update/destroy)
# - Security group rules (no 0.0.0.0/0 for database!)
# - Database settings (Multi-AZ, encryption, backups)
# - Final snapshot behavior (skip_final_snapshot = false for prod)
# - Deletion protection (enabled for prod)
```

#### 6. Apply Changes

```bash
# Apply infrastructure changes
terraform apply tfplan

# Save outputs for reference
terraform output -json > outputs.json

# Retrieve database endpoint
terraform output database_endpoint
```

#### 7. Verify Deployment

```bash
# Check RDS instance status
aws rds describe-db-instances \
  --db-instance-identifier $(terraform output -raw database_endpoint | cut -d. -f1) \
  --query 'DBInstances[0].DBInstanceStatus'

# Expected output: "available"

# Test connectivity (from allowed security group)
DB_ENDPOINT=$(terraform output -raw database_endpoint)
psql -h $DB_ENDPOINT -U dbadmin -d postgres
```

---

## Project Structure

```
projects/01-sde-devops/PRJ-SDE-001/
├── README.md                           # This file (project documentation)
│
├── .github/
│   └── workflows/
│       └── terraform-ci.yml            # CI/CD workflow (validation, plan, apply)
│
└── infrastructure/
    ├── .gitignore                      # Prevents committing secrets, state files
    ├── main.tf                         # Root Terraform configuration
    ├── variables.tf                    # Input variable definitions
    ├── outputs.tf                      # Output value definitions
    ├── terraform.tfvars.example        # Example variable values (safe to commit)
    └── terraform.tfvars                # Actual values (NEVER commit!)
```

### Key Files Explained

| File | Purpose |
|------|---------|
| `.github/workflows/terraform-ci.yml` | GitHub Actions CI/CD workflow for validation, security scanning, and deployment |
| `infrastructure/.gitignore` | Prevents committing sensitive files (`.tfstate`, `*.tfvars`, credentials) |
| `infrastructure/main.tf` | Root Terraform configuration using database module from `../../../../infrastructure/terraform/modules/database` |
| `infrastructure/variables.tf` | Variable definitions with production-safe defaults |
| `infrastructure/outputs.tf` | Output values (database endpoint, security group IDs, connection strings) |
| `infrastructure/terraform.tfvars.example` | Example configuration with production-safe defaults |
| `infrastructure/terraform.tfvars` | Actual configuration (NEVER commit to git!) |

---

## CI/CD Workflow

### GitHub Actions Automation

**Location:** `.github/workflows/terraform-ci.yml`

This project includes a production-ready GitHub Actions workflow with:

1. **Validation Job** (runs on all PRs and pushes)
   - ✅ `terraform fmt -check` (code formatting)
   - ✅ `terraform init -backend=false` (syntax check)
   - ✅ `terraform validate` (configuration validation)
   - ✅ Comments results on pull requests

2. **Security Scan Job** (runs after validation)
   - ✅ `tfsec` security scanning
   - ✅ Identifies misconfigurations (soft fail, reports issues)

3. **Terraform Plan Job** (runs on pull requests)
   - ✅ AWS credentials configuration
   - ✅ `terraform plan` with output
   - ✅ **P1 Fix:** Conditional plan file reading (only if plan succeeds)
   - ✅ **P1 Fix:** Failure notification comment (when plan fails)
   - ✅ Comments plan output on PR
   - ✅ Uploads plan artifact

4. **Terraform Apply Job** (runs on main branch pushes)
   - ✅ **Security Fix:** Depends on security-scan job
   - ✅ AWS credentials configuration
   - ✅ `terraform plan` + `terraform apply`
   - ✅ Outputs database endpoint
   - ✅ Creates deployment summary

5. **Cost Estimation Job** (runs on pull requests)
   - ✅ Infracost integration
   - ✅ Comments cost breakdown on PR
   - ✅ Budget visibility before merge

### Workflow Triggers

```yaml
on:
  push:
    branches: [main, develop]
    paths:
      - 'projects/01-sde-devops/PRJ-SDE-001/infrastructure/**'
      - 'infrastructure/terraform/modules/database/**'
  pull_request:
    branches: [main, develop]
    paths: [same as above]
  workflow_dispatch: # Manual triggers
```

### Required GitHub Secrets

Configure these secrets in your repository settings:

| Secret | Purpose | How to Create |
|--------|---------|---------------|
| `AWS_ACCESS_KEY_ID` | AWS authentication | Create IAM user with terraform permissions |
| `AWS_SECRET_ACCESS_KEY` | AWS authentication | IAM user access key |
| `DB_PASSWORD` | Database master password | Generate strong password (min 8 chars) |
| `INFRACOST_API_KEY` | Cost estimation | Register at [infracost.io](https://www.infracost.io/) |

**⚠️ Security Recommendation:** Use AWS OIDC instead of static credentials:

```yaml
# Preferred: OIDC role assumption (no static keys)
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
    aws-region: us-east-1
```

### Workflow Fixes Applied

**✅ P1 Critical Fix:**
- Added `if: steps.plan.outcome == 'success'` to prevent reading non-existent plan files
- Added failure notification step for clear error feedback
- Prevents workflow failures when terraform plan has errors

**✅ Security Enhancement:**
- Made `terraform-apply` job depend on `terraform-security-scan`
- Ensures security validation before production deployment

---

## Configuration Guide

### Variable Reference

#### Required Variables

| Variable | Type | Description |
|----------|------|-------------|
| `project_name` | string | Project identifier for resource naming (e.g., "myapp") |
| `environment` | string | Environment name: "dev", "staging", or "prod" |
| `db_username` | string | Master database username (sensitive) |
| `db_password` | string | Master database password (min 8 chars, sensitive) |

#### Optional Variables (with Production-Safe Defaults)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `aws_region` | string | `us-east-1` | AWS region for resource deployment |
| `db_instance_class` | string | `db.t3.small` | RDS instance type |
| `db_allocated_storage` | number | `20` | Initial storage in GB (20-65536) |
| `db_max_allocated_storage` | number | `100` | Maximum autoscaled storage in GB |
| `db_engine_version` | string | `15.4` | PostgreSQL engine version |
| `db_multi_az` | bool | `true` | Enable Multi-AZ (HA) deployment |
| `db_backup_retention_days` | number | `7` | Backup retention (0-35 days) |
| `db_deletion_protection` | bool | `true` | Prevent accidental database deletion |
| `db_skip_final_snapshot` | bool | `false` | Skip final snapshot on destroy (⚠️ data loss!) |
| `db_apply_immediately` | bool | `false` | Apply changes immediately vs. maintenance window |

### Output Values

After successful `terraform apply`, retrieve outputs:

```bash
# All outputs
terraform output

# Specific output (raw format)
terraform output -raw database_endpoint

# JSON format for scripting
terraform output -json > outputs.json
```

**Available Outputs:**

| Output | Description |
|--------|-------------|
| `database_endpoint` | RDS endpoint for database connections (host:port) |
| `database_security_group_id` | Security group ID attached to RDS instance |
| `app_security_group_id` | Security group ID for application servers |
| `connection_string` | PostgreSQL connection string template (password redacted) |
| `cloudwatch_alarms` | CloudWatch alarm names for monitoring |
| `next_steps` | Post-deployment instructions and important reminders |

---

## Security

### Security Best Practices

**Secrets Management:**

```hcl
# ❌ BAD: Hardcoded password in variable file
db_password = "MyPassword123"

# ✅ GOOD: Environment variable
export TF_VAR_db_password="$(aws secretsmanager get-secret-value --secret-id prod/db/password --query SecretString --output text)"

# ✅ BEST: AWS Secrets Manager integration
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/myapp/db-password"
}

locals {
  db_password = data.aws_secretsmanager_secret_version.db_password.secret_string
}
```

**Network Security:**

- ✅ Deploy databases in private subnets (no internet gateway route)
- ✅ Security groups as firewalls (least-privilege rules)
- ✅ Never allow 0.0.0.0/0 ingress to database port
- ✅ Use VPC Flow Logs for traffic analysis

**Encryption:**

- ✅ At rest: RDS (KMS), backups (same KMS key)
- ✅ In transit: TLS 1.2+ enforced for PostgreSQL connections
- ✅ Enable automatic KMS key rotation (365 days)

**IAM Least Privilege:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:CreateDBInstance",
        "rds:DescribeDBInstances",
        "rds:ModifyDBInstance",
        "rds:DeleteDBInstance",
        "rds:CreateDBSnapshot"
      ],
      "Resource": "arn:aws:rds:us-east-1:123456789012:db:myapp-*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

### Pre-Commit Checks

**Prevent secret commits with git-secrets:**

```bash
# Install git-secrets
brew install git-secrets  # macOS
apt-get install git-secrets  # Ubuntu

# Configure for repository
cd Portfolio-Project
git secrets --install
git secrets --register-aws

# Scan repository
git secrets --scan
```

**Pre-commit hooks (.git/hooks/pre-commit):**

```bash
#!/bin/bash
# Prevent committing terraform.tfvars
if git diff --cached --name-only | grep -q "terraform.tfvars$"; then
  echo "❌ ERROR: Attempted to commit terraform.tfvars (contains secrets!)"
  echo "Only commit terraform.tfvars.example"
  exit 1
fi

# Terraform formatting check
terraform fmt -check -recursive || {
  echo "❌ ERROR: Terraform files not formatted. Run: terraform fmt -recursive"
  exit 1
}

exit 0
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Terraform State Lock Error

**Symptom:**
```
Error: Error acquiring the state lock
Error message: ConditionalCheckFailedException
```

**Cause:** Another Terraform process is running, or previous run crashed.

**Solution:**
```bash
# 1. Verify no other processes
ps aux | grep terraform

# 2. If safe, force unlock
terraform force-unlock <LOCK_ID>

# 3. Retry operation
terraform apply
```

#### Issue 2: Database Connection Timeout

**Symptom:**
```
psql: error: connection to server at "myapp-dev-db.abc123.rds.amazonaws.com", port 5432 failed:
Connection timed out
```

**Troubleshooting:**

```bash
# 1. Check database status
aws rds describe-db-instances \
  --db-instance-identifier myapp-dev-db \
  --query 'DBInstances[0].[DBInstanceStatus,Endpoint.Address]' \
  --output text

# 2. Check security group rules
terraform output -raw database_security_group_id
aws ec2 describe-security-groups --group-ids <sg-id>

# 3. Verify you're connecting from allowed source
# Must be in same VPC or use VPN/bastion host

# 4. Test network connectivity
telnet myapp-dev-db.abc123.rds.amazonaws.com 5432
```

#### Issue 3: "Skip Final Snapshot" Error on Destroy

**Symptom:**
```
Error: DB Instance FinalSnapshotIdentifier is required when skip_final_snapshot is false
```

**Cause:** `skip_final_snapshot = false` but no snapshot identifier auto-generated.

**Solution:**
```bash
# This is actually expected behavior! Terraform will auto-generate snapshot ID.
# If you see this error, it's a bug. Workaround:

# Option A: Destroy with final snapshot (recommended)
terraform destroy -auto-approve

# Option B: Skip final snapshot (⚠️ DATA LOSS!)
# Edit terraform.tfvars:
db_skip_final_snapshot = true

terraform destroy -auto-approve
```

#### Issue 4: Terraform Plan Fails in GitHub Actions

**Symptom:**
```
Error: Error loading state: AccessDenied: Access Denied
```

**Cause:** GitHub Actions IAM role lacks S3 permissions for state backend.

**Solution:**
```json
// Add to IAM policy for GitHub Actions role
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject"
  ],
  "Resource": "arn:aws:s3:::terraform-state-bucket/path/to/state/*"
},
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:PutItem",
    "dynamodb:GetItem",
    "dynamodb:DeleteItem"
  ],
  "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/terraform-lock"
}
```

#### Issue 5: Database Module Not Found

**Symptom:**
```
Error: Module not found
The module address "../../../../infrastructure/terraform/modules/database" could not be resolved.
```

**Cause:** Database module doesn't exist at expected path.

**Solution:**
```bash
# Verify module exists
ls -la ../../../../infrastructure/terraform/modules/database/

# If missing, you need the shared database module
# This PRJ-SDE-001 project depends on:
# Portfolio-Project/infrastructure/terraform/modules/database/

# Ensure you have cloned the full repository:
git clone https://github.com/samueljackson-collab/Portfolio-Project.git
cd Portfolio-Project/projects/01-sde-devops/PRJ-SDE-001/infrastructure
terraform init
```

---

## Contributing

We welcome contributions! Please follow this workflow:

### Contribution Workflow

1. **Fork the repository**

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Portfolio-Project.git
   cd Portfolio-Project/projects/01-sde-devops/PRJ-SDE-001
   ```

3. **Create a feature branch:**
   ```bash
   git checkout -b feat/prj-sde-001-your-feature-name
   ```

4. **Make changes and test locally:**
   ```bash
   cd infrastructure
   terraform fmt -recursive
   terraform validate
   terraform plan

   # Optional: Run security scanning
   tfsec .
   ```

5. **Commit with conventional commits:**
   ```bash
   git add .
   git commit -m "feat(prj-sde-001): add CloudWatch dashboard module"
   ```

6. **Push and open a Pull Request:**
   ```bash
   git push origin feat/prj-sde-001-your-feature-name
   ```

7. **Address code review feedback**

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Example:**
```
fix(prj-sde-001): address terraform workflow and configuration issues

- Add conditional checks to prevent reading non-existent plan files
- Make terraform-apply job depend on security scan
- Change db_deletion_protection default to true
- Change db_multi_az default to true for HA
- Update terraform.tfvars.example with production-safe defaults
- Replace magic number with calculation for readability

Fixes: Code review issues from chatgpt-codex-connector and gemini-code-assist
```

### Code Standards

- Use `terraform fmt` (2-space indentation)
- Name resources with underscores: `aws_db_instance.this`
- Add `description` to all variables
- Mark sensitive variables with `sensitive = true`
- Include usage examples in documentation
- Production-safe defaults (enable safety controls by default)

### Pre-PR Checklist

- [ ] Code formatted: `terraform fmt -recursive`
- [ ] Validation passes: `terraform validate`
- [ ] Security scan clean: `tfsec .` (no HIGH/CRITICAL)
- [ ] Documentation updated (README, inline comments)
- [ ] Conventional commit message used
- [ ] No secrets committed (check `.gitignore`)
- [ ] Tested in AWS environment (dev/staging)

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Sam Jackson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Acknowledgments

- **HashiCorp Terraform:** Infrastructure as Code platform
- **AWS Well-Architected Framework:** Design principles and best practices
- **Terraform AWS Modules:** Community module patterns
- **GitHub Security:** Workflow security scanning and secret detection

---

## Contact & Support

**Sam Jackson**
📧 Email: contact via [LinkedIn](https://www.linkedin.com/in/sams-jackson)
💼 LinkedIn: [linkedin.com/in/sams-jackson](https://www.linkedin.com/in/sams-jackson)
🐙 GitHub: [github.com/sams-jackson](https://github.com/sams-jackson)

**Project Links:**
- **Repository:** https://github.com/samueljackson-collab/Portfolio-Project
- **Issues:** https://github.com/samueljackson-collab/Portfolio-Project/issues
- **Project Board:** https://github.com/samueljackson-collab/Portfolio-Project/projects

---

<div align="center">

**Built with 🛡️ Safety-First Design Principles**

*Production-ready infrastructure with security and reliability by default*

[⬆ Back to Top](#aws-rds-postgresql-infrastructure-prj-sde-001)

</div>
