---
title: Deployment Status — Project 4: DevSecOps Pipeline
description: **Status:** Targeted for initial live deployment - **Environment:** Production (Demo) - **Deployment date:** 2025-02-14 (planned) - **Pipeline dashboard:** https://devsecops.example.com - **SBOM index
tags: [documentation, portfolio]
path: portfolio/4-devsecops/deployment-status
created: 2026-03-08T22:19:13.359578+00:00
updated: 2026-03-08T22:04:38.722902+00:00
---

# Deployment Status — Project 4: DevSecOps Pipeline

**Status:** Targeted for initial live deployment

## Environment
- **Environment:** Production (Demo)
- **Deployment date:** 2025-02-14 (planned)

## Live URLs
- **Pipeline dashboard:** https://devsecops.example.com
- **SBOM index:** https://devsecops.example.com/sbom
- **Verification endpoint:** https://devsecops.example.com/healthz

## Deployment artifacts & logs
- `deployments/2025-02-14/pipeline-run.log`
- `deployments/2025-02-14/security-scan-summary.json`
- `deployments/2025-02-14/sbom-summary.json`

## Verification steps
1. `curl -fsSL https://devsecops.example.com/healthz`
2. `curl -fsSL https://devsecops.example.com/sbom`
3. `gh run list --workflow "security-pipeline" --limit 5`
