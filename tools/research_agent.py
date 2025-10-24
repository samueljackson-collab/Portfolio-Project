#!/usr/bin/env python3
"""CLI helper for generating structured research dossiers."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

try:  # pragma: no cover - external dependency detection
    import typer  # type: ignore
except ImportError:  # pragma: no cover
    typer = None  # type: ignore


@dataclass
class TemplateSection:
    """Represents a section of a report template."""

    heading: str
    prompt: str


@dataclass
class ReportTemplate:
    """Reusable definition for a research report outline."""

    key: str
    title: str
    description: str
    sections: List[TemplateSection]
    spotlight: List[str]


TEMPLATES: Dict[str, ReportTemplate] = {
    "executive_summary": ReportTemplate(
        key="executive_summary",
        title="Executive Research Dossier",
        description="Default template balancing breadth-to-depth findings with clear stakeholder actions.",
        sections=[
            TemplateSection(
                heading="Executive Summary",
                prompt=(
                    "Summarize the problem framing, two to three leading signals, and the decision or action this dossier enables. "
                    "Reference evidence grades for the strongest claims."
                ),
            ),
            TemplateSection(
                heading="Key Findings",
                prompt=(
                    "List thematic findings using a claims → evidence table. Include citation IDs, confidence levels, and "
                    "reference to supporting data visualizations if applicable."
                ),
            ),
            TemplateSection(
                heading="Implications & Recommendations",
                prompt=(
                    "Translate findings into decision-ready guidance. Cover recommended actions, owners, expected impact, and "
                    "dependencies."
                ),
            ),
            TemplateSection(
                heading="Risks, Gaps & Counterpoints",
                prompt=(
                    "Document dissenting evidence, open questions, and mitigation ideas. Map each risk to validation tasks or "
                    "assumptions to monitor."
                ),
            ),
            TemplateSection(
                heading="Next Steps & Research Backlog",
                prompt=(
                    "List follow-up analyses, stakeholder interviews, or data pulls needed to increase confidence or update the dossier."
                ),
            ),
            TemplateSection(
                heading="Appendix",
                prompt=(
                    "Attach methodology notes, search logs, evidence grading rationale, and full citation list. Cross-reference "
                    "supporting artifacts stored in version control."
                ),
            ),
        ],
        spotlight=[
            "Use prompts/research/01_strategy.md to verify scope and success criteria before populating the sections.",
            "Harvest citations and metadata per prompts/research/02_collection.md to maintain reproducibility.",
            "Translate notes into claim/evidence grids using prompts/research/03_analysis.md before drafting prose.",
            "Validate assertions with prompts/research/05_validation.md prior to sharing the dossier.",
        ],
    ),
    "deep_dive": ReportTemplate(
        key="deep_dive",
        title="Deep Dive Research Deck",
        description="Expanded outline suited for technical reviews or executive briefings requiring depth and scenario planning.",
        sections=[
            TemplateSection(
                heading="Context & Objectives",
                prompt="Detail stakeholder goals, research scope, and critical questions guiding the investigation.",
            ),
            TemplateSection(
                heading="Methodology",
                prompt="Summarize search coverage, evidence grading decisions, and tools used during collection and analysis.",
            ),
            TemplateSection(
                heading="Detailed Findings by Theme",
                prompt=(
                    "Create subsections per theme with claim statements, supporting evidence, visuals, and explicit counterpoints."
                ),
            ),
            TemplateSection(
                heading="Scenario Analysis",
                prompt=(
                    "Explore best/expected/worst-case scenarios. Highlight triggers, indicators to monitor, and decision impact for each."
                ),
            ),
            TemplateSection(
                heading="Recommendations & Roadmap",
                prompt="Propose initiatives with timeline, resource requirements, and dependencies.",
            ),
            TemplateSection(
                heading="Risk Register",
                prompt="List operational, compliance, or market risks plus mitigation owners and review cadence.",
            ),
            TemplateSection(
                heading="Appendix",
                prompt="Provide extended tables, interview summaries, and the full bibliography.",
            ),
        ],
        spotlight=[
            "Cross-link each theme with claim IDs from the analysis templates for traceability.",
            "Capture automation prompts and datasets in the appendix to ease reproducibility.",
        ],
    ),
    "rapid_brief": ReportTemplate(
        key="rapid_brief",
        title="Rapid Research Brief",
        description="Concise outline optimized for quick stakeholder updates or daily syncs.",
        sections=[
            TemplateSection(
                heading="Overview",
                prompt="State the topic, stakeholder concern, and reason this brief matters now.",
            ),
            TemplateSection(
                heading="Key Signals",
                prompt="Highlight three leading insights with supporting evidence grades and quick citations.",
            ),
            TemplateSection(
                heading="Risks & Open Questions",
                prompt="Identify uncertainties, blockers, or areas needing validation.",
            ),
            TemplateSection(
                heading="Immediate Actions",
                prompt="List recommended next steps with owners and due dates.",
            ),
            TemplateSection(
                heading="Reference Links",
                prompt="Provide quick-access links or IDs for the top sources referenced.",
            ),
        ],
        spotlight=[
            "Ideal for fast-moving situations; schedule a full dossier once higher confidence is required.",
        ],
    ),
}


def _render_metadata(
    topic: str,
    template: ReportTemplate,
    stakeholder: Optional[str],
    researcher: Optional[str],
    additional_notes: Optional[str],
) -> str:
    """Render metadata header for the dossier."""

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    metadata = {
        "topic": topic,
        "template": template.key,
        "generated_at_utc": timestamp,
    }
    if stakeholder:
        metadata["stakeholder"] = stakeholder
    if researcher:
        metadata["researcher"] = researcher
    if additional_notes:
        metadata["notes"] = additional_notes

    pretty_metadata = json.dumps(metadata, indent=2)
    return f"```json\n{pretty_metadata}\n```\n"


def build_dossier(
    topic: str,
    template: ReportTemplate,
    stakeholder: Optional[str] = None,
    researcher: Optional[str] = None,
    additional_notes: Optional[str] = None,
) -> str:
    """Construct the dossier content as Markdown."""

    lines: List[str] = []
    lines.append(f"# {template.title}: {topic}")
    lines.append("")
    lines.append("## Metadata")
    lines.append(_render_metadata(topic, template, stakeholder, researcher, additional_notes))

    lines.append("## Template Guidance")
    lines.append(
        "- Refer to the prompts/research directory for detailed strategy, collection, analysis, reporting, and validation guardrails."
    )
    for spotlight in template.spotlight:
        lines.append(f"- {spotlight}")
    lines.append("")

    for section in template.sections:
        lines.append(f"## {section.heading}")
        lines.append(section.prompt)
        lines.append("")
        lines.append("> Notes: \n> - [ ] Evidence grade recorded\n> - [ ] Citation IDs linked\n> - [ ] Validation status updated")
        lines.append("")

    lines.append("---")
    lines.append(
        "_Generated with tools/research_agent.py. Update sections with synthesized insights, citations, and validation notes before publishing._"
    )
    return "\n".join(lines).strip() + "\n"


def _get_template(template_key: str) -> ReportTemplate:
    key = template_key.lower()
    if key not in TEMPLATES:
        available = ", ".join(sorted(TEMPLATES))
        raise ValueError(f"Unknown template '{template_key}'. Available templates: {available}")
    return TEMPLATES[key]


def _write_output(dossier: str, output: Optional[Path]) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(dossier, encoding="utf-8")
        print(f"Dossier written to {output.resolve()}")
    else:
        print(dossier)


def _run_generate(
    topic: str,
    template: str,
    stakeholder: Optional[str],
    researcher: Optional[str],
    notes: Optional[str],
    output: Optional[Path],
    *,
    error_handler: Optional[Callable[[str], None]] = None,
) -> None:
    try:
        template_obj = _get_template(template)
    except ValueError as exc:
        if error_handler is not None:
            error_handler(str(exc))
            return
        raise

    dossier = build_dossier(topic, template_obj, stakeholder, researcher, notes)
    _write_output(dossier, output)


def _run_list_templates() -> None:
    for key in sorted(TEMPLATES):
        template = TEMPLATES[key]
        sections = ", ".join(section.heading for section in template.sections)
        print(f"{key}\n  Title      : {template.title}\n  Description: {template.description}\n  Sections   : {sections}\n")


def _typer_entrypoint() -> None:  # pragma: no cover - exercised via manual runs
    app = typer.Typer(help="Generate research dossiers using repeatable templates.")

    @app.command("generate")
    def generate_dossier(
        topic: str = typer.Argument(..., help="Primary research question or subject."),
        template: str = typer.Option(
            "executive_summary",
            "--template",
            "-t",
            help="Template key to use. Run `list-templates` to see options.",
        ),
        stakeholder: Optional[str] = typer.Option(None, help="Intended audience to emphasize in the report."),
        researcher: Optional[str] = typer.Option(None, help="Name or team preparing the dossier."),
        notes: Optional[str] = typer.Option(None, help="Extra context recorded in metadata."),
        output: Optional[Path] = typer.Option(None, help="Optional path to write the dossier Markdown file."),
    ) -> None:
        def _raise_error(message: str) -> None:
            raise typer.BadParameter(message)

        _run_generate(
            topic,
            template,
            stakeholder,
            researcher,
            notes,
            output,
            error_handler=_raise_error,
        )

    @app.command("list-templates")
    def list_templates() -> None:
        _run_list_templates()

    app()


def _argparse_entrypoint(argv: Optional[Sequence[str]] = None) -> None:
    print(
        "Typer not available; falling back to basic argparse CLI. Install 'typer' for the full experience.",
        file=sys.stderr,
    )
    parser = argparse.ArgumentParser(description="Generate research dossiers using repeatable templates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate a structured research dossier.")
    generate_parser.add_argument("topic", help="Primary research question or subject.")
    generate_parser.add_argument(
        "--template",
        "-t",
        default="executive_summary",
        help="Template key to use. Options: {}".format(", ".join(sorted(TEMPLATES))),
    )
    generate_parser.add_argument("--stakeholder", help="Intended audience to emphasize in the report.")
    generate_parser.add_argument("--researcher", help="Name or team preparing the dossier.")
    generate_parser.add_argument("--notes", help="Extra context recorded in metadata.")
    generate_parser.add_argument("--output", "-o", help="Optional path to write the dossier Markdown file.")

    list_parser = subparsers.add_parser("list-templates", help="Show available report templates.")

    args = parser.parse_args(argv)

    if args.command == "generate":
        output_path = Path(args.output).expanduser().resolve() if args.output else None

        def _error(message: str) -> None:
            generate_parser.error(message)

        _run_generate(
            args.topic,
            args.template,
            getattr(args, "stakeholder", None),
            getattr(args, "researcher", None),
            getattr(args, "notes", None),
            output_path,
            error_handler=_error,
        )
    elif args.command == "list-templates":
        _run_list_templates()
    else:  # pragma: no cover - defensive, subparser enforces commands
        parser.error("Unknown command")


def main() -> None:
    if typer is not None:
        _typer_entrypoint()
    else:
        _argparse_entrypoint()


if __name__ == "__main__":
    main()
