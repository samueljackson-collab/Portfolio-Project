#!/usr/bin/env python3
"""
Enhanced Wiki.js Content Generator

Generates comprehensive wiki documentation for portfolio projects with:
- Wiki.js-compatible frontmatter and metadata
- Deep Dive educational modules (tag-based explanations)
- Structured sections: Problem Statement, Tech Stack Selection, Deployment Walkthrough
- Technology knowledge base for intelligent content generation
- Navigation/sidebar configuration generation
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# =============================================================================
# TECHNOLOGY KNOWLEDGE BASE
# =============================================================================
# Educational content mapped by technology/tag for reusable "Deep Dive" modules

TECHNOLOGY_DEEP_DIVES = {
    # Infrastructure & Cloud
    "terraform": {
        "title": "Why Terraform?",
        "explanation": """Terraform is HashiCorp's Infrastructure as Code (IaC) tool that enables
declarative infrastructure management across multiple cloud providers. It uses HCL (HashiCorp
Configuration Language) to define resources in a human-readable format.""",
        "benefits": [
            "**Provider Agnostic**: Single workflow for AWS, GCP, Azure, and 100+ providers",
            "**State Management**: Tracks infrastructure state for safe modifications",
            "**Plan Before Apply**: Preview changes before execution reduces risk",
            "**Modular Design**: Reusable modules promote DRY principles",
            "**Version Control Friendly**: Text-based configs integrate with Git workflows"
        ],
        "learning_resources": [
            "[Terraform Documentation](https://developer.hashicorp.com/terraform/docs)",
            "[Terraform Best Practices](https://www.terraform-best-practices.com/)"
        ]
    },
    "aws": {
        "title": "Why AWS?",
        "explanation": """Amazon Web Services (AWS) is the world's most comprehensive cloud platform,
offering 200+ services from data centers globally. It provides the building blocks for
scalable, reliable, and cost-effective infrastructure.""",
        "benefits": [
            "**Market Leader**: Largest ecosystem with extensive documentation",
            "**Global Infrastructure**: 30+ regions for low-latency deployments",
            "**Service Breadth**: Compute, storage, ML, IoT, analytics under one roof",
            "**Pay-as-you-go**: Optimize costs with granular billing",
            "**Enterprise Ready**: Compliance certifications (SOC, HIPAA, PCI)"
        ],
        "learning_resources": [
            "[AWS Documentation](https://docs.aws.amazon.com/)",
            "[AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)"
        ]
    },
    "kubernetes": {
        "title": "Why Kubernetes?",
        "explanation": """Kubernetes (K8s) is the industry-standard container orchestration platform.
Originally designed by Google, it automates deployment, scaling, and management of
containerized applications across clusters of hosts.""",
        "benefits": [
            "**Self-Healing**: Automatically restarts failed containers",
            "**Horizontal Scaling**: Scale applications based on demand",
            "**Service Discovery**: Built-in DNS and load balancing",
            "**Rolling Updates**: Zero-downtime deployments",
            "**Declarative Configuration**: Define desired state, K8s handles the rest"
        ],
        "learning_resources": [
            "[Kubernetes Documentation](https://kubernetes.io/docs/)",
            "[CNCF Kubernetes Training](https://www.cncf.io/certification/cka/)"
        ]
    },
    "docker": {
        "title": "Why Docker?",
        "explanation": """Docker revolutionized software delivery by packaging applications with their
dependencies into portable containers. This ensures consistency across development,
testing, and production environments.""",
        "benefits": [
            "**Consistency**: Same container runs everywhere",
            "**Isolation**: Applications run in isolated environments",
            "**Efficiency**: Lightweight compared to VMs",
            "**Version Control**: Image tags enable reproducible deployments",
            "**Ecosystem**: Docker Hub hosts millions of pre-built images"
        ],
        "learning_resources": [
            "[Docker Documentation](https://docs.docker.com/)",
            "[Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)"
        ]
    },

    # CI/CD & GitOps
    "github-actions": {
        "title": "Why GitHub Actions?",
        "explanation": """GitHub Actions is a CI/CD platform integrated directly into GitHub repositories.
It enables automation of build, test, and deployment workflows triggered by repository events.""",
        "benefits": [
            "**Native Integration**: No external CI server needed",
            "**Marketplace**: 10,000+ community actions available",
            "**Matrix Builds**: Test across multiple OS/versions simultaneously",
            "**Secrets Management**: Secure credential storage",
            "**Free Tier**: Generous free minutes for open source"
        ],
        "learning_resources": [
            "[GitHub Actions Documentation](https://docs.github.com/en/actions)",
            "[GitHub Actions Marketplace](https://github.com/marketplace?type=actions)"
        ]
    },
    "argocd": {
        "title": "Why ArgoCD?",
        "explanation": """ArgoCD is a declarative GitOps continuous delivery tool for Kubernetes.
It continuously monitors Git repositories and automatically syncs application state
to match the desired configuration.""",
        "benefits": [
            "**GitOps Native**: Git as single source of truth",
            "**Auto-Sync**: Automatically reconciles cluster state",
            "**Multi-Cluster**: Manage multiple clusters from one instance",
            "**Rollback**: One-click rollback to previous versions",
            "**RBAC**: Fine-grained access control"
        ],
        "learning_resources": [
            "[ArgoCD Documentation](https://argo-cd.readthedocs.io/)",
            "[GitOps Principles](https://opengitops.dev/)"
        ]
    },

    # Data & Streaming
    "kafka": {
        "title": "Why Apache Kafka?",
        "explanation": """Apache Kafka is a distributed event streaming platform capable of handling
trillions of events per day. It provides durable, fault-tolerant message storage
with high throughput for real-time data pipelines.""",
        "benefits": [
            "**High Throughput**: Millions of messages per second",
            "**Durability**: Persists messages to disk with replication",
            "**Scalability**: Horizontally scalable across partitions",
            "**Exactly-Once Semantics**: Guaranteed message delivery",
            "**Ecosystem**: Connect, Streams, Schema Registry"
        ],
        "learning_resources": [
            "[Kafka Documentation](https://kafka.apache.org/documentation/)",
            "[Confluent Developer](https://developer.confluent.io/)"
        ]
    },
    "flink": {
        "title": "Why Apache Flink?",
        "explanation": """Apache Flink is a stream processing framework for stateful computations
over unbounded and bounded data streams. It excels at event-time processing
with exactly-once state consistency.""",
        "benefits": [
            "**True Streaming**: Process events as they arrive",
            "**Stateful Processing**: Maintain state across events",
            "**Event Time**: Handle out-of-order events correctly",
            "**Checkpointing**: Fault-tolerant state snapshots",
            "**SQL Support**: Flink SQL for declarative queries"
        ],
        "learning_resources": [
            "[Flink Documentation](https://flink.apache.org/)",
            "[Flink Training](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/overview/)"
        ]
    },

    # Machine Learning & AI
    "mlflow": {
        "title": "Why MLflow?",
        "explanation": """MLflow is an open-source platform for managing the complete machine learning
lifecycle. It provides experiment tracking, model packaging, and deployment capabilities.""",
        "benefits": [
            "**Experiment Tracking**: Log parameters, metrics, and artifacts",
            "**Model Registry**: Version and stage models centrally",
            "**Reproducibility**: Package models with dependencies",
            "**Framework Agnostic**: Works with any ML library",
            "**Deployment**: Deploy to various serving platforms"
        ],
        "learning_resources": [
            "[MLflow Documentation](https://mlflow.org/docs/latest/index.html)",
            "[MLflow Tutorials](https://mlflow.org/docs/latest/tutorials-and-examples/index.html)"
        ]
    },
    "llm": {
        "title": "Why Large Language Models?",
        "explanation": """Large Language Models (LLMs) are neural networks trained on vast text corpora,
capable of understanding and generating human-like text. They power modern AI assistants,
code generation, and knowledge retrieval systems.""",
        "benefits": [
            "**Natural Language Understanding**: Process complex queries",
            "**Code Generation**: Assist with programming tasks",
            "**Knowledge Synthesis**: Combine information from training data",
            "**Few-Shot Learning**: Adapt to tasks with minimal examples",
            "**RAG Integration**: Augment with external knowledge bases"
        ],
        "learning_resources": [
            "[LangChain Documentation](https://python.langchain.com/docs/)",
            "[OpenAI API Guide](https://platform.openai.com/docs/)"
        ]
    },

    # Security
    "security": {
        "title": "Why Security-First Development?",
        "explanation": """Security-first development integrates security practices throughout the SDLC
rather than treating it as an afterthought. This shift-left approach catches
vulnerabilities early when they're cheapest to fix.""",
        "benefits": [
            "**Early Detection**: Find vulnerabilities before production",
            "**Cost Reduction**: Fix issues when they're cheapest",
            "**Compliance**: Meet regulatory requirements (SOC2, HIPAA)",
            "**Trust**: Build confidence with customers",
            "**Automation**: Consistent security checks in CI/CD"
        ],
        "learning_resources": [
            "[OWASP Top 10](https://owasp.org/www-project-top-ten/)",
            "[NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)"
        ]
    },
    "sast": {
        "title": "What is SAST?",
        "explanation": """Static Application Security Testing (SAST) analyzes source code to identify
security vulnerabilities without executing the application. It's a white-box testing
approach that catches issues early in development.""",
        "benefits": [
            "**Early Detection**: Scan code before it runs",
            "**Line-Level Feedback**: Pinpoint exact vulnerability locations",
            "**CI/CD Integration**: Automate in build pipelines",
            "**Coverage**: Analyze entire codebase systematically",
            "**Developer-Friendly**: Provide actionable remediation guidance"
        ],
        "learning_resources": [
            "[SonarQube Documentation](https://docs.sonarqube.org/)",
            "[Semgrep Rules](https://semgrep.dev/docs/)"
        ]
    },

    # Serverless
    "serverless": {
        "title": "Why Serverless?",
        "explanation": """Serverless computing abstracts infrastructure management, allowing developers
to focus on code. Cloud providers handle scaling, patching, and availability,
charging only for actual execution time.""",
        "benefits": [
            "**No Server Management**: Focus on business logic",
            "**Auto-Scaling**: Scale to zero or millions automatically",
            "**Pay-Per-Use**: No charges when idle",
            "**Faster Time-to-Market**: Deploy functions in minutes",
            "**Built-in HA**: Automatic multi-AZ deployment"
        ],
        "learning_resources": [
            "[AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)",
            "[Serverless Framework](https://www.serverless.com/framework/docs/)"
        ]
    },
    "aws-lambda": {
        "title": "Why AWS Lambda?",
        "explanation": """AWS Lambda is a serverless compute service that runs code in response to events.
It automatically manages the compute resources, scaling from zero to thousands
of concurrent executions.""",
        "benefits": [
            "**Event-Driven**: Trigger from 200+ AWS services",
            "**Sub-Second Billing**: Pay only for execution time",
            "**Language Support**: Python, Node.js, Java, Go, and more",
            "**Provisioned Concurrency**: Eliminate cold starts",
            "**Container Support**: Deploy as container images"
        ],
        "learning_resources": [
            "[Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)",
            "[AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)"
        ]
    },

    # Monitoring & Observability
    "prometheus": {
        "title": "Why Prometheus?",
        "explanation": """Prometheus is an open-source monitoring system with a dimensional data model
and powerful query language (PromQL). It's the de facto standard for Kubernetes
monitoring and cloud-native observability.""",
        "benefits": [
            "**Pull-Based Model**: Prometheus scrapes metrics from targets",
            "**PromQL**: Powerful query language for analysis",
            "**Service Discovery**: Auto-discover Kubernetes pods",
            "**Alertmanager**: Flexible alerting with routing",
            "**CNCF Graduated**: Production-proven, community-backed"
        ],
        "learning_resources": [
            "[Prometheus Documentation](https://prometheus.io/docs/)",
            "[PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)"
        ]
    },
    "grafana": {
        "title": "Why Grafana?",
        "explanation": """Grafana is the leading open-source visualization platform for metrics, logs,
and traces. It unifies data from multiple sources into interactive dashboards
with powerful alerting capabilities.""",
        "benefits": [
            "**Multi-Source**: Connect Prometheus, Loki, Tempo, and 100+ datasources",
            "**Rich Visualizations**: Charts, tables, heatmaps, and more",
            "**Alerting**: Unified alerting across all data sources",
            "**Dashboards as Code**: Version control with JSON/YAML",
            "**Plugin Ecosystem**: Extend with community plugins"
        ],
        "learning_resources": [
            "[Grafana Documentation](https://grafana.com/docs/)",
            "[Grafana Tutorials](https://grafana.com/tutorials/)"
        ]
    },

    # Blockchain
    "blockchain": {
        "title": "Why Blockchain?",
        "explanation": """Blockchain technology provides decentralized, immutable ledgers for trustless
transactions. Smart contracts enable programmable agreements that execute
automatically when conditions are met.""",
        "benefits": [
            "**Immutability**: Transactions cannot be altered",
            "**Decentralization**: No single point of failure",
            "**Transparency**: Public audit trail",
            "**Smart Contracts**: Self-executing agreements",
            "**Tokenization**: Represent assets digitally"
        ],
        "learning_resources": [
            "[Ethereum Documentation](https://ethereum.org/developers/docs/)",
            "[Solidity by Example](https://solidity-by-example.org/)"
        ]
    },
    "solidity": {
        "title": "Why Solidity?",
        "explanation": """Solidity is the primary programming language for Ethereum smart contracts.
It's a statically-typed, contract-oriented language influenced by C++, Python,
and JavaScript.""",
        "benefits": [
            "**EVM Compatible**: Runs on Ethereum and compatible chains",
            "**Mature Tooling**: Hardhat, Foundry, Remix IDE",
            "**Large Community**: Extensive documentation and examples",
            "**Security Patterns**: Well-documented best practices",
            "**Upgradability**: Proxy patterns for contract upgrades"
        ],
        "learning_resources": [
            "[Solidity Documentation](https://docs.soliditylang.org/)",
            "[OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)"
        ]
    },

    # Databases
    "database": {
        "title": "Why Database Engineering?",
        "explanation": """Database engineering ensures data systems are reliable, performant, and scalable.
It encompasses schema design, query optimization, replication strategies,
and migration planning.""",
        "benefits": [
            "**Data Integrity**: ACID guarantees protect consistency",
            "**Performance**: Optimized queries reduce latency",
            "**Scalability**: Handle growing data volumes",
            "**Availability**: Replication prevents data loss",
            "**Migration**: Evolve schemas safely"
        ],
        "learning_resources": [
            "[PostgreSQL Documentation](https://www.postgresql.org/docs/)",
            "[Database Internals](https://www.databass.dev/)"
        ]
    },

    # IoT
    "iot": {
        "title": "Why IoT Architecture?",
        "explanation": """Internet of Things (IoT) architecture connects physical devices to cloud
services for data collection, analysis, and actuation. It spans edge computing,
communication protocols, and real-time analytics.""",
        "benefits": [
            "**Real-Time Data**: Continuous telemetry streams",
            "**Edge Processing**: Reduce latency with local compute",
            "**Scalability**: Handle millions of devices",
            "**Insights**: ML-powered anomaly detection",
            "**Automation**: Trigger actions based on sensor data"
        ],
        "learning_resources": [
            "[AWS IoT Documentation](https://docs.aws.amazon.com/iot/)",
            "[MQTT Protocol](https://mqtt.org/getting-started/)"
        ]
    },

    # Quantum Computing
    "quantum-computing": {
        "title": "Why Quantum Computing?",
        "explanation": """Quantum computing leverages quantum mechanical phenomena to solve problems
intractable for classical computers. It promises breakthroughs in optimization,
cryptography, and simulation.""",
        "benefits": [
            "**Exponential Speedup**: For specific problem classes",
            "**Optimization**: Solve complex optimization problems",
            "**Simulation**: Model quantum systems accurately",
            "**Cryptography**: Break and build new encryption",
            "**Machine Learning**: Quantum-enhanced algorithms"
        ],
        "learning_resources": [
            "[Qiskit Textbook](https://qiskit.org/textbook/)",
            "[IBM Quantum Learning](https://learning.quantum-computing.ibm.com/)"
        ]
    },

    # Service Mesh
    "istio": {
        "title": "Why Istio?",
        "explanation": """Istio is a service mesh that provides traffic management, security, and
observability for microservices. It uses sidecar proxies (Envoy) to intercept
and control all network communication.""",
        "benefits": [
            "**mTLS**: Automatic encryption between services",
            "**Traffic Management**: Canary releases, A/B testing",
            "**Observability**: Distributed tracing, metrics",
            "**Policy Enforcement**: Rate limiting, access control",
            "**Multi-Cluster**: Span services across clusters"
        ],
        "learning_resources": [
            "[Istio Documentation](https://istio.io/latest/docs/)",
            "[Envoy Proxy](https://www.envoyproxy.io/docs/)"
        ]
    },

    # Data Lake
    "data-lake": {
        "title": "Why Data Lake Architecture?",
        "explanation": """Data lakes store raw data at scale, enabling diverse analytics workloads.
The medallion architecture (Bronze/Silver/Gold) progressively refines data
quality while maintaining lineage.""",
        "benefits": [
            "**Schema-on-Read**: Store first, structure later",
            "**Cost Effective**: Object storage is cheap",
            "**Flexibility**: Support structured and unstructured data",
            "**Decoupling**: Separate storage from compute",
            "**ACID Transactions**: Delta Lake adds reliability"
        ],
        "learning_resources": [
            "[Delta Lake Documentation](https://docs.delta.io/)",
            "[Databricks Lakehouse](https://www.databricks.com/product/data-lakehouse)"
        ]
    },

    # GPU Computing
    "gpu": {
        "title": "Why GPU Computing?",
        "explanation": """GPU computing harnesses parallel processing power for computationally
intensive tasks. Originally designed for graphics, GPUs now accelerate
machine learning, scientific simulations, and financial modeling.""",
        "benefits": [
            "**Massive Parallelism**: Thousands of cores for parallel tasks",
            "**ML Training**: Essential for deep learning",
            "**Scientific Computing**: Simulations, modeling",
            "**Cost Efficiency**: Better perf/$ for parallel workloads",
            "**Cloud Availability**: On-demand GPU instances"
        ],
        "learning_resources": [
            "[NVIDIA CUDA Documentation](https://docs.nvidia.com/cuda/)",
            "[CuPy Documentation](https://docs.cupy.dev/)"
        ]
    },

    # Cryptography
    "cryptography": {
        "title": "Why Post-Quantum Cryptography?",
        "explanation": """Post-quantum cryptography develops algorithms resistant to quantum computer
attacks. As quantum computers advance, current encryption (RSA, ECC) will
become vulnerable, requiring migration to quantum-safe alternatives.""",
        "benefits": [
            "**Future-Proof**: Protect against quantum threats",
            "**NIST Standards**: Standardized algorithms (Kyber, Dilithium)",
            "**Hybrid Approach**: Combine classical and PQC",
            "**Regulatory Compliance**: Prepare for mandates",
            "**Data Protection**: Secure long-lived secrets"
        ],
        "learning_resources": [
            "[NIST PQC](https://csrc.nist.gov/projects/post-quantum-cryptography)",
            "[Open Quantum Safe](https://openquantumsafe.org/)"
        ]
    },

    # Real-time Collaboration
    "websockets": {
        "title": "Why WebSockets?",
        "explanation": """WebSockets provide full-duplex communication over a single TCP connection,
enabling real-time bidirectional data flow between clients and servers.
They're essential for live collaboration, gaming, and streaming applications.""",
        "benefits": [
            "**Low Latency**: No HTTP overhead per message",
            "**Bidirectional**: Server can push to clients",
            "**Persistent Connection**: Single connection for session",
            "**Real-Time**: Sub-second message delivery",
            "**Wide Support**: All modern browsers support WebSockets"
        ],
        "learning_resources": [
            "[WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)",
            "[Socket.IO Documentation](https://socket.io/docs/)"
        ]
    },

    # CRDT
    "crdt": {
        "title": "What are CRDTs?",
        "explanation": """Conflict-free Replicated Data Types (CRDTs) are data structures that can
be replicated across multiple nodes and merged without conflicts. They enable
collaborative editing without central coordination.""",
        "benefits": [
            "**Conflict-Free**: Automatic merge without conflicts",
            "**Offline Support**: Continue editing without connection",
            "**Decentralized**: No central authority needed",
            "**Eventual Consistency**: All replicas converge",
            "**Collaboration**: Multiple users edit simultaneously"
        ],
        "learning_resources": [
            "[CRDT.tech](https://crdt.tech/)",
            "[Yjs CRDT Library](https://docs.yjs.dev/)"
        ]
    }
}

# =============================================================================
# PROBLEM STATEMENT TEMPLATES
# =============================================================================
# Maps project types/tags to problem statement frameworks

PROBLEM_TEMPLATES = {
    "infrastructure": """Modern cloud infrastructure demands **reproducibility**, **auditability**, and
**disaster recovery** capabilities. Manual provisioning leads to configuration drift,
undocumented changes, and prolonged recovery times during outages.""",

    "migration": """Database migrations are high-risk operations that traditionally require downtime.
Business continuity demands **zero-downtime** cutover while maintaining **data integrity**
across source and target systems.""",

    "ci-cd": """Traditional deployment processes involve manual steps, inconsistent environments,
and risky production releases. Teams need **automated**, **observable**, and
**reversible** deployment pipelines.""",

    "security": """Security vulnerabilities discovered in production are **50x more expensive** to fix
than those caught during development. Organizations need automated security gates
integrated into the development workflow.""",

    "streaming": """Batch processing introduces latency that's unacceptable for real-time use cases.
Modern applications require **sub-second** event processing with **exactly-once**
semantics to prevent data loss or duplication.""",

    "mlops": """Machine learning models degrade over time due to data drift and concept drift.
Without **automated monitoring**, **versioning**, and **retraining pipelines**,
models become unreliable in production.""",

    "serverless": """Traditional server management involves provisioning, patching, and scaling overhead.
Event-driven workloads with variable traffic patterns benefit from **automatic scaling**
and **pay-per-use** pricing models.""",

    "ai": """Users expect intelligent, context-aware interactions. Retrieval-Augmented Generation (RAG)
combines the power of large language models with domain-specific knowledge bases
for accurate, grounded responses.""",

    "dr": """System failures are inevitable. Without **automated failover**, **tested recovery procedures**,
and **validated RTO/RPO metrics**, organizations face extended outages and data loss.""",

    "blockchain": """Traditional systems rely on trusted intermediaries for transactions. Decentralized
applications require **trustless execution**, **transparent governance**, and
**immutable audit trails**.""",

    "iot": """IoT deployments generate massive telemetry streams that overwhelm traditional databases.
Edge-to-cloud architectures must handle **high-frequency ingestion**, **real-time analytics**,
and **anomaly detection** at scale.""",

    "monitoring": """Siloed monitoring tools create blind spots. Modern observability requires **unified metrics**,
**distributed tracing**, and **log aggregation** correlated across the entire stack.""",

    "collaboration": """Real-time collaboration requires handling concurrent edits without data loss.
Traditional locking mechanisms create poor user experience; modern solutions need
**conflict-free** synchronization.""",

    "default": """Modern software systems face increasing complexity in deployment, scaling, and operations.
This project addresses key challenges through automation, best practices, and
production-ready implementations."""
}

# =============================================================================
# WIKI PAGE GENERATOR
# =============================================================================


class WikiContentGenerator:
    """Generates comprehensive Wiki.js pages for portfolio projects."""

    def __init__(self, projects: list[dict[str, Any]], output_dir: str = "wiki"):
        self.projects = projects
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_frontmatter(self, project: dict[str, Any]) -> str:
        """Generate Wiki.js compatible YAML frontmatter."""
        tags_yaml = "\n".join(f"  - {tag}" for tag in project.get("tags", []))
        status_class = self._get_status_class(project.get("status", ""))

        return f"""---
title: {project['name']}
description: {project['description']}
published: true
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}
tags:
{tags_yaml}
editor: markdown
dateCreated: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}
---

"""

    def _get_status_class(self, status: str) -> str:
        """Map status to CSS class for styling."""
        status_map = {
            "Production Ready": "success",
            "Advanced": "info",
            "Substantial": "warning",
            "In Development": "warning",
            "Basic": "secondary"
        }
        return status_map.get(status, "secondary")

    def generate_header(self, project: dict[str, Any]) -> str:
        """Generate page header with status badge and metadata."""
        status = project.get("status", "Unknown")
        completion = project.get("completion_percentage", 0)
        tags = project.get("tags", [])

        # Create tag badges
        tag_badges = " ".join(f"`{tag}`" for tag in tags)

        # Progress bar visualization
        filled = int(completion / 10)
        empty = 10 - filled
        progress_bar = f"[{'█' * filled}{'░' * empty}] {completion}%"

        return f"""# {project['name']}

> **Status**: {status} | **Completion**: {progress_bar}
>
> {tag_badges}

{project['description']}

---

"""

    def generate_problem_statement(self, project: dict[str, Any]) -> str:
        """Generate the Problem Statement section based on project tags."""
        tags = project.get("tags", [])

        # Find matching problem template
        problem_text = PROBLEM_TEMPLATES["default"]
        for tag in tags:
            if tag in PROBLEM_TEMPLATES:
                problem_text = PROBLEM_TEMPLATES[tag]
                break

        return f"""## 🎯 Problem Statement

{problem_text}

### This Project Solves

"""

    def generate_features_section(self, project: dict[str, Any]) -> str:
        """Generate features as solution points."""
        features = project.get("features", [])
        if not features:
            return ""

        feature_list = "\n".join(f"- ✅ **{f}**" for f in features)

        return f"""{feature_list}

---

"""

    def generate_tech_stack_section(self, project: dict[str, Any]) -> str:
        """Generate Tech Stack Selection section with rationale."""
        technologies = project.get("technologies", [])
        if not technologies:
            return ""

        tech_table = "| Technology | Purpose |\n|------------|----------|\n"

        # Map technologies to purposes (intelligent defaults)
        tech_purposes = {
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
            "Kubernetes API": "Programmatic cluster access"
        }

        for tech in technologies:
            purpose = tech_purposes.get(tech, "Core technology component")
            tech_table += f"| **{tech}** | {purpose} |\n"

        return f"""## 🛠️ Tech Stack Selection

{tech_table}

### Why This Stack?

This combination was chosen to balance **developer productivity**, **operational simplicity**,
and **production reliability**. Each component integrates seamlessly while serving a specific
purpose in the overall architecture.

---

"""

    def generate_deep_dives(self, project: dict[str, Any]) -> str:
        """Generate Deep Dive educational modules based on project tags."""
        tags = project.get("tags", [])
        deep_dives = []

        # Find matching deep dive content (limit to 2 most relevant)
        matched = 0
        for tag in tags:
            if tag in TECHNOLOGY_DEEP_DIVES and matched < 2:
                dive = TECHNOLOGY_DEEP_DIVES[tag]
                benefits = "\n".join(f"- {b}" for b in dive.get("benefits", []))
                resources = "\n".join(f"- {r}" for r in dive.get("learning_resources", []))

                section = f"""### 📚 {dive['title']}

{dive['explanation']}

**Key Benefits:**
{benefits}

**Learn More:**
{resources}

"""
                deep_dives.append(section)
                matched += 1

        if not deep_dives:
            return ""

        return f"""## 🔬 Technology Deep Dives

{"".join(deep_dives)}
---

"""

    def generate_architecture_section(self, project: dict[str, Any]) -> str:
        """Generate architecture overview section."""
        return f"""## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    {project['name'][:40]:<40} │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Input Layer] ──▶ [Processing] ──▶ [Output Layer]         │
│                                                             │
│  • Data ingestion      • Core logic        • API/Events    │
│  • Validation          • Transformation    • Storage       │
│  • Authentication      • Orchestration     • Monitoring    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> 💡 **Note**: Refer to the project's `docs/architecture.md` for detailed diagrams.

---

"""

    def generate_quickstart(self, project: dict[str, Any]) -> str:
        """Generate getting started section."""
        github_path = project.get("github_path", "")
        slug = project.get("slug", "project")

        return f"""## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Required cloud CLI tools (AWS CLI, kubectl, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/samueljackson-collab/Portfolio-Project.git
cd Portfolio-Project/{github_path}

# Review the README
cat README.md

# Run with Docker Compose (if available)
docker-compose up -d
```

### Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration values

3. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```

---

"""

    def generate_implementation_walkthrough(self, project: dict[str, Any]) -> str:
        """Generate implementation walkthrough section."""
        features = project.get("features", [])[:3]  # Top 3 features

        walkthrough = """## 📖 Implementation Walkthrough

This section outlines key implementation details and patterns used in this project.

"""

        for i, feature in enumerate(features, 1):
            walkthrough += f"""### Step {i}: {feature}

Implementation approach and key considerations for this feature.

```python
# Example code pattern
def implement_{feature.lower().replace(' ', '_').replace('-', '_')[:20]}():
    \"\"\"
    Implementation skeleton for {feature}
    \"\"\"
    # Configuration
    config = load_config()

    # Core logic
    result = process(config)

    # Return or persist
    return result
```

"""

        return walkthrough + "---\n\n"

    def generate_operational_section(self, project: dict[str, Any]) -> str:
        """Generate operational wisdom section."""
        return f"""## ⚙️ Operational Guide

### Monitoring & Observability

- **Metrics**: Key metrics are exposed via Prometheus endpoints
- **Logs**: Structured JSON logging for aggregation
- **Traces**: OpenTelemetry instrumentation for distributed tracing

### Common Operations

| Task | Command |
|------|---------|
| Health check | `make health` |
| View logs | `docker-compose logs -f` |
| Run tests | `make test` |
| Deploy | `make deploy` |

### Troubleshooting

<details>
<summary>Common Issues</summary>

1. **Connection refused**: Ensure all services are running
2. **Authentication failure**: Verify credentials in `.env`
3. **Resource limits**: Check container memory/CPU allocation

</details>

---

"""

    def generate_related_projects(self, project: dict[str, Any]) -> str:
        """Generate related projects section based on shared tags."""
        current_tags = set(project.get("tags", []))
        current_id = project.get("id")

        related = []
        for p in self.projects:
            if p.get("id") == current_id:
                continue
            p_tags = set(p.get("tags", []))
            overlap = len(current_tags & p_tags)
            if overlap >= 1:
                related.append((overlap, p))

        # Sort by overlap and take top 3
        related.sort(key=lambda x: x[0], reverse=True)
        related = related[:3]

        if not related:
            return ""

        links = "\n".join(
            f"- [{p['name']}](/projects/{p['slug']}) - {p['description'][:60]}..."
            for _, p in related
        )

        return f"""## 🔗 Related Projects

{links}

---

"""

    def generate_footer(self, project: dict[str, Any]) -> str:
        """Generate page footer with metadata."""
        github_path = project.get("github_path", "")

        return f"""## 📚 Resources

- **Source Code**: [GitHub Repository](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/{github_path})
- **Documentation**: See `{github_path}/docs/` for detailed guides
- **Issues**: [Report bugs or request features](https://github.com/samueljackson-collab/Portfolio-Project/issues)

---

<small>
Last updated: {datetime.now().strftime('%Y-%m-%d')} |
Generated by Portfolio Wiki Content Generator
</small>
"""

    def generate_wiki_page(self, project: dict[str, Any]) -> str:
        """Generate complete wiki page for a project."""
        sections = [
            self.generate_frontmatter(project),
            self.generate_header(project),
            self.generate_problem_statement(project),
            self.generate_features_section(project),
            self.generate_tech_stack_section(project),
            self.generate_deep_dives(project),
            self.generate_architecture_section(project),
            self.generate_quickstart(project),
            self.generate_implementation_walkthrough(project),
            self.generate_operational_section(project),
            self.generate_related_projects(project),
            self.generate_footer(project)
        ]

        return "".join(sections)

    def generate_all_pages(self) -> dict[str, str]:
        """Generate wiki pages for all projects."""
        pages = {}
        for project in self.projects:
            slug = project.get("slug", f"project-{project.get('id', 0)}")
            content = self.generate_wiki_page(project)
            pages[slug] = content

            # Write to file
            filepath = self.output_dir / f"{slug}.md"
            filepath.write_text(content)
            print(f"Generated: {filepath}")

        return pages


# =============================================================================
# SIDEBAR CONFIGURATION GENERATOR
# =============================================================================


class WikiSidebarGenerator:
    """Generates Wiki.js sidebar/navigation configuration."""

    def __init__(self, projects: list[dict[str, Any]]):
        self.projects = projects

    def generate_sidebar_config(self) -> dict[str, Any]:
        """Generate sidebar configuration grouped by status and tags."""
        # Group projects by status
        by_status: dict[str, list[dict[str, Any]]] = {}
        for p in self.projects:
            status = p.get("status", "Other")
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(p)

        # Build sidebar structure
        sidebar = {
            "title": "Portfolio Projects",
            "items": []
        }

        # Status order
        status_order = [
            "Production Ready",
            "Advanced",
            "Substantial",
            "In Development",
            "Basic"
        ]

        for status in status_order:
            if status in by_status:
                group = {
                    "text": f"📦 {status}",
                    "collapsed": status != "Production Ready",
                    "items": [
                        {
                            "text": p["name"],
                            "link": f"/projects/{p['slug']}"
                        }
                        for p in sorted(by_status[status], key=lambda x: x["name"])
                    ]
                }
                sidebar["items"].append(group)

        return sidebar

    def generate_tags_index(self) -> dict[str, list[dict[str, Any]]]:
        """Generate tag-to-projects mapping for tag-based navigation."""
        tags_index: dict[str, list[dict[str, Any]]] = {}

        for p in self.projects:
            for tag in p.get("tags", []):
                if tag not in tags_index:
                    tags_index[tag] = []
                tags_index[tag].append({
                    "name": p["name"],
                    "slug": p["slug"],
                    "description": p["description"][:80]
                })

        return tags_index

    def generate_sidebar_yaml(self) -> str:
        """Generate YAML format sidebar for Wiki.js."""
        config = self.generate_sidebar_config()

        yaml_content = f"""# Wiki.js Sidebar Configuration
# Auto-generated by Portfolio Wiki Content Generator

navigation:
  - title: Home
    path: /
    icon: mdi-home

  - title: Projects
    icon: mdi-folder-multiple
    children:
"""

        for group in config["items"]:
            yaml_content += f"""      - title: "{group['text']}"
        children:
"""
            for item in group["items"]:
                yaml_content += f"""          - title: "{item['text']}"
            path: {item['link']}
"""

        yaml_content += """
  - title: By Technology
    icon: mdi-tag-multiple
    children:
"""

        tags = self.generate_tags_index()
        for tag in sorted(tags.keys())[:15]:  # Top 15 tags
            yaml_content += f"""      - title: "{tag}"
        path: /tags/{tag}
"""

        return yaml_content

    def generate_tags_page(self) -> str:
        """Generate a tags overview page."""
        tags = self.generate_tags_index()

        content = """---
title: Browse by Technology
description: Explore projects by technology tags
published: true
---

# 🏷️ Browse by Technology

Explore portfolio projects organized by technology and domain.

"""

        for tag in sorted(tags.keys()):
            projects = tags[tag]
            content += f"""## {tag.replace('-', ' ').title()}

"""
            for p in projects:
                content += f"- [{p['name']}](/projects/{p['slug']}) - {p['description']}\n"
            content += "\n"

        return content


# =============================================================================
# MAIN EXECUTION
# =============================================================================


def main():
    """Main entry point for wiki content generation."""
    # Load projects data
    projects_json = '''[
    {"id": 1, "name": "AWS Infrastructure Automation", "slug": "aws-infrastructure-automation", "description": "Production-ready AWS environment using Terraform, CDK, and Pulumi. Features Multi-AZ VPC, EKS cluster, and RDS PostgreSQL.", "status": "Production Ready", "completion_percentage": 100, "tags": ["aws", "terraform", "infrastructure", "eks", "rds"], "github_path": "projects/1-aws-infrastructure-automation", "technologies": ["Terraform", "AWS CDK", "Pulumi", "Python", "Bash"], "features": ["Multi-AZ VPC architecture", "Managed EKS Cluster", "RDS PostgreSQL with backups", "Automated DR drills", "Cost estimation scripts"]},
    {"id": 2, "name": "Database Migration Platform", "slug": "database-migration-platform", "description": "Zero-downtime database migration orchestrator using Change Data Capture (CDC) with Debezium and AWS DMS.", "status": "Production Ready", "completion_percentage": 100, "tags": ["database", "migration", "aws-dms", "python", "kafka"], "github_path": "projects/2-database-migration", "technologies": ["Python", "Debezium", "Kafka", "PostgreSQL", "Docker"], "features": ["Zero-downtime cutover", "Data integrity validation", "Automated rollback", "Real-time replication monitoring"]},
    {"id": 3, "name": "Kubernetes CI/CD Pipeline", "slug": "kubernetes-cicd", "description": "GitOps-driven continuous delivery pipeline combining GitHub Actions and ArgoCD for progressive deployment.", "status": "Production Ready", "completion_percentage": 100, "tags": ["kubernetes", "ci-cd", "argocd", "github-actions"], "github_path": "projects/3-kubernetes-cicd", "technologies": ["GitHub Actions", "ArgoCD", "Helm", "Kustomize", "Python"], "features": ["Blue-Green/Canary deployments", "Automated rollback on health failure", "Multi-environment support", "Container security scanning"]},
    {"id": 4, "name": "DevSecOps Pipeline", "slug": "devsecops-pipeline", "description": "Security-first CI pipeline integrating SAST, DAST, and container scanning.", "status": "In Development", "completion_percentage": 25, "tags": ["security", "devops", "ci-cd", "sast", "dast"], "github_path": "projects/4-devsecops", "technologies": ["GitHub Actions", "Trivy", "SonarQube", "OWASP ZAP"], "features": ["SBOM generation", "Automated vulnerability scanning", "Policy enforcement gates"]},
    {"id": 5, "name": "Real-time Data Streaming", "slug": "real-time-data-streaming", "description": "High-throughput event streaming pipeline using Apache Kafka and Flink with exactly-once semantics.", "status": "Production Ready", "completion_percentage": 100, "tags": ["kafka", "flink", "streaming", "python", "docker"], "github_path": "projects/5-real-time-data-streaming", "technologies": ["Apache Kafka", "Apache Flink", "Python", "Avro", "Docker"], "features": ["Exactly-once processing", "Schema Registry integration", "Flink SQL analytics", "RocksDB state backend"]},
    {"id": 6, "name": "MLOps Platform", "slug": "mlops-platform", "description": "End-to-end MLOps workflow for training, evaluating, and deploying models with drift detection.", "status": "Production Ready", "completion_percentage": 100, "tags": ["mlops", "machine-learning", "python", "mlflow", "kubernetes"], "github_path": "projects/6-mlops-platform", "technologies": ["MLflow", "Optuna", "FastAPI", "Scikit-learn", "Kubernetes"], "features": ["Automated training pipeline", "A/B testing framework", "Model drift detection", "Model serving API"]},
    {"id": 7, "name": "Serverless Data Processing", "slug": "serverless-data-processing", "description": "Event-driven analytics pipeline built on AWS serverless services (Lambda, Step Functions).", "status": "Production Ready", "completion_percentage": 100, "tags": ["serverless", "aws-lambda", "data-engineering", "step-functions"], "github_path": "projects/7-serverless-data-processing", "technologies": ["AWS SAM", "Lambda", "Step Functions", "DynamoDB", "Python"], "features": ["Workflow orchestration", "API Gateway integration", "Cognito authentication", "Automated error handling"]},
    {"id": 8, "name": "Advanced AI Chatbot", "slug": "advanced-ai-chatbot", "description": "RAG chatbot indexing portfolio assets with tool-augmented workflows.", "status": "Substantial", "completion_percentage": 55, "tags": ["ai", "chatbot", "llm", "rag", "fastapi"], "github_path": "projects/8-advanced-ai-chatbot", "technologies": ["Python", "FastAPI", "LangChain", "Vector DB"], "features": ["Retrieval-Augmented Generation", "WebSocket streaming", "Context awareness"]},
    {"id": 9, "name": "Multi-Region Disaster Recovery", "slug": "multi-region-disaster-recovery", "description": "Resilient architecture with automated failover between AWS regions.", "status": "Production Ready", "completion_percentage": 100, "tags": ["aws", "dr", "reliability", "terraform", "automation"], "github_path": "projects/9-multi-region-disaster-recovery", "technologies": ["Terraform", "AWS Route53", "AWS RDS Global", "Python"], "features": ["Automated failover scripts", "Backup verification", "Cross-region replication", "RTO/RPO validation"]},
    {"id": 10, "name": "Blockchain Smart Contract Platform", "slug": "blockchain-smart-contract-platform", "description": "DeFi protocol with modular smart contracts for staking and governance.", "status": "Advanced", "completion_percentage": 70, "tags": ["blockchain", "solidity", "smart-contracts", "web3"], "github_path": "projects/10-blockchain-smart-contract-platform", "technologies": ["Solidity", "Hardhat", "TypeScript", "Ethers.js"], "features": ["Staking logic", "Governance tokens", "Automated testing", "Security analysis"]},
    {"id": 11, "name": "IoT Data Analytics", "slug": "iot-data-analytics", "description": "Edge-to-cloud ingestion stack with MQTT telemetry and anomaly detection.", "status": "Production Ready", "completion_percentage": 100, "tags": ["iot", "analytics", "timescaledb", "mqtt", "machine-learning"], "github_path": "projects/11-iot-data-analytics", "technologies": ["AWS IoT Core", "Python", "TimescaleDB", "MQTT", "Scikit-learn"], "features": ["Device provisioning automation", "ML-based anomaly detection", "Real-time telemetry", "Infrastructure as Code"]},
    {"id": 12, "name": "Quantum Computing Integration", "slug": "quantum-computing-integration", "description": "Hybrid quantum-classical workloads using Qiskit.", "status": "Substantial", "completion_percentage": 50, "tags": ["quantum-computing", "qiskit", "research", "python"], "github_path": "projects/12-quantum-computing", "technologies": ["Qiskit", "Python", "AWS Batch"], "features": ["Variational Quantum Eigensolver", "Hybrid workflow orchestration"]},
    {"id": 13, "name": "Advanced Cybersecurity Platform", "slug": "advanced-cybersecurity-platform", "description": "SOAR engine consolidating SIEM alerts with automated playbooks.", "status": "Substantial", "completion_percentage": 45, "tags": ["cybersecurity", "soc", "siem", "soar", "python"], "github_path": "projects/13-advanced-cybersecurity", "technologies": ["Python", "ELK Stack", "VirusTotal API"], "features": ["Alert aggregation", "Automated response playbooks", "Threat intelligence enrichment"]},
    {"id": 14, "name": "Edge AI Inference Platform", "slug": "edge-ai-inference-platform", "description": "Containerized ONNX Runtime microservice for edge devices.", "status": "Substantial", "completion_percentage": 50, "tags": ["edge-ai", "inference", "onnx", "iot"], "github_path": "projects/14-edge-ai-inference", "technologies": ["ONNX Runtime", "Python", "Docker", "Azure IoT Edge"], "features": ["Low-latency inference", "Model optimization", "Containerized deployment"]},
    {"id": 15, "name": "Real-time Collaboration Platform", "slug": "real-time-collaboration-platform", "description": "Operational Transform collaboration server with CRDT backup.", "status": "Substantial", "completion_percentage": 50, "tags": ["websockets", "real-time", "collaboration", "crdt"], "github_path": "projects/15-real-time-collaboration", "technologies": ["Python", "WebSockets", "Redis"], "features": ["Real-time document editing", "Conflict resolution", "Presence tracking"]},
    {"id": 16, "name": "Advanced Data Lake", "slug": "advanced-data-lake", "description": "Medallion architecture with Delta Lake and structured streaming.", "status": "Substantial", "completion_percentage": 55, "tags": ["data-lake", "glue", "athena", "spark"], "github_path": "projects/16-advanced-data-lake", "technologies": ["Databricks", "Delta Lake", "Python", "SQL"], "features": ["Bronze/Silver/Gold layers", "ACID transactions", "Stream ingestion"]},
    {"id": 17, "name": "Multi-Cloud Service Mesh", "slug": "multi-cloud-service-mesh", "description": "Istio service mesh spanning AWS and GKE clusters.", "status": "Basic", "completion_percentage": 40, "tags": ["service-mesh", "istio", "multi-cloud", "kubernetes"], "github_path": "projects/17-multi-cloud-service-mesh", "technologies": ["Istio", "Kubernetes", "Consul"], "features": ["Cross-cluster communication", "mTLS enforcement", "Traffic splitting"]},
    {"id": 18, "name": "GPU-Accelerated Computing", "slug": "gpu-accelerated-computing", "description": "CUDA-based risk simulation engine with Dask.", "status": "Substantial", "completion_percentage": 45, "tags": ["gpu", "cuda", "hpc", "python"], "github_path": "projects/18-gpu-accelerated-computing", "technologies": ["CUDA", "Python", "Dask", "Nvidia Drivers"], "features": ["Monte Carlo simulations", "Parallel processing", "Performance benchmarking"]},
    {"id": 19, "name": "Advanced Kubernetes Operators", "slug": "advanced-kubernetes-operators", "description": "Custom resource operator built with Kopf.", "status": "Substantial", "completion_percentage": 50, "tags": ["kubernetes", "operators", "python", "kopf"], "github_path": "projects/19-advanced-kubernetes-operators", "technologies": ["Python", "Kopf", "Kubernetes API"], "features": ["Custom Resource Definitions", "Automated reconciliation", "State management"]},
    {"id": 20, "name": "Blockchain Oracle Service", "slug": "blockchain-oracle-service", "description": "Chainlink-compatible external adapter.", "status": "Substantial", "completion_percentage": 50, "tags": ["blockchain", "oracle", "chainlink", "solidity"], "github_path": "projects/20-blockchain-oracle-service", "technologies": ["Node.js", "Solidity", "Docker"], "features": ["Off-chain data fetching", "Cryptographic signing", "Smart contract integration"]},
    {"id": 21, "name": "Quantum-Safe Cryptography", "slug": "quantum-safe-cryptography", "description": "Hybrid key exchange service using Kyber KEM.", "status": "Substantial", "completion_percentage": 50, "tags": ["cryptography", "post-quantum", "security", "python"], "github_path": "projects/21-quantum-safe-cryptography", "technologies": ["Python", "Kyber", "Cryptography Libraries"], "features": ["Post-quantum key exchange", "Hybrid encryption scheme", "NIST-standard algorithms"]},
    {"id": 22, "name": "Autonomous DevOps Platform", "slug": "autonomous-devops-platform", "description": "Event-driven automation layer for self-healing infrastructure.", "status": "Basic", "completion_percentage": 40, "tags": ["devops", "automation", "ai", "python"], "github_path": "projects/22-autonomous-devops-platform", "technologies": ["Python", "Prometheus API", "Kubernetes API"], "features": ["Incident detection", "Automated remediation", "Runbook automation"]},
    {"id": 23, "name": "Advanced Monitoring & Observability", "slug": "advanced-monitoring-observability", "description": "Unified observability stack with Prometheus, Tempo, Loki, and Grafana.", "status": "Production Ready", "completion_percentage": 100, "tags": ["monitoring", "observability", "grafana", "prometheus"], "github_path": "projects/23-advanced-monitoring", "technologies": ["Prometheus", "Grafana", "Loki", "Thanos", "Python"], "features": ["Custom application exporter", "Multi-channel alerting", "Long-term storage", "SLO tracking"]},
    {"id": 24, "name": "Portfolio Report Generator", "slug": "report-generator", "description": "Automated report generation system using Jinja2 and WeasyPrint.", "status": "Production Ready", "completion_percentage": 100, "tags": ["automation", "reporting", "python"], "github_path": "projects/24-report-generator", "technologies": ["Python", "Jinja2", "WeasyPrint", "APScheduler"], "features": ["Scheduled generation", "Email delivery", "Historical trending", "PDF/HTML output"]},
    {"id": 25, "name": "Portfolio Website", "slug": "portfolio-website", "description": "Static documentation portal generated with VitePress.", "status": "Production Ready", "completion_percentage": 100, "tags": ["web", "vitepress", "documentation", "vue"], "github_path": "projects/25-portfolio-website", "technologies": ["VitePress", "Vue.js", "Node.js", "GitHub Pages"], "features": ["Project showcase", "Automated deployment", "Responsive design", "Search functionality"]}
    ]'''

    projects = json.loads(projects_json)

    # Create output directory
    output_dir = Path("wiki/projects")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate wiki pages
    print("=" * 60)
    print("Wiki.js Content Generator")
    print("=" * 60)

    generator = WikiContentGenerator(projects, str(output_dir))
    pages = generator.generate_all_pages()
    print(f"\nGenerated {len(pages)} wiki pages")

    # Generate sidebar configuration
    sidebar_gen = WikiSidebarGenerator(projects)

    sidebar_path = Path("wiki/config/sidebar.yaml")
    sidebar_path.parent.mkdir(parents=True, exist_ok=True)
    sidebar_path.write_text(sidebar_gen.generate_sidebar_yaml())
    print(f"Generated: {sidebar_path}")

    # Generate tags page
    tags_path = Path("wiki/tags.md")
    tags_path.write_text(sidebar_gen.generate_tags_page())
    print(f"Generated: {tags_path}")

    # Generate JSON config for programmatic use
    config_json = {
        "sidebar": sidebar_gen.generate_sidebar_config(),
        "tags": sidebar_gen.generate_tags_index(),
        "generated_at": datetime.now().isoformat(),
        "total_projects": len(projects)
    }

    config_path = Path("wiki/config/wiki_config.json")
    config_path.write_text(json.dumps(config_json, indent=2))
    print(f"Generated: {config_path}")

    print("\n" + "=" * 60)
    print("Generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
