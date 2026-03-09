---
title: High-Availability Web App Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [documentation, portfolio]
path: portfolio/p13-ha-webapp/pipeline-recovery
created: 2026-03-08T22:19:13.762570+00:00
updated: 2026-03-08T22:04:37.908902+00:00
---

# High-Availability Web App Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
