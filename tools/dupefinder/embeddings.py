"""Embedding helpers for semantic duplicate detection."""

from __future__ import annotations

import hashlib
import math
import warnings
from pathlib import Path
from typing import Dict, Iterable, List

try:  # pragma: no cover - optional dependency
    import torch  # type: ignore
    import clip  # type: ignore

    CLIP_AVAILABLE = True
except Exception:  # pragma: no cover - exercised in tests
    CLIP_AVAILABLE = False
    torch = None  # type: ignore
    clip = None  # type: ignore


Vector = List[float]


def _normalize(values: Iterable[float]) -> Vector:
    vector = [float(v) for v in values]
    norm = math.sqrt(sum(component * component for component in vector))
    if norm == 0:
        return vector
    return [component / norm for component in vector]


def _fallback_vector(path: Path) -> Vector:
    data = hashlib.sha256(path.read_bytes()).digest()
    # Map digest to a small 8 dimensional vector in [0, 1]
    floats = [(byte / 255.0) for byte in data[:8]]
    return _normalize(floats)


def compute_embedding(path: Path) -> Dict[str, object]:
    """Compute an embedding representation for *path*.

    The default implementation uses a lightweight digest based fallback when CLIP is
    not available. A structured dictionary is returned so callers can reason about
    the metadata irrespective of the backend.
    """

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(path)

    if not CLIP_AVAILABLE:
        warnings.warn(
            "OpenAI CLIP not available - using deterministic fallback embeddings.",
            RuntimeWarning,
            stacklevel=2,
        )
        vector = _fallback_vector(path)
        return {
            "model": "stub",
            "vector": vector,
            "dim": len(vector),
            "normalized": True,
            "metadata": {"backend": "sha256"},
        }

    try:  # pragma: no cover - requires heavyweight deps
        model, preprocess = clip.load("ViT-B/32", device="cpu")  # type: ignore[arg-type]
        image = preprocess(Path(path).open("rb"))  # type: ignore[call-arg]
        with torch.no_grad():
            embedding = model.encode_image(image.unsqueeze(0))
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        vector = embedding.squeeze(0).cpu().tolist()
        return {
            "model": "clip-vit-b32",
            "vector": vector,
            "dim": len(vector),
            "normalized": True,
            "metadata": {"backend": "clip"},
        }
    except Exception:
        warnings.warn(
            "CLIP embedding failed - using fallback digest embedding.",
            RuntimeWarning,
            stacklevel=2,
        )
        vector = _fallback_vector(path)
        return {
            "model": "stub",
            "vector": vector,
            "dim": len(vector),
            "normalized": True,
            "metadata": {"backend": "sha256"},
        }


__all__ = ["compute_embedding", "CLIP_AVAILABLE"]
