# Threat Model (STRIDE)
- **Spoofing**: Fake IMSI senders; mitigated by mutual TLS and token-based auth on producer endpoints.
- **Tampering**: Kafka topic tampering; mitigated with ACLs, topic-level encryption, and checksum validation in consumer.
- **Repudiation**: Audit logging with signed Kafka headers; immutable logs stored in object storage.
- **Information Disclosure**: PII exposure; mitigate with field-level encryption and data minimization.
- **Denial of Service**: Kafka flood; rate limits at ingress gateway and autoscaling consumers.
- **Elevation of Privilege**: Namespace RBAC least-privilege and PodSecurity restricted profiles.

## Data classification
- Subscriber identifiers treated as sensitive; masked in logs and dashboards.
