from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class BugFindingOut(BaseModel):
    id: str
    session_id: str
    title: str
    description: str
    severity: str
    category: str
    platform: str
    line_number: int | None
    code_snippet: str
    recommendation: str
    cwe_id: str | None
    cvss_score: float | None
    evidence: str

    model_config = {"from_attributes": True}


class ScanSessionOut(BaseModel):
    id: str
    platform: str
    filename: str
    language: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    risk_score: float
    findings: list[BugFindingOut] = []

    model_config = {"from_attributes": True}


class ScanSessionSummary(BaseModel):
    id: str
    platform: str
    filename: str
    language: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    risk_score: float

    model_config = {"from_attributes": True}


class ScanCreateRequest(BaseModel):
    platform: str
    filename: str = Field(..., max_length=255)
    code_content: str
    scan_options: dict | None = None


class ReportOut(BaseModel):
    id: str
    session_id: str
    generated_at: datetime
    executive_summary: str
    total_findings: int
    risk_score: float
    html_content: str

    model_config = {"from_attributes": True}


class ReportSummary(BaseModel):
    id: str
    session_id: str
    generated_at: datetime
    executive_summary: str
    total_findings: int
    risk_score: float

    model_config = {"from_attributes": True}
