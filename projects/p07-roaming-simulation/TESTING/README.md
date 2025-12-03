# Testing Strategy — P07

## Test Types
- **Unit:** State-machine transitions, IMSI validator, HLR/VLR adapters (pytest).
- **Integration:** MAP/Diameter handshake between mock VLR and HLR, billing trigger generation, PCAP hook writes capture files.
- **E2E:** Scenario-driven roaming journeys using `config/roaming.yaml` with assertions on success/failure outcomes and latency budgets.
- **Chaos:** Optional packet loss/latency injection via `toxiproxy` container to validate retry behavior.

## How to Run
```bash
# Lint + unit
make lint test-unit

# Integration (requires docker compose)
make test-integration

# E2E with coverage + JUnit
make test-e2e
pytest --cov=src --cov-report=xml --junitxml=reports/junit.xml
```

## Test Matrix
| Scenario | Expected Behavior | Assertion |
| --- | --- | --- |
| Valid roam with agreement | Device attaches to visited network | `result == SUCCESS`, latency < 300ms |
| No agreement | Reject with `ROAMING_DENIED` | `failure_reason == "NO_AGREEMENT"` |
| IMSI format error | Reject early | Validator raises ValueError |
| Billing triggered | Generate CDR stub | CDR event persists to `logs/billing.jsonl` |
| Packet loss 5% | Retry with backoff | Event eventually succeeds or dead-lettered |

## Data and Fixtures
- **`tests/fixtures/subscribers.json`**: synthetic subscribers for happy-path and denial cases.
- **`tests/fixtures/pcap/`**: trimmed pcap samples proving packet-capture hook.
- **`tests/fixtures/events.csv`**: replay file for deterministic state-machine runs.

## Evidence and Reporting
- Coverage reports stored under `reports/coverage/`.
- PCAPs stored under `artifacts/pcap/` and published in CI.
- JUnit XML uploaded by CI for build health.
- Include run metadata (commit SHA, env vars) in `reports/run-metadata.json`.
