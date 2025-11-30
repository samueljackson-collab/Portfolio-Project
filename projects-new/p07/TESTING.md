# Testing Strategy

## Test pyramid
- **Unit**: Python producer parsers; Go consumer validation functions; run via `make test`.
- **Contract**: JSON Schema validation against sample roaming events in `tests/data/roaming_event.json`.
- **Integration**: Docker Compose harness spins Kafka + Postgres + services; asserts end-to-end ingestion.
- **Performance**: Locust profiles targeting producer endpoint; Kafka lag alert checks under sustained load.
- **Chaos**: Fault injection toggles for Kafka latency and DB failover; verify retries and alerts.

## Key cases
- Reject malformed IMSI/ICCID pairs and log structured errors.
- Ensure duplicate TAP-in events are deduped by message key.
- Verify anomaly job opens PagerDuty incident when TAP-out missing for >30 minutes.
- Validate metrics presence: `roaming_events_processed_total`, `roaming_anomalies_total`.

## Data management
- Synthetic scenarios are deterministic; seeds live under `docker/jobs/scenarios/`.
- Test data retention: cleanup script `docker/jobs/cleanup.sh` purges containers/volumes after runs.

## How to run
```sh
# Unit
make test

# Integration
make compose-test

# Performance baseline
make perf-test
```
