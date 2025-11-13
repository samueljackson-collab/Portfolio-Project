export interface TechnicalImplementation {
  fileName: string
  language: string
  code: string
}

export interface DocumentSection {
  title: string
  content: string
}

export interface Project {
  id: string
  category: string
  title: string
  description: string
  strategicDocs: DocumentSection
  technicalImpl: TechnicalImplementation[]
  operationalMats: DocumentSection
}

export interface PortfolioProfile {
  name: string
  title: string
  summary: string
}

export interface PortfolioData {
  profile: PortfolioProfile
  projects: Project[]
}

export type ProjectGroups = Record<string, Project[]>

export const portfolioData: PortfolioData = {
  profile: {
    name: 'Samuel Jackson',
    title: 'Principal Cloud & Security Architect',
    summary:
      'Leader of cloud platform, DevOps, and security initiatives for global engineering teams. Passionate about building resilient systems, simplifying developer workflows, and aligning technical execution with enterprise risk goals.',
  },
  projects: [
    {
      id: 'p01',
      category: 'Cloud & Infrastructure',
      title: 'AWS Landing Zone Accelerator',
      description:
        'Delivered a reusable AWS landing zone with account vending, identity federation, and network baselines. The solution standardized tagging, guardrails, and observability across 20+ business units.',
      strategicDocs: {
        title: 'Cloud Operating Model Brief',
        content:
          'Adopt a centralized landing zone team that publishes versioned infrastructure modules. Application teams inherit secure-by-default accounts, while the platform group maintains shared services such as logging, guardrails, and network connectivity.',
      },
      technicalImpl: [
        {
          fileName: 'terraform/providers.tf',
          language: 'hcl',
          code: `terraform {
  required_version = ">= 1.6.0"
  backend "s3" {
    bucket = "corp-landing-zone-state"
    key    = "global/root.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Owner       = "Platform"
      Environment = "Shared"
    }
  }
}
`,
        },
        {
          fileName: 'terraform/modules/network/main.tf',
          language: 'hcl',
          code: `resource "aws_vpc" "core" {
  cidr_block           = "10.10.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.core.id
  cidr_block              = cidrsubnet(aws_vpc.core.cidr_block, 4, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
}
`,
        },
      ],
      operationalMats: {
        title: 'Runbook: New Account Provisioning',
        content:
          '1. Intake request via ServiceNow. 2. Trigger the account vending pipeline with business metadata. 3. Verify baseline controls (CloudTrail, GuardDuty, SCPs). 4. Publish account information and IAM roles to the requesting team.',
      },
    },
    {
      id: 'p02',
      category: 'DevOps & Platform',
      title: 'Managed Kubernetes Platform',
      description:
        'Built a hardened Amazon EKS stack with GitOps deployments, add-on lifecycle automation, and golden observability dashboards. Reduced cluster provisioning time from weeks to hours.',
      strategicDocs: {
        title: 'Container Strategy Highlights',
        content:
          'Standardize on a managed control plane (EKS) with Fleet-level add-on management. Enforce namespace isolation, admission policies, and signed images. Integrate cluster onboarding with the landing zone so that network, DNS, and secrets management are pre-approved.',
      },
      technicalImpl: [
        {
          fileName: 'terraform/modules/eks/main.tf',
          language: 'hcl',
          code: `module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.8.4"

  cluster_name    = "enterprise-platform"
  cluster_version = "1.29"
  vpc_id          = var.vpc_id
  subnet_ids      = var.private_subnets

  eks_managed_node_groups = {
    default = {
      instance_types = ["t3.large"]
      desired_size   = 3
      min_size       = 3
      max_size       = 6
    }
  }
}
`,
        },
        {
          fileName: 'gitops/apps/cluster-addons.yaml',
          language: 'yaml',
          code: `apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: platform-addons
  namespace: argocd
spec:
  project: platform
  source:
    repoURL: https://github.com/org/cluster-addons.git
    path: base
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: addons
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
`,
        },
      ],
      operationalMats: {
        title: 'Playbook: Cluster Upgrades',
        content:
          'Run preflight checks (deprecated API scan, load testing). Upgrade the control plane via Terraform, then roll managed node groups one at a time. Validate metrics, restart GitOps sync, and notify application teams once the upgrade passes smoke tests.',
      },
    },
    {
      id: 'p03',
      category: 'Cloud Networking',
      title: 'Multi-Cloud Transit Fabric',
      description:
        'Designed a resilient network mesh between AWS, Azure, and the on-prem core using transit gateways and redundant VPN tunnels. Enabled secure data replication and shared services across environments.',
      strategicDocs: {
        title: 'Connectivity Design Notes',
        content:
          'Use AWS Transit Gateway as the aggregation hub and connect Azure Virtual WAN plus the MPLS edge. Apply consistent segmentation tags, shared services route tables, and automated health checks. Logging is centralized in the SIEM for every tunnel.',
      },
      technicalImpl: [
        {
          fileName: 'aws/transit-gateway.tf',
          language: 'hcl',
          code: `resource "aws_ec2_transit_gateway" "main" {
  description = "enterprise-core"
  amazon_side_asn = 64512
  default_route_table_association = "disable"
  default_route_table_propagation = "disable"
}

resource "aws_vpn_connection" "azure" {
  customer_gateway_id = aws_customer_gateway.azure.id
  transit_gateway_id  = aws_ec2_transit_gateway.main.id
  type                = "ipsec.1"
}
`,
        },
      ],
      operationalMats: {
        title: 'Runbook: Tunnel Troubleshooting',
        content:
          '1. Confirm the VPN status in AWS and Azure portals. 2. Validate BGP route advertisements. 3. Review security group and NSG rules. 4. Capture packets on both sides to confirm traffic flow. 5. Escalate to carrier if latency or packet loss persists.',
      },
    },
    {
      id: 'p04',
      category: 'DevOps & Platform',
      title: 'GitOps & Secure CI/CD',
      description:
        'Implemented a GitLab CI pipeline with automated testing, container scanning, and progressive deployments through Argo CD. Security gates are enforced without slowing down developer feedback.',
      strategicDocs: {
        title: 'Shift-Left Guidance',
        content:
          'Integrate SAST, dependency scanning, and container scanning directly into merge requests. Fail fast on critical issues, but allow engineers to request temporary exceptions with documented risk owners.',
      },
      technicalImpl: [
        {
          fileName: '.gitlab-ci.yml',
          language: 'yaml',
          code: `stages:
  - build
  - test
  - scan
  - deploy

build-image:
  stage: build
  image: gcr.io/kaniko-project/executor:v1.21.0
  script:
    - /kaniko/executor --context $CI_PROJECT_DIR --dockerfile Dockerfile --destination $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

dependency-scan:
  stage: scan
  image: aquasec/trivy:latest
  script:
    - trivy fs . --severity HIGH,CRITICAL --exit-code 1
`,
        },
      ],
      operationalMats: {
        title: 'Vulnerability Response',
        content:
          'When the pipeline fails on a critical finding, notify the feature squad immediately, log a Jira ticket, and pair with the security champion to determine remediation or a documented exception.',
      },
    },
    {
      id: 'p05',
      category: 'Software Delivery',
      title: 'Polyglot Event Processing Platform',
      description:
        'Created a message-driven architecture with FastAPI workers, Node.js APIs, and RabbitMQ. Enabled traceability and autoscaling for media processing workloads.',
      strategicDocs: {
        title: 'Service Architecture Snapshot',
        content:
          'Expose external traffic through a Node.js gateway, fan out events via RabbitMQ, and process data inside Python workers. Use structured logging plus OpenTelemetry so each job can be traced end-to-end.',
      },
      technicalImpl: [
        {
          fileName: 'services/api-gateway/index.js',
          language: 'javascript',
          code: `const express = require('express')
const amqp = require('amqplib')
const { v4: uuid } = require('uuid')

const app = express()
app.use(express.json())

let channel

async function initQueue() {
  const connection = await amqp.connect('amqp://rabbitmq')
  channel = await connection.createChannel()
  await channel.assertQueue('tasks', { durable: true })
}

app.post('/jobs', async (req, res) => {
  if (!channel) {
    return res.status(503).send('Queue not ready')
  }
  const jobId = uuid()
  channel.sendToQueue('tasks', Buffer.from(JSON.stringify({ jobId, payload: req.body })), { persistent: true })
  res.status(202).json({ jobId })
})

initQueue()
app.listen(3000)
`,
        },
      ],
      operationalMats: {
        title: 'Runbook: Queue Lag',
        content:
          'Monitor queue depth, scale worker deployments horizontally, and investigate any poison messages by replaying them through a sandbox environment.',
      },
    },
    {
      id: 'p06',
      category: 'Security & Resilience',
      title: 'Incident Response Modernization',
      description:
        'Authored incident response playbooks, tabletop exercises, and automation hooks for ransomware scenarios. Reduced response time by aligning tooling, communications, and decision records.',
      strategicDocs: {
        title: 'Incident Policy Summary',
        content:
          'All employees must report suspected incidents immediately. The CSIRT is empowered to isolate systems, revoke access, and coordinate executive briefings following the NIST 800-61 framework.',
      },
      technicalImpl: [
        {
          fileName: 'automation/isolate-instance.sh',
          language: 'bash',
          code: `#!/usr/bin/env bash
INSTANCE_ID=$1
aws ec2 modify-instance-attribute --instance-id "$INSTANCE_ID" --no-source-dest-check
aws ec2 create-tags --resources "$INSTANCE_ID" --tags Key=Quarantine,Value=true
`,
        },
      ],
      operationalMats: {
        title: 'Tabletop Highlights',
        content:
          'During quarterly exercises, rehearse executive communications, validate that backups remain offline, and capture improvement actions for tooling and staffing.',
      },
    },
  ],
}
