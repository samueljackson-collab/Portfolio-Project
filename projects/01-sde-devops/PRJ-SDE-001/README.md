# PRJ-SDE-001: Database Infrastructure Module

**Status:** 🟠 In Progress
**Category:** System Development Engineering / DevOps
**Technologies:** Terraform, AWS RDS, PostgreSQL, Infrastructure as Code

---

## Overview

This project contains Terraform infrastructure code for provisioning and managing a production-ready PostgreSQL database on AWS RDS with security hardening, backup automation, and high availability.

## What's Implemented

### ✅ RDS Database Module (`infrastructure/terraform/modules/database/`)

A reusable Terraform module that provisions:

- **RDS PostgreSQL Instance** with configurable engine version (default: 15.4)
- **Security Group** with dynamic ingress rules for application access
- **DB Subnet Group** for multi-AZ deployment
- **Storage Encryption** enabled by default
- **Automated Backups** with configurable retention (default: 7 days)
- **Auto-scaling Storage** with configurable min/max limits
- **Multi-AZ Deployment** support for high availability
- **Deletion Protection** configurable for production safety

### Key Security Features

1. **No Public Access** - `publicly_accessible = false`
2. **Encrypted at Rest** - `storage_encrypted = true`
3. **Sensitive Variables** - Password marked as sensitive
4. **Security Group Rules** - Port 5432 restricted to specific security groups only
5. **Final Snapshot Control** - Prevents accidental data loss with `skip_final_snapshot = false` default

### Configurable Variables

The module accepts 18 input variables including:
- Project name and environment
- Database credentials (managed securely)
- Network configuration (VPC, subnets, security groups)
- Instance sizing (class, storage)
- HA and backup settings
- Safety controls (deletion protection, snapshot behavior)
- Resource tags

See: [main.tf](../../../infrastructure/terraform/modules/database/main.tf)

### Outputs

- `db_endpoint` - Database connection endpoint
- `db_security_group_id` - Security group ID for application access

## Usage

### 1. Configure Variables

Copy the example configuration:
```bash
cp examples/terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:
```hcl
project_name = "my-project"
environment  = "production"
db_username  = "dbadmin"
db_password  = "RETRIEVE_FROM_SECRETS_MANAGER"
vpc_id       = "vpc-xxxxx"
subnet_ids   = ["subnet-xxxxx", "subnet-yyyyy"]
```

**IMPORTANT:** Never commit `terraform.tfvars` - it's excluded by `.gitignore`

### 2. Initialize Terraform

```bash
cd infrastructure/terraform
terraform init
```

### 3. Plan and Apply

```bash
terraform plan -out=tfplan
terraform apply tfplan
```

### 4. Retrieve Database Endpoint

```bash
terraform output db_endpoint
```

## What's Still Needed

This module is functional but the project needs:

- [ ] **Root Terraform Configuration** - Main module to orchestrate database and other infrastructure
- [ ] **VPC Module** - Network infrastructure (VPC, subnets, route tables, NAT gateway)
- [ ] **Application Module** - Compute resources (ECS, EC2, Lambda) that use the database
- [ ] **Monitoring Module** - CloudWatch alarms, dashboards for database metrics
- [ ] **Backup Verification** - Automated restore testing scripts
- [ ] **State Backend Configuration** - S3 + DynamoDB for remote state
- [ ] **CI/CD Pipeline** - GitHub Actions workflow for terraform plan/apply
- [ ] **Multi-Environment Setup** - Dev/Staging/Prod workspace configuration
- [ ] **Architecture Diagrams** - Visual documentation of infrastructure design

## Architecture

### Current State

```
┌─────────────────────────────────────┐
│      AWS RDS PostgreSQL             │
│  ┌───────────────────────────────┐  │
│  │  Database Instance            │  │
│  │  - Encrypted Storage          │  │
│  │  - Multi-AZ (optional)        │  │
│  │  - Automated Backups          │  │
│  └───────────────────────────────┘  │
│             ▲                        │
│             │ Port 5432              │
│  ┌──────────┴──────────────────┐    │
│  │   Security Group            │    │
│  │   - Ingress from App SGs    │    │
│  └─────────────────────────────┘    │
│                                      │
│  ┌─────────────────────────────┐    │
│  │   DB Subnet Group           │    │
│  │   - Private Subnets         │    │
│  │   - Multi-AZ Placement      │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

### Planned Future State

```
┌───────────────────────────────────────────────┐
│            AWS Infrastructure                 │
│                                               │
│  ┌─────────────────┐    ┌─────────────────┐  │
│  │  Application    │───→│   RDS Database  │  │
│  │  (ECS/EC2)      │    │   (PostgreSQL)  │  │
│  └─────────────────┘    └─────────────────┘  │
│         │                       │             │
│         │                       │             │
│  ┌──────┴───────────────────────┴──────────┐  │
│  │        Monitoring & Alerting            │  │
│  │  (CloudWatch, SNS, Alarms)              │  │
│  └─────────────────────────────────────────┘  │
│                                               │
│  ┌─────────────────────────────────────────┐  │
│  │         VPC Network                     │  │
│  │  (Subnets, NACLs, Route Tables)         │  │
│  └─────────────────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

## Testing

### Local Validation

```bash
# Format check
terraform fmt -check -recursive

# Validation
terraform init -backend=false
terraform validate

# Security scanning
tflint
tfsec .
```

### Cost Estimation

```bash
# Using Infracost (if installed)
infracost breakdown --path .
```

## Best Practices Demonstrated

1. **Modular Design** - Reusable module with clear inputs/outputs
2. **Security Defaults** - Encryption, private access, security groups
3. **Configuration Over Hardcoding** - All settings exposed as variables
4. **Safe Destruction** - Final snapshots prevent data loss
5. **Documentation** - Inline comments and comprehensive README
6. **Tagging Strategy** - Consistent resource tagging with merge()
7. **Name Sanitization** - Handles special characters in resource names
8. **Sensitive Data Handling** - Password marked sensitive in output

## Related Documentation

- [GitHub Setup Guide](../../../docs/github-repository-setup-guide.md)
- [Security Documentation](../../../docs/security.md)
- [Deployment Guide](../../../DEPLOYMENT.md)
- [Release Notes v0.1.0](../../../RELEASE_NOTES.md)

## Lessons Learned

### What Went Well
- Module design is flexible and reusable
- Security group rules use dynamic blocks for scalability
- Variables provide good balance between flexibility and safe defaults

### What Could Be Improved
- Need integration tests with Terratest
- Should add CloudWatch alarms for database metrics
- Consider adding read replicas for scaling reads
- Add parameter groups for PostgreSQL tuning

## Future Enhancements

1. **Add Read Replicas** - For read-heavy workloads
2. **Parameter Groups** - Custom PostgreSQL configuration
3. **Option Groups** - Advanced database features
4. **IAM Authentication** - Enhanced security over password auth
5. **Performance Insights** - Database performance monitoring
6. **Automated Snapshots Export** - S3 export for long-term retention
7. **Blue/Green Deployments** - Zero-downtime major version upgrades

---

**Project Lead:** Sam Jackson
**Last Updated:** October 28, 2025
**Terraform Version:** >= 1.6.x
**AWS Provider:** >= 5.0
