#!/usr/bin/env python3
"""
Extended Knowledge Base for Wiki.js Content Generation

Contains detailed educational content, real-world scenarios, best practices,
and comprehensive technology explanations for portfolio wiki pages.
"""

# =============================================================================
# EXTENDED TECHNOLOGY DEEP DIVES
# =============================================================================

TECHNOLOGY_DEEP_DIVES = {
    "terraform": {
        "title": "Why Terraform?",
        "explanation": """Terraform is HashiCorp's Infrastructure as Code (IaC) tool that enables
declarative infrastructure management across multiple cloud providers. It uses HCL (HashiCorp
Configuration Language) to define resources in a human-readable format.

Unlike imperative approaches where you specify *how* to create infrastructure, Terraform's
declarative model lets you specify *what* you want. Terraform figures out the creation order,
handles dependencies, and maintains state to track what exists.""",
        "how_it_works": """
**Core Workflow:**
1. **Write** - Define infrastructure in `.tf` files using HCL
2. **Plan** - Preview changes with `terraform plan`
3. **Apply** - Execute changes with `terraform apply`
4. **Destroy** - Remove infrastructure with `terraform destroy`

**State Management:**
Terraform maintains a state file (`terraform.tfstate`) that maps your configuration to
real-world resources. This enables:
- Tracking resource metadata and dependencies
- Detecting drift between config and reality
- Planning minimal changes for updates
""",
        "code_example": '''```hcl
# Example: AWS VPC with Terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "production-vpc"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

resource "aws_subnet" "public" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "public-subnet-${count.index + 1}"
    Type = "public"
  }
}
```''',
        "benefits": [
            "**Provider Agnostic**: Single workflow for AWS, GCP, Azure, and 100+ providers",
            "**State Management**: Tracks infrastructure state for safe modifications",
            "**Plan Before Apply**: Preview changes before execution reduces risk",
            "**Modular Design**: Reusable modules promote DRY principles",
            "**Version Control Friendly**: Text-based configs integrate with Git workflows",
            "**Dependency Graph**: Automatically determines resource creation order",
            "**Idempotent Operations**: Running apply multiple times yields same result"
        ],
        "best_practices": [
            "Use remote state storage (S3, GCS) with state locking (DynamoDB)",
            "Implement workspaces or directory structure for environment separation",
            "Pin provider versions to avoid unexpected breaking changes",
            "Use modules for reusable infrastructure components",
            "Never commit `.tfstate` files or secrets to version control",
            "Implement `terraform fmt` and `terraform validate` in CI pipelines"
        ],
        "anti_patterns": [
            "❌ Storing state locally in team environments",
            "❌ Hardcoding values instead of using variables",
            "❌ Creating monolithic configurations instead of modules",
            "❌ Ignoring plan output before applying changes",
            "❌ Manual changes to infrastructure outside Terraform"
        ],
        "learning_resources": [
            "[Terraform Documentation](https://developer.hashicorp.com/terraform/docs)",
            "[Terraform Best Practices](https://www.terraform-best-practices.com/)",
            "[Terraform Up & Running (Book)](https://www.terraformupandrunning.com/)"
        ]
    },

    "kubernetes": {
        "title": "Why Kubernetes?",
        "explanation": """Kubernetes (K8s) is the industry-standard container orchestration platform.
Originally designed by Google based on their internal Borg system, it automates deployment,
scaling, and management of containerized applications across clusters of hosts.

Kubernetes abstracts away the underlying infrastructure, allowing you to describe your
application's desired state declaratively. The control plane continuously works to
maintain that state, handling failures, scaling, and updates automatically.""",
        "how_it_works": """
**Architecture Overview:**
- **Control Plane**: API Server, etcd, Scheduler, Controller Manager
- **Worker Nodes**: kubelet, kube-proxy, Container Runtime
- **Pods**: Smallest deployable unit (one or more containers)

**Key Concepts:**
- **Deployments**: Manage stateless application replicas
- **Services**: Stable networking for pod communication
- **ConfigMaps/Secrets**: Configuration and sensitive data management
- **Ingress**: HTTP/HTTPS routing to services
- **Namespaces**: Virtual clusters for resource isolation
""",
        "code_example": '''```yaml
# Example: Kubernetes Deployment with Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-application
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:1.25
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 3
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```''',
        "benefits": [
            "**Self-Healing**: Automatically restarts failed containers and replaces unhealthy nodes",
            "**Horizontal Scaling**: Scale applications based on CPU, memory, or custom metrics",
            "**Service Discovery**: Built-in DNS and load balancing between pods",
            "**Rolling Updates**: Zero-downtime deployments with automatic rollback",
            "**Declarative Configuration**: Define desired state, K8s reconciles reality",
            "**Secret Management**: Secure storage for sensitive configuration",
            "**Resource Management**: CPU/memory limits prevent noisy neighbors"
        ],
        "best_practices": [
            "Always set resource requests and limits for containers",
            "Use namespaces to isolate environments and teams",
            "Implement liveness and readiness probes for all services",
            "Use PodDisruptionBudgets for high availability during maintenance",
            "Store manifests in Git and use GitOps for deployments",
            "Use NetworkPolicies to restrict pod-to-pod communication"
        ],
        "anti_patterns": [
            "❌ Running containers as root without security context",
            "❌ Using `latest` tag for container images",
            "❌ Storing secrets in ConfigMaps or environment variables",
            "❌ Not setting resource limits (allows resource exhaustion)",
            "❌ Single replica deployments for production workloads"
        ],
        "learning_resources": [
            "[Kubernetes Documentation](https://kubernetes.io/docs/)",
            "[CNCF Kubernetes Training](https://www.cncf.io/certification/cka/)",
            "[Kubernetes Patterns (Book)](https://k8spatterns.io/)"
        ]
    },

    "kafka": {
        "title": "Why Apache Kafka?",
        "explanation": """Apache Kafka is a distributed event streaming platform capable of handling
trillions of events per day. Originally developed at LinkedIn, it provides durable,
fault-tolerant message storage with high throughput for real-time data pipelines.

Kafka decouples data producers from consumers, enabling asynchronous communication
at scale. Unlike traditional message queues, Kafka retains messages for configurable
periods, allowing consumers to replay events and enabling event sourcing patterns.""",
        "how_it_works": """
**Core Concepts:**
- **Topics**: Named feeds of messages, partitioned for parallelism
- **Partitions**: Ordered, immutable sequence of records
- **Producers**: Publish messages to topics
- **Consumers**: Subscribe to topics and process messages
- **Consumer Groups**: Coordinate consumption across instances

**Data Flow:**
1. Producers send records to topic partitions
2. Brokers persist records to disk with replication
3. Consumers poll brokers for new records
4. Offsets track consumer progress (committed after processing)
""",
        "code_example": '''```python
# Example: Kafka Producer and Consumer with Python
from confluent_kafka import Producer, Consumer
import json

# Producer Configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',  # Wait for all replicas
    'retries': 3,
    'linger.ms': 5  # Batch messages for efficiency
}

producer = Producer(producer_config)

def delivery_callback(err, msg):
    if err:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()}[{msg.partition()}]')

# Send message
event = {'user_id': 123, 'action': 'purchase', 'amount': 99.99}
producer.produce(
    topic='user-events',
    key=str(event['user_id']).encode(),
    value=json.dumps(event).encode(),
    callback=delivery_callback
)
producer.flush()

# Consumer Configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'analytics-consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False  # Manual commit for exactly-once
}

consumer = Consumer(consumer_config)
consumer.subscribe(['user-events'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print(f'Consumer error: {msg.error()}')
            continue

        event = json.loads(msg.value().decode())
        process_event(event)  # Your business logic
        consumer.commit(asynchronous=False)  # Commit after processing
finally:
    consumer.close()
```''',
        "benefits": [
            "**High Throughput**: Handle millions of messages per second per broker",
            "**Durability**: Messages persisted to disk with configurable replication",
            "**Scalability**: Add partitions and brokers for horizontal scaling",
            "**Exactly-Once Semantics**: Guaranteed delivery without duplicates",
            "**Message Retention**: Replay events for recovery or reprocessing",
            "**Ecosystem**: Connect, Streams, Schema Registry, ksqlDB"
        ],
        "best_practices": [
            "Use meaningful partition keys for related event ordering",
            "Set appropriate replication factor (min 3 for production)",
            "Enable idempotent producers for exactly-once semantics",
            "Use Schema Registry for schema evolution management",
            "Monitor consumer lag to detect processing bottlenecks",
            "Implement dead letter queues for poison messages"
        ],
        "anti_patterns": [
            "❌ Using Kafka for request-response patterns (use gRPC/REST)",
            "❌ Storing large payloads in messages (use references instead)",
            "❌ Single partition topics for high-throughput workloads",
            "❌ Auto-commit offsets without idempotent processing",
            "❌ Ignoring consumer group rebalancing implications"
        ],
        "learning_resources": [
            "[Kafka Documentation](https://kafka.apache.org/documentation/)",
            "[Confluent Developer](https://developer.confluent.io/)",
            "[Designing Data-Intensive Applications (Book)](https://dataintensive.net/)"
        ]
    },

    "argocd": {
        "title": "Why ArgoCD?",
        "explanation": """ArgoCD is a declarative GitOps continuous delivery tool for Kubernetes.
It continuously monitors Git repositories and automatically syncs application state
to match the desired configuration stored in version control.

GitOps treats Git as the single source of truth for infrastructure and applications.
ArgoCD watches for changes in Git and reconciles the cluster state, providing
audit trails, easy rollbacks, and consistent deployments across environments.""",
        "how_it_works": """
**GitOps Workflow:**
1. Developer commits changes to Git repository
2. ArgoCD detects changes via webhook or polling
3. ArgoCD compares desired state (Git) vs live state (cluster)
4. Out-of-sync resources are identified
5. ArgoCD syncs changes (manual or automatic)
6. Health checks verify deployment success

**Sync Strategies:**
- **Manual Sync**: Require explicit approval
- **Auto-Sync**: Automatically apply changes
- **Self-Heal**: Revert manual cluster changes
""",
        "code_example": '''```yaml
# Example: ArgoCD Application Manifest
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-application
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default

  source:
    repoURL: https://github.com/org/app-manifests.git
    targetRevision: main
    path: environments/production

    # Helm support
    helm:
      valueFiles:
        - values-production.yaml
      parameters:
        - name: image.tag
          value: "v1.2.3"

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true      # Delete removed resources
      selfHeal: true   # Revert manual changes
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  # Health checks
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas  # Ignore HPA-managed replicas
```''',
        "benefits": [
            "**GitOps Native**: Git as single source of truth with full audit trail",
            "**Auto-Sync**: Automatically reconciles cluster state with Git",
            "**Multi-Cluster**: Manage deployments across multiple Kubernetes clusters",
            "**Rollback**: One-click rollback to any previous Git commit",
            "**RBAC**: Fine-grained access control with SSO integration",
            "**Health Monitoring**: Custom health checks for application resources",
            "**Web UI**: Visual dashboard for deployment status and history"
        ],
        "best_practices": [
            "Separate application code repos from manifest repos",
            "Use ApplicationSets for multi-cluster/multi-env deployments",
            "Implement progressive delivery with Argo Rollouts",
            "Configure webhook triggers for faster sync detection",
            "Use projects to isolate teams and limit cluster access",
            "Enable self-heal to prevent configuration drift"
        ],
        "anti_patterns": [
            "❌ Storing sensitive values in Git (use sealed-secrets or external-secrets)",
            "❌ Manual kubectl changes that bypass GitOps workflow",
            "❌ Single Application for multiple unrelated services",
            "❌ Disabling pruning (leaves orphaned resources)",
            "❌ Auto-sync without proper CI validation gates"
        ],
        "learning_resources": [
            "[ArgoCD Documentation](https://argo-cd.readthedocs.io/)",
            "[GitOps Principles](https://opengitops.dev/)",
            "[Argo Project](https://argoproj.github.io/)"
        ]
    },

    "docker": {
        "title": "Why Docker?",
        "explanation": """Docker revolutionized software delivery by packaging applications with their
dependencies into portable containers. This ensures consistency across development,
testing, and production environments—eliminating "works on my machine" problems.

Containers share the host OS kernel but isolate the application environment,
making them lighter and faster than virtual machines while providing similar
isolation benefits.""",
        "how_it_works": """
**Container vs VM:**
- VMs virtualize hardware, each with full OS (~GBs, minutes to start)
- Containers virtualize OS, sharing kernel (~MBs, seconds to start)

**Docker Architecture:**
- **Docker Engine**: Runtime that manages containers
- **Images**: Read-only templates for containers
- **Containers**: Running instances of images
- **Dockerfile**: Instructions to build images
- **Registry**: Storage for sharing images (Docker Hub, ECR, GCR)
""",
        "code_example": '''```dockerfile
# Example: Multi-stage Dockerfile for Python Application
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim as production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```''',
        "benefits": [
            "**Consistency**: Same container runs identically everywhere",
            "**Isolation**: Applications don't interfere with each other",
            "**Efficiency**: Share OS kernel, minimal overhead",
            "**Version Control**: Image tags enable reproducible deployments",
            "**Fast Startup**: Seconds vs minutes for VMs",
            "**Ecosystem**: Millions of pre-built images on Docker Hub",
            "**DevOps Enabler**: Foundation for CI/CD and orchestration"
        ],
        "best_practices": [
            "Use multi-stage builds to minimize image size",
            "Run containers as non-root users for security",
            "Pin specific image versions, never use `latest` in production",
            "Use `.dockerignore` to exclude unnecessary files",
            "One process per container (single responsibility)",
            "Use HEALTHCHECK for container health monitoring"
        ],
        "anti_patterns": [
            "❌ Running containers as root",
            "❌ Storing secrets in images or environment variables",
            "❌ Using `latest` tag in production deployments",
            "❌ Installing unnecessary packages in images",
            "❌ Not leveraging layer caching (order matters in Dockerfile)"
        ],
        "learning_resources": [
            "[Docker Documentation](https://docs.docker.com/)",
            "[Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)",
            "[Docker Security](https://docs.docker.com/engine/security/)"
        ]
    },

    "aws": {
        "title": "Why AWS?",
        "explanation": """Amazon Web Services (AWS) is the world's most comprehensive cloud platform,
offering 200+ services from data centers globally. Launched in 2006, it pioneered
cloud computing and maintains market leadership with the largest ecosystem.

AWS provides the building blocks for virtually any workload—from simple web hosting
to complex machine learning pipelines—with enterprise-grade security, compliance,
and global infrastructure.""",
        "how_it_works": """
**Core Service Categories:**
- **Compute**: EC2, Lambda, ECS, EKS, Fargate
- **Storage**: S3, EBS, EFS, Glacier
- **Database**: RDS, DynamoDB, Aurora, ElastiCache
- **Networking**: VPC, Route53, CloudFront, ELB
- **Security**: IAM, KMS, Secrets Manager, WAF

**Global Infrastructure:**
- 30+ Regions (geographic areas)
- 100+ Availability Zones (isolated data centers)
- 400+ Edge Locations (CDN/DNS endpoints)
""",
        "code_example": '''```python
# Example: AWS SDK (boto3) Usage
import boto3
from botocore.config import Config

# Configure client with retry logic
config = Config(
    retries={'max_attempts': 3, 'mode': 'adaptive'},
    connect_timeout=5,
    read_timeout=30
)

# S3 Operations
s3 = boto3.client('s3', config=config)

# Upload file with server-side encryption
s3.upload_file(
    Filename='data.json',
    Bucket='my-bucket',
    Key='uploads/data.json',
    ExtraArgs={
        'ServerSideEncryption': 'aws:kms',
        'SSEKMSKeyId': 'alias/my-key'
    }
)

# DynamoDB Operations
dynamodb = boto3.resource('dynamodb', config=config)
table = dynamodb.Table('users')

# Put item with condition
table.put_item(
    Item={
        'user_id': '123',
        'email': 'user@example.com',
        'created_at': '2024-01-15T10:30:00Z'
    },
    ConditionExpression='attribute_not_exists(user_id)'
)

# Lambda invocation
lambda_client = boto3.client('lambda', config=config)
response = lambda_client.invoke(
    FunctionName='process-data',
    InvocationType='Event',  # Async
    Payload=json.dumps({'key': 'value'})
)
```''',
        "benefits": [
            "**Market Leader**: Largest ecosystem with extensive documentation and community",
            "**Global Infrastructure**: 30+ regions for low-latency deployments worldwide",
            "**Service Breadth**: Compute, storage, ML, IoT, analytics under one roof",
            "**Pay-as-you-go**: Optimize costs with granular per-second billing",
            "**Enterprise Ready**: Compliance certifications (SOC, HIPAA, PCI, FedRAMP)",
            "**Innovation Pace**: 2000+ new features/services annually",
            "**Mature IaC**: CloudFormation, CDK, and excellent Terraform support"
        ],
        "best_practices": [
            "Use IAM roles instead of access keys where possible",
            "Enable CloudTrail for API audit logging",
            "Implement VPC for network isolation",
            "Use AWS Organizations for multi-account strategy",
            "Enable S3 versioning and encryption by default",
            "Set up billing alerts and cost allocation tags"
        ],
        "anti_patterns": [
            "❌ Hardcoding credentials in code or config files",
            "❌ Using root account for daily operations",
            "❌ Public S3 buckets without explicit business need",
            "❌ Single AZ deployments for production workloads",
            "❌ Ignoring Reserved Instances/Savings Plans for steady-state workloads"
        ],
        "learning_resources": [
            "[AWS Documentation](https://docs.aws.amazon.com/)",
            "[AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)",
            "[AWS Certification Path](https://aws.amazon.com/certification/)"
        ]
    },

    "github-actions": {
        "title": "Why GitHub Actions?",
        "explanation": """GitHub Actions is a CI/CD platform integrated directly into GitHub repositories.
It enables automation of build, test, and deployment workflows triggered by repository
events like pushes, pull requests, or scheduled times.

The tight GitHub integration eliminates the need for external CI servers, while the
marketplace of 10,000+ community actions accelerates pipeline development.""",
        "how_it_works": """
**Workflow Components:**
- **Workflow**: YAML file in `.github/workflows/`
- **Events**: Triggers (push, PR, schedule, manual)
- **Jobs**: Groups of steps that run on a runner
- **Steps**: Individual tasks (run commands or actions)
- **Actions**: Reusable units of code
- **Runners**: Machines that execute jobs (hosted or self-hosted)

**Execution Model:**
1. Event triggers workflow
2. Jobs run in parallel (unless dependencies defined)
3. Steps execute sequentially within a job
4. Artifacts and outputs pass between jobs
""",
        "code_example": '''```yaml
# Example: Comprehensive CI/CD Workflow
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options: [staging, production]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
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

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Deploy to Kubernetes
        uses: azure/k8s-deploy@v4
        with:
          manifests: k8s/
          images: ${{ needs.build.outputs.image-tag }}
```''',
        "benefits": [
            "**Native Integration**: No external CI server needed, tight GitHub integration",
            "**Marketplace**: 10,000+ community actions for common tasks",
            "**Matrix Builds**: Test across multiple OS/language versions simultaneously",
            "**Secrets Management**: Secure credential storage with environment scoping",
            "**Free Tier**: Generous free minutes for public and private repos",
            "**Self-Hosted Runners**: Run on your own infrastructure when needed",
            "**Reusable Workflows**: Share workflows across repositories"
        ],
        "best_practices": [
            "Use specific action versions (@v4) not @latest or @main",
            "Cache dependencies to speed up builds",
            "Use environments for deployment approvals and secrets",
            "Implement branch protection rules with required checks",
            "Use composite actions to DRY up repeated steps",
            "Set timeout-minutes to prevent runaway jobs"
        ],
        "anti_patterns": [
            "❌ Storing secrets in workflow files or repository code",
            "❌ Using `pull_request_target` without security review",
            "❌ Skipping tests for 'small' changes",
            "❌ Overly broad permissions (use least privilege)",
            "❌ Not using caching for dependencies"
        ],
        "learning_resources": [
            "[GitHub Actions Documentation](https://docs.github.com/en/actions)",
            "[GitHub Actions Marketplace](https://github.com/marketplace?type=actions)",
            "[GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)"
        ]
    },

    "mlflow": {
        "title": "Why MLflow?",
        "explanation": """MLflow is an open-source platform for managing the complete machine learning
lifecycle. It provides experiment tracking, model packaging, versioning, and
deployment capabilities—addressing the unique challenges of ML operations.

Unlike traditional software where code changes are tracked in Git, ML models depend
on code, data, hyperparameters, and environment. MLflow tracks all these dimensions,
enabling reproducibility and collaboration.""",
        "how_it_works": """
**Core Components:**
- **Tracking**: Log parameters, metrics, and artifacts
- **Projects**: Package code for reproducible runs
- **Models**: Standard format for model packaging
- **Registry**: Centralized model store with versioning

**Workflow:**
1. Log experiments during training (params, metrics, artifacts)
2. Compare runs to find best model
3. Register model in Model Registry
4. Transition through stages (Staging → Production)
5. Deploy using MLflow's deployment tools
""",
        "code_example": '''```python
# Example: MLflow Experiment Tracking
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

# Set experiment
mlflow.set_experiment("customer-churn-prediction")

# Enable autologging for sklearn
mlflow.sklearn.autolog()

# Or manual logging for more control
with mlflow.start_run(run_name="rf-baseline") as run:
    # Log parameters
    params = {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "random_state": 42
    }
    mlflow.log_params(params)

    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # Evaluate and log metrics
    y_pred = model.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "test_size": len(X_test)
    }
    mlflow.log_metrics(metrics)

    # Log model with signature
    from mlflow.models import infer_signature
    signature = infer_signature(X_train, model.predict(X_train))
    mlflow.sklearn.log_model(
        model,
        "model",
        signature=signature,
        registered_model_name="churn-classifier"
    )

    # Log artifacts
    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(cm)
    disp.plot()
    plt.savefig("confusion_matrix.png")
    mlflow.log_artifact("confusion_matrix.png")

    print(f"Run ID: {run.info.run_id}")
    print(f"Artifact URI: {mlflow.get_artifact_uri()}")
```''',
        "benefits": [
            "**Experiment Tracking**: Log parameters, metrics, and artifacts automatically",
            "**Model Registry**: Version and stage models with approval workflows",
            "**Reproducibility**: Package models with exact dependencies",
            "**Framework Agnostic**: Works with sklearn, TensorFlow, PyTorch, and more",
            "**Deployment Options**: Deploy to SageMaker, Azure ML, or REST API",
            "**Collaboration**: Share experiments across team members",
            "**Open Source**: No vendor lock-in, self-hosted or managed options"
        ],
        "best_practices": [
            "Use MLflow Projects for reproducible experiment packaging",
            "Implement model signatures for input/output validation",
            "Use Model Registry stages (Staging/Production) for deployment workflow",
            "Log dataset versions alongside experiments",
            "Set up artifact storage on S3/GCS for large models",
            "Integrate with CI/CD for automated model validation"
        ],
        "anti_patterns": [
            "❌ Not logging the random seed (breaks reproducibility)",
            "❌ Storing large datasets as artifacts (use references)",
            "❌ Skipping model signatures (prevents input validation)",
            "❌ Manual model versioning outside the registry",
            "❌ Not tracking data preprocessing steps"
        ],
        "learning_resources": [
            "[MLflow Documentation](https://mlflow.org/docs/latest/index.html)",
            "[MLflow Tutorials](https://mlflow.org/docs/latest/tutorials-and-examples/index.html)",
            "[MLOps: Continuous Delivery for ML](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)"
        ]
    },

    "prometheus": {
        "title": "Why Prometheus?",
        "explanation": """Prometheus is an open-source monitoring system with a dimensional data model
and powerful query language (PromQL). Originally built at SoundCloud and now a
CNCF graduated project, it's the de facto standard for Kubernetes monitoring.

Prometheus uses a pull-based model where it scrapes metrics from targets at
configured intervals. This approach simplifies service discovery and makes it
easy to monitor dynamic environments.""",
        "how_it_works": """
**Architecture:**
- **Prometheus Server**: Scrapes and stores metrics
- **Exporters**: Expose metrics in Prometheus format
- **Alertmanager**: Handles alert routing and deduplication
- **Pushgateway**: For short-lived batch jobs

**Data Model:**
- Time series identified by metric name + labels
- Labels enable dimensional queries
- Samples: (timestamp, value) pairs

**Example Metrics:**
- `http_requests_total{method="GET", status="200"}` (counter)
- `http_request_duration_seconds` (histogram)
- `process_cpu_seconds_total` (gauge)
""",
        "code_example": '''```python
# Example: Custom Prometheus Exporter
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    start_http_server, CollectorRegistry
)
import time
import random

# Define metrics
REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'app_request_duration_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10]
)

ACTIVE_CONNECTIONS = Gauge(
    'app_active_connections',
    'Number of active connections'
)

APP_INFO = Info(
    'app',
    'Application information'
)

# Set static info
APP_INFO.info({
    'version': '1.2.3',
    'environment': 'production'
})

# Instrument your application
def handle_request(method: str, endpoint: str):
    """Example request handler with metrics."""
    ACTIVE_CONNECTIONS.inc()

    start_time = time.time()
    try:
        # Simulate request processing
        time.sleep(random.uniform(0.01, 0.5))
        status = "200"
    except Exception:
        status = "500"
    finally:
        duration = time.time() - start_time

        # Record metrics
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        ACTIVE_CONNECTIONS.dec()

if __name__ == '__main__':
    # Start metrics server on port 8000
    start_http_server(8000)
    print("Metrics available at http://localhost:8000/metrics")

    # Simulate traffic
    while True:
        handle_request("GET", "/api/users")
        time.sleep(0.1)
```

```yaml
# prometheus.yml - Scrape configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts/*.yml'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'application'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: (.+)
```''',
        "benefits": [
            "**Pull-Based Model**: Prometheus scrapes metrics, simplifying service discovery",
            "**PromQL**: Powerful query language for analysis and alerting",
            "**Service Discovery**: Auto-discover Kubernetes pods, EC2 instances, etc.",
            "**Alertmanager**: Flexible alerting with routing, grouping, silencing",
            "**CNCF Graduated**: Production-proven with strong community support",
            "**Dimensional Data**: Labels enable flexible querying and aggregation",
            "**Efficient Storage**: Custom TSDB optimized for time series"
        ],
        "best_practices": [
            "Use recording rules for frequently-used complex queries",
            "Implement alerting rules with proper severity levels",
            "Set appropriate scrape intervals (15s default is usually fine)",
            "Use relabeling to add metadata and filter targets",
            "Configure retention based on storage capacity",
            "Use federation or remote write for long-term storage"
        ],
        "anti_patterns": [
            "❌ High-cardinality labels (user IDs, request IDs)",
            "❌ Storing logs in Prometheus (use Loki instead)",
            "❌ Missing `le` label in histogram queries",
            "❌ Alerting on raw values without smoothing",
            "❌ Too short scrape intervals causing load"
        ],
        "learning_resources": [
            "[Prometheus Documentation](https://prometheus.io/docs/)",
            "[PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)",
            "[Prometheus: Up & Running (Book)](https://www.oreilly.com/library/view/prometheus-up/9781492034131/)"
        ]
    },

    "security": {
        "title": "Why Security-First Development?",
        "explanation": """Security-first development integrates security practices throughout the SDLC
rather than treating it as an afterthought. This "shift-left" approach catches
vulnerabilities early when they're cheapest to fix—before they reach production.

Studies show that fixing a vulnerability in production costs 100x more than
fixing it during development. By embedding security into CI/CD pipelines,
teams catch issues automatically without slowing down delivery.""",
        "how_it_works": """
**Shift-Left Security Stages:**
1. **Design**: Threat modeling, security requirements
2. **Code**: SAST, secret scanning, dependency scanning
3. **Build**: Container scanning, SBOM generation
4. **Test**: DAST, penetration testing
5. **Deploy**: Configuration scanning, compliance checks
6. **Runtime**: WAF, monitoring, incident response

**Key Tools by Stage:**
- SAST: SonarQube, Semgrep, CodeQL
- Dependencies: Snyk, Dependabot, OWASP Dependency-Check
- Containers: Trivy, Grype, Clair
- DAST: OWASP ZAP, Burp Suite
- Secrets: GitLeaks, TruffleHog
""",
        "code_example": '''```yaml
# Example: Security Pipeline in GitHub Actions
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6am

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for secret detection

      - name: GitLeaks Scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: python, javascript

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3

      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten

  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t app:${{ github.sha }} .

      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: app:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  dast:
    runs-on: ubuntu-latest
    needs: [sast, dependency-scan]
    steps:
      - name: Start application
        run: docker-compose up -d

      - name: OWASP ZAP Scan
        uses: zaproxy/action-full-scan@v0.8.0
        with:
          target: 'http://localhost:8080'
          rules_file_name: '.zap/rules.tsv'
```''',
        "benefits": [
            "**Early Detection**: Find vulnerabilities before production (100x cheaper)",
            "**Cost Reduction**: Automated scanning vs expensive penetration tests",
            "**Compliance**: Meet regulatory requirements (SOC2, HIPAA, PCI-DSS)",
            "**Customer Trust**: Build confidence with secure-by-default practices",
            "**Automation**: Consistent security checks in every CI/CD run",
            "**Developer Enablement**: Security feedback in familiar tools (IDE, PR)",
            "**Supply Chain Security**: Detect vulnerable dependencies automatically"
        ],
        "best_practices": [
            "Implement security scanning in CI with blocking thresholds",
            "Use secret scanning with pre-commit hooks",
            "Maintain SBOM (Software Bill of Materials) for all releases",
            "Conduct threat modeling during design phase",
            "Implement least-privilege access for all services",
            "Regular security training for development teams"
        ],
        "anti_patterns": [
            "❌ Security as a gate at the end of development",
            "❌ Ignoring vulnerability findings without triage",
            "❌ Relying solely on perimeter security",
            "❌ Storing secrets in code or environment variables",
            "❌ Security exceptions that never get reviewed"
        ],
        "learning_resources": [
            "[OWASP Top 10](https://owasp.org/www-project-top-ten/)",
            "[NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)",
            "[DevSecOps Maturity Model](https://dsomm.owasp.org/)"
        ]
    },

    "serverless": {
        "title": "Why Serverless?",
        "explanation": """Serverless computing abstracts infrastructure management, allowing developers
to focus entirely on code. Cloud providers handle scaling, patching, availability,
and capacity planning—charging only for actual execution time.

The "serverless" name is a misnomer—servers still exist, but you don't manage them.
This model excels for event-driven workloads with variable traffic, enabling
rapid development and cost optimization for appropriate use cases.""",
        "how_it_works": """
**Execution Model:**
1. Event triggers function (HTTP, queue, schedule, etc.)
2. Cloud provider provisions execution environment
3. Function executes (milliseconds to 15 minutes)
4. Environment may be reused (warm start) or destroyed (cold start)
5. Billing based on execution time and memory

**Key Characteristics:**
- **Stateless**: No persistent local storage
- **Event-Driven**: Triggered by events, not always running
- **Auto-Scaling**: 0 to thousands of instances automatically
- **Pay-Per-Use**: Charged per invocation and duration
""",
        "code_example": '''```python
# Example: AWS Lambda with API Gateway
import json
import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()
metrics = Metrics()
app = APIGatewayRestResolver()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

@app.get("/users/<user_id>")
@tracer.capture_method
def get_user(user_id: str):
    """Get user by ID."""
    logger.info(f"Getting user: {user_id}")

    response = table.get_item(Key={'user_id': user_id})

    if 'Item' not in response:
        return {"error": "User not found"}, 404

    metrics.add_metric(name="UserFetched", unit="Count", value=1)
    return response['Item']

@app.post("/users")
@tracer.capture_method
def create_user():
    """Create new user."""
    body = app.current_event.json_body

    # Validate input
    required_fields = ['email', 'name']
    if not all(field in body for field in required_fields):
        return {"error": "Missing required fields"}, 400

    user_id = str(uuid.uuid4())
    item = {
        'user_id': user_id,
        'email': body['email'],
        'name': body['name'],
        'created_at': datetime.utcnow().isoformat()
    }

    table.put_item(Item=item)

    metrics.add_metric(name="UserCreated", unit="Count", value=1)
    logger.info(f"Created user: {user_id}")

    return item, 201

@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """Main Lambda entry point."""
    return app.resolve(event, context)
```

```yaml
# SAM template for deployment
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    MemorySize: 256
    Runtime: python3.11
    Tracing: Active
    Environment:
      Variables:
        LOG_LEVEL: INFO

Resources:
  UserFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: app.lambda_handler
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable
      Events:
        GetUser:
          Type: Api
          Properties:
            Path: /users/{user_id}
            Method: get
        CreateUser:
          Type: Api
          Properties:
            Path: /users
            Method: post

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: users
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: user_id
          AttributeType: S
      KeySchema:
        - AttributeName: user_id
          KeyType: HASH
```''',
        "benefits": [
            "**No Server Management**: Focus on business logic, not infrastructure",
            "**Auto-Scaling**: Scale from 0 to thousands of instances automatically",
            "**Pay-Per-Use**: No charges when idle, sub-second billing",
            "**Faster Time-to-Market**: Deploy functions in minutes, not days",
            "**Built-in HA**: Automatic multi-AZ deployment and failover",
            "**Event Integration**: Native triggers from queues, streams, schedules",
            "**Reduced Ops Burden**: No patching, no capacity planning"
        ],
        "best_practices": [
            "Keep functions focused (single responsibility)",
            "Minimize cold starts with provisioned concurrency for critical paths",
            "Use environment variables for configuration",
            "Implement proper error handling and dead letter queues",
            "Use layers for shared code and dependencies",
            "Monitor with structured logging and distributed tracing"
        ],
        "anti_patterns": [
            "❌ Long-running processes (use containers instead)",
            "❌ Functions that maintain local state",
            "❌ Monolithic functions doing too much",
            "❌ Synchronous chains of Lambda calls",
            "❌ Ignoring cold start impact on latency-sensitive paths"
        ],
        "learning_resources": [
            "[AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)",
            "[Serverless Framework](https://www.serverless.com/framework/docs/)",
            "[AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/)"
        ]
    },

    "blockchain": {
        "title": "Why Blockchain?",
        "explanation": """Blockchain technology provides decentralized, immutable ledgers for trustless
transactions. By distributing data across many nodes with cryptographic verification,
blockchains eliminate the need for trusted intermediaries.

Smart contracts extend this concept by enabling programmable agreements that
execute automatically when conditions are met. This creates new possibilities
for DeFi, governance, supply chain tracking, and digital ownership.""",
        "how_it_works": """
**Core Concepts:**
- **Blocks**: Groups of transactions linked cryptographically
- **Consensus**: Agreement mechanism (PoW, PoS, etc.)
- **Smart Contracts**: Self-executing code on the blockchain
- **Wallets**: Public/private key pairs for signing transactions
- **Gas**: Fee for computation and storage

**Transaction Lifecycle:**
1. User signs transaction with private key
2. Transaction broadcast to network
3. Validators include in block
4. Block added to chain after consensus
5. Transaction finalized (immutable)
""",
        "code_example": '''```solidity
// Example: ERC-20 Token with Staking
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract StakingToken is ERC20, ReentrancyGuard, Ownable {
    // Staking state
    mapping(address => uint256) public stakedBalance;
    mapping(address => uint256) public stakingTimestamp;

    uint256 public constant REWARD_RATE = 100; // 1% per day (100 basis points)
    uint256 public constant MIN_STAKE_DURATION = 1 days;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount, uint256 reward);

    constructor() ERC20("StakingToken", "STK") {
        _mint(msg.sender, 1000000 * 10**decimals());
    }

    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot stake 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");

        // Claim any existing rewards first
        if (stakedBalance[msg.sender] > 0) {
            _claimRewards(msg.sender);
        }

        _transfer(msg.sender, address(this), amount);
        stakedBalance[msg.sender] += amount;
        stakingTimestamp[msg.sender] = block.timestamp;

        emit Staked(msg.sender, amount);
    }

    function unstake() external nonReentrant {
        uint256 staked = stakedBalance[msg.sender];
        require(staked > 0, "No staked balance");
        require(
            block.timestamp >= stakingTimestamp[msg.sender] + MIN_STAKE_DURATION,
            "Minimum stake duration not met"
        );

        uint256 reward = calculateReward(msg.sender);
        stakedBalance[msg.sender] = 0;

        _transfer(address(this), msg.sender, staked);
        if (reward > 0) {
            _mint(msg.sender, reward);
        }

        emit Unstaked(msg.sender, staked, reward);
    }

    function calculateReward(address user) public view returns (uint256) {
        if (stakedBalance[user] == 0) return 0;

        uint256 duration = block.timestamp - stakingTimestamp[user];
        uint256 daysStaked = duration / 1 days;

        return (stakedBalance[user] * REWARD_RATE * daysStaked) / 10000;
    }

    function _claimRewards(address user) internal {
        uint256 reward = calculateReward(user);
        if (reward > 0) {
            _mint(user, reward);
            stakingTimestamp[user] = block.timestamp;
        }
    }
}
```''',
        "benefits": [
            "**Immutability**: Transactions cannot be altered once confirmed",
            "**Decentralization**: No single point of failure or control",
            "**Transparency**: Public audit trail for all transactions",
            "**Smart Contracts**: Self-executing agreements reduce intermediaries",
            "**Tokenization**: Represent any asset digitally",
            "**Composability**: Smart contracts can interact (DeFi Legos)",
            "**Global Access**: Permissionless participation"
        ],
        "best_practices": [
            "Use established patterns (OpenZeppelin) for common functionality",
            "Implement comprehensive test suites including fuzzing",
            "Conduct security audits before mainnet deployment",
            "Use upgradeable proxy patterns for long-lived contracts",
            "Implement circuit breakers for emergency situations",
            "Follow checks-effects-interactions pattern"
        ],
        "anti_patterns": [
            "❌ Storing sensitive data on-chain (everything is public)",
            "❌ Unbounded loops that can run out of gas",
            "❌ External calls before state changes (reentrancy)",
            "❌ Using block.timestamp for critical logic",
            "❌ Deploying without thorough testing and audit"
        ],
        "learning_resources": [
            "[Ethereum Documentation](https://ethereum.org/developers/docs/)",
            "[Solidity by Example](https://solidity-by-example.org/)",
            "[OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)"
        ]
    },

    "iot": {
        "title": "Why IoT Architecture?",
        "explanation": """Internet of Things (IoT) architecture connects physical devices to cloud
services for data collection, analysis, and actuation. Modern IoT systems span
edge computing, communication protocols, time-series databases, and real-time
analytics—handling millions of devices generating continuous telemetry.

IoT enables digital twins, predictive maintenance, smart automation, and
data-driven insights from the physical world.""",
        "how_it_works": """
**IoT Architecture Layers:**
1. **Device Layer**: Sensors, actuators, microcontrollers
2. **Edge Layer**: Local processing, protocol translation
3. **Network Layer**: MQTT, CoAP, cellular, LoRaWAN
4. **Platform Layer**: Device management, message routing
5. **Application Layer**: Analytics, dashboards, ML models

**Data Flow:**
- Devices → Edge Gateway → Cloud Broker → Storage → Analytics
- Commands flow in reverse for actuation
""",
        "code_example": '''```python
# Example: IoT Device Simulator with MQTT
import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

class IoTDevice:
    """Simulated IoT sensor device."""

    def __init__(self, device_id: str, broker: str, port: int = 8883):
        self.device_id = device_id
        self.client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv5)

        # TLS configuration for secure connection
        self.client.tls_set(
            ca_certs='certs/root-ca.pem',
            certfile=f'certs/{device_id}.cert.pem',
            keyfile=f'certs/{device_id}.private.key'
        )

        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # Connect to broker
        self.client.connect(broker, port, keepalive=60)
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"Device {self.device_id} connected with code {rc}")
        # Subscribe to command topic
        client.subscribe(f"devices/{self.device_id}/commands")

    def _on_message(self, client, userdata, msg):
        print(f"Received command: {msg.payload.decode()}")
        command = json.loads(msg.payload.decode())
        self._handle_command(command)

    def _on_disconnect(self, client, userdata, rc):
        print(f"Device {self.device_id} disconnected")

    def _handle_command(self, command: dict):
        """Process commands from cloud."""
        if command.get('action') == 'reboot':
            print("Rebooting device...")
        elif command.get('action') == 'update_config':
            print(f"Updating config: {command.get('config')}")

    def publish_telemetry(self):
        """Publish sensor readings."""
        telemetry = {
            'device_id': self.device_id,
            'timestamp': datetime.utcnow().isoformat(),
            'sensors': {
                'temperature': round(random.uniform(20, 30), 2),
                'humidity': round(random.uniform(40, 60), 2),
                'pressure': round(random.uniform(1000, 1020), 2),
                'battery': round(random.uniform(80, 100), 1)
            },
            'metadata': {
                'firmware_version': '1.2.3',
                'signal_strength': random.randint(-80, -40)
            }
        }

        topic = f"devices/{self.device_id}/telemetry"
        self.client.publish(
            topic,
            json.dumps(telemetry),
            qos=1  # At least once delivery
        )
        print(f"Published: {telemetry['sensors']}")

    def run(self, interval: int = 5):
        """Main loop publishing telemetry at interval."""
        try:
            while True:
                self.publish_telemetry()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == '__main__':
    device = IoTDevice(
        device_id='sensor-001',
        broker='iot.example.com'
    )
    device.run(interval=10)
```''',
        "benefits": [
            "**Real-Time Data**: Continuous telemetry streams from physical world",
            "**Edge Processing**: Reduce latency with local compute",
            "**Scalability**: Handle millions of devices with managed services",
            "**Predictive Insights**: ML-powered anomaly detection and forecasting",
            "**Automation**: Trigger actions based on sensor data",
            "**Digital Twins**: Virtual representations of physical assets",
            "**Cost Optimization**: Predictive maintenance reduces downtime"
        ],
        "best_practices": [
            "Use TLS/mTLS for all device communication",
            "Implement device provisioning with unique credentials",
            "Design for intermittent connectivity (store-and-forward)",
            "Use time-series databases optimized for telemetry",
            "Implement firmware OTA updates with rollback",
            "Set up alerting on device health metrics"
        ],
        "anti_patterns": [
            "❌ Hardcoded credentials in device firmware",
            "❌ Unencrypted communication channels",
            "❌ Sending raw data without edge preprocessing",
            "❌ Ignoring device lifecycle management",
            "❌ Using relational databases for high-frequency telemetry"
        ],
        "learning_resources": [
            "[AWS IoT Documentation](https://docs.aws.amazon.com/iot/)",
            "[MQTT Protocol](https://mqtt.org/getting-started/)",
            "[TimescaleDB for IoT](https://docs.timescale.com/use-cases/latest/industrial-iot/)"
        ]
    },

    "monitoring": {
        "title": "Why Unified Observability?",
        "explanation": """Modern systems generate signals across three pillars: metrics, logs, and traces.
Siloed monitoring tools create blind spots—a spike in error rate (metric) needs
correlation with stack traces (logs) and request flow (traces) for effective debugging.

Unified observability platforms like Grafana combine these signals, enabling
engineers to understand system behavior holistically and reduce Mean Time to
Resolution (MTTR).""",
        "how_it_works": """
**Three Pillars of Observability:**
- **Metrics**: Numeric measurements over time (Prometheus)
- **Logs**: Discrete events with context (Loki)
- **Traces**: Request flow across services (Tempo/Jaeger)

**Correlation:**
- Trace ID links logs and traces
- Exemplars connect metrics to traces
- Labels/tags enable cross-signal queries

**Alerting Flow:**
1. Metrics trigger alert conditions
2. Alertmanager routes and deduplicates
3. Notifications sent to PagerDuty/Slack
4. Dashboard links provide investigation context
""",
        "code_example": '''```python
# Example: Instrumented FastAPI Application
from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog
import time

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="tempo:4317", insecure=True)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start_time = time.time()

    # Get trace context
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')

    # Add trace ID to logs
    log = logger.bind(
        trace_id=trace_id,
        method=request.method,
        path=request.url.path
    )

    try:
        response = await call_next(request)
        status = response.status_code
        log.info("request_completed", status=status)
    except Exception as e:
        status = 500
        log.error("request_failed", error=str(e))
        raise
    finally:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=status
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

    return response

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    with tracer.start_as_current_span("fetch_user") as span:
        span.set_attribute("user.id", user_id)
        logger.info("fetching_user", user_id=user_id)

        # Simulate database call
        with tracer.start_as_current_span("db_query"):
            await asyncio.sleep(0.05)

        return {"user_id": user_id, "name": "Example User"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```''',
        "benefits": [
            "**Unified View**: Correlate metrics, logs, and traces in one platform",
            "**Faster MTTR**: Quickly identify root cause with connected signals",
            "**Proactive Alerting**: Detect issues before users are impacted",
            "**Capacity Planning**: Historical data informs scaling decisions",
            "**SLO Tracking**: Measure and report on service level objectives",
            "**Cost Visibility**: Understand resource utilization",
            "**Team Collaboration**: Shared dashboards and runbooks"
        ],
        "best_practices": [
            "Instrument applications with OpenTelemetry for vendor neutrality",
            "Use structured logging with trace IDs for correlation",
            "Define SLOs with error budgets for reliability targets",
            "Create actionable alerts with runbook links",
            "Implement log sampling for high-volume services",
            "Use recording rules for frequently-used Prometheus queries"
        ],
        "anti_patterns": [
            "❌ Alert fatigue from too many low-value alerts",
            "❌ Separate tools without correlation capability",
            "❌ High-cardinality labels in Prometheus",
            "❌ Storing logs indefinitely without retention policy",
            "❌ Missing context in alerts (no runbook, no dashboard)"
        ],
        "learning_resources": [
            "[Grafana Documentation](https://grafana.com/docs/)",
            "[OpenTelemetry](https://opentelemetry.io/docs/)",
            "[Google SRE Book](https://sre.google/sre-book/table-of-contents/)"
        ]
    },

    "data-lake": {
        "title": "Why Data Lake Architecture?",
        "explanation": """Data lakes store raw data at scale in open formats, enabling diverse analytics
workloads from BI to machine learning. Unlike data warehouses that require
schema-on-write, data lakes use schema-on-read for flexibility.

The medallion architecture (Bronze/Silver/Gold) progressively refines data
quality while maintaining lineage. Delta Lake adds ACID transactions and
time travel to data lakes, combining the best of lakes and warehouses.""",
        "how_it_works": """
**Medallion Architecture:**
- **Bronze (Raw)**: Ingested data in original format
- **Silver (Cleaned)**: Validated, deduplicated, standardized
- **Gold (Curated)**: Business-level aggregates, ready for consumption

**Key Technologies:**
- **Storage**: S3, ADLS, GCS (object storage)
- **Format**: Parquet, Delta Lake, Iceberg
- **Compute**: Spark, Databricks, Athena
- **Catalog**: Glue Catalog, Hive Metastore, Unity Catalog
""",
        "code_example": '''```python
# Example: Delta Lake Medallion Architecture with PySpark
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import DeltaTable

spark = SparkSession.builder \\
    .appName("MedallionPipeline") \\
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \\
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \\
    .getOrCreate()

# Bronze Layer: Raw Ingestion
def ingest_to_bronze(source_path: str, bronze_path: str):
    """Ingest raw data to bronze layer."""
    raw_df = spark.read \\
        .format("json") \\
        .option("inferSchema", "true") \\
        .load(source_path)

    # Add metadata columns
    bronze_df = raw_df \\
        .withColumn("_ingested_at", current_timestamp()) \\
        .withColumn("_source_file", input_file_name())

    bronze_df.write \\
        .format("delta") \\
        .mode("append") \\
        .option("mergeSchema", "true") \\
        .save(bronze_path)

    return bronze_df

# Silver Layer: Cleaned and Validated
def bronze_to_silver(bronze_path: str, silver_path: str):
    """Transform bronze to silver with cleaning."""
    bronze_df = spark.read.format("delta").load(bronze_path)

    silver_df = bronze_df \\
        .dropDuplicates(["event_id"]) \\
        .filter(col("event_id").isNotNull()) \\
        .withColumn("event_date", to_date("timestamp")) \\
        .withColumn("amount", col("amount").cast("decimal(18,2)")) \\
        .withColumn("_processed_at", current_timestamp())

    # Merge for upsert semantics
    if DeltaTable.isDeltaTable(spark, silver_path):
        delta_table = DeltaTable.forPath(spark, silver_path)
        delta_table.alias("target").merge(
            silver_df.alias("source"),
            "target.event_id = source.event_id"
        ).whenMatchedUpdateAll() \\
         .whenNotMatchedInsertAll() \\
         .execute()
    else:
        silver_df.write.format("delta").save(silver_path)

# Gold Layer: Business Aggregates
def silver_to_gold(silver_path: str, gold_path: str):
    """Create business-level aggregates."""
    silver_df = spark.read.format("delta").load(silver_path)

    # Daily aggregates by customer
    gold_df = silver_df \\
        .groupBy("customer_id", "event_date") \\
        .agg(
            count("*").alias("total_events"),
            sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount"),
            countDistinct("product_id").alias("unique_products")
        ) \\
        .withColumn("_aggregated_at", current_timestamp())

    gold_df.write \\
        .format("delta") \\
        .mode("overwrite") \\
        .partitionBy("event_date") \\
        .save(gold_path)

# Time Travel Query
def query_as_of(path: str, version: int = None, timestamp: str = None):
    """Query historical data using Delta Lake time travel."""
    reader = spark.read.format("delta")

    if version is not None:
        reader = reader.option("versionAsOf", version)
    elif timestamp is not None:
        reader = reader.option("timestampAsOf", timestamp)

    return reader.load(path)

# Run pipeline
if __name__ == "__main__":
    ingest_to_bronze("s3://raw-data/events/", "s3://lake/bronze/events")
    bronze_to_silver("s3://lake/bronze/events", "s3://lake/silver/events")
    silver_to_gold("s3://lake/silver/events", "s3://lake/gold/daily_metrics")
```''',
        "benefits": [
            "**Schema-on-Read**: Store first, structure later for flexibility",
            "**Cost Effective**: Object storage is orders of magnitude cheaper",
            "**Open Formats**: Parquet, Delta Lake avoid vendor lock-in",
            "**Decoupling**: Separate storage from compute for optimization",
            "**ACID Transactions**: Delta Lake adds reliability to data lakes",
            "**Time Travel**: Query historical snapshots for auditing/debugging",
            "**Unified Analytics**: BI, ML, and streaming from same data"
        ],
        "best_practices": [
            "Use medallion architecture for progressive data quality",
            "Partition data by common query patterns (date, region)",
            "Implement data quality checks between layers",
            "Use Delta Lake or Iceberg for ACID guarantees",
            "Maintain data lineage for debugging and compliance",
            "Set up retention policies and optimize file sizes (ZORDER, OPTIMIZE)"
        ],
        "anti_patterns": [
            "❌ Small files problem (too many tiny Parquet files)",
            "❌ No data governance or catalog (data swamp)",
            "❌ Skipping Silver layer (Gold directly from Bronze)",
            "❌ Over-partitioning creating metadata overhead",
            "❌ Not handling late-arriving data in streaming"
        ],
        "learning_resources": [
            "[Delta Lake Documentation](https://docs.delta.io/)",
            "[Databricks Lakehouse](https://www.databricks.com/product/data-lakehouse)",
            "[Data Engineering with Apache Spark](https://spark.apache.org/docs/latest/)"
        ]
    }
}
