# Runbook: Check Zero-Trust Health
- Confirm SPIRE server and agents are running: `kubectl -n security get pods`.
- Check number of issued SVIDs: `kubectl -n security logs statefulset/spire-server | grep SVID`.
- Inspect Envoy stats: `kubectl -n apps exec deploy/frontend -- curl -s localhost:15000/stats | grep handshake`.
- Review OPA decision counts: `kubectl -n apps logs deploy/frontend -c opa | tail`.
- Validate Prometheus alerts status: `kubectl -n observability get pods` and Grafana dashboards.
