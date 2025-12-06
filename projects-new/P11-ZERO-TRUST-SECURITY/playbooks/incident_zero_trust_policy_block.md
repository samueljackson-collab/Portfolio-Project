# Incident Playbook: Zero-Trust Policy Block
1. **Detect**: Alert from Grafana/Prometheus shows spike in OPA denies.
2. **Triage**: Identify impacted service pair and request path.
3. **Inspect**: Review `opa_decision_logs` for violation reasons and caller SPIFFE ID.
4. **Rollback/Fix**: Revert to previous policy ConfigMap or patch rule to permit intended traffic with least privilege.
5. **Validate**: Run `tests/integration/test_zero_trust_flows.sh`.
6. **Postcondition**: Traffic restored; audit log captured in incident tracker.
