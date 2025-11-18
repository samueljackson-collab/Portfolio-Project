#!/usr/bin/env bash
# Summarize the health of the multi-tier AWS stack using Terraform outputs and AWS CLI calls.
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
TF_DIR="${ROOT_DIR}/terraform"

for cmd in terraform aws jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

ALB_DNS=$(terraform -chdir="${TF_DIR}" output -raw alb_dns_name)
ASG_NAME=$(terraform -chdir="${TF_DIR}" output -raw autoscaling_group_name)
TARGET_GROUP_ARN=$(terraform -chdir="${TF_DIR}" output -raw target_group_arn)
RDS_ID=$(terraform -chdir="${TF_DIR}" output -raw rds_instance_id)

printf '\n=== Application Load Balancer ===\n'
printf 'URL: https://%s\n' "$ALB_DNS"
aws elbv2 describe-target-health \
  --target-group-arn "$TARGET_GROUP_ARN" \
  --query 'TargetHealthDescriptions[*].{InstanceId:Target.Id,State:TargetHealth.State,Reason:TargetHealth.Reason}' \
  --output table

printf '\n=== Auto Scaling Group ===\n'
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names "$ASG_NAME" \
  --query 'AutoScalingGroups[0].{Min:MinSize,Desired:DesiredCapacity,Max:MaxSize,Instances:Instances[*].[InstanceId,LifecycleState,HealthStatus,AvailabilityZone]}' \
  | jq

printf '\n=== RDS PostgreSQL ===\n'
aws rds describe-db-instances \
  --db-instance-identifier "$RDS_ID" \
  --query 'DBInstances[0].{Status:DBInstanceStatus,MultiAZ:MultiAZ,Endpoint:Endpoint.Address,AllocatedStorage:AllocatedStorage,FreeStorage:FreeStorageSpace}' \
  | jq

printf '\n=== Active CloudWatch Alarms ===\n'
aws cloudwatch describe-alarms \
  --state-value ALARM \
  --query 'MetricAlarms[].{Name:AlarmName,State:StateValue,Updated:StateUpdatedTimestamp}' \
  --output table
