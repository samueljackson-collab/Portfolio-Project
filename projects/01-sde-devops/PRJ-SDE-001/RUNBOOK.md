# Runbook — PRJ-SDE-001 (Database Infrastructure Module)

## Overview

Production operations runbook for the full-stack database infrastructure deployment on AWS. This runbook covers infrastructure management, deployment procedures, incident response, and troubleshooting for the Terraform-managed VPC, RDS PostgreSQL, and ECS Fargate application stack.

**System Components:**
- AWS VPC with multi-tier architecture (public, private, database subnets)
- RDS PostgreSQL database with Multi-AZ support
- ECS Fargate application with auto-scaling
- Application Load Balancer with health checks
- CloudWatch monitoring and alarms

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Database availability** | 99.95% | RDS Multi-AZ uptime |
| **Application availability** | 99.9% | ALB health check success rate |
| **Database response time** | < 50ms p95 | CloudWatch RDS metrics |
| **Application response time** | < 200ms p95 | ALB target response time |
| **Deployment success rate** | 99% | Terraform apply completion |
| **Backup success rate** | 100% | RDS automated backup completion |
| **RTO (Recovery Time Objective)** | < 30 minutes | Time to restore from backup |
| **RPO (Recovery Point Objective)** | < 5 minutes | Time since last backup/transaction |

---

## Dashboards & Alerts

### CloudWatch Dashboards

Access CloudWatch Console: https://console.aws.amazon.com/cloudwatch/

**Key Dashboards:**
1. **Infrastructure Overview** - VPC flow logs, NAT Gateway metrics
2. **Database Health** - RDS CPU, connections, storage, IOPS
3. **Application Health** - ECS task count, CPU/memory, ALB metrics
4. **Cost Dashboard** - Resource usage and cost tracking

#### Quick Health Check
```bash
# Check infrastructure status
cd infrastructure
terraform show | grep -E "status|state"

# Check RDS database status
aws rds describe-db-instances \
  --db-instance-identifier $(terraform output -raw db_instance_id) \
  --query 'DBInstances[0].DBInstanceStatus'

# Check ECS service status
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw ecs_service_name) \
  --query 'services[0].status'

# Check ALB target health
aws elbv2 describe-target-health \
  --target-group-arn $(terraform output -raw alb_target_group_arn) \
  --query 'TargetHealthDescriptions[*].TargetHealth.State'
```

### Alerts

CloudWatch alarms are automatically created by Terraform:

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Database CPU > 90% for 15 min | Immediate | Scale instance, investigate queries |
| **P0** | Database storage < 1 GB | Immediate | Extend storage or cleanup |
| **P0** | Zero healthy targets in ALB | Immediate | Check ECS tasks, rollback if recent deploy |
| **P1** | Database CPU > 80% for 10 min | 15 minutes | Review query performance |
| **P1** | Database connections > 80 | 15 minutes | Check connection pooling |
| **P1** | ECS task desired count not met | 15 minutes | Check task failures, resource constraints |
| **P2** | High memory usage (>80%) | 30 minutes | Investigate memory leaks |
| **P2** | ALB 5xx errors > 5% | 30 minutes | Check application logs |

#### Alert Queries

```bash
# Check active CloudWatch alarms
aws cloudwatch describe-alarms \
  --state-value ALARM \
  --query 'MetricAlarms[*].[AlarmName,StateValue,StateReason]' \
  --output table

# Check RDS metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=$(terraform output -raw db_instance_id) \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# Check ECS service metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=$(terraform output -raw ecs_service_name) \
              Name=ClusterName,Value=$(terraform output -raw ecs_cluster_name) \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

---

## Standard Operations

### Infrastructure Deployment

#### Initial Deployment

```bash
# 1. Configure AWS credentials
export AWS_PROFILE=production  # or use aws configure
aws sts get-caller-identity  # Verify credentials

# 2. Navigate to infrastructure directory
cd infrastructure

# 3. Create terraform.tfvars from example
cp terraform.tfvars.example terraform.tfvars

# 4. Edit configuration (CRITICAL: Set strong database password)
vi terraform.tfvars

# Required variables:
# - project_name
# - environment
# - aws_region
# - db_username
# - db_password (use strong password, store in secrets manager for production)

# 5. Initialize Terraform
terraform init

# 6. Validate configuration
terraform validate

# 7. Review planned changes
terraform plan -out=tfplan

# IMPORTANT: Review the plan carefully
# - Verify resource counts
# - Check security group rules
# - Validate CIDR blocks
# - Confirm instance types match budget

# 8. Apply infrastructure
terraform apply tfplan

# Deployment time: 15-20 minutes for full stack
# - VPC creation: 2-3 minutes
# - RDS instance: 10-15 minutes
# - ECS service: 3-5 minutes

# 9. Save outputs
terraform output > deployment-outputs.txt
terraform output -json > deployment-outputs.json
```

#### Update Existing Infrastructure

```bash
# 1. Review current state
terraform show

# 2. Make changes to configuration
vi terraform.tfvars
# or
vi main.tf

# 3. Plan changes
terraform plan -out=tfplan

# 4. Review impact
# - Resources to add: GREEN
# - Resources to change: YELLOW (check for downtime impact)
# - Resources to destroy: RED (WARNING - data loss possible)

# 5. Apply changes
terraform apply tfplan

# 6. Monitor deployment
# Watch CloudWatch logs, RDS events, ECS service events
```

#### Database-Only Deployment

```bash
# For cost savings, deploy only VPC + RDS
vi terraform.tfvars

# Set:
deploy_application = false

terraform plan -out=tfplan
terraform apply tfplan

# Cost: ~$15-30/month (vs $50-100/month for full stack)
```

### Database Operations

#### Connect to Database

```bash
# From within VPC (ECS task, EC2 bastion)
DB_ENDPOINT=$(terraform output -raw database_endpoint)
DB_USER=$(terraform output -raw database_username)

# Connect with psql (will prompt for password)
# For security, do not pass password in connection string
psql -U ${DB_USER} -h ${DB_ENDPOINT} -p 5432 -d postgres

# Create application database
CREATE DATABASE myapp;
GRANT ALL PRIVILEGES ON DATABASE myapp TO ${DB_USER};
\c myapp
```

#### Database Performance Tuning

```bash
# Check active connections
psql -h $DB_ENDPOINT -U $DB_USER -d postgres -c \
  "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Check slow queries
psql -h $DB_ENDPOINT -U $DB_USER -d postgres -c \
  "SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
   FROM pg_stat_activity
   WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
   ORDER BY duration DESC;"

# Kill long-running query (if needed)
psql -h $DB_ENDPOINT -U $DB_USER -d postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = <PID>;"

# Check database size
psql -h $DB_ENDPOINT -U $DB_USER -d postgres -c \
  "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size
   FROM pg_database
   ORDER BY pg_database_size(pg_database.datname) DESC;"
```

#### Manual Backup

```bash
# Create manual snapshot
DB_INSTANCE=$(terraform output -raw db_instance_id)

aws rds create-db-snapshot \
  --db-instance-identifier $DB_INSTANCE \
  --db-snapshot-identifier "${DB_INSTANCE}-manual-$(date +%Y%m%d-%H%M)"

# List snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier $DB_INSTANCE \
  --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime,Status]' \
  --output table

# Export snapshot to S3 (for long-term retention)
# Replace placeholders: <AWS_REGION>, <AWS_ACCOUNT_ID>, <SNAPSHOT_NAME>, <KMS_KEY_ID>
aws rds start-export-task \
  --export-task-identifier "${DB_INSTANCE}-export-$(date +%Y%m%d)" \
  --source-arn "arn:aws:rds:<AWS_REGION>:<AWS_ACCOUNT_ID>:snapshot:<SNAPSHOT_NAME>" \
  --s3-bucket-name <YOUR_S3_BUCKET_FOR_EXPORTS> \
  --iam-role-arn "arn:aws:iam::<AWS_ACCOUNT_ID>:role/rds-s3-export-role" \
  --kms-key-id "arn:aws:kms:<AWS_REGION>:<AWS_ACCOUNT_ID>:key/<KMS_KEY_ID>"
```

### Application Operations

#### Scale ECS Service

```bash
CLUSTER=$(terraform output -raw ecs_cluster_name)
SERVICE=$(terraform output -raw ecs_service_name)

# Scale up (manually)
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --desired-count 5

# Scale down
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --desired-count 2

# View current task count
aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --query 'services[0].[desiredCount,runningCount,pendingCount]'
```

#### Update Application Image

```bash
# Update task definition with new image
aws ecs describe-task-definition \
  --task-definition $(terraform output -raw ecs_task_definition_family) \
  --query 'taskDefinition' > task-def.json

# Edit task-def.json to update image
vi task-def.json
# Change: "image": "nginx:1.24" → "image": "nginx:1.25"

# Register new task definition
NEW_TASK_DEF=$(aws ecs register-task-definition \
  --cli-input-json file://task-def.json \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

# Update service to use new task definition
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --task-definition $NEW_TASK_DEF \
  --force-new-deployment

# Monitor rollout
watch -n 5 "aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --query 'services[0].deployments[*].[status,runningCount,desiredCount]'"
```

#### View Application Logs

```bash
# Get log group name
LOG_GROUP=$(terraform output -raw ecs_log_group_name)

# Stream recent logs
aws logs tail $LOG_GROUP --follow

# Search logs for errors
aws logs filter-log-events \
  --log-group-name $LOG_GROUP \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000

# Get logs for specific task
TASK_ID="abc123def456"
aws logs tail $LOG_GROUP --follow --log-stream-name-prefix "ecs/app/$TASK_ID"
```

### VPC and Network Operations

#### Check VPC Flow Logs

```bash
# Get flow log group
FLOW_LOG_GROUP="/aws/vpc/$(terraform output -raw vpc_id)-flow-logs"

# View flow logs
aws logs tail $FLOW_LOG_GROUP --since 1h

# Analyze rejected connections
aws logs filter-log-events \
  --log-group-name $FLOW_LOG_GROUP \
  --filter-pattern "[version, account, eni, source, destination, srcport, destport, protocol, packets, bytes, windowstart, windowend, action=REJECT, flowlogstatus]" \
  --start-time $(date -d '1 hour ago' +%s)000

# Find top talkers
aws logs tail $FLOW_LOG_GROUP --since 1h | \
  awk '{print $4}' | sort | uniq -c | sort -rn | head -20
```

---

## Incident Response

### P0: Database High CPU

**Immediate Actions (0-5 minutes):**
```bash
# 1. Verify alarm is legitimate
aws cloudwatch describe-alarms \
  --alarm-names "$(terraform output -raw project_name)-database-high-cpu" \
  --query 'MetricAlarms[0].StateReason'

# 2. Check current CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=$(terraform output -raw db_instance_id) \
  --start-time $(date -u -d '15 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Maximum

# 3. Identify expensive queries
psql -h $(terraform output -raw database_endpoint) -U $DB_USER -d postgres -c \
  "SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
   FROM pg_stat_activity
   WHERE state != 'idle'
   ORDER BY duration DESC
   LIMIT 10;"
```

**Investigation (5-15 minutes):**
```bash
# Check for missing indexes
psql -h $(terraform output -raw database_endpoint) -U $DB_USER -d myapp -c \
  "SELECT schemaname, tablename, attname, n_distinct, correlation
   FROM pg_stats
   WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
   ORDER BY abs(correlation) DESC;"

# Check table bloat
psql -h $(terraform output -raw database_endpoint) -U $DB_USER -d myapp -c \
  "SELECT current_database(), schemaname, tablename,
   pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
   LIMIT 10;"

# Check for locks
psql -h $(terraform output -raw database_endpoint) -U $DB_USER -d postgres -c \
  "SELECT blocked_locks.pid AS blocked_pid, blocking_locks.pid AS blocking_pid,
   blocked_activity.query AS blocked_statement,
   blocking_activity.query AS blocking_statement
   FROM pg_catalog.pg_locks blocked_locks
   JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
   JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
   JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
   WHERE NOT blocked_locks.granted;"
```

**Mitigation:**
```bash
# Option 1: Kill expensive query
psql -h $(terraform output -raw database_endpoint) -U $DB_USER -d postgres -c \
  "SELECT pg_terminate_backend(<PID>);"

# Option 2: Scale up instance temporarily
DB_INSTANCE=$(terraform output -raw db_instance_id)

# Modify to larger instance class (will cause brief downtime)
aws rds modify-db-instance \
  --db-instance-identifier $DB_INSTANCE \
  --db-instance-class db.t3.large \
  --apply-immediately

# Monitor instance modification
watch -n 10 "aws rds describe-db-instances \
  --db-instance-identifier $DB_INSTANCE \
  --query 'DBInstances[0].DBInstanceStatus'"

# Option 3: Add read replica for read-heavy workload
aws rds create-db-instance-read-replica \
  --db-instance-identifier "${DB_INSTANCE}-replica" \
  --source-db-instance-identifier $DB_INSTANCE \
  --db-instance-class db.t3.small
```

### P0: Zero Healthy Targets in ALB

**Immediate Actions:**
```bash
# 1. Check target health
ALB_TG_ARN=$(terraform output -raw alb_target_group_arn)

aws elbv2 describe-target-health \
  --target-group-arn $ALB_TG_ARN

# 2. Check ECS service status
CLUSTER=$(terraform output -raw ecs_cluster_name)
SERVICE=$(terraform output -raw ecs_service_name)

aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --query 'services[0].[desiredCount,runningCount,deployments[*].[status,taskDefinition]]'

# 3. Check recent task failures
aws ecs list-tasks \
  --cluster $CLUSTER \
  --service-name $SERVICE \
  --desired-status STOPPED \
  --max-results 10 | \
jq -r '.taskArns[]' | \
while read task; do
  aws ecs describe-tasks --cluster $CLUSTER --tasks $task \
    --query 'tasks[0].[taskArn,stoppedReason,containers[0].reason]'
done

# 4. Check task logs for errors
LOG_GROUP=$(terraform output -raw ecs_log_group_name)
aws logs tail $LOG_GROUP --since 30m | grep -i error
```

**Common Causes:**

| Cause | Symptom | Resolution |
|-------|---------|------------|
| Failed health checks | Tasks running but unhealthy | Fix application /health endpoint |
| Image pull errors | Tasks fail to start | Verify Docker image exists and ECR permissions |
| Resource constraints | Tasks pending | Increase cluster capacity or reduce task resources |
| Application crash | Tasks start then stop | Check logs, fix application bug |
| Network issues | Tasks can't reach ALB | Check security groups, subnet routing |

**Resolution:**
```bash
# If recent deployment caused issue, rollback
# Get previous task definition
OLD_TASK_DEF=$(aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --query 'services[0].deployments[1].taskDefinition' \
  --output text)

# Rollback to previous version
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --task-definition $OLD_TASK_DEF \
  --force-new-deployment

# Monitor recovery
watch -n 5 "aws elbv2 describe-target-health \
  --target-group-arn $ALB_TG_ARN \
  --query 'TargetHealthDescriptions[*].TargetHealth.State'"
```

### P1: Database Storage Low

**Immediate Actions:**
```bash
# Check current storage
DB_INSTANCE=$(terraform output -raw db_instance_id)

aws rds describe-db-instances \
  --db-instance-identifier $DB_INSTANCE \
  --query 'DBInstances[0].[AllocatedStorage,MaxAllocatedStorage,DBInstanceStorageType]'

# Check storage metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name FreeStorageSpace \
  --dimensions Name=DBInstanceIdentifier,Value=$DB_INSTANCE \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average \
  --query 'Datapoints | sort_by(@, &Timestamp)'
```

**Mitigation:**
```bash
# Option 1: Increase max allocated storage (auto-scales)
aws rds modify-db-instance \
  --db-instance-identifier $DB_INSTANCE \
  --max-allocated-storage 200 \
  --apply-immediately

# Option 2: Manually increase storage immediately
aws rds modify-db-instance \
  --db-instance-identifier $DB_INSTANCE \
  --allocated-storage 100 \
  --apply-immediately

# Option 3: Clean up old data (if applicable)
psql -h $(terraform output -raw database_endpoint) -U $DB_USER -d myapp <<EOF
-- Delete old records (example)
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days';

-- Vacuum to reclaim space
VACUUM FULL;
EOF

# Note: VACUUM FULL locks table, run during maintenance window
```

---

## Troubleshooting

### Issue: Terraform Apply Fails

**Symptoms:**
- `terraform apply` exits with error
- Resources partially created
- State file may be out of sync

**Diagnosis:**
```bash
# Check Terraform state
terraform show

# Verify AWS credentials
aws sts get-caller-identity

# Check resource limits
aws service-quotas list-service-quotas \
  --service-code vpc \
  --query 'Quotas[?QuotaName==`VPCs per Region`]'

# Check for conflicting resources
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=$(terraform output -raw project_name)*"
```

**Resolution:**
```bash
# Option 1: Retry with debug logging
TF_LOG=DEBUG terraform apply

# Option 2: Import existing resources
terraform import aws_vpc.main <vpc-id>

# Option 3: Remove failed resources and retry
terraform state rm aws_rds_cluster.main
terraform apply

# Option 4: Recreate from scratch (DESTRUCTIVE)
terraform destroy -auto-approve
terraform apply
```

### Issue: Cannot Connect to Database

**Diagnosis:**
```bash
# 1. Verify database is running
aws rds describe-db-instances \
  --db-instance-identifier $(terraform output -raw db_instance_id) \
  --query 'DBInstances[0].DBInstanceStatus'

# 2. Check security groups
DB_SG=$(terraform output -raw db_security_group_id)

aws ec2 describe-security-groups \
  --group-ids $DB_SG \
  --query 'SecurityGroups[0].IpPermissions'

# 3. Check network ACLs
VPC_ID=$(terraform output -raw vpc_id)

aws ec2 describe-network-acls \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'NetworkAcls[*].Entries'

# 4. Test connectivity from ECS task
CLUSTER=$(terraform output -raw ecs_cluster_name)
SERVICE=$(terraform output -raw ecs_service_name)

# Get task ID
TASK=$(aws ecs list-tasks --cluster $CLUSTER --service-name $SERVICE \
  --query 'taskArns[0]' --output text)

# Execute psql in task
aws ecs execute-command \
  --cluster $CLUSTER \
  --task $TASK \
  --container app \
  --command "nc -zv $(terraform output -raw database_endpoint) 5432" \
  --interactive
```

**Resolution:**
```bash
# If security group is blocking
# Update security group to allow traffic from ECS tasks
APP_SG=$(terraform output -raw ecs_security_group_id)

aws ec2 authorize-security-group-ingress \
  --group-id $DB_SG \
  --protocol tcp \
  --port 5432 \
  --source-group $APP_SG

# Or update Terraform configuration
vi infrastructure/modules/database/security.tf
# Add ingress rule for ECS security group
terraform apply
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Check CloudWatch alarms
aws cloudwatch describe-alarms \
  --state-value ALARM \
  --output table

# Check backup status
aws rds describe-db-instances \
  --db-instance-identifier $(terraform output -raw db_instance_id) \
  --query 'DBInstances[0].[LatestRestorableTime,BackupRetentionPeriod]'

# Check ECS service health
CLUSTER=$(terraform output -raw ecs_cluster_name)
SERVICE=$(terraform output -raw ecs_service_name)

aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --query 'services[0].[serviceName,status,runningCount,desiredCount]'
```

#### Weekly Tasks
```bash
# Review CloudWatch Logs Insights
# Check for application errors, slow queries, security events

# Review cost and usage
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=SERVICE

# Check for unused resources
# - Orphaned EBS volumes
# - Unattached Elastic IPs
# - Idle NAT Gateways

# Update Terraform modules
cd infrastructure
terraform init -upgrade
terraform plan
```

#### Monthly Tasks
```bash
# Review and update instance types
# - Check for newer instance generations
# - Evaluate cost savings with Reserved Instances

# Test disaster recovery procedures
# - Restore database from snapshot
# - Recreate infrastructure in different region

# Security audit
# - Review IAM policies
# - Check security group rules
# - Rotate database password
# - Review VPC flow logs for anomalies

# Update documentation
# - Review and update runbook
# - Document any new procedures
# - Update architecture diagrams
```

### Database Maintenance Window

**Schedule:** First Sunday of month, 02:00-04:00 UTC

```bash
# 1. Announce maintenance
echo "Database maintenance starting at $(date)"

# 2. Create pre-maintenance snapshot
DB_INSTANCE=$(terraform output -raw db_instance_id)

aws rds create-db-snapshot \
  --db-instance-identifier $DB_INSTANCE \
  --db-snapshot-identifier "${DB_INSTANCE}-pre-maint-$(date +%Y%m%d)"

# 3. Apply pending OS patches
aws rds modify-db-instance \
  --db-instance-identifier $DB_INSTANCE \
  --apply-immediately \
  --auto-minor-version-upgrade

# 4. Reboot database (if required by patches)
aws rds reboot-db-instance \
  --db-instance-identifier $DB_INSTANCE

# 5. Wait for database to be available
while true; do
  STATUS=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE \
    --query 'DBInstances[0].DBInstanceStatus' \
    --output text)
  echo "Status: $STATUS"
  [[ $STATUS == "available" ]] && break
  sleep 30
done

# 6. Run VACUUM and ANALYZE
psql -h $(terraform output -raw database_endpoint) -U $DB_USER -d myapp <<EOF
VACUUM ANALYZE;
REINDEX DATABASE myapp;
EOF

# 7. Verify health
psql -h $(terraform output -raw database_endpoint) -U $DB_USER -d postgres -c \
  "SELECT version();"

# 8. Monitor for 30 minutes
echo "Maintenance complete at $(date)"
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 5 minutes (automated backups + transaction logs)
- **RTO** (Recovery Time Objective): 30 minutes (restore from snapshot + apply logs)

### Backup Strategy

**Automated Backups:**
- Daily automated snapshots during maintenance window
- 7-35 day retention (configurable in terraform.tfvars)
- Transaction logs backed up every 5 minutes
- Point-in-time recovery available

**Manual Backups:**
- Before major changes (infrastructure updates, schema migrations)
- Before and after maintenance windows
- Export to S3 for long-term retention

### Complete Infrastructure Recovery

**Scenario:** Total infrastructure loss (region failure, accidental `terraform destroy`)

```bash
# 1. Restore Terraform state from backup
# Assume state is stored in S3 backend
aws s3 cp s3://my-terraform-state/prod/terraform.tfstate terraform.tfstate.backup

# 2. Restore database from latest snapshot
DB_SNAPSHOT=$(aws rds describe-db-snapshots \
  --db-instance-identifier $(terraform output -raw db_instance_id) \
  --query 'DBSnapshots | sort_by(@, &SnapshotCreateTime) | [-1].DBSnapshotIdentifier' \
  --output text)

echo "Latest snapshot: $DB_SNAPSHOT"

# 3. Recreate infrastructure with Terraform
cd infrastructure

# Modify main.tf to restore from snapshot
cat >> main.tf <<EOF
# In database module call, add:
snapshot_identifier = "$DB_SNAPSHOT"
EOF

# 4. Apply Terraform
terraform init
terraform plan -out=recovery.tfplan
terraform apply recovery.tfplan

# 5. Verify database connectivity and data
psql -h $(terraform output -raw database_endpoint) -U $DB_USER -d myapp -c \
  "SELECT count(*) FROM pg_tables WHERE schemaname = 'public';"

# 6. Verify application health
ALB_DNS=$(terraform output -raw alb_dns_name)
curl -f http://$ALB_DNS/health

# 7. Document recovery
echo "Recovery completed at $(date)" > recovery-$(date +%Y%m%d-%H%M).log
echo "Snapshot used: $DB_SNAPSHOT" >> recovery-$(date +%Y%m%d-%H%M).log
echo "RTO: <actual_time>" >> recovery-$(date +%Y%m%d-%H%M).log
```

### Database Point-in-Time Recovery

```bash
# Restore to specific timestamp
DB_INSTANCE=$(terraform output -raw db_instance_id)
RESTORE_TIME="2025-11-10T14:30:00Z"

aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier $DB_INSTANCE \
  --target-db-instance-identifier "${DB_INSTANCE}-pitr-$(date +%Y%m%d)" \
  --restore-time $RESTORE_TIME \
  --db-subnet-group-name $(terraform output -raw db_subnet_group_name) \
  --vpc-security-group-ids $(terraform output -raw db_security_group_id)

# Wait for restore to complete (10-15 minutes)
watch -n 30 "aws rds describe-db-instances \
  --db-instance-identifier ${DB_INSTANCE}-pitr-$(date +%Y%m%d) \
  --query 'DBInstances[0].DBInstanceStatus'"

# Verify data
NEW_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier "${DB_INSTANCE}-pitr-$(date +%Y%m%d)" \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

psql -h $NEW_ENDPOINT -U $DB_USER -d myapp -c "SELECT NOW();"

# If verified, promote to production or keep as investigation instance
```

---

## Operational Best Practices

### Pre-Deployment Checklist
- [ ] Code reviewed and approved
- [ ] Terraform plan reviewed (no unexpected destroys)
- [ ] Secrets stored in AWS Secrets Manager (not in tfvars)
- [ ] Backup taken before major changes
- [ ] Rollback plan documented
- [ ] Stakeholders notified of deployment window
- [ ] Monitoring dashboards open and visible

### Post-Deployment Checklist
- [ ] Terraform apply completed successfully
- [ ] All CloudWatch alarms in OK state
- [ ] Database accessible and responding
- [ ] ECS tasks healthy (all targets in ALB healthy)
- [ ] Application logs show no errors
- [ ] Smoke tests pass
- [ ] Monitor for 30 minutes after deployment

### Security Best Practices

**Implemented:**
- ✅ VPC with network segmentation
- ✅ RDS in private subnet (no public access)
- ✅ Encryption at rest (KMS)
- ✅ Encryption in transit (SSL/TLS)
- ✅ Automated backups
- ✅ CloudWatch logging and monitoring
- ✅ IAM roles with least privilege

**Recommended Enhancements:**
- 🔒 Store database password in AWS Secrets Manager
- 🔒 Enable RDS IAM authentication
- 🔒 Add AWS WAF to ALB
- 🔒 Enable GuardDuty for threat detection
- 🔒 Use ACM for HTTPS on ALB
- 🔒 Implement VPC endpoints for AWS services

---

## Quick Reference

### Most Common Operations
```bash
# Check infrastructure status
cd infrastructure && terraform show

# View database endpoint
terraform output database_endpoint

# View application URL
terraform output application_url

# Check ECS tasks
aws ecs list-tasks --cluster $(terraform output -raw ecs_cluster_name) \
  --service-name $(terraform output -raw ecs_service_name)

# View application logs
aws logs tail $(terraform output -raw ecs_log_group_name) --follow

# Create database backup
aws rds create-db-snapshot \
  --db-instance-identifier $(terraform output -raw db_instance_id) \
  --db-snapshot-identifier "manual-$(date +%Y%m%d-%H%M)"

# Check CloudWatch alarms
aws cloudwatch describe-alarms --state-value ALARM
```

### Emergency Response
```bash
# P0: Database down
aws rds reboot-db-instance \
  --db-instance-identifier $(terraform output -raw db_instance_id)

# P0: Zero healthy application targets
# Rollback ECS service to previous task definition
aws ecs describe-services --cluster $CLUSTER --services $SERVICE \
  --query 'services[0].deployments[1].taskDefinition'
# Then update service with that task definition

# P1: Out of disk space on database
aws rds modify-db-instance \
  --db-instance-identifier $(terraform output -raw db_instance_id) \
  --allocated-storage 200 \
  --apply-immediately
```

---

## References

### Internal Documentation
- [PRJ-SDE-001 README](./README.md)
- [Terraform Modules](./infrastructure/modules/)
- [Architecture Diagrams](./README.md#architecture)

### External Resources
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/intro.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Emergency Contacts
- **On-call rotation:** See internal wiki
- **Slack channels:** #infrastructure, #incidents
- **AWS Support:** https://console.aws.amazon.com/support/

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Infrastructure Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
