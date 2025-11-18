"""Generate templated READMEs for each project in exports/projects.json."""
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports" / "projects.json"
PROJECTS_DIR = ROOT / "projects"


def load_projects() -> list[dict]:
    with EXPORTS.open() as f:
        return json.load(f)


def build_readme(project: dict) -> str:
    stack = ", ".join(project.get("stack", [])) or "See repo"
    return dedent(
        f"""
        # {project['title']}

        **Category:** {project.get('category', 'General')}  \
        **Status:** {project.get('status', 'unknown').title()}

        ## Overview
        {project.get('summary', 'No description provided.')}

        ## Tech Stack
        {stack}

        ## Running Locally
        1. Clone the repo and navigate to `{project['slug']}`.
        2. Follow the service-specific README or docker-compose file to start dependencies.
        3. Run the test suite to validate changes.

        ## Links
        - Portfolio API: http://localhost:8000
        - Frontend: http://localhost:5173
        """
    ).strip() + "\n"


def write_readmes(projects: list[dict]) -> None:
    for project in projects:
        slug = project["slug"]
        project_dir = PROJECTS_DIR / slug
        project_dir.mkdir(parents=True, exist_ok=True)
        readme_path = project_dir / "README.md"
        readme_path.write_text(build_readme(project), encoding="utf-8")
        print(f"Wrote {readme_path}")


def main() -> None:
    projects = load_projects()
    write_readmes(projects)


if __name__ == "__main__":
    main()
