# Standard Operating Procedures — P07

## Daily Checks
- Ensure `docker ps` shows HLR, VLR, telemetry containers healthy.
- Review Grafana dashboard `Roaming Overview` for attach success trend.
- Confirm last `jobs/rotate_logs.py` run is within 24h (check `artifacts/rotation/manifest.json`).

## Change Management
- All config updates to `config/roaming.yaml` require PR + link to test evidence.
- PCAP capture toggles must be documented in change ticket with retention plan.
- Secrets rotation (`Ki` values) performed monthly; update `.env` and re-run `make sync-secrets`.

## Data Handling
- Use `scripts/sanitize_logs.sh` before sharing logs externally.
- Delete PCAPs older than 30 days via `python jobs/rotate_logs.py --delete`.
