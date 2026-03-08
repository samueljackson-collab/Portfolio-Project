---
title: Threat Model
description: - **Data integrity:** Signed payload hash added in `demo_job.enrich_payload` to detect tampering. - **Least privilege:** Sample Deployment runs as non-root and disables privilege escalation. - **Obser
tags: [cryptography, documentation, portfolio, quantum-computing]
path: portfolio/p21-quantum-safe-cryptography/threat-model
created: 2026-03-08T22:19:13.871171+00:00
updated: 2026-03-08T22:04:38.016902+00:00
---

# Threat Model

- **Data integrity:** Signed payload hash added in `demo_job.enrich_payload` to detect tampering.
- **Least privilege:** Sample Deployment runs as non-root and disables privilege escalation.
- **Observability:** Consumer emits a trace-friendly log entry with correlation IDs.
