from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
    import imagehash
except Exception:  # pragma: no cover - optional dependency
    Image = None  # type: ignore
    imagehash = None  # type: ignore
    logging.getLogger(__name__).warning("imagehash not available; pHash will be stubbed")


def compute_phash(path: Path) -> Optional[str]:
    if Image is None or imagehash is None:
        return None
    try:
        with Image.open(path) as img:
            return str(imagehash.phash(img))
    except Exception:  # pragma: no cover - best effort only
        return None
