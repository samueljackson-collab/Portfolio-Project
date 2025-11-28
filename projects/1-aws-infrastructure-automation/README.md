# Project 1: AWS Infrastructure Automation

This project provisions a production-ready AWS environment with interchangeable IaC stacks and guardrails for validation, testing, and observability.

## Goals
- Launch a multi-AZ network foundation with private, public, and database subnets.
- Provide a managed Kubernetes control plane, managed worker nodes, and autoscaling policies.
- Supply a resilient PostgreSQL database tier with routine backups and monitoring toggles.
- Offer interchangeable infrastructure definitions so the same outcome can be reached with different toolchains.

## Contents
- **Terraform** – core implementation in [`terraform/main.tf`](terraform/main.tf) with variables (`terraform/variables.tf`) and environment overlays (`terraform/dev.tfvars`, `terraform/production.tfvars`).
- **AWS CDK** – Python app in [`cdk/app.py`](cdk/app.py) configured by [`cdk/cdk.json`](cdk/cdk.json) and [`cdk/requirements.txt`](cdk/requirements.txt).
- **Pulumi** – Python stack in [`pulumi/__main__.py`](pulumi/__main__.py) and [`pulumi/Pulumi.yaml`](pulumi/Pulumi.yaml) for multi-cloud parity.
- **Runbooks** – Deployment and validation steps in [`RUNBOOK.md`](RUNBOOK.md) and field notes in [`wiki/overview.md`](wiki/overview.md).
- **Automation scripts** – Helper commands in [`scripts/`](scripts/) for Terraform, Pulumi, and CDK deployment and validation.
- **Tests** – Pytest coverage for IaC conventions in [`tests/test_infrastructure.py`](tests/test_infrastructure.py) with settings in [`pytest.ini`](pytest.ini).
- **CI Pipeline** – GitHub Actions workflow [`./.github/workflows/ci.yml`](.github/workflows/ci.yml) enforcing fmt/validate + tests.
- **Kubernetes addon** – Cluster monitoring DaemonSet in [`k8s/cluster-addons.yaml`](k8s/cluster-addons.yaml).
- **Monitoring** – Prometheus alert rules for EKS in [`monitoring/eks-prometheus-rules.yaml`](monitoring/eks-prometheus-rules.yaml).

Each implementation aligns with the runbooks so the documentation, automation, and validation steps can be exercised end-to-end.
