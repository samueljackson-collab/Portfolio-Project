"""Generate portfolio reports in HTML and PDF formats."""

from __future__ import annotations

import click
import importlib
import importlib.util
import re
import yaml
from html import unescape
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from data_collector import PortfolioDataCollector


class ReportGenerator:
    """Generate portfolio reports from templates."""

    def __init__(
        self,
        portfolio_root: Path,
        templates_dir: Path,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.portfolio_root = portfolio_root
        self.templates_dir = templates_dir
        self.config = config or {}

        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.env.filters["format_date"] = self._format_date
        self.env.filters["format_number"] = self._format_number

        # Initialize data collector
        self.collector = PortfolioDataCollector(portfolio_root)

    def _format_date(self, value: str, format: str = "%Y-%m-%d %H:%M") -> str:
        """Format ISO date string."""
        try:
            if isinstance(value, str):
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            else:
                dt = value
            return dt.strftime(format)
        except Exception:
            return str(value)

    def _format_number(self, value: int) -> str:
        """Format number with thousands separator."""
        try:
            return f"{value:,}"
        except Exception:
            return str(value)

    def collect_data(self) -> Dict[str, Any]:
        """Collect all data needed for reports."""
        projects = self.collector.collect_all_projects()
        summary = self.collector.get_summary_stats(projects)

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "generated_time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
            "projects": [p.to_dict() for p in projects],
            "summary": summary,
            "config": self.config,
        }

    def render_template(
        self,
        template_name: str,
        output_path: Path,
        format: str = "html",
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Render a template to HTML or PDF.

        Args:
            template_name: Name of template file
            output_path: Output file path
            format: Output format ('html' or 'pdf')
            custom_data: Additional data to merge with collected data
        """
        # Collect portfolio data
        data = self.collect_data()

        # Merge with custom data if provided
        if custom_data:
            data.update(custom_data)

        # Render template
        template = self.env.get_template(template_name)
        html_content = template.render(**data)

        if format == "html":
            # Write HTML directly
            output_path.write_text(html_content, encoding="utf-8")
            click.echo(f"✓ HTML report generated: {output_path}")

        elif format == "pdf":
            self._render_pdf(html_content, output_path)
            click.echo(f"✓ PDF report generated: {output_path}")

        else:
            raise ValueError(f"Unsupported format: {format}")

    def _render_pdf(self, html_content: str, output_path: Path) -> None:
        """Render PDF using WeasyPrint when available, with a simple fallback."""
        spec = importlib.util.find_spec("weasyprint")
        if spec is not None:
            weasyprint = importlib.import_module("weasyprint")
            html = weasyprint.HTML(
                string=html_content,
                base_url=str(self.templates_dir),
            )
            html.write_pdf(output_path)
            return

        text_content = self._strip_html(html_content)
        self._write_simple_pdf(text_content, output_path)

    def _strip_html(self, html_content: str) -> str:
        """Convert HTML content to a plain-text fallback."""
        cleaned = re.sub(r"<(script|style).*?>.*?</\\1>", "", html_content, flags=re.S)
        cleaned = re.sub(r"<br\\s*/?>", "\n", cleaned, flags=re.I)
        cleaned = re.sub(r"</p>", "\n\n", cleaned, flags=re.I)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        cleaned = unescape(cleaned)
        return "\n".join(line.strip() for line in cleaned.splitlines()).strip()

    def _write_simple_pdf(self, text: str, output_path: Path) -> None:
        """Write a minimal PDF with plain text content."""
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            lines = [""]

        def escape_pdf(value: str) -> str:
            return (
                value.replace("\\", "\\\\")
                .replace("(", "\\(")
                .replace(")", "\\)")
            )

        content_lines = ["BT", "/F1 11 Tf", "72 720 Td"]
        for index, line in enumerate(lines):
            if index > 0:
                content_lines.append("T*")
            content_lines.append(f"({escape_pdf(line)}) Tj")
        content_lines.append("ET")
        content_stream = "\n".join(content_lines)
        content_bytes = content_stream.encode("latin-1", errors="replace")

        objects = []

        def add_object(content: bytes) -> None:
            objects.append(content)

        add_object(b"<< /Type /Catalog /Pages 2 0 R >>")
        add_object(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
        add_object(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
        )
        add_object(b"<< /Length " + str(len(content_bytes)).encode("ascii") + b" >>")
        add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

        output = bytearray()
        output.extend(b"%PDF-1.4\n")
        offsets = []

        for index, obj in enumerate(objects, start=1):
            offsets.append(len(output))
            output.extend(f"{index} 0 obj\n".encode("ascii"))
            if index == 4:
                output.extend(obj + b"\nstream\n" + content_bytes + b"\nendstream\n")
            else:
                output.extend(obj + b"\n")
            output.extend(b"endobj\n")

        xref_offset = len(output)
        output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        output.extend(b"0000000000 65535 f \n")
        for offset in offsets:
            output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        output.extend(
            b"trailer\n"
            + f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("ascii")
            + b"startxref\n"
            + f"{xref_offset}\n".encode("ascii")
            + b"%%EOF"
        )

        output_path.write_bytes(output)

    def generate_all_reports(self, output_dir: Path) -> None:
        """Generate all report types."""
        output_dir.mkdir(parents=True, exist_ok=True)

        reports = [
            ("project_status.html", "project-status", ["html", "pdf"]),
            ("executive_summary.html", "executive-summary", ["html", "pdf"]),
            ("technical_documentation.html", "technical-docs", ["html", "pdf"]),
            ("weekly.html", "weekly-report", ["html"]),
        ]

        for template, basename, formats in reports:
            template_path = self.templates_dir / template
            if not template_path.exists():
                click.echo(f"⚠ Template not found: {template}")
                continue

            for fmt in formats:
                output_file = output_dir / f"{basename}.{fmt}"
                try:
                    self.render_template(template, output_file, format=fmt)
                except Exception as e:
                    click.echo(f"✗ Error generating {basename}.{fmt}: {e}")


@click.group()
def cli():
    """Portfolio Report Generator CLI."""
    pass


@cli.command()
@click.option("--template", "-t", required=True, help="Template file name")
@click.option(
    "--output", "-o", required=True, type=click.Path(), help="Output file path"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["html", "pdf"]),
    default="html",
    help="Output format",
)
@click.option(
    "--portfolio-root", type=click.Path(exists=True), help="Portfolio root directory"
)
@click.option("--config", type=click.Path(exists=True), help="Configuration YAML file")
def generate(
    template: str,
    output: str,
    format: str,
    portfolio_root: Optional[str],
    config: Optional[str],
):
    """Generate a single report from a template."""
    # Determine paths
    if portfolio_root:
        portfolio_path = Path(portfolio_root)
    else:
        # Assume we're in projects/24-report-generator
        portfolio_path = Path(__file__).parent.parent.parent.parent

    templates_dir = Path(__file__).parent.parent / "templates"
    output_path = Path(output)

    # Load config if provided
    config_data = {}
    if config:
        with open(config, "r") as f:
            config_data = yaml.safe_load(f)

    # Generate report
    generator = ReportGenerator(portfolio_path, templates_dir, config_data)

    try:
        generator.render_template(template, output_path, format=format)
        click.echo(f"✓ Report generated successfully: {output_path}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="./reports",
    help="Output directory",
)
@click.option(
    "--portfolio-root", type=click.Path(exists=True), help="Portfolio root directory"
)
@click.option("--config", type=click.Path(exists=True), help="Configuration YAML file")
def generate_all(output_dir: str, portfolio_root: Optional[str], config: Optional[str]):
    """Generate all available reports."""
    # Determine paths
    if portfolio_root:
        portfolio_path = Path(portfolio_root)
    else:
        portfolio_path = Path(__file__).parent.parent.parent.parent

    templates_dir = Path(__file__).parent.parent / "templates"
    output_path = Path(output_dir)

    # Load config if provided
    config_data = {}
    if config:
        with open(config, "r") as f:
            config_data = yaml.safe_load(f)

    # Generate all reports
    click.echo("Generating all reports...")
    generator = ReportGenerator(portfolio_path, templates_dir, config_data)
    generator.generate_all_reports(output_path)
    click.echo(f"\n✓ All reports generated in: {output_path}")


@cli.command()
@click.option(
    "--portfolio-root", type=click.Path(exists=True), help="Portfolio root directory"
)
def stats(portfolio_root: Optional[str]):
    """Display portfolio statistics."""
    # Determine paths
    if portfolio_root:
        portfolio_path = Path(portfolio_root)
    else:
        portfolio_path = Path(__file__).parent.parent.parent.parent

    collector = PortfolioDataCollector(portfolio_path)
    projects = collector.collect_all_projects()
    summary = collector.get_summary_stats(projects)

    click.echo("\n=== Portfolio Statistics ===\n")
    click.echo(f"Total Projects: {summary['total_projects']}")
    click.echo(f"Average Completion: {summary['avg_completion']}%")
    click.echo(f"Total Lines of Code: {summary['total_lines']:,}")
    click.echo(f"Total Files: {summary['total_files']:,}")

    click.echo("\n=== Project Status Breakdown ===")
    for status, count in summary["status_breakdown"].items():
        click.echo(f"  {status}: {count}")

    click.echo("\n=== Quality Metrics ===")
    click.echo(f"  Projects with Tests: {summary['projects_with_tests']}")
    click.echo(f"  Projects with CI/CD: {summary['projects_with_ci_cd']}")
    click.echo(f"  Projects with Docker: {summary['projects_with_docker']}")
    click.echo(f"  Projects with K8s: {summary['projects_with_k8s']}")

    click.echo("\n=== Top Technologies ===")
    for tech, count in list(summary["tech_stack_count"].items())[:5]:
        click.echo(f"  {tech}: {count} projects")

    click.echo()


if __name__ == "__main__":
    cli()
