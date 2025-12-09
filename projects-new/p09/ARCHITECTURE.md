# Architecture
- Minimal producer publishes sample events to NATS.
- Consumer service processes and stores to SQLite (for POC) and exposes /metrics.
- K8s manifests include namespace, deployments, service, and HPA.
