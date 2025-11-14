"""Async helpers for saving photo files to disk."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiofiles

from app.config import settings


def sanitize_filename(name: str) -> str:
    keep = [c if c.isalnum() or c in {'.', '-', '_'} else '-' for c in name]
    sanitized = ''.join(keep).strip('-') or 'photo'
    return sanitized[:120]


def _build_base_dir(user_id: str, capture_date: Optional[datetime]) -> Path:
    date = (capture_date or datetime.utcnow()).strftime('%Y/%m/%d')
    return Path(settings.photo_storage_dir) / str(user_id) / date


async def save_photo_bytes(user_id: str, capture_date: Optional[datetime], file_name: str, data: bytes) -> str:
    base = _build_base_dir(user_id, capture_date)
    base.mkdir(parents=True, exist_ok=True)
    path = base / sanitize_filename(file_name)
    async with aiofiles.open(path, 'wb') as f:
        await f.write(data)
    return str(path)


async def save_thumbnail_bytes(user_id: str, capture_date: Optional[datetime], file_name: str, data: bytes) -> str:
    base = _build_base_dir(user_id, capture_date) / settings.thumbnail_subdir
    base.mkdir(parents=True, exist_ok=True)
    path = base / (Path(file_name).stem + '_thumb.jpg')
    async with aiofiles.open(path, 'wb') as f:
        await f.write(data)
    return str(path)


async def delete_file(path: Optional[str]) -> None:
    if not path:
        return
    loop = asyncio.get_running_loop()
    file_path = Path(path)
    if file_path.exists():
        await loop.run_in_executor(None, file_path.unlink)
