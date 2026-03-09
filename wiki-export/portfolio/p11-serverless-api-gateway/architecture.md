---
title: API Gateway & Serverless Architecture
description: - **Pattern:** Build a Lambda + API Gateway stack with DynamoDB persistence and observability hooks. - **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest. 
tags: [documentation, portfolio]
path: portfolio/p11-serverless-api-gateway/architecture
created: 2026-03-08T22:19:13.729426+00:00
updated: 2026-03-08T22:04:37.883902+00:00
---

# API Gateway & Serverless Architecture

- **Pattern:** Build a Lambda + API Gateway stack with DynamoDB persistence and observability hooks.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
