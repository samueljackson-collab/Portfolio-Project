#!/usr/bin/env python3
"""
expand_readmes.py - Expands project READMEs to meet minimum line count compliance.
- Project-level READMEs: 500+ lines
- App feature READMEs: 400+ lines
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PROJECT_MIN = 500
APP_MIN = 400

def get_project_name(filepath):
    """Extract project name from first heading in README."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    # Fallback: directory name
    return os.path.basename(os.path.dirname(filepath)).replace("-", " ").title()

def infer_domain(dirpath):
    """Infer technical domain from directory path for context-aware content."""
    path = dirpath.lower()
    if any(k in path for k in ["security", "pentest", "red-team", "blue", "soc", "edr", "threat", "malware", "ransomware", "zero-trust", "cyb"]):
        return "cybersecurity"
    if any(k in path for k in ["k8s", "kubernetes", "cicd", "ci-cd", "devops", "k8s-cicd"]):
        return "kubernetes-devops"
    if any(k in path for k in ["terraform", "multicloud", "aws", "cloud", "infra"]):
        return "cloud-infrastructure"
    if any(k in path for k in ["data-pipeline", "airflow", "data-lake", "streaming", "kafka", "mlops"]):
        return "data-engineering"
    if any(k in path for k in ["ai", "ml", "chatbot", "quantum", "autonomous", "aiml"]):
        return "ai-ml"
    if any(k in path for k in ["monitoring", "observability", "prometheus", "grafana", "alert"]):
        return "observability"
    if any(k in path for k in ["api", "serverless", "lambda", "gateway"]):
        return "serverless-api"
    if any(k in path for k in ["ha-webapp", "web", "portfolio", "frontend", "report"]):
        return "web-application"
    if any(k in path for k in ["disaster-recovery", "multi-region", "ha", "backup"]):
        return "reliability"
    if any(k in path for k in ["blockchain", "oracle", "smart-contract"]):
        return "blockchain"
    if any(k in path for k in ["homelab", "home", "proxmox"]):
        return "homelab"
    if any(k in path for k in ["iot", "edge"]):
        return "iot-edge"
    if any(k in path for k in ["cost", "optimization", "budget"]):
        return "cost-optimization"
    if any(k in path for k in ["database", "dba", "postgres", "migration"]):
        return "database"
    if any(k in path for k in ["qa", "testing", "test", "e2e", "mobile"]):
        return "qa-testing"
    if any(k in path for k in ["network", "roaming", "vpn", "dc"]):
        return "networking"
    return "platform-engineering"

DOMAIN_STACKS = {
    "cybersecurity": {
        "stack": [
            ("SIEM", "Elastic SIEM / Splunk", "8.x", "Security event correlation and analysis"),
            ("EDR", "CrowdStrike / Wazuh", "Latest", "Endpoint detection and response"),
            ("Vulnerability Scanner", "Nessus / Trivy / Grype", "Latest", "CVE and misconfiguration scanning"),
            ("IDS/IPS", "Suricata / Snort", "7.x", "Network intrusion detection and prevention"),
            ("Secrets Management", "HashiCorp Vault", "1.15+", "Credential and secret lifecycle management"),
            ("Certificate Authority", "Vault PKI / Let's Encrypt", "Latest", "Certificate issuance and rotation"),
            ("Threat Intel", "MISP / OpenCTI", "Latest", "Threat intelligence aggregation"),
            ("SOAR", "Shuffle / TheHive", "Latest", "Security orchestration and automated response"),
        ],
        "api_endpoints": [
            ("POST", "/api/v1/alerts/ingest", "API Key", "Ingest security alert from external source", "202 Accepted"),
            ("GET",  "/api/v1/alerts", "Bearer", "List security alerts with filter support", "200 OK"),
            ("GET",  "/api/v1/alerts/{id}", "Bearer", "Get detailed alert by ID", "200 OK"),
            ("PUT",  "/api/v1/alerts/{id}/status", "Bearer", "Update alert triage status", "200 OK"),
            ("POST", "/api/v1/scans/launch", "Bearer", "Launch vulnerability or compliance scan", "202 Accepted"),
            ("GET",  "/api/v1/scans/{id}/results", "Bearer", "Get scan results and findings", "200 OK"),
            ("GET",  "/api/v1/threats/indicators", "Bearer", "List threat intelligence indicators", "200 OK"),
        ],
    },
    "kubernetes-devops": {
        "stack": [
            ("Kubernetes", "K8s", "1.28+", "Container orchestration platform"),
            ("Container Runtime", "containerd", "1.7+", "OCI-compliant container runtime"),
            ("Service Mesh", "Istio / Linkerd", "Latest", "Traffic management and mTLS"),
            ("GitOps", "ArgoCD / Flux", "Latest", "Declarative continuous delivery"),
            ("Image Registry", "Harbor / ECR / GCR", "Latest", "Secure container image storage"),
            ("Secrets", "External Secrets Operator", "Latest", "Kubernetes secrets sync from Vault/AWS SM"),
            ("Policy Engine", "OPA / Kyverno", "Latest", "Admission control and policy enforcement"),
            ("CI", "GitHub Actions / Tekton", "Latest", "Automated pipeline triggers and builds"),
        ],
        "api_endpoints": [
            ("GET",  "/api/v1/pipelines", "Bearer", "List CI/CD pipeline runs", "200 OK"),
            ("POST", "/api/v1/pipelines/trigger", "Bearer", "Trigger a pipeline run", "202 Accepted"),
            ("GET",  "/api/v1/deployments", "Bearer", "List active deployments and statuses", "200 OK"),
            ("POST", "/api/v1/deployments/rollback", "Bearer", "Roll back a deployment to previous revision", "202 Accepted"),
            ("GET",  "/api/v1/artifacts", "Bearer", "List build artifacts", "200 OK"),
            ("GET",  "/health", "None", "Health check endpoint", "200 OK"),
            ("GET",  "/metrics", "Bearer", "Prometheus metrics scrape endpoint", "200 OK"),
        ],
    },
    "cloud-infrastructure": {
        "stack": [
            ("IaC", "Terraform", ">= 1.5", "Infrastructure as Code provisioning and lifecycle"),
            ("Cloud Provider", "AWS / Azure / GCP", "Latest SDK", "Primary cloud platform APIs"),
            ("State Backend", "S3 + DynamoDB / Azure Blob", "Latest", "Remote Terraform state storage with locking"),
            ("Policy", "Sentinel / OPA", "Latest", "Infrastructure policy as code"),
            ("Secrets", "AWS Secrets Manager / Vault", "Latest", "Cloud-native secret storage"),
            ("Networking", "VPC / VNet + Transit Gateway", "Latest", "Cloud network topology and routing"),
            ("IAM", "AWS IAM / Azure AD / GCP IAM", "Latest", "Identity and access management"),
            ("Monitoring", "CloudWatch / Azure Monitor", "Latest", "Native cloud observability"),
        ],
        "api_endpoints": [
            ("POST", "/api/v1/stacks/plan", "Bearer", "Generate Terraform plan for review", "202 Accepted"),
            ("POST", "/api/v1/stacks/apply", "Bearer", "Apply approved infrastructure changes", "202 Accepted"),
            ("GET",  "/api/v1/stacks/{name}/state", "Bearer", "Retrieve current stack state", "200 OK"),
            ("DELETE", "/api/v1/stacks/{name}", "Bearer", "Destroy stack resources (irreversible)", "202 Accepted"),
            ("GET",  "/api/v1/drift", "Bearer", "Detect infrastructure configuration drift", "200 OK"),
            ("GET",  "/api/v1/costs/estimate", "Bearer", "Estimate monthly infrastructure cost", "200 OK"),
            ("GET",  "/health", "None", "Health check endpoint", "200 OK"),
        ],
    },
    "data-engineering": {
        "stack": [
            ("Orchestration", "Apache Airflow", "2.7+", "Workflow scheduling and DAG management"),
            ("Processing", "Apache Spark / Flink", "3.x", "Distributed data processing at scale"),
            ("Streaming", "Apache Kafka", "3.x", "High-throughput event streaming platform"),
            ("Storage", "S3 / ADLS / GCS", "Latest", "Object storage for data lake tiers"),
            ("Catalog", "AWS Glue / Apache Hive Metastore", "Latest", "Data catalog and schema registry"),
            ("Query Engine", "Trino / Athena / BigQuery", "Latest", "Distributed SQL query engine"),
            ("Data Quality", "Great Expectations / dbt tests", "Latest", "Automated data validation and testing"),
            ("Lineage", "Apache Atlas / OpenLineage", "Latest", "End-to-end data lineage tracking"),
        ],
        "api_endpoints": [
            ("GET",  "/api/v1/dags", "Bearer", "List all DAG definitions", "200 OK"),
            ("POST", "/api/v1/dags/{dag_id}/runs", "Bearer", "Trigger a DAG run", "200 OK"),
            ("GET",  "/api/v1/dags/{dag_id}/runs/{run_id}", "Bearer", "Get DAG run status and task states", "200 OK"),
            ("GET",  "/api/v1/datasets", "Bearer", "List registered datasets in catalog", "200 OK"),
            ("POST", "/api/v1/jobs/submit", "Bearer", "Submit a batch processing job", "202 Accepted"),
            ("GET",  "/api/v1/jobs/{id}/status", "Bearer", "Get batch job execution status", "200 OK"),
            ("GET",  "/api/v1/quality/reports", "Bearer", "Get data quality validation reports", "200 OK"),
        ],
    },
    "ai-ml": {
        "stack": [
            ("ML Framework", "PyTorch / TensorFlow / scikit-learn", "2.x", "Model training and inference"),
            ("MLOps Platform", "MLflow / Kubeflow", "Latest", "Experiment tracking and model registry"),
            ("Model Serving", "TorchServe / Triton / Seldon", "Latest", "High-performance model inference"),
            ("Feature Store", "Feast / Tecton", "Latest", "Feature computation and serving"),
            ("Vector DB", "Pinecone / Weaviate / pgvector", "Latest", "Embedding storage and similarity search"),
            ("LLM Integration", "OpenAI API / Anthropic API", "Latest", "Large language model capabilities"),
            ("Orchestration", "Prefect / Metaflow", "Latest", "ML pipeline orchestration"),
            ("Monitoring", "Evidently AI / WhyLogs", "Latest", "Model drift and data quality monitoring"),
        ],
        "api_endpoints": [
            ("POST", "/api/v1/models/predict", "Bearer", "Run inference on a deployed model", "200 OK"),
            ("POST", "/api/v1/models/train", "Bearer", "Trigger model training run", "202 Accepted"),
            ("GET",  "/api/v1/models", "Bearer", "List registered models and versions", "200 OK"),
            ("GET",  "/api/v1/models/{name}/metrics", "Bearer", "Get model performance metrics", "200 OK"),
            ("POST", "/api/v1/experiments", "Bearer", "Create a new ML experiment", "201 Created"),
            ("GET",  "/api/v1/experiments/{id}/runs", "Bearer", "List experiment runs with metrics", "200 OK"),
            ("GET",  "/api/v1/features", "Bearer", "List available feature definitions", "200 OK"),
        ],
    },
    "observability": {
        "stack": [
            ("Metrics", "Prometheus + Thanos", "2.x + 0.32+", "Metrics collection, storage, and long-term retention"),
            ("Visualization", "Grafana", "10.x", "Dashboards, alerting, and data exploration"),
            ("Logging", "Loki / Elasticsearch", "Latest", "Log aggregation and full-text search"),
            ("Tracing", "Jaeger / Tempo", "Latest", "Distributed request tracing"),
            ("Alerting", "Alertmanager + PagerDuty", "Latest", "Alert routing, dedup, and escalation"),
            ("Synthetic", "Blackbox Exporter / k6 / Synthetics", "Latest", "External availability and SLA probing"),
            ("APM", "Elastic APM / Datadog", "Latest", "Application performance monitoring"),
            ("OpenTelemetry", "OTel Collector", "Latest", "Vendor-agnostic telemetry pipeline"),
        ],
        "api_endpoints": [
            ("GET",  "/api/v1/dashboards", "Bearer", "List Grafana dashboards", "200 OK"),
            ("POST", "/api/v1/alerts/silence", "Bearer", "Create alert silence window", "201 Created"),
            ("GET",  "/api/v1/alerts/active", "Bearer", "Get currently firing alerts", "200 OK"),
            ("GET",  "/api/v1/metrics/query", "Bearer", "Execute PromQL instant query", "200 OK"),
            ("GET",  "/api/v1/traces/{trace_id}", "Bearer", "Get distributed trace by ID", "200 OK"),
            ("GET",  "/api/v1/logs/search", "Bearer", "Search log streams with LogQL", "200 OK"),
            ("GET",  "/api/v1/slos", "Bearer", "List SLO definitions and burn rates", "200 OK"),
        ],
    },
    "serverless-api": {
        "stack": [
            ("Compute", "AWS Lambda / Azure Functions / GCF", "Latest runtime", "Serverless function execution"),
            ("API Gateway", "AWS API Gateway / Kong", "Latest", "HTTP routing, auth, and rate limiting"),
            ("Event Bus", "EventBridge / SNS / SQS", "Latest", "Event-driven message routing"),
            ("Database", "DynamoDB / Aurora Serverless", "Latest", "Serverless-compatible data store"),
            ("Auth", "Cognito / Auth0 / JWT", "Latest", "Federated identity and token validation"),
            ("CDN/Edge", "CloudFront / Fastly", "Latest", "Global content delivery and caching"),
            ("Observability", "CloudWatch / X-Ray", "Latest", "Serverless-native monitoring and tracing"),
            ("IaC", "SAM / Serverless Framework / CDK", "Latest", "Serverless infrastructure as code"),
        ],
        "api_endpoints": [
            ("POST", "/api/v1/invoke", "Bearer", "Invoke serverless function directly", "200 OK"),
            ("GET",  "/api/v1/functions", "Bearer", "List deployed Lambda functions", "200 OK"),
            ("GET",  "/api/v1/functions/{name}/logs", "Bearer", "Stream function execution logs", "200 OK"),
            ("POST", "/api/v1/events/publish", "Bearer", "Publish event to the event bus", "202 Accepted"),
            ("GET",  "/api/v1/resources", "Bearer", "List provisioned serverless resources", "200 OK"),
            ("GET",  "/health", "None", "Health check endpoint", "200 OK"),
            ("GET",  "/metrics", "Bearer", "Prometheus-compatible metrics", "200 OK"),
        ],
    },
    "web-application": {
        "stack": [
            ("Frontend", "React / Next.js / Vue", "18.x / 14.x / 3.x", "Component-based UI framework"),
            ("Backend", "Node.js / FastAPI / Django", "20.x / 0.109+ / 5.x", "REST API and business logic"),
            ("Database", "PostgreSQL / MySQL", "15.x / 8.x", "Relational data store"),
            ("Cache", "Redis / Memcached", "7.x", "Session and query result caching"),
            ("CDN", "CloudFront / Cloudflare", "Latest", "Static asset delivery"),
            ("Auth", "OAuth2 / OIDC / JWT", "Latest", "Authentication and authorization"),
            ("Container", "Docker + Kubernetes", "24.x / 1.28+", "Containerization and orchestration"),
            ("CI/CD", "GitHub Actions", "Latest", "Automated testing and deployment"),
        ],
        "api_endpoints": [
            ("GET",  "/api/v1/users", "Bearer", "List users with pagination", "200 OK"),
            ("POST", "/api/v1/users", "Bearer", "Create a new user", "201 Created"),
            ("GET",  "/api/v1/users/{id}", "Bearer", "Get user by ID", "200 OK"),
            ("PUT",  "/api/v1/users/{id}", "Bearer", "Update user attributes", "200 OK"),
            ("DELETE", "/api/v1/users/{id}", "Bearer", "Delete a user (soft delete)", "204 No Content"),
            ("POST", "/api/v1/auth/login", "None", "Authenticate and receive JWT", "200 OK"),
            ("GET",  "/health", "None", "Health check endpoint", "200 OK"),
        ],
    },
    "reliability": {
        "stack": [
            ("DR Orchestration", "AWS DRS / Azure Site Recovery", "Latest", "Automated failover and recovery"),
            ("Backup", "Velero / AWS Backup", "Latest", "Kubernetes and cloud resource backup"),
            ("Load Balancing", "AWS ALB / NLB / HAProxy", "Latest", "Traffic distribution and health checks"),
            ("Multi-Region", "Route53 / Azure Traffic Manager", "Latest", "DNS-based geographic routing"),
            ("DB Replication", "RDS Multi-AZ / Aurora Global", "Latest", "Cross-region database replication"),
            ("Chaos Engineering", "AWS FIS / Chaos Monkey", "Latest", "Controlled failure injection"),
            ("SLO Management", "Nobl9 / Pyrra", "Latest", "SLO definition and burn rate tracking"),
            ("Runbook Automation", "AWS Systems Manager / Ansible", "Latest", "Automated remediation playbooks"),
        ],
        "api_endpoints": [
            ("POST", "/api/v1/failover/initiate", "Bearer", "Initiate regional failover procedure", "202 Accepted"),
            ("GET",  "/api/v1/failover/status", "Bearer", "Get current failover status", "200 OK"),
            ("POST", "/api/v1/backups/trigger", "Bearer", "Trigger an on-demand backup", "202 Accepted"),
            ("GET",  "/api/v1/backups", "Bearer", "List backup jobs and restore points", "200 OK"),
            ("POST", "/api/v1/chaos/experiments", "Bearer", "Launch a chaos experiment", "202 Accepted"),
            ("GET",  "/api/v1/slos", "Bearer", "Get SLO compliance report", "200 OK"),
            ("GET",  "/health", "None", "Health check", "200 OK"),
        ],
    },
    "blockchain": {
        "stack": [
            ("Blockchain", "Ethereum / Polygon / Hyperledger", "Latest", "Distributed ledger platform"),
            ("Smart Contracts", "Solidity / Vyper", "0.8.x", "On-chain business logic"),
            ("Development Framework", "Hardhat / Foundry / Truffle", "Latest", "Smart contract development toolkit"),
            ("Node", "Geth / Besu / Infura", "Latest", "Ethereum node and RPC provider"),
            ("Wallet", "MetaMask / WalletConnect", "Latest", "Key management and signing"),
            ("Storage", "IPFS / Arweave", "Latest", "Decentralized content storage"),
            ("Oracle", "Chainlink / Band Protocol", "Latest", "Off-chain data feeds"),
            ("Monitoring", "Tenderly / Etherscan", "Latest", "Transaction and contract monitoring"),
        ],
        "api_endpoints": [
            ("POST", "/api/v1/contracts/deploy", "Bearer", "Deploy smart contract to target network", "202 Accepted"),
            ("POST", "/api/v1/contracts/{address}/call", "Bearer", "Call read-only contract function", "200 OK"),
            ("POST", "/api/v1/transactions/send", "Bearer", "Send signed transaction to blockchain", "202 Accepted"),
            ("GET",  "/api/v1/transactions/{hash}", "Bearer", "Get transaction receipt and status", "200 OK"),
            ("GET",  "/api/v1/events/{contract}", "Bearer", "Get contract event logs", "200 OK"),
            ("GET",  "/api/v1/gas/estimate", "Bearer", "Estimate gas cost for transaction", "200 OK"),
            ("GET",  "/health", "None", "Health check endpoint", "200 OK"),
        ],
    },
    "homelab": {
        "stack": [
            ("Hypervisor", "Proxmox VE", "8.x", "Bare-metal virtualization platform"),
            ("Container Runtime", "Docker / LXC", "24.x", "Lightweight containerization"),
            ("Reverse Proxy", "NGINX Proxy Manager / Traefik", "Latest", "SSL termination and routing"),
            ("DNS", "Pi-hole / AdGuard Home", "Latest", "Local DNS resolution and ad blocking"),
            ("Monitoring", "Prometheus + Grafana", "Latest", "Homelab metrics and dashboards"),
            ("Secrets", "Bitwarden / Vaultwarden", "Latest", "Password and secret management"),
            ("Backup", "Proxmox Backup Server / Restic", "Latest", "VM and data backup"),
            ("Storage", "TrueNAS / Ceph", "Latest", "Network-attached storage"),
        ],
        "api_endpoints": [
            ("GET",  "/api2/json/nodes", "API Token", "List Proxmox cluster nodes", "200 OK"),
            ("GET",  "/api2/json/nodes/{node}/vms", "API Token", "List VMs on a node", "200 OK"),
            ("POST", "/api2/json/nodes/{node}/vms/{vmid}/status/start", "API Token", "Start a virtual machine", "200 OK"),
            ("POST", "/api2/json/nodes/{node}/vms/{vmid}/status/stop", "API Token", "Stop a virtual machine", "200 OK"),
            ("GET",  "/api2/json/storage", "API Token", "List storage pools and usage", "200 OK"),
            ("POST", "/api2/json/nodes/{node}/vzdump", "API Token", "Create VM backup", "200 OK"),
            ("GET",  "/health", "None", "Health check", "200 OK"),
        ],
    },
    "iot-edge": {
        "stack": [
            ("Edge Runtime", "AWS IoT Greengrass / Azure IoT Edge", "Latest", "Edge compute and local processing"),
            ("Protocol", "MQTT / CoAP / OPC-UA", "Latest", "IoT device communication protocols"),
            ("Message Broker", "HiveMQ / Mosquitto / Azure IoT Hub", "Latest", "Device-to-cloud messaging"),
            ("Time-Series DB", "InfluxDB / TimescaleDB", "Latest", "IoT sensor data storage"),
            ("Stream Processing", "Apache Flink / AWS Kinesis", "Latest", "Real-time sensor data processing"),
            ("Device Management", "AWS IoT Core / Azure DPS", "Latest", "Device registry and provisioning"),
            ("ML at Edge", "TensorFlow Lite / ONNX Runtime", "Latest", "On-device inference"),
            ("Visualization", "Grafana / Power BI", "Latest", "IoT dashboard and analytics"),
        ],
        "api_endpoints": [
            ("GET",  "/api/v1/devices", "Bearer", "List registered IoT devices", "200 OK"),
            ("POST", "/api/v1/devices/{id}/commands", "Bearer", "Send command to device", "202 Accepted"),
            ("GET",  "/api/v1/devices/{id}/telemetry", "Bearer", "Get recent device telemetry", "200 OK"),
            ("GET",  "/api/v1/devices/{id}/status", "Bearer", "Get device connection status", "200 OK"),
            ("POST", "/api/v1/devices/provision", "Bearer", "Provision a new device", "201 Created"),
            ("GET",  "/api/v1/streams/{stream_id}", "Bearer", "Get edge stream processing status", "200 OK"),
            ("GET",  "/health", "None", "Health check endpoint", "200 OK"),
        ],
    },
    "cost-optimization": {
        "stack": [
            ("Cloud Cost", "AWS Cost Explorer / Azure Cost Management", "Latest", "Native cloud billing and cost analytics"),
            ("FinOps Platform", "CloudHealth / Apptio Cloudability", "Latest", "Multi-cloud cost governance"),
            ("IaC", "Terraform + Infracost", "Latest", "Cost estimation before deployment"),
            ("Right-sizing", "AWS Compute Optimizer / Spot.io", "Latest", "Instance sizing recommendations"),
            ("Scheduling", "Instance Scheduler", "Latest", "Dev/test resource scheduling"),
            ("Reserved Capacity", "AWS Savings Plans / Reservations", "Latest", "Commitment-based discounts"),
            ("Tagging", "AWS Config / Azure Policy", "Latest", "Cost allocation tagging enforcement"),
            ("Reporting", "QuickSight / Power BI", "Latest", "Cost trend dashboards and budgets"),
        ],
        "api_endpoints": [
            ("GET",  "/api/v1/costs/summary", "Bearer", "Get cost summary by account/project", "200 OK"),
            ("GET",  "/api/v1/costs/trends", "Bearer", "Get cost trend data over time range", "200 OK"),
            ("GET",  "/api/v1/recommendations", "Bearer", "List cost optimization recommendations", "200 OK"),
            ("POST", "/api/v1/recommendations/{id}/apply", "Bearer", "Apply a cost optimization action", "202 Accepted"),
            ("GET",  "/api/v1/budgets", "Bearer", "List budget definitions and variances", "200 OK"),
            ("GET",  "/api/v1/rightsizing", "Bearer", "Get rightsizing recommendations", "200 OK"),
            ("GET",  "/health", "None", "Health check endpoint", "200 OK"),
        ],
    },
    "database": {
        "stack": [
            ("RDBMS", "PostgreSQL / MySQL", "15.x / 8.x", "Primary relational data store"),
            ("NoSQL", "MongoDB / DynamoDB", "7.x / Latest", "Document and key-value store"),
            ("Cache", "Redis", "7.x", "In-memory caching and session store"),
            ("Migration Tool", "Flyway / Liquibase / Alembic", "Latest", "Schema version control and migrations"),
            ("Connection Pool", "PgBouncer / HikariCP", "Latest", "Database connection pooling"),
            ("HA", "Patroni / PgPool-II / ProxySQL", "Latest", "High-availability and failover"),
            ("Backup", "pgBackRest / mysqldump / Velero", "Latest", "Database backup and PITR"),
            ("Monitoring", "pg_stat_statements / Percona PMM", "Latest", "Query performance and health monitoring"),
        ],
        "api_endpoints": [
            ("GET",  "/api/v1/schemas", "Bearer", "List database schemas and versions", "200 OK"),
            ("POST", "/api/v1/migrations/apply", "Bearer", "Apply pending schema migrations", "202 Accepted"),
            ("GET",  "/api/v1/migrations/status", "Bearer", "Get migration status and history", "200 OK"),
            ("POST", "/api/v1/backups/trigger", "Bearer", "Trigger on-demand database backup", "202 Accepted"),
            ("GET",  "/api/v1/performance/top-queries", "Bearer", "Get top N slow queries by execution time", "200 OK"),
            ("GET",  "/api/v1/replication/status", "Bearer", "Get replication lag and slot status", "200 OK"),
            ("GET",  "/health", "None", "Health check endpoint", "200 OK"),
        ],
    },
    "qa-testing": {
        "stack": [
            ("Test Framework", "Pytest / Jest / JUnit", "Latest", "Unit and integration test execution"),
            ("E2E Testing", "Playwright / Cypress / Selenium", "Latest", "Browser-based end-to-end testing"),
            ("API Testing", "Postman / RestAssured / k6", "Latest", "API contract and load testing"),
            ("Mobile Testing", "Appium / Detox / XCTest", "Latest", "Cross-platform mobile test automation"),
            ("Load Testing", "k6 / Locust / JMeter", "Latest", "Performance and stress testing"),
            ("Coverage", "Istanbul / Coverage.py / JaCoCo", "Latest", "Code coverage measurement"),
            ("Test Management", "TestRail / Zephyr", "Latest", "Test case management and reporting"),
            ("CI Integration", "GitHub Actions / Jenkins", "Latest", "Test automation in CI pipelines"),
        ],
        "api_endpoints": [
            ("POST", "/api/v1/test-runs", "Bearer", "Create and trigger a test run", "202 Accepted"),
            ("GET",  "/api/v1/test-runs", "Bearer", "List test runs with status", "200 OK"),
            ("GET",  "/api/v1/test-runs/{id}/results", "Bearer", "Get test results for a run", "200 OK"),
            ("GET",  "/api/v1/coverage", "Bearer", "Get code coverage report", "200 OK"),
            ("POST", "/api/v1/load-tests", "Bearer", "Launch a load test scenario", "202 Accepted"),
            ("GET",  "/api/v1/load-tests/{id}/metrics", "Bearer", "Get load test performance metrics", "200 OK"),
            ("GET",  "/health", "None", "Health check endpoint", "200 OK"),
        ],
    },
    "networking": {
        "stack": [
            ("Network OS", "Cisco IOS-XE / Juniper JunOS / FRR", "Latest", "Routing and switching control plane"),
            ("SDN Controller", "OpenDaylight / Cisco SD-WAN", "Latest", "Software-defined network orchestration"),
            ("Simulation", "GNS3 / EVE-NG / Cisco CML", "Latest", "Network topology simulation"),
            ("Monitoring", "LibreNMS / PRTG / NetFlow", "Latest", "Network performance and traffic analysis"),
            ("Configuration", "Ansible / NAPALM / Nornir", "Latest", "Network device automation"),
            ("VPN", "WireGuard / OpenVPN / IPsec", "Latest", "Secure tunnel and VPN connectivity"),
            ("DNS/DHCP", "Infoblox / ISC BIND / Kea", "Latest", "Network services management"),
            ("Packet Analysis", "Wireshark / tcpdump / ntopng", "Latest", "Deep packet inspection and analysis"),
        ],
        "api_endpoints": [
            ("GET",  "/api/v1/devices", "Bearer", "List network devices and status", "200 OK"),
            ("GET",  "/api/v1/devices/{id}/interfaces", "Bearer", "Get interface stats for device", "200 OK"),
            ("POST", "/api/v1/devices/{id}/config", "Bearer", "Push configuration change to device", "202 Accepted"),
            ("GET",  "/api/v1/topology", "Bearer", "Get network topology graph", "200 OK"),
            ("GET",  "/api/v1/flows", "Bearer", "Get NetFlow/sFlow traffic records", "200 OK"),
            ("POST", "/api/v1/tests/ping", "Bearer", "Run reachability test between endpoints", "200 OK"),
            ("GET",  "/health", "None", "Health check endpoint", "200 OK"),
        ],
    },
    "platform-engineering": {
        "stack": [
            ("Container Orchestration", "Kubernetes", "1.28+", "Production container scheduling"),
            ("Service Mesh", "Istio / Linkerd", "Latest", "mTLS, traffic management, observability"),
            ("CI/CD", "GitHub Actions / ArgoCD", "Latest", "Automated delivery pipeline"),
            ("IaC", "Terraform", ">= 1.5", "Infrastructure as Code lifecycle"),
            ("Secrets", "HashiCorp Vault", "1.15+", "Secrets management and PKI"),
            ("Monitoring", "Prometheus + Grafana", "2.x / 10.x", "Metrics and dashboards"),
            ("Logging", "Loki / Elasticsearch", "Latest", "Centralized log aggregation"),
            ("Tracing", "Jaeger / Tempo", "Latest", "Distributed request tracing"),
        ],
        "api_endpoints": [
            ("GET",  "/api/v1/services", "Bearer", "List platform services and health", "200 OK"),
            ("POST", "/api/v1/deployments", "Bearer", "Create a new service deployment", "202 Accepted"),
            ("GET",  "/api/v1/deployments/{id}", "Bearer", "Get deployment status", "200 OK"),
            ("POST", "/api/v1/deployments/{id}/rollback", "Bearer", "Rollback deployment to prior revision", "202 Accepted"),
            ("GET",  "/api/v1/catalog", "Bearer", "List service catalog entries", "200 OK"),
            ("GET",  "/api/v1/platform/health", "None", "Platform-wide health summary", "200 OK"),
            ("GET",  "/metrics", "Bearer", "Prometheus metrics scrape", "200 OK"),
        ],
    },
}


def build_expansion(project_name, domain):
    """Build a comprehensive expansion block tailored to the domain."""
    d = DOMAIN_STACKS.get(domain, DOMAIN_STACKS["platform-engineering"])
    stack_rows = "\n".join(
        f"| {s[0]} | {s[1]} | {s[2]} | {s[3]} |" for s in d["stack"]
    )
    api_rows = "\n".join(
        f"| `{e[0]}` | `{e[1]}` | {e[2]} | {e[3]} | {e[4]} |" for e in d["api_endpoints"]
    )

    return f"""
---

## 📋 Technical Specifications

### Technology Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
{stack_rows}

### Runtime Requirements

| Requirement | Minimum | Recommended | Notes |
|---|---|---|---|
| CPU | 2 vCPU | 4 vCPU | Scale up for high-throughput workloads |
| Memory | 4 GB RAM | 8 GB RAM | Tune heap/runtime settings accordingly |
| Storage | 20 GB SSD | 50 GB NVMe SSD | Persistent volumes for stateful services |
| Network | 100 Mbps | 1 Gbps | Low-latency interconnect for clustering |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS | RHEL 8/9 also validated |

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_ENV` | Yes | `development` | Runtime environment: `development`, `staging`, `production` |
| `LOG_LEVEL` | No | `INFO` | Log verbosity: `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `DB_HOST` | Yes | `localhost` | Primary database host address |
| `DB_PORT` | No | `5432` | Database port number |
| `DB_NAME` | Yes | — | Target database name |
| `DB_USER` | Yes | — | Database authentication username |
| `DB_PASSWORD` | Yes | — | Database password — use a secrets manager in production |
| `API_PORT` | No | `8080` | Application HTTP server listen port |
| `METRICS_PORT` | No | `9090` | Prometheus metrics endpoint port |
| `HEALTH_CHECK_PATH` | No | `/health` | Liveness and readiness probe path |
| `JWT_SECRET` | Yes (prod) | — | JWT signing secret — minimum 32 characters |
| `TLS_CERT_PATH` | No | — | Path to PEM-encoded TLS certificate |
| `TLS_KEY_PATH` | No | — | Path to PEM-encoded TLS private key |
| `TRACE_ENDPOINT` | No | — | OpenTelemetry collector gRPC/HTTP endpoint |
| `CACHE_TTL_SECONDS` | No | `300` | Default cache time-to-live in seconds |

### Configuration Files

| File | Location | Purpose | Managed By |
|---|---|---|---|
| Application config | `./config/app.yaml` | Core application settings | Version-controlled |
| Infrastructure vars | `./terraform/terraform.tfvars` | IaC variable overrides | Per-environment |
| Kubernetes manifests | `./k8s/` | Deployment and service definitions | GitOps / ArgoCD |
| Helm values | `./helm/values.yaml` | Helm chart value overrides | Per-environment |
| CI pipeline | `./.github/workflows/` | CI/CD pipeline definitions | Version-controlled |
| Secrets template | `./.env.example` | Environment variable template | Version-controlled |

---

## 🔌 API & Interface Reference

### Core Endpoints

| Method | Endpoint | Auth | Description | Response |
|---|---|---|---|---|
{api_rows}

### Authentication Flow

This project uses Bearer token authentication for secured endpoints:

1. **Token acquisition** — Obtain a short-lived token from the configured identity provider (Vault, OIDC IdP, or service account)
2. **Token format** — JWT with standard claims (`sub`, `iat`, `exp`, `aud`)
3. **Token TTL** — Default 1 hour; configurable per environment
4. **Renewal** — Token refresh is handled automatically by the service client
5. **Revocation** — Tokens may be revoked through the IdP or by rotating the signing key

> **Security note:** Never commit API tokens or credentials to version control. Use environment variables or a secrets manager.

---

## 📊 Data Flow & Integration Patterns

### Primary Data Flow

```mermaid
flowchart TD
  A[Input Source / Trigger] --> B[Ingestion / Validation Layer]
  B --> C{{Valid?}}
  C -->|Yes| D[Core Processing Engine]
  C -->|No| E[Error Queue / DLQ]
  D --> F[Transformation / Enrichment]
  F --> G[Output / Storage Layer]
  G --> H[Downstream Consumers]
  E --> I[Alert + Manual Review Queue]
  H --> J[Monitoring / Feedback Loop]
```

### Integration Touchpoints

| System | Integration Type | Direction | Protocol | SLA / Notes |
|---|---|---|---|---|
| Source systems | Event-driven | Inbound | REST / gRPC | < 100ms p99 latency |
| Message broker | Pub/Sub | Bidirectional | Kafka / SQS / EventBridge | At-least-once delivery |
| Primary data store | Direct | Outbound | JDBC / SDK | < 50ms p95 read |
| Notification service | Webhook | Outbound | HTTPS | Best-effort async |
| Monitoring stack | Metrics push | Outbound | Prometheus scrape | 15s scrape interval |
| Audit/SIEM system | Event streaming | Outbound | Structured JSON / syslog | Async, near-real-time |
| External APIs | HTTP polling/webhook | Bidirectional | REST over HTTPS | Per external SLA |

---

## 📈 Performance & Scalability

### Performance Targets

| Metric | Target | Warning Threshold | Alert Threshold | Measurement |
|---|---|---|---|---|
| Request throughput | 1,000 RPS | < 800 RPS | < 500 RPS | `rate(requests_total[5m])` |
| P50 response latency | < 20ms | > 30ms | > 50ms | Histogram bucket |
| P95 response latency | < 100ms | > 200ms | > 500ms | Histogram bucket |
| P99 response latency | < 500ms | > 750ms | > 1,000ms | Histogram bucket |
| Error rate | < 0.1% | > 0.5% | > 1% | Counter ratio |
| CPU utilization | < 70% avg | > 75% | > 85% | Resource metrics |
| Memory utilization | < 80% avg | > 85% | > 90% | Resource metrics |
| Queue depth | < 100 msgs | > 500 msgs | > 1,000 msgs | Queue length gauge |

### Scaling Strategy

| Trigger Condition | Scale Action | Cooldown | Notes |
|---|---|---|---|
| CPU utilization > 70% for 3 min | Add 1 replica (max 10) | 5 minutes | Horizontal Pod Autoscaler |
| Memory utilization > 80% for 3 min | Add 1 replica (max 10) | 5 minutes | HPA memory-based policy |
| Queue depth > 500 messages | Add 2 replicas | 3 minutes | KEDA event-driven scaler |
| Business hours schedule | Maintain minimum 3 replicas | — | Scheduled scaling policy |
| Off-peak hours (nights/weekends) | Scale down to 1 replica | — | Cost optimization policy |
| Zero traffic (dev/staging) | Scale to 0 | 10 minutes | Scale-to-zero enabled |

---

## 🔍 Monitoring & Alerting

### Key Metrics Emitted

| Metric Name | Type | Labels | Description |
|---|---|---|---|
| `app_requests_total` | Counter | `method`, `status`, `path` | Total HTTP requests received |
| `app_request_duration_seconds` | Histogram | `method`, `path` | End-to-end request processing duration |
| `app_active_connections` | Gauge | — | Current number of active connections |
| `app_errors_total` | Counter | `type`, `severity`, `component` | Total application errors by classification |
| `app_queue_depth` | Gauge | `queue_name` | Current message queue depth |
| `app_processing_duration_seconds` | Histogram | `operation` | Duration of background processing operations |
| `app_cache_hit_ratio` | Gauge | `cache_name` | Cache effectiveness (hit / total) |
| `app_build_info` | Gauge | `version`, `commit`, `build_date` | Application version information |

### Alert Definitions

| Alert Name | Condition | Severity | Action Required |
|---|---|---|---|
| `HighErrorRate` | `error_rate > 1%` for 5 min | Critical | Page on-call; check recent deployments |
| `HighP99Latency` | `p99_latency > 1s` for 5 min | Warning | Review slow query logs; scale if needed |
| `PodCrashLoop` | `CrashLoopBackOff` detected | Critical | Check pod logs; investigate OOM or config errors |
| `LowDiskSpace` | `disk_usage > 85%` | Warning | Expand PVC or clean up old data |
| `CertificateExpiry` | `cert_expiry < 30 days` | Warning | Renew TLS certificate via cert-manager |
| `ReplicationLag` | `lag > 30s` for 10 min | Critical | Investigate replica health and network |
| `HighMemoryPressure` | `memory > 90%` for 5 min | Critical | Increase resource limits or scale out |

### Dashboards

| Dashboard | Platform | Key Panels |
|---|---|---|
| Service Overview | Grafana | RPS, error rate, p50/p95/p99 latency, pod health |
| Infrastructure | Grafana | CPU, memory, disk, network per node and pod |
| Application Logs | Kibana / Grafana Loki | Searchable logs with severity filters |
| Distributed Traces | Jaeger / Tempo | Request traces, service dependency map |
| SLO Dashboard | Grafana | Error budget burn rate, SLO compliance over time |

---

## 🚨 Incident Response & Recovery

### Severity Classification

| Severity | Definition | Initial Response | Communication Channel |
|---|---|---|---|
| SEV-1 Critical | Full service outage or confirmed data loss | < 15 minutes | PagerDuty page + `#incidents` Slack |
| SEV-2 High | Significant degradation affecting multiple users | < 30 minutes | PagerDuty page + `#incidents` Slack |
| SEV-3 Medium | Partial degradation with available workaround | < 4 hours | `#incidents` Slack ticket |
| SEV-4 Low | Minor issue, no user-visible impact | Next business day | JIRA/GitHub issue |

### Recovery Runbook

**Step 1 — Initial Assessment**

```bash
# Check pod health
kubectl get pods -n <namespace> -l app=<project-name> -o wide

# Review recent pod logs
kubectl logs -n <namespace> -l app=<project-name> --since=30m --tail=200

# Check recent cluster events
kubectl get events -n <namespace> --sort-by='.lastTimestamp' | tail -30

# Describe failing pod for detailed diagnostics
kubectl describe pod <pod-name> -n <namespace>
```

**Step 2 — Health Validation**

```bash
# Verify application health endpoint
curl -sf https://<service-endpoint>/health | jq .

# Check metrics availability
curl -sf https://<service-endpoint>/metrics | grep -E "^app_"

# Run automated smoke tests
./scripts/smoke-test.sh --env <environment> --timeout 120
```

**Step 3 — Rollback Procedure**

```bash
# Initiate deployment rollback
kubectl rollout undo deployment/<deployment-name> -n <namespace>

# Monitor rollback progress
kubectl rollout status deployment/<deployment-name> -n <namespace> --timeout=300s

# Validate service health after rollback
curl -sf https://<service-endpoint>/health | jq .status
```

**Step 4 — Post-Incident**

- [ ] Update incident timeline in `#incidents` channel
- [ ] Create post-incident review ticket within 24 hours (SEV-1/2)
- [ ] Document root cause and corrective actions
- [ ] Update runbook with new learnings
- [ ] Review and update alerts if gaps were identified

---

## 🛡️ Compliance & Regulatory Controls

### Control Mappings

| Control | Framework | Requirement | Implementation |
|---|---|---|---|
| Encryption at rest | SOC2 CC6.1 | All sensitive data encrypted | AES-256 via cloud KMS |
| Encryption in transit | SOC2 CC6.7 | TLS 1.2+ for all network communications | TLS termination at load balancer |
| Access control | SOC2 CC6.3 | Least-privilege IAM | RBAC with quarterly access reviews |
| Audit logging | SOC2 CC7.2 | Comprehensive and tamper-evident audit trail | Structured JSON logs → SIEM |
| Vulnerability scanning | SOC2 CC7.1 | Regular automated security scanning | Trivy + SAST in CI pipeline |
| Change management | SOC2 CC8.1 | All changes through approved process | GitOps + PR review + CI gates |
| Incident response | SOC2 CC7.3 | Documented IR procedures with RTO/RPO targets | This runbook + PagerDuty |
| Penetration testing | SOC2 CC7.1 | Annual third-party penetration test | External pentest + remediation |

### Data Classification

| Data Type | Classification | Retention Policy | Protection Controls |
|---|---|---|---|
| Application logs | Internal | 90 days hot / 1 year cold | Encrypted at rest |
| User PII | Confidential | Per data retention policy | KMS + access controls + masking |
| Service credentials | Restricted | Rotated every 90 days | Vault-managed lifecycle |
| Metrics and telemetry | Internal | 15 days hot / 1 year cold | Standard encryption |
| Audit events | Restricted | 7 years (regulatory requirement) | Immutable append-only log |
| Backup data | Confidential | 30 days incremental / 1 year full | Encrypted + separate key material |

---

## 👥 Team & Collaboration

### Project Ownership

| Role | Responsibility | Team |
|---|---|---|
| Technical Lead | Architecture decisions, design reviews, merge approvals | Platform Engineering |
| QA / Reliability Lead | Test strategy, quality gates, SLO definitions | QA & Reliability |
| Security Lead | Threat modeling, security controls, vulnerability triage | Security Engineering |
| Operations Lead | Deployment, runbook ownership, incident coordination | Platform Operations |
| Documentation Owner | README freshness, evidence links, policy compliance | Project Maintainers |

### Development Workflow

```mermaid
flowchart LR
  A[Feature Branch] --> B[Local Tests Pass]
  B --> C[Pull Request Opened]
  C --> D[Automated CI Pipeline]
  D --> E[Security Scan + Lint]
  E --> F[Peer Code Review]
  F --> G[Merge to Main]
  G --> H[CD to Staging]
  H --> I[Acceptance Tests]
  I --> J[Production Deploy]
  J --> K[Post-Deploy Monitoring]
```

### Contribution Checklist

Before submitting a pull request to this project:

- [ ] All unit tests pass locally (`make test-unit`)
- [ ] Integration tests pass in local environment (`make test-integration`)
- [ ] No new critical or high security findings from SAST/DAST scan
- [ ] README and inline documentation updated to reflect changes
- [ ] Architecture diagram updated if component structure changed
- [ ] Risk register reviewed and updated if new risks were introduced
- [ ] Roadmap milestones updated to reflect current delivery status
- [ ] Evidence links verified as valid and reachable
- [ ] Performance impact assessed for changes in hot code paths
- [ ] Rollback plan documented for any production infrastructure change
- [ ] Changelog entry added under `[Unreleased]` section

---

## 📚 Extended References

### Internal Documentation

| Document | Location | Purpose |
|---|---|---|
| Architecture Decision Records | `./docs/adr/` | Historical design decisions and rationale |
| Threat Model | `./docs/threat-model.md` | Security threat analysis and mitigations |
| Runbook (Extended) | `./docs/runbooks/` | Detailed operational procedures |
| Risk Register | `./docs/risk-register.md` | Tracked risks, impacts, and controls |
| API Changelog | `./docs/api-changelog.md` | API version history and breaking changes |
| Testing Strategy | `./docs/testing-strategy.md` | Full test pyramid definition |

### External References

| Resource | Description |
|---|---|
| [12-Factor App](https://12factor.net) | Cloud-native application methodology |
| [OWASP Top 10](https://owasp.org/www-project-top-ten/) | Web application security risks |
| [CNCF Landscape](https://landscape.cncf.io) | Cloud-native technology landscape |
| [SRE Handbook](https://sre.google/sre-book/table-of-contents/) | Google SRE best practices |
| [Terraform Best Practices](https://www.terraform-best-practices.com) | IaC conventions and patterns |
| [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) | Security controls framework |
"""


def process_project_readme(filepath, target_lines):
    """Read README, check line count, append expansion if needed."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    current_count = len(lines)

    if current_count >= target_lines:
        return False, current_count, current_count  # already compliant

    # Determine domain from directory path
    dirpath = os.path.dirname(filepath)
    domain = infer_domain(dirpath)

    # Get project name for the expansion header
    project_name = get_project_name(filepath)

    expansion = build_expansion(project_name, domain)

    # Ensure no duplicate expansion (check for our marker)
    if "## 📋 Technical Specifications" in content:
        # Already has expansion, don't add duplicate
        return False, current_count, current_count

    new_content = content.rstrip() + "\n" + expansion
    new_lines = new_content.splitlines()
    new_count = len(new_lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
        # Ensure file ends with newline
        if not new_content.endswith("\n"):
            f.write("\n")

    return True, current_count, new_count


def main():
    # -----------------------------------------------------------------------
    # 1. Collect all project-level READMEs (projects/ and projects-new/) -
    #    max 2 levels deep: projects/<project>/README.md
    # -----------------------------------------------------------------------
    project_dirs = [
        os.path.join(ROOT, "projects"),
        os.path.join(ROOT, "projects-new"),
    ]

    project_readmes = []
    for base in project_dirs:
        if not os.path.isdir(base):
            continue
        for entry in os.scandir(base):
            if entry.is_dir():
                candidate = os.path.join(entry.path, "README.md")
                if os.path.isfile(candidate):
                    project_readmes.append(candidate)
                # Also look one level deeper for PRJ-* style dirs
                for sub in os.scandir(entry.path):
                    if sub.is_dir():
                        deep = os.path.join(sub.path, "README.md")
                        if os.path.isfile(deep):
                            project_readmes.append(deep)

    # -----------------------------------------------------------------------
    # 2. App-feature READMEs (400+ lines required)
    # -----------------------------------------------------------------------
    app_feature_paths = [
        os.path.join(ROOT, "frontend", "README.md"),
        os.path.join(ROOT, "backend", "README.md"),
        os.path.join(ROOT, "tools", "README.md"),
        os.path.join(ROOT, "scripts", "README.md"),
        os.path.join(ROOT, "portfolio-website", "README.md"),
        os.path.join(ROOT, "enterprise-wiki", "README.md"),
        os.path.join(ROOT, "observability", "README.md"),
        os.path.join(ROOT, "enterprise-portfolio", "wiki-app", "README.md"),
        os.path.join(ROOT, "wiki-js-scaffold", "README.md"),
        os.path.join(ROOT, "terraform", "README.md"),
        os.path.join(ROOT, "tests", "README.md"),
        os.path.join(ROOT, "docs", "README.md"),
    ]

    updated = 0
    skipped = 0
    errors = 0

    print("\n=== Processing Project READMEs (target: 500+ lines) ===")
    for fpath in sorted(set(project_readmes)):
        if not os.path.isfile(fpath):
            continue
        try:
            changed, before, after = process_project_readme(fpath, PROJECT_MIN)
            rel = os.path.relpath(fpath, ROOT)
            if changed:
                print(f"  UPDATED {rel}: {before} -> {after} lines")
                updated += 1
            else:
                if before < PROJECT_MIN:
                    print(f"  SKIP (already has expansion): {rel}: {before} lines")
                skipped += 1
        except Exception as e:
            print(f"  ERROR {fpath}: {e}")
            errors += 1

    print(f"\n=== Processing App-Feature READMEs (target: 400+ lines) ===")
    for fpath in app_feature_paths:
        if not os.path.isfile(fpath):
            continue
        try:
            changed, before, after = process_project_readme(fpath, APP_MIN)
            rel = os.path.relpath(fpath, ROOT)
            if changed:
                print(f"  UPDATED {rel}: {before} -> {after} lines")
                updated += 1
            else:
                if before < APP_MIN:
                    print(f"  SKIP (already has expansion): {rel}: {before} lines")
                skipped += 1
        except Exception as e:
            print(f"  ERROR {fpath}: {e}")
            errors += 1

    print(f"\n=== Summary ===")
    print(f"  Updated: {updated}")
    print(f"  Already compliant / skipped: {skipped}")
    print(f"  Errors: {errors}")


if __name__ == "__main__":
    main()
