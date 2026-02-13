"""High level orchestration for indexing and duplicate detection."""

from __future__ import annotations

import hashlib
import itertools
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import MediaItem, get_session
from .phash import compute_phash


@dataclass
class MatchResult:
    """Represents a potential duplicate group."""

    paths: List[str]
    score: float
    reason: str


class DupeFinderService:
    """Service responsible for indexing and matching media files."""

    def __init__(self, database_url: str = "sqlite:///:memory:") -> None:
        self.database_url = database_url

    @contextmanager
    def _session(self) -> Iterator[Session]:
        generator = get_session(self.database_url)
        session = next(generator)
        try:
            yield session
            session.commit()
        except Exception:  # noqa: BLE001 - ensure rollback on any failure
            session.rollback()
            raise
        finally:
            session.close()

    def index_path(self, root: Path) -> int:
        """Index every file under ``root`` recursively."""

        if not root.exists():
            raise FileNotFoundError(root)
        files = [p for p in root.rglob("*") if p.is_file()]
        if not files:
            return 0
        with self._session() as session:
            count = 0
            for file_path in files:
                record = session.scalar(select(MediaItem).where(MediaItem.path == str(file_path)))
                if record is None:
                    record = MediaItem(path=str(file_path))
                stat = file_path.stat()
                record.size = stat.st_size
                record.sha1 = hashlib.sha1(file_path.read_bytes()).hexdigest()
                record.phash = compute_phash(file_path)
                record.kind = file_path.suffix.lower().lstrip(".") or None
                session.add(record)
                count += 1
            return count

    def match(self, threshold: float = 0.85) -> List[MatchResult]:
        """Return possible duplicates with a configurable similarity threshold."""

        with self._session() as session:
            items = session.scalars(select(MediaItem)).all()
        if not items:
            return []
        results: List[MatchResult] = []
        by_hash: Dict[str, List[MediaItem]] = {}
        for item in items:
            if item.sha1:
                by_hash.setdefault(item.sha1, []).append(item)
        for sha, group in by_hash.items():
            if len(group) > 1:
                results.append(
                    MatchResult(paths=[entry.path for entry in group], score=1.0, reason=f"sha1:{sha}")
                )
        if threshold >= 1.0:
            return results
        # Approximate matches using perceptual hash similarity when available.
        phashed = [item for item in items if item.phash]
        for left, right in itertools.combinations(phashed, 2):
            score = _phash_similarity(left.phash, right.phash)
            if score >= threshold:
                pair = sorted({left.path, right.path})
                if not any(set(pair).issubset(set(result.paths)) and result.score >= score for result in results):
                    results.append(MatchResult(paths=pair, score=score, reason="phash"))
        results.sort(key=lambda item: item.score, reverse=True)
        return results


def _phash_similarity(left: str | None, right: str | None) -> float:
    """Compute a similarity ratio between two hexadecimal hashes."""

    if not left or not right or len(left) != len(right):
        return 0.0
    left_bits = bin(int(left, 16))[2:].zfill(len(left) * 4)
    right_bits = bin(int(right, 16))[2:].zfill(len(right) * 4)
    matches = sum(l == r for l, r in zip(left_bits, right_bits))
    return matches / len(left_bits)
