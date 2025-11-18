# ADR 0001: Choose Terraform over CloudFormation
Date: 2025-11-17
Status: Accepted

## Context
We need vendor-neutral IaC across AWS and multi-cloud (P01, P05, P21).

## Decision
Use Terraform with modules per layer; TFLint + Terratest in CI.

## Consequences
+ Reusable modules across projects
+ Rich lint/test ecosystem
- Extra tool to learn; state backend management required
