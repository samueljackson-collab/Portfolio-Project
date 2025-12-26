# Risk Register

| Risk ID | Category | Description | Likelihood | Impact | Score | Mitigation | Owner | Status | Review Date |
|---------|----------|-------------|------------|--------|-------|------------|-------|--------|-------------|
| R1 | Data Quality/Drift | Training data quality degrades undetected, causing model performance drop | Medium | High | 12 | Automated data validation (Great Expectations), drift monitoring, alerts | Data Eng | Open | Monthly |
| R2 | Data Quality/Drift | Concept drift not detected; model predictions become stale | Medium | High | 12 | Drift detector with tuned thresholds, automated retraining triggers, business metric monitoring | ML Eng | Open | Monthly |
| R3 | Model Bias | Model exhibits bias against protected groups, regulatory/reputational risk | Low | High | 8 | Fairness audits (Fairlearn), diverse training data, human review gates, explainability tools | ML Lead | Open | Quarterly |
| R4 | Infrastructure | Kubeflow/MLflow/Feast outage disrupts training or serving | Medium | High | 12 | HA deployments (multi-replica), health checks, runbooks, failover to backup clusters | Platform Eng | Open | Monthly |
| R5 | Infrastructure | GPU node unavailability delays critical retraining | Medium | Medium | 9 | Multi-region node pools, spot+on-demand mix, pipeline retry logic | Platform Eng | Open | Quarterly |
| R6 | Cost | Uncontrolled GPU usage causes budget overrun | Medium | High | 12 | Resource quotas, cost alerts (threshold > 20% over baseline), spot instances, auto-shutdown for idle jobs | FinOps | Open | Monthly |
| R7 | Cost | Artifact storage growth exceeds budget | Medium | Medium | 9 | S3 lifecycle policies (delete old artifacts after 90 days), model compression, deduplication | Platform Eng | Open | Quarterly |
| R8 | Security | Model or data exfiltration via compromised credentials | Low | Critical | 12 | Short-lived credentials (IRSA/Workload Identity), secret scanning, audit logs, encryption | Security | Open | Monthly |
| R9 | Security | Supply chain attack via malicious dependency in pipeline | Medium | High | 12 | SBOM generation, vulnerability scanning (Trivy), image signing (Cosign), admission control | Security | Open | Monthly |
| R10 | Security | PII leakage in logs or model artifacts | Low | Critical | 12 | PII detection/redaction, log filtering, encryption at rest, access audits | Compliance | Open | Monthly |
| R11 | Governance | Models deployed without proper approval, violating compliance | Low | High | 8 | Enforced promotion workflow (MLflow stages), approval tickets, audit trail | ML Lead | Open | Quarterly |
| R12 | Governance | Lack of model lineage hampers debugging and audits | Low | Medium | 6 | MLflow metadata (git SHA, dataset version), automated tagging in pipelines, documentation templates | ML Lead | Open | Quarterly |
| R13 | Operational | Training pipeline fails repeatedly, blocking model updates | Medium | High | 12 | Robust error handling, retries, monitoring, runbooks, on-call escalation | Platform Eng | Open | Monthly |
| R14 | Operational | Canary deployment issues cause production outage | Low | High | 8 | Thorough testing in staging, gradual rollout (10% canary), automated rollback on errors | ML SRE | Open | Quarterly |
| R15 | Performance | Inference latency exceeds SLA, harming user experience | Medium | High | 12 | Load testing, HPA tuning, caching (Feast), model optimization (ONNX), capacity planning | ML SRE | Open | Monthly |
| R16 | Performance | Feature store (Feast) latency bottleneck | Medium | Medium | 9 | Redis scaling, caching in predictor, batch feature retrieval, monitoring | Platform Eng | Open | Quarterly |
| R17 | Reliability | Drift detector false positives trigger unnecessary retraining, wasting compute | Medium | Medium | 9 | Threshold tuning, historical validation, human-in-the-loop review | ML Eng | Open | Quarterly |
| R18 | Reliability | Model versioning conflicts (multiple teams deploying concurrently) | Low | Medium | 6 | Namespace isolation, registry conventions, deployment locks, communication channels | ML Lead | Open | Quarterly |
| R19 | Compliance | GDPR/CCPA violation due to improper data handling | Low | Critical | 12 | Data classification, PII anonymization, retention policies, legal review | Compliance | Open | Quarterly |
| R20 | Vendor | Kubeflow/MLflow/Feast project abandonment or breaking changes | Low | Medium | 6 | Monitor project health, contribute to communities, maintain fork/migration plan | Platform Eng | Open | Annually |

## Risk Scoring
- **Likelihood:** Low (1), Medium (3), High (5)
- **Impact:** Low (2), Medium (4), High (6), Critical (8)
- **Score:** Likelihood × Impact (prioritize scores ≥ 12)

## Mitigation Status
- **Open:** Risk acknowledged, mitigations in progress or planned
- **Mitigated:** Controls implemented and validated
- **Accepted:** Risk accepted; no further action (document rationale)
- **Closed:** Risk no longer applicable

## Review Cadence
- **Monthly:** High-score risks (≥ 12) reviewed by ML platform team
- **Quarterly:** All risks reviewed; new risks added from incidents/changes
- **Annually:** Full risk register audit with stakeholders (security, compliance, finance)

## Escalation
- Risks with score ≥ 15 escalated to engineering director
- Critical impact risks escalated to VP Engineering and Legal (for compliance)
