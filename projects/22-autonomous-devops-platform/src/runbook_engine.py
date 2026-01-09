#!/usr/bin/env python3
"""
Runbook Execution Engine

Executes automated remediation workflows based on event triggers.
Supports:
- YAML-based runbook definitions
- Conditional execution
- Parallel and sequential steps
- Kubernetes and AWS actions
- Rollback capabilities
"""

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import yaml
import re

logger = logging.getLogger('runbook-engine')


class ActionType(Enum):
    """Types of runbook actions."""
    KUBERNETES = "kubernetes"
    AWS = "aws"
    SHELL = "shell"
    HTTP = "http"
    NOTIFICATION = "notification"
    WAIT = "wait"
    CONDITION = "condition"


class ExecutionStatus(Enum):
    """Execution status states."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    ROLLED_BACK = "rolled_back"


@dataclass
class RunbookStep:
    """A single step in a runbook."""
    name: str
    action_type: ActionType
    action: Dict[str, Any]
    condition: Optional[str] = None
    timeout_seconds: int = 300
    retry_count: int = 0
    retry_delay_seconds: int = 10
    rollback: Optional[Dict[str, Any]] = None
    continue_on_failure: bool = False


@dataclass
class Runbook:
    """A runbook definition."""
    name: str
    description: str
    triggers: List[str]
    steps: List[RunbookStep]
    labels: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    cooldown_seconds: int = 300
    max_concurrent: int = 1


@dataclass
class ExecutionRecord:
    """Record of a runbook execution."""
    id: str
    runbook_name: str
    event_id: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class KubernetesClient:
    """Kubernetes operations client."""

    async def scale_deployment(self, namespace: str, deployment: str,
                               replicas: int) -> Dict[str, Any]:
        """Scale a Kubernetes deployment."""
        cmd = [
            "kubectl", "scale", "deployment", deployment,
            "-n", namespace, f"--replicas={replicas}"
        ]
        result = await self._run_command(cmd)
        return {"scaled": True, "replicas": replicas, **result}

    async def restart_deployment(self, namespace: str,
                                 deployment: str) -> Dict[str, Any]:
        """Restart a Kubernetes deployment."""
        cmd = [
            "kubectl", "rollout", "restart", "deployment", deployment,
            "-n", namespace
        ]
        return await self._run_command(cmd)

    async def delete_pod(self, namespace: str, pod: str) -> Dict[str, Any]:
        """Delete a Kubernetes pod."""
        cmd = ["kubectl", "delete", "pod", pod, "-n", namespace]
        return await self._run_command(cmd)

    async def get_pods(self, namespace: str,
                       selector: Optional[str] = None) -> Dict[str, Any]:
        """Get pods in a namespace."""
        cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
        if selector:
            cmd.extend(["-l", selector])
        result = await self._run_command(cmd)
        if result.get("success") and result.get("stdout"):
            result["pods"] = json.loads(result["stdout"])
        return result

    async def apply_manifest(self, manifest: str) -> Dict[str, Any]:
        """Apply a Kubernetes manifest."""
        cmd = ["kubectl", "apply", "-f", "-"]
        return await self._run_command(cmd, input=manifest)

    async def _run_command(self, cmd: List[str],
                          input: Optional[str] = None) -> Dict[str, Any]:
        """Run a kubectl command."""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE if input else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate(
                input=input.encode() if input else None
            )
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "returncode": process.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class AWSClient:
    """AWS operations client."""

    async def scale_asg(self, asg_name: str, desired: int,
                       min_size: Optional[int] = None,
                       max_size: Optional[int] = None) -> Dict[str, Any]:
        """Scale an Auto Scaling Group."""
        cmd = [
            "aws", "autoscaling", "update-auto-scaling-group",
            "--auto-scaling-group-name", asg_name,
            "--desired-capacity", str(desired)
        ]
        if min_size is not None:
            cmd.extend(["--min-size", str(min_size)])
        if max_size is not None:
            cmd.extend(["--max-size", str(max_size)])

        return await self._run_command(cmd)

    async def restart_ecs_service(self, cluster: str,
                                  service: str) -> Dict[str, Any]:
        """Force a new deployment of an ECS service."""
        cmd = [
            "aws", "ecs", "update-service",
            "--cluster", cluster,
            "--service", service,
            "--force-new-deployment"
        ]
        return await self._run_command(cmd)

    async def invoke_lambda(self, function_name: str,
                           payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a Lambda function."""
        cmd = [
            "aws", "lambda", "invoke",
            "--function-name", function_name,
            "--payload", json.dumps(payload),
            "/dev/stdout"
        ]
        return await self._run_command(cmd)

    async def publish_sns(self, topic_arn: str, message: str,
                         subject: Optional[str] = None) -> Dict[str, Any]:
        """Publish a message to SNS."""
        cmd = [
            "aws", "sns", "publish",
            "--topic-arn", topic_arn,
            "--message", message
        ]
        if subject:
            cmd.extend(["--subject", subject])
        return await self._run_command(cmd)

    async def _run_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Run an AWS CLI command."""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "returncode": process.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class RunbookEngine:
    """
    Executes runbooks based on events.

    Supports:
    - YAML-based runbook definitions
    - Event pattern matching
    - Step execution with retry and rollback
    - Concurrent execution limits
    """

    def __init__(self):
        self.runbooks: Dict[str, Runbook] = {}
        self.executions: Dict[str, ExecutionRecord] = {}
        self.k8s_client = KubernetesClient()
        self.aws_client = AWSClient()
        self.last_execution: Dict[str, datetime] = {}
        self.active_executions: Dict[str, int] = {}
        self._execution_counter = 0

    def load_runbook(self, path: Path) -> Runbook:
        """Load a runbook from a YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)

        steps = []
        for step_data in data.get("steps", []):
            step = RunbookStep(
                name=step_data["name"],
                action_type=ActionType(step_data["type"]),
                action=step_data.get("action", {}),
                condition=step_data.get("condition"),
                timeout_seconds=step_data.get("timeout", 300),
                retry_count=step_data.get("retry", 0),
                retry_delay_seconds=step_data.get("retry_delay", 10),
                rollback=step_data.get("rollback"),
                continue_on_failure=step_data.get("continue_on_failure", False)
            )
            steps.append(step)

        runbook = Runbook(
            name=data["name"],
            description=data.get("description", ""),
            triggers=data.get("triggers", []),
            steps=steps,
            labels=data.get("labels", {}),
            enabled=data.get("enabled", True),
            cooldown_seconds=data.get("cooldown", 300),
            max_concurrent=data.get("max_concurrent", 1)
        )

        self.runbooks[runbook.name] = runbook
        return runbook

    def register_runbook(self, runbook: Runbook):
        """Register a runbook programmatically."""
        self.runbooks[runbook.name] = runbook

    async def execute_for_event(self, event) -> Optional[ExecutionRecord]:
        """
        Find and execute appropriate runbook for an event.

        Args:
            event: The triggering event

        Returns:
            ExecutionRecord if a runbook was executed, None otherwise
        """
        # Find matching runbook
        runbook = self._find_matching_runbook(event)
        if not runbook:
            logger.debug(f"No matching runbook for event: {event.event_type}")
            return None

        # Check cooldown
        if not self._check_cooldown(runbook):
            logger.info(f"Runbook {runbook.name} is in cooldown period")
            return None

        # Check concurrent execution limit
        if not self._check_concurrent_limit(runbook):
            logger.info(f"Runbook {runbook.name} has reached concurrent limit")
            return None

        # Execute the runbook
        return await self.execute(runbook, event)

    def _find_matching_runbook(self, event) -> Optional[Runbook]:
        """Find a runbook that matches the event."""
        for runbook in self.runbooks.values():
            if not runbook.enabled:
                continue

            for trigger in runbook.triggers:
                if self._matches_trigger(trigger, event):
                    return runbook

        return None

    def _matches_trigger(self, trigger: str, event) -> bool:
        """Check if an event matches a trigger pattern."""
        # Simple wildcard matching
        pattern = trigger.replace("*", ".*")
        return bool(re.match(pattern, event.event_type))

    def _check_cooldown(self, runbook: Runbook) -> bool:
        """Check if runbook is past its cooldown period."""
        last = self.last_execution.get(runbook.name)
        if not last:
            return True

        elapsed = (datetime.utcnow() - last).total_seconds()
        return elapsed >= runbook.cooldown_seconds

    def _check_concurrent_limit(self, runbook: Runbook) -> bool:
        """Check if runbook is within concurrent execution limit."""
        current = self.active_executions.get(runbook.name, 0)
        return current < runbook.max_concurrent

    async def execute(self, runbook: Runbook, event) -> ExecutionRecord:
        """
        Execute a runbook.

        Args:
            runbook: The runbook to execute
            event: The triggering event

        Returns:
            ExecutionRecord with execution details
        """
        self._execution_counter += 1
        execution_id = f"exec-{self._execution_counter}-{int(datetime.utcnow().timestamp())}"

        record = ExecutionRecord(
            id=execution_id,
            runbook_name=runbook.name,
            event_id=event.id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        self.executions[execution_id] = record

        # Track active executions
        self.active_executions[runbook.name] = \
            self.active_executions.get(runbook.name, 0) + 1
        self.last_execution[runbook.name] = datetime.utcnow()

        logger.info(f"Starting runbook execution: {runbook.name} [{execution_id}]")

        context = {
            "event": event,
            "execution_id": execution_id,
            "runbook": runbook.name,
            "outputs": {}
        }

        completed_steps = []
        try:
            for step in runbook.steps:
                # Check condition
                if step.condition and not self._evaluate_condition(step.condition, context):
                    logger.info(f"Skipping step {step.name} (condition not met)")
                    continue

                # Execute step with retry
                success = await self._execute_step_with_retry(step, context)

                if success:
                    completed_steps.append(step)
                    record.steps_completed.append(step.name)
                else:
                    record.steps_failed.append(step.name)
                    if not step.continue_on_failure:
                        raise RuntimeError(f"Step {step.name} failed")

            record.status = ExecutionStatus.SUCCESS
            logger.info(f"Runbook execution completed: {execution_id}")

        except Exception as e:
            record.status = ExecutionStatus.FAILED
            record.error = str(e)
            logger.error(f"Runbook execution failed: {execution_id} - {e}")

            # Execute rollbacks
            await self._execute_rollbacks(completed_steps, context)

        finally:
            record.completed_at = datetime.utcnow()
            record.output = context.get("outputs", {})
            self.active_executions[runbook.name] = \
                max(0, self.active_executions.get(runbook.name, 1) - 1)

        return record

    async def _execute_step_with_retry(self, step: RunbookStep,
                                        context: Dict[str, Any]) -> bool:
        """Execute a step with retry logic."""
        attempts = 0
        max_attempts = step.retry_count + 1

        while attempts < max_attempts:
            attempts += 1
            try:
                result = await asyncio.wait_for(
                    self._execute_step(step, context),
                    timeout=step.timeout_seconds
                )
                context["outputs"][step.name] = result
                return True

            except asyncio.TimeoutError:
                logger.warning(f"Step {step.name} timed out (attempt {attempts}/{max_attempts})")

            except Exception as e:
                logger.warning(f"Step {step.name} failed: {e} (attempt {attempts}/{max_attempts})")

            if attempts < max_attempts:
                await asyncio.sleep(step.retry_delay_seconds)

        return False

    async def _execute_step(self, step: RunbookStep,
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step."""
        logger.info(f"Executing step: {step.name}")

        # Interpolate variables in action
        action = self._interpolate_action(step.action, context)

        if step.action_type == ActionType.KUBERNETES:
            return await self._execute_kubernetes_action(action)

        elif step.action_type == ActionType.AWS:
            return await self._execute_aws_action(action)

        elif step.action_type == ActionType.SHELL:
            return await self._execute_shell_action(action)

        elif step.action_type == ActionType.WAIT:
            await asyncio.sleep(action.get("seconds", 10))
            return {"waited": action.get("seconds", 10)}

        elif step.action_type == ActionType.NOTIFICATION:
            return await self._execute_notification_action(action)

        else:
            raise ValueError(f"Unknown action type: {step.action_type}")

    def _interpolate_action(self, action: Dict[str, Any],
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Interpolate variables in action configuration."""
        result = {}
        for key, value in action.items():
            if isinstance(value, str):
                # Replace {{ variable }} patterns
                for match in re.finditer(r'\{\{\s*(\w+(?:\.\w+)*)\s*\}\}', value):
                    var_path = match.group(1).split('.')
                    var_value = context
                    for part in var_path:
                        if isinstance(var_value, dict):
                            var_value = var_value.get(part, "")
                        elif hasattr(var_value, part):
                            var_value = getattr(var_value, part, "")
                        else:
                            var_value = ""
                            break
                    value = value.replace(match.group(0), str(var_value))
                result[key] = value
            elif isinstance(value, dict):
                result[key] = self._interpolate_action(value, context)
            else:
                result[key] = value
        return result

    async def _execute_kubernetes_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Kubernetes action."""
        operation = action.get("operation")

        if operation == "scale":
            return await self.k8s_client.scale_deployment(
                action["namespace"],
                action["deployment"],
                action["replicas"]
            )
        elif operation == "restart":
            return await self.k8s_client.restart_deployment(
                action["namespace"],
                action["deployment"]
            )
        elif operation == "delete_pod":
            return await self.k8s_client.delete_pod(
                action["namespace"],
                action["pod"]
            )
        elif operation == "apply":
            return await self.k8s_client.apply_manifest(action["manifest"])
        else:
            raise ValueError(f"Unknown Kubernetes operation: {operation}")

    async def _execute_aws_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an AWS action."""
        operation = action.get("operation")

        if operation == "scale_asg":
            return await self.aws_client.scale_asg(
                action["asg_name"],
                action["desired"],
                action.get("min_size"),
                action.get("max_size")
            )
        elif operation == "restart_ecs":
            return await self.aws_client.restart_ecs_service(
                action["cluster"],
                action["service"]
            )
        elif operation == "invoke_lambda":
            return await self.aws_client.invoke_lambda(
                action["function_name"],
                action.get("payload", {})
            )
        elif operation == "publish_sns":
            return await self.aws_client.publish_sns(
                action["topic_arn"],
                action["message"],
                action.get("subject")
            )
        else:
            raise ValueError(f"Unknown AWS operation: {operation}")

    async def _execute_shell_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a shell command."""
        command = action.get("command")
        if not command:
            raise ValueError("Shell action requires 'command'")

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        return {
            "success": process.returncode == 0,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": process.returncode
        }

    async def _execute_notification_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a notification action."""
        channel = action.get("channel", "log")
        message = action.get("message", "")

        if channel == "log":
            logger.info(f"NOTIFICATION: {message}")
            return {"sent": True, "channel": "log"}

        elif channel == "sns":
            return await self.aws_client.publish_sns(
                action["topic_arn"],
                message,
                action.get("subject")
            )

        return {"sent": False, "error": f"Unknown channel: {channel}"}

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        # Simple condition evaluation
        try:
            # Replace context variables
            for match in re.finditer(r'\{\{\s*(\w+(?:\.\w+)*)\s*\}\}', condition):
                var_path = match.group(1).split('.')
                var_value = context
                for part in var_path:
                    if isinstance(var_value, dict):
                        var_value = var_value.get(part)
                    elif hasattr(var_value, part):
                        var_value = getattr(var_value, part)
                    else:
                        var_value = None
                        break
                condition = condition.replace(match.group(0), repr(var_value))

            # Evaluate safely
            return eval(condition, {"__builtins__": {}}, {})
        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return False

    async def _execute_rollbacks(self, completed_steps: List[RunbookStep],
                                  context: Dict[str, Any]):
        """Execute rollback actions for completed steps."""
        logger.info("Executing rollbacks...")

        for step in reversed(completed_steps):
            if step.rollback:
                try:
                    rollback_step = RunbookStep(
                        name=f"{step.name}_rollback",
                        action_type=ActionType(step.rollback.get("type", step.action_type.value)),
                        action=step.rollback.get("action", {}),
                        timeout_seconds=step.timeout_seconds
                    )
                    await self._execute_step(rollback_step, context)
                    logger.info(f"Rollback completed for step: {step.name}")
                except Exception as e:
                    logger.error(f"Rollback failed for step {step.name}: {e}")

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Get an execution record by ID."""
        return self.executions.get(execution_id)

    def get_executions(self, runbook_name: Optional[str] = None,
                       limit: int = 100) -> List[ExecutionRecord]:
        """Get execution records."""
        executions = list(self.executions.values())

        if runbook_name:
            executions = [e for e in executions if e.runbook_name == runbook_name]

        return sorted(executions, key=lambda e: e.started_at, reverse=True)[:limit]

    def get_runbooks(self) -> List[Dict[str, Any]]:
        """Get list of registered runbooks."""
        return [
            {
                "name": r.name,
                "description": r.description,
                "triggers": r.triggers,
                "enabled": r.enabled,
                "step_count": len(r.steps)
            }
            for r in self.runbooks.values()
        ]
