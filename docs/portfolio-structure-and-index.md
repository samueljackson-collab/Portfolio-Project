# Portfolio Repo Structure and 25-Project Index

Use this scaffold for every project to keep documentation, code, and operations consistent.

## Repository scaffold
```
/projects/PXX-<slug>/{src,infra,helm,tests,docs,runbooks,scripts}
/common/{ci,observability,security,templates}
.github/workflows/portfolio-ci.yml
```

Recommended contents:
- `/common/observability`: Prometheus, Grafana, Jaeger docker-compose and OpenTelemetry snippets.
- `/common/security`: pre-commit, gitleaks, semgrep rules, and Trivy usage notes.
- `/common/templates`: README, ADR, runbook, and diagram templates.
- `/common/ci`: reusable workflow job fragments for lint, test, scan, package, and deploy.

## 25-project index (keep synchronized)
| ID | Project | Scope |
| --- | --- | --- |
| P01 | AWS CloudFormation VPC baseline | VPC + IAM foundation |
| P02 | Database migration factory | Dry-run + reporting |
| P03 | CI/CD with ArgoCD & canary | GitOps progressive delivery |
| P04 | DevSecOps guardrails | SAST/DAST, secrets, supply chain |
| P05 | Service mesh rollout | mTLS, traffic policy |
| P06 | Streaming data platform | Kafka + consumers |
| P07 | AI/ML automation | Pipelines and feature stores |
| P08 | Serverless apps | Event-driven patterns |
| P09 | RAG chatbot | Retrieval augmented QA |
| P10 | Data lake (Iceberg) | Ingest + analytics |
| P11 | Zero trust identity | IAM and policy |
| P12 | Smart contracts | Solidity + auditing |
| P13 | Post-quantum crypto | PQC readiness |
| P14 | SIEM/SOAR | Detection engineering |
| P15 | IAM hardening | Least privilege |
| P16 | IoT pipeline | Device to cloud |
| P17 | Quantum experiments | Simulators |
| P18 | Edge AI | On-device inference |
| P19 | AR/VR demo | Experience prototype |
| P20 | 5G slice lab | Latency profiles |
| P21 | Disaster recovery | Playbooks and tests |
| P22 | CRDT collaboration | Yjs/WebSocket demo |
| P23 | GPU/CUDA workloads | Accelerated compute |
| P24 | Analytics/reporting | Automated reporting |
| P25 | Observability baseline | Prometheus/Grafana/Jaeger |

Document the “Definition of Ready” for each project in `/projects/PXX-*/.project.json` including region, secrets approach, environments, demo scope, and success KPI.
