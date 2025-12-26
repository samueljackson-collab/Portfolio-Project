# ADR-001: Contract Tests as Gate for Deployments
- **Status:** Accepted
- **Context:** APIs are versioned but occasionally change without notice. We need early detection of breaking changes.
- **Decision:** Make contract tests blocking in CI/CD; no deploy if drift detected.
- **Consequences:**
  - Ensures consumers are protected; adds gate time (~2 minutes) per pipeline.
  - Requires API owners to update schemas promptly.
