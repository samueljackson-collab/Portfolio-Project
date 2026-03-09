---
title: Threat Model
description: - **Data integrity:** Signed payload hash added in `demo_job.enrich_payload` to detect tampering. - **Least privilege:** Sample Deployment runs as non-root and disables privilege escalation. - **Obser
tags: [documentation, portfolio]
path: portfolio/p25-portfolio-website/threat-model
created: 2026-03-08T22:19:13.918691+00:00
updated: 2026-03-08T22:04:38.051902+00:00
---

# Threat Model

- **Data integrity:** Signed payload hash added in `demo_job.enrich_payload` to detect tampering.
- **Least privilege:** Sample Deployment runs as non-root and disables privilege escalation.
- **Observability:** Consumer emits a trace-friendly log entry with correlation IDs.
