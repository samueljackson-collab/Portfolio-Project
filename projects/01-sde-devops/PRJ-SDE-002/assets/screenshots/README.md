# Screenshots (Text-Only Repository Guidance)

Binary dashboard captures are intentionally omitted because the PR channel does not support binary assets. Use this folder to store locally generated, sanitized PNGs when working outside the PR channel.

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
