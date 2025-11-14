"""Backup monitoring endpoints."""

from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import APIRouter, status

from app.services.backup_service import default_backup_config, sync_all_photos

router = APIRouter(prefix="/backup", tags=["Backup"])


@router.post("/sync", status_code=status.HTTP_202_ACCEPTED)
async def trigger_backup(full: Optional[bool] = True) -> dict:
    async def _run_sync() -> None:
        try:
            await sync_all_photos(default_backup_config())
        except Exception as exc:  # pragma: no cover - logged for observability
            # Log via default logger
            import logging

            logging.getLogger(__name__).exception("Backup sync failed: %s", exc)

    asyncio.create_task(_run_sync())
    return {
        "message": "Backup sync initiated",
        "note": "Use the status endpoint to check progress",
        "recommendation": "For production, use the backup_sync.py script via cron",
    }
