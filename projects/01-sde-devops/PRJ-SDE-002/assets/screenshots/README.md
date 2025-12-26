# Screenshots (Sanitized Evidence)

This folder contains sanitized SVG snapshots of key monitoring views. Use PNG exports for higher-fidelity captures as needed.

## Available Snapshots
- `PRJ-SDE-002_dashboards_01_20251110.svg` — Grafana infrastructure overview.
- `PRJ-SDE-002_monitoring_01_20251110.svg` — Prometheus targets health.
- `PRJ-SDE-002_monitoring_02_20251110.svg` — Alertmanager overview.

## How to Recreate Sanitized Screenshots
1. Import the Grafana dashboards from `../grafana/dashboards/` (Infrastructure overview, Application metrics, Backup health).
2. Point them at demo or lab datasources that use placeholder hostnames (e.g., `demo-api`, `pbs.example.internal`) and no real customer data.
3. Apply redaction overlays or Grafana text panels for any sensitive values before capturing.
4. Capture screenshots from Grafana (Share → PNG) and save them here as `infrastructure-overview.png` or `backup-health.png`.
5. Verify captures against the sanitization checklist in the asset `README.md` before sharing.

## Sanitization Reminder
- Do not include tenant/customer identifiers.
- Keep URLs/hosts generic and secrets injected via environment variables.
- If in doubt, regenerate using mock data only.
