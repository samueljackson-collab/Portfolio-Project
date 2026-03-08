---
title: Data Pipeline (Airflow) Pipeline Recovery
description: 1. Re-run producer with `--validate`. 2. Clear `artifacts/` if stale files cause confusion. 3. Reapply `k8s/deployment.yaml` to restart the worker.
tags: [analytics, data-engineering, documentation, pipeline, portfolio]
path: portfolio/p12-data-pipeline-airflow/pipeline-recovery
created: 2026-03-08T22:19:13.751193+00:00
updated: 2026-03-08T22:04:37.898902+00:00
---

# Data Pipeline (Airflow) Pipeline Recovery

1. Re-run producer with `--validate`.
2. Clear `artifacts/` if stale files cause confusion.
3. Reapply `k8s/deployment.yaml` to restart the worker.
