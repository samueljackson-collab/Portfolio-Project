# Operations Runbook

## Monitoring
- CloudWatch dashboard `prj-aws-001-<env>-operations` for ASG CPU and ALB 5xx.
- Subscribe the alarm SNS topic to PagerDuty/Slack for 24x7 notification.
- Review VPC Flow Logs daily for denied traffic spikes.

## On-Call Procedures
1. **ALB 5xx Alarm**
   - Check target group health. If instances unhealthy, inspect Auto Scaling activity.
   - Review recent deployments/user data logs on EC2.
2. **ASG CPU Alarm**
   - Scale out via Terraform variable changes or temporarily adjust desired capacity using AWS CLI.
   - Investigate load (APM traces, logs) before tuning thresholds.
3. **Database Connectivity Issues**
   - Validate SG relationships: ALB -> App -> DB.
   - Ensure DB parameter group healthy and Multi-AZ failover completed.

## Routine Tasks
- Patch AMIs monthly and rotate `ami_id` variables per environment.
- Rotate DB credentials via AWS Secrets Manager; update `terraform.tfvars` or use external data sources.
- Run `terraform/scripts/validate.sh` weekly to catch drift.

## Incident Documentation
Record timeline, AWS resources impacted, Terraform plan references, and remediation actions in the ops wiki.
