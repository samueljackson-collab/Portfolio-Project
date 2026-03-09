# ADR-001: Active/Passive Failover
- **Status:** Accepted
- **Context:** Simplicity and cost control outweigh active/active complexity.
- **Decision:** Use active/passive with Route 53 failover records.
- **Consequences:**
  - Lower cost; simpler data sync.
  - Requires drills to ensure RTO met; some cold-start latency on secondary.
