---
title: Quantum-Safe Cryptography Architecture
description: - **Pattern:** PQ-safe key exchange demo with hybrid TLS posture checks. - **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest. - **Execution:** Run `python
tags: [cryptography, documentation, portfolio, quantum-computing]
path: portfolio/p21-quantum-safe-cryptography/architecture
created: 2026-03-08T22:19:13.874358+00:00
updated: 2026-03-08T22:04:38.013902+00:00
---

# Quantum-Safe Cryptography Architecture

- **Pattern:** PQ-safe key exchange demo with hybrid TLS posture checks.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
