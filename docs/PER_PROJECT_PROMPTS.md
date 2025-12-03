# Per-Project "What's Missing" Prompts

This guide distills the missing components for each portfolio project into ready-to-run prompts. Pair these with the observability, runbook, testing, and diagram packs (4.1–4.4) when filling gaps.

## P01 — AWS Infra (Terraform + Scripts)
- Fill `projects/P01-aws-infra/infra` with Terraform modules: VPC, security, compute, ALB, RDS.
- Add `environments/{dev,staging,prod}.tfvars`.
- Provide `scripts/{validate,plan,apply,destroy}.sh`.
- Output plan for `dev`. Ensure tags, KMS, least-privilege security groups.
- Add tests, runbooks, diagrams, and observability using packs 4.1/4.2/4.3/4.4.

## P02 — DB Migration (Dual-Write + Validator)
- Implement a proxy (Node or Python) that writes to MySQL and Postgres with idempotency and retry.
- Add `validator.py` to checksum/row-count tables and diff mismatches.
- Create `rollback.sh` to flip read/write back.
- Provide `docker-compose` for local dry-run with synthetic data.

## P03 — K8s CI/CD (Pipeline + Helm/Argo + Canary)
- Generate `.github/workflows/pipeline.yml` with jobs: lint, unit, integration (with Postgres/Redis services), SAST, build, Trivy, SBOM, push, Helm upgrade to kind/EKS, smoke test, and automated rollback on failing health gates.
- Include Helm chart and Istio VirtualService for 10%→100% rollout.

## P04 — DevSecOps (Scanners + Policy + Reports)
- Add scanners and policy coverage using pack 4.4.
- Include an intentionally vulnerable sample microservice to produce findings, and a `fix-findings.md` that references the SARIF.

## P05 — Multi-Cloud Mesh (Cluster IaC + Istio Multi-Cluster)
- Terraform EKS + AKS + GKE (small nodes); install Istio multi-cluster (east/west gateways).
- Add sample services, cross-cluster service export/import, scripted failover test (kill in cloud A; assert success in B).
- Output kubeconfigs and `mesh-link.sh`.

## P06 — Streaming (Docker Infra + Producers + Flink)
- Compose Kafka + registry; `producer.py` and `consumer.py`.
- Add Flink job with tumbling windows and exactly-once to Postgres; load generator; e2e test asserting counts and late-event handling.

## P07 — MLOps (Kubeflow + MLflow + Canary)
- Define Kubeflow pipeline (Py DSL) and integrate MLflow for tracking and registry.
- Deploy best model behind FastAPI; add shadow/canary route; drift check job.
- Add tests for feature code and basic accuracy threshold.

## P08 — Serverless ETL (Lambda + IaC + DLQ)
- Lambda (Python) for S3 put → transform → DynamoDB; IaC SAM; retries, DLQ, alarms.
- Add local tests with mocked events and a cost model in README.

## P09 — RAG Chatbot (Ingestion + Eval)
- FastAPI + FAISS; ingest docs directory; embed with open model; retrieve-then-read with citations and streaming.
- Include eval harness (exact/semantic), tests, and a small web UI.

## P10 — Data Lake (Spark/Glue + Iceberg)
- Spark job to ingest CSV→Parquet; register Iceberg tables; partition and evolve schema.
- Add Trino/Athena queries; tests verifying row counts and schema evolution.

## P11 — Zero-Trust (SPIRE/Envoy)
- SPIRE server/agents issuing SVIDs; Envoy sidecars enforce mTLS + RBAC.
- Demo app with allowed/denied call; scripts to show 403 vs 200.

## P12 — Smart Contracts (Hardhat + Tests + Deploy)
- Hardhat scaffold, Solidity ERC-20 or crowdfunding contract, unit tests, coverage, deploy to testnet, minimal web client, threat model, and gas report.

## P13 — PQC (Kyber Demo)
- Python demo using liboqs with keygen/encap/decap; encrypt secret; perf timings; CLI with subcommands; README with hybrid TLS migration guidance.

## P14 — SIEM/SOAR (Ingestion + Detections + Playbook)
- ELK or Loki+Grafana stack; log pipelines; rules for failed logins/beaconing.
- SOAR Python to disable user or quarantine pod; synthetic attack dataset; dashboards and screenshots.

## P15 — IAM/SSO (IdP + Client + RBAC)
- Keycloak docker; realm + OIDC client; sample app with login; roles/claims to RBAC routes.
- Test script to fetch token and verify permissions.

## P16 — IoT Platform (Broker + Sims + Timescale)
- Mosquitto broker; Python device sims; subscriber writes to TimescaleDB; retention policy; dashboards; offline buffer/reconnect logic; tests.

## P17 — Quantum (Qiskit Notebooks)
- Notebooks for Bell state and small Grover; circuit diagrams; histograms; markdown explanations; export images for README.

## P18 — Edge AI (TFLite + Perf Logs)
- Convert MobileNet to TFLite; inference script; quantized variants; FPS/latency logs; device notes; tests comparing output deltas.

## P19 — AR/VR (WebXR App)
- Minimal WebXR + Three.js; interactive 3D object; tap-to-rotate; deployable static site; screenshots and short demo GIF.

## P20 — 5G Slicing (Lab + Metrics)
- Dockerized Open5GS lab; two slices (eMBB/URLLC) with config diffs; traffic generator; measurements; lab guide and diagrams.

## P21 — Multi-Region DR (IaC + Drill)
- Terraform two regions; Route53 health check + failover; cross-region DB replication; DR drill script; RTO/RPO report with evidence logs.

## P22 — Collaboration (Server + Client + CRDT)
- Node WebSocket server + Yjs client; offline reconciliation; load test; latency budget; sequence diagram; conflict-resolution tests.

## P23 — GPU Compute (CUDA + Timing Harness)
- C++ CPU vs CUDA matrix multiply; NVCC build; timing harness; correctness check; speedup chart; tuning notes.

## P24 — Autonomous DevOps (Agent + Guardrails)
- Agent polling Prometheus; forecasts load; scales k8s deployments; policy guardrails + manual override; training loop; MVP with synthetic data; tests.

## P25 — Observability (Full Stack + Rules)
- Prometheus scrape config; OpenTelemetry SDK in demo service; Jaeger; Grafana dashboard JSON; alert rules; tests that hit endpoints and assert metrics exported.

---

## One-Shot Generators (Run Once; Reuse Everywhere)
- **Boilerplate generator:** Create `/tools/new_project.py` that, given `<PXX> <title>`, scaffolds folders, README/ADR/RUNBOOK from templates, Makefile, CI stub, pre-commit, and a hello-world app/service. Include unit test and a `make up` local run path.
- **Evidence capturer:** Create `/tools/evidence.sh` to run a command, tee logs to `/projects/<PXX>/evidence/*.log`, capture a screenshot or curl output, and append to `/projects/<PXX>/docs/EVIDENCE.md` with timestamps.
- **Release checklist:** Emit `/RELEASE_CHECKLIST.md` and `/scripts/release-verify.sh` that (1) checks tests, (2) verifies image/tag exists, (3) lints IaC, (4) validates alert rules JSON/YAML, (5) renders Mermaid diagrams headless, (6) prints rollback steps.
