# Deployment Runbook

## 1. Overview

This runbook describes the process for deploying the portfolio services to AWS-backed environments. Environments follow GitOps principles managed by ArgoCD, with Terraform responsible for foundational infrastructure.

## 2. Environments
- **Development**: Lightweight footprint, single AZ, spot instances allowed.
- **Staging**: Mirrors production topology, used for release verification.
- **Production**: Multi-AZ, auto-scaling, enhanced monitoring and alerting.

## 3. Terraform Workflow

```bash
cd infra/environments/<env>
terraform init
terraform plan -out plan.tfplan
terraform apply plan.tfplan
```

State is stored in S3 with DynamoDB locking. Validate `backend.tf` for correct bucket/prefix before running `init`.

## 4. Application Deployment

1. Build Docker images via CI pipeline (`ci.yml`).
2. Release pipeline (`release.yml`) pushes images to ECR and triggers ArgoCD syncs.
3. For manual deployments, use:

```bash
kubectl config use-context <env>
helm upgrade --install portfolio charts/portfolio \
  --set image.tag=<tag> \
  --set backend.envSecretsRef=portfolio-secrets
```

## 5. Database Migrations

- Alembic migrations run automatically via backend container entrypoint.
- For manual execution:

```bash
cd backend
alembic upgrade head
```

## 6. Verification Steps
- [ ] Backend `/health` returns 200 with `status: ok`.
- [ ] Frontend loads homepage and dashboard with authenticated session.
- [ ] Prometheus scraping targets show `UP`.
- [ ] Alertmanager has no firing alerts post-deploy.
- [ ] k6 smoke test passes under `e2e-tests/k6/smoke` scenario.

## 7. Rollback Procedures
- Use Helm revision history: `helm rollback portfolio <revision>`.
- For database issues, restore from latest snapshot (`aws rds restore-db-instance-to-point-in-time`).
- Update status in `STATUS_BOARD.md` and document root cause via ADR/postmortem template.

## 8. Compliance & Approvals
- Production deploys require approval from `@operations-lead` via GitHub Actions.
- Security pipeline must be green before release pipeline can proceed.

