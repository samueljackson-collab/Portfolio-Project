# Operations Guide

This guide captures the day-to-day procedures and incident response steps for the multi-tier AWS stack. Every action references either Terraform state, the helper scripts in `scripts/`, or single AWS CLI commands so the environment stays consistent and auditable.

## Daily Checklist (5 minutes)
1. **Dashboard review** – Open the CloudWatch dashboard (`aws-multi-tier-prod-infra` by default) and confirm:
   - ALB request count and target response time remain within norms.
   - Auto Scaling CPU averages below 60% outside of known traffic spikes.
   - RDS CPU < 60% and FreeStorageSpace well above alarm threshold (10 GiB).
2. **CloudWatch alarms** – Run `aws cloudwatch describe-alarms --state-value ALARM` or execute `scripts/verify-stack.sh` to confirm no alarms are active.
3. **Backups** – Check AWS Backup job history for the latest daily and weekly jobs (expect success within 24h and 7d respectively).

## Deploy & Change Management
- Use `scripts/deploy.sh` for all infrastructure changes. The script runs `terraform fmt`, `validate`, `plan`, and prompts before `apply`.
- Pull requests must include Terraform plan output in the discussion for peer review.
- After changes apply, run `scripts/verify-stack.sh` to confirm targets are healthy and scaling parameters remain as expected.

## Validation Commands
- **End-to-end smoke test**: `curl -I https://$(terraform -chdir=terraform output -raw alb_dns_name)`
- **Check Auto Scaling instances**: `aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names $(terraform -chdir=terraform output -raw autoscaling_group_name)`
- **RDS health summary**: `aws rds describe-db-instances --db-instance-identifier $(terraform -chdir=terraform output -raw rds_instance_id)`

## Incident Runbooks

### 1. Auto Scaling CPU High Alert
**Trigger:** `aws_cloudwatch_metric_alarm.asg_cpu_high` fires (>70% CPU for 4 minutes).

1. Run `scripts/verify-stack.sh` to capture current scale and instance health.
2. Inspect ALB target health table in the script output for any failing hosts.
3. If demand is legitimate, temporarily raise capacity limits:
   ```bash
   aws autoscaling update-auto-scaling-group \
     --auto-scaling-group-name $(terraform -chdir=terraform output -raw autoscaling_group_name) \
     --max-size 8 --desired-capacity 4
   ```
4. If issue is application-level (errors, crash loop), pull application logs from the instances (`aws ssm start-session` or SSH via bastion) and roll back the last deployment.
5. After remediation, restore scaling targets to desired values and document the change.

### 2. ALB Unhealthy Targets Alert
**Trigger:** `aws_cloudwatch_metric_alarm.alb_unhealthy` enters ALARM.

1. Use `scripts/verify-stack.sh` to display target health and reason codes.
2. If all targets show `TargetNotRegistered`, confirm Terraform apply succeeded; rerun apply if necessary.
3. If targets are unhealthy:
   - SSH/SSM into the failing instance and validate NGINX is running (`systemctl status nginx`).
   - Review `/var/log/nginx/error.log` for application errors.
   - If the AMI bootstrap failed, terminate the instance to let Auto Scaling replace it.
4. Once at least one target reports `healthy`, confirm the alarm clears.

### 3. RDS Storage Low Alert
**Trigger:** `aws_cloudwatch_metric_alarm.rds_storage_low` (<10 GiB free).

1. Capture database connections and top queries via Performance Insights (AWS console) or CloudWatch logs.
2. Increase allocated storage through Terraform (adjust `db_allocated_storage` or `db_max_allocated_storage`) and redeploy.
3. Confirm new storage value: `aws rds describe-db-instances --db-instance-identifier ... --query 'DBInstances[0].{Allocated:AllocatedStorage,Free:FreeStorageSpace}'`.
4. For emergency relief, perform manual storage modification with `aws rds modify-db-instance --db-instance-identifier ... --allocated-storage ... --apply-immediately` and update Terraform afterward.

### 4. Restore Database from Backup
**Scenario:** Data corruption or major schema regression.

1. Stop application writes by setting Auto Scaling desired capacity to 0 (`aws autoscaling update-auto-scaling-group ... --desired-capacity 0`).
2. Execute `scripts/rds-restore-from-latest.sh [optional-new-id]` to create a clean copy from the latest snapshot.
3. Once the new instance is `available`, promote it:
   - Update Terraform variables (`db_multi_az`, identifiers if switching endpoints) and apply.
   - Rotate credentials in Secrets Manager if necessary.
4. Warm application tier back to baseline capacity.
5. Document recovery steps and root cause.

### 5. Region/AZ Outage Drill
1. Confirm Auto Scaling instances are distributed across AZs (`scripts/verify-stack.sh`).
2. Simulate AZ loss by setting one subnet to `NoSchedule` (temporarily removing it from the Auto Scaling group) and ensure traffic remains healthy.
3. Validate RDS Multi-AZ failover by initiating `aws rds reboot-db-instance --db-instance-identifier $(terraform -chdir=terraform output -raw rds_instance_id) --force-failover`.
4. Record downtime observed (expected <60s) and ensure alarms triggered appropriately.

## Maintenance Windows
- **Weekly patch window** – Mondays 04:00–05:00 UTC (aligned with RDS maintenance window) for AMI refreshes and Terraform changes.
- **Quarterly DR drill** – Execute the failover procedure above and update this document with findings.

## Tooling Reference
- `scripts/deploy.sh` – Terraform init/plan/apply helper.
- `scripts/verify-stack.sh` – Aggregates ALB, ASG, RDS health and lists active alarms.
- `scripts/rds-restore-from-latest.sh` – Restores the latest automated snapshot for recovery scenarios.

Everything lives inside Terraform state; avoid console edits unless explicitly captured in this runbook and mirrored back into code.
