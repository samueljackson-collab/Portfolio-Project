---
title: High-Availability Web App Architecture
description: - **Pattern:** NGINX front-end with replicated app tier and resilient session handling. - **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest. - **Execution
tags: [documentation, portfolio]
path: portfolio/p13-ha-webapp/architecture
created: 2026-03-08T22:19:13.756312+00:00
updated: 2026-03-08T22:04:37.906902+00:00
---

# High-Availability Web App Architecture

- **Pattern:** NGINX front-end with replicated app tier and resilient session handling.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
