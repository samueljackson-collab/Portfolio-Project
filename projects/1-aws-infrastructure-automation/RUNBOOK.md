# Runbook — Project 1 (AWS Infrastructure Automation)

## Overview

Production operations runbook for Project 1 AWS Infrastructure Automation platform. This runbook covers infrastructure provisioning, EKS cluster operations, RDS database management, incident response, and troubleshooting across Terraform, AWS CDK, and Pulumi implementations.

**System Components:**
- Multi-AZ VPC with public, private, and database subnets
- Amazon EKS (Elastic Kubernetes Service) cluster with managed node groups
- Amazon RDS PostgreSQL with Multi-AZ deployment
- Auto Scaling groups for EKS worker nodes and standalone web tier behind an Application Load Balancer
- S3 bucket for static assets fronted by CloudFront distribution
- CloudWatch monitoring and alerting
- Infrastructure-as-Code (Terraform, AWS CDK, Pulumi)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Infrastructure deployment success rate** | 99% | Terraform/CDK/Pulumi apply success responses |
| **EKS control plane availability** | 99.95% | EKS API server reachability |
| **RDS availability** | 99.95% (Multi-AZ) | CloudWatch `DatabaseConnections` > 0 |
| **Node autoscaling response time** | < 5 minutes | Time from high CPU → new nodes Running |
| **RDS failover time (RTO)** | < 2 minutes | Time from failover initiate → RDS available |
| **Infrastructure drift detection** | < 5 minutes | Terraform/CDK drift check latency |

---

## Dashboards & Alerts

### Dashboards

#### Infrastructure Overview Dashboard
```bash
# Check VPC and networking
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=aws-infra-automation"
aws ec2 describe-subnets --filters "Name=tag:Project,Values=aws-infra-automation"

# Check EKS cluster status
aws eks describe-cluster --name production-eks-cluster --query 'cluster.status'

# Check RDS instance status
aws rds describe-db-instances --db-instance-identifier production-postgres
```

#### EKS Cluster Dashboard
- [AWS EKS Console](https://console.aws.amazon.com/eks/home?region=us-east-1#/clusters)
- Control plane status, API server endpoint
- Node group health and scaling activity
- Add-on versions (CoreDNS, kube-proxy, VPC CNI)

#### RDS Database Dashboard
- [AWS RDS Console](https://console.aws.amazon.com/rds/home?region=us-east-1)
- CPU utilization, Free storage, DB connections
- Multi-AZ failover events
- Automated backup status

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | EKS cluster unavailable | Immediate | Emergency escalation |
| **P0** | RDS instance down | Immediate | Force Multi-AZ failover |
| **P0** | Infrastructure deployment failure (prod) | Immediate | Rollback and investigate |
| **P1** | All EKS nodes unhealthy | 5 minutes | Investigate and restart nodes |
| **P1** | RDS CPU >80% for 10 min | 15 minutes | Scale instance or optimize queries |
| **P2** | Infrastructure drift detected | 30 minutes | Review and remediate drift |
| **P2** | Node autoscaling delayed | 30 minutes | Check ASG policies |
| **P3** | RDS storage <20% | 1 hour | Plan storage scaling |

---

## Standard Operations

### Infrastructure Deployment

#### Terraform Deployment
```bash
# Navigate to Terraform directory
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation/terraform

# Initialize Terraform
terraform init

# Plan deployment (dry run)
terraform plan -var-file=environments/dev.tfvars -out=tfplan

# Apply deployment
terraform apply tfplan

# Verify deployment
terraform show
terraform output
```

#### AWS CDK Deployment
```bash
# Navigate to CDK directory
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation/cdk

# Install dependencies
pip install -r requirements.txt

# Synthesize CloudFormation template
cdk synth

# Deploy stack
cdk deploy --all --require-approval never

# Check stack status
aws cloudformation describe-stacks --stack-name InfrastructureStack
```

#### Pulumi Deployment
```bash
# Navigate to Pulumi directory
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation/pulumi

# Install dependencies
pip install -r requirements.txt

# Preview changes
pulumi preview

# Deploy infrastructure
pulumi up --yes

# Check stack outputs
pulumi stack output
```

### EKS Cluster Management

#### Connect to EKS Cluster
```bash
# Update kubeconfig
aws eks update-kubeconfig --name production-eks-cluster --region us-east-1

# Verify connection
kubectl cluster-info
kubectl get nodes
kubectl get pods -A
```

#### Check Cluster Health
```bash
# Check control plane status
aws eks describe-cluster --name production-eks-cluster \
  --query 'cluster.{Status:status,Endpoint:endpoint,Version:version}'

# Check node groups
aws eks list-nodegroups --cluster-name production-eks-cluster
aws eks describe-nodegroup --cluster-name production-eks-cluster \
  --nodegroup-name default-node-group

# Check nodes
kubectl get nodes -o wide
kubectl top nodes
```

#### Scale Node Groups
```bash
# Scale node group up
aws eks update-nodegroup-config \
  --cluster-name production-eks-cluster \
  --nodegroup-name default-node-group \
  --scaling-config minSize=3,maxSize=10,desiredSize=5

# Verify scaling
aws eks describe-nodegroup --cluster-name production-eks-cluster \
  --nodegroup-name default-node-group \
  --query 'nodegroup.scalingConfig'

# Watch nodes come online
watch kubectl get nodes
```

#### Update EKS Cluster Version
```bash
# Check current version
aws eks describe-cluster --name production-eks-cluster \
  --query 'cluster.version'

# Update control plane (requires maintenance window)
aws eks update-cluster-version \
  --name production-eks-cluster \
  --kubernetes-version 1.28

# Monitor update progress
aws eks describe-update --name production-eks-cluster \
  --update-id <update-id>

# Update node group after control plane
aws eks update-nodegroup-version \
  --cluster-name production-eks-cluster \
  --nodegroup-name default-node-group
```

### Web Tier (ALB + Auto Scaling Group)

#### Check ALB and Target Health
```bash
# List ALBs
aws elbv2 describe-load-balancers \
  --names "portfolio-alb-${ENVIRONMENT:-production}"
  --query 'LoadBalancers[*].DNSName'

# Target group health
aws elbv2 describe-target-health \
  --target-group-arn $(terraform output -raw alb_target_group_arn)
```

#### Inspect Web Auto Scaling Group
```bash
WEB_ASG=$(terraform output -raw web_autoscaling_group_name)
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names "$WEB_ASG" \
  --query 'AutoScalingGroups[0].{Desired:DesiredCapacity,InService:Instances[*].LifecycleState}'

# Scale out/in
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name "$WEB_ASG" \
  --desired-capacity 4
```

### S3 + CloudFront Static Delivery
```bash
# Upload static asset
aws s3 cp ./assets/index.html s3://$(terraform output -raw asset_bucket_name)/index.html

# Invalidate cache for updated assets
aws cloudfront create-invalidation \
  --distribution-id $(terraform output -raw cloudfront_distribution_id) \
  --paths "/index.html"
```


### RDS Database Management

#### Check RDS Status
```bash
# Get RDS instance details
aws rds describe-db-instances \
  --db-instance-identifier production-postgres \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Endpoint:Endpoint.Address,AZ:AvailabilityZone}'

# Check database connections
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=production-postgres \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

#### Start/Stop RDS (Non-Prod Only)
```bash
# Stop RDS instance (saves costs in dev/stage)
aws rds stop-db-instance --db-instance-identifier dev-postgres

# Start RDS instance
aws rds start-db-instance --db-instance-identifier dev-postgres

# Verify status
aws rds describe-db-instances --db-instance-identifier dev-postgres \
  --query 'DBInstances[0].DBInstanceStatus'
```

#### Scale RDS Instance
```bash
# Modify instance class
aws rds modify-db-instance \
  --db-instance-identifier production-postgres \
  --db-instance-class db.r6g.xlarge \
  --apply-immediately

# Monitor modification progress
aws rds describe-db-instances \
  --db-instance-identifier production-postgres \
  --query 'DBInstances[0].{Status:DBInstanceStatus,PendingChanges:PendingModifiedValues}'
```

#### Create RDS Snapshot
```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier production-postgres \
  --db-snapshot-identifier production-postgres-$(date +%Y%m%d-%H%M)

# List snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier production-postgres \
  --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime,Status]' \
  --output table
```

---

## Incident Response

### Detection

**Automated Detection:**
- CloudWatch alarms trigger SNS notifications
- Infrastructure drift detected by scheduled scans
- EKS cluster health checks fail
- RDS performance degradation alerts

**Manual Detection:**
```bash
# Check overall AWS infrastructure health
aws health describe-events --filter eventTypeCategories=issue,accountSpecific

# Check EKS cluster
aws eks describe-cluster --name production-eks-cluster \
  --query 'cluster.status'

# Check RDS
aws rds describe-db-instances --db-instance-identifier production-postgres \
  --query 'DBInstances[0].DBInstanceStatus'

# Check recent CloudWatch alarms
aws cloudwatch describe-alarms \
  --state-value ALARM \
  --max-records 20
```

### Triage

#### Severity Classification

**P0: Complete Outage**
- EKS cluster API server unreachable
- RDS instance stopped or failed
- Complete infrastructure deployment failure in production
- VPC networking failure affecting all services

**P1: Degraded Service**
- All EKS nodes unhealthy or terminated
- RDS connection exhaustion
- Single-AZ failure affecting availability
- Infrastructure drift causing service issues

**P2: Warning State**
- Infrastructure drift detected
- Node autoscaling not responding
- RDS storage approaching limits
- Non-critical deployment failures

**P3: Informational**
- Cost optimization opportunities
- Minor configuration drift
- Successful but slow deployments

### Incident Response Procedures

#### P0: EKS Cluster Unreachable

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check cluster status
aws eks describe-cluster --name production-eks-cluster

# 2. Check AWS service health
aws health describe-events --filter eventTypeCategories=issue

# 3. Check VPC and networking
aws ec2 describe-vpcs --vpc-ids <vpc-id>
aws ec2 describe-subnets --filters "Name=vpc-id,Values=<vpc-id>"

# 4. Check security groups
aws ec2 describe-security-groups --filters "Name=tag:Project,Values=aws-infra-automation"
```

**Investigation (5-15 minutes):**
```bash
# Check CloudTrail for recent API calls
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceType,AttributeValue=AWS::EKS::Cluster \
  --max-results 50

# Check cluster endpoint access
curl -k <eks-cluster-endpoint>/healthz

# Check IAM roles
aws iam get-role --role-name <eks-cluster-role>
```

**Mitigation:**
```bash
# If networking issue, check route tables
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=<vpc-id>"

# If control plane issue, contact AWS support immediately
aws support create-case \
  --subject "EKS Cluster Unreachable - P0" \
  --service-code "amazon-eks" \
  --severity-code "urgent" \
  --communication-body "Production EKS cluster unreachable..."

# Consider disaster recovery: restore from infrastructure code
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation/terraform
terraform apply -auto-approve
```

#### P0: RDS Instance Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check RDS instance status
aws rds describe-db-instances --db-instance-identifier production-postgres

# 2. Check recent RDS events
aws rds describe-events \
  --source-identifier production-postgres \
  --duration 60 \
  --source-type db-instance

# 3. Force Multi-AZ failover if primary unhealthy
aws rds reboot-db-instance \
  --db-instance-identifier production-postgres \
  --force-failover

# 4. Monitor failover progress
watch -n 5 'aws rds describe-db-instances \
  --db-instance-identifier production-postgres \
  --query "DBInstances[0].DBInstanceStatus"'
```

**Investigation (5-15 minutes):**
```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=production-postgres \
  --start-time $(date -u -d '2 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# Check error logs
aws rds download-db-log-file-portion \
  --db-instance-identifier production-postgres \
  --log-file-name error/postgresql.log.0
```

**Recovery:**
```bash
# If failover doesn't work, restore from snapshot
LATEST_SNAPSHOT=$(aws rds describe-db-snapshots \
  --db-instance-identifier production-postgres \
  --query 'DBSnapshots[-1].DBSnapshotIdentifier' \
  --output text)

aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier production-postgres-recovered \
  --db-snapshot-identifier $LATEST_SNAPSHOT

# Update application connection strings to point to new instance
```

#### P1: All EKS Nodes Unhealthy

**Investigation:**
```bash
# Check node status
kubectl get nodes -o wide
kubectl describe nodes

# Check node group status
aws eks describe-nodegroup \
  --cluster-name production-eks-cluster \
  --nodegroup-name default-node-group

# Check Auto Scaling group
ASG_NAME=$(aws eks describe-nodegroup \
  --cluster-name production-eks-cluster \
  --nodegroup-name default-node-group \
  --query 'nodegroup.resources.autoScalingGroups[0].name' \
  --output text)

aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names $ASG_NAME
```

**Mitigation:**
```bash
# Terminate unhealthy nodes (ASG will replace them)
kubectl get nodes -o jsonpath='{.items[*].metadata.name}' | xargs -n1 kubectl drain --ignore-daemonsets --delete-emptydir-data

# Force new node creation
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name $ASG_NAME \
  --desired-capacity 3

# Or create new node group
aws eks create-nodegroup \
  --cluster-name production-eks-cluster \
  --nodegroup-name emergency-node-group \
  --scaling-config minSize=2,maxSize=5,desiredSize=3 \
  --subnets <subnet-ids> \
  --node-role <node-role-arn>
```

#### P2: Infrastructure Drift Detected

**Investigation:**
```bash
# Terraform drift check
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation/terraform
terraform plan -var-file=environments/prod.tfvars

# CDK drift check
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation/cdk
cdk diff

# AWS Config drift check
aws cloudformation detect-stack-drift --stack-name InfrastructureStack
aws cloudformation describe-stack-resource-drifts --stack-name InfrastructureStack
```

**Remediation:**
```bash
# Option 1: Import manual changes to code
terraform import aws_security_group.manual_sg sg-xxxxx

# Option 2: Revert manual changes
terraform apply -auto-approve

# Option 3: Update code to match manual changes
# Edit terraform files, then:
terraform plan
terraform apply
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Incident Report

**Date:** $(date)
**Severity:** P0/P1/P2
**Duration:** XX minutes
**Affected Component:** EKS/RDS/Infrastructure

## Timeline
- HH:MM: Incident detected
- HH:MM: Investigation started
- HH:MM: Root cause identified
- HH:MM: Mitigation applied
- HH:MM: Service restored

## Root Cause
[Description of root cause]

## Action Items
- [ ] Update monitoring thresholds
- [ ] Improve documentation
- [ ] Add automated remediation

EOF

# Review and update runbook
# Document any new procedures discovered during incident
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective):
  - Infrastructure: 0 minutes (Infrastructure-as-Code in Git)
  - RDS Data: 5 minutes (automated snapshots)
- **RTO** (Recovery Time Objective):
  - Infrastructure: 30 minutes (redeployment from code)
  - RDS: 2 minutes (Multi-AZ automatic failover)

### Backup Strategy

#### Infrastructure Backups
```bash
# Infrastructure is backed up in Git
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation
git add terraform/ cdk/ pulumi/
git commit -m "backup: infrastructure state $(date +%Y-%m-%d)"
git push

# Export Terraform state
cd terraform
terraform state pull > backups/terraform-state-$(date +%Y%m%d).json

# Export current infrastructure as code
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --query 'StackSummaries[*].[StackName,StackStatus]' --output table
```

#### RDS Automated Backups
```bash
# Verify automated backup configuration
aws rds describe-db-instances \
  --db-instance-identifier production-postgres \
  --query 'DBInstances[0].{BackupRetentionPeriod:BackupRetentionPeriod,PreferredBackupWindow:PreferredBackupWindow}'

# List available automated snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier production-postgres \
  --snapshot-type automated

# Create manual snapshot before major changes
aws rds create-db-snapshot \
  --db-instance-identifier production-postgres \
  --db-snapshot-identifier pre-upgrade-$(date +%Y%m%d-%H%M)
```

### Disaster Recovery Procedures

#### Complete Infrastructure Recovery
```bash
# 1. Clone repository
git clone <repository-url>
cd Portfolio-Project/projects/1-aws-infrastructure-automation

# 2. Choose IaC tool and deploy
# Using Terraform:
cd terraform
terraform init
terraform apply -var-file=environments/prod.tfvars -auto-approve

# Using CDK:
cd cdk
pip install -r requirements.txt
cdk deploy --all --require-approval never

# Using Pulumi:
cd pulumi
pip install -r requirements.txt
pulumi up --yes

# 3. Verify deployment
aws eks describe-cluster --name production-eks-cluster
aws rds describe-db-instances --db-instance-identifier production-postgres

# 4. Restore RDS data if needed
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier production-postgres \
  --db-snapshot-identifier <latest-snapshot>

# 5. Update kubeconfig and verify applications
aws eks update-kubeconfig --name production-eks-cluster --region us-east-1
kubectl get pods -A
```

#### RDS Point-in-Time Recovery
```bash
# Restore to specific timestamp
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier production-postgres \
  --target-db-instance-identifier production-postgres-pitr \
  --restore-time 2025-11-10T14:30:00Z

# Or restore to latest restorable time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier production-postgres \
  --target-db-instance-identifier production-postgres-pitr \
  --use-latest-restorable-time
```

### DR Drill Procedure

**Monthly DR Drill (1 hour):**
```bash
# 1. Announce drill
echo "DR drill starting at $(date)" | tee dr-drill-log.txt

# 2. Document current state
terraform show > dr-drill-before-state.txt
aws eks describe-cluster --name production-eks-cluster > dr-drill-eks-before.json
aws rds describe-db-instances --db-instance-identifier production-postgres > dr-drill-rds-before.json

# 3. Simulate disaster: Destroy non-prod infrastructure
cd terraform
terraform destroy -var-file=environments/dev.tfvars -auto-approve

# 4. Start recovery timer
START_TIME=$(date +%s)

# 5. Execute recovery
terraform apply -var-file=environments/dev.tfvars -auto-approve

# 6. Verify recovery
aws eks describe-cluster --name dev-eks-cluster --query 'cluster.status'
aws rds describe-db-instances --db-instance-identifier dev-postgres --query 'DBInstances[0].DBInstanceStatus'

# 7. Calculate recovery time
END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))
echo "Recovery completed in $RECOVERY_TIME seconds" | tee -a dr-drill-log.txt
echo "Target RTO: 1800 seconds (30 minutes)" | tee -a dr-drill-log.txt

# 8. Document results and lessons learned
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Morning health check
aws eks describe-cluster --name production-eks-cluster --query 'cluster.status'
aws rds describe-db-instances --db-instance-identifier production-postgres --query 'DBInstances[0].DBInstanceStatus'

# Check CloudWatch alarms
aws cloudwatch describe-alarms --state-value ALARM

# Check for drift
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation/terraform
terraform plan -var-file=environments/prod.tfvars | tee drift-check-$(date +%Y%m%d).log
```

#### Weekly Tasks
```bash
# Review node health and scaling
aws eks describe-nodegroup --cluster-name production-eks-cluster --nodegroup-name default-node-group
kubectl top nodes

# Review RDS performance
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=production-postgres \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average,Maximum

# Review costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=TAG,Key=Project
```

#### Monthly Tasks
```bash
# Update EKS add-ons
aws eks list-addons --cluster-name production-eks-cluster
aws eks update-addon --cluster-name production-eks-cluster --addon-name vpc-cni --addon-version latest

# Review and update security groups
aws ec2 describe-security-groups --filters "Name=tag:Project,Values=aws-infra-automation"

# Test disaster recovery procedures (see DR Drill above)

# Review and update documentation
git pull
# Review this runbook and update as needed
```

### Upgrade Procedures

#### Upgrade EKS Cluster
```bash
# 1. Check current version
aws eks describe-cluster --name production-eks-cluster --query 'cluster.version'

# 2. Review upgrade guide
# https://docs.aws.amazon.com/eks/latest/userguide/update-cluster.html

# 3. Update in non-prod first
aws eks update-cluster-version --name dev-eks-cluster --kubernetes-version 1.28

# 4. Monitor update
aws eks describe-update --name dev-eks-cluster --update-id <update-id>

# 5. Update node groups
aws eks update-nodegroup-version --cluster-name dev-eks-cluster --nodegroup-name default-node-group

# 6. Verify and test
kubectl get nodes
kubectl version

# 7. Update production (during maintenance window)
aws eks update-cluster-version --name production-eks-cluster --kubernetes-version 1.28
```

#### Upgrade RDS Version
```bash
# 1. Check available versions
aws rds describe-db-engine-versions \
  --engine postgres \
  --engine-version 14.9 \
  --query 'DBEngineVersions[*].ValidUpgradeTarget[*].EngineVersion'

# 2. Create snapshot before upgrade
aws rds create-db-snapshot \
  --db-instance-identifier production-postgres \
  --db-snapshot-identifier pre-upgrade-$(date +%Y%m%d)

# 3. Test upgrade in non-prod
aws rds modify-db-instance \
  --db-instance-identifier dev-postgres \
  --engine-version 15.4 \
  --apply-immediately

# 4. Upgrade production (during maintenance window)
aws rds modify-db-instance \
  --db-instance-identifier production-postgres \
  --engine-version 15.4 \
  --no-apply-immediately

# 5. Monitor upgrade during next maintenance window
aws rds describe-db-instances --db-instance-identifier production-postgres
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Terraform Apply Fails with State Lock

**Symptoms:**
```
Error: Error locking state: Error acquiring the state lock
```

**Solution:**
```bash
# Check who has the lock
terraform force-unlock <lock-id>

# If lock is stale (previous run crashed)
terraform force-unlock -force <lock-id>

# Verify state
terraform state list
```

#### Issue: EKS Nodes Not Joining Cluster

**Diagnosis:**
```bash
# Check node group configuration
aws eks describe-nodegroup --cluster-name production-eks-cluster --nodegroup-name default-node-group

# Check nodes in Auto Scaling group
ASG_NAME=$(aws eks describe-nodegroup --cluster-name production-eks-cluster --nodegroup-name default-node-group --query 'nodegroup.resources.autoScalingGroups[0].name' --output text)
aws autoscaling describe-auto-scaling-instances --output table

# Check CloudWatch logs for node bootstrap errors
aws logs tail /aws/eks/production-eks-cluster/cluster --follow
```

**Solution:**
```bash
# Verify IAM role has correct permissions
aws iam get-role --role-name <node-role-name>

# Check security groups allow communication
aws ec2 describe-security-groups --group-ids <cluster-sg> <node-sg>

# Recreate node group if needed
aws eks delete-nodegroup --cluster-name production-eks-cluster --nodegroup-name default-node-group
# Wait for deletion to complete
aws eks create-nodegroup --cluster-name production-eks-cluster --nodegroup-name default-node-group --subnets <subnet-ids> --node-role <role-arn>
```

#### Issue: RDS Connection Timeout

**Diagnosis:**
```bash
# Check RDS endpoint
aws rds describe-db-instances --db-instance-identifier production-postgres --query 'DBInstances[0].Endpoint'

# Check security group rules
aws ec2 describe-security-groups --group-ids <db-security-group>

# Test connectivity from EC2 or EKS node
# SSH to node or use kubectl exec
psql -h <rds-endpoint> -U <username> -d postgres
```

**Solution:**
```bash
# Update security group to allow connections
aws ec2 authorize-security-group-ingress \
  --group-id <db-security-group> \
  --protocol tcp \
  --port 5432 \
  --source-group <app-security-group>

# Verify parameter group settings
aws rds describe-db-parameters --db-parameter-group-name <parameter-group>
```

#### Issue: High AWS Costs

**Investigation:**
```bash
# Check cost breakdown
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Identify expensive resources
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=TAG,Key=Name
```

**Optimization:**
```bash
# Stop non-prod RDS instances after hours
aws rds stop-db-instance --db-instance-identifier dev-postgres

# Scale down non-prod EKS nodes
aws eks update-nodegroup-config \
  --cluster-name dev-eks-cluster \
  --nodegroup-name default-node-group \
  --scaling-config minSize=0,maxSize=2,desiredSize=0

# Review and remove unused resources
aws ec2 describe-volumes --filters "Name=status,Values=available"
aws ec2 describe-snapshots --owner-ids self --query 'Snapshots[?StartTime<`2025-01-01`]'
```

---

## Quick Reference Card

### Most Common Operations

```bash
# Check infrastructure health
aws eks describe-cluster --name production-eks-cluster --query 'cluster.status'
aws rds describe-db-instances --db-instance-identifier production-postgres --query 'DBInstances[0].DBInstanceStatus'

# Deploy infrastructure (Terraform)
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation/terraform
terraform plan -var-file=environments/prod.tfvars
terraform apply -var-file=environments/prod.tfvars

# Connect to EKS
aws eks update-kubeconfig --name production-eks-cluster --region us-east-1
kubectl get nodes

# Scale EKS nodes
aws eks update-nodegroup-config --cluster-name production-eks-cluster --nodegroup-name default-node-group --scaling-config desiredSize=5

# Create RDS snapshot
aws rds create-db-snapshot --db-instance-identifier production-postgres --db-snapshot-identifier manual-$(date +%Y%m%d)

# Check for drift
cd terraform && terraform plan

# Emergency rollback
cd terraform && terraform apply -var-file=backups/previous-config.tfvars
```

### Emergency Response

```bash
# P0: EKS cluster unreachable
aws eks describe-cluster --name production-eks-cluster
aws support create-case --subject "EKS Cluster Down" --service-code amazon-eks --severity-code urgent

# P0: RDS down
aws rds reboot-db-instance --db-instance-identifier production-postgres --force-failover
# Monitor: watch -n 5 'aws rds describe-db-instances --db-instance-identifier production-postgres --query "DBInstances[0].DBInstanceStatus"'

# P1: All nodes unhealthy
kubectl get nodes
aws eks describe-nodegroup --cluster-name production-eks-cluster --nodegroup-name default-node-group
# Force refresh: kubectl drain <node> && kubectl delete node <node>

# Emergency infrastructure redeployment
# ⚠️ DANGER: This will destroy ALL production infrastructure!
# ⚠️ Only use as absolute last resort with approval from VP Engineering
# ⚠️ Ensure backups are recent before proceeding
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation/terraform

# Safer approach: Targeted resource recreation
# terraform taint aws_eks_cluster.this
# terraform apply -var-file=environments/prod.tfvars

# Complete redeployment (requires multiple confirmations):
# Step 1: Verify you have recent backups
# Step 2: Get written approval from leadership
# Step 3: Export current state for recovery
terraform show > state-backup-$(date +%Y%m%d-%H%M%S).txt
# Step 4: Destroy (will prompt for confirmation - do NOT use -auto-approve)
terraform destroy -var-file=environments/prod.tfvars
# Step 5: Redeploy (will prompt for confirmation - do NOT use -auto-approve)
terraform apply -var-file=environments/prod.tfvars
cd /home/user/Portfolio-Project/projects/1-aws-infrastructure-automation/terraform
terraform destroy -var-file=environments/prod.tfvars
terraform apply -var-file=environments/prod.tfvars -auto-approve
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
