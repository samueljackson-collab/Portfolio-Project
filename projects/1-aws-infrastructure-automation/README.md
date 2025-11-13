# Project 1: AWS Infrastructure Automation

This project provisions a production-ready AWS environment with multiple implementation paths so the portfolio can demonstrate infrastructure-as-code fluency across Terraform, the AWS CDK, and Pulumi.

## Goals
- Launch a multi-AZ network foundation with private, public, and database subnets, binding each subnet to a deterministic availability zone for high availability.
- Provide a managed Kubernetes control plane, managed worker nodes, and autoscaling policies.
- Supply a resilient PostgreSQL database tier with routine backups and monitoring toggles.
- Offer interchangeable infrastructure definitions so the same outcome can be reached with different toolchains.

## Contents
- `terraform/` — Primary IaC implementation using community modules and environment-specific variables.
- `cdk/` — Python-based AWS CDK app that mirrors the Terraform footprint and highlights programmatic constructs.
- `pulumi/` — Pulumi project using Python for multi-cloud friendly infrastructure authoring.
- `scripts/` — Helper scripts for planning, deployment, validation, and teardown workflows.

Each implementation aligns with the runbooks described in the Wiki.js guide so the documentation, automation, and validation steps can be exercised end-to-end.
