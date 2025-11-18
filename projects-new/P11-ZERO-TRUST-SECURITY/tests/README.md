# Testing Strategy

## Unit Tests
- Run `opa test policies policies/tests` to validate Rego rules for service-to-service authorization.
- Extend with helper libraries to validate SPIRE/Envoy configuration renderers if added.

## Integration Tests
- Deploy cluster via `kind` and apply manifests.
- From test pod in `apps` namespace, verify allowed flow:
  ```bash
  kubectl -n apps exec deploy/frontend -- curl -s http://api:8080/payments
  ```
- Verify blocked flow (guest to admin):
  ```bash
  kubectl -n apps exec deploy/payments -- curl -s -o /dev/null -w "%{http_code}\n" http://admin:8080/ops
  # Expect 403
  ```
- Expired identity scenario: scale down SPIRE server or revoke entry, then confirm Envoy mTLS fails (curl returns 503 with TLS error).

## Security Tests
- Attempt plaintext HTTP between pods (`curl http://api:8080` bypassing Envoy) — should fail due to NetworkPolicy.
- Attempt direct pod IP to admin without sidecar — expect deny.
- OPA negative tests: inject unauthorized SPIFFE ID using test sidecar and expect `403` with violation message.

## Files
- `integration/test_zero_trust_flows.sh`: bash script orchestrating happy-path and blocked scenarios.
- `policies/tests/test_service_to_service.rego`: policy unit tests.
