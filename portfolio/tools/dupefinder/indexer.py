from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass
class IndexedVector:
    id: int
    vector: Sequence[float]


class SimpleIndexer:
    """Naive cosine similarity index to avoid heavy deps."""

    def __init__(self) -> None:
        self._vectors: list[IndexedVector] = []

    def add(self, item_id: int, vector: Sequence[float]) -> None:
        self._vectors.append(IndexedVector(item_id, list(vector)))

    def search(self, query: Sequence[float], threshold: float = 0.85) -> List[int]:
        results: list[int] = []
        for entry in self._vectors:
            if not entry.vector:
                continue
            score = self._cosine_similarity(query, entry.vector)
            if score >= threshold:
                results.append(entry.id)
        return results

    @staticmethod
    def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


__all__ = ["SimpleIndexer", "IndexedVector"]
