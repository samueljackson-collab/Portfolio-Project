---
title: Deployment Status — Project 1: AWS Infrastructure Automation
description: **Status:** Targeted for initial live deployment - **Environment:** Production (Demo) - **Deployment date:** 2025-02-14 (planned) - **Primary endpoint:** https://aws-infra-automation.example.com - **H
tags: [aws, cloud, documentation, infrastructure, portfolio]
path: portfolio/1-aws-infrastructure-automation/deployment-status
created: 2026-03-08T22:19:13.148765+00:00
updated: 2026-03-08T22:04:38.464902+00:00
---

# Deployment Status — Project 1: AWS Infrastructure Automation

**Status:** Targeted for initial live deployment

## Environment
- **Environment:** Production (Demo)
- **Deployment date:** 2025-02-14 (planned)

## Live URLs
- **Primary endpoint:** https://aws-infra-automation.example.com
- **Health check:** https://aws-infra-automation.example.com/healthz
- **Static assets (CDN):** https://static.aws-infra-automation.example.com

## Deployment artifacts & logs
- `deployments/2025-02-14/terraform-plan.txt`
- `deployments/2025-02-14/terraform-apply.log`
- `deployments/2025-02-14/outputs.json`

## Verification steps
1. `curl -fsSL https://aws-infra-automation.example.com/healthz`
2. `curl -I https://static.aws-infra-automation.example.com`
3. `aws elbv2 describe-load-balancers --names portfolio-app-prod`
