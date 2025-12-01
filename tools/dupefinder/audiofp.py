"""Audio fingerprint helpers with optional Chromaprint support."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional, Tuple

try:  # pragma: no cover - optional dependency
    import acoustid
    import chromaprint
except Exception:  # noqa: BLE001 - optional dependencies may be missing
    acoustid = None  # type: ignore
    chromaprint = None  # type: ignore


def compute_fingerprint(path: Path) -> Tuple[Optional[str], Optional[int]]:
    """Return a Chromaprint-style fingerprint when available, else a stub hash."""

    if acoustid is not None and chromaprint is not None:  # pragma: no cover
        duration, fp = acoustid.fingerprint_file(str(path))
        return fp, duration
    data = path.read_bytes()
    digest = hashlib.md5(data).hexdigest()
    return digest[:32], None
