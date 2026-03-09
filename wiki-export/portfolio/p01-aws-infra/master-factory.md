---
title: Master Factory — P01 AWS Infra
description: This factory document enumerates the CI and IaC steps that every delivery asset must align to. The GitHub Actions workflow, Terraform modules, and CloudFormation templates in this project are grounded
tags: [aws, cloud, documentation, infrastructure, portfolio]
path: portfolio/p01-aws-infra/master-factory
created: 2026-03-08T22:19:13.473505+00:00
updated: 2026-03-08T22:04:38.865902+00:00
---

# Master Factory — P01 AWS Infra

This factory document enumerates the CI and IaC steps that every delivery asset must align to. The GitHub Actions workflow, Terraform modules, and CloudFormation templates in this project are grounded in the following stages:

1. **Lint & Unit Tests** – validate Python utilities, templates, and supporting scripts before any infrastructure action.
2. **Terraform Plan** – run `terraform init` and `terraform plan` with S3/DynamoDB-backed state to preview network changes.
3. **CloudFormation Change Sets** – create and review change sets for the RDS stack prior to execution.
4. **Gated Apply** – require manual approval (protected environment) before applying Terraform or executing CloudFormation change sets.

Each asset under `projects/p01-aws-infra/` references these stages to keep CI, remote state, and database provisioning consistent.
