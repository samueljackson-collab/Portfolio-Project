---
title: Threat Model
description: - **Data integrity:** Signed payload hash added in `demo_job.enrich_payload` to detect tampering. - **Least privilege:** Sample Deployment runs as non-root and disables privilege escalation. - **Obser
tags: [analytics, data-engineering, documentation, pipeline, portfolio]
path: portfolio/p12-data-pipeline-airflow/threat-model
created: 2026-03-08T22:19:13.740506+00:00
updated: 2026-03-08T22:04:37.899902+00:00
---

# Threat Model

- **Data integrity:** Signed payload hash added in `demo_job.enrich_payload` to detect tampering.
- **Least privilege:** Sample Deployment runs as non-root and disables privilege escalation.
- **Observability:** Consumer emits a trace-friendly log entry with correlation IDs.
