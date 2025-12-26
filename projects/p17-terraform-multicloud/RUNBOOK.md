# Runbook — P17 (Terraform Multi-Cloud Deployment)

## Overview

Production operations runbook for multi-cloud infrastructure deployment using Terraform. This runbook covers infrastructure provisioning, state management, workspace operations, and incident response for AWS and Azure cloud environments.

**System Components:**
- Terraform configuration files (AWS and Azure modules)
- Remote state backend (S3 + DynamoDB for AWS, Azure Storage for Azure)
- Terraform workspaces (dev, staging, production)
- AWS provider (VPC, EC2, RDS)
- Azure provider (VNet, VMs, Azure SQL)
- CI/CD pipeline integration
- State locking mechanism

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Infrastructure deployment success rate** | 99% | Terraform apply completion rate |
| **State lock acquisition time** | < 5 seconds | Time to acquire state lock |
| **Drift detection frequency** | Daily | Terraform plan scheduled runs |
| **Multi-cloud deployment time** | < 20 minutes | Time from plan → apply completion |
| **State backup success rate** | 100% | Automated state backup verification |
| **Plan accuracy** | 100% match | Plan vs apply resource changes |

---

## Dashboards & Alerts

### Dashboards

#### Infrastructure Status Dashboard
```bash
# Check current infrastructure state
make status

# List all workspaces
terraform workspace list

# Show current workspace resources (AWS)
terraform state list

# Show current workspace resources (Azure)
cd azure && terraform state list

# Check resource counts
echo "AWS Resources: $(terraform state list | wc -l)"
echo "Azure Resources: $(cd azure && terraform state list | wc -l)"
```

#### Drift Detection Dashboard
```bash
# Check for infrastructure drift (AWS)
make plan-aws

# Check for infrastructure drift (Azure)
make plan-azure

# Compare current vs desired state
terraform show -json | jq '.values.root_module.resources[] | {address, type}'

# List changed resources
terraform plan -detailed-exitcode 2>&1 | grep -E "will be (created|destroyed|updated)"
```

#### State Management Dashboard
```bash
# Check state backend configuration
terraform state pull | jq '.backend'

# Verify state lock status
aws dynamodb get-item \
  --table-name terraform-lock-table \
  --key '{"LockID":{"S":"terraform-state/prod/terraform.tfstate-md5"}}' \
  --query 'Item.LockID' 2>/dev/null || echo "Not locked"

# Check state version
terraform state pull | jq '.version'

# List state backups
aws s3 ls s3://terraform-state-backup/ --recursive | tail -10
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | State file corrupted | Immediate | Restore from backup |
| **P0** | Terraform destroy in production | Immediate | Investigate, potentially restore |
| **P1** | Apply failed with errors | 30 minutes | Investigate and retry |
| **P1** | State lock held > 15 minutes | 1 hour | Force unlock if safe |
| **P2** | Drift detected in production | 2 hours | Review and apply corrections |
| **P2** | State backup failed | 4 hours | Fix backup mechanism |
| **P3** | Plan shows unexpected changes | 24 hours | Review changes before next apply |

#### Alert Queries

```bash
# Check for state lock timeout
LOCK_AGE=$(aws dynamodb get-item \
  --table-name terraform-lock-table \
  --key '{"LockID":{"S":"terraform-state/prod/terraform.tfstate-md5"}}' \
  --query 'Item.Info.S' --output text 2>/dev/null | jq -r '.Created')

if [ ! -z "$LOCK_AGE" ]; then
  NOW=$(date +%s)
  LOCK_TIME=$(date -d "$LOCK_AGE" +%s)
  LOCK_DURATION=$(( (NOW - LOCK_TIME) / 60 ))
  if [ $LOCK_DURATION -gt 15 ]; then
    echo "ALERT: State lock held for $LOCK_DURATION minutes"
  fi
fi

# Check for failed applies in last 24 hours
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=Apply \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --query 'Events[?contains(CloudTrailEvent, `"errorCode"`)].CloudTrailEvent' | grep terraform

# Monitor for unexpected resource deletions
terraform plan -json | jq -r '.resource_changes[] | select(.change.actions[] == "delete") | .address'
```

---

## Standard Operations

### Workspace Management

#### Create New Workspace
```bash
# Create workspace for new environment
terraform workspace new staging

# Verify workspace created
terraform workspace list

# Initialize workspace with backend
terraform init

# Verify backend configuration
terraform state pull | jq '.backend'
```

#### Switch Workspaces
```bash
# List available workspaces
terraform workspace list

# Switch to production workspace
terraform workspace select production

# Verify current workspace
terraform workspace show

# Show workspace resources
terraform state list
```

#### Delete Workspace
```bash
# Switch away from target workspace
terraform workspace select default

# Verify workspace is empty
terraform workspace select old-workspace
terraform state list  # Should be empty

# Delete workspace
terraform workspace select default
terraform workspace delete old-workspace

# Verify deletion
terraform workspace list
```

### Infrastructure Deployment

#### Plan Changes (AWS)
```bash
# Validate configuration
make validate

# Format Terraform files
terraform fmt -recursive

# Initialize providers
terraform init -upgrade

# Generate plan
make plan-aws

# Save plan for later apply
terraform plan -out=tfplan-aws-$(date +%Y%m%d).plan

# Review plan
terraform show tfplan-aws-*.plan | less
```

#### Apply Changes (AWS)
```bash
# Apply from saved plan
terraform apply tfplan-aws-*.plan

# Or interactive apply
make apply-aws

# Monitor apply progress
# Watch the output for:
# - Resource creation order
# - Any errors or warnings
# - Completion summary

# Verify resources created
terraform state list
aws ec2 describe-instances --filters "Name=tag:ManagedBy,Values=Terraform"
```

#### Plan Changes (Azure)
```bash
# Switch to Azure directory
cd azure/

# Validate configuration
terraform validate

# Generate plan
make plan-azure

# Save plan
terraform plan -out=tfplan-azure-$(date +%Y%m%d).plan

# Review plan
terraform show tfplan-azure-*.plan
```

#### Apply Changes (Azure)
```bash
# Apply from saved plan
terraform apply tfplan-azure-*.plan

# Or interactive apply
make apply-azure

# Verify resources created
az resource list --tag ManagedBy=Terraform --output table
```

#### Multi-Cloud Deployment
```bash
# Deploy to both clouds sequentially
make plan-aws
make apply-aws

make plan-azure
make apply-azure

# Or use orchestration script
./scripts/deploy-multicloud.sh --env=production

# Verify both deployments
terraform state list
cd azure && terraform state list && cd ..
```

### State Management

#### Pull and Inspect State
```bash
# Pull current state
terraform state pull > state-backup-local.json

# Inspect state
cat state-backup-local.json | jq '.resources[] | {type, name}'

# List all resources
terraform state list

# Show specific resource
terraform state show aws_vpc.main
```

#### Push State (Restore)
```bash
# Backup current state first
terraform state pull > state-current-backup.json

# Restore from backup
terraform state push state-backup-YYYYMMDD.json

# Verify state restored
terraform state list

# Re-sync state with actual infrastructure
terraform refresh
```

#### State Locking

```bash
# Check lock status
aws dynamodb get-item \
  --table-name terraform-lock-table \
  --key '{"LockID":{"S":"terraform-state/prod/terraform.tfstate-md5"}}'

# Force unlock (CAUTION: only if certain no apply is running)
terraform force-unlock <lock-id>

# Verify unlock
terraform plan  # Should not show lock error
```

#### Move Resources Between States
```bash
# Move resource to different state address
terraform state mv aws_instance.old_name aws_instance.new_name

# Move resource to different module
terraform state mv aws_instance.web module.web.aws_instance.web

# Import existing resource
terraform import aws_instance.imported i-1234567890abcdef0

# Remove resource from state (without destroying)
terraform state rm aws_instance.unmanaged
```

### Provider Configuration

#### Update AWS Provider
```bash
# Edit provider configuration
cat >> providers.tf << 'EOF'
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      ManagedBy = "Terraform"
      Environment = terraform.workspace
    }
  }
}
EOF

# Re-initialize with new provider version
terraform init -upgrade

# Verify provider version
terraform version
```

#### Update Azure Provider
```bash
# Edit provider configuration
cat >> providers.tf << 'EOF'
provider "azurerm" {
  features {}

  subscription_id = var.azure_subscription_id
}
EOF

# Re-initialize
terraform init -upgrade

# Verify authentication
az account show
```

### Module Management

#### Create Reusable Module
```bash
# Create module directory structure
mkdir -p modules/vpc/{main.tf,variables.tf,outputs.tf}

# Define module
cat > modules/vpc/main.tf << 'EOF'
resource "aws_vpc" "main" {
  cidr_block = var.cidr_block

  tags = {
    Name = var.name
  }
}
EOF

# Use module in root configuration
cat >> main.tf << 'EOF'
module "vpc" {
  source = "./modules/vpc"

  cidr_block = "10.0.0.0/16"
  name       = "production-vpc"
}
EOF
```

#### Update Module Version
```bash
# Update module source
sed -i 's|source = "./modules/vpc"|source = "git::https://github.com/org/modules.git//vpc?ref=v2.0.0"|' main.tf

# Re-initialize to download new module version
terraform init -upgrade

# Plan to see module changes
terraform plan
```

---

## Incident Response

### Detection

**Automated Detection:**
- Terraform apply failures (CI/CD alerts)
- State lock timeout alerts
- Drift detection reports
- Resource quota exceeded errors
- Provider authentication failures

**Manual Detection:**
```bash
# Check recent Terraform runs
./scripts/check-terraform-history.sh

# Review CloudTrail for Terraform activity (AWS)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=terraform \
  --max-results 50

# Check Azure activity logs
az monitor activity-log list \
  --resource-group production-rg \
  --caller terraform@example.com \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S)

# Check for state inconsistencies
terraform plan -detailed-exitcode
```

### Triage

#### Severity Classification

**P0: Critical Infrastructure Failure**
- State file corrupted or lost
- Accidental terraform destroy in production
- State lock corrupted preventing all operations
- Multi-cloud cascading failure

**P1: Deployment Failure**
- Terraform apply failed with errors
- Resource creation failed
- Provider authentication failure
- State lock held indefinitely

**P2: Configuration Drift**
- Unmanaged changes detected in production
- Terraform plan shows unexpected changes
- State backup failed
- Provider version mismatch

**P3: Operational Warnings**
- Deprecated resource usage warnings
- Provider deprecation notices
- Module version updates available

### Incident Response Procedures

#### P0: State File Corrupted

**Immediate Actions (0-5 minutes):**
```bash
# 1. Stop all Terraform operations immediately
echo "INCIDENT: State file corrupted - halt all deployments" | ./scripts/notify-team.sh

# 2. Verify state corruption
terraform state pull > corrupted-state.json
cat corrupted-state.json | jq . || echo "State is corrupted (invalid JSON)"

# 3. List available backups
aws s3 ls s3://terraform-state-backup/ | tail -20

# 4. Identify last known good state
aws s3 cp s3://terraform-state-backup/terraform.tfstate-$(date -d '1 hour ago' +%Y%m%d-%H) latest-backup.json

# 5. Verify backup integrity
cat latest-backup.json | jq . && echo "Backup is valid"
```

**Restoration (5-20 minutes):**
```bash
# 1. Create safety backup of corrupted state
terraform state pull > corrupted-state-$(date +%Y%m%d-%H%M%S).json

# 2. Restore from backup
terraform state push latest-backup.json

# 3. Verify restoration
terraform state list

# 4. Refresh state from actual infrastructure
terraform refresh

# 5. Verify state matches infrastructure
terraform plan  # Should show no changes or minimal drift

# 6. Document incident
cat > incidents/state-corruption-$(date +%Y%m%d).md << 'EOF'
# State Corruption Incident
**Time:** $(date)
**Duration:** 15 minutes
**Action:** Restored from backup taken 1 hour prior
**Data Loss:** None confirmed
**Root Cause:** Under investigation
EOF
```

#### P0: Accidental Destroy in Production

**Immediate Actions (0-2 minutes):**
```bash
# 1. STOP THE DESTROY IMMEDIATELY
# If still running, Ctrl+C the terraform destroy

# 2. Check what was destroyed
terraform show -json | jq '.values.root_module.resources[].address'

# 3. Lock state to prevent further changes
./scripts/emergency-lock-state.sh production
```

**Recovery (2-30 minutes):**
```bash
# 1. Pull state before destroy
aws s3 cp s3://terraform-state-backup/terraform.tfstate-pre-destroy.backup pre-destroy-state.json

# 2. Identify destroyed resources
diff <(cat pre-destroy-state.json | jq -r '.resources[].type + "." + .resources[].name') \
     <(terraform state list)

# 3. Restore infrastructure
# Option A: Restore from state backup
terraform state push pre-destroy-state.json
terraform apply

# Option B: Re-import destroyed resources
# For critical resources that still exist in cloud
terraform import aws_instance.web i-1234567890abcdef0

# 4. Verify restoration
terraform plan  # Should show infrastructure is correct

# 5. Post-incident
# Enable deletion protection on critical resources
# Implement approval workflow for destroys
# Add workspace validation to CI/CD
```

#### P1: Terraform Apply Failed

**Investigation:**
```bash
# 1. Review error output
terraform apply 2>&1 | tee apply-error-$(date +%Y%m%d-%H%M%S).log

# 2. Check resource-specific errors
terraform show -json | jq '.resource_changes[] | select(.change.actions[] == "create") | {address, error}'

# 3. Verify provider connectivity
# AWS
aws sts get-caller-identity

# Azure
az account show

# 4. Check resource quotas
# AWS
aws service-quotas list-service-quotas --service-code ec2

# Azure
az vm list-usage --location eastus
```

**Remediation:**

**Insufficient Permissions:**
```bash
# Check current permissions
aws iam get-user
aws iam list-attached-user-policies --user-name terraform-user

# Grant required permissions
aws iam attach-user-policy \
  --user-name terraform-user \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
```

**Resource Quota Exceeded:**
```bash
# Request quota increase
aws service-quotas request-service-quota-increase \
  --service-code ec2 \
  --quota-code L-1216C47A \
  --desired-value 50

# Or reduce resources in configuration
terraform apply -target=aws_instance.web[0]  # Deploy subset
```

**Dependency Error:**
```bash
# Identify dependency chain
terraform graph | dot -Tpng > dependency-graph.png

# Apply with targeted resource
terraform apply -target=aws_vpc.main
terraform apply -target=aws_subnet.private
terraform apply  # Now apply everything
```

#### P2: Configuration Drift Detected

**Investigation:**
```bash
# 1. Identify drifted resources
terraform plan -out=drift-check.plan

# 2. Show detailed drift
terraform show drift-check.plan | grep -A 10 "will be updated"

# 3. Check who made manual changes
# AWS
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=<resource-id>

# Azure
az monitor activity-log list --resource-group production-rg
```

**Remediation:**
```bash
# Option 1: Align infrastructure with Terraform
terraform apply  # Apply Terraform's desired state

# Option 2: Import manual changes into Terraform
# Update Terraform configuration to match manual changes
terraform plan  # Verify no changes needed

# Option 3: Document exception
# If manual change was intentional
./scripts/document-drift-exception.sh resource_id reason
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Terraform Infrastructure Incident

**Date:** $(date)
**Severity:** P1
**Duration:** 30 minutes
**Affected Environment:** Production

## Timeline
- 15:00: Terraform apply failed
- 15:05: Identified insufficient IAM permissions
- 15:15: Granted required permissions
- 15:20: Retry apply successful
- 15:30: Verified infrastructure healthy

## Root Cause
IAM policy updated by security team, removed required permissions

## Action Items
- [ ] Implement Terraform permission testing in CI/CD
- [ ] Add IAM policy change alerts
- [ ] Document minimum required permissions
- [ ] Create permission validation script

EOF

# Update state backup
terraform state pull > backups/post-incident-$(date +%Y%m%d).json
aws s3 cp backups/post-incident-*.json s3://terraform-state-backup/

# Review and improve automation
make test
./scripts/validate-permissions.sh
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: State Lock Timeout

**Symptoms:**
```bash
$ terraform apply
Error: Error locking state: Error acquiring the state lock: ConditionalCheckFailedException
Lock Info:
  ID:        abc-123-xyz
  Path:      terraform-state/prod/terraform.tfstate
  Operation: OperationTypeApply
  Who:       user@hostname
  Version:   1.5.0
  Created:   2025-11-10 14:00:00 UTC
```

**Diagnosis:**
```bash
# Check lock details
aws dynamodb get-item \
  --table-name terraform-lock-table \
  --key '{"LockID":{"S":"terraform-state/prod/terraform.tfstate-md5"}}' \
  --query 'Item'

# Check if locked by active process
ps aux | grep terraform
```

**Solution:**
```bash
# If terraform process is dead, force unlock
terraform force-unlock <lock-id>

# If process is alive and stuck, kill it first
kill <terraform-pid>
terraform force-unlock <lock-id>

# Verify unlock
terraform plan  # Should succeed
```

---

#### Issue: Provider Authentication Failed

**Symptoms:**
```bash
$ terraform plan
Error: error configuring Terraform AWS Provider: failed to refresh cached credentials
```

**Diagnosis:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check credential expiration
aws sts get-caller-identity --query 'UserId' || echo "Credentials expired"

# For Azure
az account show
```

**Solution:**
```bash
# AWS: Refresh credentials
aws sso login
# Or
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>

# Azure: Re-authenticate
az login

# Verify
terraform plan
```

---

#### Issue: Resource Already Exists

**Symptoms:**
```bash
$ terraform apply
Error: Error creating VPC: VpcLimitExceeded: The maximum number of VPCs has been reached
```

**Diagnosis:**
```bash
# Check if resource exists outside Terraform
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=production-vpc"

# Check Terraform state
terraform state list | grep vpc
```

**Solution:**
```bash
# Import existing resource
terraform import aws_vpc.main vpc-1234567890abcdef0

# Verify import
terraform state show aws_vpc.main

# Plan should show no changes
terraform plan
```

---

#### Issue: Module Not Found

**Symptoms:**
```bash
$ terraform init
Error: Module not found: ./modules/vpc
```

**Diagnosis:**
```bash
# Check module path
ls -la modules/vpc/

# Check module source in configuration
grep -r "source.*vpc" *.tf
```

**Solution:**
```bash
# If module moved, update source
sed -i 's|./modules/vpc|./terraform/modules/vpc|' main.tf

# If module in Git, ensure correct ref
# source = "git::https://github.com/org/modules.git//vpc?ref=v1.0.0"

# Re-initialize
terraform init

# Verify module loaded
terraform get
```

---

#### Issue: Inconsistent State

**Symptoms:**
```bash
$ terraform plan
Error: Provider produced inconsistent final plan
```

**Diagnosis:**
```bash
# Refresh state from actual infrastructure
terraform refresh

# Check for corrupted state
terraform state pull | jq . || echo "State corrupted"

# Validate configuration
terraform validate
```

**Solution:**
```bash
# Refresh state
terraform refresh

# If still failing, try targeted refresh
terraform refresh -target=aws_instance.web

# Last resort: Restore from backup
aws s3 cp s3://terraform-state-backup/latest.json backup-state.json
terraform state push backup-state.json
terraform refresh
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (automated state backups)
- **RTO** (Recovery Time Objective): 30 minutes (state restoration + infrastructure rebuild)

### Backup Strategy

**State File Backups:**
```bash
# Automated backup (pre-apply hook)
cat > .terraform.d/pre-apply.sh << 'EOF'
#!/bin/bash
BACKUP_FILE="terraform-state-$(date +%Y%m%d-%H%M%S).json"
terraform state pull > $BACKUP_FILE
aws s3 cp $BACKUP_FILE s3://terraform-state-backup/
EOF

# Manual backup
terraform state pull > manual-backup-$(date +%Y%m%d).json
aws s3 cp manual-backup-*.json s3://terraform-state-backup/manual/

# Verify backup
aws s3 ls s3://terraform-state-backup/ --recursive | tail -10
```

**Configuration Backups:**
```bash
# Version control (Git)
git add *.tf modules/
git commit -m "backup: terraform configuration $(date +%Y-%m-%d)"
git tag -a backup-$(date +%Y%m%d) -m "Daily backup"
git push --tags

# Export all resources
./scripts/export-all-resources.sh > infrastructure-export-$(date +%Y%m%d).json
```

**Provider-Specific Backups:**
```bash
# AWS: CloudFormation drift detection
aws cloudformation detect-stack-drift --stack-name terraform-managed

# Azure: Resource Group export
az group export --name production-rg > azure-resources-$(date +%Y%m%d).json
```

### Disaster Recovery Procedures

#### Complete State Loss

**Recovery Steps (30-60 minutes):**
```bash
# 1. Attempt to restore from latest backup
aws s3 cp s3://terraform-state-backup/latest.json recovered-state.json
terraform state push recovered-state.json

# 2. If no backup available, reconstruct state
# Create new empty state
terraform init -reconfigure

# 3. Import all existing resources
# List all resources that should be managed
cat infrastructure-inventory.txt | while read resource_type resource_name resource_id; do
  terraform import $resource_type.$resource_name $resource_id
done

# 4. Verify state
terraform state list

# 5. Refresh state
terraform refresh

# 6. Verify infrastructure matches configuration
terraform plan  # Should show minimal or no changes
```

#### Multi-Cloud Failure

**Recovery Steps (45-90 minutes):**
```bash
# 1. Isolate working cloud environments
# If AWS working but Azure failed
terraform workspace select production-aws-only

# 2. Restore failed cloud provider
cd azure/
terraform init -reconfigure
terraform state push <azure-state-backup>.json
terraform refresh
terraform apply

# 3. Verify cross-cloud dependencies
./scripts/verify-multicloud-connectivity.sh

# 4. Re-enable full multi-cloud operations
terraform workspace select production
terraform plan
```

### DR Drill Procedure

**Monthly DR Drill (90 minutes):**
```bash
# 1. Create test workspace
terraform workspace new dr-drill-$(date +%Y%m%d)

# 2. Simulate state loss
rm -f terraform.tfstate

# 3. Start recovery timer
START_TIME=$(date +%s)

# 4. Execute recovery procedure
aws s3 cp s3://terraform-state-backup/latest.json recovered-state.json
terraform state push recovered-state.json
terraform refresh
terraform apply

# 5. Verify infrastructure
terraform state list
make test

# 6. Calculate recovery time
END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))
echo "DR Drill Recovery Time: $RECOVERY_TIME seconds" | tee dr-drill-$(date +%Y%m%d).log

# 7. Cleanup
terraform workspace select default
terraform workspace delete dr-drill-*

# 8. Document lessons learned
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check for infrastructure drift
make plan-aws
make plan-azure

# Review state locks
./scripts/check-state-locks.sh

# Verify state backups
aws s3 ls s3://terraform-state-backup/ | tail -5

# Check provider status
terraform version
aws --version
az --version
```

### Weekly Tasks
```bash
# Update provider versions
terraform init -upgrade

# Review Terraform security advisories
./scripts/check-security-advisories.sh

# Audit resource tagging compliance
./scripts/audit-resource-tags.sh

# Review and clean up unused resources
terraform state list | ./scripts/find-unused-resources.sh
```

### Monthly Tasks
```bash
# Rotate state backend credentials
./scripts/rotate-backend-credentials.sh

# Review and optimize module versions
./scripts/check-module-updates.sh

# Conduct cost optimization review
terraform show -json | ./scripts/analyze-costs.sh

# Archive old state backups
aws s3 sync s3://terraform-state-backup/ s3://terraform-state-archive/$(date +%Y-%m)/
```

### Quarterly Tasks
```bash
# Major provider version upgrades
./scripts/upgrade-providers.sh

# Security audit of Terraform configurations
./scripts/security-audit.sh

# Review and update disaster recovery procedures
make dr-drill

# Multi-cloud cost comparison analysis
./scripts/multicloud-cost-analysis.sh
```

---

## Operational Best Practices

### Pre-Deployment Checklist
- [ ] Configuration validated (`terraform validate`)
- [ ] Plan reviewed and approved
- [ ] State backup created
- [ ] Workspace verified (`terraform workspace show`)
- [ ] Provider credentials valid
- [ ] Resource quotas checked
- [ ] Change window approved

### Post-Deployment Checklist
- [ ] Apply completed successfully
- [ ] Resources verified in cloud consoles
- [ ] State backup created
- [ ] Drift check performed (`terraform plan`)
- [ ] Monitoring updated
- [ ] Documentation updated

### Terraform Best Practices
- **Always use remote state** with locking enabled
- **Never commit sensitive values** to Git (use variables)
- **Use workspaces** for environment separation
- **Tag all resources** with ManagedBy=Terraform
- **Version pin providers** to avoid unexpected changes
- **Use modules** for reusable components
- **Run plan before apply** every time
- **Review plans carefully** especially for destroys

---

## Quick Reference

### Most Common Operations
```bash
# Validate configuration
terraform validate

# Plan changes (AWS)
make plan-aws

# Apply changes (AWS)
make apply-aws

# Plan changes (Azure)
make plan-azure

# Apply changes (Azure)
make apply-azure

# List workspaces
terraform workspace list

# Switch workspace
terraform workspace select <name>

# Show state
terraform state list

# Backup state
terraform state pull > backup.json
```

### Emergency Response
```bash
# P0: State corrupted
aws s3 cp s3://terraform-state-backup/latest.json backup.json
terraform state push backup.json

# P0: Accidental destroy
# Stop immediately (Ctrl+C)
terraform state push pre-destroy-backup.json
terraform apply

# P1: Apply failed
terraform refresh
terraform apply -target=<failed-resource>

# P1: State locked
terraform force-unlock <lock-id>
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

## Evidence & Verification

Verification summary: Baseline evidence captured to validate the latest quickstart configuration and document supporting artifacts for audits.

**Evidence artifacts**
- [Screenshot](./docs/evidence/screenshot.svg)
- [Run log](./docs/evidence/run-log.txt)
- [Dashboard export](./docs/evidence/dashboard-export.json)
- [Load test summary](./docs/evidence/load-test-summary.txt)

### Evidence Checklist

| Evidence Item | Location | Status |
| --- | --- | --- |
| Screenshot captured | `docs/evidence/screenshot.svg` | ✅ |
| Run log captured | `docs/evidence/run-log.txt` | ✅ |
| Dashboard export captured | `docs/evidence/dashboard-export.json` | ✅ |
| Load test summary captured | `docs/evidence/load-test-summary.txt` | ✅ |
