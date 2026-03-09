---
title: Cloud Security Automation Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [compliance, devsecops, documentation, portfolio, security]
path: portfolio/p19-security-automation/pipeline-recovery
created: 2026-03-08T22:19:13.855147+00:00
updated: 2026-03-08T22:04:37.997902+00:00
---

# Cloud Security Automation Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
