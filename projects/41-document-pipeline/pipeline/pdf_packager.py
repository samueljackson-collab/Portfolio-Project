#!/usr/bin/env python3
"""
pdf_packager.py — Packages generated documents into a ZIP archive with a manifest.

In this pipeline, documents are produced as Markdown files. This module collects
them into a single distributable ZIP bundle that includes a JSON manifest describing
every file in the archive.
"""
import json
import os
import zipfile
import datetime
from pathlib import Path
from typing import Dict, List


def build_manifest(documents: List[Dict], generated_at: str) -> Dict:
    """
    Build a JSON manifest dictionary for the document bundle.

    Parameters
    ----------
    documents:
        List of document metadata records (as produced by DocumentGenerator).
    generated_at:
        ISO-format timestamp for when the bundle was created.

    Returns
    -------
    dict — manifest structure that will be serialised to manifest.json inside the ZIP.
    """
    return {
        "bundle_version": "1.0",
        "generated_at": generated_at,
        "document_count": len(documents),
        "documents": [
            {
                "document_id": doc["document_id"],
                "title": doc["title"],
                "type": doc["type"],
                "template": doc["template"],
                "filename": Path(doc["path"]).name,
                "word_count": doc["word_count"],
                "file_size_bytes": doc["file_size_bytes"],
                "status": doc["status"],
            }
            for doc in documents
        ],
    }


def package_documents(
    documents: List[Dict],
    index_csv_path: str,
    output_zip_path: str,
) -> int:
    """
    Package all generated documents and the CSV index into a ZIP archive.

    Creates the output directory if it does not exist.  Adds a ``manifest.json``
    at the root of the archive describing every included file.

    Parameters
    ----------
    documents:
        List of document metadata dicts (each must have a ``path`` key).
    index_csv_path:
        Absolute path to the CSV index file to include in the bundle.
    output_zip_path:
        Destination path for the ZIP file.

    Returns
    -------
    int — total byte size of the created ZIP file.
    """
    output_zip = Path(output_zip_path)
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    now_iso = datetime.datetime.now().isoformat(timespec="seconds")
    manifest = build_manifest(documents, now_iso)

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Add each generated document
        for doc in documents:
            doc_path = Path(doc["path"])
            if doc_path.exists():
                zf.write(doc_path, arcname=f"documents/{doc_path.name}")

        # Add the CSV index
        index_path = Path(index_csv_path)
        if index_path.exists():
            zf.write(index_path, arcname="document_index.csv")

        # Add the manifest
        manifest_json = json.dumps(manifest, indent=2)
        zf.writestr("manifest.json", manifest_json)

    return output_zip.stat().st_size


def extract_bundle(zip_path: str, extract_to: str) -> List[str]:
    """
    Extract a document bundle to the given directory.

    Returns the list of extracted file names.
    """
    extract_dir = Path(extract_to)
    extract_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
        extracted = zf.namelist()
    return extracted


def read_manifest(zip_path: str) -> Dict:
    """Read and return the manifest.json from a bundle ZIP without fully extracting it."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        with zf.open("manifest.json") as f:
            return json.loads(f.read().decode("utf-8"))
