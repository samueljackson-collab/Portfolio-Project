#!/usr/bin/env python3
"""
xlsx_exporter.py — Exports structured pipeline data to CSV (Excel-compatible).

Generates a metrics/summary spreadsheet from the documents produced by the pipeline.
All output is in standard CSV format so it can be opened directly in Excel, Google
Sheets, or any spreadsheet application without additional dependencies.
"""
import csv
import datetime
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


# ---------------------------------------------------------------------------
# Column definitions for each sheet type
# ---------------------------------------------------------------------------

SUMMARY_COLUMNS = [
    "document_id",
    "title",
    "type",
    "template",
    "generated_at",
    "word_count",
    "file_size_bytes",
    "status",
]

METRICS_COLUMNS = [
    "document_id",
    "document_title",
    "metric_name",
    "metric_value",
    "metric_target",
    "metric_status",
]

BATCH_STATS_COLUMNS = [
    "run_timestamp",
    "total_documents",
    "total_words",
    "total_size_bytes",
    "avg_words_per_doc",
    "avg_size_bytes_per_doc",
    "templates_used",
    "status",
]


# ---------------------------------------------------------------------------
# Exporter class
# ---------------------------------------------------------------------------

class XlsxExporter:
    """
    Exports pipeline output data to CSV files suitable for Excel / Google Sheets.

    Each ``export_*`` method writes one CSV 'sheet' (file).  All files land in
    ``output_dir`` with a consistent naming scheme so they can be consumed by
    downstream BI tools or manually reviewed.
    """

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.exported_files: List[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def export_document_summary(self, documents: List[Dict]) -> str:
        """
        Write a one-row-per-document summary CSV.

        Parameters
        ----------
        documents:
            List of document metadata dicts from DocumentGenerator.generated.

        Returns
        -------
        str — absolute path of the written CSV file.
        """
        path = self.output_dir / "document_summary.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=SUMMARY_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for doc in documents:
                writer.writerow({k: doc.get(k, "") for k in SUMMARY_COLUMNS})
        self.exported_files.append(str(path))
        return str(path)

    def export_metrics(self, documents_with_metrics: List[Dict]) -> str:
        """
        Write a flattened metrics CSV — one row per metric across all documents.

        Each dict in ``documents_with_metrics`` should have:
            - document_id: str
            - title: str
            - metrics: list of dicts with keys name/value/target/status

        Returns
        -------
        str — absolute path of the written CSV file.
        """
        path = self.output_dir / "metrics_detail.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=METRICS_COLUMNS)
            writer.writeheader()
            for doc in documents_with_metrics:
                doc_id = doc.get("document_id", "")
                doc_title = doc.get("title", "")
                for m in doc.get("metrics", []):
                    writer.writerow({
                        "document_id": doc_id,
                        "document_title": doc_title,
                        "metric_name": m.get("name", m.get("Metric", "")),
                        "metric_value": m.get("value", m.get("Value", "")),
                        "metric_target": m.get("target", m.get("Target", "")),
                        "metric_status": m.get("status", m.get("Status", "")),
                    })
        self.exported_files.append(str(path))
        return str(path)

    def export_batch_stats(self, documents: List[Dict], run_timestamp: Optional[str] = None) -> str:
        """
        Write aggregate statistics for the pipeline run to a single-row CSV.

        Returns
        -------
        str — absolute path of the written CSV file.
        """
        ts = run_timestamp or datetime.datetime.now().isoformat(timespec="seconds")
        total_docs = len(documents)
        total_words = sum(d.get("word_count", 0) for d in documents)
        total_bytes = sum(d.get("file_size_bytes", 0) for d in documents)
        avg_words = round(total_words / total_docs, 1) if total_docs else 0
        avg_bytes = round(total_bytes / total_docs, 1) if total_docs else 0
        templates = ", ".join(sorted({d.get("template", "") for d in documents}))

        path = self.output_dir / "batch_stats.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=BATCH_STATS_COLUMNS)
            writer.writeheader()
            writer.writerow({
                "run_timestamp": ts,
                "total_documents": total_docs,
                "total_words": total_words,
                "total_size_bytes": total_bytes,
                "avg_words_per_doc": avg_words,
                "avg_size_bytes_per_doc": avg_bytes,
                "templates_used": templates,
                "status": "SUCCESS",
            })
        self.exported_files.append(str(path))
        return str(path)

    def export_all(
        self,
        documents: List[Dict],
        documents_with_metrics: Optional[List[Dict]] = None,
        run_timestamp: Optional[str] = None,
    ) -> List[str]:
        """
        Run all export methods and return a list of written file paths.

        Parameters
        ----------
        documents:
            List of document metadata dicts.
        documents_with_metrics:
            Optional subset of documents that carry a ``metrics`` key.
            If omitted, ``export_metrics`` is skipped.
        run_timestamp:
            ISO timestamp for the run; defaults to now.
        """
        paths = []
        paths.append(self.export_document_summary(documents))
        if documents_with_metrics:
            paths.append(self.export_metrics(documents_with_metrics))
        paths.append(self.export_batch_stats(documents, run_timestamp))
        return paths


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def export_pipeline_results(
    documents: List[Dict],
    output_dir: str,
    documents_with_metrics: Optional[List[Dict]] = None,
) -> List[str]:
    """
    Convenience wrapper: create an XlsxExporter and run all exports.

    Returns list of written CSV file paths.
    """
    exporter = XlsxExporter(output_dir)
    return exporter.export_all(
        documents=documents,
        documents_with_metrics=documents_with_metrics,
        run_timestamp=datetime.datetime.now().isoformat(timespec="seconds"),
    )
