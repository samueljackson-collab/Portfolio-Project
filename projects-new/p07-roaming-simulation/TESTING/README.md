# Testing Strategy

## Objectives
- Validate roaming policy enforcement across carrier profiles.
- Ensure impairment injection produces expected jitter/loss distributions.
- Verify consumer exports KPIs and supports idempotent replays.

## Test Types
- **Unit**: Policy rule evaluation, schema validation.
- **Integration**: Producer → Consumer pipeline with TLS enabled; impairment latencies asserted.
- **Load**: 1k–10k events/minute with HPA scaling assertions.
- **Chaos**: Drop 10% of impairment pods; expect retries and alerting.

## Test Cases
| ID | Scenario | Steps | Expected |
|----|----------|-------|----------|
| TC-ROAM-01 | Urban attach flow | Generate 100 urban events with 50ms latency profile. | Attach success rate > 98%, p95 latency < 120ms. |
| TC-ROAM-02 | Fair-use throttling | Send 20GB/session stream; verify policy marks `throttle`. | 100% flagged, consumer aggregates throttle count. |
| TC-ROAM-03 | Cross-border fraud | Inject IMSI pattern flagged as fraud. | Policy emits `block`, alert raised in metrics.
| TC-ROAM-04 | Packet loss recovery | Apply 5% loss; ensure retransmit counter increments. | KPI `drop_call_pct` < 1%, retries logged.

## Execution
- Local: `pytest -q` for unit tests; `make test-integration` to exercise producer/consumer endpoints.
- CI: Wire `docker compose -f docker/compose.roaming.yaml up -d` before integration stage.
- K8s smoke: `kubectl port-forward deploy/roaming-producer 50051:50051` then run `tests/smoke_roaming.py`.
