#!/usr/bin/env python3
"""Portfolio materials inventory and analysis tool.

This script scans one or more directories, categorises the discovered files,
lines them up with a set of flagship "elite" projects, and emits a structured
JSON report that can be reused elsewhere (dashboards, documentation, etc.).

It is intentionally designed to be deterministic and easy to automate so it can
slot into scheduled jobs or CI pipelines.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, MutableMapping

# Define the 5 elite projects
ELITE_PROJECTS: Dict[str, Dict[str, object]] = {
    "1_aws_terraform": {
        "name": "AWS Multi-Tier Architecture with Terraform",
        "category": "Infrastructure/Cloud",
        "keywords": [
            "aws",
            "terraform",
            "vpc",
            "multi-tier",
            "cloudformation",
            "infrastructure",
            "iac",
        ],
        "description": (
            "Production-grade AWS infrastructure with Terraform showcasing "
            "multi-tier architecture, security groups, and automated deployment"
        ),
    },
    "2_k8s_cicd": {
        "name": "Complete Kubernetes CI/CD Pipeline",
        "category": "DevOps",
        "keywords": [
            "kubernetes",
            "k8s",
            "cicd",
            "jenkins",
            "gitlab",
            "argocd",
            "gitops",
            "pipeline",
            "devops",
        ],
        "description": (
            "End-to-end CI/CD pipeline with Kubernetes, GitOps, automated testing, "
            "and blue-green deployments"
        ),
    },
    "3_iam_security": {
        "name": "IAM Security Hardening",
        "category": "Security",
        "keywords": [
            "iam",
            "security",
            "hardening",
            "policies",
            "rbac",
            "least privilege",
            "compliance",
        ],
        "description": (
            "Comprehensive IAM security implementation with policy-as-code, "
            "compliance automation, and security auditing"
        ),
    },
    "4_monitoring": {
        "name": "Enterprise Monitoring Stack (Prometheus/Grafana/ELK)",
        "category": "Monitoring/Observability",
        "keywords": [
            "prometheus",
            "grafana",
            "elk",
            "elasticsearch",
            "monitoring",
            "observability",
            "metrics",
            "logging",
        ],
        "description": (
            "Full-stack observability platform with metrics, logs, traces, and "
            "custom dashboards"
        ),
    },
    "5_incident_response": {
        "name": "Incident Response Runbook & Playbook System",
        "category": "SRE/Operations",
        "keywords": [
            "incident",
            "runbook",
            "playbook",
            "sre",
            "disaster",
            "recovery",
            "operations",
            "troubleshooting",
        ],
        "description": (
            "Comprehensive incident response framework with runbooks, playbooks, "
            "and automated remediation"
        ),
    },
}

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
}


def _safe_file_size(path: Path) -> int:
    """Return the size of *path* in bytes, handling any access errors."""

    try:
        return path.stat().st_size
    except OSError:
        return 0


def scan_directory(
    base_path: Path, *, exclude_dirs: Iterable[str] | None = None
) -> DefaultDict[str, List[Dict[str, object]]]:
    """Scan *base_path* and bucket the discovered files by type."""

    inventory: DefaultDict[str, List[Dict[str, object]]] = defaultdict(list)
    base_path = Path(base_path).expanduser()

    if not base_path.exists():
        print(f"Warning: directory '{base_path}' does not exist; skipping.")
        return inventory

    exclude_names = set(DEFAULT_EXCLUDED_DIRS)
    if exclude_dirs:
        exclude_names.update(exclude_dirs)

    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in exclude_names]
        root_path = Path(root)

        for file_name in files:
            file_path = root_path / file_name
            relative_path = file_path.relative_to(base_path)
            extension = file_path.suffix.lower()

            file_info = {
                "path": str(file_path),
                "relative_path": str(relative_path),
                "name": file_name,
                "extension": extension,
                "size": _safe_file_size(file_path),
            }

            if extension in {".md", ".txt"}:
                inventory["documentation"].append(file_info)
            elif extension in {".py", ".js", ".ts", ".tsx", ".go", ".java"}:
                inventory["code"].append(file_info)
            elif extension in {".tf", ".yml", ".yaml", ".json"}:
                inventory["config"].append(file_info)
            elif extension in {".sh", ".ps1", ".bat"}:
                inventory["scripts"].append(file_info)
            elif extension in {".pdf", ".docx", ".doc"}:
                inventory["documents"].append(file_info)
            else:
                inventory["other"].append(file_info)

    return inventory


def map_to_elite_projects(
    inventory: MutableMapping[str, List[Dict[str, object]]]
) -> Dict[str, List[Dict[str, object]]]:
    """Map inventory items to elite projects based on keyword matching."""

    project_mapping: Dict[str, List[Dict[str, object]]] = {
        key: [] for key in ELITE_PROJECTS
    }

    for category, items in inventory.items():
        for item in items:
            file_path_lower = item["path"].lower()
            file_name_lower = item["name"].lower()

            for project_key, project_info in ELITE_PROJECTS.items():
                keywords = project_info["keywords"]

                if any(
                    keyword in file_path_lower or keyword in file_name_lower
                    for keyword in keywords
                ):
                    project_mapping[project_key].append(
                        {
                            "file": item,
                            "category": category,
                            "relevance": (
                                "high"
                                if any(kw in file_name_lower for kw in keywords)
                                else "medium"
                            ),
                        }
                    )

    return project_mapping


def generate_inventory_report(
    working_dir: Path,
    uploads_dir: Path,
    *,
    exclude_dirs: Iterable[str] | None = None,
    max_category_items: int = 50,
    max_project_items: int = 30,
) -> tuple[Dict[str, object], Dict[str, List[Dict[str, object]]]]:
    """Generate the full inventory report structure."""

    print("Scanning working directory...")
    working_inventory = scan_directory(working_dir, exclude_dirs=exclude_dirs)

    print("Scanning uploads directory...")
    uploads_inventory = scan_directory(uploads_dir, exclude_dirs=exclude_dirs)

    combined_inventory: DefaultDict[str, List[Dict[str, object]]] = defaultdict(list)
    for key in set(working_inventory) | set(uploads_inventory):
        combined_inventory[key] = working_inventory.get(key, []) + uploads_inventory.get(
            key, []
        )

    print("\nMapping to elite projects...")
    project_mapping = map_to_elite_projects(combined_inventory)

    stats = {
        "total_files": sum(len(items) for items in combined_inventory.values()),
        "by_category": {cat: len(items) for cat, items in combined_inventory.items()},
        "by_project": {key: len(items) for key, items in project_mapping.items()},
    }

    generated_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    report: Dict[str, object] = {
        "metadata": {
            "generated_at": generated_at,
            "working_directory": str(Path(working_dir).expanduser()),
            "uploads_directory": str(Path(uploads_dir).expanduser()),
        },
        "statistics": stats,
        "elite_projects": ELITE_PROJECTS,
        "inventory_by_category": {
            cat: [
                {
                    "path": item["relative_path"],
                    "name": item["name"],
                    "size": item["size"],
                }
                for item in items[:max_category_items]
            ]
            for cat, items in combined_inventory.items()
        },
        "project_mapping": {
            key: {
                "project_info": ELITE_PROJECTS[key],
                "mapped_files_count": len(items),
                "files": [
                    {
                        "path": item["file"]["relative_path"],
                        "category": item["category"],
                        "relevance": item["relevance"],
                    }
                    for item in items[:max_project_items]
                ],
            }
            for key, items in project_mapping.items()
        },
    }

    return report, project_mapping


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate a JSON inventory that maps portfolio artefacts to elite projects."
        )
    )
    parser.add_argument(
        "--working-dir",
        type=Path,
        default=Path.home() / "portfolio_working",
        help="Directory containing in-progress or staged portfolio assets.",
    )
    parser.add_argument(
        "--uploads-dir",
        type=Path,
        default=Path.home() / "Uploads",
        help="Directory containing uploaded artefacts (evidence, exports, etc.).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "portfolio_analysis",
        help="Directory where the JSON report should be written.",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="master_inventory.json",
        help="Filename (within the output directory) for the JSON report.",
    )
    parser.add_argument(
        "--max-category-items",
        type=int,
        default=50,
        help="Maximum number of files to include per category in the report.",
    )
    parser.add_argument(
        "--max-project-items",
        type=int,
        default=30,
        help="Maximum number of files to include per elite project in the report.",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        metavar="NAME",
        help=(
            "Directory names to exclude during scanning. Can be specified multiple times."
        ),
    )

    return parser.parse_args()


def main() -> Dict[str, object]:
    """Entry-point used by the CLI."""

    args = parse_args()

    output_dir = args.output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("PORTFOLIO MATERIALS INVENTORY & ANALYSIS")
    print("=" * 80)

    report, project_mapping = generate_inventory_report(
        args.working_dir,
        args.uploads_dir,
        exclude_dirs=args.exclude_dir,
        max_category_items=args.max_category_items,
        max_project_items=args.max_project_items,
    )

    output_path = output_dir / args.output_file
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    print(f"\nInventory saved to: {output_path}")

    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Total Files Scanned: {report['statistics']['total_files']}")

    print("\nBy Category:")
    for cat, count in sorted(report["statistics"]["by_category"].items()):
        print(f"  {cat}: {count}")

    print("\nBy Elite Project:")
    for key, count in sorted(report["statistics"]["by_project"].items()):
        project_name = ELITE_PROJECTS[key]["name"]
        print(f"  {project_name}: {count} files")

    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)

    return report


if __name__ == "__main__":
    main()
