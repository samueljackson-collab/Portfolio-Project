---
title: Threat Model
description: - **Data integrity:** Signed payload hash added in `demo_job.enrich_payload` to detect tampering. - **Least privilege:** Sample Deployment runs as non-root and disables privilege escalation. - **Obser
tags: [automation, cicd, containers, devops, documentation, kubernetes, orchestration, portfolio]
path: portfolio/p18-k8s-cicd/threat-model
created: 2026-03-08T22:19:13.832226+00:00
updated: 2026-03-08T22:04:37.991902+00:00
---

# Threat Model

- **Data integrity:** Signed payload hash added in `demo_job.enrich_payload` to detect tampering.
- **Least privilege:** Sample Deployment runs as non-root and disables privilege escalation.
- **Observability:** Consumer emits a trace-friendly log entry with correlation IDs.
