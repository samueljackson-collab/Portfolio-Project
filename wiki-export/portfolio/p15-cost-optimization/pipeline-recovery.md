---
title: Cloud Cost Optimization Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [documentation, portfolio]
path: portfolio/p15-cost-optimization/pipeline-recovery
created: 2026-03-08T22:19:13.801090+00:00
updated: 2026-03-08T22:04:37.967902+00:00
---

# Cloud Cost Optimization Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
