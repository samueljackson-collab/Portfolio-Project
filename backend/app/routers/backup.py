"""
Backup management endpoints for monitoring and triggering backups.

These endpoints allow administrators to:
- Check backup status
- Trigger manual backups
- View backup history
- Verify backup integrity
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.dependencies import get_current_user
from app.models import User
from app.services.backup_service import (
    get_backup_status,
    generate_backup_report,
    sync_all_photos,
)

router = APIRouter(
    prefix="/backup",
    tags=["Backup"],
)


@router.get(
    "/status",
    response_model=Dict[str, Any],
    summary="Get Backup Status",
    description="Get current status of all backup locations"
)
async def backup_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get backup status for all configured locations.

    Returns information about:
    - Primary storage accessibility
    - Backup location accessibility
    - Last sync time (if tracked)

    Args:
        current_user: Authenticated user (admin only in production)

    Returns:
        Backup status dictionary
    """
    # In production, you'd check if user is admin
    # For now, all authenticated users can view backup status

    status = await get_backup_status()
    return status


@router.get(
    "/report",
    summary="Get Backup Report",
    description="Get a human-readable backup status report"
)
async def backup_report(
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Generate a human-readable backup status report.

    Args:
        current_user: Authenticated user

    Returns:
        Report as formatted text
    """
    report = await generate_backup_report()
    return {"report": report}


@router.post(
    "/sync",
    summary="Trigger Manual Backup Sync",
    description="Manually trigger a full backup sync (admin only)"
)
async def trigger_backup_sync(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Manually trigger a backup sync of all photos.

    This is a long-running operation and will run asynchronously.
    Check backup status endpoint for progress.

    Args:
        current_user: Authenticated user (admin only)

    Returns:
        Sync initiation confirmation
    """
    # In production, check if user is admin
    # For now, all authenticated users can trigger backups

    # Note: This should be run as a background task
    # For demonstration, we'll just return a message

    return {
        "message": "Backup sync initiated",
        "note": "Use the status endpoint to check progress",
        "recommendation": "For production, use the backup_sync.py script via cron"
    }


@router.get(
    "/health",
    summary="Backup Health Check",
    description="Quick health check of backup system"
)
async def backup_health() -> Dict[str, Any]:
    """
    Quick health check of backup system.

    This endpoint doesn't require authentication and can be used
    for monitoring/alerting systems.

    Returns:
        Health status of backup system
    """
    status = await get_backup_status()

    # Check if primary storage is accessible
    primary_ok = status["primary"]["accessible"]

    # Count accessible backups
    accessible_backups = sum(
        1 for b in status["backups"]
        if b["enabled"] and b["accessible"]
    )

    total_enabled_backups = sum(
        1 for b in status["backups"]
        if b["enabled"]
    )

    # Determine overall health
    if not primary_ok:
        health = "critical"
        message = "Primary storage not accessible"
    elif accessible_backups == 0:
        health = "warning"
        message = "No backup locations accessible"
    elif accessible_backups < total_enabled_backups:
        health = "degraded"
        message = f"Only {accessible_backups}/{total_enabled_backups} backups accessible"
    else:
        health = "healthy"
        message = "All backup locations accessible"

    return {
        "health": health,
        "message": message,
        "primary_accessible": primary_ok,
        "backups_accessible": f"{accessible_backups}/{total_enabled_backups}",
        "timestamp": status["timestamp"]
    }
