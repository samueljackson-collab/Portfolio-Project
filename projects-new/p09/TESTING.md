# Testing
- Unit: run `pytest docker/tests` for producer/consumer utilities.
- Integration: `docker compose up` then hit `/metrics` to verify ingest counters.
- Smoke (K8s): `kubectl -n cloud-poc logs deploy/poc-consumer` should show processed events.
