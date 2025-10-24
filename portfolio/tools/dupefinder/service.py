from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List

from .audiofp import compute_audio_fingerprint
from .embeddings import generate_embedding
from .indexer import SimpleIndexer
from .models import Embedding, Fingerprint, Media, SessionLocal
from .phash import compute_phash


class DuplicateFinderService:
    """Coordinate fingerprint extraction and similarity checks."""

    def __init__(self) -> None:
        self._indexer = SimpleIndexer()

    def index_path(self, path: Path) -> int:
        path = path.expanduser()
        files = [p for p in path.rglob('*') if p.is_file()]
        session = SessionLocal()
        try:
            for file_path in files:
                media = session.query(Media).filter_by(path=str(file_path)).one_or_none()
                if media is None:
                    media = Media(path=str(file_path))
                    session.add(media)
                    session.flush()
                self._store_fingerprints(session, media, file_path)
            session.commit()
        finally:
            session.close()
        return len(files)

    def _store_fingerprints(self, session, media: Media, file_path: Path) -> None:
        phash_value = compute_phash(file_path)
        if phash_value:
            session.add(Fingerprint(media_id=media.id, kind="phash", value=phash_value))
        audio_value = compute_audio_fingerprint(file_path)
        if audio_value:
            session.add(Fingerprint(media_id=media.id, kind="audio", value=audio_value))
        vector = generate_embedding(file_path)
        if vector:
            session.add(Embedding(media_id=media.id, vector=','.join(map(str, vector))))
            self._indexer.add(media.id, vector)
        else:
            # fallback hashed bytes for stable indexing
            digest = hashlib.sha256(file_path.read_bytes()).digest()
            norm_vector = [b / 255 for b in digest[:16]]
            self._indexer.add(media.id, norm_vector)

    def find_matches(self, threshold: float = 0.85) -> List[Dict[str, Any]]:
        session = SessionLocal()
        try:
            results: list[dict[str, Any]] = []
            for media in session.query(Media).all():
                vector = None
                if media.embeddings:
                    vector = [float(x) for x in media.embeddings[0].vector.split(',') if x]
                if vector is None or not vector:
                    digest = hashlib.sha256(Path(media.path).read_bytes()).digest()
                    vector = [b / 255 for b in digest[:16]]
                matches = self._indexer.search(vector, threshold=threshold)
                matches = [m for m in matches if m != media.id]
                if matches:
                    results.append({
                        "media": media.path,
                        "matches": matches,
                    })
            return results
        finally:
            session.close()
