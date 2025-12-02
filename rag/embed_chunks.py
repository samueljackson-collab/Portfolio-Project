"""
Embed all RAG chunks and write them to embeddings.jsonl

Usage examples:

    # Dry run (no embeddings, just structure check)
    python -m rag.embed_chunks --dry-run

    # Use OpenAI embeddings (requires OPENAI_API_KEY)
    python -m rag.embed_chunks --provider openai --model text-embedding-3-large

This script expects:
- rag/manifest.json
- rag/chunks/*.md

and will output:
- rag/embeddings.jsonl   (one JSON object per line)

Each line looks like:
{
  "id": "rt-external-infra-pentest-summary",
  "embedding": [0.123, 0.456, ...],
  "metadata": {
    "project_slug": "...",
    "project_title": "...",
    "category": "...",
    "section": "...",
    "tags": [...]
  }
}

IMPORTANT:
- The OpenAI call here is a working example, but you can replace it with any
  embedding provider as long as `embed_texts()` returns list[list[float]].
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .rag_loader import iter_chunks, RagChunk


RAG_ROOT = Path(__file__).resolve().parent
EMBEDDINGS_PATH = RAG_ROOT / "embeddings.jsonl"


# -------- Embedding provider abstraction ------------------------------------


def embed_texts_openai(
    texts: List[str],
    model: str,
    api_key: Optional[str] = None,
) -> List[List[float]]:
    """
    Embed a list of texts using OpenAI's embeddings API.

    Requires:
        pip install openai

    And env var:
        OPENAI_API_KEY=sk-...

    Returns:
        List of embedding vectors (one per input text).
    """
    if importlib.util.find_spec("openai") is None:
        raise RuntimeError(
            "openai package is not installed. Run `pip install openai`."
        )

    from openai import OpenAI

    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    client = OpenAI(api_key=api_key)

    response = client.embeddings.create(
        model=model,
        input=texts,
    )

    vectors: List[List[float]] = []
    for item in response.data:
        vectors.append(item.embedding)  # type: ignore[attr-defined]

    if len(vectors) != len(texts):
        raise RuntimeError(
            f"Expected {len(texts)} embeddings, got {len(vectors)} from provider."
        )

    return vectors


def embed_texts_dummy(texts: List[str], dim: int = 8) -> List[List[float]]:
    """
    Dummy embedding function for testing or offline dev.

    Returns low-dimension vectors filled with zeros.
    """
    return [[0.0] * dim for _ in texts]


# -------- Core logic ---------------------------------------------------------


def chunk_to_record(chunk: RagChunk, embedding: List[float]) -> Dict[str, Any]:
    """
    Convert a RagChunk + embedding into a JSON-serializable record.
    """
    meta_dict = {
        "project_slug": chunk.meta.project_slug,
        "project_title": chunk.meta.project_title,
        "category": chunk.meta.category,
        "section": chunk.meta.section,
        "path": chunk.meta.path,
        "tokens_estimate": chunk.meta.tokens_estimate,
        "tags": chunk.meta.tags or [],
    }
    return {
        "id": chunk.meta.id,
        "embedding": embedding,
        "metadata": meta_dict,
    }


def generate_embeddings(
    provider: str,
    model: Optional[str] = None,
    batch_size: int = 8,
    dry_run: bool = False,
) -> None:
    """
    Main routine:

    - Load all RagChunks
    - Batch texts
    - Call embedding provider
    - Write JSONL to rag/embeddings.jsonl
    """
    chunks: List[RagChunk] = list(iter_chunks())
    if not chunks:
        raise RuntimeError("No chunks found. Check rag/manifest.json and rag/chunks/.")

    print(f"[embed] Loaded {len(chunks)} chunks from manifest.")

    if dry_run:
        print("[embed] DRY RUN mode: not calling any embedding API, not writing file.")
        out_f = None
    else:
        if EMBEDDINGS_PATH.exists():
            print(f"[embed] Overwriting existing file: {EMBEDDINGS_PATH}")
        else:
            print(f"[embed] Writing embeddings to: {EMBEDDINGS_PATH}")
        out_f = EMBEDDINGS_PATH.open("w", encoding="utf-8")

    try:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c.text for c in batch]
            ids = [c.meta.id for c in batch]

            print(f"[embed] Processing batch {i // batch_size + 1} containing {len(batch)} chunks.")

            if dry_run:
                print("        (dry-run) ids:", ", ".join(ids))
                continue

            if provider == "openai":
                if not model:
                    raise RuntimeError("Model is required when provider is 'openai'.")
                embeddings = embed_texts_openai(texts, model=model)
            elif provider == "dummy":
                embeddings = embed_texts_dummy(texts)
            else:
                raise ValueError(f"Unknown provider: {provider!r}")

            if len(embeddings) != len(batch):
                raise RuntimeError(
                    f"Embedding count mismatch for batch starting at {i}: "
                    f"{len(batch)} chunks vs {len(embeddings)} embeddings."
                )

            if out_f is None:
                continue

            for chunk, emb in zip(batch, embeddings):
                record = chunk_to_record(chunk, emb)
                json_line = json.dumps(record, ensure_ascii=False)
                out_f.write(json_line + "\n")

    finally:
        if out_f is not None:
            out_f.close()
            print(f"[embed] Finished writing embeddings to {EMBEDDINGS_PATH}")


# -------- CLI entrypoint -----------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Embed RAG chunks and write to embeddings.jsonl"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "dummy"],
        default="dummy",
        help="Embedding provider to use (default: dummy).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Embedding model name (required for provider=openai).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size for embedding requests (default: 8).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not call embedding provider or write file; only list chunks.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_embeddings(
        provider=args.provider,
        model=args.model,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
