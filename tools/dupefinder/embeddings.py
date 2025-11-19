"""Lightweight embedding helpers with optional CLIP integration."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, List, Optional

try:  # pragma: no cover - optional dependency
    from PIL import Image
    import torch
    from transformers import CLIPModel, CLIPProcessor
except Exception:  # noqa: BLE001 - intentional broad catch for optional deps
    Image = None  # type: ignore
    CLIPModel = None  # type: ignore
    CLIPProcessor = None  # type: ignore
    torch = None  # type: ignore

_MODEL = None
_PROCESSOR = None


def _load_clip() -> bool:
    """Attempt to lazily load CLIP if available."""

    global _MODEL, _PROCESSOR
    if CLIPModel is None or CLIPProcessor is None or torch is None:
        return False
    if _MODEL is None or _PROCESSOR is None:
        _MODEL = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")  # pragma: no cover - heavy path
        _PROCESSOR = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return True


def embed_path(path: Path) -> Optional[List[float]]:
    """Generate a deterministic embedding for a file.

    Falls back to a stable hash-based embedding when CLIP is unavailable.
    """

    if Image is not None and _load_clip():  # pragma: no cover - requires heavy deps
        image = Image.open(path)
        inputs = _PROCESSOR(images=image, return_tensors="pt")
        outputs = _MODEL.get_image_features(**inputs)
        return outputs.detach().numpy().flatten().tolist()
    data = path.read_bytes()
    digest = hashlib.sha256(data).digest()
    return [int(b) / 255 for b in digest[:16]]


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    """Compute cosine similarity between two vectors."""

    vec_a = list(a)
    vec_b = list(b)
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(x * y for x, y in zip(vec_a, vec_b))
    norm_a = sum(x * x for x in vec_a) ** 0.5
    norm_b = sum(y * y for y in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
