# Project 1: AWS Infrastructure Automation

This project provisions a production-ready AWS environment with multiple implementation paths so the portfolio can demonstrate infrastructure-as-code fluency across Terraform, the AWS CDK, and Pulumi.

## Goals
- Launch a multi-AZ network foundation with private, public, and database subnets.
- Provide a managed Kubernetes control plane, managed worker nodes, and autoscaling policies.
- Supply a resilient PostgreSQL database tier with routine backups and monitoring toggles.
- Offer interchangeable infrastructure definitions so the same outcome can be reached with different toolchains.

## Contents
- `terraform/` — Primary IaC implementation using community modules and environment-specific variables.
- `cdk/` — Python-based AWS CDK app that mirrors the Terraform footprint and highlights programmatic constructs.
- `pulumi/` — Pulumi project using Python for multi-cloud friendly infrastructure authoring.
- `scripts/` — Helper scripts for planning, deployment, validation, and teardown workflows.

Each implementation aligns with the runbooks described in the Wiki.js guide so the documentation, automation, and validation steps can be exercised end-to-end.

## Phase 1 Architecture Diagram

Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

- **Context**: Foundation IaC patterns are split across Terraform, CDK, and Pulumi while CI/CD enforces linting, tfsec, and approval gates before applying to AWS accounts.
- **Decision**: Isolate developer workstations, CI/CD control plane, and AWS runtime in separate trust boundaries with remote state (S3+DynamoDB) and CloudWatch feedback loops.
- **Consequences**: Reusable pipelines catch drift and security regressions early, while state locking and telemetry keep production changes auditable. Update the [Mermaid source](assets/diagrams/architecture.mmd) alongside the PNG when evolving the deployment topology.
