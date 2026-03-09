# Risk Register

| Risk ID | Category | Description | Likelihood | Impact | Score | Mitigation | Owner | Status | Review Date |
|---------|----------|-------------|------------|--------|-------|------------|-------|--------|-------------|
| R1 | Data Quality | Poor document quality leads to irrelevant retrievals | Medium | High | 12 | Source validation, quality scoring, user feedback loop | Data Eng | Open | Monthly |
| R2 | Hallucination | LLM generates ungrounded responses despite RAG | Medium | Critical | 16 | Grounding score checks, citation enforcement, eval harness | ML Eng | Open | Monthly |
| R3 | Security | Prompt injection bypasses safety guardrails | Low | Critical | 12 | Multi-layer filtering, input sanitization, monitoring | Security | Open | Monthly |
| R4 | Reliability | Vector DB outage disrupts service | Low | High | 8 | HA deployment, fallback responses, graceful degradation | SRE | Open | Quarterly |
| R5 | Performance | High latency under load degrades UX | Medium | High | 12 | Caching, HPA, async processing, load testing | SRE | Open | Monthly |
| R6 | Cost | Token usage exceeds budget | High | Medium | 12 | Rate limiting, caching, budget alerts, GPT-3.5 over GPT-4 | FinOps | Open | Monthly |
| R7 | PII Leakage | Sensitive data exposed in logs or responses | Low | Critical | 12 | PII detection/redaction, encryption, access controls | Compliance | Open | Monthly |
| R8 | Retrieval Drift | Document updates not reflected in embeddings | Medium | Medium | 9 | Scheduled re-embedding, version tracking, freshness monitoring | Data Eng | Open | Quarterly |
| R9 | Auth Bypass | Weak token validation allows unauthorized access | Low | High | 8 | JWT best practices, token rotation, security audits | Security | Open | Quarterly |
| R10 | Model Staleness | Embedding/LLM models become outdated | Medium | Medium | 9 | Model versioning, evaluation tracking, upgrade plan | ML Eng | Open | Quarterly |
| R11 | Vendor Lock-In | OpenAI dependency limits flexibility | Medium | Medium | 9 | Abstract LLM interface, test alternative providers, local model POC | Platform | Open | Annually |
| R12 | Scaling Limits | Vector DB performance degrades at 10M+ docs | Low | High | 8 | Sharding strategy, query optimization, capacity planning | Platform | Open | Quarterly |
| R13 | Feedback Bias | Negative feedback not captured or acted upon | Medium | Medium | 9 | Prominent feedback UI, review workflow, continuous improvement | Product | Open | Monthly |
| R14 | Compliance | GDPR/data residency requirements not met | Low | Critical | 12 | Data classification, regional deployments, legal review | Compliance | Open | Quarterly |

## Risk Scoring
- **Likelihood:** Low (1), Medium (3), High (5)
- **Impact:** Low (2), Medium (4), High (6), Critical (8)
- **Score:** Likelihood × Impact (prioritize ≥12)

## Mitigation Status
- **Open:** Active risk, mitigations in progress
- **Mitigated:** Controls implemented and validated
- **Accepted:** Risk accepted with documented rationale
- **Closed:** No longer applicable

## Review Cadence
- **Monthly:** High-score risks (≥12)
- **Quarterly:** All risks reviewed, new risks added
- **Annually:** Full risk audit with stakeholders
