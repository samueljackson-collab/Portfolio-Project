import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class ScanSession(Base):
    __tablename__ = "scan_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    platform: Mapped[str] = mapped_column(String(20))
    filename: Mapped[str] = mapped_column(String(255))
    code_content: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(50), default="unknown")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    critical_count: Mapped[int] = mapped_column(Integer, default=0)
    high_count: Mapped[int] = mapped_column(Integer, default=0)
    medium_count: Mapped[int] = mapped_column(Integer, default=0)
    low_count: Mapped[int] = mapped_column(Integer, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)

    findings: Mapped[list["BugFinding"]] = relationship("BugFinding", back_populates="session", cascade="all, delete-orphan")
    report: Mapped["Report | None"] = relationship("Report", back_populates="session", uselist=False, cascade="all, delete-orphan")


class BugFinding(Base):
    __tablename__ = "bug_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("scan_sessions.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(50))
    platform: Mapped[str] = mapped_column(String(20))
    line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    code_snippet: Mapped[str] = mapped_column(Text, default="")
    recommendation: Mapped[str] = mapped_column(Text)
    cwe_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence: Mapped[str] = mapped_column(Text, default="")

    session: Mapped["ScanSession"] = relationship("ScanSession", back_populates="findings")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("scan_sessions.id"), unique=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    executive_summary: Mapped[str] = mapped_column(Text)
    total_findings: Mapped[int] = mapped_column(Integer, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    html_content: Mapped[str] = mapped_column(Text)

    session: Mapped["ScanSession"] = relationship("ScanSession", back_populates="report")
