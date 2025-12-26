# Threat Model

## Assets
- Roaming event data (potential PII)
- TLS certificates for producer/consumer
- Policy rules and fraud heuristics

## Threats
- **Eavesdropping** on gRPC traffic between producer and consumer.
- **Data poisoning** by injecting malformed events to skew KPIs.
- **Credential leakage** for certificates or Kubernetes secrets.
- **Replay attacks** using previously captured roaming batches.

## Mitigations
- Enforce mTLS on gRPC endpoints; rotate certs every 90 days.
- Schema validation in producer and consumer with rejection metrics.
- Kubernetes secrets mounted as tmpfs; restrict RBAC to namespace operators.
- Nonce and timestamp validation to detect replay attempts.
