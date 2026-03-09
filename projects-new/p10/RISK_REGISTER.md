# Risk Register

| Risk ID | Category | Description | Likelihood | Impact | Score | Mitigation | Owner | Status | Review Date |
|---------|----------|-------------|------------|--------|-------|------------|-------|--------|-------------|
| R1 | Data Integrity | Iceberg metadata corruption due to failed commits | Low | Critical | 12 | Atomic commits, checkpoints, backups, monitoring | Data Eng | Open | Monthly |
| R2 | Governance | Unauthorized data access violating compliance | Low | Critical | 12 | Lake Formation RBAC, audit logs, encryption, regular audits | Compliance | Open | Monthly |
| R3 | Performance | Query performance degrades with table growth | Medium | High | 12 | Partitioning, z-ordering, compaction, caching, capacity planning | Platform | Open | Monthly |
| R4 | Performance | Small file problem increases query latency | High | Medium | 12 | Scheduled compaction jobs, write tuning, monitoring file counts | Data Eng | Open | Monthly |
| R5 | Cost | Storage costs exceed budget due to retention | Medium | High | 12 | Lifecycle policies, snapshot expiry, compression, monitoring | FinOps | Open | Monthly |
| R6 | Cost | Athena query costs spike unexpectedly | Medium | Medium | 9 | Query optimization, result caching, cost alerts, education | FinOps | Open | Monthly |
| R7 | Security | S3 bucket misconfiguration exposes data | Low | Critical | 12 | Bucket policies, Block Public Access, Terraform validation, audits | Security | Open | Quarterly |
| R8 | Security | KMS key deletion causes data unavailability | Low | Critical | 12 | Key rotation policy, multi-region keys, deletion protection, backups | Security | Open | Quarterly |
| R9 | Operational | Spark job failures block pipeline | Medium | High | 12 | Retry logic, monitoring, alerting, runbooks, on-call | Data Eng | Open | Monthly |
| R10 | Operational | Schema evolution breaks downstream consumers | Medium | High | 12 | Backward compatibility checks, testing, communication, rollback plan | Data Eng | Open | Monthly |
| R11 | Reliability | Glue Catalog throttling during heavy metadata ops | Medium | Medium | 9 | Batch updates, rate limiting, retries, catalog sharding consideration | Platform | Open | Quarterly |
| R12 | Reliability | Snapshot expiry deletes snapshots in use | Low | High | 8 | Snapshot tagging, retention safety margin, validation checks | Data Eng | Open | Quarterly |
| R13 | Scalability | Partition explosion (too many partitions) | Medium | Medium | 9 | Partition design guidelines, monitoring, table redesign if needed | Data Eng | Open | Quarterly |
| R14 | Compliance | Data retention policy not enforced | Low | High | 8 | Automated deletion jobs, audits, documentation, legal sign-off | Compliance | Open | Quarterly |
| R15 | Vendor Lock-in | AWS dependency limits portability | Medium | Medium | 9 | Abstract interfaces, multi-cloud POC, Iceberg portability advantage | Platform | Open | Annually |

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
- **Monthly:** High-score risks (≥12) reviewed by data platform team
- **Quarterly:** All risks reviewed; new risks added from incidents
- **Annually:** Full risk register audit with stakeholders (security, compliance, finance)

## Escalation
- Risks with score ≥15 escalated to engineering director
- Critical impact risks escalated to VP Engineering and Legal
