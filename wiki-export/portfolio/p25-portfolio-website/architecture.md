---
title: Portfolio Website Experience Architecture
description: - **Pattern:** Static+API hybrid site with content build pipeline and uptime probes. - **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest. - **Execution:**
tags: [documentation, portfolio]
path: portfolio/p25-portfolio-website/architecture
created: 2026-03-08T22:19:13.921550+00:00
updated: 2026-03-08T22:04:38.048902+00:00
---

# Portfolio Website Experience Architecture

- **Pattern:** Static+API hybrid site with content build pipeline and uptime probes.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
