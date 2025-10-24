#!/usr/bin/env python3
"""Validate the enterprise portfolio structure."""
from __future__ import annotations

import json
from pathlib import Path
import sys

EXPECTED = {
    "cloud-infrastructure": [
        "aws-landing-zone",
        "multi-cloud-kubernetes",
        "serverless-platform",
        "cost-optimization-engine",
        "network-hub-spoke",
        "disaster-recovery-automation",
    ],
    "security-compliance": [
        "zero-trust-architecture",
        "security-hub-automation",
        "compliance-as-code",
        "secrets-management",
        "container-security",
        "cloud-security-posture",
    ],
    "devops-automation": [
        "gitops-platform",
        "ci-cd-pipelines",
        "infrastructure-as-code",
        "monitoring-stack",
        "self-service-platform",
        "chatops-automation",
    ],
    "full-stack-apps": [
        "microservices-ecommerce",
        "real-time-dashboard",
        "serverless-api-gateway",
        "react-enterprise-app",
        "mobile-backend",
        "websocket-platform",
    ],
    "data-engineering": [
        "real-time-data-pipeline",
        "data-lake-formation",
        "mlops-platform",
        "streaming-analytics",
        "data-governance",
        "bi-dashboard-platform",
    ],
}

DOCS = [
    Path("docs/ARCHITECTURE.md"),
    Path("docs/STRATEGY.md"),
    Path("docs/ROADMAP.md"),
    Path("PROJECTS.md"),
]

REQUIRED_PROJECT_FILES = ["README.md", "deploy.sh", "validate.sh", "terraform/main.tf"]


def check_files(root: Path) -> list[str]:
    """Return a list of validation errors."""
    errors: list[str] = []

    for doc in DOCS:
        if not (root / doc).is_file():
            errors.append(f"Missing documentation file: {doc}")

    projects_root = root / "projects"
    if not projects_root.exists():
        errors.append("Projects directory missing")
        return errors

    for category, projects in EXPECTED.items():
        category_dir = projects_root / category
        if not category_dir.is_dir():
            errors.append(f"Missing project category directory: {category}")
            continue
        for project in projects:
            project_dir = category_dir / project
            if not project_dir.is_dir():
                errors.append(f"Missing project: {category}/{project}")
                continue
            for required in REQUIRED_PROJECT_FILES:
                if not (project_dir / required).exists():
                    errors.append(
                        f"Missing {required} in project {category}/{project}"
                    )

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = check_files(root)
    if errors:
        print(json.dumps({"status": "failed", "errors": errors}, indent=2))
        return 1

    summary = {category: len(projects) for category, projects in EXPECTED.items()}
    print(json.dumps({"status": "ok", "projects": summary}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
