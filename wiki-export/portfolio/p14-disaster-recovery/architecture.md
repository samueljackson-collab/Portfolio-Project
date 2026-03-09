---
title: Disaster Recovery Architecture
description: - **Pattern:** Backup/restore workflows with automated failover drills. - **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest. - **Execution:** Run `python 
tags: [documentation, portfolio]
path: portfolio/p14-disaster-recovery/architecture
created: 2026-03-08T22:19:13.767581+00:00
updated: 2026-03-08T22:04:37.917902+00:00
---

# Disaster Recovery Architecture

- **Pattern:** Backup/restore workflows with automated failover drills.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
