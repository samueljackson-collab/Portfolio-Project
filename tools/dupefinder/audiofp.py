"""Audio fingerprint stubs compatible with Chromaprint/pyacoustid."""

from __future__ import annotations

import hashlib
import warnings
from pathlib import Path
from typing import Optional, Tuple

try:  # pragma: no cover - optional dependency
    import acoustid  # type: ignore

    try:
        import chromaprint  # type: ignore
    except Exception:  # pragma: no cover - acoustid brings chromaprint along usually
        chromaprint = None  # type: ignore

    ACOUSTID_AVAILABLE = True
except Exception:  # pragma: no cover - exercised in tests
    ACOUSTID_AVAILABLE = False
    acoustid = None  # type: ignore
    chromaprint = None  # type: ignore


def _fallback_audio_hash(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:20]


def compute_audio_fingerprint(path: Path) -> Tuple[str, Optional[float]]:
    """Return a tuple of (fingerprint, confidence).

    The Chromaprint/AcoustID path is optional; if unavailable we return a deterministic
    fingerprint and ``None`` for the confidence score.
    """

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(path)

    if not ACOUSTID_AVAILABLE:
        warnings.warn(
            "Chromaprint/pyacoustid not available - using digest based audio stub.",
            RuntimeWarning,
            stacklevel=2,
        )
        return _fallback_audio_hash(path), None

    try:  # pragma: no cover - requires audio deps and media files
        fingerprint, _ = acoustid.fingerprint_file(str(path))  # type: ignore[attr-defined]
        confidence: Optional[float] = None
        if isinstance(fingerprint, tuple):
            fp_data, confidence = fingerprint  # type: ignore[assignment]
        else:
            fp_data = fingerprint
        if isinstance(fp_data, bytes):
            fp_data = fp_data.decode("utf8", "ignore")
        return str(fp_data), confidence
    except Exception:
        warnings.warn(
            "Failed to fingerprint audio with Chromaprint - falling back to digest.",
            RuntimeWarning,
            stacklevel=2,
        )
        return _fallback_audio_hash(path), None


__all__ = ["compute_audio_fingerprint", "ACOUSTID_AVAILABLE"]
