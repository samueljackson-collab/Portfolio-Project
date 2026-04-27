from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

RAG_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = RAG_ROOT / "manifest.json"
CHUNKS_DIR = RAG_ROOT / "chunks"


@dataclass
class RagChunkMeta:
    id: str
    project_slug: str
    project_title: str
    category: str
    section: str
    path: str
    tokens_estimate: Optional[int] = None
    tags: Optional[List[str]] = None


@dataclass
class RagChunk:
    meta: RagChunkMeta
    text: str


def load_manifest() -> List[Dict[str, object]]:
    """Load and normalize the RAG manifest file."""
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found at {MANIFEST_PATH}")

    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "chunks" in data:
        entries = data["chunks"]
    elif isinstance(data, list):
        entries = data
    else:
        raise ValueError("Manifest must be a list or contain a 'chunks' list.")

    if not isinstance(entries, list):
        raise ValueError("Manifest 'chunks' value must be a list.")

    return entries


def _meta_from_entry(entry: Dict[str, object]) -> RagChunkMeta:
    required_keys = [
        "id",
        "project_slug",
        "project_title",
        "category",
        "section",
        "path",
    ]
    for key in required_keys:
        if key not in entry:
            raise KeyError(f"Manifest entry missing required field: {key}")

    return RagChunkMeta(
        id=str(entry["id"]),
        project_slug=str(entry["project_slug"]),
        project_title=str(entry["project_title"]),
        category=str(entry["category"]),
        section=str(entry["section"]),
        path=str(entry["path"]),
        tokens_estimate=int(entry["tokens_estimate"]) if "tokens_estimate" in entry and entry["tokens_estimate"] is not None else None,
        tags=list(entry.get("tags", [])) if entry.get("tags") is not None else None,
    )


def iter_chunks() -> Iterable[RagChunk]:
    """Yield :class:`RagChunk` objects described in the manifest."""
    entries = load_manifest()

    for entry in entries:
        meta = _meta_from_entry(entry)
        chunk_path = Path(meta.path)
        if not chunk_path.is_absolute():
            chunk_path = RAG_ROOT / chunk_path

        if not chunk_path.exists():
            raise FileNotFoundError(f"Chunk file not found: {chunk_path}")

        text = chunk_path.read_text(encoding="utf-8")
        yield RagChunk(meta=meta, text=text)


__all__ = [
    "RagChunk",
    "RagChunkMeta",
    "MANIFEST_PATH",
    "CHUNKS_DIR",
    "iter_chunks",
    "load_manifest",
]
