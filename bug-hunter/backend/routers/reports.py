from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import require_api_key
from database import get_db
from models import Report, ScanSession
from schemas import ReportOut, ReportSummary

logger = logging.getLogger("bughunter.reports")
router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("", response_model=list[ReportSummary],
            dependencies=[Depends(require_api_key)])
async def list_reports(
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report).order_by(Report.generated_at.desc()).limit(limit).offset(offset)
    )
    return result.scalars().all()


@router.get("/{report_id}", response_model=ReportOut,
            dependencies=[Depends(require_api_key)])
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/html", response_class=HTMLResponse,
            dependencies=[Depends(require_api_key)])
async def download_report_html(report_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    session_result = await db.execute(select(ScanSession).where(ScanSession.id == report.session_id))
    session = session_result.scalar_one_or_none()
    filename = session.filename if session else "report"

    return HTMLResponse(
        content=report.html_content,
        headers={"Content-Disposition": f'attachment; filename="bughunt-{filename}.html"'},
    )


@router.get("/{report_id}/pdf", dependencies=[Depends(require_api_key)])
async def download_report_pdf(report_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    session_result = await db.execute(select(ScanSession).where(ScanSession.id == report.session_id))
    session = session_result.scalar_one_or_none()
    filename = session.filename if session else "report"

    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=report.html_content).write_pdf()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="bughunt-{filename}.pdf"'},
        )
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="PDF generation requires WeasyPrint. Install it with: pip install weasyprint",
        )
    except Exception as exc:
        logger.error("PDF generation failed for report %s", report_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="PDF generation failed")
