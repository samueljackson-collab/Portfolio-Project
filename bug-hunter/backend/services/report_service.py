from __future__ import annotations
import uuid
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import ScanSession, BugFinding, Report

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def _build_executive_summary(session: ScanSession, findings: list[BugFinding]) -> str:
    total = len(findings)
    platform = session.platform.upper()
    filename = session.filename

    if total == 0:
        return (
            f"Static analysis of '{filename}' targeting the {platform} platform completed with no issues detected. "
            "The code appears to follow secure coding practices for the identified rule set. "
            "Note that static analysis cannot detect all vulnerabilities; manual code review and dynamic testing are also recommended."
        )

    severity_parts = []
    if session.critical_count:
        severity_parts.append(f"{session.critical_count} Critical")
    if session.high_count:
        severity_parts.append(f"{session.high_count} High")
    if session.medium_count:
        severity_parts.append(f"{session.medium_count} Medium")
    if session.low_count:
        severity_parts.append(f"{session.low_count} Low")

    severity_summary = ", ".join(severity_parts)
    risk_label = (
        "CRITICAL — immediate action required"
        if session.risk_score >= 70
        else "HIGH — remediate before deployment"
        if session.risk_score >= 40
        else "MODERATE — address in next sprint"
        if session.risk_score >= 20
        else "LOW — minor issues to clean up"
    )

    top_findings = [f.title for f in findings[:3] if f.severity in ("Critical", "High")]
    top_str = "; ".join(top_findings) if top_findings else findings[0].title if findings else "various issues"

    categories = list(dict.fromkeys(f.category for f in findings))[:4]
    cat_str = ", ".join(categories)

    return (
        f"Static analysis of '{filename}' targeting the {platform} platform identified {total} vulnerabilities "
        f"({severity_summary}). The overall risk score is {session.risk_score:.0f}/100 — rated {risk_label}. "
        f"The most critical issues include: {top_str}. "
        f"Vulnerability categories detected: {cat_str}. "
        f"Immediate remediation is recommended for all Critical and High severity findings before this code is deployed "
        f"to a production environment or submitted as part of a bug bounty program. "
        f"Detailed remediation guidance is provided for each finding in the sections below."
    )


def _risk_class(score: float) -> str:
    if score >= 70:
        return "risk-critical"
    if score >= 40:
        return "risk-high"
    if score >= 20:
        return "risk-medium"
    return "risk-low"


async def generate_report(session_id: str, db: AsyncSession) -> Report:
    result = await db.execute(
        select(ScanSession).where(ScanSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise ValueError(f"Scan session {session_id} not found")

    findings_result = await db.execute(
        select(BugFinding)
        .where(BugFinding.session_id == session_id)
        .order_by(BugFinding.severity)
    )
    findings = list(findings_result.scalars().all())
    findings.sort(key=lambda f: SEVERITY_ORDER.get(f.severity, 99))

    executive_summary = _build_executive_summary(session, findings)
    generated_at = datetime.utcnow()

    # Determine the report ID before rendering so the template gets the real ID
    # and we avoid a fragile second-pass string replacement.
    existing_result = await db.execute(select(Report).where(Report.session_id == session_id))
    existing_report = existing_result.scalar_one_or_none()
    report_id = existing_report.id if existing_report else str(uuid.uuid4())

    template = jinja_env.get_template("report.html")
    html_content = template.render(
        session=session,
        findings=findings,
        report=type("R", (), {
            "id": report_id,
            "risk_score": session.risk_score,
            "total_findings": len(findings),
            "executive_summary": executive_summary,
        })(),
        generated_at=generated_at.strftime("%Y-%m-%d %H:%M UTC"),
        risk_class=_risk_class(session.risk_score),
    )

    if existing_report:
        existing_report.executive_summary = executive_summary
        existing_report.total_findings = len(findings)
        existing_report.risk_score = session.risk_score
        existing_report.html_content = html_content
        existing_report.generated_at = generated_at
        report = existing_report
    else:
        report = Report(
            id=report_id,
            session_id=session_id,
            generated_at=generated_at,
            executive_summary=executive_summary,
            total_findings=len(findings),
            risk_score=session.risk_score,
            html_content=html_content,
        )
        db.add(report)

    await db.commit()
    await db.refresh(report)
    return report
