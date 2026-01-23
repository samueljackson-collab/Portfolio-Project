---
title: "AWS Infrastructure Automation"
description: "Production-ready AWS environment using Terraform, CDK, and Pulumi. Features Multi-AZ VPC, EKS cluster, and RDS PostgreSQL."
published: true
date: 2026-01-23T15:24:46.000Z
tags:
  - aws
  - terraform
  - infrastructure
  - eks
  - rds
editor: markdown
dateCreated: 2026-01-23T15:24:46.000Z
---


# AWS Infrastructure Automation

> **Status**: Production Ready | **Completion**: [██████████] 100%
>
> `aws` `terraform` `infrastructure` `eks` `rds`

Production-ready AWS environment using Terraform, CDK, and Pulumi. Features Multi-AZ VPC, EKS cluster, and RDS PostgreSQL.

---


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


## 🎯 Problem Statement

### The Infrastructure Challenge

In traditional infrastructure management, teams face a cascade of challenges
that compound over time:

**Configuration Drift**: When infrastructure is managed manually through console clicks or
ad-hoc scripts, configurations inevitably diverge between environments. What works in
staging mysteriously fails in production. Teams spend hours comparing configurations
trying to find the difference.

**Knowledge Silos**: Tribal knowledge about "how the network is set up" lives in the
heads of senior engineers. When they leave, critical institutional knowledge walks
out the door. New team members spend weeks just understanding the current state.

**Audit Nightmares**: Compliance requires knowing who changed what, when, and why.
With manual changes, the audit trail is scattered across CloudTrail logs, Slack
messages, and incomplete runbooks. SOC 2 auditors are not amused.

**Disaster Recovery**: Can you recreate your entire infrastructure from scratch? Most
teams discover the answer is "maybe, eventually" only when they actually need to.


**Business Impact:**
- Mean Time to Recovery (MTTR) measured in days, not minutes
- Production incidents from environment inconsistencies
- Failed audits and compliance findings
- Knowledge loss during team transitions
- Slow onboarding for new engineers


### How This Project Solves It


**Infrastructure as Code (IaC) transforms this reality:**

1. **Declarative Definition**: Infrastructure is defined in code, version-controlled,
   and reviewed like application code. The "desired state" is explicit.

2. **Reproducibility**: Any environment can be recreated from code. Spin up identical
   environments for testing, demos, or disaster recovery.

3. **Change Management**: Pull requests for infrastructure changes enable peer review,
   automated validation, and clear audit trails.

4. **Automation**: CI/CD pipelines apply infrastructure changes consistently, with
   plan previews before execution.


### Key Capabilities Delivered

- ✅ **Multi-AZ VPC architecture**
- ✅ **Managed EKS Cluster**
- ✅ **RDS PostgreSQL with backups**
- ✅ **Automated DR drills**
- ✅ **Cost estimation scripts**

---


## 🎓 Learning Objectives

By studying and implementing this project, you will:

   1. Understand Infrastructure as Code principles and benefits
   2. Design multi-AZ architectures for high availability
   3. Implement secure networking with VPCs, subnets, and security groups
   4. Configure managed Kubernetes clusters for container orchestration
   5. Set up automated backup and disaster recovery procedures

**Prerequisites:**
- Basic understanding of cloud services (AWS/GCP/Azure)
- Familiarity with containerization (Docker)
- Command-line proficiency (Bash/Linux)
- Version control with Git

**Estimated Learning Time:** 15-25 hours for full implementation

---


## 🏗️ Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AWS Infrastructure Automation                        │
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

### Component Breakdown

**Network Layer**
- VPC, Subnets, Route Tables, NAT Gateway, Internet Gateway

**Compute Layer**
- EKS Cluster, Node Groups, Auto Scaling, Spot Instances

**Data Layer**
- RDS PostgreSQL, Multi-AZ Deployment, Read Replicas, Automated Backups

**Security Layer**
- IAM Roles, Security Groups, KMS Encryption, Secrets Manager

### Data Flow

`User Request → Load Balancer → Ingress → Service → Pod → Database`

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Multi-AZ Deployment | Ensures high availability during AZ failures |
| Managed Services | Reduces operational burden, focus on business logic |
| Infrastructure as Code | Reproducibility, version control, audit trail |
| GitOps Workflow | Single source of truth, automated reconciliation |

---


## 🛠️ Tech Stack

### Technologies Used

| Technology | Purpose & Rationale |
|------------|---------------------|
| **Terraform** | Infrastructure as Code - declarative, version-controlled resource management across cloud providers |
| **AWS CDK** | Type-safe infrastructure definitions using TypeScript/Python with compile-time validation |
| **Pulumi** | Multi-language IaC supporting Python, TypeScript, Go with real programming constructs |
| **Python** | Primary automation language for scripts, data processing, and ML pipelines |
| **Bash** | Shell scripting for system integration and CI/CD pipeline steps |

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

## 🔬 Technology Deep Dives

### 📚 Why AWS?

Amazon Web Services (AWS) is the world's most comprehensive cloud platform,
offering 200+ services from data centers globally. Launched in 2006, it pioneered
cloud computing and maintains market leadership with the largest ecosystem.

AWS provides the building blocks for virtually any workload—from simple web hosting
to complex machine learning pipelines—with enterprise-grade security, compliance,
and global infrastructure.

#### How It Works


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


#### Working Code Example

```python
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
```

#### Key Benefits

- **Market Leader**: Largest ecosystem with extensive documentation and community
- **Global Infrastructure**: 30+ regions for low-latency deployments worldwide
- **Service Breadth**: Compute, storage, ML, IoT, analytics under one roof
- **Pay-as-you-go**: Optimize costs with granular per-second billing
- **Enterprise Ready**: Compliance certifications (SOC, HIPAA, PCI, FedRAMP)
- **Innovation Pace**: 2000+ new features/services annually
- **Mature IaC**: CloudFormation, CDK, and excellent Terraform support

#### Best Practices

- ✅ Use IAM roles instead of access keys where possible
- ✅ Enable CloudTrail for API audit logging
- ✅ Implement VPC for network isolation
- ✅ Use AWS Organizations for multi-account strategy
- ✅ Enable S3 versioning and encryption by default
- ✅ Set up billing alerts and cost allocation tags

#### Common Pitfalls to Avoid

- ❌ Hardcoding credentials in code or config files
- ❌ Using root account for daily operations
- ❌ Public S3 buckets without explicit business need
- ❌ Single AZ deployments for production workloads
- ❌ Ignoring Reserved Instances/Savings Plans for steady-state workloads

#### Further Reading

- [AWS Documentation](https://docs.aws.amazon.com/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Certification Path](https://aws.amazon.com/certification/)

---

### 📚 Why Terraform?

Terraform is HashiCorp's Infrastructure as Code (IaC) tool that enables
declarative infrastructure management across multiple cloud providers. It uses HCL (HashiCorp
Configuration Language) to define resources in a human-readable format.

Unlike imperative approaches where you specify *how* to create infrastructure, Terraform's
declarative model lets you specify *what* you want. Terraform figures out the creation order,
handles dependencies, and maintains state to track what exists.

#### How It Works


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


#### Working Code Example

```hcl
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
```

#### Key Benefits

- **Provider Agnostic**: Single workflow for AWS, GCP, Azure, and 100+ providers
- **State Management**: Tracks infrastructure state for safe modifications
- **Plan Before Apply**: Preview changes before execution reduces risk
- **Modular Design**: Reusable modules promote DRY principles
- **Version Control Friendly**: Text-based configs integrate with Git workflows
- **Dependency Graph**: Automatically determines resource creation order
- **Idempotent Operations**: Running apply multiple times yields same result

#### Best Practices

- ✅ Use remote state storage (S3, GCS) with state locking (DynamoDB)
- ✅ Implement workspaces or directory structure for environment separation
- ✅ Pin provider versions to avoid unexpected breaking changes
- ✅ Use modules for reusable infrastructure components
- ✅ Never commit `.tfstate` files or secrets to version control
- ✅ Implement `terraform fmt` and `terraform validate` in CI pipelines

#### Common Pitfalls to Avoid

- ❌ Storing state locally in team environments
- ❌ Hardcoding values instead of using variables
- ❌ Creating monolithic configurations instead of modules
- ❌ Ignoring plan output before applying changes
- ❌ Manual changes to infrastructure outside Terraform

#### Further Reading

- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Terraform Up & Running (Book)](https://www.terraformupandrunning.com/)

---



## 📖 Implementation Guide

This section provides production-ready code you can adapt for your own projects.

### Vpc

```hcl
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
```

### Eks

```python
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
```

### Rds

```hcl
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
```

---


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
cd Portfolio-Project/projects/1-aws-infrastructure-automation
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


## 🌍 Real-World Scenarios

These scenarios demonstrate how this project applies to actual business situations.

### Scenario: Black Friday Traffic Surge

**Challenge:** E-commerce platform needs to handle 10x normal traffic for 48 hours

**Solution:** Pre-provisioned capacity defined in Terraform, auto-scaling policies, and load testing validation ensure seamless scaling

---

### Scenario: Region Outage Recovery

**Challenge:** Primary AWS region experiences extended outage

**Solution:** Multi-region infrastructure in code enables spinning up DR environment in alternate region within RTO

---

### Scenario: Security Compliance Audit

**Challenge:** SOC 2 auditor requests complete infrastructure change history

**Solution:** Git history provides complete audit trail of all infrastructure changes with approvers and timestamps

---



## 🔗 Related Projects

Explore these related projects that share technologies or concepts:

| Project | Description | Shared Tags |
|---------|-------------|-------------|
| [Multi-Region Disaster Recovery](/projects/multi-region-disaster-recovery) | Resilient architecture with automated failover bet... | 2 |

---


## 📚 Resources

### Project Links

| Resource | Link |
|----------|------|
| 📂 Source Code | [GitHub Repository](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/1-aws-infrastructure-automation) |
| 📖 Documentation | [`projects/1-aws-infrastructure-automation/docs/`](projects/1-aws-infrastructure-automation/docs/) |
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

**Last Updated:** 2026-01-23 |
**Version:** 3.0 |
**Generated by:** Portfolio Wiki Content Generator

*Found this helpful? Star the repository!*

</div>
