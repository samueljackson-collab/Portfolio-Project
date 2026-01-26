# Screenshots (Sanitized Evidence)

This folder contains guidance for sanitized monitoring snapshots. The SVG placeholders were removed from the repo; store regenerated screenshots externally as needed.

## Available Snapshots
- Stored externally. Regenerate PNG exports when needed and follow the sanitization steps below.

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
