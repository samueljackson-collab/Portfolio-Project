---
title: Data Pipeline (Airflow) Architecture
description: - **Pattern:** Containerized Airflow ETL with sample DAGs and data quality checks. - **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest. - **Execution:** R
tags: [analytics, data-engineering, documentation, pipeline, portfolio]
path: portfolio/p12-data-pipeline-airflow/architecture
created: 2026-03-08T22:19:13.743676+00:00
updated: 2026-03-08T22:04:37.896902+00:00
---

# Data Pipeline (Airflow) Architecture

- **Pattern:** Containerized Airflow ETL with sample DAGs and data quality checks.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
