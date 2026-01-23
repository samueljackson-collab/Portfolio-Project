#!/usr/bin/env python3
"""
Enhanced Wiki.js Content Generator v3

Generates comprehensive, professional wiki documentation with:
- Complete problem statements with business context
- Full technology deep dives with real code examples
- Project-specific implementation guides
- Detailed architecture explanations
- Best practices and anti-patterns
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
# PROJECT DATA WITH CATEGORIES
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
    "Terraform": "Infrastructure as Code - declarative, version-controlled resource management across cloud providers",
    "AWS CDK": "Type-safe infrastructure definitions using TypeScript/Python with compile-time validation",
    "Pulumi": "Multi-language IaC supporting Python, TypeScript, Go with real programming constructs",
    "Python": "Primary automation language for scripts, data processing, and ML pipelines",
    "Bash": "Shell scripting for system integration and CI/CD pipeline steps",
    "Docker": "Container packaging ensuring consistent runtime environments across all stages",
    "GitHub Actions": "Native CI/CD automation with deep GitHub integration and marketplace ecosystem",
    "ArgoCD": "GitOps controller continuously syncing Kubernetes state from Git repositories",
    "Helm": "Kubernetes package manager with templating for environment-specific configurations",
    "Kustomize": "Native Kubernetes configuration customization without templating",
    "Apache Kafka": "Distributed event streaming with persistence, replay, and exactly-once semantics",
    "Apache Flink": "Stateful stream processing with event-time semantics and checkpointing",
    "MLflow": "ML lifecycle management: experiment tracking, model registry, deployment",
    "FastAPI": "Modern Python API framework with automatic OpenAPI docs and async support",
    "Prometheus": "Pull-based metrics collection with powerful PromQL query language",
    "Grafana": "Unified visualization platform connecting metrics, logs, and traces",
    "Loki": "Log aggregation designed for efficiency with label-based indexing",
    "AWS SAM": "Serverless application framework simplifying Lambda development and deployment",
    "Lambda": "Event-driven serverless compute with automatic scaling and pay-per-use",
    "Step Functions": "Visual workflow orchestration with error handling and state management",
    "DynamoDB": "Serverless NoSQL with single-digit millisecond latency at any scale",
    "Solidity": "Smart contract language for Ethereum and EVM-compatible blockchains",
    "Hardhat": "Ethereum development environment with testing, debugging, and deployment",
    "Ethers.js": "Complete Ethereum library for wallet and contract interaction",
    "TypeScript": "Type-safe JavaScript enabling better tooling and refactoring",
    "AWS IoT Core": "Managed MQTT broker handling billions of messages from IoT devices",
    "TimescaleDB": "PostgreSQL extension optimized for time-series data at scale",
    "MQTT": "Lightweight pub/sub protocol designed for constrained IoT devices",
    "Scikit-learn": "Production-ready ML algorithms with consistent API",
    "Qiskit": "Open-source quantum computing SDK for algorithm development",
    "ELK Stack": "Elasticsearch, Logstash, Kibana for log aggregation and analysis",
    "ONNX Runtime": "Cross-platform ML inference optimized for production deployment",
    "Azure IoT Edge": "Edge runtime for running containerized workloads on devices",
    "Redis": "In-memory data store for caching, pub/sub, and real-time features",
    "WebSockets": "Full-duplex communication enabling real-time bidirectional data flow",
    "Databricks": "Unified analytics platform combining data engineering and data science",
    "Delta Lake": "ACID transactions and time-travel for data lakes on object storage",
    "Istio": "Service mesh providing mTLS, traffic management, and observability",
    "Consul": "Service discovery and configuration across multi-cloud environments",
    "CUDA": "NVIDIA parallel computing platform for GPU-accelerated workloads",
    "Dask": "Parallel computing library scaling Python analytics to clusters",
    "Kopf": "Python framework for building Kubernetes operators with minimal boilerplate",
    "Node.js": "JavaScript runtime for backend services and blockchain tooling",
    "Thanos": "Highly available Prometheus with long-term storage and global querying",
    "Jinja2": "Python templating engine for generating configuration and reports",
    "WeasyPrint": "HTML/CSS to PDF conversion for professional document generation",
    "APScheduler": "Python task scheduling for cron-like job execution",
    "VitePress": "Vue-powered static site generator optimized for documentation",
    "Vue.js": "Progressive JavaScript framework for building user interfaces",
    "LangChain": "Framework for building LLM applications with chains and agents",
    "Vector DB": "Specialized database for similarity search on embeddings",
    "Debezium": "CDC platform capturing database changes as event streams",
    "PostgreSQL": "Enterprise-grade relational database with extensibility",
    "Trivy": "Comprehensive vulnerability scanner for containers, IaC, and code",
    "SonarQube": "Code quality platform detecting bugs, vulnerabilities, and smells",
    "OWASP ZAP": "Dynamic application security testing for finding vulnerabilities",
    "Avro": "Compact binary serialization with schema evolution support",
    "Optuna": "Hyperparameter optimization framework with pruning strategies",
    "Kubernetes": "Container orchestration platform for automated deployment and scaling",
    "Kubernetes API": "Programmatic access to cluster resources for automation",
    "SQL": "Declarative language for relational data querying and manipulation",
    "Nvidia Drivers": "GPU drivers enabling CUDA workloads on compatible hardware",
    "Kyber": "NIST-selected post-quantum key encapsulation mechanism",
    "Cryptography Libraries": "Primitives for encryption, hashing, and key management",
    "VirusTotal API": "Malware analysis service aggregating 70+ antivirus engines",
    "AWS Route53": "Scalable DNS with health checks and traffic routing policies",
    "AWS RDS Global": "Multi-region database replication with sub-second failover"
}

# =============================================================================
# PROJECT-SPECIFIC IMPLEMENTATION EXAMPLES
# =============================================================================

PROJECT_IMPLEMENTATIONS = {
    "infrastructure": {
        "vpc": '''```hcl
# Multi-AZ VPC with Public and Private Subnets
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "production-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = false  # One per AZ for HA
  one_nat_gateway_per_az = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  # VPC Flow Logs for network monitoring
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_cloudwatch_iam_role  = true

  tags = {
    Environment = "production"
    Terraform   = "true"
    Project     = "aws-infrastructure-automation"
  }
}

# EKS Cluster with Managed Node Groups
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "production-cluster"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Enable IRSA for pod-level IAM
  enable_irsa = true

  eks_managed_node_groups = {
    general = {
      min_size     = 2
      max_size     = 10
      desired_size = 3

      instance_types = ["m5.large"]
      capacity_type  = "ON_DEMAND"

      labels = {
        workload = "general"
      }
    }
  }

  # Cluster access configuration
  cluster_endpoint_public_access = true
  cluster_endpoint_private_access = true
}
```''',
        "eks": '''```python
# EKS Cluster Health Check and Node Management
import boto3
from kubernetes import client, config
from dataclasses import dataclass
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NodeHealth:
    name: str
    status: str
    cpu_capacity: str
    memory_capacity: str
    pods_running: int
    conditions: dict

class EKSManager:
    """Manage EKS cluster operations and health monitoring."""

    def __init__(self, cluster_name: str, region: str = "us-east-1"):
        self.cluster_name = cluster_name
        self.region = region
        self.eks_client = boto3.client("eks", region_name=region)

        # Load kubeconfig for the cluster
        self._configure_kubernetes()

    def _configure_kubernetes(self):
        """Configure kubectl to use EKS cluster."""
        cluster_info = self.eks_client.describe_cluster(name=self.cluster_name)
        cluster = cluster_info["cluster"]

        # Write kubeconfig
        config.load_kube_config()
        self.k8s_core = client.CoreV1Api()
        self.k8s_apps = client.AppsV1Api()

    def get_node_health(self) -> List[NodeHealth]:
        """Get health status of all cluster nodes."""
        nodes = self.k8s_core.list_node()
        health_reports = []

        for node in nodes.items:
            # Parse node conditions
            conditions = {
                c.type: c.status
                for c in node.status.conditions
            }

            # Count pods on this node
            pods = self.k8s_core.list_pod_for_all_namespaces(
                field_selector=f"spec.nodeName={node.metadata.name}"
            )

            health = NodeHealth(
                name=node.metadata.name,
                status="Ready" if conditions.get("Ready") == "True" else "NotReady",
                cpu_capacity=node.status.capacity.get("cpu", "unknown"),
                memory_capacity=node.status.capacity.get("memory", "unknown"),
                pods_running=len([p for p in pods.items if p.status.phase == "Running"]),
                conditions=conditions
            )
            health_reports.append(health)

        return health_reports

    def cordon_node(self, node_name: str) -> bool:
        """Mark node as unschedulable for maintenance."""
        try:
            body = {"spec": {"unschedulable": True}}
            self.k8s_core.patch_node(node_name, body)
            logger.info(f"Node {node_name} cordoned successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to cordon node: {e}")
            return False

    def drain_node(self, node_name: str, grace_period: int = 30) -> bool:
        """Evict all pods from a node for maintenance."""
        pods = self.k8s_core.list_pod_for_all_namespaces(
            field_selector=f"spec.nodeName={node_name}"
        )

        for pod in pods.items:
            if pod.metadata.namespace in ["kube-system"]:
                continue  # Skip system pods

            try:
                eviction = client.V1Eviction(
                    metadata=client.V1ObjectMeta(
                        name=pod.metadata.name,
                        namespace=pod.metadata.namespace
                    ),
                    delete_options=client.V1DeleteOptions(
                        grace_period_seconds=grace_period
                    )
                )
                self.k8s_core.create_namespaced_pod_eviction(
                    pod.metadata.name,
                    pod.metadata.namespace,
                    eviction
                )
                logger.info(f"Evicted pod {pod.metadata.name}")
            except Exception as e:
                logger.warning(f"Could not evict {pod.metadata.name}: {e}")

        return True

# Usage example
if __name__ == "__main__":
    manager = EKSManager("production-cluster")

    # Check cluster health
    for node in manager.get_node_health():
        print(f"Node: {node.name}")
        print(f"  Status: {node.status}")
        print(f"  CPU: {node.cpu_capacity}, Memory: {node.memory_capacity}")
        print(f"  Running Pods: {node.pods_running}")
```''',
        "rds": '''```hcl
# RDS PostgreSQL with Multi-AZ and Automated Backups
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "production-postgres"

  engine               = "postgres"
  engine_version       = "15.4"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = "db.r6g.large"

  allocated_storage     = 100
  max_allocated_storage = 500  # Autoscaling

  db_name  = "application"
  username = "admin"
  port     = 5432

  # High availability
  multi_az = true

  # Network
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [module.security_group_rds.security_group_id]

  # Backups
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  # Encryption
  storage_encrypted = true
  kms_key_id       = aws_kms_key.rds.arn

  # Performance Insights
  performance_insights_enabled          = true
  performance_insights_retention_period = 7

  # Enhanced monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  # Parameter group for tuning
  parameters = [
    {
      name  = "shared_preload_libraries"
      value = "pg_stat_statements"
    },
    {
      name  = "log_min_duration_statement"
      value = "1000"  # Log queries > 1 second
    }
  ]

  tags = {
    Environment = "production"
    Backup      = "required"
  }
}

# Automated backup verification
resource "aws_lambda_function" "backup_verify" {
  filename         = "backup_verify.zip"
  function_name    = "rds-backup-verification"
  role             = aws_iam_role.backup_verify.arn
  handler          = "index.handler"
  runtime          = "python3.11"
  timeout          = 300

  environment {
    variables = {
      DB_IDENTIFIER = module.rds.db_instance_identifier
      SNS_TOPIC_ARN = aws_sns_topic.alerts.arn
    }
  }
}
```'''
    },
    "migration": {
        "cdc": '''```python
# Zero-Downtime Database Migration with CDC
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from confluent_kafka import Consumer, Producer, KafkaError
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChangeEvent:
    """Represents a database change captured by Debezium."""
    operation: str  # 'c' (create), 'u' (update), 'd' (delete)
    table: str
    before: Optional[Dict[str, Any]]
    after: Optional[Dict[str, Any]]
    timestamp: datetime
    transaction_id: str

class CDCMigrator:
    """
    Handles zero-downtime database migration using CDC.

    Flow:
    1. Initial snapshot of source database
    2. Continuous CDC replication during migration
    3. Dual-write verification
    4. Traffic cutover with instant rollback capability
    """

    def __init__(self, source_config: dict, target_config: dict, kafka_config: dict):
        self.source_conn = psycopg2.connect(**source_config)
        self.target_conn = psycopg2.connect(**target_config)

        self.consumer = Consumer({
            'bootstrap.servers': kafka_config['bootstrap_servers'],
            'group.id': 'migration-consumer',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })

        self.producer = Producer({
            'bootstrap.servers': kafka_config['bootstrap_servers'],
            'acks': 'all'
        })

        self.metrics = {
            'events_processed': 0,
            'events_failed': 0,
            'lag_ms': 0
        }

    def start_initial_snapshot(self, tables: list[str]) -> None:
        """Perform initial data snapshot to target database."""
        logger.info("Starting initial snapshot...")

        for table in tables:
            with self.source_conn.cursor(cursor_factory=RealDictCursor) as src_cur:
                with self.target_conn.cursor() as tgt_cur:
                    # Get row count for progress tracking
                    src_cur.execute(f"SELECT COUNT(*) FROM {table}")
                    total_rows = src_cur.fetchone()['count']

                    # Stream data in batches
                    src_cur.execute(f"SELECT * FROM {table}")
                    batch_size = 1000
                    processed = 0

                    while True:
                        rows = src_cur.fetchmany(batch_size)
                        if not rows:
                            break

                        # Insert batch into target
                        columns = rows[0].keys()
                        values_template = ','.join(['%s'] * len(columns))
                        insert_sql = f"""
                            INSERT INTO {table} ({','.join(columns)})
                            VALUES ({values_template})
                            ON CONFLICT DO NOTHING
                        """

                        for row in rows:
                            tgt_cur.execute(insert_sql, list(row.values()))

                        self.target_conn.commit()
                        processed += len(rows)
                        logger.info(f"Snapshot progress: {table} - {processed}/{total_rows}")

        logger.info("Initial snapshot completed")

    def process_cdc_events(self, topic: str) -> None:
        """Process CDC events from Kafka and apply to target."""
        self.consumer.subscribe([topic])
        logger.info(f"Subscribed to CDC topic: {topic}")

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

                # Parse Debezium event
                event = self._parse_debezium_event(msg.value())

                # Apply to target database
                success = self._apply_change(event)

                if success:
                    self.consumer.commit(asynchronous=False)
                    self.metrics['events_processed'] += 1
                else:
                    self.metrics['events_failed'] += 1
                    # Send to dead letter queue
                    self._send_to_dlq(msg.value())

        except KeyboardInterrupt:
            logger.info("Shutting down CDC processor")
        finally:
            self.consumer.close()

    def _parse_debezium_event(self, raw_event: bytes) -> ChangeEvent:
        """Parse Debezium CDC event."""
        data = json.loads(raw_event.decode('utf-8'))
        payload = data['payload']

        return ChangeEvent(
            operation=payload['op'],
            table=payload['source']['table'],
            before=payload.get('before'),
            after=payload.get('after'),
            timestamp=datetime.fromtimestamp(payload['ts_ms'] / 1000),
            transaction_id=str(payload['source']['txId'])
        )

    def _apply_change(self, event: ChangeEvent) -> bool:
        """Apply a single change event to target database."""
        try:
            with self.target_conn.cursor() as cur:
                if event.operation == 'c':  # INSERT
                    columns = event.after.keys()
                    values = [event.after[c] for c in columns]
                    sql = f"""
                        INSERT INTO {event.table} ({','.join(columns)})
                        VALUES ({','.join(['%s'] * len(columns))})
                    """
                    cur.execute(sql, values)

                elif event.operation == 'u':  # UPDATE
                    set_clause = ', '.join([f"{k} = %s" for k in event.after.keys()])
                    sql = f"UPDATE {event.table} SET {set_clause} WHERE id = %s"
                    values = list(event.after.values()) + [event.after['id']]
                    cur.execute(sql, values)

                elif event.operation == 'd':  # DELETE
                    sql = f"DELETE FROM {event.table} WHERE id = %s"
                    cur.execute(sql, [event.before['id']])

                self.target_conn.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to apply change: {e}")
            self.target_conn.rollback()
            return False

    def validate_data_integrity(self, table: str) -> dict:
        """Compare row counts and checksums between source and target."""
        with self.source_conn.cursor() as src_cur:
            with self.target_conn.cursor() as tgt_cur:
                # Row count comparison
                src_cur.execute(f"SELECT COUNT(*) FROM {table}")
                src_count = src_cur.fetchone()[0]

                tgt_cur.execute(f"SELECT COUNT(*) FROM {table}")
                tgt_count = tgt_cur.fetchone()[0]

                # Checksum comparison (sample)
                src_cur.execute(f"""
                    SELECT MD5(CAST(ARRAY_AGG(t.* ORDER BY id) AS TEXT))
                    FROM (SELECT * FROM {table} ORDER BY id LIMIT 1000) t
                """)
                src_checksum = src_cur.fetchone()[0]

                tgt_cur.execute(f"""
                    SELECT MD5(CAST(ARRAY_AGG(t.* ORDER BY id) AS TEXT))
                    FROM (SELECT * FROM {table} ORDER BY id LIMIT 1000) t
                """)
                tgt_checksum = tgt_cur.fetchone()[0]

                return {
                    'table': table,
                    'source_count': src_count,
                    'target_count': tgt_count,
                    'counts_match': src_count == tgt_count,
                    'checksums_match': src_checksum == tgt_checksum,
                    'validated_at': datetime.utcnow().isoformat()
                }
```'''
    },
    "ci-cd": {
        "pipeline": '''```yaml
# Complete GitOps CI/CD Pipeline
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ============================================
  # Stage 1: Build and Test
  # ============================================
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          ruff check .
          mypy src/

      - name: Run tests with coverage
        run: |
          pytest tests/ \\
            --cov=src \\
            --cov-report=xml \\
            --cov-report=term-missing \\
            --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
          fail_ci_if_error: true

  # ============================================
  # Stage 2: Security Scanning
  # ============================================
  security:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

      - name: Run Semgrep SAST
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets

  # ============================================
  # Stage 3: Build and Push Container
  # ============================================
  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    permissions:
      contents: read
      packages: write
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      digest: ${{ steps.build.outputs.digest }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ steps.build.outputs.digest }}

  # ============================================
  # Stage 4: Deploy to Staging
  # ============================================
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    environment: staging
    if: github.ref == 'refs/heads/develop'

    steps:
      - uses: actions/checkout@v4

      - name: Update Kubernetes manifests
        run: |
          cd k8s/overlays/staging
          kustomize edit set image app=${{ needs.build.outputs.image-tag }}

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Deploy to staging: ${{ github.sha }}"
          git push

      # ArgoCD will auto-sync from Git

  # ============================================
  # Stage 5: Deploy to Production
  # ============================================
  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    environment: production
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Update Kubernetes manifests
        run: |
          cd k8s/overlays/production
          kustomize edit set image app=${{ needs.build.outputs.image-tag }}

      - name: Create canary deployment
        run: |
          # Deploy to 10% of traffic initially
          kubectl apply -f k8s/canary/

      - name: Monitor canary metrics
        run: |
          # Check error rate for 5 minutes
          ./scripts/canary-analysis.sh --threshold 0.01 --duration 300

      - name: Promote to full deployment
        run: |
          kubectl apply -f k8s/overlays/production/
```''',
        "argocd": '''```yaml
# ArgoCD Application with Progressive Delivery
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: production-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default

  source:
    repoURL: https://github.com/org/app-manifests.git
    targetRevision: main
    path: k8s/overlays/production

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

---
# Argo Rollout for Canary Deployments
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: app-rollout
  namespace: production
spec:
  replicas: 10
  selector:
    matchLabels:
      app: production-app
  template:
    metadata:
      labels:
        app: production-app
    spec:
      containers:
        - name: app
          image: app:latest
          ports:
            - containerPort: 8080
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5

  strategy:
    canary:
      steps:
        - setWeight: 10
        - pause: {duration: 5m}
        - setWeight: 30
        - pause: {duration: 5m}
        - setWeight: 50
        - pause: {duration: 10m}
        - setWeight: 100

      analysis:
        templates:
          - templateName: success-rate
        startingStep: 1
        args:
          - name: service-name
            value: production-app

      trafficRouting:
        istio:
          virtualService:
            name: app-vsvc
            routes:
              - primary

---
# Analysis Template for Canary Validation
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
    - name: service-name
  metrics:
    - name: success-rate
      interval: 1m
      successCondition: result[0] >= 0.99
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{
              service="{{args.service-name}}",
              status=~"2.."
            }[5m])) /
            sum(rate(http_requests_total{
              service="{{args.service-name}}"
            }[5m]))
```'''
    }
}


class ProfessionalWikiGenerator:
    """Generates professional, comprehensive wiki documentation."""

    def __init__(self, projects: list[dict], output_dir: str = "wiki"):
        self.projects = projects
        self.output_dir = Path(output_dir)

    def generate_page(self, project: dict) -> str:
        """Generate a complete professional wiki page."""
        sections = [
            self._frontmatter(project),
            self._header(project),
            self._toc(),
            self._problem_statement(project),
            self._learning_objectives(project),
            self._architecture(project),
            self._tech_stack(project),
            self._deep_dives(project),
            self._implementation_guide(project),
            self._best_practices(project),
            self._quick_start(project),
            self._operational_guide(project),
            self._real_world_scenarios(project),
            self._related_projects(project),
            self._resources(project)
        ]
        return "\n".join(sections)

    def _frontmatter(self, p: dict) -> str:
        tags = "\n".join(f"  - {t}" for t in p.get("tags", []))
        return f"""---
title: "{p['name']}"
description: "{p['description']}"
published: true
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}
tags:
{tags}
editor: markdown
dateCreated: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}
---
"""

    def _header(self, p: dict) -> str:
        completion = p.get("completion_percentage", 0)
        filled = int(completion / 10)
        bar = f"{'█' * filled}{'░' * (10 - filled)}"
        tags = " ".join(f"`{t}`" for t in p.get("tags", []))

        return f"""
# {p['name']}

> **Status**: {p.get('status', 'Unknown')} | **Completion**: [{bar}] {completion}%
>
> {tags}

{p['description']}

---
"""

    def _toc(self) -> str:
        return """
## 📋 Table of Contents

1. [Problem Statement](#-problem-statement) - Why this project exists
2. [Learning Objectives](#-learning-objectives) - What you'll learn
3. [Architecture](#-architecture) - System design and components
4. [Tech Stack](#-tech-stack) - Technologies and their purposes
5. [Technology Deep Dives](#-technology-deep-dives) - In-depth explanations
6. [Implementation Guide](#-implementation-guide) - How to build it
7. [Best Practices](#-best-practices) - Do's and don'ts
8. [Quick Start](#-quick-start) - Get running in minutes
9. [Operational Guide](#-operational-guide) - Day-2 operations
10. [Real-World Scenarios](#-real-world-scenarios) - Practical applications

---
"""

    def _problem_statement(self, p: dict) -> str:
        category = p.get("category", "infrastructure")
        problem = PROBLEM_STATEMENTS.get(category, PROBLEM_STATEMENTS.get("infrastructure"))

        features = "\n".join(f"- ✅ **{f}**" for f in p.get("features", []))

        return f"""
## 🎯 Problem Statement

### {problem['title']}

{problem['context']}

{problem['impact']}

### How This Project Solves It

{problem['solution_approach']}

### Key Capabilities Delivered

{features}

---
"""

    def _learning_objectives(self, p: dict) -> str:
        category = p.get("category", "infrastructure")
        objectives = LEARNING_OBJECTIVES.get(category, [])

        if not objectives:
            objectives = [
                "Understand the core problem domain and challenges",
                "Design and implement production-grade solutions",
                "Apply industry best practices and patterns",
                "Build confidence through hands-on implementation",
                "Develop operational skills for day-2 management"
            ]

        obj_list = "\n".join(f"   {i}. {obj}" for i, obj in enumerate(objectives, 1))

        return f"""
## 🎓 Learning Objectives

By studying and implementing this project, you will:

{obj_list}

**Prerequisites:**
- Basic understanding of cloud services (AWS/GCP/Azure)
- Familiarity with containerization (Docker)
- Command-line proficiency (Bash/Linux)
- Version control with Git

**Estimated Learning Time:** 15-25 hours for full implementation

---
"""

    def _architecture(self, p: dict) -> str:
        category = p.get("category", "infrastructure")
        arch = ARCHITECTURE_COMPONENTS.get(category, {})

        name = p['name'][:50]

        content = f"""
## 🏗️ Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         {name:<50}   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌───────────────┐    ┌─────────────────┐    ┌───────────────────┐   │
│   │    INPUT      │    │   PROCESSING    │    │     OUTPUT        │   │
│   │               │───▶│                 │───▶│                   │   │
│   │ • API Gateway │    │ • Business Logic│    │ • Response/Events │   │
│   │ • Event Queue │    │ • Validation    │    │ • Persistence     │   │
│   │ • File Upload │    │ • Transformation│    │ • Notifications   │   │
│   └───────────────┘    └─────────────────┘    └───────────────────┘   │
│           │                    │                       │              │
│           └────────────────────┴───────────────────────┘              │
│                                │                                       │
│                    ┌───────────┴───────────┐                          │
│                    │    INFRASTRUCTURE     │                          │
│                    │ • Compute (EKS/Lambda)│                          │
│                    │ • Storage (S3/RDS)    │                          │
│                    │ • Network (VPC/ALB)   │                          │
│                    │ • Security (IAM/KMS)  │                          │
│                    └───────────────────────┘                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

"""

        if arch.get("layers"):
            content += "### Component Breakdown\n\n"
            for layer in arch["layers"]:
                components = ", ".join(layer["components"])
                content += f"**{layer['name']}**\n"
                content += f"- {components}\n\n"

        if arch.get("data_flow"):
            content += f"### Data Flow\n\n`{arch['data_flow']}`\n\n"

        content += """### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Multi-AZ Deployment | Ensures high availability during AZ failures |
| Managed Services | Reduces operational burden, focus on business logic |
| Infrastructure as Code | Reproducibility, version control, audit trail |
| GitOps Workflow | Single source of truth, automated reconciliation |

---
"""
        return content

    def _tech_stack(self, p: dict) -> str:
        technologies = p.get("technologies", [])

        rows = "\n".join(
            f"| **{t}** | {TECH_PURPOSES.get(t, 'Core component')} |"
            for t in technologies
        )

        return f"""
## 🛠️ Tech Stack

### Technologies Used

| Technology | Purpose & Rationale |
|------------|---------------------|
{rows}

### Why This Combination?

This stack was carefully selected based on:

1. **Production Maturity** - All components are battle-tested at scale
2. **Community & Ecosystem** - Strong documentation, plugins, and support
3. **Integration** - Technologies work together with established patterns
4. **Scalability** - Architecture supports growth without major refactoring
5. **Operability** - Built-in observability and debugging capabilities
6. **Cost Efficiency** - Balance of capability and cloud spend optimization

### Alternative Considerations

| Current Choice | Alternatives Considered | Why Current Was Chosen |
|---------------|------------------------|------------------------|
| Terraform | CloudFormation, Pulumi | Provider-agnostic, mature ecosystem |
| Kubernetes | ECS, Nomad | Industry standard, portable |
| PostgreSQL | MySQL, MongoDB | ACID compliance, JSON support |

---
"""

    def _deep_dives(self, p: dict) -> str:
        tags = p.get("tags", [])
        content = "## 🔬 Technology Deep Dives\n\n"

        matched = 0
        for tag in tags:
            if tag in TECHNOLOGY_DEEP_DIVES and matched < 2:
                dive = TECHNOLOGY_DEEP_DIVES[tag]

                content += f"### 📚 {dive['title']}\n\n"
                content += f"{dive['explanation']}\n\n"

                if dive.get("how_it_works"):
                    content += f"#### How It Works\n\n{dive['how_it_works']}\n\n"

                if dive.get("code_example"):
                    content += f"#### Working Code Example\n\n{dive['code_example']}\n\n"

                if dive.get("benefits"):
                    content += "#### Key Benefits\n\n"
                    for b in dive["benefits"]:
                        content += f"- {b}\n"
                    content += "\n"

                if dive.get("best_practices"):
                    content += "#### Best Practices\n\n"
                    for bp in dive["best_practices"]:
                        content += f"- ✅ {bp}\n"
                    content += "\n"

                if dive.get("anti_patterns"):
                    content += "#### Common Pitfalls to Avoid\n\n"
                    for ap in dive["anti_patterns"]:
                        content += f"- {ap}\n"
                    content += "\n"

                if dive.get("learning_resources"):
                    content += "#### Further Reading\n\n"
                    for lr in dive["learning_resources"]:
                        content += f"- {lr}\n"
                    content += "\n"

                content += "---\n\n"
                matched += 1

        return content

    def _implementation_guide(self, p: dict) -> str:
        category = p.get("category", "infrastructure")
        implementations = PROJECT_IMPLEMENTATIONS.get(category, {})

        content = """
## 📖 Implementation Guide

This section provides production-ready code you can adapt for your own projects.

"""

        if implementations:
            for name, code in implementations.items():
                content += f"### {name.replace('_', ' ').title()}\n\n"
                content += f"{code}\n\n"
        else:
            # Generic implementation guide
            features = p.get("features", [])[:3]
            for i, feature in enumerate(features, 1):
                content += f"""### Step {i}: Implementing {feature}

**Objective:** Build {feature.lower()} with production-grade quality.

**Implementation Approach:**

1. **Define Requirements**
   - Functional: What it must do
   - Non-functional: Performance, security, reliability targets

2. **Design the Solution**
   - Consider failure modes and edge cases
   - Plan for observability from the start
   - Document architectural decisions

3. **Implement Iteratively**
   - Start with a minimal working version
   - Add tests before extending functionality
   - Refactor for clarity and maintainability

4. **Validate Thoroughly**
   - Unit tests for business logic
   - Integration tests for component interaction
   - Load tests for performance validation

"""

        content += "---\n"
        return content

    def _best_practices(self, p: dict) -> str:
        return """
## ✅ Best Practices

### Infrastructure

| Practice | Description | Why It Matters |
|----------|-------------|----------------|
| **Infrastructure as Code** | Define all resources in version-controlled code | Reproducibility, audit trail, peer review |
| **Immutable Infrastructure** | Replace instances, don't modify them | Consistency, easier rollback, no drift |
| **Least Privilege** | Grant minimum required permissions | Security, blast radius reduction |
| **Multi-AZ Deployment** | Distribute across availability zones | High availability during AZ failures |

### Security

- ⛔ **Never** hardcode credentials in source code
- ⛔ **Never** commit secrets to version control
- ✅ **Always** use IAM roles over access keys
- ✅ **Always** encrypt data at rest and in transit
- ✅ **Always** enable audit logging (CloudTrail, VPC Flow Logs)

### Operations

1. **Observability First**
   - Instrument code before production deployment
   - Establish baselines for normal behavior
   - Create actionable alerts, not noise

2. **Automate Everything**
   - Manual processes don't scale
   - Runbooks should be scripts, not documents
   - Test automation regularly

3. **Practice Failure**
   - Regular DR drills validate recovery procedures
   - Chaos engineering builds confidence
   - Document and learn from incidents

### Code Quality

```python
# ✅ Good: Clear, testable, observable
class PaymentProcessor:
    def __init__(self, gateway: PaymentGateway, metrics: MetricsClient):
        self.gateway = gateway
        self.metrics = metrics
        self.logger = logging.getLogger(__name__)

    def process(self, payment: Payment) -> Result:
        self.logger.info(f"Processing payment {payment.id}")
        start = time.time()

        try:
            result = self.gateway.charge(payment)
            self.metrics.increment("payments.success")
            return result
        except GatewayError as e:
            self.metrics.increment("payments.failure")
            self.logger.error(f"Payment failed: {e}")
            raise
        finally:
            self.metrics.timing("payments.duration", time.time() - start)

# ❌ Bad: Untestable, no observability
def process_payment(payment):
    return requests.post(GATEWAY_URL, json=payment).json()
```

---
"""

    def _quick_start(self, p: dict) -> str:
        github_path = p.get("github_path", "")

        return f"""
## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- [ ] **Docker** (20.10+) and Docker Compose installed
- [ ] **Python** 3.11+ with pip
- [ ] **AWS CLI** configured with appropriate credentials
- [ ] **kubectl** installed and configured
- [ ] **Terraform** 1.5+ installed
- [ ] **Git** for version control

### Step 1: Clone the Repository

```bash
git clone https://github.com/samueljackson-collab/Portfolio-Project.git
cd Portfolio-Project/{github_path}
```

### Step 2: Review the Documentation

```bash
# Read the project README
cat README.md

# Review available make targets
make help
```

### Step 3: Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
vim .env

# Validate configuration
make validate-config
```

### Step 4: Start Local Development

```bash
# Start all services with Docker Compose
make up

# Verify services are running
make status

# View logs
make logs

# Run tests
make test
```

### Step 5: Deploy to Cloud

```bash
# Initialize Terraform
cd terraform
terraform init

# Review planned changes
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan

# Deploy application
cd ..
make deploy ENV=staging
```

### Verification

```bash
# Check deployment health
make health

# Run smoke tests
make smoke-test

# View dashboards
open http://localhost:3000  # Grafana
```

---
"""

    def _operational_guide(self, p: dict) -> str:
        return """
## ⚙️ Operational Guide

### Monitoring & Alerting

| Metric Type | Tool | Dashboard |
|-------------|------|-----------|
| **Metrics** | Prometheus | Grafana `http://localhost:3000` |
| **Logs** | Loki | Grafana Explore |
| **Traces** | Tempo/Jaeger | Grafana Explore |
| **Errors** | Sentry | `https://sentry.io/org/project` |

### Key Metrics to Monitor

```promql
# Request latency (P99)
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m]))

# Resource utilization
container_memory_usage_bytes / container_spec_memory_limit_bytes
```

### Common Operations

| Task | Command | When to Use |
|------|---------|-------------|
| View logs | `kubectl logs -f deploy/app` | Debugging issues |
| Scale up | `kubectl scale deploy/app --replicas=5` | Handling load |
| Rollback | `kubectl rollout undo deploy/app` | Bad deployment |
| Port forward | `kubectl port-forward svc/app 8080:80` | Local debugging |
| Exec into pod | `kubectl exec -it deploy/app -- bash` | Investigation |

### Runbooks

<details>
<summary><strong>🔴 High Error Rate</strong></summary>

**Symptoms:** Error rate exceeds 1% threshold

**Investigation:**
1. Check recent deployments: `kubectl rollout history deploy/app`
2. Review error logs: `kubectl logs -l app=app --since=1h | grep ERROR`
3. Check dependency health: `make check-dependencies`
4. Review metrics dashboard for patterns

**Resolution:**
- If recent deployment: `kubectl rollout undo deploy/app`
- If dependency failure: Check upstream service status
- If resource exhaustion: Scale horizontally or vertically

**Escalation:** Page on-call if not resolved in 15 minutes
</details>

<details>
<summary><strong>🟡 High Latency</strong></summary>

**Symptoms:** P99 latency > 500ms

**Investigation:**
1. Check traces for slow operations
2. Review database query performance
3. Check for resource constraints
4. Review recent configuration changes

**Resolution:**
- Identify slow queries and optimize
- Add caching for frequently accessed data
- Scale database read replicas
- Review and optimize N+1 queries
</details>

<details>
<summary><strong>🔵 Deployment Failure</strong></summary>

**Symptoms:** ArgoCD sync fails or pods not ready

**Investigation:**
1. Check ArgoCD UI for sync errors
2. Review pod events: `kubectl describe pod <pod>`
3. Check image pull status
4. Verify secrets and config maps exist

**Resolution:**
- Fix manifest issues and re-sync
- Ensure image exists in registry
- Verify RBAC permissions
- Check resource quotas
</details>

### Disaster Recovery

**RTO Target:** 15 minutes
**RPO Target:** 1 hour

```bash
# Failover to DR region
./scripts/dr-failover.sh --region us-west-2

# Validate data integrity
./scripts/dr-validate.sh

# Failback to primary
./scripts/dr-failback.sh --region us-east-1
```

---
"""

    def _real_world_scenarios(self, p: dict) -> str:
        category = p.get("category", "infrastructure")
        scenarios = REAL_WORLD_SCENARIOS.get(category, [])

        content = """
## 🌍 Real-World Scenarios

These scenarios demonstrate how this project applies to actual business situations.

"""

        if scenarios:
            for scenario in scenarios:
                content += f"""### Scenario: {scenario['scenario']}

**Challenge:** {scenario['challenge']}

**Solution:** {scenario['solution']}

---

"""
        else:
            content += """### Scenario: Production Traffic Surge

**Challenge:** Application needs to handle 5x normal traffic during peak events.

**Solution:** Auto-scaling policies trigger based on CPU and request metrics.
Load testing validates capacity before the event. Runbooks document
manual intervention procedures if automated scaling is insufficient.

---

### Scenario: Security Incident Response

**Challenge:** Vulnerability discovered in production dependency.

**Solution:** Automated scanning detected the CVE. Patch branch created
and tested within hours. Rolling deployment updated all instances with
zero downtime. Audit trail documented the entire response timeline.

---
"""

        return content

    def _related_projects(self, p: dict) -> str:
        current_tags = set(p.get("tags", []))
        related = []

        for proj in self.projects:
            if proj.get("id") == p.get("id"):
                continue
            overlap = len(current_tags & set(proj.get("tags", [])))
            if overlap >= 1:
                related.append((overlap, proj))

        related.sort(key=lambda x: x[0], reverse=True)
        related = related[:4]

        if not related:
            return ""

        rows = "\n".join(
            f"| [{r['name']}](/projects/{r['slug']}) | "
            f"{r['description'][:50]}... | {overlap} |"
            for overlap, r in related
        )

        return f"""
## 🔗 Related Projects

Explore these related projects that share technologies or concepts:

| Project | Description | Shared Tags |
|---------|-------------|-------------|
{rows}

---
"""

    def _resources(self, p: dict) -> str:
        github_path = p.get("github_path", "")

        return f"""
## 📚 Resources

### Project Links

| Resource | Link |
|----------|------|
| 📂 Source Code | [GitHub Repository](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/{github_path}) |
| 📖 Documentation | [`{github_path}/docs/`]({github_path}/docs/) |
| 🐛 Issues | [Report bugs or request features](https://github.com/samueljackson-collab/Portfolio-Project/issues) |

### Recommended Reading

- [The Twelve-Factor App](https://12factor.net/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

### Community Resources

- Stack Overflow: Tag your questions appropriately
- Reddit: r/devops, r/aws, r/kubernetes
- Discord: Many technology-specific servers

---

<div align="center">

**Last Updated:** {datetime.now().strftime('%Y-%m-%d')} |
**Version:** 3.0 |
**Generated by:** Portfolio Wiki Content Generator

*Found this helpful? Star the repository!*

</div>
"""

    def generate_all(self) -> dict[str, str]:
        """Generate all wiki pages."""
        output = self.output_dir / "projects"
        output.mkdir(parents=True, exist_ok=True)

        pages = {}
        for project in self.projects:
            slug = project.get("slug")
            content = self.generate_page(project)
            pages[slug] = content

            (output / f"{slug}.md").write_text(content)
            print(f"✅ Generated: {slug}.md ({len(content):,} chars)")

        return pages


def main():
    print("=" * 70)
    print("Wiki.js Content Generator v3 - Professional Edition")
    print("=" * 70)
    print()

    generator = ProfessionalWikiGenerator(PROJECTS_DATA, "wiki")
    pages = generator.generate_all()

    print()
    print(f"Generated {len(pages)} professional wiki pages")
    print("=" * 70)


if __name__ == "__main__":
    main()
