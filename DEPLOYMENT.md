# 🚀 Deployment Guide

## Environment Setup

### Prerequisites
- Docker 20.10+
- Kubernetes 1.28+
- Terraform 1.5+
- AWS CLI configured with IAM credentials

### Local Development Workflow
1. Clone the repository and run `./scripts/setup/init.sh` to bootstrap Python and Node tooling.
2. Launch the local stack with `docker-compose up --build -d` to start PostgreSQL, Redis, the FastAPI sample API, and the static frontend served via Nginx.
3. Use `scripts/test/smoke-tests.sh` to verify the API and frontend locally.

### Production Deployment

Deploy to any environment with the enterprise automation script:

```bash
./scripts/deployment/enterprise-deploy.sh production
./scripts/deployment/enterprise-deploy.sh staging
```

The script provisions AWS infrastructure with Terraform, configures EKS, installs core add-ons (Istio, cert-manager, Prometheus stack), and applies security policies before deploying workloads.

## Configuration

### Environment Variables

```bash
export AWS_REGION=us-west-2
export ENVIRONMENT=production
export KUBECONFIG=~/.kube/config
```

### Terraform Variables

Create `infrastructure/terraform/terraform.tfvars` with environment-specific overrides:

```hcl
environment = "production"
aws_region  = "us-west-2"
db_username = "admin"
db_password = "secure-password"
```

## Monitoring & Logging

Access monitoring components once deployed:
- Grafana: `http://monitoring.portfolio.example.com`
- Prometheus: `http://prometheus.portfolio.example.com`
- Loki/Kibana: `http://logs.portfolio.example.com`

Alerting rules are defined in `monitoring/prometheus/alert-rules.yaml` and ship with common SLO checks.

## Backup & Recovery

Create ad-hoc backups using:

```bash
./scripts/backup/full-backup.sh
```

Restore from a tarball backup with:

```bash
./scripts/backup/restore-backup.sh backup/archive.tar.gz
```

## Common Issues

| Symptom | Possible Cause | Resolution |
| --- | --- | --- |
| Terraform apply fails | Missing credentials | Confirm `aws sts get-caller-identity` succeeds |
| Kubernetes pods pending | Insufficient node capacity | Adjust node group sizes in Terraform variables |
| TLS errors at ingress | Cert-manager not ready | Check `kubectl get pods -n cert-manager` and rerun script |
| Grafana login fails | Incorrect credentials | Use default admin password (`admin`) or reset via `kubectl` secret |

## Disaster Recovery Steps

1. Promote the secondary region infrastructure using the Terraform workspace for DR.
2. Update DNS records to point to the secondary ingress.
3. Validate application health with `scripts/test/smoke-tests.sh`.
4. Initiate data validation routines from `projects/2-database-migration` to confirm integrity.
