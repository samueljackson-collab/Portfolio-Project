# Cost Optimization Tooling - Implementation Playbook

**Version:** 1.0.0 | **Last Updated:** 2025-11-10

## Overview

This playbook provides step-by-step instructions for implementing, deploying, and operating Cost Optimization Tooling from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Infrastructure Provisioning](#infrastructure-provisioning)
4. [Application Deployment](#application-deployment)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Going Live](#going-live)

---

## Prerequisites

### Required Tools

```bash
# Verify installations
terraform version  # >= 1.5.0
docker version     # >= 20.10
kubectl version    # >= 1.27
python --version   # >= 3.9
aws --version      # >= 2.0
```

### Required Access

- [ ] AWS account with admin access
- [ ] GitHub repository access
- [ ] PagerDuty account for alerting
- [ ] Grafana Cloud account (or self-hosted)

### Cost Estimate

| Component | Monthly Cost (USD) |
|-----------|-------------------|
| EC2 Instances | $100-200 |
| RDS Database | $50-150 |
| Load Balancer | $20-50 |
| **Total** | **$170-400** |

---

## Initial Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/yourorg/portfolio.git
cd portfolio/P08-cost-optimization
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env
```

**Required Variables:**

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cost-optimization
DB_USER=admin
DB_PASSWORD=<generate-strong-password>

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=<generate-secret-key>
```

### Step 3: Install Dependencies

```bash
# Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Terraform providers
cd infrastructure/terraform
terraform init
```

---

## Infrastructure Provisioning

### Step 1: Configure Terraform Backend

```bash
# Run bootstrap script to create S3 backend
../../scripts/bootstrap_remote_state.sh cost-optimization us-east-1

# Output will show:
# S3 Bucket: cost-optimization-tfstate-xxxxx
# DynamoDB Table: cost-optimization-tfstate-lock
```

Edit `infrastructure/terraform/backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "cost-optimization-tfstate-xxxxx"  # From bootstrap output
    key            = "cost-optimization/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "cost-optimization-tfstate-lock"
    encrypt        = true
  }
}
```

### Step 2: Plan Infrastructure Changes

```bash
cd infrastructure/terraform

# Review planned changes
terraform plan -out=tfplan

# Expected resources:
# + VPC with public/private subnets
# + RDS PostgreSQL instance
# + ElastiCache Redis cluster
# + ECS cluster with Fargate tasks
# + Application Load Balancer
# + Security groups
# + IAM roles
```

### Step 3: Provision Infrastructure

```bash
# Apply Terraform configuration
terraform apply tfplan

# This will take 10-15 minutes
# Output will show:
# load_balancer_dns = "xxx.us-east-1.elb.amazonaws.com"
# rds_endpoint = "xxx.rds.amazonaws.com:5432"
# redis_endpoint = "xxx.cache.amazonaws.com:6379"
```

### Step 4: Verify Infrastructure

```bash
# Check VPC
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=cost-optimization-vpc"

# Check RDS
aws rds describe-db-instances --db-instance-identifier cost-optimization-db

# Check ECS cluster
aws ecs describe-clusters --clusters cost-optimization-cluster
```

---

## Application Deployment

### Step 1: Build Docker Image

```bash
# Build image
docker build -t cost-optimization:latest .

# Test locally
docker run -p 8080:8080 --env-file .env cost-optimization:latest

# Verify health
curl http://localhost:8080/health
```

### Step 2: Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag cost-optimization:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/cost-optimization:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/cost-optimization:latest
```

### Step 3: Run Database Migrations

```bash
# Connect to RDS via bastion host
ssh -L 5432:<rds-endpoint>:5432 bastion.example.com

# Run migrations
export DATABASE_URL="postgresql://admin:<password>@localhost:5432/cost-optimization"
alembic upgrade head
```

### Step 4: Deploy to ECS

```bash
# Update ECS task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Update service
aws ecs update-service \
  --cluster cost-optimization-cluster \
  --service cost-optimization-service \
  --force-new-deployment

# Monitor deployment
aws ecs wait services-stable \
  --cluster cost-optimization-cluster \
  --services cost-optimization-service
```

---

## Configuration

### Step 1: Configure Monitoring

```bash
# Deploy Prometheus and Grafana
cd infrastructure/monitoring
docker-compose up -d

# Import dashboards
curl -X POST http://localhost:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d @grafana-dashboard.json
```

### Step 2: Configure Alerting

```bash
# Set up PagerDuty integration
export PAGERDUTY_SERVICE_KEY="your-service-key"

# Configure alert rules
kubectl apply -f infrastructure/monitoring/alert-rules.yaml

# Test alerting
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d @test-alert.json
```

### Step 3: Configure Backups

```bash
# Enable automated RDS backups
aws rds modify-db-instance \
  --db-instance-identifier cost-optimization-db \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"

# Test backup script
./scripts/backup_database.sh
```

---

## Testing

### Step 1: Run Unit Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests with coverage
pytest tests/unit --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Step 2: Run Integration Tests

```bash
# Start test dependencies
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration -v

# Cleanup
docker-compose -f docker-compose.test.yml down
```

### Step 3: Run Load Tests

```bash
# Install k6 load testing tool
brew install k6

# Run load test
k6 run tests/performance/load_test.js

# Expected results:
# - RPS: >100 requests/second
# - P95 latency: <500ms
# - Error rate: <1%
```

---

## Going Live

### Pre-Launch Checklist

- [ ] All tests passing
- [ ] Security scan completed (no critical issues)
- [ ] Load testing passed
- [ ] Monitoring and alerting configured
- [ ] Backups configured and tested
- [ ] DR drill completed successfully
- [ ] Runbook reviewed by team
- [ ] On-call rotation scheduled
- [ ] Stakeholders notified of launch date

### Launch Procedure

```bash
# 1. Final smoke tests in staging
make test ENV=staging

# 2. Create release tag
git tag -a v1.0.0 -m "Initial production release"
git push origin v1.0.0

# 3. Deploy to production
make deploy ENV=production

# 4. Verify health
curl https://api.example.com/health

# 5. Monitor for 1 hour
# Watch Grafana dashboard for anomalies
```

### Post-Launch

```bash
# Monitor key metrics for 24 hours:
# - Error rate should be <0.1%
# - Latency P95 should be <500ms
# - CPU usage should be <70%
# - Memory usage should be stable

# If issues detected:
# 1. Check runbook for troubleshooting steps
# 2. If severe, execute rollback procedure
# 3. Create incident post-mortem
```

---

## Troubleshooting

### Common Issues

**Issue:** Terraform apply fails with "Resource already exists"

**Solution:**
```bash
# Import existing resource
terraform import aws_vpc.main vpc-xxxxx

# Or destroy and recreate
terraform destroy -target=aws_vpc.main
terraform apply
```

**Issue:** Docker image won't build

**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t cost-optimization:latest .
```

**Issue:** Database migration fails

**Solution:**
```bash
# Check current migration version
alembic current

# Rollback to previous version
alembic downgrade -1

# Reapply migration
alembic upgrade head
```

---

## Next Steps

1. **Optimize Performance:** Review application metrics and optimize bottlenecks
2. **Enhance Security:** Conduct security audit and penetration testing
3. **Add Features:** Implement additional functionality per roadmap
4. **Improve Docs:** Update documentation based on operational learnings

---

## References

- [Enterprise Engineer's Handbook](../../../docs/PRJ-MASTER-HANDBOOK/README.md)
- [IT Playbook](../../../docs/PRJ-MASTER-PLAYBOOK/README.md)
- [Configuration Guide](../../../CONFIGURATION_GUIDE.md)
- [RUNBOOK](./RUNBOOK.md)

---

**Maintained by:** Cost Optimization Tooling Team
**Last Review:** 2025-11-10
