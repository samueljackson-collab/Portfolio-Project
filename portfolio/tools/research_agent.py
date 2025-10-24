"""Generate lightweight research dossiers using prompt scaffolds."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

APP = typer.Typer(help="Generate research dossiers based on predefined templates.")
ROOT = Path(__file__).resolve().parents[1]
INSTRUCTION_BANK_PATH = ROOT / "prompts" / ".private" / "ai_instruction_bank.json"

DEFAULT_TEMPLATE_KEYS: list[tuple[str, str | None]] = [
    ("Strategy", "strategy"),
    ("Collection", "collection"),
    ("Analysis", "analysis"),
    ("Reporting", "reporting"),
    ("Validation", "validation"),
]

EXECUTIVE_TEMPLATE_KEYS: list[tuple[str, str | None]] = [
    ("Executive Summary", None),
    ("Key Findings", None),
    ("Recommendations", None),
    ("Risks", None),
    ("Appendix", "validation"),
]

TEMPLATES: dict[str, list[tuple[str, str | None]]] = {
    "default": DEFAULT_TEMPLATE_KEYS,
    "executive": EXECUTIVE_TEMPLATE_KEYS,
}


def _load_instruction_bank() -> dict[str, object]:
    try:
        with INSTRUCTION_BANK_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:  # pragma: no cover - misconfiguration guard
        raise typer.BadParameter(
            "Instruction bank not found. Ensure prompts/.private/ai_instruction_bank.json exists."
        ) from exc


def _read_optional(section_key: Optional[str], sections: dict[str, object]) -> str:
    if section_key is None:
        return ""
    return str(sections.get(section_key, "")).strip()


def build_dossier(topic: str, template: str) -> str:
    if template not in TEMPLATES:
        raise typer.BadParameter(f"Unknown template '{template}'. Available: {', '.join(TEMPLATES)}")
    instruction_bank = _load_instruction_bank()
    sections_data = instruction_bank.get("research_sections", {})
    if not isinstance(sections_data, dict):
        sections_data = {}
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sections = [f"# Research Dossier: {topic}", f"_Generated {timestamp}_", ""]
    for title, section_key in TEMPLATES[template]:
        sections.append(f"## {title}")
        body = _read_optional(section_key, sections_data)
        if body:
            sections.append(body.strip())
        else:
            sections.append("- TODO: Populate findings.")
        sections.append("")
    return "\n".join(sections).strip() + "\n"


@APP.command()
def generate(topic: str, template: str = typer.Option("default", "--template", "-t")) -> None:
    """Render a dossier to stdout."""
    typer.echo(build_dossier(topic, template))


if __name__ == "__main__":
    APP()
