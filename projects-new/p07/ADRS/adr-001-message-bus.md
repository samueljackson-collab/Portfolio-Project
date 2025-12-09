# ADR-001: Use Kafka-Compatible Bus for Roaming Events
- **Status**: Accepted
- **Context**: High-throughput roaming events require ordering guarantees and strong tooling.
- **Decision**: Use Kafka/Redpanda for event transport with idempotent producer keys and compacted topics.
- **Consequences**:
  - Pros: Ecosystem maturity, native lag metrics, schema registry integration.
  - Cons: Operational overhead vs. simpler queues; requires tuned storage.
