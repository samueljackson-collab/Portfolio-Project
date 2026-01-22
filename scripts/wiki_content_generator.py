#!/usr/bin/env python3
"""
Enhanced Wiki.js Content Generator v2

Generates comprehensive wiki documentation for portfolio projects with:
- Wiki.js-compatible frontmatter and metadata
- Deep Dive educational modules with code examples
- Detailed problem statements with real-world context
- Best practices and anti-patterns
- Learning objectives and key takeaways
- Architecture component explanations
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from wiki_knowledge_base import TECHNOLOGY_DEEP_DIVES
from wiki_problem_templates import (
    PROBLEM_STATEMENTS,
    LEARNING_OBJECTIVES,
    ARCHITECTURE_COMPONENTS,
    REAL_WORLD_SCENARIOS
)


# =============================================================================
# PROJECT DATA
# =============================================================================

PROJECTS_DATA = [
    {"id": 1, "name": "AWS Infrastructure Automation", "slug": "aws-infrastructure-automation", "description": "Production-ready AWS environment using Terraform, CDK, and Pulumi. Features Multi-AZ VPC, EKS cluster, and RDS PostgreSQL.", "status": "Production Ready", "completion_percentage": 100, "tags": ["aws", "terraform", "infrastructure", "eks", "rds"], "github_path": "projects/1-aws-infrastructure-automation", "technologies": ["Terraform", "AWS CDK", "Pulumi", "Python", "Bash"], "features": ["Multi-AZ VPC architecture", "Managed EKS Cluster", "RDS PostgreSQL with backups", "Automated DR drills", "Cost estimation scripts"], "category": "infrastructure"},
    {"id": 2, "name": "Database Migration Platform", "slug": "database-migration-platform", "description": "Zero-downtime database migration orchestrator using Change Data Capture (CDC) with Debezium and AWS DMS.", "status": "Production Ready", "completion_percentage": 100, "tags": ["database", "migration", "aws-dms", "python", "kafka"], "github_path": "projects/2-database-migration", "technologies": ["Python", "Debezium", "Kafka", "PostgreSQL", "Docker"], "features": ["Zero-downtime cutover", "Data integrity validation", "Automated rollback", "Real-time replication monitoring"], "category": "migration"},
    {"id": 3, "name": "Kubernetes CI/CD Pipeline", "slug": "kubernetes-cicd", "description": "GitOps-driven continuous delivery pipeline combining GitHub Actions and ArgoCD for progressive deployment.", "status": "Production Ready", "completion_percentage": 100, "tags": ["kubernetes", "ci-cd", "argocd", "github-actions"], "github_path": "projects/3-kubernetes-cicd", "technologies": ["GitHub Actions", "ArgoCD", "Helm", "Kustomize", "Python"], "features": ["Blue-Green/Canary deployments", "Automated rollback on health failure", "Multi-environment support", "Container security scanning"], "category": "ci-cd"},
    {"id": 4, "name": "DevSecOps Pipeline", "slug": "devsecops-pipeline", "description": "Security-first CI pipeline integrating SAST, DAST, and container scanning.", "status": "In Development", "completion_percentage": 25, "tags": ["security", "devops", "ci-cd", "sast", "dast"], "github_path": "projects/4-devsecops", "technologies": ["GitHub Actions", "Trivy", "SonarQube", "OWASP ZAP"], "features": ["SBOM generation", "Automated vulnerability scanning", "Policy enforcement gates"], "category": "security"},
    {"id": 5, "name": "Real-time Data Streaming", "slug": "real-time-data-streaming", "description": "High-throughput event streaming pipeline using Apache Kafka and Flink with exactly-once semantics.", "status": "Production Ready", "completion_percentage": 100, "tags": ["kafka", "flink", "streaming", "python", "docker"], "github_path": "projects/5-real-time-data-streaming", "technologies": ["Apache Kafka", "Apache Flink", "Python", "Avro", "Docker"], "features": ["Exactly-once processing", "Schema Registry integration", "Flink SQL analytics", "RocksDB state backend"], "category": "streaming"},
    {"id": 6, "name": "MLOps Platform", "slug": "mlops-platform", "description": "End-to-end MLOps workflow for training, evaluating, and deploying models with drift detection.", "status": "Production Ready", "completion_percentage": 100, "tags": ["mlops", "machine-learning", "python", "mlflow", "kubernetes"], "github_path": "projects/6-mlops-platform", "technologies": ["MLflow", "Optuna", "FastAPI", "Scikit-learn", "Kubernetes"], "features": ["Automated training pipeline", "A/B testing framework", "Model drift detection", "Model serving API"], "category": "mlops"},
    {"id": 7, "name": "Serverless Data Processing", "slug": "serverless-data-processing", "description": "Event-driven analytics pipeline built on AWS serverless services (Lambda, Step Functions).", "status": "Production Ready", "completion_percentage": 100, "tags": ["serverless", "aws-lambda", "data-engineering", "step-functions"], "github_path": "projects/7-serverless-data-processing", "technologies": ["AWS SAM", "Lambda", "Step Functions", "DynamoDB", "Python"], "features": ["Workflow orchestration", "API Gateway integration", "Cognito authentication", "Automated error handling"], "category": "serverless"},
    {"id": 8, "name": "Advanced AI Chatbot", "slug": "advanced-ai-chatbot", "description": "RAG chatbot indexing portfolio assets with tool-augmented workflows.", "status": "Substantial", "completion_percentage": 55, "tags": ["ai", "chatbot", "llm", "rag", "fastapi"], "github_path": "projects/8-advanced-ai-chatbot", "technologies": ["Python", "FastAPI", "LangChain", "Vector DB"], "features": ["Retrieval-Augmented Generation", "WebSocket streaming", "Context awareness"], "category": "ai"},
    {"id": 9, "name": "Multi-Region Disaster Recovery", "slug": "multi-region-disaster-recovery", "description": "Resilient architecture with automated failover between AWS regions.", "status": "Production Ready", "completion_percentage": 100, "tags": ["aws", "dr", "reliability", "terraform", "automation"], "github_path": "projects/9-multi-region-disaster-recovery", "technologies": ["Terraform", "AWS Route53", "AWS RDS Global", "Python"], "features": ["Automated failover scripts", "Backup verification", "Cross-region replication", "RTO/RPO validation"], "category": "dr"},
    {"id": 10, "name": "Blockchain Smart Contract Platform", "slug": "blockchain-smart-contract-platform", "description": "DeFi protocol with modular smart contracts for staking and governance.", "status": "Advanced", "completion_percentage": 70, "tags": ["blockchain", "solidity", "smart-contracts", "web3"], "github_path": "projects/10-blockchain-smart-contract-platform", "technologies": ["Solidity", "Hardhat", "TypeScript", "Ethers.js"], "features": ["Staking logic", "Governance tokens", "Automated testing", "Security analysis"], "category": "blockchain"},
    {"id": 11, "name": "IoT Data Analytics", "slug": "iot-data-analytics", "description": "Edge-to-cloud ingestion stack with MQTT telemetry and anomaly detection.", "status": "Production Ready", "completion_percentage": 100, "tags": ["iot", "analytics", "timescaledb", "mqtt", "machine-learning"], "github_path": "projects/11-iot-data-analytics", "technologies": ["AWS IoT Core", "Python", "TimescaleDB", "MQTT", "Scikit-learn"], "features": ["Device provisioning automation", "ML-based anomaly detection", "Real-time telemetry", "Infrastructure as Code"], "category": "iot"},
    {"id": 12, "name": "Quantum Computing Integration", "slug": "quantum-computing-integration", "description": "Hybrid quantum-classical workloads using Qiskit.", "status": "Substantial", "completion_percentage": 50, "tags": ["quantum-computing", "qiskit", "research", "python"], "github_path": "projects/12-quantum-computing", "technologies": ["Qiskit", "Python", "AWS Batch"], "features": ["Variational Quantum Eigensolver", "Hybrid workflow orchestration"], "category": "infrastructure"},
    {"id": 13, "name": "Advanced Cybersecurity Platform", "slug": "advanced-cybersecurity-platform", "description": "SOAR engine consolidating SIEM alerts with automated playbooks.", "status": "Substantial", "completion_percentage": 45, "tags": ["cybersecurity", "soc", "siem", "soar", "python"], "github_path": "projects/13-advanced-cybersecurity", "technologies": ["Python", "ELK Stack", "VirusTotal API"], "features": ["Alert aggregation", "Automated response playbooks", "Threat intelligence enrichment"], "category": "security"},
    {"id": 14, "name": "Edge AI Inference Platform", "slug": "edge-ai-inference-platform", "description": "Containerized ONNX Runtime microservice for edge devices.", "status": "Substantial", "completion_percentage": 50, "tags": ["edge-ai", "inference", "onnx", "iot"], "github_path": "projects/14-edge-ai-inference", "technologies": ["ONNX Runtime", "Python", "Docker", "Azure IoT Edge"], "features": ["Low-latency inference", "Model optimization", "Containerized deployment"], "category": "iot"},
    {"id": 15, "name": "Real-time Collaboration Platform", "slug": "real-time-collaboration-platform", "description": "Operational Transform collaboration server with CRDT backup.", "status": "Substantial", "completion_percentage": 50, "tags": ["websockets", "real-time", "collaboration", "crdt"], "github_path": "projects/15-real-time-collaboration", "technologies": ["Python", "WebSockets", "Redis"], "features": ["Real-time document editing", "Conflict resolution", "Presence tracking"], "category": "streaming"},
    {"id": 16, "name": "Advanced Data Lake", "slug": "advanced-data-lake", "description": "Medallion architecture with Delta Lake and structured streaming.", "status": "Substantial", "completion_percentage": 55, "tags": ["data-lake", "glue", "athena", "spark"], "github_path": "projects/16-advanced-data-lake", "technologies": ["Databricks", "Delta Lake", "Python", "SQL"], "features": ["Bronze/Silver/Gold layers", "ACID transactions", "Stream ingestion"], "category": "streaming"},
    {"id": 17, "name": "Multi-Cloud Service Mesh", "slug": "multi-cloud-service-mesh", "description": "Istio service mesh spanning AWS and GKE clusters.", "status": "Basic", "completion_percentage": 40, "tags": ["service-mesh", "istio", "multi-cloud", "kubernetes"], "github_path": "projects/17-multi-cloud-service-mesh", "technologies": ["Istio", "Kubernetes", "Consul"], "features": ["Cross-cluster communication", "mTLS enforcement", "Traffic splitting"], "category": "infrastructure"},
    {"id": 18, "name": "GPU-Accelerated Computing", "slug": "gpu-accelerated-computing", "description": "CUDA-based risk simulation engine with Dask.", "status": "Substantial", "completion_percentage": 45, "tags": ["gpu", "cuda", "hpc", "python"], "github_path": "projects/18-gpu-accelerated-computing", "technologies": ["CUDA", "Python", "Dask", "Nvidia Drivers"], "features": ["Monte Carlo simulations", "Parallel processing", "Performance benchmarking"], "category": "infrastructure"},
    {"id": 19, "name": "Advanced Kubernetes Operators", "slug": "advanced-kubernetes-operators", "description": "Custom resource operator built with Kopf.", "status": "Substantial", "completion_percentage": 50, "tags": ["kubernetes", "operators", "python", "kopf"], "github_path": "projects/19-advanced-kubernetes-operators", "technologies": ["Python", "Kopf", "Kubernetes API"], "features": ["Custom Resource Definitions", "Automated reconciliation", "State management"], "category": "infrastructure"},
    {"id": 20, "name": "Blockchain Oracle Service", "slug": "blockchain-oracle-service", "description": "Chainlink-compatible external adapter.", "status": "Substantial", "completion_percentage": 50, "tags": ["blockchain", "oracle", "chainlink", "solidity"], "github_path": "projects/20-blockchain-oracle-service", "technologies": ["Node.js", "Solidity", "Docker"], "features": ["Off-chain data fetching", "Cryptographic signing", "Smart contract integration"], "category": "blockchain"},
    {"id": 21, "name": "Quantum-Safe Cryptography", "slug": "quantum-safe-cryptography", "description": "Hybrid key exchange service using Kyber KEM.", "status": "Substantial", "completion_percentage": 50, "tags": ["cryptography", "post-quantum", "security", "python"], "github_path": "projects/21-quantum-safe-cryptography", "technologies": ["Python", "Kyber", "Cryptography Libraries"], "features": ["Post-quantum key exchange", "Hybrid encryption scheme", "NIST-standard algorithms"], "category": "security"},
    {"id": 22, "name": "Autonomous DevOps Platform", "slug": "autonomous-devops-platform", "description": "Event-driven automation layer for self-healing infrastructure.", "status": "Basic", "completion_percentage": 40, "tags": ["devops", "automation", "ai", "python"], "github_path": "projects/22-autonomous-devops-platform", "technologies": ["Python", "Prometheus API", "Kubernetes API"], "features": ["Incident detection", "Automated remediation", "Runbook automation"], "category": "monitoring"},
    {"id": 23, "name": "Advanced Monitoring & Observability", "slug": "advanced-monitoring-observability", "description": "Unified observability stack with Prometheus, Tempo, Loki, and Grafana.", "status": "Production Ready", "completion_percentage": 100, "tags": ["monitoring", "observability", "grafana", "prometheus"], "github_path": "projects/23-advanced-monitoring", "technologies": ["Prometheus", "Grafana", "Loki", "Thanos", "Python"], "features": ["Custom application exporter", "Multi-channel alerting", "Long-term storage", "SLO tracking"], "category": "monitoring"},
    {"id": 24, "name": "Portfolio Report Generator", "slug": "report-generator", "description": "Automated report generation system using Jinja2 and WeasyPrint.", "status": "Production Ready", "completion_percentage": 100, "tags": ["automation", "reporting", "python"], "github_path": "projects/24-report-generator", "technologies": ["Python", "Jinja2", "WeasyPrint", "APScheduler"], "features": ["Scheduled generation", "Email delivery", "Historical trending", "PDF/HTML output"], "category": "serverless"},
    {"id": 25, "name": "Portfolio Website", "slug": "portfolio-website", "description": "Static documentation portal generated with VitePress.", "status": "Production Ready", "completion_percentage": 100, "tags": ["web", "vitepress", "documentation", "vue"], "github_path": "projects/25-portfolio-website", "technologies": ["VitePress", "Vue.js", "Node.js", "GitHub Pages"], "features": ["Project showcase", "Automated deployment", "Responsive design", "Search functionality"], "category": "ci-cd"}
]

# =============================================================================
# TECHNOLOGY PURPOSE MAPPING
# =============================================================================

TECH_PURPOSES = {
    "Terraform": "Infrastructure as Code - declarative resource management",
    "AWS CDK": "Type-safe infrastructure definitions with familiar languages",
    "Pulumi": "Multi-language IaC with state management",
    "Python": "Automation scripts, data processing, ML pipelines",
    "Bash": "Shell automation and system integration",
    "Docker": "Containerization for consistent deployments",
    "GitHub Actions": "CI/CD workflow automation",
    "ArgoCD": "GitOps continuous delivery for Kubernetes",
    "Helm": "Kubernetes package management",
    "Kustomize": "Kubernetes configuration customization",
    "Apache Kafka": "Distributed event streaming platform",
    "Apache Flink": "Stateful stream processing",
    "MLflow": "ML experiment tracking and model registry",
    "FastAPI": "High-performance Python API framework",
    "Prometheus": "Metrics collection and alerting",
    "Grafana": "Visualization and dashboards",
    "Loki": "Log aggregation and querying",
    "AWS SAM": "Serverless application development",
    "Lambda": "Event-driven serverless compute",
    "Step Functions": "Workflow orchestration",
    "DynamoDB": "Serverless NoSQL database",
    "Solidity": "Smart contract development",
    "Hardhat": "Ethereum development environment",
    "Ethers.js": "Ethereum JavaScript library",
    "TypeScript": "Type-safe JavaScript development",
    "AWS IoT Core": "Managed IoT message broker",
    "TimescaleDB": "Time-series database for telemetry",
    "MQTT": "Lightweight IoT messaging protocol",
    "Scikit-learn": "Machine learning algorithms",
    "Qiskit": "Quantum computing SDK",
    "ELK Stack": "Elasticsearch, Logstash, Kibana",
    "ONNX Runtime": "Cross-platform ML inference",
    "Azure IoT Edge": "Edge computing runtime",
    "Redis": "In-memory data store and caching",
    "WebSockets": "Real-time bidirectional communication",
    "Databricks": "Unified analytics platform",
    "Delta Lake": "ACID transactions for data lakes",
    "Istio": "Service mesh for microservices",
    "Consul": "Service discovery and configuration",
    "CUDA": "GPU parallel computing platform",
    "Dask": "Parallel computing library",
    "Kopf": "Kubernetes operator framework",
    "Node.js": "JavaScript runtime for backend services",
    "Thanos": "Long-term Prometheus storage",
    "Jinja2": "Template engine for report generation",
    "WeasyPrint": "HTML to PDF conversion",
    "APScheduler": "Task scheduling library",
    "VitePress": "Static site generator",
    "Vue.js": "Frontend JavaScript framework",
    "LangChain": "LLM application framework",
    "Vector DB": "Embedding storage and retrieval",
    "Debezium": "Change Data Capture platform",
    "PostgreSQL": "Relational database",
    "Trivy": "Container vulnerability scanner",
    "SonarQube": "Code quality analysis",
    "OWASP ZAP": "Web application security testing",
    "Avro": "Data serialization format",
    "Optuna": "Hyperparameter optimization",
    "Kubernetes": "Container orchestration",
    "Kubernetes API": "Programmatic cluster access",
    "Kafka": "Event streaming (alias)",
    "SQL": "Structured Query Language",
    "Nvidia Drivers": "GPU driver software",
    "Kyber": "Post-quantum cryptographic algorithm",
    "Cryptography Libraries": "Cryptographic primitives",
    "VirusTotal API": "Malware analysis service",
    "AWS Route53": "DNS and traffic routing",
    "AWS RDS Global": "Multi-region database"
}


class EnhancedWikiGenerator:
    """Generates comprehensive Wiki.js pages with detailed educational content."""

    def __init__(self, projects: list[dict], output_dir: str = "wiki"):
        self.projects = projects
        self.output_dir = Path(output_dir)

    def generate_frontmatter(self, project: dict) -> str:
        """Generate Wiki.js compatible YAML frontmatter."""
        tags = "\n".join(f"  - {tag}" for tag in project.get("tags", []))
        return f"""---
title: "{project['name']}"
description: "{project['description']}"
published: true
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}
tags:
{tags}
editor: markdown
dateCreated: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}
---

"""

    def generate_header(self, project: dict) -> str:
        """Generate page header with status and metadata."""
        status = project.get("status", "Unknown")
        completion = project.get("completion_percentage", 0)
        tags = " ".join(f"`{tag}`" for tag in project.get("tags", []))
        filled = int(completion / 10)
        progress = f"[{'█' * filled}{'░' * (10 - filled)}] {completion}%"

        return f"""# {project['name']}

> **Status**: {status} | **Completion**: {progress}
>
> {tags}

{project['description']}

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Learning Objectives](#-learning-objectives)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Technology Deep Dives](#-technology-deep-dives)
- [Implementation Guide](#-implementation-guide)
- [Best Practices](#-best-practices)
- [Quick Start](#-quick-start)
- [Operational Guide](#-operational-guide)
- [Related Projects](#-related-projects)

---

"""

    def generate_problem_section(self, project: dict) -> str:
        """Generate detailed problem statement section."""
        category = project.get("category", "infrastructure")
        problem = PROBLEM_STATEMENTS.get(category, PROBLEM_STATEMENTS.get("infrastructure"))

        return f"""## 🎯 Problem Statement

### {problem['title']}

{problem['context']}

{problem['impact']}

### How This Project Addresses It

{problem['solution_approach']}

### Key Features Delivered

"""

    def generate_features(self, project: dict) -> str:
        """Generate features list."""
        features = project.get("features", [])
        return "\n".join(f"- ✅ **{f}**" for f in features) + "\n\n---\n\n"

    def generate_learning_objectives(self, project: dict) -> str:
        """Generate learning objectives section."""
        category = project.get("category", "infrastructure")
        objectives = LEARNING_OBJECTIVES.get(category, [])

        if not objectives:
            return ""

        obj_list = "\n".join(f"{i}. {obj}" for i, obj in enumerate(objectives, 1))

        return f"""## 🎓 Learning Objectives

By studying this project, you will learn to:

{obj_list}

---

"""

    def generate_architecture(self, project: dict) -> str:
        """Generate architecture section."""
        category = project.get("category", "infrastructure")
        arch = ARCHITECTURE_COMPONENTS.get(category)

        content = f"""## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      {project['name'][:45]:<45}  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐     ┌─────────────┐     ┌─────────────┐          │
│   │  Input  │────▶│  Processing │────▶│   Output    │          │
│   │  Layer  │     │    Layer    │     │    Layer    │          │
│   └─────────┘     └─────────────┘     └─────────────┘          │
│                                                                 │
│   • Data ingestion     • Core logic       • API/Events         │
│   • Validation         • Transformation   • Storage            │
│   • Authentication     • Orchestration    • Monitoring         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

"""

        if arch:
            content += "### Component Layers\n\n"
            for layer in arch.get("layers", []):
                components = ", ".join(layer["components"])
                content += f"**{layer['name']}**\n"
                content += f"- Components: {components}\n\n"

            if arch.get("data_flow"):
                content += f"### Data Flow\n\n`{arch['data_flow']}`\n\n"

        content += "---\n\n"
        return content

    def generate_tech_stack(self, project: dict) -> str:
        """Generate tech stack section with rationale."""
        technologies = project.get("technologies", [])

        content = """## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
"""

        for tech in technologies:
            purpose = TECH_PURPOSES.get(tech, "Core technology component")
            content += f"| **{tech}** | {purpose} |\n"

        content += """
### Stack Selection Rationale

This technology stack was selected based on:

1. **Production Readiness**: All components are battle-tested in production environments
2. **Community Support**: Strong ecosystems with extensive documentation
3. **Integration**: Technologies work well together with established patterns
4. **Scalability**: Architecture supports horizontal scaling as requirements grow
5. **Observability**: Built-in support for metrics, logging, and tracing

---

"""
        return content

    def generate_deep_dives(self, project: dict) -> str:
        """Generate technology deep dive sections."""
        tags = project.get("tags", [])
        content = "## 🔬 Technology Deep Dives\n\n"

        matched = 0
        for tag in tags:
            if tag in TECHNOLOGY_DEEP_DIVES and matched < 2:
                dive = TECHNOLOGY_DEEP_DIVES[tag]
                content += f"### 📚 {dive['title']}\n\n"
                content += f"{dive['explanation']}\n\n"

                if dive.get("how_it_works"):
                    content += f"#### How It Works\n{dive['how_it_works']}\n\n"

                if dive.get("code_example"):
                    content += f"#### Code Example\n\n{dive['code_example']}\n\n"

                if dive.get("benefits"):
                    content += "#### Key Benefits\n\n"
                    for b in dive["benefits"]:
                        content += f"- {b}\n"
                    content += "\n"

                if dive.get("best_practices"):
                    content += "#### Best Practices\n\n"
                    for bp in dive["best_practices"]:
                        content += f"- {bp}\n"
                    content += "\n"

                if dive.get("anti_patterns"):
                    content += "#### Anti-Patterns to Avoid\n\n"
                    for ap in dive["anti_patterns"]:
                        content += f"- {ap}\n"
                    content += "\n"

                if dive.get("learning_resources"):
                    content += "#### Learning Resources\n\n"
                    for lr in dive["learning_resources"]:
                        content += f"- {lr}\n"
                    content += "\n"

                content += "---\n\n"
                matched += 1

        if matched == 0:
            content += "*Deep dive content will be added as this project matures.*\n\n---\n\n"

        return content

    def generate_implementation_guide(self, project: dict) -> str:
        """Generate implementation guide section."""
        features = project.get("features", [])[:3]

        content = """## 📖 Implementation Guide

This section provides detailed implementation guidance for key features.

"""

        for i, feature in enumerate(features, 1):
            safe_name = feature.lower().replace(" ", "_").replace("-", "_").replace("/", "_")[:20]
            content += f"""### Step {i}: {feature}

**Objective**: Implement {feature.lower()} following best practices.

**Approach**:
1. Define requirements and acceptance criteria
2. Design the component architecture
3. Implement with test coverage
4. Validate in staging environment
5. Deploy with monitoring

**Key Considerations**:
- Error handling and edge cases
- Performance implications
- Security requirements
- Monitoring and alerting

```python
# Implementation pattern for {feature}
class {safe_name.title().replace('_', '')}Handler:
    \"\"\"Handler for {feature}.\"\"\"

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def execute(self, input_data: dict) -> dict:
        \"\"\"Execute the {feature.lower()} logic.\"\"\"
        self.logger.info(f"Processing: {{input_data}}")

        # Validation
        self._validate(input_data)

        # Core logic
        result = self._process(input_data)

        # Persist/return
        return result

    def _validate(self, data: dict) -> None:
        \"\"\"Validate input data.\"\"\"
        pass

    def _process(self, data: dict) -> dict:
        \"\"\"Core processing logic.\"\"\"
        return {{"status": "success"}}
```

"""

        content += "---\n\n"
        return content

    def generate_best_practices(self, project: dict) -> str:
        """Generate best practices section."""
        category = project.get("category", "infrastructure")

        content = """## ✅ Best Practices

### General Guidelines

1. **Infrastructure as Code**: All resources defined in version-controlled code
2. **Immutable Infrastructure**: Replace rather than modify running instances
3. **Defense in Depth**: Multiple security layers, not single points of protection
4. **Observability First**: Instrument before deploying to production
5. **Automate Everything**: Manual processes are error-prone and don't scale

### Security Practices

- Never store secrets in code or environment variables
- Use IAM roles and service accounts with least privilege
- Enable encryption at rest and in transit
- Implement network segmentation with security groups
- Regular security scanning in CI/CD pipelines

### Operational Practices

- Implement health checks for all services
- Set up alerting with actionable runbooks
- Practice chaos engineering to validate resilience
- Document operational procedures
- Conduct regular disaster recovery drills

### What to Avoid

- ❌ Manual changes to production systems
- ❌ Sharing credentials between services
- ❌ Skipping tests for "simple" changes
- ❌ Single points of failure without redundancy
- ❌ Ignoring security scanner findings

---

"""
        return content

    def generate_quickstart(self, project: dict) -> str:
        """Generate quick start section."""
        github_path = project.get("github_path", "")

        return f"""## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ with pip
- AWS CLI configured (for AWS projects)
- kubectl configured (for Kubernetes projects)

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/samueljackson-collab/Portfolio-Project.git
cd Portfolio-Project/{github_path}

# Review documentation
cat README.md

# Copy environment template
cp .env.example .env

# Edit configuration
vim .env
```

### Run Locally

```bash
# Using Docker Compose
docker-compose up -d

# Verify services
docker-compose ps

# View logs
docker-compose logs -f

# Run tests
docker-compose exec app pytest
```

### Deploy to Cloud

```bash
# Initialize infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# Deploy application
./scripts/deploy.sh
```

---

"""

    def generate_operational_guide(self, project: dict) -> str:
        """Generate operational guide section."""
        return """## ⚙️ Operational Guide

### Monitoring & Observability

| Signal | Tool | Access |
|--------|------|--------|
| Metrics | Prometheus/Grafana | `http://grafana:3000` |
| Logs | Loki/Grafana | Grafana Explore |
| Traces | Tempo/Jaeger | Grafana Explore |

### Common Operations

| Task | Command |
|------|---------|
| Health check | `make health` or `curl /health` |
| View logs | `docker-compose logs -f [service]` |
| Run tests | `make test` |
| Deploy | `make deploy ENV=production` |
| Rollback | `make rollback VERSION=previous` |

### Troubleshooting Guide

<details>
<summary><strong>Service won't start</strong></summary>

1. Check logs: `docker-compose logs [service]`
2. Verify configuration: `docker-compose config`
3. Check resource limits: `docker stats`
4. Validate dependencies are running
</details>

<details>
<summary><strong>Connection refused errors</strong></summary>

1. Verify service is running: `docker-compose ps`
2. Check network connectivity: `docker network ls`
3. Validate port mappings in compose file
4. Check firewall/security group rules
</details>

<details>
<summary><strong>Performance degradation</strong></summary>

1. Check metrics dashboards for resource usage
2. Review recent deployments for changes
3. Analyze slow queries/requests with tracing
4. Scale horizontally if resource-bound
</details>

### Runbook Links

- [Incident Response](docs/runbooks/incident-response.md)
- [Scaling Procedures](docs/runbooks/scaling.md)
- [Backup & Recovery](docs/runbooks/backup-recovery.md)
- [Security Incident](docs/runbooks/security-incident.md)

---

"""

    def generate_related_projects(self, project: dict) -> str:
        """Generate related projects section."""
        current_tags = set(project.get("tags", []))
        current_id = project.get("id")

        related = []
        for p in self.projects:
            if p.get("id") == current_id:
                continue
            overlap = len(current_tags & set(p.get("tags", [])))
            if overlap >= 1:
                related.append((overlap, p))

        related.sort(key=lambda x: x[0], reverse=True)
        related = related[:4]

        if not related:
            return ""

        content = "## 🔗 Related Projects\n\n"
        content += "| Project | Description | Overlap |\n"
        content += "|---------|-------------|--------|\n"

        for overlap, p in related:
            desc = p['description'][:50] + "..." if len(p['description']) > 50 else p['description']
            content += f"| [{p['name']}](/projects/{p['slug']}) | {desc} | {overlap} tags |\n"

        content += "\n---\n\n"
        return content

    def generate_footer(self, project: dict) -> str:
        """Generate page footer."""
        github_path = project.get("github_path", "")

        return f"""## 📚 Additional Resources

### Project Links

- 📂 **Source Code**: [GitHub Repository](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/{github_path})
- 📖 **Documentation**: [`{github_path}/docs/`](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/{github_path}/docs)
- 🐛 **Issues**: [Report bugs or request features](https://github.com/samueljackson-collab/Portfolio-Project/issues)

### External Resources

- [AWS Documentation](https://docs.aws.amazon.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Terraform Registry](https://registry.terraform.io/)

---

<div align="center">
<small>

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')} |
**Generated by**: Portfolio Wiki Content Generator v2

</small>
</div>
"""

    def generate_wiki_page(self, project: dict) -> str:
        """Generate complete wiki page."""
        sections = [
            self.generate_frontmatter(project),
            self.generate_header(project),
            self.generate_problem_section(project),
            self.generate_features(project),
            self.generate_learning_objectives(project),
            self.generate_architecture(project),
            self.generate_tech_stack(project),
            self.generate_deep_dives(project),
            self.generate_implementation_guide(project),
            self.generate_best_practices(project),
            self.generate_quickstart(project),
            self.generate_operational_guide(project),
            self.generate_related_projects(project),
            self.generate_footer(project)
        ]
        return "".join(sections)

    def generate_all(self) -> dict[str, str]:
        """Generate all wiki pages."""
        output_path = self.output_dir / "projects"
        output_path.mkdir(parents=True, exist_ok=True)

        pages = {}
        for project in self.projects:
            slug = project.get("slug", f"project-{project.get('id', 0)}")
            content = self.generate_wiki_page(project)
            pages[slug] = content

            filepath = output_path / f"{slug}.md"
            filepath.write_text(content)
            print(f"Generated: {filepath}")

        return pages


class WikiConfigGenerator:
    """Generate Wiki.js sidebar and navigation config."""

    def __init__(self, projects: list[dict]):
        self.projects = projects

    def generate_sidebar(self) -> str:
        """Generate YAML sidebar config."""
        by_status: dict[str, list] = {}
        for p in self.projects:
            status = p.get("status", "Other")
            by_status.setdefault(status, []).append(p)

        yaml = """# Wiki.js Sidebar Configuration
# Generated by Portfolio Wiki Content Generator

navigation:
  - title: Home
    path: /
    icon: mdi-home

  - title: Projects
    icon: mdi-folder-multiple
    children:
"""

        for status in ["Production Ready", "Advanced", "Substantial", "In Development", "Basic"]:
            if status in by_status:
                yaml += f'      - title: "{status}"\n'
                yaml += "        children:\n"
                for p in sorted(by_status[status], key=lambda x: x["name"]):
                    yaml += f'          - title: "{p["name"]}"\n'
                    yaml += f'            path: /projects/{p["slug"]}\n'

        return yaml

    def generate_tags_page(self) -> str:
        """Generate tags overview page."""
        tags: dict[str, list] = {}
        for p in self.projects:
            for tag in p.get("tags", []):
                tags.setdefault(tag, []).append(p)

        content = """---
title: Browse by Technology
description: Explore projects by technology tags
published: true
---

# 🏷️ Browse by Technology

Explore portfolio projects organized by technology and domain.

| Tag | Projects |
|-----|----------|
"""

        for tag in sorted(tags.keys()):
            count = len(tags[tag])
            content += f"| `{tag}` | {count} project{'s' if count > 1 else ''} |\n"

        content += "\n---\n\n"

        for tag in sorted(tags.keys()):
            content += f"## {tag.replace('-', ' ').title()}\n\n"
            for p in tags[tag]:
                content += f"- [{p['name']}](/projects/{p['slug']}) - {p['description'][:60]}...\n"
            content += "\n"

        return content


def main():
    """Main entry point."""
    print("=" * 60)
    print("Wiki.js Content Generator v2 - Enhanced Edition")
    print("=" * 60)

    # Generate wiki pages
    generator = EnhancedWikiGenerator(PROJECTS_DATA, "wiki")
    pages = generator.generate_all()
    print(f"\nGenerated {len(pages)} enhanced wiki pages")

    # Generate config
    config_gen = WikiConfigGenerator(PROJECTS_DATA)

    config_path = Path("wiki/config")
    config_path.mkdir(parents=True, exist_ok=True)

    sidebar_path = config_path / "sidebar.yaml"
    sidebar_path.write_text(config_gen.generate_sidebar())
    print(f"Generated: {sidebar_path}")

    tags_path = Path("wiki/tags.md")
    tags_path.write_text(config_gen.generate_tags_page())
    print(f"Generated: {tags_path}")

    # Generate JSON config
    config_json = {
        "generated_at": datetime.now().isoformat(),
        "total_projects": len(PROJECTS_DATA),
        "version": "2.0"
    }
    json_path = config_path / "wiki_config.json"
    json_path.write_text(json.dumps(config_json, indent=2))
    print(f"Generated: {json_path}")

    print("\n" + "=" * 60)
    print("Generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
