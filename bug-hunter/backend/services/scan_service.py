from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import SCAN_TIMEOUT_SECONDS
from models import ScanSession, BugFinding
from analyzers import AndroidAnalyzer, IOSAnalyzer, WindowsAnalyzer, MacOSAnalyzer, WebAnalyzer
from analyzers.base import RawFinding

logger = logging.getLogger("bughunter.scan_service")

PLATFORM_ANALYZERS: dict[str, list] = {
    "android": [AndroidAnalyzer(), WebAnalyzer()],
    "ios": [IOSAnalyzer(), WebAnalyzer()],
    "windows": [WindowsAnalyzer(), WebAnalyzer()],
    "macos": [MacOSAnalyzer(), WebAnalyzer()],
    "web": [WebAnalyzer()],
}

LANGUAGE_MAP: dict[str, str] = {
    ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin",
    ".swift": "Swift", ".m": "Objective-C", ".mm": "Objective-C++",
    ".cs": "C#", ".cpp": "C++", ".cxx": "C++", ".cc": "C++", ".c": "C",
    ".ps1": "PowerShell", ".psm1": "PowerShell",
    ".js": "JavaScript", ".ts": "TypeScript", ".jsx": "JavaScript", ".tsx": "TypeScript",
    ".py": "Python", ".php": "PHP", ".rb": "Ruby",
    ".html": "HTML", ".vue": "Vue",
}

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def detect_language(filename: str, code: str) -> str:
    import os
    ext = os.path.splitext(filename)[1].lower()
    if ext in LANGUAGE_MAP:
        return LANGUAGE_MAP[ext]
    if "import android" in code or "package com.android" in code:
        return "Java"
    if "import SwiftUI" in code or "import UIKit" in code:
        return "Swift"
    if "#include <windows.h>" in code or "using System;" in code:
        return "C#"
    if "<?php" in code:
        return "PHP"
    if "def " in code and "import " in code:
        return "Python"
    return "Unknown"


def compute_risk_score(findings: list[RawFinding]) -> float:
    # Weighted severity sum: Critical=25, High=10, Medium=4, Low=1, capped at 100.
    critical = sum(1 for f in findings if f.severity == "Critical")
    high = sum(1 for f in findings if f.severity == "High")
    medium = sum(1 for f in findings if f.severity == "Medium")
    low = sum(1 for f in findings if f.severity == "Low")
    return min(100.0, critical * 25 + high * 10 + medium * 4 + low * 1)


def deduplicate(findings: list[RawFinding]) -> list[RawFinding]:
    seen: set[tuple] = set()
    result = []
    for f in findings:
        key = (f.title, f.line_number)
        if key not in seen:
            seen.add(key)
            result.append(f)
    return result


async def _run_analyzers(session: ScanSession, db: AsyncSession) -> None:
    """Inner coroutine that performs the actual analysis work."""
    from services.report_service import generate_report

    session.status = "running"
    await db.commit()

    analyzers = PLATFORM_ANALYZERS.get(session.platform, [WebAnalyzer()])
    all_raw: list[RawFinding] = []
    seen: set[tuple] = set()

    for analyzer in analyzers:
        async for raw in analyzer.analyze_streaming(session.code_content, session.filename):
            key = (raw.title, raw.line_number)
            if key in seen:
                continue
            seen.add(key)
            all_raw.append(raw)

            finding = BugFinding(
                id=str(uuid.uuid4()),
                session_id=session.id,
                title=raw.title,
                description=raw.description,
                severity=raw.severity,
                category=raw.category,
                platform=raw.platform,
                line_number=raw.line_number,
                code_snippet=raw.code_snippet,
                recommendation=raw.recommendation,
                cwe_id=raw.cwe_id,
                cvss_score=raw.cvss_score,
                evidence=raw.evidence,
            )
            db.add(finding)

            if raw.severity == "Critical":
                session.critical_count += 1
            elif raw.severity == "High":
                session.high_count += 1
            elif raw.severity == "Medium":
                session.medium_count += 1
            elif raw.severity == "Low":
                session.low_count += 1

    # Compute risk score once and flush all findings + status in a single commit.
    session.risk_score = compute_risk_score(all_raw)
    session.status = "complete"
    session.completed_at = datetime.utcnow()
    await db.commit()

    await generate_report(session.id, db)
    logger.info("Scan %s complete: %d findings, risk=%.1f",
                session.id, len(all_raw), session.risk_score)


async def run_scan(session_id: str, db: AsyncSession) -> None:
    result = await db.execute(select(ScanSession).where(ScanSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        logger.warning("Scan %s not found — skipping analysis", session_id)
        return

    try:
        async with asyncio.timeout(SCAN_TIMEOUT_SECONDS):
            await _run_analyzers(session, db)
    except asyncio.TimeoutError:
        logger.error("Scan %s timed out after %ds", session_id, SCAN_TIMEOUT_SECONDS)
        session.status = "failed"
        await db.commit()
    except Exception as exc:
        logger.error("Scan %s failed: %s", session_id, exc, exc_info=True)
        session.status = "failed"
        await db.commit()
        raise
