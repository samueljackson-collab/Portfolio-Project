# Runbooks — P07

## Runbook: Start Local Simulation Stack
1. `cp config/roaming.yaml.example config/roaming.yaml` and adjust MCC/MNC list.
2. `docker-compose -f docker/compose.roaming.yaml up -d` (HLR, VLR, Prometheus, Loki).
3. `make run-simulation` to trigger default scenario.
4. `make metrics` to query Prometheus (`http://localhost:9090`) for `p07_roam_attach_success_total`.
5. Export PCAPs from `artifacts/pcap/` if evidence is needed.

## Runbook: Rotate Logs/PII
1. Run `python jobs/rotate_logs.py --path logs/audit --days 30`.
2. Verify archive tarball under `artifacts/rotation/` contains `metadata.json` with hash list.
3. Update compliance log using `REPORT_TEMPLATES/README.md` guidance.

## Runbook: Perf Baseline
1. Launch stack with `LOW_LATENCY_MODE=true make run-simulation`.
2. Execute `pytest tests/perf/test_latency.py -q`.
3. Capture metrics snapshot using `scripts/capture_metrics.sh` writing to `reports/perf_snapshot.json`.
