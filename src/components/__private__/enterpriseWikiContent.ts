import type { RoleContent, RoleKey } from '../enterpriseWikiTypes';

// All of the textual curriculum lives in this file to keep the exported module
// lean. The UI consumes the exported record, but the data itself stays tucked
// away so it can be curated without noise in the rendering logic.
export const roleContent: Record<RoleKey, RoleContent> = {
  sde: {
    overview: {
      responsibilities: [
        'Design and implement highly available infrastructure',
        'Automate infrastructure provisioning with Terraform',
        'Implement monitoring and observability solutions',
        'Ensure system reliability and performance',
        'Manage multi-region deployments',
      ],
      skills: [
        'Infrastructure as Code (Terraform, CloudFormation)',
        'Cloud Platforms (AWS, Azure, GCP)',
        'Container Orchestration (Kubernetes, ECS)',
        'Monitoring & Observability (Prometheus, Grafana)',
        'Scripting (Python, Bash, Go)',
      ],
    },
    weeks: [
      {
        number: 1,
        title: 'Infrastructure Foundations',
        topics: [
          'Terraform AWS Setup',
          'VPC Design & Implementation',
          'Multi-AZ Architecture',
          'Security Groups & NACLs',
        ],
        deliverables: [
          'Complete VPC infrastructure',
          'Bastion host setup',
          'Network diagram',
          'Security documentation',
        ],
      },
      {
        number: 2,
        title: 'Compute & Load Balancing',
        topics: [
          'EC2 Auto Scaling Groups',
          'Application Load Balancer',
          'Launch Templates',
          'Health Checks',
        ],
        deliverables: [
          'Auto-scaling configuration',
          'ALB with SSL',
          'Health check endpoints',
          'Scaling policies',
        ],
      },
      {
        number: 3,
        title: 'Database & Storage',
        topics: [
          'RDS PostgreSQL Multi-AZ',
          'ElastiCache Redis Cluster',
          'S3 Buckets & Policies',
          'Database Backups',
        ],
        deliverables: [
          'Production database',
          'Cache configuration',
          'Backup strategy',
          'Recovery procedures',
        ],
      },
      {
        number: 4,
        title: 'Container Orchestration',
        topics: [
          'EKS Cluster Setup',
          'Node Groups Configuration',
          'Pod Security Policies',
          'Network Policies',
        ],
        deliverables: [
          'Production EKS cluster',
          'RBAC configuration',
          'Network policies',
          'Security scanning',
        ],
      },
      {
        number: 5,
        title: 'Monitoring & Observability',
        topics: [
          'Prometheus Setup',
          'Grafana Dashboards',
          'AlertManager Configuration',
          'Log Aggregation (ELK)',
        ],
        deliverables: [
          'Complete monitoring stack',
          'Custom dashboards',
          'Alert rules',
          'Log retention policies',
        ],
      },
      {
        number: 6,
        title: 'Event-Driven Architecture',
        topics: [
          'SQS Queue Configuration',
          'SNS Topics & Subscriptions',
          'EventBridge Rules',
          'Lambda Functions',
        ],
        deliverables: [
          'Message queue setup',
          'Event processing',
          'Dead letter queues',
          'Monitoring integration',
        ],
      },
      {
        number: 7,
        title: 'Disaster Recovery',
        topics: [
          'Backup Automation',
          'Cross-Region Replication',
          'Failover Procedures',
          'DR Testing',
        ],
        deliverables: [
          'DR plan documentation',
          'Automated backups',
          'Failover runbooks',
          'Test results',
        ],
      },
      {
        number: 8,
        title: 'Security Hardening',
        topics: [
          'IAM Policies & Roles',
          'Secrets Management',
          'Security Scanning',
          'Compliance Auditing',
        ],
        deliverables: [
          'Security baseline',
          'Secrets rotation',
          'Audit reports',
          'Compliance documentation',
        ],
      },
    ],
  },
  devops: {
    overview: {
      responsibilities: [
        'Design and maintain CI/CD pipelines',
        'Implement GitOps workflows',
        'Automate deployment processes',
        'Manage configuration as code',
        'Ensure zero-downtime deployments',
      ],
      skills: [
        'CI/CD Tools (GitHub Actions, GitLab CI, Jenkins)',
        'GitOps (ArgoCD, Flux)',
        'Configuration Management (Ansible, Chef)',
        'Container Technologies (Docker, Kubernetes)',
        'Scripting & Automation',
      ],
    },
    weeks: [
      {
        number: 1,
        title: 'CI/CD Pipeline Setup',
        topics: [
          'GitHub Actions Workflows',
          'Multi-stage Pipelines',
          'Security Scanning',
          'Artifact Management',
        ],
        deliverables: [
          'Complete CI pipeline',
          'Security gates',
          'Test automation',
          'Build optimization',
        ],
      },
      {
        number: 2,
        title: 'GitOps Implementation',
        topics: [
          'ArgoCD Installation',
          'Application Manifests',
          'Automated Sync',
          'Rollback Strategies',
        ],
        deliverables: [
          'ArgoCD setup',
          'GitOps repository',
          'Sync policies',
          'Rollback procedures',
        ],
      },
      {
        number: 3,
        title: 'Configuration Management',
        topics: [
          'Ansible Playbooks',
          'Inventory Management',
          'Role Development',
          'Vault Integration',
        ],
        deliverables: [
          'Ansible repository',
          'Server configuration',
          'Secret management',
          'Deployment automation',
        ],
      },
      {
        number: 4,
        title: 'Container Registry',
        topics: [
          'Registry Setup',
          'Image Scanning',
          'Vulnerability Management',
          'Image Signing',
        ],
        deliverables: [
          'Container registry',
          'Scanning pipeline',
          'Security policies',
          'Image lifecycle',
        ],
      },
      {
        number: 5,
        title: 'Deployment Strategies',
        topics: [
          'Blue-Green Deployments',
          'Canary Releases',
          'Rolling Updates',
          'Feature Flags',
        ],
        deliverables: [
          'Deployment manifests',
          'Traffic management',
          'Rollback automation',
          'Feature flag system',
        ],
      },
      {
        number: 6,
        title: 'Pipeline Optimization',
        topics: [
          'Build Caching',
          'Parallel Execution',
          'Resource Optimization',
          'Cost Management',
        ],
        deliverables: [
          'Optimized pipelines',
          'Performance metrics',
          'Cost analysis',
          'Best practices guide',
        ],
      },
    ],
  },
  qa: {
    overview: {
      responsibilities: [
        'Design comprehensive test strategies',
        'Implement test automation frameworks',
        'Perform security and performance testing',
        'Establish quality gates',
        'Lead testing best practices',
      ],
      skills: [
        'Test Automation (Cypress, Playwright, Selenium)',
        'API Testing (Postman, REST Assured)',
        'Performance Testing (K6, JMeter)',
        'Security Testing (OWASP ZAP, Burp Suite)',
        'Test Strategy & Planning',
      ],
    },
    weeks: [
      {
        number: 1,
        title: 'Test Framework Setup',
        topics: [
          'Jest Configuration',
          'Cypress Setup',
          'Test Structure',
          'Code Coverage',
        ],
        deliverables: [
          'Unit test framework',
          'E2E test suite',
          'Coverage reports',
          'Testing guidelines',
        ],
      },
      {
        number: 2,
        title: 'API Testing',
        topics: [
          'REST API Testing',
          'GraphQL Testing',
          'Contract Testing',
          'Mock Services',
        ],
        deliverables: [
          'API test suite',
          'Contract tests',
          'Mock server setup',
          'Test data management',
        ],
      },
      {
        number: 3,
        title: 'E2E Testing',
        topics: [
          'User Flow Testing',
          'Cross-browser Testing',
          'Mobile Testing',
          'Visual Regression',
        ],
        deliverables: [
          'E2E test scenarios',
          'Browser matrix',
          'Visual tests',
          'Test reports',
        ],
      },
      {
        number: 4,
        title: 'Performance Testing',
        topics: [
          'Load Testing',
          'Stress Testing',
          'Spike Testing',
          'Endurance Testing',
        ],
        deliverables: [
          'Performance test suite',
          'Load profiles',
          'Performance benchmarks',
          'Optimization recommendations',
        ],
      },
      {
        number: 5,
        title: 'Security Testing',
        topics: [
          'OWASP Top 10',
          'Penetration Testing',
          'Vulnerability Scanning',
          'Security Reports',
        ],
        deliverables: [
          'Security test plan',
          'Vulnerability reports',
          'Remediation tracking',
          'Security baseline',
        ],
      },
      {
        number: 6,
        title: 'CI/CD Integration',
        topics: [
          'Automated Testing',
          'Quality Gates',
          'Test Reporting',
          'Failure Analysis',
        ],
        deliverables: [
          'CI test integration',
          'Quality metrics',
          'Automated reports',
          'Failure handling',
        ],
      },
    ],
  },
  architect: {
    overview: {
      responsibilities: [
        'Design scalable system architectures',
        'Make technology decisions',
        'Define architecture patterns',
        'Ensure security and compliance',
        'Lead technical reviews',
      ],
      skills: [
        'System Design & Architecture Patterns',
        'Cloud Architecture (AWS, Azure, Multi-cloud)',
        'Microservices & Event-driven Architecture',
        'Security & Compliance',
        'Technical Leadership',
      ],
    },
    weeks: [
      {
        number: 1,
        title: 'Architecture Fundamentals',
        topics: [
          'Design Principles',
          'Architecture Patterns',
          'Trade-off Analysis',
          'System Requirements',
        ],
        deliverables: [
          'Architecture principles',
          'Pattern catalog',
          'Decision framework',
          'Requirements template',
        ],
      },
      {
        number: 2,
        title: 'Microservices Design',
        topics: [
          'Service Boundaries',
          'API Gateway Patterns',
          'Service Mesh',
          'Data Management',
        ],
        deliverables: [
          'Service architecture',
          'API specifications',
          'Data flow diagrams',
          'Integration patterns',
        ],
      },
      {
        number: 3,
        title: 'Event-Driven Architecture',
        topics: [
          'Event Sourcing',
          'CQRS Pattern',
          'Message Brokers',
          'Event Choreography',
        ],
        deliverables: [
          'Event architecture',
          'Message schemas',
          'Event flows',
          'Consistency patterns',
        ],
      },
      {
        number: 4,
        title: 'Scalability Patterns',
        topics: [
          'Horizontal Scaling',
          'Caching Strategies',
          'Database Sharding',
          'CDN Integration',
        ],
        deliverables: [
          'Scaling strategy',
          'Cache architecture',
          'Database design',
          'Performance plan',
        ],
      },
      {
        number: 5,
        title: 'Security Architecture',
        topics: [
          'Zero Trust Security',
          'Identity & Access',
          'Data Encryption',
          'Compliance Framework',
        ],
        deliverables: [
          'Security architecture',
          'IAM design',
          'Encryption strategy',
          'Compliance checklist',
        ],
      },
      {
        number: 6,
        title: 'Resilience Patterns',
        topics: [
          'Circuit Breakers',
          'Retry Policies',
          'Bulkheads',
          'Chaos Engineering',
        ],
        deliverables: [
          'Resilience patterns',
          'Fault tolerance',
          'Recovery procedures',
          'Testing strategy',
        ],
      },
      {
        number: 7,
        title: 'Multi-Region Architecture',
        topics: [
          'Global Load Balancing',
          'Data Replication',
          'Disaster Recovery',
          'Latency Optimization',
        ],
        deliverables: [
          'Multi-region design',
          'Replication strategy',
          'DR plan',
          'Performance metrics',
        ],
      },
      {
        number: 8,
        title: 'Cost Optimization',
        topics: [
          'Resource Optimization',
          'Reserved Capacity',
          'Right-sizing',
          'Cost Monitoring',
        ],
        deliverables: [
          'Cost architecture',
          'Optimization plan',
          'Budget forecasts',
          'Cost dashboards',
        ],
      },
    ],
  },
};
