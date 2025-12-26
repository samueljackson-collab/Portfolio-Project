"""Threat hunting program management endpoints."""

from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from app.dependencies import CurrentUser, DatabaseSession, raise_not_found
from app.models import DetectionRule, HuntFinding, HuntHypothesis
from app.schemas import (
    DetectionRuleCreate,
    DetectionRuleResponse,
    FindingCreate,
    FindingResponse,
    HypothesisCreate,
    HypothesisResponse,
)


router = APIRouter(prefix="/threat-hunting", tags=["Threat Hunting"])


@router.post("/hypotheses", response_model=HypothesisResponse, status_code=status.HTTP_201_CREATED)
async def create_hypothesis(payload: HypothesisCreate, db: DatabaseSession, _: CurrentUser) -> HuntHypothesis:
    hypothesis = HuntHypothesis(**payload.model_dump())
    db.add(hypothesis)
    await db.flush()
    await db.refresh(hypothesis)
    return hypothesis


@router.get("/hypotheses", response_model=list[HypothesisResponse])
async def list_hypotheses(db: DatabaseSession) -> list[HuntHypothesis]:
    result = await db.execute(select(HuntHypothesis))
    return result.scalars().all()


@router.put("/hypotheses/{hypothesis_id}", response_model=HypothesisResponse)
async def update_hypothesis(hypothesis_id: str, payload: HypothesisCreate, db: DatabaseSession, _: CurrentUser) -> HuntHypothesis:
    hypothesis = await db.get(HuntHypothesis, uuid.UUID(str(hypothesis_id)))
    if not hypothesis:
        raise_not_found("Hypothesis")
    for key, value in payload.model_dump().items():
        setattr(hypothesis, key, value)
    await db.flush()
    await db.refresh(hypothesis)
    return hypothesis


@router.delete("/hypotheses/{hypothesis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hypothesis(hypothesis_id: str, db: DatabaseSession, _: CurrentUser) -> None:
    hypothesis = await db.get(HuntHypothesis, uuid.UUID(str(hypothesis_id)))
    if not hypothesis:
        raise_not_found("Hypothesis")
    await db.delete(hypothesis)


@router.post("/hypotheses/{hypothesis_id}/findings", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
async def add_finding(hypothesis_id: str, payload: FindingCreate, db: DatabaseSession, _: CurrentUser) -> HuntFinding:
    hypothesis = await db.get(HuntHypothesis, uuid.UUID(str(hypothesis_id)))
    if not hypothesis:
        raise_not_found("Hypothesis")
    finding = HuntFinding(**payload.model_dump(), hypothesis_id=hypothesis.id)
    db.add(finding)
    await db.flush()
    await db.refresh(finding)
    return finding


@router.get("/hypotheses/{hypothesis_id}/findings", response_model=list[FindingResponse])
async def list_findings(hypothesis_id: str, db: DatabaseSession) -> list[HuntFinding]:
    hyp_id = uuid.UUID(str(hypothesis_id))
    result = await db.execute(select(HuntFinding).where(HuntFinding.hypothesis_id == hyp_id))
    return result.scalars().all()


@router.post("/detection-rules", response_model=DetectionRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_detection_rule(payload: DetectionRuleCreate, db: DatabaseSession, _: CurrentUser) -> DetectionRule:
    rule = DetectionRule(**payload.model_dump())
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return rule


@router.get("/detection-rules", response_model=list[DetectionRuleResponse])
async def list_detection_rules(db: DatabaseSession, status_filter: Optional[str] = Query(None, alias="status")) -> list[DetectionRule]:
    stmt = select(DetectionRule)
    if status_filter:
        stmt = stmt.where(DetectionRule.status == status_filter)
    result = await db.execute(stmt.order_by(DetectionRule.created_at.desc()))
    return result.scalars().all()


@router.post("/findings/{finding_id}/promote", response_model=DetectionRuleResponse)
async def promote_finding(finding_id: str, db: DatabaseSession, _: CurrentUser) -> DetectionRule:
    finding = await db.get(HuntFinding, uuid.UUID(str(finding_id)))
    if not finding:
        raise_not_found("Finding")
    rule = DetectionRule(
        name=f"Rule from finding {finding.id}",
        query=f"search logs for: {finding.details}",
        status="Draft",
        source_finding_id=finding.id,
    )
    db.add(rule)
    finding.status = "promoted"
    await db.flush()
    await db.refresh(rule)
    return rule
