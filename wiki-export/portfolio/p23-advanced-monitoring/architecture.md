---
title: Advanced Monitoring Architecture
description: - **Pattern:** SLO-first monitoring stack with anomaly detection hooks. - **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest. - **Execution:** Run `python 
tags: [documentation, grafana, monitoring, observability, portfolio]
path: portfolio/p23-advanced-monitoring/architecture
created: 2026-03-08T22:19:13.899601+00:00
updated: 2026-03-08T22:04:38.029902+00:00
---

# Advanced Monitoring Architecture

- **Pattern:** SLO-first monitoring stack with anomaly detection hooks.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
