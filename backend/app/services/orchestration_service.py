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
        """Return all available orchestration plans.

        Plans are defined at __init__ time and are immutable at runtime.
        They represent the three deployment environments (dev, staging, prod)
        and reference the Terraform vars file and Ansible playbook for each.
        """
        return self._plans

    def list_runs(self) -> List[Dict[str, object]]:
        """Return all recorded runs, sorted newest-first by start time.

        NOTE: Runs are stored in a plain dict keyed by UUID. Sorting is done
        at read time (not at write time) so insertions stay O(1).
        """
        return sorted(
            self._runs.values(), key=lambda run: run["started_at"], reverse=True
        )

    def get_run(self, run_id: str) -> Dict[str, object]:
        """Return a single run record by its UUID.

        Raises:
            HTTPException 404: If the run_id is not in the in-memory store.
                               The `from exc` clause preserves the original
                               KeyError in the traceback for easier debugging.
        """
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
        """Create and record a new orchestration run.

        This method simulates a deployment dry-run: it validates the plan,
        builds an audit record with structured log lines and artifact paths,
        then stores the result in memory. No real infrastructure is changed.

        Args:
            plan_id:      Must match the 'id' field of one of the plans in
                          self._plans. Raises 404 if no match is found.
            requested_by: The email of the authenticated user who triggered
                          the run — used for the audit trail.
            parameters:   Optional dict of run-time metadata (e.g. change_ticket,
                          change_window) forwarded from the frontend console.

        Returns:
            The complete run record dict (matches the OrchestrationRun schema).

        Raises:
            HTTPException 404: If plan_id does not match any known plan.
        """
        plan = next((plan for plan in self._plans if plan["id"] == plan_id), None)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No orchestration plan matches {plan_id}",
            )

        run_id = str(uuid4())
        started_at = datetime.now(timezone.utc)

        # Build simulated log output for the run. All three lines use f-strings
        # for consistency — previously the third line used .format() which was
        # a stylistic inconsistency with no functional difference.
        logs: List[str] = [
            f"[{started_at.isoformat()}] Validated tfvars: {plan['tfvars_file']}",
            "Running terraform fmt && validate",
            f"Queued Ansible deploy with playbook: {plan['playbook_path']}",
            "Streaming OTEL traces to collector",
        ]

        run_record: Dict[str, object] = {
            "id": run_id,
            "plan_id": plan_id,
            "environment": plan["environment"],
            # Always 'succeeded' in the demo — no real infrastructure is changed.
            # A production implementation would update this field asynchronously
            # as the actual Terraform/Ansible run progresses.
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


# Module-level singleton — all FastAPI requests share this one instance so that
# run history persists across requests within a single server process.
# IMPORTANT: This means run history is lost when the server restarts.
# For production use, replace the in-memory dict with a database-backed store.
orchestration_service = OrchestrationService()


def get_orchestration_service() -> OrchestrationService:
    """FastAPI dependency that returns the shared OrchestrationService instance.

    Usage in a router:
        service: OrchestrationService = Depends(get_orchestration_service)

    WHY A FUNCTION INSTEAD OF JUST INJECTING THE MODULE-LEVEL OBJECT:
    FastAPI's Depends() system expects a callable. Wrapping the singleton in
    this function allows FastAPI to call it at request time and also makes it
    easy to override in tests (just override the dependency with a mock).
    """
    return orchestration_service
