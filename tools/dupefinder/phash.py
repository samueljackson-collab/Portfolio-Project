"""Perceptual hash helpers with graceful fallbacks."""

from __future__ import annotations

import hashlib
import warnings
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - optional dependency
    from PIL import Image
    import imagehash

    IMAGEHASH_AVAILABLE = True
except Exception:  # pragma: no cover - exercised during tests
    IMAGEHASH_AVAILABLE = False
    Image = None  # type: ignore
    imagehash = None  # type: ignore


def _fallback_hash(path: Path) -> str:
    data = path.read_bytes()
    digest = hashlib.sha1(data).hexdigest()
    return digest[:16]


def compute_phash(path: Path) -> Optional[str]:
    """Return a perceptual hash string for *path*.

    When :mod:`imagehash` (and Pillow) are unavailable a deterministic hash based on
    the file contents is returned instead. The stub emits a warning to make it clear
    that the high quality backend is missing, but it still enables tests to run.
    """

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(path)

    if not IMAGEHASH_AVAILABLE:
        warnings.warn(
            "imagehash/Pillow not available - using a simple SHA1 based fallback.",
            RuntimeWarning,
            stacklevel=2,
        )
        return _fallback_hash(path)

    try:  # pragma: no cover - exercised when deps are installed
        with Image.open(path) as handle:  # type: ignore[misc]
            phash = imagehash.phash(handle)
            return str(phash)
    except Exception:
        warnings.warn(
            "Failed to compute perceptual hash with imagehash, falling back to SHA1.",
            RuntimeWarning,
            stacklevel=2,
        )
        return _fallback_hash(path)


__all__ = ["compute_phash", "IMAGEHASH_AVAILABLE"]
