#!/usr/bin/env python3
"""Portfolio Bootstrap Kit scaffolding utility.

This script initializes a repository with the standard folder layout
and seed files required by the Portfolio Bootstrap Kit. It is safe to
run multiple times; existing files are left untouched unless `--force`
is provided.
"""
from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]

DIRECTORIES = [
    "docs",
    "docs/assets",
    "prompts",
    "scripts",
    "tasks",
    "tools",
]

TEMPLATES: Dict[str, Dict[str, str]] = {
    "prompts/agents.json": {
        "description": "Seed agent definitions used by automation prompts.",
        "content": textwrap.dedent(
            """
            [
              {
                "name": "InstructionalExplainer",
                "description": "Breaks down complex technical topics into sequential, teachable steps.",
                "input": "User question or topic requiring explanation.",
                "output": "Numbered learning steps with context, examples, and references.",
                "approach": "Research linked specs, outline core ideas, validate assumptions, and present in progressive layers.",
                "tools": ["knowledge_base", "diagram_builder", "glossary"]
              },
              {
                "name": "TechGuideWriter",
                "description": "Produces implementation guides that combine architecture decisions, commands, and validation steps.",
                "input": "Feature brief or operational change request.",
                "output": "End-to-end guide with prerequisites, execution steps, and verification checks.",
                "approach": "Gather environment details, model infrastructure dependencies, propose sequence with guardrails, and capture follow-up tasks.",
                "tools": ["shell", "config_linter", "runbook_template"]
              },
              {
                "name": "DiagramBuilder",
                "description": "Generates diagram briefs and PlantUML/Draw.io structures for documentation.",
                "input": "Architecture narrative or workflow description.",
                "output": "Diagram JSON/PlantUML plus annotations for visual styling.",
                "approach": "Identify actors, systems, and flows; map them into consistent layouts with labelled interactions.",
                "tools": ["diagram_renderer", "style_guide"]
              }
            ]
            """
        ).strip()
    },
    "prompts/BUILD_SPEC.json": {
        "description": "Baseline build specification to coordinate automation.",
        "content": json.dumps(
            {
                "stacks": {
                    "infrastructure": ["terraform", "ansible"],
                    "application": ["python", "node"],
                    "documentation": ["mkdocs", "drawio"],
                },
                "policies": {
                    "branching": "feature-branches with squash merges",
                    "reviews": "require at least one approval and successful CI",
                    "security": "run dependency and secret scanning weekly",
                },
                "quality_gates": [
                    "lint passes",
                    "unit tests green",
                    "docs updated",
                    "diagrams versioned",
                ],
            },
            indent=2,
        )
    },
    "tasks/ai_tasks_v1.json": {
        "description": "List of automatable tasks consumed by AI agents.",
        "content": json.dumps(
            {
                "version": 1,
                "tasks": [
                    {
                        "id": "DOC-GUIDE-001",
                        "domain": "documentation",
                        "input": "Feature summary and environment assumptions",
                        "tool": "TechGuideWriter",
                        "expected_output": "Comprehensive implementation guide with validation checks",
                    },
                    {
                        "id": "ARCH-DIAG-001",
                        "domain": "architecture",
                        "input": "System context narrative",
                        "tool": "DiagramBuilder",
                        "expected_output": "Layered diagrams and annotations",
                    },
                    {
                        "id": "QA-RUNBOOK-001",
                        "domain": "quality",
                        "input": "Regression scope and release notes",
                        "tool": "InstructionalExplainer",
                        "expected_output": "Step-by-step QA runbook",
                    },
                ],
            },
            indent=2,
        )
    },
    "tasks/ai_tasks_v1.csv": {
        "description": "CSV form of automatable tasks for spreadsheet workflows.",
        "content": textwrap.dedent(
            """
            id,domain,input,tool,expected_output
            DOC-GUIDE-001,documentation,"Feature summary and environment assumptions",TechGuideWriter,"Comprehensive implementation guide with validation checks"
            ARCH-DIAG-001,architecture,"System context narrative",DiagramBuilder,"Layered diagrams and annotations"
            QA-RUNBOOK-001,quality,"Regression scope and release notes",InstructionalExplainer,"Step-by-step QA runbook"
            """
        ).strip()
    },
}


def ensure_directories(directories: list[str], *, dry_run: bool) -> list[str]:
    actions = []
    for rel_path in directories:
        path = ROOT / rel_path
        if path.exists():
            continue
        actions.append(f"create_dir {rel_path}")
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)
    return actions


def write_file(path: Path, content: str, *, force: bool, dry_run: bool) -> str:
    rel = path.relative_to(ROOT)
    if path.exists() and not force:
        return f"skip {rel} (exists)"
    if dry_run:
        return f"write {rel}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"write {rel}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize Portfolio Bootstrap Kit structure.")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without writing files.")
    parser.add_argument("--force", action="store_true", help="Overwrite files using embedded templates.")
    parser.add_argument("--list", action="store_true", help="List managed files and exit.")
    args = parser.parse_args()

    if args.list:
        for rel, meta in TEMPLATES.items():
            print(f"{rel}: {meta['description']}")
        return

    actions = ensure_directories(DIRECTORIES, dry_run=args.dry_run)
    for rel, meta in TEMPLATES.items():
        path = ROOT / rel
        action = write_file(path, meta["content"], force=args.force, dry_run=args.dry_run)
        actions.append(action)

    if actions:
        for action in actions:
            print(action)
    else:
        print("No changes required. Repository already matches bootstrap layout.")


if __name__ == "__main__":
    main()
