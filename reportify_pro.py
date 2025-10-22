"""
Enterprise Portfolio & Report Generation System

A production-ready system for generating professional portfolio documentation
and technical reports with enterprise-grade validation and extensibility.

Author: Your Name
License: MIT
Version: 1.0.0
"""

import argparse
import json
import logging
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt
    from pydantic import BaseModel, Field, field_validator
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Install with: pip install python-docx pydantic")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('portfolio_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class OutputFormat(str, Enum):
    """Supported output formats."""
    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"


class ReportSection(str, Enum):
    """Standard report sections."""
    COVER = "cover"
    EXECUTIVE_SUMMARY = "executive_summary"
    OBJECTIVES = "objectives"
    APPROACH = "approach"
    RESULTS = "results"
    TIMELINE = "timeline"
    CONCLUSION = "conclusion"
    NEXT_STEPS = "next_steps"


class ProjectData(BaseModel):
    """Data model for project information with validation."""
    project_id: str = Field(default_factory=lambda: f"PROJ-{uuid4().hex[:8].upper()}")
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=300)
    author: str = Field(..., min_length=1, max_length=100)
    date: Optional[str] = None
    executive_summary: Optional[str] = None
    objectives: List[str] = Field(default_factory=list)
    approach: Optional[str] = None
    results: List[str] = Field(default_factory=list)
    timeline: List[Dict[str, str]] = Field(default_factory=list)
    conclusion: Optional[str] = None
    next_steps: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: Optional[str]) -> str:
        """Set default date if not provided."""
        if v is None:
            return datetime.now().strftime("%B %d, %Y")
        return v

    @field_validator('timeline')
    @classmethod
    def validate_timeline(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate timeline entries have required fields."""
        for entry in v:
            if 'milestone' not in entry or 'date' not in entry:
                raise ValueError("Timeline entries must contain 'milestone' and 'date'")
        return v


class ReportConfig(BaseModel):
    """Configuration for report generation."""
    template_name: str = Field(default="standard")
    output_format: OutputFormat = Field(default=OutputFormat.DOCX)
    include_sections: List[ReportSection] = Field(default_factory=list)
    exclude_sections: List[ReportSection] = Field(default_factory=list)
    style_settings: Dict[str, Any] = Field(default_factory=dict)
    company_branding: Optional[Dict[str, str]] = None

    class Config:
        use_enum_values = True


class ReportSectionRenderer(ABC):
    """Abstract base class for report section renderers."""

    @abstractmethod
    def render(self, doc: Document, data: ProjectData, config: ReportConfig) -> None:
        """Render section to document."""
        pass

    def _add_section_title(self, doc: Document, title: str, level: int = 1) -> None:
        """Add formatted section title."""
        heading = doc.add_heading(title, level=level)
        heading.alignment = WD_ALIGN_PARAGRAPH.LEFT


class CoverPageRenderer(ReportSectionRenderer):
    """Renders report cover page."""

    def render(self, doc: Document, data: ProjectData, config: ReportConfig) -> None:
        """Add cover page with project details."""
        try:
            # Title
            title_para = doc.add_paragraph()
            title_run = title_para.add_run(data.title)
            title_run.font.size = Pt(24)
            title_run.bold = True
            title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Subtitle
            if data.subtitle:
                subtitle_para = doc.add_paragraph()
                subtitle_run = subtitle_para.add_run(data.subtitle)
                subtitle_run.font.size = Pt(14)
                subtitle_run.italic = True
                subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Author and date
            details_para = doc.add_paragraph()
            details_para.add_run(f"Prepared by: {data.author}\n")
            details_para.add_run(f"Date: {data.date}\n")
            details_para.add_run(f"Project ID: {data.project_id}")
            details_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

            doc.add_page_break()
            logger.info("Cover page rendered successfully")

        except Exception as e:
            logger.error(f"Error rendering cover page: {e}")
            raise


class ExecutiveSummaryRenderer(ReportSectionRenderer):
    """Renders executive summary section."""

    def render(self, doc: Document, data: ProjectData, config: ReportConfig) -> None:
        """Add executive summary."""
        if data.executive_summary:
            self._add_section_title(doc, "Executive Summary")
            doc.add_paragraph(data.executive_summary)
            logger.debug("Executive summary section rendered")


class BulletListRenderer(ReportSectionRenderer):
    """Renders bulleted lists for sections."""

    def __init__(self, section_title: str, data_field: str):
        self.section_title = section_title
        self.data_field = data_field

    def render(self, doc: Document, data: ProjectData, config: ReportConfig) -> None:
        """Add bulleted list section."""
        items = getattr(data, self.data_field, [])
        if items:
            self._add_section_title(doc, self.section_title)
            for item in items:
                doc.add_paragraph(item, style="List Bullet")


class ParagraphRenderer(ReportSectionRenderer):
    """Renders simple paragraph sections."""

    def __init__(self, section_title: str, data_field: str):
        self.section_title = section_title
        self.data_field = data_field

    def render(self, doc: Document, data: ProjectData, config: ReportConfig) -> None:
        """Add paragraph section."""
        content = getattr(data, self.data_field, None)
        if content:
            self._add_section_title(doc, self.section_title)
            doc.add_paragraph(content)


class TimelineRenderer(ReportSectionRenderer):
    """Renders project timeline as a table."""

    def render(self, doc: Document, data: ProjectData, config: ReportConfig) -> None:
        """Add timeline table."""
        if data.timeline:
            self._add_section_title(doc, "Project Timeline")
            table = doc.add_table(rows=1, cols=3)
            table.style = "Light Grid Accent 1"

            # Header row
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = "Milestone"
            hdr_cells[1].text = "Date"
            hdr_cells[2].text = "Status"

            # Data rows
            for entry in data.timeline:
                row_cells = table.add_row().cells
                row_cells[0].text = entry.get('milestone', '')
                row_cells[1].text = entry.get('date', '')
                row_cells[2].text = entry.get('status', 'Completed')

            logger.debug("Timeline section rendered")


class ReportTemplate:
    """Manages report template and section rendering."""

    def __init__(self, config: ReportConfig):
        self.config = config
        self.renderers: Dict[ReportSection, ReportSectionRenderer] = self._initialize_renderers()

    def _initialize_renderers(self) -> Dict[ReportSection, ReportSectionRenderer]:
        """Initialize section renderers based on configuration."""
        return {
            ReportSection.COVER: CoverPageRenderer(),
            ReportSection.EXECUTIVE_SUMMARY: ExecutiveSummaryRenderer(),
            ReportSection.OBJECTIVES: BulletListRenderer("Objectives", "objectives"),
            ReportSection.APPROACH: ParagraphRenderer("Approach", "approach"),
            ReportSection.RESULTS: BulletListRenderer("Results", "results"),
            ReportSection.TIMELINE: TimelineRenderer(),
            ReportSection.CONCLUSION: ParagraphRenderer("Conclusion", "conclusion"),
            ReportSection.NEXT_STEPS: BulletListRenderer("Next Steps", "next_steps"),
        }

    def get_render_order(self) -> List[ReportSection]:
        """Determine section rendering order."""
        default_order = [
            ReportSection.COVER,
            ReportSection.EXECUTIVE_SUMMARY,
            ReportSection.OBJECTIVES,
            ReportSection.APPROACH,
            ReportSection.RESULTS,
            ReportSection.TIMELINE,
            ReportSection.CONCLUSION,
            ReportSection.NEXT_STEPS,
        ]

        # Apply inclusions/exclusions
        if self.config.include_sections:
            return [s for s in default_order if s in self.config.include_sections]
        else:
            return [s for s in default_order if s not in self.config.exclude_sections]


class DocumentBuilder:
    """Builds documents using configured templates and data."""

    def __init__(self, template: ReportTemplate):
        self.template = template
        self.document = Document()
        self._setup_document_styles()

    def _setup_document_styles(self) -> None:
        """Configure document styles and formatting."""
        for section in self.document.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

    def build(self, data: ProjectData) -> Document:
        """Build complete document."""
        try:
            render_order = self.template.get_render_order()

            for section in render_order:
                renderer = self.template.renderers.get(section)
                if renderer:
                    renderer.render(self.document, data, self.template.config)
                    logger.debug(f"Rendered section: {section.value}")

            logger.info(f"Document built with {len(render_order)} sections")
            return self.document

        except Exception as e:
            logger.error(f"Error building document: {e}")
            raise


class ReportGenerator:
    """Main report generation orchestrator."""

    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self.template = ReportTemplate(self.config)

    def generate(self, data: ProjectData, output_path: Path) -> None:
        """Generate report from data."""
        try:
            logger.info(f"Generating report: {data.project_id}")

            builder = DocumentBuilder(self.template)
            document = builder.build(data)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save document
            document.save(str(output_path))
            logger.info(f"Report saved to: {output_path}")

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise


class DataLoader:
    """Handles data loading and validation."""

    @staticmethod
    def load_from_json(file_path: Path) -> ProjectData:
        """Load and validate project data from JSON file."""
        try:
            with file_path.open('r', encoding='utf-8') as f:
                raw_data = json.load(f)
            return ProjectData(**raw_data)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            raise


class ConfigManager:
    """Manages configuration loading and validation."""

    @staticmethod
    def load_config(config_path: Optional[Path] = None) -> ReportConfig:
        """Load configuration from file or use defaults."""
        if config_path and config_path.exists():
            try:
                with config_path.open('r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return ReportConfig(**config_data)
            except Exception as e:
                logger.warning(f"Config load failed, using defaults: {e}")

        return ReportConfig()


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Enterprise Portfolio & Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i project.json -o report.docx
  %(prog)s -i project.json -o report.docx --config config.json -v
        """
    )

    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Path to input JSON file with project data"
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("reports/generated_report.docx"),
        help="Output path for generated report (default: reports/generated_report.docx)"
    )

    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to configuration JSON file"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    return parser.parse_args()


def main() -> int:
    """Main execution function."""
    try:
        args = parse_arguments()

        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Validate input file exists
        if not args.input.exists():
            logger.error(f"Input file not found: {args.input}")
            return 1

        # Load configuration
        config = ConfigManager.load_config(args.config)

        # Load and validate data
        project_data = DataLoader.load_from_json(args.input)

        # Generate report
        generator = ReportGenerator(config)
        generator.generate(project_data, args.output)

        logger.info("Report generation completed successfully")
        return 0

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=args.verbose if 'args' in locals() else False)
        return 1


if __name__ == "__main__":
    sys.exit(main())
