"""Simple 3-2-1 backup helpers for ElderPhoto files."""

from __future__ import annotations

import asyncio
import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import aiofiles

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class BackupLocation:
    name: str
    path: str
    remote: bool = False
    host: Optional[str] = None
    user: Optional[str] = None


@dataclass
class BackupConfig:
    locations: List[BackupLocation] = field(default_factory=list)


def default_backup_config() -> BackupConfig:
    local_copy = Path(settings.photo_storage_dir).parent / "backups" / "local"
    cloud_copy = Path(settings.photo_storage_dir).parent / "backups" / "cloud"
    return BackupConfig(
        locations=[
            BackupLocation(name="Local Mirror", path=str(local_copy)),
            BackupLocation(name="Cloud Mirror", path=str(cloud_copy)),
        ]
    )


async def calculate_file_hash(path: Path) -> str:
    md5 = hashlib.md5()
    async with aiofiles.open(path, "rb") as f:
        while chunk := await f.read(1024 * 1024):
            md5.update(chunk)
    return md5.hexdigest()


async def sync_file_via_rsync(source_path: Path, location: BackupLocation, relative_path: Path) -> bool:
    dest = f"{location.path.rstrip('/')}/{relative_path.as_posix()}"
    cmd = [
        "rsync",
        "-az",
        "--relative",
        str(source_path),
        f"{dest}",
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        logger.error("rsync failed for %s -> %s: %s", source_path, dest, stderr.decode())
        return False
    if stdout:
        logger.info(stdout.decode().strip())
    return True


async def copy_file_to_location(source_path: Path, backup_location: BackupLocation, relative_path: Path) -> bool:
    if backup_location.remote:
        rsync_ok = await sync_file_via_rsync(source_path, backup_location, relative_path)
        if not rsync_ok:
            return False
    else:
        destination = Path(backup_location.path) / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(source_path, "rb") as src:
            async with aiofiles.open(destination, "wb") as dst:
                while chunk := await src.read(1024 * 1024):
                    await dst.write(chunk)
        source_hash = await calculate_file_hash(source_path)
        dest_hash = await calculate_file_hash(destination)
        if source_hash != dest_hash:
            logger.error("Hash mismatch for %s at %s", relative_path, backup_location.name)
            return False
    logger.info("Copied %s to %s", relative_path, backup_location.name)
    return True


async def sync_all_photos(config: Optional[BackupConfig] = None) -> None:
    config = config or default_backup_config()
    storage_root = Path(settings.photo_storage_dir)
    if not storage_root.exists():
        logger.info("Storage directory %s does not exist, skipping backup", storage_root)
        return

    file_paths = [p for p in storage_root.rglob('*') if p.is_file()]
    for path in file_paths:
        relative = path.relative_to(storage_root)
        for location in config.locations:
            ok = await copy_file_to_location(path, location, relative)
            if not ok:
                logger.error("Stopping backup because copy failed for %s", path)
                return


__all__ = [
    "BackupConfig",
    "BackupLocation",
    "copy_file_to_location",
    "default_backup_config",
    "sync_all_photos",
]
