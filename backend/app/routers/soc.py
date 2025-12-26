"""SOC portal endpoints covering alerts, cases, and playbooks."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import CurrentUser, DatabaseSession, raise_not_found
from app.models import SocAlert, SocCase, SocPlaybook
from app.schemas import (
    SocAlertCreate,
    SocAlertResponse,
    SocCaseCreate,
    SocCaseResponse,
    SocCaseUpdate,
    SocPlaybookResponse,
)


router = APIRouter(prefix="/soc", tags=["SOC Portal"])


DEFAULT_PLAYBOOKS = [
    {
        "name": "Credential Theft Containment",
        "description": "Lock accounts, rotate secrets, and enable step-up MFA",
        "steps": ["Disable affected accounts", "Force MFA re-enrollment", "Collect forensic artifacts"],
    },
    {
        "name": "Webshell Eradication",
        "description": "Respond to suspicious web uploads and regain control",
        "steps": [
            "Snapshot the host",
            "Remove malicious artifact",
            "Deploy WAF block rule",
            "Validate integrity",
        ],
    },
]


async def ensure_playbooks(db: AsyncSession) -> None:
    result = await db.execute(select(SocPlaybook))
    if result.scalars().first():
        return
    for data in DEFAULT_PLAYBOOKS:
        db.add(SocPlaybook(**data))
    await db.flush()


@router.get("/playbooks", response_model=list[SocPlaybookResponse])
async def list_playbooks(db: DatabaseSession) -> list[SocPlaybook]:
    await ensure_playbooks(db)
    result = await db.execute(select(SocPlaybook))
    return result.scalars().all()


@router.post("/alerts", response_model=SocAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(payload: SocAlertCreate, db: DatabaseSession, _: CurrentUser) -> SocAlert:
    alert = SocAlert(**payload.model_dump())
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


@router.get("/alerts", response_model=list[SocAlertResponse])
async def list_alerts(
    db: DatabaseSession,
    severity: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
) -> list[SocAlert]:
    stmt = select(SocAlert)
    if severity:
        stmt = stmt.where(SocAlert.severity == severity)
    if status_filter:
        stmt = stmt.where(SocAlert.status == status_filter)
    result = await db.execute(stmt.order_by(SocAlert.created_at.desc()))
    return result.scalars().all()


@router.patch("/alerts/{alert_id}", response_model=SocAlertResponse)
async def update_alert(alert_id: str, payload: SocAlertCreate, db: DatabaseSession, _: CurrentUser) -> SocAlert:
    alert = await db.get(SocAlert, alert_id)
    if not alert:
        raise_not_found("Alert")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(alert, key, value)
    alert.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(alert)
    return alert


@router.post("/cases", response_model=SocCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(payload: SocCaseCreate, db: DatabaseSession, _: CurrentUser) -> SocCase:
    await ensure_playbooks(db)
    case = SocCase(title=payload.title, assigned_to=payload.assigned_to, playbook_id=payload.playbook_id)
    db.add(case)
    await db.flush()
    if payload.alert_ids:
        result = await db.execute(select(SocAlert).where(SocAlert.id.in_(payload.alert_ids)))
        for alert in result.scalars().all():
            alert.case_id = case.id
    await db.refresh(case, attribute_names=["alerts"])
    return case


@router.get("/cases", response_model=list[SocCaseResponse])
async def list_cases(db: DatabaseSession) -> list[SocCase]:
    result = await db.execute(select(SocCase))
    cases = result.scalars().unique().all()
    for case in cases:
        await db.refresh(case, attribute_names=["alerts"])
    return cases


@router.patch("/cases/{case_id}", response_model=SocCaseResponse)
async def update_case(case_id: str, payload: SocCaseUpdate, db: DatabaseSession, _: CurrentUser) -> SocCase:
    case = await db.get(SocCase, case_id)
    if not case:
        raise_not_found("Case")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(case, key, value)
    case.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(case, attribute_names=["alerts"])
    return case


@router.post("/alerts/generate", response_model=list[SocAlertResponse])
async def generate_fake_alerts(db: DatabaseSession, _: CurrentUser) -> list[SocAlert]:
    """Generate deterministic alerts to demonstrate automation hooks."""

    demo_alerts = [
        SocAlert(title="Brute force attempt", description="Multiple SSH failures", severity="high", status="open"),
        SocAlert(title="Malware detection", description="Endpoint flagged suspicious DLL", severity="medium", status="open"),
        SocAlert(title="Impossible travel", description="Login anomalies detected", severity="low", status="triage"),
    ]
    for alert in demo_alerts:
        db.add(alert)
    await db.flush()
    for alert in demo_alerts:
        await db.refresh(alert)
    return demo_alerts
