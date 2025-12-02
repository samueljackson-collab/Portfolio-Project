"""Endpoints for coordinating Terraform and Ansible executions.

These endpoints let the frontend poll environment readiness and trigger
idempotent deploy simulations that mirror the infrastructure assets
in this repository.
"""
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/orchestration", tags=["Orchestration"])


class DeploymentRequest(BaseModel):
    """Incoming deployment request payload."""

    environment: str = Field(..., description="Target environment (staging|production)")
    artifact_version: str = Field(..., description="Container or playbook revision to roll out")
    dry_run: bool = Field(False, description="When true, only return the computed plan")


class DeploymentPlan(BaseModel):
    """Calculated work items for a deployment."""

    terraform_plan: str
    ansible_playbook: str
    checks: List[str]


class DeploymentStatus(BaseModel):
    """Current state of an environment plus the plan that produced it."""

    environment: str
    status: str
    last_deploy: datetime
    artifact_version: str
    plan: DeploymentPlan
    notes: List[str] = Field(default_factory=list)


def _baseline_plan(env: str) -> DeploymentPlan:
    return DeploymentPlan(
        terraform_plan=f"infrastructure/terraform/environments/{env}",
        ansible_playbook="infrastructure/ansible/playbooks/site.yml",
        checks=[
            "terraform validate",
            "ansible-lint --profile production",
            "pytest backend/tests -m smoke",
        ],
    )


def _seed_status() -> Dict[str, DeploymentStatus]:
    now = datetime.now(timezone.utc)
    return {
        "staging": DeploymentStatus(
            environment="staging",
            status="healthy",
            last_deploy=now,
            artifact_version="staging",
            plan=_baseline_plan("staging"),
            notes=["Using spot capacity and 2 task replicas."],
        ),
        "production": DeploymentStatus(
            environment="production",
            status="draining",
            last_deploy=now,
            artifact_version="latest",
            plan=_baseline_plan("production"),
            notes=["Blue/green cutover waiting on health checks."],
        ),
    }


ENVIRONMENT_STATE: Dict[str, DeploymentStatus] = _seed_status()


@router.get("/environments", response_model=List[DeploymentStatus])
def list_environments() -> List[DeploymentStatus]:
    """Return the tracked environments and their current deployment state."""

    return list(ENVIRONMENT_STATE.values())


@router.post("/deploy", response_model=DeploymentStatus)
def trigger_deploy(request: DeploymentRequest) -> DeploymentStatus:
    """Simulate an idempotent deployment run for the requested environment."""

    environment = request.environment.lower()
    if environment not in ENVIRONMENT_STATE:
        raise HTTPException(status_code=404, detail="Unknown environment")

    previous = ENVIRONMENT_STATE[environment]
    plan = _baseline_plan(environment)

    updated = DeploymentStatus(
        environment=environment,
        status="planned" if request.dry_run else "in-progress",
        last_deploy=datetime.now(timezone.utc),
        artifact_version=request.artifact_version,
        plan=plan,
        notes=[
            f"Dry-run={request.dry_run}",
            f"Applying image version {request.artifact_version}",
            f"Previous state was {previous.status}",
        ],
    )

    ENVIRONMENT_STATE[environment] = updated
    return updated
