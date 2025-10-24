"""Database models and fallbacks for the duplicate finder package."""

from __future__ import annotations

import json
import threading
import warnings
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

try:  # pragma: no cover - exercised indirectly
    from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
    from sqlalchemy.orm import declarative_base, relationship, sessionmaker

    SQLALCHEMY_AVAILABLE = True
except Exception:  # pragma: no cover - fallback path
    SQLALCHEMY_AVAILABLE = False


if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()

    class Media(Base):
        __tablename__ = "media"

        id = Column(Integer, primary_key=True)
        path = Column(String, unique=True, nullable=False)
        media_type = Column(String, nullable=False)
        size = Column(Integer, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

        fingerprints = relationship(
            "Fingerprint", back_populates="media", cascade="all, delete-orphan", lazy="joined"
        )
        embeddings = relationship(
            "Embedding", back_populates="media", cascade="all, delete-orphan", lazy="joined"
        )

    class Fingerprint(Base):
        __tablename__ = "fingerprint"

        id = Column(Integer, primary_key=True)
        media_id = Column(Integer, ForeignKey("media.id"), nullable=False, index=True)
        kind = Column(String, nullable=False)
        value = Column(String, nullable=False)
        score = Column(Float, nullable=True)

        media = relationship("Media", back_populates="fingerprints")

    class Embedding(Base):
        __tablename__ = "embedding"

        id = Column(Integer, primary_key=True)
        media_id = Column(Integer, ForeignKey("media.id"), nullable=False, index=True)
        model_name = Column(String, nullable=False)
        vector = Column(Text, nullable=False)
        metadata_json = Column(Text, nullable=True)

        media = relationship("Media", back_populates="embeddings")

    def get_engine(url: str = "sqlite:///:memory:", **kwargs: Any):
        return create_engine(url, future=True, **kwargs)

    def init_db(engine: Any) -> None:
        Base.metadata.create_all(engine)

    def _make_session_factory(engine: Any):
        return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)

    @contextmanager
    def session_scope(engine: Any):
        SessionLocal = _make_session_factory(engine)
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:  # pragma: no cover - defensive
            session.rollback()
            raise
        finally:
            session.close()
else:
    warnings.warn(
        "SQLAlchemy not available - using in-memory database fallback.",
        RuntimeWarning,
        stacklevel=2,
    )

    @dataclass
    class Media:  # type: ignore[override]
        path: str
        media_type: str
        size: Optional[int] = None
        id: Optional[int] = None
        created_at: datetime = field(default_factory=datetime.utcnow)
        fingerprints: List["Fingerprint"] = field(default_factory=list)
        embeddings: List["Embedding"] = field(default_factory=list)

    @dataclass
    class Fingerprint:  # type: ignore[override]
        kind: str
        value: str
        score: Optional[float] = None
        media: Optional[Media] = None
        media_id: Optional[int] = None
        id: Optional[int] = None

    @dataclass
    class Embedding:  # type: ignore[override]
        model_name: str
        vector: List[float]
        metadata: Optional[Dict[str, Any]] = None
        media: Optional[Media] = None
        media_id: Optional[int] = None
        id: Optional[int] = None

    class _InMemoryEngine(dict):
        pass

    _ENGINE_REGISTRY: Dict[str, "_InMemoryEngine"] = {}

    class _InMemoryQuery:
        def __init__(self, items: Iterable[Any]):
            self._items = list(items)

        def filter_by(self, **kwargs: Any) -> "_InMemoryQuery":
            filtered = [
                item
                for item in self._items
                if all(getattr(item, key) == value for key, value in kwargs.items())
            ]
            return _InMemoryQuery(filtered)

        def all(self) -> List[Any]:
            return list(self._items)

        def first(self) -> Optional[Any]:
            return self._items[0] if self._items else None

        def one_or_none(self) -> Optional[Any]:
            if not self._items:
                return None
            if len(self._items) > 1:
                raise ValueError("Multiple results found in in-memory fallback.")
            return self._items[0]

        def __iter__(self):
            return iter(self._items)

    class _InMemorySession:
        def __init__(self, engine: "_InMemoryEngine") -> None:
            self._engine = engine
            storage = engine.setdefault(
                "storage", {"media": [], "fingerprint": [], "embedding": []}
            )
            self._storage = storage
            self._lock = engine.setdefault("lock", threading.Lock())
            engine.setdefault("sequence", {"media": 1, "fingerprint": 1, "embedding": 1})

        def add(self, obj: Any) -> None:
            if isinstance(obj, Media):
                with self._lock:
                    if obj.id is None:
                        obj.id = self._engine["sequence"]["media"]
                        self._engine["sequence"]["media"] += 1
                    existing = next((m for m in self._storage["media"] if m.path == obj.path), None)
                    if existing is None:
                        self._storage["media"].append(obj)
                    else:
                        obj.id = existing.id
            elif isinstance(obj, Fingerprint):
                with self._lock:
                    if obj.id is None:
                        obj.id = self._engine["sequence"]["fingerprint"]
                        self._engine["sequence"]["fingerprint"] += 1
                    if obj.media is None and obj.media_id is not None:
                        obj.media = self.get(Media).filter_by(id=obj.media_id).one_or_none()
                    if obj.media and obj not in obj.media.fingerprints:
                        obj.media.fingerprints.append(obj)
                    self._storage["fingerprint"].append(obj)
            elif isinstance(obj, Embedding):
                with self._lock:
                    if obj.id is None:
                        obj.id = self._engine["sequence"]["embedding"]
                        self._engine["sequence"]["embedding"] += 1
                    if obj.media is None and obj.media_id is not None:
                        obj.media = self.get(Media).filter_by(id=obj.media_id).one_or_none()
                    if obj.media and obj not in obj.media.embeddings:
                        obj.media.embeddings.append(obj)
                    self._storage["embedding"].append(obj)
            else:  # pragma: no cover - defensive branch
                raise TypeError(f"Unsupported object {type(obj)!r} for in-memory session")

        def commit(self) -> None:  # pragma: no cover - nothing to do
            return

        def rollback(self) -> None:  # pragma: no cover - nothing to do
            return

        def close(self) -> None:  # pragma: no cover - nothing to do
            return

        def query(self, model: Any) -> _InMemoryQuery:
            table_name = {
                Media: "media",
                Fingerprint: "fingerprint",
                Embedding: "embedding",
            }.get(model)
            if table_name is None:  # pragma: no cover - defensive
                raise TypeError(f"Unsupported query model {model!r}")
            return _InMemoryQuery(self._storage.get(table_name, []))

        # compatibility helper for Fingerprint/Embedding linking
        def get(self, model: Any) -> _InMemoryQuery:
            return self.query(model)

    def get_engine(url: str = "sqlite:///:memory:", **_: Any) -> _InMemoryEngine:
        if url == "sqlite:///:memory:":
            return _InMemoryEngine(url=url)
        engine = _ENGINE_REGISTRY.get(url)
        if engine is None:
            engine = _InMemoryEngine(url=url)
            _ENGINE_REGISTRY[url] = engine
        return engine

    def init_db(engine: Any) -> None:  # pragma: no cover - nothing to do
        engine.setdefault("storage", {"media": [], "fingerprint": [], "embedding": []})
        engine.setdefault("sequence", {"media": 1, "fingerprint": 1, "embedding": 1})
        engine.setdefault("lock", threading.Lock())

    @contextmanager
    def session_scope(engine: Any):
        session = _InMemorySession(engine)
        try:
            yield session
        finally:
            session.close()


def serialize_vector(vector: Iterable[float]) -> str:
    return json.dumps(list(vector))


def serialize_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[str]:
    if metadata is None:
        return None
    return json.dumps(metadata)


def deserialize_vector(data: Any) -> List[float]:
    if SQLALCHEMY_AVAILABLE and isinstance(data, str):
        return list(json.loads(data))
    if isinstance(data, list):
        return list(data)
    return []


def deserialize_metadata(data: Any) -> Dict[str, Any]:
    if SQLALCHEMY_AVAILABLE and isinstance(data, str):
        return json.loads(data) if data else {}
    if isinstance(data, dict):
        return data
    return {}
