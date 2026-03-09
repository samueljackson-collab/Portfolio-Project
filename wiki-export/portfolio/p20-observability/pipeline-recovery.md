---
title: Observability Engineering Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [documentation, portfolio]
path: portfolio/p20-observability/pipeline-recovery
created: 2026-03-08T22:19:13.866161+00:00
updated: 2026-03-08T22:04:38.006902+00:00
---

# Observability Engineering Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
