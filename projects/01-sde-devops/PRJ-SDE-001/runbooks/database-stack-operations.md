# CloudFormation-Style Runbook · Terraform RDS PostgreSQL Stack

## Purpose & When to Use
Use this runbook to deploy, update, test, scale, and retire the PRJ-SDE-001 Amazon RDS PostgreSQL infrastructure. Follow it whenever:
- Launching a new environment (dev, staging, prod).
- Applying configuration updates or parameter changes.
- Executing controlled failover or resiliency testing.
- Performing capacity scaling (compute, storage, or replicas).
- Managing backup/restore workflows.
- Hardening security posture or rotating credentials.
- Decommissioning environments with audit evidence.

Each procedure includes prerequisites, execution time, rollback, and verification guidance.

---

## Prerequisites
- **Tooling:** Terraform 1.6+, AWS CLI 2.13+, `jq` 1.6, `psql` 15 client.
- **Access:** IAM role `arn:aws:iam::123456789012:role/terraform-deploy-prod` (adjust per environment) with permissions outlined in the project README.
- **State:** Remote state S3 bucket and DynamoDB table created (`terraform-state-prod`, `terraform-locks`).
- **Secrets:** Database credentials stored in AWS Secrets Manager (`prod/app/db/master`).
- **Network:** Confirm VPC and subnets meet requirements (two private subnets, NAT access for patching).
- **Monitoring:** CloudWatch alarms enabled for CPU, storage, connections.
- **Change Management:** Approved change request or maintenance window for staging/prod.

Pre-checks before any operation:
```bash
cd infrastructure/terraform/stacks/database
aws sts get-caller-identity
terraform fmt -check
terraform validate
```
If the format or validation commands fail, resolve configuration issues before proceeding.

---

## Procedure 1: Deploy New Database (10-15 minutes)
1. **Prepare Variables (2 min)**
   ```bash
   cp examples/production.tfvars.example prod.tfvars
   export TF_VAR_db_password=$(aws secretsmanager get-secret-value \
     --secret-id prod/app/db/master \
     --query 'SecretString' --output text | jq -r '.password')
   ```
2. **Plan Deployment (4 min)**
   ```bash
   terraform init \
     -backend-config="bucket=terraform-state-prod" \
     -backend-config="key=database/prod/terraform.tfstate" \
     -backend-config="dynamodb_table=terraform-locks" \
     -backend-config="region=us-west-2"
   terraform plan -var-file=prod.tfvars -out=plan.out
   ```
   Review `plan.out` for resource count: `3 to add, 0 to change, 0 to destroy`.
3. **Apply (4 min)**
   ```bash
   terraform apply plan.out
   ```
   Expected output: `Apply complete! Resources: 3 added, 0 changed, 0 destroyed.`
4. **Validate (3 min)**
   ```bash
   aws rds describe-db-instances --db-instance-identifier prod-app-db \
     --query 'DBInstances[0].{Status:DBInstanceStatus,MultiAZ:MultiAZ}'
   ```
   Ensure `Status` = `available` and `MultiAZ` = `true`.
5. **Post-Deployment**
   - Record endpoint and security group ID from Terraform outputs.
   - Update application secret store with connection string.
   - Notify stakeholders via Slack `#platform-changes` with deployment summary.

Rollback: `terraform destroy -var-file=prod.tfvars` (non-prod). For prod, open incident ticket and restore latest snapshot.

---

## Procedure 2: Update Existing Database (20-30 minutes)
1. **Impact Assessment**
   - Pull latest main branch.
   - Run `terraform plan -var-file=prod.tfvars` and export to `plan.txt` for review.
   - Check for modifications to storage, engine version, or `apply_immediately`. Flag risky items for CAB approval.
2. **Approval Workflow**
   - Submit plan summary to Change Advisory Board (CAB) with diff excerpt.
   - Obtain two reviewer approvals for production.
3. **Execute Update**
   ```bash
   terraform apply -var-file=prod.tfvars
   ```
   Monitor console logs for `modifying` status transitions.
4. **During Update**
   - Watch CloudWatch metrics for CPU spikes or connection drops.
   - For parameter changes requiring reboot, ensure maintenance window matches schedule.
5. **Verification**
   ```bash
   psql "$(terraform output -raw connection_string)" -c 'SELECT version();'
   ```
   Confirm expected PostgreSQL version or parameter change.
6. **Documentation**
   - Update runbook or README if new parameters introduced.
   - Log change in JIRA with Terraform apply output attached.

Rollback: If apply fails mid-way, Terraform halts. Rerun `terraform apply` after remediation. For regressions, restore from automated snapshot (`aws rds restore-db-instance-from-db-snapshot`).

---

## Procedure 3: Database Failover Testing (30 minutes)
1. **Prerequisites**
   - Maintenance window approved.
   - Application team available to validate service behavior.
2. **Initiate Failover**
   ```bash
   aws rds reboot-db-instance --db-instance-identifier prod-app-db --force-failover
   ```
3. **Monitor**
   - Use `watch aws rds describe-db-instances --db-instance-identifier prod-app-db --query 'DBInstances[0].DBInstanceStatus'`.
   - Measure failover duration; target < 60 seconds.
4. **Validate**
   ```bash
   psql "$(terraform output -raw connection_string)" -c 'SELECT pg_is_in_recovery();'
   ```
   Should return `f` indicating new primary.
5. **Document Metrics**
   - Record RTO, RPO in Confluence.
   - Attach CloudWatch graph of `DatabaseConnections` before/after.

Rollback: Failover is self-healing; no rollback required.

---

## Procedure 4: Scale Database Resources (45 minutes)
- **Vertical Scaling (Instance Class)**
  ```bash
  terraform apply -var-file=prod.tfvars -var "instance_class=db.r6g.xlarge"
  ```
  Ensure `apply_immediately=false` for production to avoid mid-day downtime.
- **Horizontal Scaling (Read Replicas)**
  - Create additional module deployment with `environment="prod-read"` targeting replica configuration (future enhancement noted).
- **Storage Scaling**
  ```bash
  terraform apply -var-file=prod.tfvars -var "allocated_storage=400" -var "max_allocated_storage=1200"
  ```
- **Validation**
  ```bash
  aws rds describe-db-instances --db-instance-identifier prod-app-db --query 'DBInstances[0].{Class:DBInstanceClass,Storage:AllocatedStorage}'
  ```
  Ensure new class/storage reported. Run load tests to confirm throughput increase.

Rollback: Decrease instance class by reapplying previous size during maintenance window. Storage reductions require snapshot/restore.

---

## Procedure 5: Backup & Restore (60 minutes)
- **Manual Snapshot**
  ```bash
  SNAPSHOT_ID=prod-app-db-pre-maint-$(date +%Y%m%d%H%M)
  aws rds create-db-snapshot --db-snapshot-identifier $SNAPSHOT_ID --db-instance-identifier prod-app-db
  aws rds wait db-snapshot-completed --db-snapshot-identifier $SNAPSHOT_ID
  ```
- **Verify Automated Backups**
  ```bash
  aws rds describe-db-snapshots --db-instance-identifier prod-app-db --snapshot-type automated --query 'DBSnapshots[].DBSnapshotIdentifier'
  ```
- **Point-in-Time Recovery**
  ```bash
  aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier prod-app-db \
    --target-db-instance-identifier prod-app-db-restore \
    --use-latest-restorable-time
  ```
  After restore, update security group to isolate and validate data integrity.
- **Cross-Region Copy**
  ```bash
  aws rds copy-db-snapshot \
    --source-region us-west-2 \
    --source-db-snapshot-identifier arn:aws:rds:us-west-2:123456789012:snapshot:prod-app-db-pre-maint-20240101 \
    --target-db-snapshot-identifier prod-app-db-pre-maint-us-east-1
  ```

Rollback: Delete temporary restored instance with `aws rds delete-db-instance --skip-final-snapshot` after validation.

---

## Procedure 6: Security Hardening (45 minutes)
- **Rotate Credentials**
  ```bash
  NEW_PASSWORD=$(openssl rand -base64 24)
  aws secretsmanager update-secret --secret-id prod/app/db/master --secret-string "{\"username\":\"app_admin\",\"password\":\"$NEW_PASSWORD\"}"
  terraform apply -var-file=prod.tfvars -var "apply_immediately=true"
  ```
- **Update Security Group**
  ```bash
  terraform apply -var-file=prod.tfvars -var 'allowed_security_group_ids=["sg-0123...","sg-0456..."]'
  ```
- **Enable Enhanced Logging**
  - Attach CloudWatch subscription filter to ship logs to SIEM.
- **Audit Review**
  - Run `aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=ModifyDBInstance` for compliance evidence.

Rollback: Revert to previous Terraform commit and reapply. For secrets, restore prior value from Secrets Manager version history.

---

## Procedure 7: Tear Down Database (30 minutes)
1. **Safety Checks**
   - Confirm written approval from data owner.
   - Verify latest snapshot exists (`aws rds describe-db-snapshots`).
2. **Final Backup**
   ```bash
   SNAPSHOT_ID=prod-app-db-final-$(date +%Y%m%d%H%M)
   aws rds create-db-snapshot --db-snapshot-identifier $SNAPSHOT_ID --db-instance-identifier prod-app-db
   aws rds wait db-snapshot-completed --db-snapshot-identifier $SNAPSHOT_ID
   ```
3. **Destroy**
   ```bash
   terraform destroy -var-file=prod.tfvars
   ```
   Respond `yes` after reviewing plan. Expected output: `Destroy complete! Resources: 3 destroyed.`
4. **Validation**
   ```bash
   aws rds describe-db-instances --db-instance-identifier prod-app-db
   ```
   Command should return `DBInstanceNotFound`.
5. **Cost Closure**
   - Tag snapshot with `Status=Archived`.
   - Update cost tracking spreadsheet with monthly savings.

Rollback: Restore from `prod-app-db-final` snapshot and reapply Terraform configuration.

---

## Troubleshooting

| Symptom | Root Cause | Diagnosis | Resolution |
|---------|------------|-----------|------------|
| `terraform plan` shows drift | Manual console change | `terraform show` previous state | Reapply Terraform or update configuration. |
| `psql: could not connect` | Security group missing ingress | Check `aws ec2 describe-security-groups` | Add SG via Terraform and reapply. |
| CPU > 90% sustained | Under-provisioned instance | Review CloudWatch metrics | Scale instance class (§4). |
| `StorageFull` alarm | Autoscaling cap reached | `aws rds describe-db-instances --query '...AllocatedStorage'` | Increase `max_allocated_storage` and apply. |
| Backup failures | IAM role lacks permissions | CloudWatch event details | Update IAM policy for `rds:CreateDBSnapshot`. |
| Terraform state locked | Previous run interrupted | `terraform force-unlock <LOCK_ID>` | Run after verifying no active apply. |

---

## Post-Procedure Actions
- Update change log and attach Terraform plan/apply artifacts.
- Review CloudWatch alarms post-change to ensure no lingering alerts.
- Notify stakeholders in Slack and update JIRA ticket status.
- For production, update DR documentation with snapshot IDs or failover metrics.

---

## Appendix
- **Quick Commands:** `terraform plan -refresh-only`, `aws rds describe-db-log-files`, `psql -c "SELECT now();"`.
- **IAM Policy Template:** `iam/policies/terraform-rds-admin.json` (linked in repo docs).
- **CloudWatch Insights Query:**
  ```sql
  fields @timestamp, @message
  | filter @message like /authentication failure/
  | sort @timestamp desc
  | limit 20
  ```
- **Common Error Messages:**
  - `InvalidDBSubnetGroup`: subnets not in two AZs.
  - `AccessDenied for security group`: IAM principal missing `ec2:AuthorizeSecurityGroupIngress`.
  - `KMS Key Not Accessible`: ensure RDS service principal allowed on CMK policy.
