---
title: Terraform Multi-Cloud Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [cloud, documentation, iac, portfolio, terraform]
path: portfolio/p17-terraform-multicloud/pipeline-recovery
created: 2026-03-08T22:19:13.829303+00:00
updated: 2026-03-08T22:04:37.981902+00:00
---

# Terraform Multi-Cloud Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
