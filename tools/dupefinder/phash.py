"""Perceptual hashing utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - optional dependency
    from PIL import Image
    import imagehash
except Exception:  # noqa: BLE001 - broad for optional deps
    Image = None  # type: ignore
    imagehash = None  # type: ignore


def compute_phash(path: Path) -> Optional[str]:
    """Compute a perceptual hash if dependencies are available."""

    if imagehash is not None and Image is not None:  # pragma: no cover
        with Image.open(path) as img:
            return str(imagehash.phash(img))
    # Fallback to a deterministic but simple hash for testability.
    digest = hashlib.sha1(path.read_bytes()).hexdigest()
    return digest[:16]
