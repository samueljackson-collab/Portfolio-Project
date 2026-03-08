---
title: CI/CD + Kubernetes Architecture
description: - **Pattern:** GitOps-style deployment pipeline with container builds and manifest promotion. - **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest. - **Exe
tags: [automation, cicd, containers, devops, documentation, kubernetes, orchestration, portfolio]
path: portfolio/p18-k8s-cicd/architecture
created: 2026-03-08T22:19:13.835631+00:00
updated: 2026-03-08T22:04:37.988902+00:00
---

# CI/CD + Kubernetes Architecture

- **Pattern:** GitOps-style deployment pipeline with container builds and manifest promotion.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
