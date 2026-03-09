---
title: Autonomous DevOps Platform Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [documentation, portfolio]
path: portfolio/p22-autonomous-devops-platform/pipeline-recovery
created: 2026-03-08T22:19:13.894347+00:00
updated: 2026-03-08T22:04:38.022902+00:00
---

# Autonomous DevOps Platform Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
