"""
Tests for the Document Packaging Pipeline.

All tests use temporary directories so they never depend on pre-existing
generated files and leave no side-effects in the repo.
"""
import csv
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure the project root is importable regardless of working directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.document_generator import DocumentGenerator
from pipeline.pdf_packager import package_documents, read_manifest
from pipeline.xlsx_exporter import XlsxExporter

TEMPLATE_DIR = str(PROJECT_ROOT / "templates")

# ---------------------------------------------------------------------------
# Minimal context fixtures
# ---------------------------------------------------------------------------

MINIMAL_REPORT_CONTEXT = {
    "title": "Test Infrastructure Report",
    "author": "Test Author",
    "date": "2026-01-01",
    "summary": "All systems nominal.",
    "metrics": [
        {"name": "Uptime", "value": "99.99%", "target": "99.9%", "status": "PASS"},
        {"name": "Error Rate", "value": "0.01%", "target": "< 0.1%", "status": "PASS"},
    ],
    "findings": [
        {"text": "No critical findings."},
    ],
    "recommendations": [
        {"title": "Continue monitoring", "detail": "Maintain current cadence."},
    ],
}

MINIMAL_RUNBOOK_CONTEXT = {
    "title": "Test Runbook",
    "author": "Ops Team",
    "date": "2026-01-01",
    "overview": "A minimal test runbook.",
    "prerequisites": ["Access to production console"],
    "steps": [
        {"title": "Step one", "detail": "Do the first thing."},
        {"title": "Step two", "detail": "Do the second thing."},
    ],
    "validations": ["Service returns HTTP 200"],
    "rollback_steps": ["Revert the change"],
    "contacts": [
        {"Role": "On-Call", "Name": "Alice", "Contact": "alice@example.com"},
    ],
}

MINIMAL_IR_CONTEXT = {
    "title": "INC-TEST-001 Test Incident Report",
    "incident_id": "INC-TEST-001",
    "author": "Incident Commander",
    "date": "2026-01-01",
    "impact_description": "No real impact — test only.",
    "summary_fields": [
        ["Incident ID", "INC-TEST-001"],
        ["Severity", "SEV-3"],
    ],
    "timeline": [
        ["10:00", "Alert fired", "PagerDuty"],
        ["10:05", "Resolved", "Engineer"],
    ],
    "root_cause": "Test root cause.",
    "contributing_factors": ["Factor one"],
    "remediation_actions": [{"title": "Fixed it", "detail": "Applied patch."}],
    "action_items": [
        {"Action": "Write runbook", "Owner": "Alice", "Due Date": "2026-02-01", "Priority": "P2"},
    ],
    "lessons_learned": ["Always write tests."],
}


# ---------------------------------------------------------------------------
# test_template_loading
# ---------------------------------------------------------------------------

def test_template_loading_report():
    """DocumentGenerator.load_template parses report-template.yaml correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        tmpl = gen.load_template("report-template")
        assert tmpl["document_type"] == "report"
        assert "sections" in tmpl
        section_ids = [s["id"] for s in tmpl["sections"]]
        assert "executive_summary" in section_ids
        assert "metrics" in section_ids


def test_template_loading_runbook():
    """DocumentGenerator.load_template parses runbook-template.yaml correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        tmpl = gen.load_template("runbook-template")
        assert tmpl["document_type"] == "runbook"
        section_ids = [s["id"] for s in tmpl["sections"]]
        assert "prerequisites" in section_ids
        assert "steps" in section_ids
        assert "rollback" in section_ids


def test_template_loading_incident_report():
    """DocumentGenerator.load_template parses incident-report-template.yaml correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        tmpl = gen.load_template("incident-report-template")
        assert tmpl["document_type"] == "incident_report"
        section_ids = [s["id"] for s in tmpl["sections"]]
        assert "timeline" in section_ids
        assert "root_cause" in section_ids


# ---------------------------------------------------------------------------
# test_markdown_generation
# ---------------------------------------------------------------------------

def test_markdown_generation_contains_title():
    """Generated Markdown starts with the document title as an H1 heading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        tmpl = gen.load_template("report-template")
        md = gen.generate_markdown(tmpl, MINIMAL_REPORT_CONTEXT)
        assert "# Test Infrastructure Report" in md


def test_markdown_generation_contains_author():
    """Generated Markdown includes the author metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        tmpl = gen.load_template("report-template")
        md = gen.generate_markdown(tmpl, MINIMAL_REPORT_CONTEXT)
        assert "Test Author" in md


def test_markdown_generation_metrics_table():
    """Metrics are rendered as a Markdown table with correct column headers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        tmpl = gen.load_template("report-template")
        md = gen.generate_markdown(tmpl, MINIMAL_REPORT_CONTEXT)
        assert "Metric" in md
        assert "Value" in md
        assert "Target" in md
        assert "Status" in md
        assert "Uptime" in md
        assert "99.99%" in md


def test_markdown_generation_runbook_steps():
    """Runbook Markdown contains numbered procedure steps."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        tmpl = gen.load_template("runbook-template")
        md = gen.generate_markdown(tmpl, MINIMAL_RUNBOOK_CONTEXT)
        assert "Step one" in md
        assert "Step two" in md
        assert "Procedure" in md


# ---------------------------------------------------------------------------
# test_generated_report_has_all_sections
# ---------------------------------------------------------------------------

def test_generated_report_has_all_sections():
    """A generated report Markdown contains all expected section headings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        path = gen.generate_report("report-template", MINIMAL_REPORT_CONTEXT)
        content = Path(path).read_text()
        assert "## Executive Summary" in content
        assert "## Key Metrics" in content
        assert "## Findings" in content
        assert "## Recommendations" in content


def test_generated_runbook_has_all_sections():
    """A generated runbook contains all required operational sections."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        path = gen.generate_report("runbook-template", MINIMAL_RUNBOOK_CONTEXT)
        content = Path(path).read_text()
        assert "## Overview" in content
        assert "## Prerequisites" in content
        assert "## Procedure" in content
        assert "## Validation Checks" in content
        assert "## Rollback Procedure" in content


def test_generated_ir_has_all_sections():
    """A generated incident report contains the required investigation sections."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        path = gen.generate_report("incident-report-template", MINIMAL_IR_CONTEXT)
        content = Path(path).read_text()
        assert "## Incident Timeline" in content
        assert "## Root Cause Analysis" in content
        assert "## Follow-Up Action Items" in content
        assert "## Lessons Learned" in content


# ---------------------------------------------------------------------------
# test_csv_index_has_correct_headers
# ---------------------------------------------------------------------------

def test_csv_index_has_correct_headers():
    """The exported CSV index has the required column headers."""
    expected_headers = [
        "document_id", "title", "type", "template",
        "generated_at", "word_count", "file_size_bytes", "status",
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        gen.generate_report("report-template", MINIMAL_REPORT_CONTEXT)
        index_path = gen.export_index()
        with open(index_path, newline="") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == expected_headers


def test_csv_index_row_count():
    """The CSV index has exactly one row per generated document."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        gen.generate_report("report-template", MINIMAL_REPORT_CONTEXT)
        gen.generate_report("runbook-template", MINIMAL_RUNBOOK_CONTEXT)
        index_path = gen.export_index()
        with open(index_path, newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2


def test_csv_index_status_complete():
    """Every row in the CSV index has status=complete."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        gen.generate_report("report-template", MINIMAL_REPORT_CONTEXT)
        gen.generate_report("runbook-template", MINIMAL_RUNBOOK_CONTEXT)
        index_path = gen.export_index()
        with open(index_path, newline="") as f:
            rows = list(csv.DictReader(f))
        assert all(row["status"] == "complete" for row in rows)


# ---------------------------------------------------------------------------
# test_generated_files_exist
# ---------------------------------------------------------------------------

def test_generated_files_exist():
    """generate_report writes files to disk that actually exist and are non-empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        path = gen.generate_report("report-template", MINIMAL_REPORT_CONTEXT)
        p = Path(path)
        assert p.exists(), f"Expected file at {path} but it does not exist"
        assert p.stat().st_size > 0, "Generated file should not be empty"


def test_all_three_generated_files_exist():
    """All three document types are written to disk when generated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        paths = [
            gen.generate_report("report-template", MINIMAL_REPORT_CONTEXT),
            gen.generate_report("runbook-template", MINIMAL_RUNBOOK_CONTEXT),
            gen.generate_report("incident-report-template", MINIMAL_IR_CONTEXT),
        ]
        for p in paths:
            assert Path(p).exists()
            assert Path(p).stat().st_size > 100


def test_generated_file_has_markdown_extension():
    """Generated documents are written as .md files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        path = gen.generate_report("report-template", MINIMAL_REPORT_CONTEXT)
        assert path.endswith(".md")


def test_bundle_zip_created():
    """package_documents creates a ZIP file containing all documents and a manifest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        gen.generate_report("report-template", MINIMAL_REPORT_CONTEXT)
        gen.generate_report("runbook-template", MINIMAL_RUNBOOK_CONTEXT)
        index_path = gen.export_index()
        zip_path = os.path.join(tmpdir, "bundle.zip")
        size = package_documents(gen.generated, index_path, zip_path)
        assert Path(zip_path).exists()
        assert size > 0
        manifest = read_manifest(zip_path)
        assert manifest["document_count"] == 2
        assert len(manifest["documents"]) == 2


def test_xlsx_exporter_summary_csv():
    """XlsxExporter produces a summary CSV with the correct headers and row count."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = DocumentGenerator(TEMPLATE_DIR, tmpdir)
        gen.generate_report("report-template", MINIMAL_REPORT_CONTEXT)
        gen.generate_report("runbook-template", MINIMAL_RUNBOOK_CONTEXT)

        exporter = XlsxExporter(tmpdir)
        summary_path = exporter.export_document_summary(gen.generated)
        assert Path(summary_path).exists()
        with open(summary_path, newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
        assert "document_id" in rows[0]
        assert "word_count" in rows[0]
