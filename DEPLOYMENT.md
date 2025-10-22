# Deployment Runbook

This runbook describes how to provision, configure, and operate the Portfolio API platform. It assumes access to the infrastructure repository, AWS Organization, and Kubernetes cluster permissions documented in [SECURITY.md](./SECURITY.md#access-controls).

## Prerequisites

- Terraform ≥ 1.5 with the AWS provider installed.
- kubectl ≥ 1.27 configured to authenticate via `aws eks update-kubeconfig`.
- Helm ≥ 3.0 for optional add-ons (Prometheus, external-secrets).
- AWS CLI v2 with credentials that can assume the `PortfolioPlatformAdmin` role defined in [`security/policies/iam-portfolio-api.json`](./security/policies/iam-portfolio-api.json).
- Remote state bucket and DynamoDB lock table created using `infrastructure/terraform/bootstrap.tf`.

## Environment Configuration

| Variable | Description | Example |
| --- | --- | --- |
| `TF_BACKEND_BUCKET` | S3 bucket that stores Terraform state. | `portfolio-iac-state-prod` |
| `TF_BACKEND_TABLE` | DynamoDB table for state locking. | `portfolio-iac-locks` |
| `AWS_PROFILE` | AWS CLI profile that can assume the admin role. | `portfolio-admin` |
| `KUBECONFIG` | Path to write kubeconfig after cluster creation. | `${PWD}/.kube/config` |
| `PORTFOLIO_ENV` | Deployment environment (`dev`, `staging`, `prod`). | `staging` |

Populate these variables in `env/<environment>.tfvars` and source them before running the scripts:

```bash
export PORTFOLIO_ENV=staging
export AWS_PROFILE=portfolio-admin
source env/${PORTFOLIO_ENV}.env
```

## Provision Infrastructure

Terraform code resides in [`infrastructure/terraform/`](./infrastructure/terraform/). The [`scripts/deploy.sh`](./scripts/deploy.sh) script wraps the following manual steps:

1. Initialize backends:
   ```bash
   terraform -chdir=infrastructure/terraform init \
     -backend-config="bucket=${TF_BACKEND_BUCKET}" \
     -backend-config="dynamodb_table=${TF_BACKEND_TABLE}"
   ```
2. Review and apply the plan:
   ```bash
   terraform -chdir=infrastructure/terraform apply \
     -var-file="env/${PORTFOLIO_ENV}.tfvars"
   ```
3. Update kubeconfig after the EKS cluster is provisioned:
   ```bash
   aws eks update-kubeconfig \
     --name "portfolio-${PORTFOLIO_ENV}" \
     --region us-west-2 \
     --role-arn "arn:aws:iam::${ACCOUNT_ID}:role/PortfolioPlatformAdmin"
   ```

## Deploy Application Manifests

Kubernetes manifests live in [`infrastructure/kubernetes/`](./infrastructure/kubernetes/). Deploy them using `kubectl apply` or Helmfile depending on the component.

```bash
kubectl apply -k infrastructure/kubernetes/overlays/${PORTFOLIO_ENV}
```

The kustomize overlays include:

- Namespace creation (`portfolio-system`, `portfolio-app`).
- Base Deployments and Services for API, worker, and cronjobs.
- HorizontalPodAutoscaler definitions and PodDisruptionBudgets.
- NetworkPolicy resources synced with [`security/policies/network-policy.yaml`](./security/policies/network-policy.yaml).

## Database Migrations

Flyway migrations are stored under `infrastructure/database/migrations/`. CI pipelines execute them automatically, but manual execution follows:

```bash
./scripts/run-migrations.sh --env ${PORTFOLIO_ENV}
```

The script retrieves credentials from AWS Secrets Manager, validates checksums, and applies migrations in order. Rollback scripts live alongside the migrations and can be invoked with `--target=<version>`.

## Post-Deployment Verification

1. **Smoke tests** – [`scripts/smoke-test.sh`](./scripts/smoke-test.sh) calls `/healthz`, `/readyz`, and `/api/v1/portfolio` endpoints. Failures abort the pipeline.
2. **Monitoring checks** – Ensure Prometheus targets report `up == 1` and Alertmanager is in `normal` state. See [`monitoring/prometheus/alerts.yml`](./monitoring/prometheus/alerts.yml).
3. **Data validation** – Run [`documentation/runbooks/data-validation.md`](./documentation/runbooks/data-validation.md) to confirm seed data and background jobs succeeded.

## Rollback Strategy

| Scenario | Action |
| --- | --- |
| Failed application rollout | Use `kubectl rollout undo deployment portfolio-api -n portfolio-app` and redeploy the last known good image tag. |
| Terraform apply failure | Run `terraform state pull` to inspect partial state, fix configuration, and re-run `terraform apply`. If necessary, destroy partial resources with `terraform destroy -target=<resource>`. |
| Database migration failure | Trigger Flyway repair, restore from latest snapshot (see [`documentation/runbooks/disaster-recovery.md`](./documentation/runbooks/disaster-recovery.md)), and redeploy using a fixed script. |

## Continuous Delivery

GitHub Actions workflows automate the steps above:

- `.github/workflows/terraform.yml` plans and applies Terraform after manual approval.
- `.github/workflows/deploy.yml` builds containers, pushes to ECR, runs migrations, and deploys manifests.
- `.github/workflows/security.yml` runs [`scripts/compliance-scan.sh`](./scripts/compliance-scan.sh) to ensure policies in [`security/`](./security/) remain compliant.

Pipeline status is surfaced in Grafana dashboards under *CI/CD* and in the `#portfolio-deployments` Slack channel via Alertmanager webhooks.

