"""
Backup service for photo replication across multiple locations.

Implements a 3-2-1 backup strategy:
- 3 copies of data (primary + 2 backups)
- 2 different storage types (local SSD + remote HDD)
- 1 offsite copy (geographically separated)

Locations:
- Primary: Home server (fast access)
- Backup 1: Aunt's house (local backup)
- Backup 2: Dad's house in Tucson, AZ (remote backup)
"""

import os
import asyncio
import aiofiles
import hashlib
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class BackupLocation:
    """Represents a backup location with its configuration."""

    def __init__(
        self,
        name: str,
        path: str,
        enabled: bool = True,
        remote: bool = False,
        ssh_host: Optional[str] = None,
        ssh_user: Optional[str] = None,
    ):
        self.name = name
        self.path = path
        self.enabled = enabled
        self.remote = remote
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user

    @property
    def is_accessible(self) -> bool:
        """Check if backup location is currently accessible."""
        if not self.enabled:
            return False

        if self.remote:
            # For remote locations, we'll check via SSH ping
            # This is a placeholder - actual implementation would use paramiko
            return True  # Assume accessible for now
        else:
            # For local locations, check if path exists
            return Path(self.path).exists()

    def get_full_path(self, relative_path: str) -> Path:
        """Get full path for a file in this backup location."""
        return Path(self.path) / relative_path


class BackupConfig:
    """Configuration for backup locations."""

    def __init__(self):
        # Primary storage (home server)
        self.primary = BackupLocation(
            name="Home Server",
            path=os.getenv("PRIMARY_STORAGE_PATH", "/mnt/elderphoto/primary"),
            enabled=True,
            remote=False,
        )

        # Backup 1: Aunt's house (local network)
        self.backup_aunt = BackupLocation(
            name="Aunt's House",
            path=os.getenv("BACKUP_AUNT_PATH", "/mnt/elderphoto/backup-aunt"),
            enabled=os.getenv("BACKUP_AUNT_ENABLED", "true").lower() == "true",
            remote=os.getenv("BACKUP_AUNT_REMOTE", "false").lower() == "true",
            ssh_host=os.getenv("BACKUP_AUNT_SSH_HOST"),
            ssh_user=os.getenv("BACKUP_AUNT_SSH_USER"),
        )

        # Backup 2: Dad's house in Tucson, AZ (remote)
        self.backup_dad = BackupLocation(
            name="Dad's House (Tucson)",
            path=os.getenv("BACKUP_DAD_PATH", "/mnt/elderphoto/backup-dad"),
            enabled=os.getenv("BACKUP_DAD_ENABLED", "true").lower() == "true",
            remote=os.getenv("BACKUP_DAD_REMOTE", "true").lower() == "true",
            ssh_host=os.getenv("BACKUP_DAD_SSH_HOST"),
            ssh_user=os.getenv("BACKUP_DAD_SSH_USER"),
        )

    @property
    def all_backups(self) -> List[BackupLocation]:
        """Get list of all backup locations (excluding primary)."""
        return [self.backup_aunt, self.backup_dad]

    @property
    def enabled_backups(self) -> List[BackupLocation]:
        """Get list of enabled backup locations."""
        return [b for b in self.all_backups if b.enabled]


# Global backup configuration
backup_config = BackupConfig()


async def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA256 hash of a file for verification.

    Args:
        file_path: Path to file

    Returns:
        Hex digest of file hash
    """
    sha256 = hashlib.sha256()
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


async def copy_file_to_backup(
    source_path: Path, backup_location: BackupLocation, relative_path: str
) -> bool:
    """
    Copy a file to a backup location.

    Args:
        source_path: Path to source file
        backup_location: Backup location config
        relative_path: Relative path within storage structure

    Returns:
        True if successful, False otherwise
    """
    try:
        if not backup_location.is_accessible:
            logger.warning(f"Backup location {backup_location.name} is not accessible")
            return False

        dest_path = backup_location.get_full_path(relative_path)

        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if backup_location.remote:
            # For remote locations, use rsync over SSH
            rsync_success = await sync_file_via_rsync(
                source_path,
                backup_location,
                relative_path,
            )
            if not rsync_success:
                return False
        else:
            # For local locations, use async file copy
            async with aiofiles.open(source_path, "rb") as src:
                async with aiofiles.open(dest_path, "wb") as dst:
                    while chunk := await src.read(1024 * 1024):  # 1MB chunks
                        await dst.write(chunk)

        # Verify copy
        if not backup_location.remote:
            source_hash = await calculate_file_hash(source_path)
            dest_hash = await calculate_file_hash(dest_path)

            if source_hash != dest_hash:
                logger.error(
                    f"Hash mismatch for {relative_path} at {backup_location.name}"
                )
                return False

        logger.info(f"Copied {relative_path} to {backup_location.name}")
        return True

    except Exception as e:
        logger.error(f"Failed to copy to {backup_location.name}: {e}")
        return False


async def sync_file_via_rsync(
    source_path: Path, backup_location: BackupLocation, relative_path: str
) -> bool:
    """
    Sync file to remote location using rsync over SSH.

    Args:
        source_path: Path to source file
        backup_location: Remote backup location
        relative_path: Relative path within storage

    Returns:
        True if successful
    """
    try:
        dest_path = backup_location.get_full_path(relative_path)
        remote_dest = f"{backup_location.ssh_user}@{backup_location.ssh_host}:{dest_path}"

        # Create remote directory first
        mkdir_cmd = (
            f"ssh {backup_location.ssh_user}@{backup_location.ssh_host} "
            f"'mkdir -p {dest_path.parent}'"
        )
        proc = await asyncio.create_subprocess_shell(
            mkdir_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        # Rsync file with compression and checksum verification
        rsync_cmd = f"rsync -az --checksum {source_path} {remote_dest}"

        proc = await asyncio.create_subprocess_shell(
            rsync_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.error(f"Rsync failed: {stderr.decode()}")
            return False

        return True

    except Exception as e:
        logger.error(f"Rsync error: {e}")
        return False


async def backup_photo(photo_path: str, thumbnail_path: Optional[str] = None) -> Dict[str, bool]:
    """
    Backup a photo (and its thumbnail) to all configured backup locations.

    Args:
        photo_path: Relative path to photo file
        thumbnail_path: Optional relative path to thumbnail

    Returns:
        Dictionary mapping backup location names to success status
    """
    results = {}

    # Get primary storage path
    primary_photo = backup_config.primary.get_full_path(photo_path)

    if not primary_photo.exists():
        logger.error(f"Primary photo not found: {photo_path}")
        return {}

    # Backup to each location
    for backup_location in backup_config.enabled_backups:
        success = await copy_file_to_backup(primary_photo, backup_location, photo_path)
        results[backup_location.name] = success

        # Also backup thumbnail if provided
        if thumbnail_path and success:
            primary_thumb = backup_config.primary.get_full_path(thumbnail_path)
            if primary_thumb.exists():
                await copy_file_to_backup(
                    primary_thumb, backup_location, thumbnail_path
                )

    return results


async def verify_backups(photo_path: str) -> Dict[str, bool]:
    """
    Verify that a photo exists in all backup locations.

    Args:
        photo_path: Relative path to photo file

    Returns:
        Dictionary mapping backup location names to existence status
    """
    results = {}

    for backup_location in backup_config.enabled_backups:
        if not backup_location.is_accessible:
            results[backup_location.name] = False
            continue

        backup_file = backup_location.get_full_path(photo_path)

        if backup_location.remote:
            # Check remote file existence via SSH
            check_cmd = (
                f"ssh {backup_location.ssh_user}@{backup_location.ssh_host} "
                f"'test -f {backup_file} && echo exists'"
            )
            proc = await asyncio.create_subprocess_shell(
                check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            results[backup_location.name] = b"exists" in stdout
        else:
            results[backup_location.name] = backup_file.exists()

    return results


async def sync_all_photos() -> Dict[str, int]:
    """
    Sync all photos from primary storage to backup locations.

    This is used for initial sync or recovery.

    Returns:
        Dictionary with sync statistics
    """
    stats = {"total": 0, "synced": 0, "failed": 0, "skipped": 0}

    primary_path = Path(backup_config.primary.path)

    if not primary_path.exists():
        logger.error(f"Primary storage path does not exist: {primary_path}")
        return stats

    # Find all photo files
    photo_files = list(primary_path.rglob("*.jpg")) + list(primary_path.rglob("*.jpeg"))
    photo_files += list(primary_path.rglob("*.png")) + list(primary_path.rglob("*.webp"))

    stats["total"] = len(photo_files)

    for photo_file in photo_files:
        # Get relative path
        relative_path = photo_file.relative_to(primary_path)

        # Backup to all locations
        results = await backup_photo(str(relative_path))

        if all(results.values()):
            stats["synced"] += 1
        elif any(results.values()):
            stats["failed"] += 1
        else:
            stats["skipped"] += 1

        # Log progress every 10 files
        if stats["synced"] % 10 == 0:
            logger.info(
                f"Progress: {stats['synced']}/{stats['total']} photos synced"
            )

    return stats


async def get_backup_status() -> Dict:
    """
    Get status of all backup locations.

    Returns:
        Dictionary with backup status information
    """
    status = {
        "timestamp": datetime.now().isoformat(),
        "primary": {
            "name": backup_config.primary.name,
            "path": backup_config.primary.path,
            "accessible": backup_config.primary.is_accessible,
        },
        "backups": [],
    }

    for backup in backup_config.all_backups:
        backup_status = {
            "name": backup.name,
            "path": backup.path,
            "enabled": backup.enabled,
            "remote": backup.remote,
            "accessible": backup.is_accessible,
        }

        if backup.remote:
            backup_status["ssh_host"] = backup.ssh_host

        status["backups"].append(backup_status)

    return status


async def generate_backup_report() -> str:
    """
    Generate a human-readable backup status report.

    Returns:
        Formatted status report
    """
    status = await get_backup_status()

    report = [
        "="* 60,
        "ElderPhoto Backup Status Report",
        "=" * 60,
        f"Generated: {status['timestamp']}",
        "",
        f"Primary Storage: {status['primary']['name']}",
        f"  Path: {status['primary']['path']}",
        f"  Status: {'✓ Accessible' if status['primary']['accessible'] else '✗ Not Accessible'}",
        "",
        "Backup Locations:",
        "-" * 60,
    ]

    for backup in status["backups"]:
        report.append(f"\n{backup['name']}:")
        report.append(f"  Path: {backup['path']}")
        report.append(f"  Enabled: {'Yes' if backup['enabled'] else 'No'}")
        report.append(f"  Type: {'Remote' if backup['remote'] else 'Local'}")

        if backup.get("ssh_host"):
            report.append(f"  SSH Host: {backup['ssh_host']}")

        status_icon = "✓" if backup["accessible"] else "✗"
        status_text = "Accessible" if backup["accessible"] else "Not Accessible"
        report.append(f"  Status: {status_icon} {status_text}")

    report.append("\n" + "=" * 60)

    return "\n".join(report)
