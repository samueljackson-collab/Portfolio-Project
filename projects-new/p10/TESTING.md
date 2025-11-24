# Testing
- Unit: run `pytest docker/tests` for router logic.
- Failover drill: stop region-a container and ensure router points to region-b.
- K8s smoke: `kubectl -n multi-region get pods` and curl service endpoints.
