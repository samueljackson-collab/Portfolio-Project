---
title: Deployment Attempt Log (Terraform)
description: - **Goal:** Deploy `projects/9-multi-region-disaster-recovery/terraform` into two regions (primary + DR). - **Outcome:** Deployment not executed because the environment lacks the Terraform CLI. $ terr
tags: [documentation, portfolio]
path: portfolio/9-multi-region-disaster-recovery/deployment-log
created: 2026-03-08T22:19:13.413408+00:00
updated: 2026-03-08T22:04:38.784902+00:00
---

# Deployment Attempt Log (Terraform)

## Summary
- **Goal:** Deploy `projects/9-multi-region-disaster-recovery/terraform` into two regions (primary + DR).
- **Outcome:** Deployment not executed because the environment lacks the Terraform CLI.

## Commands & Output
```bash
$ terraform -version
bash: command not found: terraform
```

## Next Steps
1. Install Terraform in the execution environment.
2. Re-run deployment with region-scoped variables:
   ```bash
   cd projects/9-multi-region-disaster-recovery/terraform
   terraform init
   terraform apply -var-file=production.tfvars
   ```
3. Capture apply output for both regions and attach to this evidence directory.
