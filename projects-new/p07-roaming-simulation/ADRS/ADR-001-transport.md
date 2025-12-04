# ADR-001: Use gRPC for Event Transport
- **Status:** Accepted
- **Context:** Producers and consumers exchange high-volume roaming events that need schema enforcement and low latency.
- **Decision:** Use gRPC with protobuf schemas instead of REST/JSON.
- **Consequences:**
  - Pros: Strong typing, streaming support, easy mTLS.
  - Cons: Extra tooling for debugging; requires proto compiler in CI.
