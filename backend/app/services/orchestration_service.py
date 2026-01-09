"""Lightweight orchestration service used by the API and console.

This service does not execute infrastructure changes directly. Instead it
coordinates the configuration assets that live in the repository (Terraform
workspaces, Ansible playbooks, and runbooks) and tracks requests for
transparency.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import HTTPException, status


class OrchestrationService:
    """In-memory orchestration service for coordinating deployments."""

    def __init__(self) -> None:
        self._plans: List[Dict[str, str]] = [
            {
                "id": "dev-apply",
                "name": "Dev workspace apply",
                "environment": "dev",
                "description": "Plan/apply dev using Terraform + Ansible rollout",
                "playbook_path": "infrastructure/ansible/playbooks/site.yml",
                "tfvars_file": "infrastructure/terraform/environments/dev.tfvars",
                "runbook": "docs/runbooks/orchestration-runbook.md",
            },
            {
                "id": "staging-bluegreen",
                "name": "Staging blue/green",
                "environment": "staging",
                "description": "Create staging artifacts and flip traffic via ALB",
                "playbook_path": "infrastructure/ansible/playbooks/site.yml",
                "tfvars_file": "infrastructure/terraform/environments/staging.tfvars",
                "runbook": "docs/runbooks/orchestration-runbook.md",
            },
            {
                "id": "prod-controlled",
                "name": "Production controlled change",
                "environment": "prod",
                "description": "Change-managed deployment with observability hooks",
                "playbook_path": "infrastructure/ansible/playbooks/site.yml",
                "tfvars_file": "infrastructure/terraform/environments/prod.tfvars",
                "runbook": "docs/runbooks/orchestration-runbook.md",
            },
        ]
        self._runs: Dict[str, Dict[str, object]] = {}

    def list_plans(self) -> List[Dict[str, str]]:
        return self._plans

    def list_runs(self) -> List[Dict[str, object]]:
        return sorted(
            self._runs.values(), key=lambda run: run["started_at"], reverse=True
        )

    def get_run(self, run_id: str) -> Dict[str, object]:
        try:
            return self._runs[run_id]
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run {run_id} was not found",
            ) from exc

    def start_run(
        self,
        *,
        plan_id: str,
        requested_by: str,
        parameters: Optional[Dict[str, str]] = None,
    ) -> Dict[str, object]:
        plan = next((plan for plan in self._plans if plan["id"] == plan_id), None)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No orchestration plan matches {plan_id}",
            )

        run_id = str(uuid4())
        started_at = datetime.now(timezone.utc)
        logs: List[str] = [
            f"[{started_at.isoformat()}] Validated tfvars: {plan['tfvars_file']}",
            "Running terraform fmt && validate",
            "Queued Ansible deploy with playbook: {playbook_path}".format(
                playbook_path=plan["playbook_path"],
            ),
            "Streaming OTEL traces to collector",
        ]

        run_record: Dict[str, object] = {
            "id": run_id,
            "plan_id": plan_id,
            "environment": plan["environment"],
            "status": "succeeded",
            "requested_by": requested_by,
            "parameters": parameters or {},
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc),
            "logs": logs,
            "artifacts": {
                "tfvars": plan["tfvars_file"],
                "playbook": plan["playbook_path"],
                "runbook": plan["runbook"],
            },
            "summary": (
                "Validated infrastructure definitions and rendered rollout for "
                f"{plan['environment']}"
            ),
        }

        self._runs[run_id] = run_record
        return run_record


def get_orchestration_service() -> OrchestrationService:
    """Provide a shared service instance for FastAPI dependency injection."""
    return orchestration_service


orchestration_service = OrchestrationService()
