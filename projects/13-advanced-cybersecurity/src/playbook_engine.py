"""YAML-based playbook execution engine for SOAR."""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import yaml

LOGGER = logging.getLogger(__name__)


class StepStatus(Enum):
    """Playbook step execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class PlaybookStatus(Enum):
    """Overall playbook execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StepResult:
    """Result of a playbook step execution."""
    step_id: str
    step_name: str
    status: StepStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class PlaybookExecution:
    """Tracks a playbook execution."""
    execution_id: str
    playbook_name: str
    status: PlaybookStatus
    context: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps: List[StepResult] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "playbook_name": self.playbook_name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "steps": [
                {
                    "step_id": s.step_id,
                    "step_name": s.step_name,
                    "status": s.status.value,
                    "duration_ms": s.duration_ms,
                    "error": s.error,
                }
                for s in self.steps
            ],
            "error": self.error,
        }


@dataclass
class PlaybookStep:
    """Represents a single step in a playbook."""
    id: str
    name: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None
    on_failure: str = "abort"  # abort, continue, retry
    retry_count: int = 0
    timeout_seconds: int = 300
    depends_on: List[str] = field(default_factory=list)


@dataclass
class Playbook:
    """Represents a SOAR playbook."""
    name: str
    description: str
    trigger: Dict[str, Any]
    steps: List[PlaybookStep]
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    enabled: bool = True

    @classmethod
    def from_yaml(cls, content: str) -> "Playbook":
        """Parse playbook from YAML content."""
        data = yaml.safe_load(content)

        steps = []
        for step_data in data.get("steps", []):
            steps.append(PlaybookStep(
                id=step_data.get("id", str(uuid.uuid4())[:8]),
                name=step_data["name"],
                action=step_data["action"],
                parameters=step_data.get("parameters", {}),
                condition=step_data.get("condition"),
                on_failure=step_data.get("on_failure", "abort"),
                retry_count=step_data.get("retry_count", 0),
                timeout_seconds=step_data.get("timeout", 300),
                depends_on=step_data.get("depends_on", []),
            ))

        return cls(
            name=data["name"],
            description=data.get("description", ""),
            trigger=data.get("trigger", {}),
            steps=steps,
            version=data.get("version", "1.0"),
            tags=data.get("tags", []),
            enabled=data.get("enabled", True),
        )


class ActionRegistry:
    """Registry of available playbook actions."""

    def __init__(self):
        self._actions: Dict[str, Callable] = {}
        self._register_defaults()

    def register(self, name: str, handler: Callable) -> None:
        """Register an action handler."""
        self._actions[name] = handler

    def get(self, name: str) -> Optional[Callable]:
        """Get an action handler by name."""
        return self._actions.get(name)

    def list_actions(self) -> List[str]:
        """List all registered actions."""
        return list(self._actions.keys())

    def _register_defaults(self) -> None:
        """Register default built-in actions."""

        async def isolate_host(context: Dict, params: Dict) -> Dict:
            """Isolate a host from the network."""
            asset_id = params.get("asset_id") or context.get("asset_id")
            LOGGER.info(f"Isolating host: {asset_id}")
            # In production, this would call firewall/EDR API
            return {"action": "isolate_host", "asset_id": asset_id, "success": True}

        async def block_ip(context: Dict, params: Dict) -> Dict:
            """Block an IP address at the firewall."""
            ip = params.get("ip") or context.get("source_ip")
            duration = params.get("duration_hours", 24)
            LOGGER.info(f"Blocking IP: {ip} for {duration} hours")
            return {"action": "block_ip", "ip": ip, "duration_hours": duration, "success": True}

        async def disable_user(context: Dict, params: Dict) -> Dict:
            """Disable a user account."""
            user = params.get("user") or context.get("user")
            LOGGER.info(f"Disabling user: {user}")
            return {"action": "disable_user", "user": user, "success": True}

        async def create_ticket(context: Dict, params: Dict) -> Dict:
            """Create an incident ticket."""
            title = params.get("title", f"Security Alert: {context.get('alert_id', 'Unknown')}")
            severity = params.get("severity", context.get("severity", "medium"))
            LOGGER.info(f"Creating ticket: {title}")
            ticket_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
            return {"action": "create_ticket", "ticket_id": ticket_id, "title": title, "success": True}

        async def send_notification(context: Dict, params: Dict) -> Dict:
            """Send notification to security team."""
            channel = params.get("channel", "security-alerts")
            message = params.get("message", f"Alert triggered: {context.get('alert_id')}")
            LOGGER.info(f"Sending notification to {channel}")
            return {"action": "send_notification", "channel": channel, "sent": True}

        async def enrich_indicator(context: Dict, params: Dict) -> Dict:
            """Enrich an indicator with threat intelligence."""
            indicator = params.get("indicator") or context.get("source_ip")
            LOGGER.info(f"Enriching indicator: {indicator}")
            return {"action": "enrich_indicator", "indicator": indicator, "enriched": True}

        async def quarantine_file(context: Dict, params: Dict) -> Dict:
            """Quarantine a malicious file."""
            file_hash = params.get("hash") or context.get("file_hash")
            LOGGER.info(f"Quarantining file: {file_hash}")
            return {"action": "quarantine_file", "hash": file_hash, "quarantined": True}

        async def run_scan(context: Dict, params: Dict) -> Dict:
            """Run a security scan on an asset."""
            target = params.get("target") or context.get("asset_id")
            scan_type = params.get("scan_type", "vulnerability")
            LOGGER.info(f"Running {scan_type} scan on: {target}")
            return {"action": "run_scan", "target": target, "scan_type": scan_type, "initiated": True}

        async def collect_forensics(context: Dict, params: Dict) -> Dict:
            """Collect forensic data from an asset."""
            asset_id = params.get("asset_id") or context.get("asset_id")
            LOGGER.info(f"Collecting forensics from: {asset_id}")
            return {"action": "collect_forensics", "asset_id": asset_id, "collection_id": uuid.uuid4().hex[:8]}

        async def reset_credentials(context: Dict, params: Dict) -> Dict:
            """Force credential reset for a user."""
            user = params.get("user") or context.get("user")
            LOGGER.info(f"Forcing credential reset for: {user}")
            return {"action": "reset_credentials", "user": user, "reset_initiated": True}

        # Register all default actions
        self.register("isolate_host", isolate_host)
        self.register("block_ip", block_ip)
        self.register("disable_user", disable_user)
        self.register("create_ticket", create_ticket)
        self.register("send_notification", send_notification)
        self.register("enrich_indicator", enrich_indicator)
        self.register("quarantine_file", quarantine_file)
        self.register("run_scan", run_scan)
        self.register("collect_forensics", collect_forensics)
        self.register("reset_credentials", reset_credentials)


class PlaybookEngine:
    """Executes SOAR playbooks."""

    def __init__(self, action_registry: Optional[ActionRegistry] = None):
        self.registry = action_registry or ActionRegistry()
        self.executions: Dict[str, PlaybookExecution] = {}
        self.playbooks: Dict[str, Playbook] = {}

    def load_playbook(self, path: str) -> Playbook:
        """Load a playbook from a YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            playbook = Playbook.from_yaml(f.read())
            self.playbooks[playbook.name] = playbook
            return playbook

    def load_playbook_from_string(self, content: str) -> Playbook:
        """Load a playbook from YAML string."""
        playbook = Playbook.from_yaml(content)
        self.playbooks[playbook.name] = playbook
        return playbook

    def get_playbook(self, name: str) -> Optional[Playbook]:
        """Get a loaded playbook by name."""
        return self.playbooks.get(name)

    def list_playbooks(self) -> List[str]:
        """List all loaded playbooks."""
        return list(self.playbooks.keys())

    async def execute(
        self,
        playbook: Playbook,
        context: Dict[str, Any],
        dry_run: bool = False,
    ) -> PlaybookExecution:
        """Execute a playbook with given context."""
        execution_id = str(uuid.uuid4())
        execution = PlaybookExecution(
            execution_id=execution_id,
            playbook_name=playbook.name,
            status=PlaybookStatus.RUNNING,
            context=context.copy(),
            started_at=datetime.utcnow(),
        )
        self.executions[execution_id] = execution

        LOGGER.info(f"Starting playbook execution: {playbook.name} (id={execution_id})")

        completed_steps: Dict[str, StepResult] = {}
        failed = False

        for step in playbook.steps:
            # Check dependencies
            if step.depends_on:
                deps_met = all(
                    dep in completed_steps and completed_steps[dep].status == StepStatus.SUCCESS
                    for dep in step.depends_on
                )
                if not deps_met:
                    LOGGER.warning(f"Skipping step {step.name}: dependencies not met")
                    step_result = StepResult(
                        step_id=step.id,
                        step_name=step.name,
                        status=StepStatus.SKIPPED,
                        started_at=datetime.utcnow(),
                        completed_at=datetime.utcnow(),
                    )
                    execution.steps.append(step_result)
                    completed_steps[step.id] = step_result
                    continue

            # Check condition
            if step.condition and not self._evaluate_condition(step.condition, context):
                LOGGER.info(f"Skipping step {step.name}: condition not met")
                step_result = StepResult(
                    step_id=step.id,
                    step_name=step.name,
                    status=StepStatus.SKIPPED,
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                )
                execution.steps.append(step_result)
                completed_steps[step.id] = step_result
                continue

            # Execute step
            step_result = await self._execute_step(step, context, dry_run)
            execution.steps.append(step_result)
            completed_steps[step.id] = step_result

            # Update context with step output
            if step_result.output:
                context[f"step_{step.id}_output"] = step_result.output

            # Handle failure
            if step_result.status == StepStatus.FAILED:
                if step.on_failure == "abort":
                    LOGGER.error(f"Step {step.name} failed, aborting playbook")
                    failed = True
                    break
                elif step.on_failure == "continue":
                    LOGGER.warning(f"Step {step.name} failed, continuing")

        # Set final status
        success_count = sum(1 for s in execution.steps if s.status == StepStatus.SUCCESS)
        total_count = len(execution.steps)

        if failed:
            execution.status = PlaybookStatus.FAILED
        elif success_count == total_count:
            execution.status = PlaybookStatus.SUCCESS
        elif success_count > 0:
            execution.status = PlaybookStatus.PARTIAL
        else:
            execution.status = PlaybookStatus.FAILED

        execution.completed_at = datetime.utcnow()

        LOGGER.info(
            f"Playbook execution completed: {playbook.name} "
            f"(status={execution.status.value}, steps={success_count}/{total_count})"
        )

        return execution

    async def _execute_step(
        self,
        step: PlaybookStep,
        context: Dict[str, Any],
        dry_run: bool,
    ) -> StepResult:
        """Execute a single playbook step."""
        started_at = datetime.utcnow()
        start_time = time.time()

        LOGGER.info(f"Executing step: {step.name} (action={step.action})")

        if dry_run:
            return StepResult(
                step_id=step.id,
                step_name=step.name,
                status=StepStatus.SUCCESS,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                output={"dry_run": True, "action": step.action},
                duration_ms=(time.time() - start_time) * 1000,
            )

        action = self.registry.get(step.action)
        if not action:
            return StepResult(
                step_id=step.id,
                step_name=step.name,
                status=StepStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                error=f"Unknown action: {step.action}",
                duration_ms=(time.time() - start_time) * 1000,
            )

        # Resolve parameter templates
        params = self._resolve_params(step.parameters, context)

        # Execute with retry
        last_error = None
        for attempt in range(step.retry_count + 1):
            try:
                result = await asyncio.wait_for(
                    action(context, params),
                    timeout=step.timeout_seconds,
                )
                return StepResult(
                    step_id=step.id,
                    step_name=step.name,
                    status=StepStatus.SUCCESS,
                    started_at=started_at,
                    completed_at=datetime.utcnow(),
                    output=result,
                    duration_ms=(time.time() - start_time) * 1000,
                )
            except asyncio.TimeoutError:
                last_error = f"Step timed out after {step.timeout_seconds}s"
                LOGGER.warning(f"Step {step.name} timeout (attempt {attempt + 1})")
            except Exception as e:
                last_error = str(e)
                LOGGER.warning(f"Step {step.name} failed (attempt {attempt + 1}): {e}")

            if attempt < step.retry_count:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        return StepResult(
            step_id=step.id,
            step_name=step.name,
            status=StepStatus.TIMEOUT if "timed out" in (last_error or "") else StepStatus.FAILED,
            started_at=started_at,
            completed_at=datetime.utcnow(),
            error=last_error,
            duration_ms=(time.time() - start_time) * 1000,
        )

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        try:
            # Simple condition evaluation (production should use safe eval)
            # Supports: severity == "critical", confidence > 0.8, etc.
            condition = condition.strip()

            for key, value in context.items():
                condition = condition.replace(f"${{{key}}}", repr(value))
                condition = condition.replace(key, repr(value))

            return eval(condition, {"__builtins__": {}}, {})
        except Exception as e:
            LOGGER.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False

    def _resolve_params(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter templates using context."""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                context_key = value[2:-1]
                resolved[key] = context.get(context_key, value)
            else:
                resolved[key] = value
        return resolved

    def get_execution(self, execution_id: str) -> Optional[PlaybookExecution]:
        """Get execution by ID."""
        return self.executions.get(execution_id)

    def list_executions(self, limit: int = 10) -> List[PlaybookExecution]:
        """List recent executions."""
        executions = sorted(
            self.executions.values(),
            key=lambda e: e.started_at,
            reverse=True,
        )
        return executions[:limit]
