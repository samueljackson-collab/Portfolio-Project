#!/usr/bin/env python3
"""
Generate missing deliverables for all portfolio projects based on the gap analysis checklist.
Creates observability configs, CI/CD workflows, IaC artifacts, tests, ADRs, and code generation prompts.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
PROJECTS_DIR = PROJECT_ROOT / "projects"

# Project type classifications
PROJECT_TYPES = {
    "infrastructure": [
        "1-aws-infrastructure-automation",
        "9-multi-region-disaster-recovery",
        "p01-aws-infra",
        "p03-hybrid-network",
        "p10-multi-region",
        "p14-disaster-recovery",
        "p15-cost-optimization",
        "p17-terraform-multicloud",
    ],
    "data_processing": [
        "5-real-time-data-streaming",
        "7-serverless-data-processing",
        "11-iot-data-analytics",
        "16-advanced-data-lake",
        "p11-serverless",
        "p12-data-pipeline",
    ],
    "application": [
        "2-database-migration",
        "8-advanced-ai-chatbot",
        "15-real-time-collaboration",
        "p13-ha-webapp",
        "24-report-generator",
        "25-portfolio-website",
    ],
    "kubernetes": [
        "3-kubernetes-cicd",
        "19-advanced-kubernetes-operators",
        "17-multi-cloud-service-mesh",
        "p09-cloud-native-poc",
        "p18-k8s-cicd",
    ],
    "security": [
        "4-devsecops",
        "13-advanced-cybersecurity",
        "p02-iam-hardening",
        "p16-zero-trust",
        "p19-security-automation",
    ],
    "testing": [
        "p05-mobile-testing",
        "p06-e2e-testing",
        "p07-roaming-simulation",
        "p08-api-testing",
    ],
    "ml_ai": [
        "6-mlops-platform",
        "14-edge-ai-inference",
        "18-gpu-accelerated-computing",
        "astradup-video-deduplication",
    ],
    "blockchain": [
        "10-blockchain-smart-contract-platform",
        "20-blockchain-oracle-service",
    ],
    "monitoring": ["23-advanced-monitoring", "p04-ops-monitoring", "p20-observability"],
    "quantum": ["12-quantum-computing", "21-quantum-safe-cryptography"],
    "devops": ["22-autonomous-devops-platform"],
}


def create_prometheus_config(project_name: str, project_type: str) -> str:
    """Generate Prometheus configuration based on project type."""
    base_config = {
        "global": {
            "scrape_interval": "15s",
            "evaluation_interval": "15s",
            "external_labels": {"cluster": project_name, "environment": "production"},
        },
        "alerting": {
            "alertmanagers": [{"static_configs": [{"targets": ["alertmanager:9093"]}]}]
        },
        "rule_files": ["rules.yml"],
        "scrape_configs": [],
    }

    # Add scrape configs based on project type
    if project_type == "infrastructure":
        base_config["scrape_configs"] = [
            {
                "job_name": "cloudwatch-exporter",
                "static_configs": [{"targets": ["cloudwatch-exporter:9106"]}],
            },
            {
                "job_name": "node-exporter",
                "static_configs": [{"targets": ["node-exporter:9100"]}],
            },
        ]
    elif project_type == "kubernetes":
        base_config["scrape_configs"] = [
            {
                "job_name": "kubernetes-nodes",
                "kubernetes_sd_configs": [{"role": "node"}],
            },
            {"job_name": "kubernetes-pods", "kubernetes_sd_configs": [{"role": "pod"}]},
        ]
    elif project_type == "data_processing":
        base_config["scrape_configs"] = [
            {
                "job_name": "pipeline-metrics",
                "static_configs": [{"targets": ["pipeline:8080"]}],
                "metrics_path": "/metrics",
            }
        ]
    else:
        base_config["scrape_configs"] = [
            {
                "job_name": f"{project_name}",
                "static_configs": [{"targets": ["app:8080"]}],
                "metrics_path": "/metrics",
            }
        ]

    return yaml.dump(base_config, default_flow_style=False, sort_keys=False)


def create_prometheus_rules(project_name: str, project_type: str) -> str:
    """Generate Prometheus alert rules based on project type."""
    return f"""# Alert Rules for {project_name}
# Tailored for {project_type} workloads

groups:
  - name: {project_name.replace('-', '_')}_alerts
    interval: 30s
    rules:
      - alert: ServiceDown
        expr: up{{job="{project_name}"}} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Service {{{{ $labels.instance }}}} is down"
          description: "Service has been down for more than 5 minutes"

      - alert: HighErrorRate
        expr: rate(http_requests_total{{status=~"5.."}}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{{{ $value | humanizePercentage }}}}"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency"
          description: "95th percentile latency: {{{{ $value }}}}s"
"""


def create_grafana_dashboard(project_name: str, project_type: str) -> Dict:
    """Generate Grafana dashboard JSON based on project type."""
    return {
        "dashboard": {
            "title": f"{project_name} Dashboard",
            "tags": [project_type, "autogenerated"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "Request Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": f'rate(http_requests_total{{job="{project_name}"}}[5m])',
                            "legendFormat": "{{{{ method }}}} - {{{{ status }}}}",
                        }
                    ],
                },
                {
                    "id": 2,
                    "title": "Error Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": f'rate(http_requests_total{{job="{project_name}",status=~"5.."}}[5m])',
                            "legendFormat": "5xx errors",
                        }
                    ],
                },
                {
                    "id": 3,
                    "title": "Latency (p95)",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{job="{project_name}"}}[5m]))',
                            "legendFormat": "p95",
                        }
                    ],
                },
            ],
            "refresh": "30s",
            "time": {"from": "now-1h", "to": "now"},
        }
    }


def create_observability_configs(
    project_path: Path, project_name: str, project_type: str
):
    """Create Prometheus and Grafana configurations for a project."""
    # Create directories
    prom_dir = project_path / "prometheus"
    grafana_dir = project_path / "grafana" / "dashboards"
    prom_dir.mkdir(parents=True, exist_ok=True)
    grafana_dir.mkdir(parents=True, exist_ok=True)

    # Create Prometheus config
    prom_config_file = prom_dir / "prometheus.yml"
    if not prom_config_file.exists():
        prom_config_file.write_text(
            create_prometheus_config(project_name, project_type)
        )
        print(f"✓ Created {prom_config_file}")

    # Create Prometheus rules
    prom_rules_file = prom_dir / "rules.yml"
    if not prom_rules_file.exists():
        prom_rules_file.write_text(create_prometheus_rules(project_name, project_type))
        print(f"✓ Created {prom_rules_file}")

    # Create Grafana dashboard
    dashboard_file = grafana_dir / f"{project_name}-dashboard.json"
    if not dashboard_file.exists():
        dashboard_file.write_text(
            json.dumps(create_grafana_dashboard(project_name, project_type), indent=2)
        )
        print(f"✓ Created {dashboard_file}")


def get_project_type(project_name: str) -> str:
    """Determine project type from project name."""
    for ptype, projects in PROJECT_TYPES.items():
        if project_name in projects:
            return ptype
    return "application"  # default


def main():
    """Generate all missing deliverables."""
    print("Generating missing deliverables for all projects...")
    print("=" * 80)

    # Get all project directories
    all_projects = [
        d.name
        for d in PROJECTS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]

    print(f"\nFound {len(all_projects)} projects")
    print("\nCreating observability configs...")
    print("-" * 80)

    for project_name in sorted(all_projects):
        project_path = PROJECTS_DIR / project_name
        project_type = get_project_type(project_name)

        print(f"\n{project_name} ({project_type}):")
        create_observability_configs(project_path, project_name, project_type)

    print("\n" + "=" * 80)
    print("✓ All observability configs generated successfully!")


if __name__ == "__main__":
    main()
