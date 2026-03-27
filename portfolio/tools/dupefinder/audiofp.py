
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

try:
    import chromaprint  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    chromaprint = None  # type: ignore
    logging.getLogger(__name__).warning("Chromaprint not available; audio fingerprints will be stubbed")


def compute_audio_fingerprint(path: Path) -> Optional[str]:
    if chromaprint is None:
        return None
    try:
        fingerprint, _ = chromaprint.encode_file(str(path))
        return fingerprint  # pragma: no cover - depends on native lib
    except Exception:  # pragma: no cover - best effort only
        return None
