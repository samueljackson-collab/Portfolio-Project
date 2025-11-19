"""Vector index abstraction with optional FAISS/HNSW backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

try:  # pragma: no cover - optional dependency
    import faiss  # type: ignore
except Exception:  # noqa: BLE001
    faiss = None  # type: ignore

from .embeddings import cosine_similarity


@dataclass
class SimpleVectorIndex:
    """In-memory fallback index used when FAISS/HNSW is unavailable."""

    dimension: int
    items: Dict[str, List[float]] = field(default_factory=dict)

    def add(self, key: str, vector: Iterable[float]) -> None:
        data = list(vector)
        if len(data) != self.dimension:
            raise ValueError("vector dimension mismatch")
        self.items[key] = data

    def query(self, vector: Iterable[float], k: int = 5) -> List[Tuple[str, float]]:
        probe = list(vector)
        if len(probe) != self.dimension:
            return []
        scores = [(key, cosine_similarity(probe, vec)) for key, vec in self.items.items()]
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:k]


def create_index(dimension: int):
    """Create a FAISS index if available, otherwise fall back to the simple implementation."""

    if faiss is not None:  # pragma: no cover - heavy dep
        index = faiss.IndexFlatIP(dimension)
        return index
    return SimpleVectorIndex(dimension)
