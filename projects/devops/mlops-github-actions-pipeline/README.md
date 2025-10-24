# MLOps CI/CD Pipeline with GitHub Actions

## Overview
End-to-end ML pipeline automating data validation, model training, evaluation, and deployment using GitHub Actions workflows.

## Workflow Stages
1. **Data Validation** – Great Expectations checks on incoming datasets, results pushed to data quality dashboards.
2. **Feature Engineering** – PySpark/Feature Store jobs executed within containerized runner.
3. **Model Training** – MLflow + scikit-learn or PyTorch training with experiment tracking.
4. **Model Evaluation** – Bias/fairness metrics using `fairlearn`, accuracy thresholds enforced.
5. **Packaging** – Build Docker image or model artifact, sign with Cosign.
6. **Deployment** – Promote to SageMaker endpoint or Kubernetes inference service via Helm.
7. **Monitoring** – Capture drift metrics and log predictions to Kafka for auditing.

## Repository Layout
- `.github/workflows/` – Workflow YAML definitions with reusable composite actions.
- `pipelines/` – Python scripts for training/evaluation.
- `infra/` – Terraform/CDK definitions for ML infrastructure.
- `docs/` – Playbooks, experiment templates.

## Security & Compliance
- Workflows use OIDC + IAM roles for temporary credentials.
- Secrets stored in GitHub Actions secrets/HashiCorp Vault.
- Evidence artifacts uploaded to S3 for audit (model cards, evaluation reports).

