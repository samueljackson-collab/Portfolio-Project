---
title: Cloud Security Automation Architecture
description: - **Pattern:** CIS scanning, drift detection, and remediation hooks. - **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest. - **Execution:** Run `python doc
tags: [compliance, devsecops, documentation, portfolio, security]
path: portfolio/p19-security-automation/architecture
created: 2026-03-08T22:19:13.848944+00:00
updated: 2026-03-08T22:04:37.996902+00:00
---

# Cloud Security Automation Architecture

- **Pattern:** CIS scanning, drift detection, and remediation hooks.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
