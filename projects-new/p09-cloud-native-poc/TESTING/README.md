# Testing Strategy

## Goals
- Verify CRUD endpoints and error paths.
- Confirm readiness/liveness behavior for rollout safety.
- Exercise worker -> API interactions.

## Cases
| ID | Scenario | Expected |
|----|----------|----------|
| TC-POC-01 | GET /health | 200 with `status: ok`. |
| TC-POC-02 | POST /todos with valid payload | 201 with ID, data persisted. |
| TC-POC-03 | Unauthorized without API key when required | 401 response. |
| TC-POC-04 | Worker health check loop | Non-zero success count, zero failures in metrics. |

## Execution
- Unit: `pytest producer tests` (placeholder for expansion).
- Integration: Run `docker compose -f docker/compose.poc.yaml up tests`.
- K8s smoke: `kubectl port-forward svc/poc-api 8000:80` then run `consumer/checks.py`.
