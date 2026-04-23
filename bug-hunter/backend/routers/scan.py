from __future__ import annotations
import asyncio
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import ScanSession, BugFinding
from schemas import ScanCreateRequest, ScanSessionOut, ScanSessionSummary
from services.scan_service import detect_language, run_scan

router = APIRouter(prefix="/api/scans", tags=["scans"])

VALID_PLATFORMS = {"android", "ios", "windows", "macos", "web"}


@router.post("", response_model=ScanSessionSummary, status_code=201)
async def create_scan(
    body: ScanCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    if body.platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=422, detail=f"Platform must be one of: {', '.join(VALID_PLATFORMS)}")
    if not body.code_content.strip():
        raise HTTPException(status_code=422, detail="code_content must not be empty")

    session_id = str(uuid.uuid4())
    language = detect_language(body.filename, body.code_content)

    session = ScanSession(
        id=session_id,
        platform=body.platform,
        filename=body.filename or "unnamed",
        code_content=body.code_content,
        language=language,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    background_tasks.add_task(_run_scan_task, session_id)

    return session


async def _run_scan_task(session_id: str) -> None:
    from database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await run_scan(session_id, db)


@router.get("", response_model=list[ScanSessionSummary])
async def list_scans(
    platform: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    q = select(ScanSession).order_by(ScanSession.created_at.desc()).limit(limit).offset(offset)
    if platform:
        q = q.where(ScanSession.platform == platform)
    if status:
        q = q.where(ScanSession.status == status)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{scan_id}", response_model=ScanSessionOut)
async def get_scan(scan_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ScanSession).where(ScanSession.id == scan_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Scan not found")

    findings_result = await db.execute(
        select(BugFinding)
        .where(BugFinding.session_id == scan_id)
        .order_by(BugFinding.severity)
    )
    findings = list(findings_result.scalars().all())
    session.findings = findings
    return session
