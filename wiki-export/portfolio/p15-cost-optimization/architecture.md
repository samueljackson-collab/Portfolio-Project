---
title: Cloud Cost Optimization Architecture
description: - **Pattern:** CUR-backed analytics with tagging compliance and savings plan insights. - **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest. - **Execution:
tags: [documentation, portfolio]
path: portfolio/p15-cost-optimization/architecture
created: 2026-03-08T22:19:13.792723+00:00
updated: 2026-03-08T22:04:37.965902+00:00
---

# Cloud Cost Optimization Architecture

- **Pattern:** CUR-backed analytics with tagging compliance and savings plan insights.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
