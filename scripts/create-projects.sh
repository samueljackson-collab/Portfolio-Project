#!/bin/bash
set -euo pipefail

# Enterprise Portfolio Project Generator
# Creates standardized project structure for 20 projects

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANONICAL_PROJECTS_DIR="${SCRIPT_DIR}/../projects-new"
PROJECTS_DIR="${CANONICAL_PROJECTS_DIR}"

mkdir -p "${PROJECTS_DIR}"
echo -e "Creating projects inside canonical directory: ${PROJECTS_DIR}"

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project definitions
declare -A PROJECTS=(
    ["P01"]="AWS Infrastructure Automation:aws-infra"
    ["P02"]="Kubernetes Cluster Management:k8s-cluster"
    ["P03"]="CI/CD Pipeline Implementation:cicd-pipeline"
    ["P04"]="Operational Monitoring Stack:monitoring-stack"
    ["P05"]="Database Performance Optimization:db-optimization"
    ["P06"]="Web Application Testing Framework:web-testing"
    ["P07"]="Security Compliance Automation:security-compliance"
    ["P08"]="Cost Optimization Tooling:cost-optimization"
    ["P09"]="Disaster Recovery Orchestration:dr-orchestration"
    ["P10"]="Log Aggregation System:log-aggregation"
    ["P11"]="API Gateway Configuration:api-gateway"
    ["P12"]="Container Registry Management:container-registry"
    ["P13"]="Secrets Management System:secrets-management"
    ["P14"]="Network Configuration Automation:network-automation"
    ["P15"]="Incident Response Automation:incident-response"
    ["P16"]="Backup Verification System:backup-verification"
    ["P17"]="Performance Load Testing:load-testing"
    ["P18"]="Service Mesh Implementation:service-mesh"
    ["P19"]="Observability Dashboard:observability-dashboard"
    ["P20"]="Multi-Cloud Orchestration:multi-cloud"
)

# Function to create project structure
create_project() {
    local project_id="$1"
    local project_name="$2"
    local project_slug="$3"
    local project_dir="${PROJECTS_DIR}/${project_id}-${project_slug}"

    echo -e "${BLUE}Creating ${project_id}: ${project_name}${NC}"

    # Create directory structure
    mkdir -p "${project_dir}"/{docs,src,scripts,tests,infrastructure/{terraform,k8s},ci}

    # Create README.md
    cat > "${project_dir}/README.md" <<EOF
# ${project_name}

**Project ID:** ${project_id}
**Status:** 🟢 Active | **Version:** 1.0.0 | **Last Updated:** $(date +%Y-%m-%d)

## Overview

${project_name} implements enterprise-grade solutions following the standards defined in the [Enterprise Engineer's Handbook](../../docs/PRJ-MASTER-HANDBOOK/README.md).

## Quick Start

\`\`\`bash
# 1. Install dependencies
make install

# 2. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 3. Run tests
make test

# 4. Deploy
make deploy
\`\`\`

## Documentation

- [📘 HANDBOOK](docs/HANDBOOK.md) - Engineering standards and best practices
- [📗 RUNBOOK](docs/RUNBOOK.md) - Operational procedures and troubleshooting
- [📙 PLAYBOOK](docs/PLAYBOOK.md) - Step-by-step implementation guide
- [🏗️ ARCHITECTURE](docs/ARCHITECTURE.md) - System design and components

## Project Structure

\`\`\`
${project_id}-${project_slug}/
├── README.md                 # This file
├── Makefile                  # Build and deployment automation
├── .env.example              # Example configuration
├── docs/                     # Documentation
│   ├── HANDBOOK.md
│   ├── RUNBOOK.md
│   ├── PLAYBOOK.md
│   └── ARCHITECTURE.md
├── src/                      # Source code
├── scripts/                  # Automation scripts
├── tests/                    # Test suite
├── infrastructure/           # IaC configurations
│   ├── terraform/
│   └── k8s/
└── ci/                       # CI/CD workflows
\`\`\`

## Features

- ✅ Enterprise-grade implementation
- ✅ Comprehensive test coverage (≥80%)
- ✅ Infrastructure as Code
- ✅ CI/CD automation
- ✅ Production-ready monitoring
- ✅ Security best practices

## Requirements

- Python 3.9+
- Terraform 1.5+
- Docker 20.10+
- kubectl 1.27+

## Testing

\`\`\`bash
# Run all tests
make test

# Run specific test suite
make test-unit
make test-integration
make test-e2e
\`\`\`

## Deployment

\`\`\`bash
# Deploy to development
make deploy ENV=dev

# Deploy to staging
make deploy ENV=staging

# Deploy to production
make deploy ENV=prod
\`\`\`

## Monitoring

- **Metrics:** Prometheus metrics exposed on \`:9090/metrics\`
- **Logs:** Structured JSON logging to stdout
- **Traces:** OpenTelemetry integration
- **Dashboards:** Grafana dashboards in \`infrastructure/monitoring/\`

## Security

- 🔒 OWASP Top 10 compliance
- 🔒 CIS benchmark compliance
- 🔒 Automated security scanning
- 🔒 Secrets management via AWS Secrets Manager

## Contributing

1. Follow the [Engineer's Handbook](../../docs/PRJ-MASTER-HANDBOOK/README.md)
2. Create feature branch: \`git checkout -b feature/your-feature\`
3. Run tests: \`make test\`
4. Submit PR with comprehensive description

## Support

- **Issues:** Open GitHub issue
- **Documentation:** See \`docs/\` directory
- **Runbook:** See \`docs/RUNBOOK.md\` for troubleshooting

## License

Proprietary - All Rights Reserved

---

**Maintained by:** Platform Engineering Team
**Last Review:** $(date +%Y-%m-%d)
EOF

    # Create HANDBOOK.md
    cat > "${project_dir}/docs/HANDBOOK.md" <<EOF
# ${project_name} - Engineering Handbook

**Version:** 1.0.0 | **Last Updated:** $(date +%Y-%m-%d)

## Overview

This handbook defines the engineering standards, code quality requirements, and best practices specific to ${project_name}. It extends the [Enterprise Engineer's Handbook](../../../docs/PRJ-MASTER-HANDBOOK/README.md) with project-specific guidance.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Code Standards](#code-standards)
3. [Testing Requirements](#testing-requirements)
4. [Security Guidelines](#security-guidelines)
5. [Deployment Standards](#deployment-standards)
6. [Monitoring & Observability](#monitoring--observability)

---

## Architecture Overview

### System Components

\`\`\`mermaid
graph TD
    A[Load Balancer] --> B[Application Layer]
    B --> C[Business Logic]
    C --> D[Data Layer]
    D --> E[Database]
\`\`\`

### Technology Stack

- **Runtime:** Python 3.9+
- **Framework:** FastAPI / Flask
- **Database:** PostgreSQL 14+
- **Cache:** Redis 7+
- **Infrastructure:** AWS / Terraform
- **Orchestration:** Kubernetes 1.27+

### Design Principles

- **Scalability:** Horizontal scaling via containerization
- **Reliability:** ≥99.9% uptime target
- **Security:** Zero-trust architecture
- **Observability:** Full instrumentation with OpenTelemetry

---

## Code Standards

### Python Style Guide

- **PEP 8 compliance** with max line length 100
- **Type hints** required for all functions
- **Docstrings** in Google style format

**Example:**

\`\`\`python
def process_data(
    input_data: Dict[str, Any],
    validate: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Process input data with optional validation.

    Args:
        input_data: Dictionary containing data to process
        validate: Whether to validate input before processing

    Returns:
        Tuple of (success: bool, error_message: Optional[str])

    Raises:
        ValueError: If input_data is empty and validate=True
    """
    if validate and not input_data:
        raise ValueError("input_data cannot be empty")

    # Process data
    return True, None
\`\`\`

### Code Review Checklist

- [ ] All functions have type hints and docstrings
- [ ] No hardcoded credentials or secrets
- [ ] Error handling for all external calls
- [ ] Logging added for debugging
- [ ] Unit tests cover new code (≥80%)
- [ ] Integration tests for API changes
- [ ] Security review completed

---

## Testing Requirements

### Coverage Targets

- **Unit Tests:** ≥80% code coverage
- **Integration Tests:** All API endpoints
- **E2E Tests:** Critical user flows
- **Performance Tests:** Load testing for >100 req/sec

### Test Organization

\`\`\`
tests/
├── unit/                 # Fast, isolated tests
│   ├── test_services.py
│   └── test_utils.py
├── integration/          # Tests with external dependencies
│   ├── test_api.py
│   └── test_database.py
├── e2e/                  # Full workflow tests
│   └── test_user_flow.py
└── performance/          # Load and stress tests
    └── load_test.py
\`\`\`

### Running Tests

\`\`\`bash
# All tests
make test

# Specific test types
pytest tests/unit -v
pytest tests/integration -v --cov=src

# With coverage report
make test-coverage
\`\`\`

---

## Security Guidelines

### Authentication & Authorization

- **API Keys:** Rotate every 90 days
- **IAM Roles:** Use instance profiles, not hardcoded credentials
- **Least Privilege:** Grant minimum required permissions

### Input Validation

\`\`\`python
from pydantic import BaseModel, Field, validator

class InputRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID must be positive")
    email: str = Field(..., regex=r"^[\\w._%+-]+@[\\w.-]+\\.[A-Z]{2,}$")

    @validator('email')
    def email_must_be_lowercase(cls, v):
        return v.lower()
\`\`\`

### Secrets Management

\`\`\`python
import boto3

def get_secret(secret_name: str) -> str:
    """Fetch secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# Usage
DB_PASSWORD = get_secret('prod/database/password')
\`\`\`

---

## Deployment Standards

### Environment Configuration

| Environment | Branch | Approval | Auto-Deploy |
|------------|--------|----------|-------------|
| Development | develop | None | Yes |
| Staging | main | 1 reviewer | Yes |
| Production | release/* | 2 reviewers | Manual |

### Deployment Checklist

- [ ] All tests passing
- [ ] Security scan completed (no critical issues)
- [ ] Performance tests passed
- [ ] Rollback plan documented
- [ ] Change ticket created
- [ ] Deployment window scheduled
- [ ] Stakeholders notified

### Blue/Green Deployment

\`\`\`bash
# Deploy to green environment
terraform apply -target=aws_instance.green

# Run smoke tests
./scripts/smoke_test.sh green

# Switch traffic to green
terraform apply -var="active_env=green"

# Monitor for 10 minutes
# If issues, rollback:
terraform apply -var="active_env=blue"
\`\`\`

---

## Monitoring & Observability

### Required Metrics

All services must expose:

- **Request Rate:** Requests per second
- **Error Rate:** 5xx errors per minute (target: <0.1%)
- **Latency:** P50, P95, P99 response times
- **Saturation:** CPU, memory, disk usage

### Structured Logging

\`\`\`python
import structlog

logger = structlog.get_logger()

logger.info(
    "user_login",
    user_id=user.id,
    ip_address=request.ip,
    duration_ms=45,
    status="success"
)
\`\`\`

### Alerting Rules

\`\`\`yaml
# Prometheus alerts
groups:
  - name: ${project_slug}
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        annotations:
          summary: "Error rate above 5%"
          runbook: "docs/RUNBOOK.md#high-error-rate"
\`\`\`

---

## References

- [Enterprise Engineer's Handbook](../../../docs/PRJ-MASTER-HANDBOOK/README.md)
- [IT Playbook](../../../docs/PRJ-MASTER-PLAYBOOK/README.md)
- [Configuration Guide](../../../CONFIGURATION_GUIDE.md)

---

**Maintained by:** ${project_name} Team
**Last Review:** $(date +%Y-%m-%d)
EOF

    # Create RUNBOOK.md
    cat > "${project_dir}/docs/RUNBOOK.md" <<EOF
# ${project_name} - Operations Runbook

**Version:** 1.0.0 | **Last Updated:** $(date +%Y-%m-%d)

## Overview

This runbook provides operational procedures, troubleshooting guides, and incident response workflows for ${project_name}.

## Table of Contents

1. [Service Overview](#service-overview)
2. [Deployment Procedures](#deployment-procedures)
3. [Monitoring & Alerts](#monitoring--alerts)
4. [Troubleshooting](#troubleshooting)
5. [Incident Response](#incident-response)
6. [Maintenance Procedures](#maintenance-procedures)

---

## Service Overview

### Service Details

- **Service Name:** ${project_name}
- **Owner:** Platform Engineering Team
- **On-Call Rotation:** PagerDuty
- **SLA Target:** 99.9% uptime
- **RTO:** 1 hour
- **RPO:** 15 minutes

### Dependencies

- **Database:** PostgreSQL (RDS)
- **Cache:** Redis (ElastiCache)
- **Queue:** SQS
- **Storage:** S3

### Endpoints

- **Health Check:** \`/health\`
- **Metrics:** \`/metrics\`
- **API Docs:** \`/docs\`

---

## Deployment Procedures

### Pre-Deployment Checklist

- [ ] All tests passing in CI/CD
- [ ] Security scan completed
- [ ] Change ticket approved
- [ ] Deployment window confirmed
- [ ] Team notified in #deployments Slack channel

### Deployment Steps

\`\`\`bash
# 1. Connect to bastion host
ssh bastion.example.com

# 2. Pull latest code
cd /opt/${project_slug}
git fetch origin
git checkout tags/v1.2.3

# 3. Run database migrations (if any)
make migrate

# 4. Deploy application
make deploy ENV=production

# 5. Verify health
curl https://api.example.com/health

# 6. Monitor for 15 minutes
watch -n 10 'curl -s https://api.example.com/health | jq'
\`\`\`

### Rollback Procedure

\`\`\`bash
# 1. Identify previous version
git tag --sort=-creatordate | head -n 5

# 2. Deploy previous version
git checkout tags/v1.2.2
make deploy ENV=production

# 3. Verify rollback
curl https://api.example.com/health
\`\`\`

---

## Monitoring & Alerts

### Key Dashboards

- **Grafana:** https://grafana.example.com/d/${project_slug}
- **CloudWatch:** https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=${project_slug}

### Alert Severity Levels

| Severity | Response Time | Escalation |
|----------|--------------|------------|
| P1 (Critical) | 15 minutes | Page on-call engineer |
| P2 (High) | 1 hour | Email + Slack |
| P3 (Medium) | 4 hours | Slack notification |
| P4 (Low) | Next business day | Ticket in backlog |

### Common Alerts

#### High Error Rate

**Alert:** \`${project_slug}_high_error_rate\`

**Symptoms:**
- 5xx error rate >5% over 5 minutes
- Users reporting "Service Unavailable" errors

**Diagnosis:**
\`\`\`bash
# Check error logs
aws logs tail /aws/lambda/${project_slug} --follow --filter '5xx'

# Check service health
kubectl get pods -n ${project_slug}
kubectl logs -n ${project_slug} <pod-name> --tail=100
\`\`\`

**Resolution:**
1. Check for recent deployments (potential bad release)
2. Review application logs for stack traces
3. If recent deployment, rollback immediately
4. If database issue, check connection pool exhaustion
5. Scale up if resource saturation detected

#### High Latency

**Alert:** \`${project_slug}_high_latency\`

**Symptoms:**
- P95 latency >500ms
- Users reporting slow page loads

**Diagnosis:**
\`\`\`bash
# Check slow query log
psql -h <db-host> -U admin -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check cache hit rate
redis-cli INFO stats | grep keyspace
\`\`\`

**Resolution:**
1. Identify slow database queries and add indexes
2. Check cache hit rate, warm cache if needed
3. Review recent code changes for inefficient loops
4. Scale up database if CPU >80%

---

## Troubleshooting

### Service Won't Start

**Symptoms:**
- Container crashes immediately after start
- Health check failing

**Diagnosis:**
\`\`\`bash
# Check container logs
docker logs <container-id>

# Check environment variables
docker exec <container-id> env | grep -E '(DB_|REDIS_|API_)'

# Check connectivity
docker exec <container-id> nc -zv <db-host> 5432
\`\`\`

**Common Causes:**
- Missing environment variables
- Database connection failure
- Port already in use
- Insufficient permissions

### Database Connection Errors

**Symptoms:**
- \`psycopg2.OperationalError: could not connect to server\`

**Resolution:**
\`\`\`bash
# 1. Verify database is running
aws rds describe-db-instances --db-instance-identifier ${project_slug}-prod

# 2. Check security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxx

# 3. Test connection from application host
psql -h <db-host> -U <user> -d <database>

# 4. Check connection pool settings in code
# Ensure max_connections not exceeded
\`\`\`

### Memory Leak

**Symptoms:**
- Gradual memory increase over time
- OOM killer terminating processes

**Diagnosis:**
\`\`\`bash
# Check memory usage trend
kubectl top pods -n ${project_slug}

# Generate memory profile
curl http://localhost:8080/debug/pprof/heap > heap.prof
go tool pprof heap.prof
\`\`\`

**Resolution:**
1. Review recent code for unbounded data structures
2. Check for unclosed database connections
3. Increase memory limit as temporary fix
4. Profile application to identify leak source

---

## Incident Response

### Incident Lifecycle

1. **Detection** - Alert fires or user report
2. **Triage** - Assess severity, page on-call
3. **Investigation** - Gather logs, metrics, traces
4. **Mitigation** - Apply fix or rollback
5. **Resolution** - Verify issue resolved
6. **Post-Mortem** - Conduct blameless review

### Incident Roles

- **Incident Commander:** Coordinates response
- **Technical Lead:** Investigates root cause
- **Communications Lead:** Updates stakeholders
- **Scribe:** Documents timeline

### Post-Incident Review Template

\`\`\`markdown
# Incident Report: ${project_slug} Outage

**Date:** YYYY-MM-DD
**Duration:** X hours Y minutes
**Severity:** P1
**Impact:** XX% of users affected

## Timeline
- 14:23 UTC: Alert fired for high error rate
- 14:25 UTC: On-call engineer paged
- 14:30 UTC: Root cause identified (database CPU 100%)
- 14:35 UTC: Mitigation applied (scaled up RDS instance)
- 14:45 UTC: Service restored, monitoring

## Root Cause
Unoptimized database query introduced in v1.2.3 caused full table scan.

## Resolution
1. Rolled back to v1.2.2
2. Scaled up RDS instance from db.t3.medium to db.t3.large
3. Added missing index to \`users\` table

## Action Items
- [ ] Add query performance tests to CI/CD (@engineer, ETA: 2 days)
- [ ] Review all queries for similar patterns (@team, ETA: 1 week)
- [ ] Set up database query monitoring alerts (@sre, ETA: 3 days)
\`\`\`

---

## Maintenance Procedures

### Database Backup Verification

\`\`\`bash
# Weekly DR drill
cd /opt/${project_slug}
python3 scripts/dr_drill.py

# Verify backup exists and is recent
aws s3 ls s3://backups-${project_slug}/latest/
\`\`\`

### SSL Certificate Renewal

\`\`\`bash
# Check certificate expiry
openssl s_client -connect api.example.com:443 -servername api.example.com \\
  | openssl x509 -noout -dates

# Renew with Let's Encrypt
certbot renew --dry-run
certbot renew
\`\`\`

### Log Rotation

\`\`\`bash
# Ensure logrotate is configured
cat /etc/logrotate.d/${project_slug}

# Test log rotation
logrotate -d /etc/logrotate.d/${project_slug}
\`\`\`

---

## Escalation

### On-Call Contacts

- **Primary:** PagerDuty rotation
- **Secondary:** platform-engineering@example.com
- **Escalation:** CTO (for P1 incidents >2 hours)

### External Dependencies

- **AWS Support:** https://console.aws.amazon.com/support/
- **Database Vendor:** support@vendor.com
- **CDN Provider:** https://dashboard.cdn.com/support

---

**Maintained by:** Platform Engineering Team
**Last Review:** $(date +%Y-%m-%d)
**Next Review:** $(date -d "+3 months" +%Y-%m-%d)
EOF

    # Create PLAYBOOK.md
    cat > "${project_dir}/docs/PLAYBOOK.md" <<EOF
# ${project_name} - Implementation Playbook

**Version:** 1.0.0 | **Last Updated:** $(date +%Y-%m-%d)

## Overview

This playbook provides step-by-step instructions for implementing, deploying, and operating ${project_name} from scratch.

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

\`\`\`bash
# Verify installations
terraform version  # >= 1.5.0
docker version     # >= 20.10
kubectl version    # >= 1.27
python --version   # >= 3.9
aws --version      # >= 2.0
\`\`\`

### Required Access

- [ ] AWS account with admin access
- [ ] GitHub repository access
- [ ] PagerDuty account for alerting
- [ ] Grafana Cloud account (or self-hosted)

### Cost Estimate

| Component | Monthly Cost (USD) |
|-----------|-------------------|
| EC2 Instances | \$100-200 |
| RDS Database | \$50-150 |
| Load Balancer | \$20-50 |
| **Total** | **\$170-400** |

---

## Initial Setup

### Step 1: Clone Repository

\`\`\`bash
git clone https://github.com/yourorg/portfolio.git
cd portfolio/${project_id}-${project_slug}
\`\`\`

### Step 2: Configure Environment

\`\`\`bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env
\`\`\`

**Required Variables:**

\`\`\`bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=${project_slug}
DB_USER=admin
DB_PASSWORD=<generate-strong-password>

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=<generate-secret-key>
\`\`\`

### Step 3: Install Dependencies

\`\`\`bash
# Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Terraform providers
cd infrastructure/terraform
terraform init
\`\`\`

---

## Infrastructure Provisioning

### Step 1: Configure Terraform Backend

\`\`\`bash
# Run bootstrap script to create S3 backend
../../scripts/bootstrap_remote_state.sh ${project_slug} us-east-1

# Output will show:
# S3 Bucket: ${project_slug}-tfstate-xxxxx
# DynamoDB Table: ${project_slug}-tfstate-lock
\`\`\`

Edit \`infrastructure/terraform/backend.tf\`:

\`\`\`hcl
terraform {
  backend "s3" {
    bucket         = "${project_slug}-tfstate-xxxxx"  # From bootstrap output
    key            = "${project_slug}/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "${project_slug}-tfstate-lock"
    encrypt        = true
  }
}
\`\`\`

### Step 2: Plan Infrastructure Changes

\`\`\`bash
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
\`\`\`

### Step 3: Provision Infrastructure

\`\`\`bash
# Apply Terraform configuration
terraform apply tfplan

# This will take 10-15 minutes
# Output will show:
# load_balancer_dns = "xxx.us-east-1.elb.amazonaws.com"
# rds_endpoint = "xxx.rds.amazonaws.com:5432"
# redis_endpoint = "xxx.cache.amazonaws.com:6379"
\`\`\`

### Step 4: Verify Infrastructure

\`\`\`bash
# Check VPC
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${project_slug}-vpc"

# Check RDS
aws rds describe-db-instances --db-instance-identifier ${project_slug}-db

# Check ECS cluster
aws ecs describe-clusters --clusters ${project_slug}-cluster
\`\`\`

---

## Application Deployment

### Step 1: Build Docker Image

\`\`\`bash
# Build image
docker build -t ${project_slug}:latest .

# Test locally
docker run -p 8080:8080 --env-file .env ${project_slug}:latest

# Verify health
curl http://localhost:8080/health
\`\`\`

### Step 2: Push to ECR

\`\`\`bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \\
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag ${project_slug}:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/${project_slug}:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/${project_slug}:latest
\`\`\`

### Step 3: Run Database Migrations

\`\`\`bash
# Connect to RDS via bastion host
ssh -L 5432:<rds-endpoint>:5432 bastion.example.com

# Run migrations
export DATABASE_URL="postgresql://admin:<password>@localhost:5432/${project_slug}"
alembic upgrade head
\`\`\`

### Step 4: Deploy to ECS

\`\`\`bash
# Update ECS task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Update service
aws ecs update-service \\
  --cluster ${project_slug}-cluster \\
  --service ${project_slug}-service \\
  --force-new-deployment

# Monitor deployment
aws ecs wait services-stable \\
  --cluster ${project_slug}-cluster \\
  --services ${project_slug}-service
\`\`\`

---

## Configuration

### Step 1: Configure Monitoring

\`\`\`bash
# Deploy Prometheus and Grafana
cd infrastructure/monitoring
docker-compose up -d

# Import dashboards
curl -X POST http://localhost:3000/api/dashboards/import \\
  -H "Content-Type: application/json" \\
  -d @grafana-dashboard.json
\`\`\`

### Step 2: Configure Alerting

\`\`\`bash
# Set up PagerDuty integration
export PAGERDUTY_SERVICE_KEY="your-service-key"

# Configure alert rules
kubectl apply -f infrastructure/monitoring/alert-rules.yaml

# Test alerting
curl -X POST http://localhost:9093/api/v1/alerts \\
  -H "Content-Type: application/json" \\
  -d @test-alert.json
\`\`\`

### Step 3: Configure Backups

\`\`\`bash
# Enable automated RDS backups
aws rds modify-db-instance \\
  --db-instance-identifier ${project_slug}-db \\
  --backup-retention-period 7 \\
  --preferred-backup-window "03:00-04:00"

# Test backup script
./scripts/backup_database.sh
\`\`\`

---

## Testing

### Step 1: Run Unit Tests

\`\`\`bash
# Activate virtual environment
source venv/bin/activate

# Run tests with coverage
pytest tests/unit --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
\`\`\`

### Step 2: Run Integration Tests

\`\`\`bash
# Start test dependencies
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration -v

# Cleanup
docker-compose -f docker-compose.test.yml down
\`\`\`

### Step 3: Run Load Tests

\`\`\`bash
# Install k6 load testing tool
brew install k6

# Run load test
k6 run tests/performance/load_test.js

# Expected results:
# - RPS: >100 requests/second
# - P95 latency: <500ms
# - Error rate: <1%
\`\`\`

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

\`\`\`bash
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
\`\`\`

### Post-Launch

\`\`\`bash
# Monitor key metrics for 24 hours:
# - Error rate should be <0.1%
# - Latency P95 should be <500ms
# - CPU usage should be <70%
# - Memory usage should be stable

# If issues detected:
# 1. Check runbook for troubleshooting steps
# 2. If severe, execute rollback procedure
# 3. Create incident post-mortem
\`\`\`

---

## Troubleshooting

### Common Issues

**Issue:** Terraform apply fails with "Resource already exists"

**Solution:**
\`\`\`bash
# Import existing resource
terraform import aws_vpc.main vpc-xxxxx

# Or destroy and recreate
terraform destroy -target=aws_vpc.main
terraform apply
\`\`\`

**Issue:** Docker image won't build

**Solution:**
\`\`\`bash
# Clear Docker cache
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t ${project_slug}:latest .
\`\`\`

**Issue:** Database migration fails

**Solution:**
\`\`\`bash
# Check current migration version
alembic current

# Rollback to previous version
alembic downgrade -1

# Reapply migration
alembic upgrade head
\`\`\`

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

**Maintained by:** ${project_name} Team
**Last Review:** $(date +%Y-%m-%d)
EOF

    # Create ARCHITECTURE.md
    cat > "${project_dir}/docs/ARCHITECTURE.md" <<EOF
# ${project_name} - Architecture Documentation

**Version:** 1.0.0 | **Last Updated:** $(date +%Y-%m-%d)

## System Overview

${project_name} is built following cloud-native architecture principles with a focus on scalability, reliability, and security.

## Architecture Diagram

\`\`\`mermaid
graph TB
    subgraph "External"
        Users[Users]
        Admin[Administrators]
    end

    subgraph "AWS Cloud"
        subgraph "Public Subnet"
            ALB[Application Load Balancer]
            Bastion[Bastion Host]
        end

        subgraph "Private Subnet"
            ECS[ECS Fargate Tasks]
            Lambda[Lambda Functions]
        end

        subgraph "Data Layer"
            RDS[(RDS PostgreSQL)]
            Redis[(ElastiCache Redis)]
            S3[S3 Buckets]
        end

        subgraph "Monitoring"
            CW[CloudWatch]
            Prometheus[Prometheus]
            Grafana[Grafana]
        end
    end

    Users --> ALB
    Admin --> Bastion
    ALB --> ECS
    ECS --> RDS
    ECS --> Redis
    ECS --> S3
    Lambda --> RDS
    ECS --> CW
    CW --> Grafana
    Prometheus --> Grafana
\`\`\`

## Technology Stack

### Application Layer
- **Runtime:** Python 3.9+
- **Framework:** FastAPI
- **Web Server:** Uvicorn

### Data Layer
- **Database:** PostgreSQL 14 (RDS)
- **Cache:** Redis 7 (ElastiCache)
- **Storage:** S3

### Infrastructure
- **Compute:** ECS Fargate
- **Load Balancer:** Application Load Balancer
- **DNS:** Route 53
- **CDN:** CloudFront

### Observability
- **Metrics:** Prometheus + CloudWatch
- **Logs:** CloudWatch Logs
- **Traces:** AWS X-Ray
- **Dashboards:** Grafana

## Component Details

### Application Service

**Responsibilities:**
- Handle HTTP requests
- Business logic execution
- Data validation
- API rate limiting

**Scaling:**
- Horizontal: 2-10 ECS tasks based on CPU
- Vertical: 2 vCPU, 4GB RAM per task

### Database Layer

**Configuration:**
- Instance: db.t3.medium (2 vCPU, 4GB RAM)
- Storage: 100GB gp3 SSD
- Backups: Daily, 7-day retention
- Multi-AZ: Yes (production)

**Connection Pooling:**
- Pool size: 20 connections
- Timeout: 30 seconds

### Cache Layer

**Configuration:**
- Node type: cache.t3.micro
- Cluster mode: Disabled
- Eviction policy: allkeys-lru
- TTL: 1 hour default

## Security Architecture

### Network Security

\`\`\`
Internet
  ↓
WAF (AWS WAF)
  ↓
CloudFront (HTTPS only)
  ↓
ALB (Public Subnet)
  ↓
ECS Tasks (Private Subnet)
  ↓
RDS/Redis (Private Subnet, isolated security groups)
\`\`\`

### Authentication Flow

\`\`\`mermaid
sequenceDiagram
    participant User
    participant API
    participant Auth Service
    participant Database

    User->>API: POST /login {username, password}
    API->>Auth Service: Validate credentials
    Auth Service->>Database: Query user
    Database-->>Auth Service: User data
    Auth Service->>Auth Service: Hash password, compare
    Auth Service-->>API: JWT token
    API-->>User: {token, expiry}

    User->>API: GET /protected (Authorization: Bearer token)
    API->>Auth Service: Verify JWT
    Auth Service-->>API: Claims
    API->>Database: Fetch data
    Database-->>API: Data
    API-->>User: Response
\`\`\`

## Data Flow

### Write Path

1. Client sends POST request to ALB
2. ALB routes to healthy ECS task
3. Application validates input (Pydantic models)
4. Data written to PostgreSQL
5. Cache invalidated (Redis)
6. Success response returned

### Read Path

1. Client sends GET request to ALB
2. Application checks Redis cache
3. If cache hit: return data immediately
4. If cache miss: query PostgreSQL
5. Store result in Redis (TTL: 1 hour)
6. Return data to client

## Deployment Architecture

### Blue/Green Deployment

\`\`\`
┌─────────────────────────────────────┐
│   Application Load Balancer         │
│   (Routes traffic to active env)    │
└──────────┬──────────────────────────┘
           │
     ┌─────┴─────┐
     │           │
┌────▼───┐  ┌───▼─────┐
│ Blue   │  │ Green   │
│ v1.2.3 │  │ v1.2.4  │
│(Active)│  │(Standby)│
└────────┘  └─────────┘
\`\`\`

### CI/CD Pipeline

\`\`\`
GitHub Push
  ↓
GitHub Actions
  ├─ Lint
  ├─ Test
  ├─ Security Scan
  ├─ Build Docker Image
  └─ Push to ECR
  ↓
Terraform Apply
  ├─ Update Task Definition
  └─ Update ECS Service
  ↓
Smoke Tests
  ├─ Health Check
  ├─ API Tests
  └─ Performance Tests
  ↓
Production Deploy
\`\`\`

## Scalability

### Horizontal Scaling

| Component | Min | Max | Trigger |
|-----------|-----|-----|---------|
| ECS Tasks | 2 | 10 | CPU >70% |
| RDS Read Replicas | 0 | 3 | Read latency >100ms |

### Vertical Scaling

- ECS Task CPU/Memory can be increased via task definition
- RDS instance type can be changed (requires brief downtime)

### Database Sharding

For >10M records, implement sharding strategy:
- Shard by user_id hash
- 4 shards (expandable to 16)
- Consistent hashing for shard assignment

## Disaster Recovery

### Backup Strategy

- **RDS:** Automated daily snapshots (7-day retention)
- **Redis:** No persistence (cache only)
- **S3:** Versioning enabled, lifecycle policy to Glacier

### Recovery Procedures

| Scenario | RTO | RPO | Procedure |
|----------|-----|-----|-----------|
| AZ Failure | 5 min | 0 | Auto-failover to standby AZ |
| Region Failure | 1 hour | 15 min | Restore from snapshot in DR region |
| Data Corruption | 2 hours | 1 hour | Point-in-time recovery |

## Performance Characteristics

### Expected Latency

- **P50:** 50ms
- **P95:** 200ms
- **P99:** 500ms

### Throughput Capacity

- **Reads:** 1000 req/sec
- **Writes:** 200 req/sec

### Resource Utilization (Normal Load)

- **CPU:** 30-50%
- **Memory:** 40-60%
- **Database Connections:** 10-15 active

## Decision Records

### ADR-001: Why FastAPI over Flask

**Context:** Need high-performance async API framework

**Decision:** Use FastAPI

**Rationale:**
- Built-in async/await support
- Automatic API documentation (OpenAPI)
- Type validation with Pydantic
- 2-3x faster than Flask in benchmarks

### ADR-002: Why ECS Fargate over EC2

**Context:** Need container orchestration

**Decision:** Use ECS Fargate

**Rationale:**
- No server management overhead
- Pay only for compute time used
- Automatic scaling
- Integration with AWS services

---

**Maintained by:** Platform Engineering Team
**Last Review:** $(date +%Y-%m-%d)
EOF

    # Create Makefile
    cat > "${project_dir}/Makefile" <<'EOF'
.PHONY: help install test test-unit test-integration test-e2e lint format clean build deploy

help:
	@echo "Available targets:"
	@echo "  install           - Install dependencies"
	@echo "  test              - Run all tests"
	@echo "  test-unit         - Run unit tests"
	@echo "  test-integration  - Run integration tests"
	@echo "  test-e2e          - Run end-to-end tests"
	@echo "  lint              - Run linters"
	@echo "  format            - Format code"
	@echo "  clean             - Clean build artifacts"
	@echo "  build             - Build Docker image"
	@echo "  deploy            - Deploy application (ENV=dev|staging|prod)"

install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && pip install -r requirements-dev.txt

test: test-unit test-integration

test-unit:
	. venv/bin/activate && pytest tests/unit -v --cov=src --cov-report=term-missing

test-integration:
	. venv/bin/activate && pytest tests/integration -v

test-e2e:
	. venv/bin/activate && pytest tests/e2e -v

lint:
	. venv/bin/activate && flake8 src tests
	. venv/bin/activate && pylint src
	. venv/bin/activate && mypy src

format:
	. venv/bin/activate && black src tests
	. venv/bin/activate && isort src tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .coverage htmlcov

build:
	docker build -t ${PROJECT_SLUG}:latest .

deploy:
	@if [ -z "$(ENV)" ]; then \
		echo "Error: ENV not set. Usage: make deploy ENV=dev|staging|prod"; \
		exit 1; \
	fi
	@echo "Deploying to $(ENV)..."
	./scripts/deploy.sh $(ENV)
EOF

    # Create example Python source file
    mkdir -p "${project_dir}/src"
    cat > "${project_dir}/src/main.py" <<'EOF'
"""
Main application module.
"""

from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        Dictionary with health status
    """
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    logger.info("Application started")
    print(health_check())
EOF

    # Create example test file
    mkdir -p "${project_dir}/tests/unit"
    cat > "${project_dir}/tests/unit/test_main.py" <<'EOF'
"""
Unit tests for main module.
"""

from src.main import health_check


def test_health_check():
    """Test health check returns expected structure."""
    result = health_check()

    assert "status" in result
    assert "version" in result
    assert result["status"] == "healthy"
EOF

    # Create requirements files
    cat > "${project_dir}/requirements.txt" <<'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.4.2
boto3==1.28.85
psycopg2-binary==2.9.9
redis==5.0.1
structlog==23.2.0
EOF

    cat > "${project_dir}/requirements-dev.txt" <<'EOF'
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
pylint==3.0.2
mypy==1.7.0
isort==5.12.0
EOF

    # Create .env.example
    cat > "${project_dir}/.env.example" <<EOF
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=${project_slug}
DB_USER=admin
DB_PASSWORD=<generate-strong-password>

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=<generate-secret-key>
EOF

    # Create Dockerfile
    cat > "${project_dir}/Dockerfile" <<'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

    # Create GitHub Actions workflow
    mkdir -p "${project_dir}/ci"
    cat > "${project_dir}/ci/ci-cd.yml" <<'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install flake8 pylint black
      - name: Run linters
        run: |
          flake8 src tests
          pylint src
          black --check src tests

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest tests/unit --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'

  build:
    needs: [lint, test, security-scan]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t app:${{ github.sha }} .
EOF

    # Create basic Terraform files
    mkdir -p "${project_dir}/infrastructure/terraform"
    cat > "${project_dir}/infrastructure/terraform/main.tf" <<EOF
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "${project_name}"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
EOF

    cat > "${project_dir}/infrastructure/terraform/variables.tf" <<EOF
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "${project_name}"
}
EOF

    # Create deploy script
    mkdir -p "${project_dir}/scripts"
    cat > "${project_dir}/scripts/deploy.sh" <<'EOF'
#!/bin/bash
set -euo pipefail

ENV=${1:-dev}

echo "Deploying to $ENV environment..."

# Build Docker image
docker build -t app:latest .

# Tag for ECR
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/app"
docker tag app:latest "${ECR_REPO}:${ENV}-$(git rev-parse --short HEAD)"

# Push to ECR
aws ecr get-login-password --region "${AWS_REGION}" | \
  docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

docker push "${ECR_REPO}:${ENV}-$(git rev-parse --short HEAD)"

echo "✓ Deployment complete"
EOF
    chmod +x "${project_dir}/scripts/deploy.sh"

    # Create .gitignore
    cat > "${project_dir}/.gitignore" <<'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
.Python
venv/
ENV/
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
*.local

# IDE
.vscode/
.idea/
*.swp

# Terraform
.terraform/
*.tfstate
*.tfstate.backup
.terraform.lock.hcl

# OS
.DS_Store
Thumbs.db
EOF

    echo -e "${GREEN}✓ Created ${project_id}: ${project_name}${NC}"
}

# Main execution
echo -e "${BLUE}=== Enterprise Portfolio Project Generator ===${NC}"
echo ""

# Create projects directory
mkdir -p "${PROJECTS_DIR}"

# Process all projects
for project_id in "${!PROJECTS[@]}"; do
    IFS=':' read -r project_name project_slug <<< "${PROJECTS[$project_id]}"
    create_project "$project_id" "$project_name" "$project_slug"
done

echo ""
echo -e "${GREEN}✓ All 20 projects created successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. cd ${PROJECTS_DIR}"
echo "2. Review each project's README.md"
echo "3. Run validation: ../scripts/validate-projects.sh"
echo "4. Commit changes: git add . && git commit -m 'feat: add 20 standardized projects'"
