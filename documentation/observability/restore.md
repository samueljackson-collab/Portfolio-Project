# Observability Platform Restore Guide

1. Provision replacement Kubernetes nodes labelled `observability=true`.
2. Restore Prometheus snapshot using `promtool tsdb restore` and mount existing PVC.
3. Recreate Loki S3 bucket credentials and redeploy Helm release with same values.
4. Import Grafana dashboards from `monitoring/grafana/dashboards/` and reconfigure data sources.
5. Validate Alertmanager routes by triggering a test alert via `amtool`. 
