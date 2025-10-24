"""Database models for the duplicate finder."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Generator

from sqlalchemy import DateTime, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    """Declarative base used across the package."""


class MediaItem(Base):
    """Represents a single indexed media asset."""

    __tablename__ = "media_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    size: Mapped[int] = mapped_column(default=0)
    sha1: Mapped[str | None] = mapped_column(String(40), index=True)
    phash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


def get_engine(database_url: str):
    """Return a SQLAlchemy engine, ensuring parent directories exist for SQLite paths."""

    if database_url.startswith("sqlite"):
        if database_url == "sqlite:///:memory:":
            return create_engine(database_url, future=True)
        path = database_url.split("sqlite:///", maxsplit=1)[-1]
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(database_url, future=True)


def get_session(database_url: str) -> Generator[Session, None, None]:
    """Yield a session connected to the provided database URL."""

    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
