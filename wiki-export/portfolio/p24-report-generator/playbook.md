---
title: Playbook
description: 1. Generate a payload: `python docker/producer/main.py`. 2. Inspect `artifacts/enriched.json` to confirm metadata enrichment. 3. Tail the consumer log output (`consumer/worker.py`) to see delivery con
tags: [documentation, portfolio]
path: portfolio/p24-report-generator/playbook
created: 2026-03-08T22:19:13.909274+00:00
updated: 2026-03-08T22:04:38.038902+00:00
---

# Playbook

1. Generate a payload: `python docker/producer/main.py`.
2. Inspect `artifacts/enriched.json` to confirm metadata enrichment.
3. Tail the consumer log output (`consumer/worker.py`) to see delivery confirmation.
4. For k8s, apply `k8s/deployment.yaml` against a local cluster (kind/minikube).
