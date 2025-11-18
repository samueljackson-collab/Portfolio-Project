# Threat Model: Zero-Trust Platform
## Assets
- SPIRE CA keys, SVIDs, OPA policies, Envoy configs, application data.
## Trust Boundaries
- User edge vs cluster ingress; workload namespace vs control plane; sidecar vs application container.
## Threats (STRIDE)
- **Spoofing:** Forged certificates or SPIFFE IDs.
- **Tampering:** Modified OPA policies or Envoy configs.
- **Repudiation:** Missing decision logs for denied traffic.
- **Information Disclosure:** mTLS disabled leading to plaintext leaks.
- **Denial of Service:** Flood of unauthorized requests increasing OPA latency.
- **Elevation of Privilege:** Compromised service account accessing admin.
## Mitigations
- SPIRE-issued short-lived certs; strict Envoy validation context; OPA decision logging; NetworkPolicies enforcing sidecar path; Prometheus alerts on denies and handshake errors.
