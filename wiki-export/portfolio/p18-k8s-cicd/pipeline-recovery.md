---
title: CI/CD + Kubernetes Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [automation, cicd, containers, devops, documentation, kubernetes, orchestration, portfolio]
path: portfolio/p18-k8s-cicd/pipeline-recovery
created: 2026-03-08T22:19:13.842270+00:00
updated: 2026-03-08T22:04:37.990902+00:00
---

# CI/CD + Kubernetes Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
