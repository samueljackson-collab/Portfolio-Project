"""Service orchestration for indexing and duplicate detection."""

from __future__ import annotations

import itertools
import math
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from . import audiofp, embeddings, indexer, models, phash

MediaType = str


class DupeFinderService:
    """High level interface coordinating feature extraction and matching."""

    def __init__(self, db_url: str = "sqlite:///:memory:") -> None:
        if "://" not in db_url:
            database_path = Path(db_url)
            database_path.parent.mkdir(parents=True, exist_ok=True)
            self.database_url = f"sqlite:///{database_path}"
        else:
            self.database_url = db_url
        self.engine = models.get_engine(self.database_url)
        models.init_db(self.engine)
        self._index = indexer.Indexer()

    # ------------------------------------------------------------------
    # indexing
    def index_path(self, root: Path) -> int:
        root = Path(root)
        if not root.exists() or not root.is_dir():
            raise NotADirectoryError(root)

        processed = 0
        for file_path in sorted(p for p in root.rglob("*") if p.is_file()):
            processed += self._index_file(file_path)
        return processed

    def _index_file(self, file_path: Path) -> int:
        media_type = self._detect_media_type(file_path)
        size = file_path.stat().st_size

        with models.session_scope(self.engine) as session:
            existing = session.query(models.Media).filter_by(path=str(file_path)).one_or_none()
            if existing is not None:
                return 0

            media = models.Media(path=str(file_path), media_type=media_type, size=size)
            session.add(media)

            # image fingerprint
            try:
                hash_value = phash.compute_phash(file_path)
            except Exception:
                hash_value = None
            if hash_value:
                fingerprint = models.Fingerprint(kind="phash", value=str(hash_value), media=media)
                session.add(fingerprint)

            if media_type == "audio":
                try:
                    audio_hash, confidence = audiofp.compute_audio_fingerprint(file_path)
                except Exception:
                    audio_hash, confidence = None, None
                if audio_hash:
                    fingerprint = models.Fingerprint(
                        kind="audio", value=str(audio_hash), score=confidence, media=media
                    )
                    session.add(fingerprint)

            try:
                embedding_info = embeddings.compute_embedding(file_path)
            except Exception:
                embedding_info = None
            if embedding_info and embedding_info.get("vector"):
                vector = list(embedding_info["vector"])  # type: ignore[index]
                metadata: Dict[str, object] = {}
                if "dim" in embedding_info:
                    metadata["dim"] = embedding_info["dim"]
                if "normalized" in embedding_info:
                    metadata["normalized"] = embedding_info["normalized"]
                extra = embedding_info.get("metadata")
                if isinstance(extra, dict):
                    metadata.update(extra)
                embedding_model = self._create_embedding_model(media, embedding_info, metadata)
                session.add(embedding_model)
                try:
                    self._index.add(str(file_path), vector)
                except ValueError:
                    # Dimension mismatch can happen if optional backends change behaviour;
                    # rebuild the index from scratch to stay safe.
                    self._rebuild_index(session)
        return 1

    @staticmethod
    def _detect_media_type(path: Path) -> MediaType:
        ext = path.suffix.lower()
        if ext in {".jpg", ".jpeg", ".png", ".gif", ".bmp"}:
            return "image"
        if ext in {".mp3", ".wav", ".flac", ".ogg", ".m4a"}:
            return "audio"
        return "generic"

    # ------------------------------------------------------------------
    # matching
    def match(self, threshold: float = 0.85) -> List[Dict[str, object]]:
        with models.session_scope(self.engine) as session:
            media_items = session.query(models.Media).all()
            self._rebuild_index(session)
            results: List[Dict[str, object]] = []
            for media_a, media_b in itertools.combinations(media_items, 2):
                score = self._score_pair(media_a, media_b)
                if score >= threshold:
                    results.append({"a": media_a.path, "b": media_b.path, "score": score})
            results.sort(key=lambda item: item["score"], reverse=True)
            return results

    # ------------------------------------------------------------------
    def _rebuild_index(self, session: object) -> None:
        self._index = indexer.Indexer()
        for media in session.query(models.Media).all():
            vector = self._first_embedding_vector(media)
            if vector:
                try:
                    self._index.add(str(media.path), vector)
                except ValueError:
                    # Skip vectors that do not match the established dimensionality.
                    continue

    def _first_embedding_vector(self, media: models.Media) -> List[float]:
        if not getattr(media, "embeddings", None):
            return []
        embedding = media.embeddings[0]
        if models.SQLALCHEMY_AVAILABLE:
            vector = models.deserialize_vector(embedding.vector)
        else:
            vector = models.deserialize_vector(embedding.vector)
        return vector

    def _score_pair(self, media_a: models.Media, media_b: models.Media) -> float:
        scores: List[float] = []

        phash_a = self._fingerprint_value(media_a, "phash")
        phash_b = self._fingerprint_value(media_b, "phash")
        if phash_a and phash_b:
            scores.append(1.0 if phash_a == phash_b else 0.0)

        audio_a = self._fingerprint_value(media_a, "audio")
        audio_b = self._fingerprint_value(media_b, "audio")
        if audio_a and audio_b:
            scores.append(1.0 if audio_a == audio_b else 0.0)

        vector_a = self._first_embedding_vector(media_a)
        vector_b = self._first_embedding_vector(media_b)
        if vector_a and vector_b:
            scores.append(self._cosine(vector_a, vector_b))

        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    @staticmethod
    def _fingerprint_value(media: models.Media, kind: str) -> Optional[str]:
        for fingerprint in getattr(media, "fingerprints", []) or []:
            if fingerprint.kind == kind:
                return getattr(fingerprint, "value", None)
        return None

    @staticmethod
    def _cosine(a: Iterable[float], b: Iterable[float]) -> float:
        numerator = sum(x * y for x, y in zip(a, b))
        denom_a = math.sqrt(sum(x * x for x in a))
        denom_b = math.sqrt(sum(y * y for y in b))
        if denom_a == 0 or denom_b == 0:
            return 0.0
        return numerator / (denom_a * denom_b)

    def _create_embedding_model(
        self,
        media: models.Media,
        embedding_info: Dict[str, object],
        metadata: Dict[str, object],
    ):
        model_name = str(embedding_info.get("model", "unknown"))
        vector = list(embedding_info.get("vector", []))  # type: ignore[list-item]
        if models.SQLALCHEMY_AVAILABLE:
            return models.Embedding(
                media=media,
                model_name=model_name,
                vector=models.serialize_vector(vector),
                metadata_json=models.serialize_metadata(metadata),
            )
        return models.Embedding(
            model_name=model_name,
            vector=vector,
            metadata=metadata,
            media=media,
        )


__all__ = ["DupeFinderService"]
