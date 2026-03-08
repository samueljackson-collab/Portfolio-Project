---
title: Playbook: Latency Regression
description: 1. **Trigger**: Alert `poc_latency_p95_ms > 250` for 5m. 2. **Verify**: Check pod resource limits; confirm no throttling. 3. **Scale**: Increase replicas via `kubectl scale deploy/poc-api --replicas=3
tags: [documentation, portfolio]
path: portfolio/p09-cloud-native-poc/latency-regression
created: 2026-03-08T22:19:14.006690+00:00
updated: 2026-03-08T22:04:38.115902+00:00
---

# Playbook: Latency Regression

1. **Trigger**: Alert `poc_latency_p95_ms > 250` for 5m.
2. **Verify**: Check pod resource limits; confirm no throttling.
3. **Scale**: Increase replicas via `kubectl scale deploy/poc-api --replicas=3`.
4. **Profile**: Enable uvicorn access logs and sample traces; inspect slow endpoints.
5. **Record**: Update `REPORT_TEMPLATES/release_report.md` with findings.
