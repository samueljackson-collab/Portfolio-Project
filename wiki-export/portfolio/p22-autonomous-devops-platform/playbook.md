---
title: Playbook
description: 1. Generate a payload: `python docker/producer/main.py`. 2. Inspect `artifacts/enriched.json` to confirm metadata enrichment. 3. Tail the consumer log output (`consumer/worker.py`) to see delivery con
tags: [documentation, portfolio]
path: portfolio/p22-autonomous-devops-platform/playbook
created: 2026-03-08T22:19:13.887133+00:00
updated: 2026-03-08T22:04:38.021902+00:00
---

# Playbook

1. Generate a payload: `python docker/producer/main.py`.
2. Inspect `artifacts/enriched.json` to confirm metadata enrichment.
3. Tail the consumer log output (`consumer/worker.py`) to see delivery confirmation.
4. For k8s, apply `k8s/deployment.yaml` against a local cluster (kind/minikube).
