# Zero-Trust Architecture Architecture

- **Pattern:** Policy-driven access controls with mutual TLS enforcement and service posture checks.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
