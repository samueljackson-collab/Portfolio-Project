# Playbook

1. Generate a payload: `python docker/producer/main.py`.
2. Inspect `artifacts/enriched.json` to confirm metadata enrichment.
3. Tail the consumer log output (`consumer/worker.py`) to see delivery confirmation.
4. For k8s, apply `k8s/deployment.yaml` against a local cluster (kind/minikube).
