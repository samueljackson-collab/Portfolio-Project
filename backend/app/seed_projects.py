"""Seed script for creating admin user and portfolio projects."""
from __future__ import annotations

import asyncio
from typing import List

from sqlalchemy import select

from app import models
from app.auth import get_password_hash
from app.config import settings
from app.database import SessionLocal, init_db

PROJECTS: List[dict[str, object]] = [
    {
        "title": "AWS Infrastructure Automation",
        "slug": "aws-infrastructure-automation",
        "category": "Infrastructure",
        "description": "Terraform, CDK, and Pulumi patterns for repeatable AWS stacks.",
        "tags": ["terraform", "aws", "iac"],
        "repo_url": "https://github.com/samueljackson-collab/portfolio-aws-infra",
    },
    {
        "title": "Database Migration Platform",
        "slug": "database-migration-platform",
        "category": "Data",
        "description": "Change data capture pipelines with automated migration validation.",
        "tags": ["cdc", "debezium", "postgres"],
    },
    {
        "title": "Kubernetes CI/CD Pipeline",
        "slug": "kubernetes-cicd",
        "category": "DevOps",
        "description": "GitOps-driven delivery with Argo CD and progressive rollouts.",
        "tags": ["kubernetes", "argocd", "gitops"],
    },
    {
        "title": "DevSecOps Pipeline",
        "slug": "devsecops-pipeline",
        "category": "Security",
        "description": "Supply chain scanning, SBOM publishing, and policy as code.",
        "tags": ["security", "sast", "supply-chain"],
    },
    {
        "title": "Real-time Data Streaming",
        "slug": "real-time-data-streaming",
        "category": "Data",
        "description": "Kafka and Flink streaming with schema management and monitoring.",
        "tags": ["kafka", "flink", "streaming"],
    },
    {
        "title": "Machine Learning Pipeline",
        "slug": "mlops-platform",
        "category": "AI/ML",
        "description": "Experiment tracking, model registry, and automated promotion gates.",
        "tags": ["mlflow", "kubeflow", "mlops"],
    },
    {
        "title": "Serverless Data Processing",
        "slug": "serverless-data-processing",
        "category": "Cloud",
        "description": "Lambda- and Step Functions-based ETL workflows with DynamoDB.",
        "tags": ["aws", "lambda", "serverless"],
    },
    {
        "title": "Advanced AI Chatbot",
        "slug": "advanced-ai-chatbot",
        "category": "AI/ML",
        "description": "RAG assistant with vector search and function calling.",
        "tags": ["rag", "openai", "vector-search"],
    },
    {
        "title": "Multi-Region Disaster Recovery",
        "slug": "multi-region-disaster-recovery",
        "category": "Reliability",
        "description": "Failover drills, replication validation, and DR runbooks.",
        "tags": ["dr", "backup", "replication"],
    },
    {
        "title": "Blockchain Smart Contract Platform",
        "slug": "blockchain-smart-contract-platform",
        "category": "Blockchain",
        "description": "Hardhat-based staking contracts with auditing guardrails.",
        "tags": ["hardhat", "solidity", "security"],
    },
    {
        "title": "IoT Data Ingestion & Analytics",
        "slug": "iot-analytics",
        "category": "IoT",
        "description": "Edge telemetry simulation, ingestion, and dashboards.",
        "tags": ["iot", "mqtt", "analytics"],
    },
    {
        "title": "Quantum Computing Integration",
        "slug": "quantum-computing",
        "category": "Research",
        "description": "Hybrid quantum/classical optimization workflows.",
        "tags": ["qiskit", "optimization", "quantum"],
    },
    {
        "title": "Advanced Cybersecurity Platform",
        "slug": "advanced-cybersecurity",
        "category": "Security",
        "description": "SOAR engine with enrichment adapters and automated response.",
        "tags": ["soar", "detections", "automation"],
    },
    {
        "title": "Edge AI Inference Platform",
        "slug": "edge-ai-inference",
        "category": "AI/ML",
        "description": "ONNX Runtime service optimized for edge accelerators.",
        "tags": ["onnx", "edge", "cuda"],
    },
    {
        "title": "Real-time Collaborative Platform",
        "slug": "real-time-collaboration",
        "category": "Web",
        "description": "CRDT/OT collaboration server with presence and history.",
        "tags": ["crdt", "websockets", "realtime"],
    },
    {
        "title": "Advanced Data Lake & Analytics",
        "slug": "advanced-data-lake",
        "category": "Data",
        "description": "Medallion architecture with Delta Lake and governance.",
        "tags": ["delta", "spark", "databricks"],
    },
    {
        "title": "Multi-Cloud Service Mesh",
        "slug": "multi-cloud-service-mesh",
        "category": "Networking",
        "description": "Istio multi-cluster service mesh with mTLS and observability.",
        "tags": ["istio", "mtls", "multicloud"],
    },
    {
        "title": "GPU-Accelerated Computing",
        "slug": "gpu-accelerated-computing",
        "category": "Compute",
        "description": "GPU orchestration and Monte Carlo simulations using CuPy.",
        "tags": ["gpu", "cupy", "simulation"],
    },
    {
        "title": "Advanced Kubernetes Operators",
        "slug": "advanced-kubernetes-operators",
        "category": "Kubernetes",
        "description": "Kopf-based operator managing portfolio lifecycle resources.",
        "tags": ["operator", "kopf", "k8s"],
    },
    {
        "title": "Blockchain Oracle Service",
        "slug": "blockchain-oracle-service",
        "category": "Blockchain",
        "description": "Chainlink adapter and consumer contracts for on-chain metrics.",
        "tags": ["chainlink", "oracle", "solidity"],
    },
    {
        "title": "Quantum-Safe Cryptography",
        "slug": "quantum-safe-cryptography",
        "category": "Security",
        "description": "Hybrid Kyber + ECDH key exchange prototype with testing harness.",
        "tags": ["pq", "kyber", "cryptography"],
    },
    {
        "title": "Autonomous DevOps Platform",
        "slug": "autonomous-devops-platform",
        "category": "DevOps",
        "description": "Event-driven remediation workflows and runbooks-as-code.",
        "tags": ["automation", "event-driven", "devops"],
    },
    {
        "title": "Advanced Monitoring & Observability",
        "slug": "advanced-monitoring",
        "category": "Observability",
        "description": "Grafana dashboards, alerting rules, and distributed tracing.",
        "tags": ["grafana", "prometheus", "otel"],
    },
    {
        "title": "Portfolio Report Generator",
        "slug": "portfolio-report-generator",
        "category": "Automation",
        "description": "Automated report templating with Jinja2 and data exports.",
        "tags": ["jinja2", "reports", "templates"],
    },
    {
        "title": "Portfolio Website & Documentation Hub",
        "slug": "portfolio-website",
        "category": "Web",
        "description": "Static documentation hub aggregating project artifacts.",
        "tags": ["vitepress", "docs", "static"],
        "featured": True,
    },
]


async def seed() -> None:
    await init_db()
    async with SessionLocal() as session:
        # Create admin user
        admin_query = await session.execute(select(models.User).where(models.User.username == "admin"))
        admin = admin_query.scalar_one_or_none()
        if not admin:
            admin = models.User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin1234"),
                is_admin=True,
            )
            session.add(admin)
            await session.commit()

        # Seed projects
        for project in PROJECTS:
            existing = await session.execute(
                select(models.Project).where(models.Project.slug == project["slug"])
            )
            if existing.scalar_one_or_none():
                continue
            session.add(
                models.Project(
                    title=project["title"],
                    slug=project["slug"],
                    category=project["category"],
                    description=project["description"],
                    tags=",".join(project.get("tags", [])),
                    repo_url=project.get("repo_url"),
                    live_url=project.get("live_url"),
                    featured=bool(project.get("featured", False)),
                )
            )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
