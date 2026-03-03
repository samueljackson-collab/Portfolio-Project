import argparse
import json
from pathlib import Path
from typing import Any, Iterable

TEMPLATE = """# {title}

- **Role Category:** {role_category}
- **Status:** {status}

## Executive Summary
{executive_summary}

## Scenario & Scope
{scenario_scope}

## Responsibilities
{responsibilities}

## Tools & Technologies
{tools_tech}

## Architecture Notes
{architecture_notes}

## Process Walkthrough
{process_walkthrough}

## Outcomes & Metrics
{outcomes_metrics}

## Evidence Links
{evidence_links}

## Reproduction Steps
{reproduction_steps}

## Interview Points
{interview_points}
"""


def format_value(value: Any) -> str:
    """Convert a project field to markdown-friendly text with sensible defaults."""
    if value is None:
        return "TBD"

    if isinstance(value, str):
        text = value.strip()
        return text if text else "TBD"

    if isinstance(value, dict):
        if not value:
            return "TBD"
        lines: Iterable[str] = (f"- {k}: {v}" for k, v in value.items())
        return "\n".join(lines)

    if isinstance(value, (list, tuple, set)):
        if not value:
            return "TBD"
        return "\n".join(f"- {str(item).strip()}" if str(item).strip() else "- (blank)" for item in value)

    return str(value)


def render_readme(project: dict) -> str:
    content = {
        "title": format_value(project.get("title")),
        "role_category": format_value(project.get("role_category")),
        "status": format_value(project.get("status")),
        "executive_summary": format_value(project.get("executive_summary")),
        "scenario_scope": format_value(project.get("scenario_scope")),
        "responsibilities": format_value(project.get("responsibilities")),
        "tools_tech": format_value(project.get("tools_tech")),
        "architecture_notes": format_value(project.get("architecture_notes")),
        "process_walkthrough": format_value(project.get("process_walkthrough")),
        "outcomes_metrics": format_value(project.get("outcomes_metrics")),
        "evidence_links": format_value(project.get("evidence_links")),
        "reproduction_steps": format_value(project.get("reproduction_steps")),
        "interview_points": format_value(project.get("interview_points")),
    }
    return TEMPLATE.format(**content)


def write_readme(project: dict, base_dir: Path) -> Path:
    slug = project.get("slug")
    if not slug:
        raise ValueError("Project entry missing required 'slug' field")

    target_dir = base_dir / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    readme_path = target_dir / "README.md"
    readme_path.write_text(render_readme(project), encoding="utf-8")
    return readme_path


def load_projects(json_path: Path) -> list[dict]:
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("projects.json must contain a list of project objects")
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate README.md files for portfolio projects")
    parser.add_argument("--only", dest="only_slug", help="Generate README for a single project slug")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent / "projects"
    projects_file = Path(__file__).resolve().parent.parent / "exports" / "projects.json"

    projects = load_projects(projects_file)

    if args.only_slug:
        projects = [p for p in projects if p.get("slug") == args.only_slug]
        if not projects:
            raise SystemExit(f"No project found with slug '{args.only_slug}'")

    generated_paths = [write_readme(project, project_root) for project in projects]

    print(f"Generated {len(generated_paths)} README file(s)")
    for path in generated_paths:
        print(f"- {path.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
