---
title: Report Generator Platform Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [documentation, portfolio]
path: portfolio/p24-report-generator/pipeline-recovery
created: 2026-03-08T22:19:13.916332+00:00
updated: 2026-03-08T22:04:38.040902+00:00
---

# Report Generator Platform Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
