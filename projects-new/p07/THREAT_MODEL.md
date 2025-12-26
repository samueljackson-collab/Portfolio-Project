# Threat Model (STRIDE/MITRE ATT&CK)

## Assets
- **Data:** Training datasets, feature stores (offline/online), prediction logs, user data
- **Models:** Trained model artifacts, model weights, MLflow registry entries
- **Infrastructure:** Kubernetes clusters, Kubeflow/MLflow/Feast services, GPU nodes, S3/GCS buckets
- **Secrets:** Cloud credentials (AWS keys, GCP service accounts), database passwords, API tokens, model signing keys
- **Code:** Pipeline definitions, training scripts, serving predictors, CI/CD workflows

## Entry Points
- **External:** KFServing inference endpoints (HTTPS), MLflow UI (authenticated web), Feast online store (gRPC/HTTP)
- **Internal:** Kubeflow Pipelines API, Feast materialization jobs, CI/CD pipelines (GitHub Actions), Kubectl/cloud console access
- **Data Ingestion:** S3/GCS upload endpoints, Kafka topics (if streaming), database connections

## Threats & Mitigations

### Spoofing (Identity)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| Unauthorized access to MLflow UI | High - Model theft, tampering | Enable authentication (LDAP/OAuth), enforce RBAC, audit logs | Low (with controls) |
| Impersonation of service accounts | High - Privilege escalation | Use K8s service account tokens with short TTL, Workload Identity (GCP)/IRSA (AWS) | Medium (key leakage risk) |
| Spoofed inference requests | Medium - Resource abuse, data poisoning | API key auth, rate limiting, WAF, client TLS certs | Low |

**MITRE Mapping:** T1078 (Valid Accounts), T1550 (Use Alternate Authentication Material)

### Tampering (Integrity)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| Model poisoning via training data manipulation | Critical - Biased/malicious predictions | Data lineage tracking, input validation, schema checks, access control to data sources | Medium (insider threat) |
| Registry tampering (unauthorized model upload) | High - Backdoored models | MLflow RBAC, model signing (Cosign), immutable artifact storage (S3 versioning) | Low |
| Pipeline code injection | Critical - Arbitrary code execution | Code review, signed commits, CI/CD security scans, restricted pipeline submission | Low |

**MITRE Mapping:** T1565 (Data Manipulation), T1195.002 (Supply Chain Compromise - Software Supply Chain)

### Repudiation (Non-repudiation)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| Untracked model deployment | High - Compliance violation | Audit logs for MLflow/KFServing, immutable deployment records, signed releases | Low |
| Unattributed data access | Medium - Privacy breach | Cloud audit logs (CloudTrail/Cloud Audit Logs), Feast access logs | Low |

**MITRE Mapping:** T1070 (Indicator Removal on Host)

### Information Disclosure (Confidentiality)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| PII leakage in training data or logs | Critical - GDPR/CCPA violation | PII detection/redaction in pipelines, encryption at rest (S3-SSE, disk encryption), column-level access control in Feast | Medium (misconfiguration risk) |
| Model extraction via inference API | High - IP theft | Rate limiting, API key rotation, model watermarking, output obfuscation for sensitive models | Medium (determined adversary) |
| Exposed S3/GCS buckets | Critical - Data breach | Bucket policies (private by default), IAM least privilege, S3 Block Public Access | Low |

**MITRE Mapping:** T1530 (Data from Cloud Storage Object), T1552.001 (Unsecured Credentials in Files)

### Denial of Service (Availability)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| Inference endpoint flooding | High - Service outage | Rate limiting (Istio/Envoy), auto-scaling (HPA), DDoS protection (CloudFlare/AWS Shield) | Low |
| Resource exhaustion via malicious training jobs | Medium - Cluster instability | Resource quotas per namespace, PodDisruptionBudgets, job timeouts | Low |
| Feast online store overload | High - Serving failures | Redis/DynamoDB auto-scaling, caching, circuit breakers in predictors | Medium (cascading failures) |

**MITRE Mapping:** T1499 (Endpoint Denial of Service), T1496 (Resource Hijacking)

### Elevation of Privilege (Authorization)
| Threat | Impact | Mitigation | Residual Risk |
|--------|--------|------------|---------------|
| Container escape to host | Critical - Cluster compromise | Pod Security Standards (restricted), seccomp/AppArmor profiles, runtime security (Falco) | Low |
| RBAC misconfiguration granting excessive permissions | High - Unauthorized operations | Least privilege by default, regular RBAC audits, deny-by-default policies | Medium (human error) |
| Supply chain attack via compromised image | Critical - Backdoor deployment | Image signing (Cosign), vulnerability scanning (Trivy), SBOM generation, admission controllers (OPA Gatekeeper) | Medium (zero-day in dependencies) |

**MITRE Mapping:** T1611 (Escape to Host), T1068 (Exploitation for Privilege Escalation)

---

## Attack Scenarios

### Scenario 1: Model Poisoning via Data Injection
**Attacker Goal:** Cause model to misclassify specific inputs (e.g., competitor products ranked lower).

**Attack Path:**
1. Attacker gains access to training data source (S3 bucket, database)
2. Injects mislabeled samples targeting specific patterns
3. Scheduled retraining ingests poisoned data
4. Model learns adversarial patterns and deploys to production
5. Biased predictions harm business or users

**Mitigations:**
- [ ] Data source access restricted to data engineers + audit logs
- [ ] Schema validation and anomaly detection in data ingestion component
- [ ] Statistical checks for label distribution shifts
- [ ] Human review for high-stakes model updates
- [ ] A/B testing to catch performance degradation

**Detection:** Drift detector flags unusual label distribution; business metrics show anomalies; audit logs show unauthorized S3 access.

---

### Scenario 2: Credential Theft from Pipeline Logs
**Attacker Goal:** Steal AWS credentials to access data or exfiltrate models.

**Attack Path:**
1. Attacker gains read access to Kubeflow pipeline logs (e.g., public dashboard misconfiguration)
2. Developer accidentally logged AWS_SECRET_ACCESS_KEY in debug output
3. Attacker extracts credential and authenticates to AWS
4. Downloads all model artifacts from S3, accesses training data

**Mitigations:**
- [ ] Secret scanning in CI (detect-secrets, TruffleHog)
- [ ] Logs filtered for sensitive patterns before storage (Fluent Bit processor)
- [ ] Short-lived credentials via IRSA/Workload Identity (no long-term keys in pods)
- [ ] RBAC on pipeline logs; authenticated access only
- [ ] Cloud trail alerts for unusual S3 access patterns

**Detection:** CloudTrail shows API calls from unknown IP; secret scanning tool alerts on commit; log anomaly detection flags secret-like patterns.

---

### Scenario 3: Model Serving API Abuse
**Attacker Goal:** Perform model extraction by querying inference API repeatedly with crafted inputs.

**Attack Path:**
1. Attacker reverse-engineers API schema (publicly documented or via trial-and-error)
2. Sends thousands of queries with varied inputs to map decision boundaries
3. Trains a surrogate model replicating original model behavior
4. Deploys competing product using stolen model logic

**Mitigations:**
- [ ] Rate limiting per API key (e.g., 100 requests/minute)
- [ ] Anomaly detection for query patterns (high frequency, systematic exploration)
- [ ] Output rounding/noise injection to reduce information leakage (for sensitive models)
- [ ] Watermarking model to detect theft if surrogate appears
- [ ] Legal protections (terms of service, DMCA)

**Detection:** Rate limiter triggers; security team reviews query logs; business intelligence detects competitor using similar predictions.

---

## Residual Risk Summary
- **High:** Insider threat with data source access (requires trust + monitoring)
- **Medium:** Supply chain vulnerabilities in ML libraries (PyTorch, TensorFlow) - mitigated by patching cadence
- **Medium:** Model extraction via API (difficult to prevent without degrading usability)
- **Low:** External attack on infrastructure (strong controls in place)

## Monitoring & Response
- **SIEM Integration:** Forward audit logs to SIEM (Splunk/ELK) with ML-specific use cases
- **Anomaly Detection:** Behavioral analytics on API usage, data access patterns, deployment frequency
- **Incident Response:** Playbook for model compromise (rollback, forensics, notification)
- **Threat Intelligence:** Subscribe to ML security feeds (e.g., adversarial ML papers, CVEs)

## Review Cadence
- Quarterly threat model review with security team
- Update after major architecture changes (new component, cloud migration)
- Incorporate lessons learned from incidents or near-misses
