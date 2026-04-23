from __future__ import annotations
import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import ScanSession, BugFinding
from analyzers import AndroidAnalyzer, IOSAnalyzer, WindowsAnalyzer, MacOSAnalyzer, WebAnalyzer
from analyzers.base import RawFinding

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


async def run_scan(session_id: str, db: AsyncSession) -> None:
    from services.report_service import generate_report

    result = await db.execute(select(ScanSession).where(ScanSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        return

    try:
        analyzers = PLATFORM_ANALYZERS.get(session.platform, [WebAnalyzer()])
        all_findings: list[RawFinding] = []

        for analyzer in analyzers:
            found = await asyncio.to_thread(analyzer.analyze, session.code_content, session.filename)
            all_findings.extend(found)

        all_findings = deduplicate(all_findings)
        all_findings.sort(key=lambda f: SEVERITY_ORDER.get(f.severity, 99))

        for raw in all_findings:
            finding = BugFinding(
                id=str(uuid.uuid4()),
                session_id=session_id,
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

        session.critical_count = sum(1 for f in all_findings if f.severity == "Critical")
        session.high_count = sum(1 for f in all_findings if f.severity == "High")
        session.medium_count = sum(1 for f in all_findings if f.severity == "Medium")
        session.low_count = sum(1 for f in all_findings if f.severity == "Low")
        session.risk_score = compute_risk_score(all_findings)
        session.status = "complete"
        session.completed_at = datetime.utcnow()
        await db.commit()

        await generate_report(session_id, db)

    except Exception as exc:
        session.status = "failed"
        await db.commit()
        raise exc
