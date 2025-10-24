# Grafana Dashboard Catalog

| Dashboard | UID | Owner | Review Cadence | Notes |
| --- | --- | --- | --- | --- |
| Golden Signals | gs-core | Platform Team | Monthly | Tied to SLO reports shared with stakeholders |
| Backup Assurance | backup-ops | SRE | Weekly | Includes heatmap of duration vs. size |
| Hardware Health | hw-lab | Infra | Monthly | SMART alerts, power draw, UPS runtime |
| Synthetic Probes | synthetics | Platform | Bi-weekly | Tracks HTTP checks and certificate expiry |

## Provisioning Path
Dashboards live in `grafana/dashboards/*.json`. FluxCD config maps render them into the cluster:
```bash
yq '.dashboardProviders.providers[0].options.path' grafana/provisioning/dashboards.yaml
```

## Change Control
1. Update JSON using Grafana UI export.
2. Run `make lint-dashboards` to ensure JSON formatting.
3. Submit PR with screenshots and threshold changes summarized.
