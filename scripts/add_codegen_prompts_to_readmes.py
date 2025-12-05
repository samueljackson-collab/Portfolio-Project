#!/usr/bin/env python3
"""
Add 'Code Generation Prompts' sections to all project READMEs.
"""

from pathlib import Path
from typing import Dict

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
PROJECTS_DIR = PROJECT_ROOT / "projects"

# Project type classifications for tailored prompts
PROJECT_TYPES = {
    "infrastructure": [
        "1-aws-infrastructure-automation", "9-multi-region-disaster-recovery",
        "p01-aws-infra", "p03-hybrid-network", "p10-multi-region", "p14-disaster-recovery",
        "p15-cost-optimization", "p17-terraform-multicloud"
    ],
    "data_processing": [
        "5-real-time-data-streaming", "7-serverless-data-processing",
        "11-iot-data-analytics", "16-advanced-data-lake", "p11-serverless", "p12-data-pipeline"
    ],
    "application": [
        "2-database-migration", "8-advanced-ai-chatbot", "15-real-time-collaboration",
        "p13-ha-webapp", "24-report-generator", "25-portfolio-website"
    ],
    "kubernetes": [
        "3-kubernetes-cicd", "19-advanced-kubernetes-operators",
        "17-multi-cloud-service-mesh", "p09-cloud-native-poc", "p18-k8s-cicd"
    ],
    "security": [
        "4-devsecops", "13-advanced-cybersecurity", "p02-iam-hardening",
        "p16-zero-trust", "p19-security-automation"
    ],
    "testing": [
        "p05-mobile-testing", "p06-e2e-testing", "p07-roaming-simulation", "p08-api-testing"
    ],
    "ml_ai": [
        "6-mlops-platform", "14-edge-ai-inference", "18-gpu-accelerated-computing",
        "astradup-video-deduplication"
    ],
    "blockchain": [
        "10-blockchain-smart-contract-platform", "20-blockchain-oracle-service"
    ],
    "monitoring": [
        "23-advanced-monitoring", "p04-ops-monitoring", "p20-observability"
    ],
    "quantum": [
        "12-quantum-computing", "21-quantum-safe-cryptography"
    ],
    "devops": [
        "22-autonomous-devops-platform"
    ]
}

def get_project_type(project_name: str) -> str:
    """Determine project type from project name."""
    for ptype, projects in PROJECT_TYPES.items():
        if project_name in projects:
            return ptype
    return "application"

def get_code_gen_prompts_section(project_name: str, project_type: str) -> str:
    """Generate Code Generation Prompts section based on project type."""

    # Type-specific prompt examples
    prompts_by_type = {
        "infrastructure": {
            "title": "Infrastructure as Code",
            "prompts": [
                ("Terraform Module", "Create a Terraform module for deploying a highly available VPC with public/private subnets across 3 availability zones, including NAT gateways and route tables"),
                ("CloudFormation Template", "Generate a CloudFormation template for an Auto Scaling Group with EC2 instances behind an Application Load Balancer, including health checks and scaling policies"),
                ("Monitoring Integration", "Write Terraform code to set up CloudWatch alarms for EC2 CPU utilization, RDS connections, and ALB target health with SNS notifications")
            ]
        },
        "kubernetes": {
            "title": "Kubernetes Resources",
            "prompts": [
                ("Deployment Manifest", "Create a Kubernetes Deployment manifest for a microservice with 3 replicas, resource limits (500m CPU, 512Mi memory), readiness/liveness probes, and rolling update strategy"),
                ("Helm Chart", "Generate a Helm chart for deploying a web application with configurable replicas, ingress, service, and persistent volume claims, including values for dev/staging/prod environments"),
                ("Custom Operator", "Write a Kubernetes operator in Go that watches for a custom CRD and automatically creates associated ConfigMaps, Secrets, and Services based on the custom resource spec")
            ]
        },
        "security": {
            "title": "Security Automation",
            "prompts": [
                ("IAM Policy", "Create an AWS IAM policy that follows principle of least privilege for a Lambda function that needs to read from S3, write to DynamoDB, and publish to SNS"),
                ("Security Scanning", "Generate a Python script that scans Docker images for vulnerabilities using Trivy, fails CI/CD if critical CVEs are found, and posts results to Slack"),
                ("Compliance Checker", "Write a script to audit AWS resources for CIS Benchmark compliance, checking security group rules, S3 bucket policies, and IAM password policies")
            ]
        },
        "data_processing": {
            "title": "Data Pipelines",
            "prompts": [
                ("ETL Pipeline", "Create a Python-based ETL pipeline using Apache Airflow that extracts data from PostgreSQL, transforms it with pandas, and loads it into a data warehouse with incremental updates"),
                ("Stream Processing", "Generate a Kafka consumer in Python that processes real-time events, performs aggregations using sliding windows, and stores results in Redis with TTL"),
                ("Data Quality", "Write a data validation framework that checks for schema compliance, null values, data freshness, and statistical anomalies, with alerting on failures")
            ]
        },
        "ml_ai": {
            "title": "Machine Learning Components",
            "prompts": [
                ("Training Pipeline", "Create a PyTorch training pipeline with data loaders, model checkpointing, TensorBoard logging, and early stopping for a classification task"),
                ("Model Serving", "Generate a FastAPI service that serves ML model predictions with request validation, batch inference support, and Prometheus metrics for latency/throughput"),
                ("Feature Engineering", "Write a feature engineering pipeline that handles missing values, encodes categorical variables, normalizes numerical features, and creates interaction terms")
            ]
        },
        "testing": {
            "title": "Test Automation",
            "prompts": [
                ("End-to-End Tests", "Create Playwright tests for a login flow, including form validation, authentication error handling, and successful redirect to dashboard"),
                ("API Tests", "Generate pytest-based API tests that verify REST endpoints for CRUD operations, including request/response validation, error cases, and authentication"),
                ("Performance Tests", "Write a Locust load test that simulates 100 concurrent users performing read/write operations, measures response times, and identifies bottlenecks")
            ]
        },
        "blockchain": {
            "title": "Smart Contract Development",
            "prompts": [
                ("Smart Contract", "Create a Solidity smart contract for an ERC-20 token with minting, burning, and transfer restrictions, including comprehensive access controls"),
                ("Contract Tests", "Generate Hardhat tests for smart contract functions covering normal operations, edge cases, access control, and gas optimization verification"),
                ("Deployment Script", "Write a deployment script that deploys smart contracts to multiple networks (local, testnet, mainnet), verifies contracts on Etherscan, and configures initial parameters")
            ]
        },
        "monitoring": {
            "title": "Observability Setup",
            "prompts": [
                ("Prometheus Rules", "Create Prometheus alerting rules for application health, including error rate thresholds, latency percentiles, and service availability with appropriate severity levels"),
                ("Grafana Dashboard", "Generate a Grafana dashboard JSON for microservices monitoring with panels for request rate, error rate, latency distribution, and resource utilization"),
                ("Log Aggregation", "Write a Fluentd configuration that collects logs from multiple sources, parses JSON logs, enriches with Kubernetes metadata, and forwards to Elasticsearch")
            ]
        },
        "quantum": {
            "title": "Quantum Computing",
            "prompts": [
                ("Quantum Circuit", "Create a Qiskit quantum circuit that implements Grover's algorithm for searching an unsorted database, including oracle construction and amplitude amplification"),
                ("Quantum Simulation", "Generate a quantum simulation using Cirq that models a quantum system's evolution, measures observables, and visualizes state probabilities"),
                ("Hybrid Algorithm", "Write a variational quantum eigensolver (VQE) implementation that combines quantum circuits with classical optimization for molecular energy calculations")
            ]
        },
        "devops": {
            "title": "DevOps Automation",
            "prompts": [
                ("CI/CD Pipeline", "Create a GitHub Actions workflow that builds, tests, scans for vulnerabilities, deploys to Kubernetes, and performs smoke tests with rollback on failure"),
                ("Infrastructure Provisioning", "Generate Ansible playbooks that provision servers, configure applications, set up monitoring agents, and enforce security baselines idempotently"),
                ("Incident Response", "Write a runbook automation script that detects service degradation, gathers diagnostic information, attempts auto-remediation, and escalates if needed")
            ]
        }
    }

    # Get prompts for this project type or use default
    prompt_config = prompts_by_type.get(project_type, {
        "title": "Code Components",
        "prompts": [
            ("Core Functionality", "Create the main application logic for [specific feature], including error handling, logging, and configuration management"),
            ("API Integration", "Generate code to integrate with [external service] API, including authentication, rate limiting, and retry logic"),
            ("Testing", "Write comprehensive tests for [component], covering normal operations, edge cases, and error scenarios")
        ]
    })

    # Build the section
    section = f'''
## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### {prompt_config["title"]}

'''

    for i, (title, prompt) in enumerate(prompt_config["prompts"], 1):
        section += f'''#### {i}. {title}
```
{prompt}
```

'''

    section += '''### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables

'''

    return section

def add_prompts_to_readme(readme_path: Path, project_name: str, project_type: str) -> bool:
    """Add Code Generation Prompts section to README if not already present."""

    if not readme_path.exists():
        print(f"  ⚠ README not found at {readme_path}")
        return False

    # Read current content
    content = readme_path.read_text()

    # Check if section already exists
    if "## Code Generation Prompts" in content or "# Code Generation Prompts" in content:
        print(f"  ⊗ Code Generation Prompts section already exists")
        return False

    # Generate new section
    new_section = get_code_gen_prompts_section(project_name, project_type)

    # Append to end of file
    updated_content = content.rstrip() + "\n\n" + new_section

    # Write back
    readme_path.write_text(updated_content)
    print(f"  ✓ Added Code Generation Prompts section")
    return True

def main():
    """Add Code Generation Prompts sections to all project READMEs."""
    print("=" * 80)
    print("Adding Code Generation Prompts sections to all project READMEs")
    print("=" * 80)

    # Get all project directories
    all_projects = [d for d in PROJECTS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]

    print(f"\nProcessing {len(all_projects)} projects...")
    print()

    updated_count = 0
    skipped_count = 0

    for project_dir in sorted(all_projects):
        project_name = project_dir.name
        project_type = get_project_type(project_name)

        print(f"{project_name} ({project_type}):")

        readme_path = project_dir / "README.md"
        if add_prompts_to_readme(readme_path, project_name, project_type):
            updated_count += 1
        else:
            skipped_count += 1

    print()
    print("=" * 80)
    print(f"✓ Complete!")
    print(f"  Updated: {updated_count} projects")
    print(f"  Skipped: {skipped_count} projects")
    print("=" * 80)

if __name__ == "__main__":
    main()
