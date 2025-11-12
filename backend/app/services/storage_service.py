"""
Storage service for managing photo file storage.

Handles saving photos and thumbnails to the local filesystem.
Organizes files by user ID and date to avoid directory bloat.
Integrates with backup service for automatic replication.
"""

import os
import uuid
import aiofiles
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

# Base storage directory (configurable via environment variable)
STORAGE_BASE = os.getenv("PRIMARY_STORAGE_PATH", os.getenv("PHOTO_STORAGE_PATH", "/tmp/elderphoto_storage"))

# Enable/disable automatic backups
AUTO_BACKUP_ENABLED = os.getenv("AUTO_BACKUP_ENABLED", "true").lower() == "true"


def _ensure_directory(directory: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Path object for directory to create
    """
    directory.mkdir(parents=True, exist_ok=True)


def _get_user_storage_path(user_id: str) -> Path:
    """
    Get the base storage path for a user.

    Organizes files by user ID: /storage/users/{user_id}/

    Args:
        user_id: User's UUID as string

    Returns:
        Path object for user's storage directory
    """
    base = Path(STORAGE_BASE)
    user_path = base / "users" / str(user_id)
    _ensure_directory(user_path)
    return user_path


def _get_date_path(capture_date: datetime = None) -> str:
    """
    Get date-based subdirectory path.

    Organizes by year/month: YYYY/MM/

    Args:
        capture_date: Photo capture date (uses current date if None)

    Returns:
        Relative path string like "2024/12"
    """
    date = capture_date or datetime.now()
    return f"{date.year}/{date.month:02d}"


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove any directory separators
    filename = os.path.basename(filename)

    # Replace potentially problematic characters
    unsafe_chars = '<>:"|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "_")

    # Limit length (keep extension)
    name, ext = os.path.splitext(filename)
    if len(name) > 200:
        name = name[:200]

    return f"{name}{ext}"


async def _trigger_backup(photo_path: str, thumbnail_path: str = None) -> None:
    """
    Trigger async backup of photo to configured backup locations.

    This runs in the background without blocking the upload response.

    Args:
        photo_path: Relative path to photo
        thumbnail_path: Optional relative path to thumbnail
    """
    if not AUTO_BACKUP_ENABLED:
        return

    try:
        # Import here to avoid circular dependency
        from app.services.backup_service import backup_photo

        # Run backup in background task
        asyncio.create_task(backup_photo(photo_path, thumbnail_path))
        logger.info(f"Triggered backup for {photo_path}")

    except Exception as e:
        # Don't fail upload if backup fails
        logger.error(f"Backup trigger failed: {e}")


async def save_photo(
    user_id: str,
    filename: str,
    file_data: bytes,
    capture_date: datetime = None,
) -> str:
    """
    Save a photo to storage and return its storage path.

    Args:
        user_id: User ID who owns the photo
        filename: Original filename
        file_data: Raw file bytes
        capture_date: Photo capture date (for organization)

    Returns:
        Relative storage path (e.g., "users/{user_id}/2024/12/abc123.jpg")
    """
    try:
        # Get user's base directory
        user_path = _get_user_storage_path(user_id)

        # Create date-based subdirectory
        date_path = _get_date_path(capture_date)
        full_dir = user_path / date_path
        _ensure_directory(full_dir)

        # Generate unique filename to prevent collisions
        sanitized = _sanitize_filename(filename)
        name, ext = os.path.splitext(sanitized)
        unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

        # Full filesystem path
        file_path = full_dir / unique_name

        # Write file asynchronously
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_data)

        # Return relative path for database storage
        relative_path = f"users/{user_id}/{date_path}/{unique_name}"

        logger.info(f"Saved photo to: {relative_path}")

        # Trigger backup asynchronously (non-blocking)
        await _trigger_backup(relative_path)

        return relative_path

    except Exception as e:
        logger.error(f"Error saving photo: {e}")
        raise


async def save_thumbnail(
    user_id: str,
    original_path: str,
    thumbnail_data: bytes,
) -> str:
    """
    Save a thumbnail image to storage.

    Args:
        user_id: User ID who owns the photo
        original_path: Path to original photo (for naming)
        thumbnail_data: Thumbnail image bytes

    Returns:
        Relative storage path to thumbnail
    """
    try:
        # Parse original path to maintain structure
        path_parts = Path(original_path).parts

        # Build thumbnail path (same structure, different subdirectory)
        user_path = _get_user_storage_path(user_id)
        thumbnail_dir = user_path / "thumbnails"

        # Maintain date structure if present
        if len(path_parts) > 3:  # users/{user_id}/YYYY/MM/file.jpg
            date_structure = "/".join(path_parts[2:-1])  # YYYY/MM
            thumbnail_dir = thumbnail_dir / date_structure

        _ensure_directory(thumbnail_dir)

        # Use same filename as original
        filename = path_parts[-1]
        file_path = thumbnail_dir / filename

        # Write thumbnail
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(thumbnail_data)

        # Return relative path
        relative_parts = ["users", user_id, "thumbnails"]
        if len(path_parts) > 3:
            relative_parts.extend(path_parts[2:-1])
        relative_parts.append(filename)
        relative_path = "/".join(relative_parts)

        logger.info(f"Saved thumbnail to: {relative_path}")

        # Trigger backup with both photo and thumbnail paths
        await _trigger_backup(original_path, relative_path)

        return relative_path

    except Exception as e:
        logger.error(f"Error saving thumbnail: {e}")
        raise


async def delete_photo(file_path: str) -> bool:
    """
    Delete a photo file from storage.

    Args:
        file_path: Relative path to photo file

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        full_path = Path(STORAGE_BASE) / file_path

        if full_path.exists():
            full_path.unlink()
            logger.info(f"Deleted photo: {file_path}")
            return True
        else:
            logger.warning(f"Photo not found for deletion: {file_path}")
            return False

    except Exception as e:
        logger.error(f"Error deleting photo: {e}")
        return False


async def delete_thumbnail(thumbnail_path: str) -> bool:
    """
    Delete a thumbnail file from storage.

    Args:
        thumbnail_path: Relative path to thumbnail file

    Returns:
        True if deleted successfully, False otherwise
    """
    return await delete_photo(thumbnail_path)


async def get_photo_data(file_path: str) -> bytes:
    """
    Read photo data from storage.

    Args:
        file_path: Relative path to photo file

    Returns:
        Photo file bytes
    """
    try:
        full_path = Path(STORAGE_BASE) / file_path

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    except Exception as e:
        logger.error(f"Error reading photo: {e}")
        raise


def get_storage_stats() -> dict:
    """
    Get storage usage statistics.

    Returns:
        Dictionary with storage stats (total_files, total_size, etc.)
    """
    base_path = Path(STORAGE_BASE)

    if not base_path.exists():
        return {"total_files": 0, "total_size": 0}

    total_files = 0
    total_size = 0

    for file in base_path.rglob("*"):
        if file.is_file():
            total_files += 1
            total_size += file.stat().st_size

    return {
        "total_files": total_files,
        "total_size": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
    }
