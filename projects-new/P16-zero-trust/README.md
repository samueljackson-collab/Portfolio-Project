# P16 – Zero-Trust Reference

Microsegmented network with identity-aware proxies, mTLS, and policy-as-code for east/west control.

## Quick start
- Stack: OPA/Envoy, SPIRE for workload identities, WireGuard for node tunnels.
- Flow: Nodes enroll via SPIRE, Envoy sidecars enforce OPA policies, and traffic allowed only with valid SVIDs and policy decisions.
- Run: make lint then pytest tests/test_policy.py
- Operate: Rotate SVID certs daily, sync policy bundles via CI, and monitor denied flows in Loki dashboards.
