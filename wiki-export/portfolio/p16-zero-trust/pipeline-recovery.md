---
title: Zero-Trust Architecture Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [documentation, network, portfolio, security, zero-trust]
path: portfolio/p16-zero-trust/pipeline-recovery
created: 2026-03-08T22:19:13.813503+00:00
updated: 2026-03-08T22:04:37.974902+00:00
---

# Zero-Trust Architecture Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
