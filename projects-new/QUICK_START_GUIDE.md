# Quick Start Guide - 20 Enterprise Projects

**Status:** 🟢 Active | **Version:** 1.0.0 | **Last Updated:** November 2025

## Overview

This guide will help you quickly get started with the 20 standardized enterprise projects in this portfolio. Each project follows the same structure and conventions defined in the [Enterprise Engineer's Handbook](../docs/PRJ-MASTER-HANDBOOK/README.md).

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Quick Start Steps](#quick-start-steps)
4. [Project Index](#project-index)
5. [Common Commands](#common-commands)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

Install these tools before working with any project:

```bash
# Python 3.9+
python --version

# Docker 20.10+
docker --version

# Terraform 1.5+
terraform version

# kubectl 1.27+ (for Kubernetes projects)
kubectl version

# AWS CLI 2.0+
aws --version

# Make
make --version
```

### AWS Credentials

Configure AWS credentials:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

Or use AWS CLI:

```bash
aws configure
```

---

## Project Structure

Every project follows this standardized structure:

```
PXX-project-name/
├── README.md                 # Project overview and quick start
├── Makefile                  # Build and deployment automation
├── .env.example              # Example configuration
├── Dockerfile                # Container image definition
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Development dependencies
├── .gitignore               # Git ignore patterns
├── docs/                     # Comprehensive documentation
│   ├── HANDBOOK.md          # Engineering standards
│   ├── RUNBOOK.md           # Operational procedures
│   ├── PLAYBOOK.md          # Implementation guide
│   └── ARCHITECTURE.md      # System design
├── src/                      # Source code
│   └── main.py              # Main application entry point
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── scripts/                  # Automation scripts
│   └── deploy.sh            # Deployment script
├── infrastructure/           # Infrastructure as Code
│   ├── terraform/           # Terraform configurations
│   │   ├── main.tf
│   │   └── variables.tf
│   └── k8s/                 # Kubernetes manifests
└── ci/                       # CI/CD workflows
    └── ci-cd.yml            # GitHub Actions workflow
```

---

## Quick Start Steps

### Step 1: Choose a Project

Navigate to any project directory:

```bash
cd projects-new/P01-aws-infra
```

### Step 2: Review Documentation

Read the project README:

```bash
cat README.md
```

Key sections:
- **Overview:** What the project does
- **Quick Start:** Fast setup instructions
- **Documentation:** Links to detailed docs
- **Features:** What's included

### Step 3: Install Dependencies

```bash
# Create virtual environment
make install

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Step 4: Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit with your values
nano .env
```

Common variables:
```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=admin
DB_PASSWORD=<generate-strong-password>
```

Generate secure passwords:
```bash
openssl rand -base64 32
```

### Step 5: Run Tests

```bash
# Run all tests
make test

# Or specific test types
make test-unit
make test-integration

# With coverage report
pytest tests/unit --cov=src --cov-report=html
```

### Step 6: Deploy

```bash
# Deploy to development
make deploy ENV=dev

# Deploy to staging
make deploy ENV=staging

# Deploy to production (requires approval)
make deploy ENV=prod
```

---

## Project Index

### Infrastructure & Platform (P01-P03)

#### P01: AWS Infrastructure Automation
**Directory:** `P01-aws-infra`

Automates AWS infrastructure provisioning with Terraform.

**Key Features:**
- VPC with public/private subnets
- RDS database provisioning
- ECS cluster setup
- Load balancer configuration

**Quick Start:**
```bash
cd P01-aws-infra
make install
cp .env.example .env
cd infrastructure/terraform
terraform init
terraform plan
```

**Documentation:** `docs/PLAYBOOK.md`

---

#### P02: Kubernetes Cluster Management
**Directory:** `P02-k8s-cluster`

Manages Kubernetes clusters with automated deployment and scaling.

**Key Features:**
- EKS cluster provisioning
- Node group management
- RBAC configuration
- Helm chart deployments

**Quick Start:**
```bash
cd P02-k8s-cluster
make install
kubectl cluster-info
kubectl get nodes
```

**Documentation:** `docs/RUNBOOK.md`

---

#### P03: CI/CD Pipeline Implementation
**Directory:** `P03-cicd-pipeline`

Complete CI/CD pipeline with automated testing and deployment.

**Key Features:**
- GitHub Actions workflows
- Multi-stage deployments
- Automated testing
- Security scanning

**Quick Start:**
```bash
cd P03-cicd-pipeline
cat ci/ci-cd.yml
# Push to trigger pipeline
git push origin main
```

**Documentation:** `docs/HANDBOOK.md`

---

### Monitoring & Observability (P04, P10, P19)

#### P04: Operational Monitoring Stack
**Directory:** `P04-monitoring-stack`

Prometheus and Grafana monitoring stack.

**Key Features:**
- Prometheus metrics collection
- Grafana dashboards
- Alert manager integration
- Custom alerting rules

**Quick Start:**
```bash
cd P04-monitoring-stack
docker-compose up -d
# Access Grafana at http://localhost:3000
```

**Documentation:** `docs/ARCHITECTURE.md`

---

#### P10: Log Aggregation System
**Directory:** `P10-log-aggregation`

Centralized log aggregation with ELK stack.

**Key Features:**
- Elasticsearch for storage
- Logstash for processing
- Kibana for visualization
- Log retention policies

**Quick Start:**
```bash
cd P10-log-aggregation
docker-compose up -d elasticsearch kibana
# Access Kibana at http://localhost:5601
```

---

#### P19: Observability Dashboard
**Directory:** `P19-observability-dashboard`

Unified observability dashboard combining metrics, logs, and traces.

**Key Features:**
- OpenTelemetry integration
- Distributed tracing
- Real-time metrics
- Custom dashboards

**Quick Start:**
```bash
cd P19-observability-dashboard
make install
make deploy ENV=dev
```

---

### Database & Performance (P05, P17)

#### P05: Database Performance Optimization
**Directory:** `P05-db-optimization`

Tools for database performance analysis and optimization.

**Key Features:**
- Slow query analysis
- Index recommendations
- Connection pool tuning
- Performance benchmarking

**Quick Start:**
```bash
cd P05-db-optimization
source venv/bin/activate
python src/main.py --analyze --database mydb
```

---

#### P17: Performance Load Testing
**Directory:** `P17-load-testing`

Load testing framework with k6 and custom scripts.

**Key Features:**
- HTTP load testing
- WebSocket testing
- Performance metrics
- Result analysis

**Quick Start:**
```bash
cd P17-load-testing
k6 run tests/performance/load_test.js
```

---

### Testing & Quality (P06)

#### P06: Web Application Testing Framework
**Directory:** `P06-web-testing`

Comprehensive web testing with Playwright and pytest.

**Key Features:**
- E2E browser testing
- Visual regression testing
- API testing
- Test reporting

**Quick Start:**
```bash
cd P06-web-testing
make install
playwright install
pytest tests/e2e -v
```

---

### Security & Compliance (P07, P13)

#### P07: Security Compliance Automation
**Directory:** `P07-security-compliance`

Automated security compliance checks.

**Key Features:**
- CIS benchmark validation
- OWASP Top 10 checks
- Vulnerability scanning
- Compliance reporting

**Quick Start:**
```bash
cd P07-security-compliance
python src/main.py --scan --profile cis-aws
```

---

#### P13: Secrets Management System
**Directory:** `P13-secrets-management`

Secure secrets management with AWS Secrets Manager.

**Key Features:**
- Secrets rotation
- Access control
- Audit logging
- CLI integration

**Quick Start:**
```bash
cd P13-secrets-management
make install
python src/main.py --list-secrets
```

---

### Cost & Resource Optimization (P08)

#### P08: Cost Optimization Tooling
**Directory:** `P08-cost-optimization`

AWS cost analysis and optimization recommendations.

**Key Features:**
- Cost Explorer integration
- Idle resource detection
- Savings recommendations
- Budget alerts

**Quick Start:**
```bash
cd P08-cost-optimization
python src/main.py --analyze --days 30
```

---

### Disaster Recovery (P09, P16)

#### P09: Disaster Recovery Orchestration
**Directory:** `P09-dr-orchestration`

Automated disaster recovery workflows.

**Key Features:**
- DR drill automation
- Backup verification
- Failover orchestration
- RTO/RPO monitoring

**Quick Start:**
```bash
cd P09-dr-orchestration
python src/main.py --run-drill
```

---

#### P16: Backup Verification System
**Directory:** `P16-backup-verification`

Automated backup testing and verification.

**Key Features:**
- Backup integrity checks
- Restore testing
- Compliance validation
- Automated reporting

**Quick Start:**
```bash
cd P16-backup-verification
./scripts/verify_backups.sh
```

---

### Networking & Infrastructure (P11, P12, P14, P18)

#### P11: API Gateway Configuration
**Directory:** `P11-api-gateway`

API Gateway setup with rate limiting and authentication.

**Quick Start:**
```bash
cd P11-api-gateway
terraform -chdir=infrastructure/terraform init
terraform -chdir=infrastructure/terraform apply
```

---

#### P12: Container Registry Management
**Directory:** `P12-container-registry`

ECR registry management with image scanning.

**Quick Start:**
```bash
cd P12-container-registry
make build
make push
```

---

#### P14: Network Configuration Automation
**Directory:** `P14-network-automation`

Network infrastructure automation.

**Quick Start:**
```bash
cd P14-network-automation
terraform -chdir=infrastructure/terraform plan
```

---

#### P18: Service Mesh Implementation
**Directory:** `P18-service-mesh`

Istio service mesh deployment and configuration.

**Quick Start:**
```bash
cd P18-service-mesh
kubectl apply -f infrastructure/k8s/
```

---

### Incident Response (P15)

#### P15: Incident Response Automation
**Directory:** `P15-incident-response`

Automated incident detection and response.

**Key Features:**
- Incident detection
- Alert aggregation
- Automated remediation
- Post-mortem generation

**Quick Start:**
```bash
cd P15-incident-response
python src/main.py --monitor
```

---

### Multi-Cloud (P20)

#### P20: Multi-Cloud Orchestration
**Directory:** `P20-multi-cloud`

Multi-cloud resource orchestration across AWS, Azure, GCP.

**Key Features:**
- Cloud-agnostic APIs
- Resource syncing
- Cost comparison
- Multi-cloud DR

**Quick Start:**
```bash
cd P20-multi-cloud
make install
python src/main.py --list-resources
```

---

## Common Commands

### All Projects Support These Commands

```bash
# Install dependencies
make install

# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-e2e

# Lint code
make lint

# Format code
make format

# Build Docker image
make build

# Deploy to environment
make deploy ENV=dev
make deploy ENV=staging
make deploy ENV=prod

# Clean build artifacts
make clean

# Show help
make help
```

---

## Troubleshooting

### Common Issues

#### 1. Python Dependencies Not Installing

**Problem:** `pip install` fails

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip

# Use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. AWS Credentials Not Found

**Problem:** `Unable to locate credentials`

**Solution:**
```bash
# Set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"

# Or configure AWS CLI
aws configure
```

#### 3. Terraform Backend Not Initialized

**Problem:** `Backend configuration changed`

**Solution:**
```bash
cd infrastructure/terraform
terraform init -reconfigure
# Or migrate state
terraform init -migrate-state
```

#### 4. Docker Build Fails

**Problem:** `Docker build fails with permission denied`

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in

# Or run with sudo
sudo docker build -t app:latest .
```

#### 5. Tests Failing

**Problem:** Tests fail with import errors

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install in editable mode
pip install -e .

# Run tests with correct Python path
PYTHONPATH=. pytest tests/
```

#### 6. Database Connection Errors

**Problem:** `Could not connect to database`

**Solution:**
```bash
# Check database is running
docker ps | grep postgres

# Start database container
docker-compose up -d postgres

# Verify connection
psql -h localhost -U admin -d mydb
```

#### 7. Port Already in Use

**Problem:** `Address already in use`

**Solution:**
```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>

# Or use different port in .env
PORT=8081
```

---

## Next Steps

### 1. Deep Dive into Documentation

Each project has comprehensive docs:

- **HANDBOOK.md** - Engineering standards and code guidelines
- **RUNBOOK.md** - Operational procedures and troubleshooting
- **PLAYBOOK.md** - Step-by-step implementation guide
- **ARCHITECTURE.md** - System design and architecture decisions

### 2. Customize for Your Use Case

Modify the template projects to fit your needs:

1. Update `variables.tf` with your AWS account details
2. Modify Docker configurations for your runtime
3. Adjust CI/CD workflows for your deployment process
4. Add project-specific business logic in `src/`

### 3. Integrate with Existing Systems

Connect projects to your infrastructure:

- Configure monitoring to send to your Grafana instance
- Update log aggregation to your centralized logging
- Integrate secrets management with your vault
- Configure alerts to your PagerDuty/OpsGenie

### 4. Run in Production

Production checklist:

- [ ] All tests passing
- [ ] Security scan completed (no critical issues)
- [ ] Environment variables configured
- [ ] Terraform backend configured with S3
- [ ] Monitoring and alerting set up
- [ ] Backup and DR procedures tested
- [ ] Documentation reviewed and updated
- [ ] On-call rotation scheduled

---

## Validation

Validate all projects meet standards:

```bash
# Run validation script
cd /path/to/portfolio
./scripts/validate-projects.sh

# Should see:
# Projects validated: 20
# Total checks: 640
# Passed: 640
# Failed: 0
# Pass rate: 100%
```

---

## Support

### Resources

- [Enterprise Engineer's Handbook](../docs/PRJ-MASTER-HANDBOOK/README.md)
- [IT Playbook (Lifecycle)](../docs/PRJ-MASTER-PLAYBOOK/README.md)
- [Configuration Guide](../CONFIGURATION_GUIDE.md)

### Getting Help

1. Check the project's `docs/RUNBOOK.md` for troubleshooting
2. Review the `docs/PLAYBOOK.md` for implementation steps
3. Search for similar issues in project documentation
4. Open GitHub issue with detailed error information

---

## Contributing

When enhancing projects:

1. Follow the [Engineer's Handbook](../docs/PRJ-MASTER-HANDBOOK/README.md) standards
2. Add tests for new functionality (≥80% coverage)
3. Update documentation (README, HANDBOOK, RUNBOOK)
4. Run validation script before committing
5. Submit PR with comprehensive description

---

**Maintained by:** Platform Engineering Team
**Last Updated:** November 2025
**Version:** 1.0.0

---

## Quick Reference

| Project | Primary Technology | Use Case | Setup Time |
|---------|-------------------|----------|------------|
| P01 | Terraform | AWS Infrastructure | 15 min |
| P02 | Kubernetes | Container Orchestration | 20 min |
| P03 | GitHub Actions | CI/CD Pipeline | 10 min |
| P04 | Prometheus/Grafana | Monitoring | 10 min |
| P05 | Python | Database Optimization | 5 min |
| P06 | Playwright | Web Testing | 15 min |
| P07 | Python/Boto3 | Security Compliance | 5 min |
| P08 | AWS Cost Explorer | Cost Optimization | 5 min |
| P09 | Python | Disaster Recovery | 10 min |
| P10 | ELK Stack | Log Aggregation | 15 min |
| P11 | Terraform | API Gateway | 10 min |
| P12 | AWS ECR | Container Registry | 5 min |
| P13 | AWS Secrets Manager | Secrets Management | 5 min |
| P14 | Terraform | Network Automation | 15 min |
| P15 | Python | Incident Response | 10 min |
| P16 | Bash/Python | Backup Verification | 5 min |
| P17 | k6 | Load Testing | 10 min |
| P18 | Istio | Service Mesh | 20 min |
| P19 | OpenTelemetry | Observability | 15 min |
| P20 | Terraform | Multi-Cloud | 20 min |

**Total estimated time to set up all 20 projects:** ~4 hours
