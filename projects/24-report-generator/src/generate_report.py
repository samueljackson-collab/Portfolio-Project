"""Render reports from templates."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def render(template_path: Path, output_path: Path) -> None:
    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)
    html = template.render(
        generated_at=datetime.utcnow().isoformat(),
        projects=[
            {"name": "AWS Infrastructure Automation", "status": "green"},
            {"name": "Serverless Data Processing", "status": "yellow"},
        ],
    )
    output_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    render(Path(args.template), Path(args.output))
