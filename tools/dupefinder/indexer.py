"""Similarity index helpers with optional accelerated backends."""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:  # pragma: no cover - optional dependency detection
    import faiss  # type: ignore

    FAISS_AVAILABLE = True
except Exception:  # pragma: no cover - exercised during tests
    FAISS_AVAILABLE = False
    faiss = None  # type: ignore

try:  # pragma: no cover - optional dependency detection
    import hnswlib  # type: ignore

    HNSW_AVAILABLE = True
except Exception:  # pragma: no cover - exercised during tests
    HNSW_AVAILABLE = False
    hnswlib = None  # type: ignore


Vector = Sequence[float]
Result = Tuple[str, float]


def _cosine(a: Vector, b: Vector) -> float:
    numerator = sum(x * y for x, y in zip(a, b))
    denom_a = math.sqrt(sum(x * x for x in a))
    denom_b = math.sqrt(sum(y * y for y in b))
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return numerator / (denom_a * denom_b)


class Indexer:
    """Simple similarity index with optional acceleration."""

    def __init__(self, metric: str = "cosine") -> None:
        self.metric = metric
        self._dim: Optional[int] = None  # type: ignore[assignment]
        self._vectors: List[List[float]] = []
        self._ids: List[str] = []
        self._id_to_index: Dict[str, int] = {}
        self._faiss_index = None
        self._hnsw_index = None

    @property
    def dimension(self) -> Optional[int]:
        return self._dim

    def _ensure_dim(self, vector: Iterable[float]) -> List[float]:
        values = [float(v) for v in vector]
        if self._dim is None:
            self._dim = len(values)
        elif len(values) != self._dim:
            raise ValueError(f"Expected vectors of length {self._dim}, got {len(values)}")
        return values

    def add(self, item_id: str, vector: Iterable[float]) -> None:
        values = self._ensure_dim(vector)
        self._id_to_index[item_id] = len(self._vectors)
        self._vectors.append(values)
        self._ids.append(item_id)

    def search(self, vector: Iterable[float], k: int = 5) -> List[Result]:
        if self._dim is None:
            return []
        values = self._ensure_dim(vector)
        if not self._vectors:
            return []
        metric = self.metric.lower()
        scores: List[Tuple[str, float]] = []
        if metric == "cosine":
            for stored_id, stored_vector in zip(self._ids, self._vectors):
                score = _cosine(values, stored_vector)
                scores.append((stored_id, score))
        else:  # pragma: no cover - not used in tests
            for stored_id, stored_vector in zip(self._ids, self._vectors):
                diff = [a - b for a, b in zip(values, stored_vector)]
                dist = math.sqrt(sum(component * component for component in diff))
                score = 1.0 / (1.0 + dist)
                scores.append((stored_id, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:k]


__all__ = ["Indexer", "FAISS_AVAILABLE", "HNSW_AVAILABLE"]
