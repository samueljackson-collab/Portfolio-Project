# Scheduled Jobs — Cloud-Native POC

This folder contains runnable maintenance jobs for the Cloud-Native POC prompt pack. Jobs are
intended to be invoked by a scheduler (cron, systemd timers, Kubernetes `CronJob`) and should exit
non-zero when action is required.

## `health_probe.py`
Periodic HTTP probe that validates the API's `/health` and `/ready` endpoints and enforces a latency
budget. Fails fast for non-2xx responses or slow requests so dashboards and alerting systems can
catch regressions early.

### Quick run
```bash
python3 health_probe.py --base-url http://localhost:8000 \
  --endpoints /health,/ready \
  --timeout 3 \
  --max-latency-ms 800
```

### Suggested schedules
- **Cron**: `*/5 * * * * cd /workspace/Portfolio-Project/projects-new/p09-cloud-native-poc/jobs && ./health_probe.py --json >> /var/log/p09-health.log`
- **systemd timer**: call the script with `--json` and have `OnUnitActiveSec=5min`
- **Kubernetes CronJob**: mount the repo or image and execute `python3 /opt/prompt-packs/p09-cloud-native-poc/jobs/health_probe.py --json`

### Exit codes
- `0`: All endpoints healthy and within latency budget
- `1`: At least one endpoint failed or exceeded the latency budget

### Notes
- No external dependencies beyond the Python 3 standard library
- Use `--json` for structured logging into SIEM or monitoring pipelines
- Tune `--max-latency-ms` to enforce SLOs as the service evolves
