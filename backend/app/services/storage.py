"""Photo storage service with multi-location backups."""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence
import uuid

from fastapi import UploadFile

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class StoredPhotoPaths:
    """Result of storing a photo.

    Attributes:
        primary: Path to the primary copy stored on the home server.
        backups: Paths to any successfully replicated backup copies.
    """

    primary: Path
    backups: list[Path]


class PhotoStorageService:
    """Store uploaded photos to primary and backup locations.

    The service writes a single authoritative copy to the "home server"
    directory and then replicates the file to any configured backup
    directories. This supports the user's desired topology:

    * Primary: home server storage
    * Secondary: local backup at aunt's house (e.g. NAS or external drive)
    * Remote: off-site backup in Tucson, AZ (e.g. VPN mounted share)
    """

    def __init__(self, primary_path: Path, backup_paths: Sequence[Path]):
        self.primary_path = primary_path
        self.backup_paths = list(backup_paths)

    def _build_relative_path(
        self,
        user_id: uuid.UUID,
        capture_date: datetime | None,
        original_filename: str,
    ) -> Path:
        """Build a deterministic relative path for the photo."""

        date_folder = capture_date.strftime("%Y/%m/%d") if capture_date else "unknown"
        safe_name = original_filename.replace(os.sep, "_")
        return Path(str(user_id)) / date_folder / safe_name

    async def save_upload(
        self,
        upload: UploadFile,
        user_id: uuid.UUID,
        capture_date: datetime | None = None,
    ) -> StoredPhotoPaths:
        """Persist an UploadFile to primary and backup locations."""

        data = await upload.read()
        if not data:
            raise ValueError("Uploaded file contained no data")

        relative_path = self._build_relative_path(
            user_id=user_id,
            capture_date=capture_date,
            original_filename=upload.filename or "photo.jpg",
        )

        primary_full_path = self.primary_path / relative_path
        await self._write_bytes(primary_full_path, data)

        backup_paths: list[Path] = []
        for backup_root in self.backup_paths:
            backup_full_path = backup_root / relative_path
            try:
                await self._write_bytes(backup_full_path, data)
            except OSError:
                logger.exception("Failed to write backup copy to %s", backup_full_path)
            else:
                backup_paths.append(backup_full_path)

        return StoredPhotoPaths(primary=primary_full_path, backups=backup_paths)

    async def _write_bytes(self, destination: Path, data: bytes) -> None:
        """Write bytes to disk using a thread to avoid blocking the event loop."""

        destination.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(destination.write_bytes, data)
        logger.info("Stored photo copy at %s", destination)


def get_photo_storage_service() -> PhotoStorageService:
    """Factory that creates a storage service using application settings."""

    primary = Path(settings.photo_primary_storage_path).expanduser()
    backups = [Path(path).expanduser() for path in settings.photo_backup_paths]
    return PhotoStorageService(primary_path=primary, backup_paths=backups)


__all__ = ["PhotoStorageService", "StoredPhotoPaths", "get_photo_storage_service"]
