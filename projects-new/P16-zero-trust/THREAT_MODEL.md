# Threat Model

Threats:
- Stolen service identity
- Policy bypass via misconfigured proxy
- Lateral movement due to broad network rules

Mitigations:
- Short-lived SVIDs with automatic rotation
- OPA unit + conftest checks in CI
- Default-deny network policy and explicit allowlists
