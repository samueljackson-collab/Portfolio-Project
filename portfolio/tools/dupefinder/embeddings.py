from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

try:
    import torch  # type: ignore
    from transformers import CLIPProcessor, CLIPModel  # type: ignore
except Exception:  # pragma: no cover - optional heavy deps
    torch = None  # type: ignore
    CLIPProcessor = None  # type: ignore
    CLIPModel = None  # type: ignore
    logging.getLogger(__name__).warning("CLIP not available; embeddings will be stubbed")


def generate_embedding(path: Path) -> Optional[list[float]]:
    if torch is None or CLIPModel is None or CLIPProcessor is None:
        return None
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    inputs = processor(text=[path.name], images=None, return_tensors="pt", padding=True)  # type: ignore[arg-type]
    with torch.no_grad():  # pragma: no cover - heavy dependency
        text_features = model.get_text_features(**inputs)
    return text_features[0].tolist()  # pragma: no cover
