---
title: API Gateway & Serverless Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [documentation, portfolio]
path: portfolio/p11-serverless-api-gateway/pipeline-recovery
created: 2026-03-08T22:19:13.735441+00:00
updated: 2026-03-08T22:04:37.885902+00:00
---

# API Gateway & Serverless Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
