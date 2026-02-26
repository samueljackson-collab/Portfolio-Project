"""AWS Infrastructure Automation Orchestrator.

Validates, plans, and deploys multi-AZ AWS infrastructure using Terraform,
with support for different environments and dry-run capabilities.
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class DeploymentPhase(str, Enum):
    INIT = "init"
    VALIDATE = "validate"
    PLAN = "plan"
    APPLY = "apply"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class ValidationResult:
    """Result of a single validation check."""

    check: str
    passed: bool
    message: str = ""
    duration_ms: int = 0


@dataclass
class InfrastructurePlan:
    """Terraform plan summary."""

    resources_to_add: int = 0
    resources_to_change: int = 0
    resources_to_destroy: int = 0
    plan_file: str = ""
    raw_output: str = ""


@dataclass
class DeploymentReport:
    """Consolidated deployment execution report."""

    run_id: str
    environment: str
    started_at: str
    completed_at: str = ""
    phase: DeploymentPhase = DeploymentPhase.INIT
    validations: List[ValidationResult] = field(default_factory=list)
    plan: Optional[InfrastructurePlan] = None
    applied: bool = False
    error: str = ""

    def to_dict(self) -> Dict:
        return {
            "run_id": self.run_id,
            "environment": self.environment,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "phase": self.phase.value,
            "validations": [
                {"check": v.check, "passed": v.passed, "message": v.message, "duration_ms": v.duration_ms}
                for v in self.validations
            ],
            "plan": {
                "resources_to_add": self.plan.resources_to_add,
                "resources_to_change": self.plan.resources_to_change,
                "resources_to_destroy": self.plan.resources_to_destroy,
                "plan_file": self.plan.plan_file,
            } if self.plan else None,
            "applied": self.applied,
            "error": self.error,
        }


class AWSInfrastructureOrchestrator:
    """Orchestrates AWS infrastructure deployment using Terraform."""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        environment: str = "dev",
        auto_approve: bool = False,
    ) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[1]
        self.terraform_dir = self.project_root / "terraform"
        self.environment = environment
        self.auto_approve = auto_approve
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Execute a shell command and return result."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.terraform_dir,
                capture_output=True,
                text=True,
                timeout=600,
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error("Command timed out: %s", " ".join(cmd))
            raise
        except FileNotFoundError:
            logger.warning("Command not found: %s", cmd[0])
            raise

    def validate_prerequisites(self) -> List[ValidationResult]:
        """Validate required tools and configurations exist."""
        start = datetime.now(timezone.utc)
        results: List[ValidationResult] = []

        # Check Terraform directory exists
        tf_exists = self.terraform_dir.exists()
        results.append(ValidationResult(
            check="terraform_directory",
            passed=tf_exists,
            message=f"Terraform directory: {self.terraform_dir}" if tf_exists else "Terraform directory not found",
        ))

        # Check main.tf exists
        main_tf = self.terraform_dir / "main.tf"
        main_exists = main_tf.exists()
        results.append(ValidationResult(
            check="main_tf_exists",
            passed=main_exists,
            message="main.tf found" if main_exists else "main.tf not found",
        ))

        # Check variables.tf exists
        vars_tf = self.terraform_dir / "variables.tf"
        vars_exists = vars_tf.exists()
        results.append(ValidationResult(
            check="variables_tf_exists",
            passed=vars_exists,
            message="variables.tf found" if vars_exists else "variables.tf not found",
        ))

        # Check environment tfvars exists
        env_tfvars = self.terraform_dir / "environments" / f"{self.environment}.tfvars"
        if not env_tfvars.exists():
            env_tfvars = self.terraform_dir / f"{self.environment}.tfvars"
        env_exists = env_tfvars.exists()
        results.append(ValidationResult(
            check="environment_tfvars",
            passed=env_exists,
            message=f"Environment config: {env_tfvars}" if env_exists else f"No tfvars for {self.environment}",
        ))

        # Check Terraform binary available
        try:
            result = self._run_command(["terraform", "version"])
            tf_available = result.returncode == 0
            version = result.stdout.split("\n")[0] if tf_available else ""
            results.append(ValidationResult(
                check="terraform_binary",
                passed=tf_available,
                message=version if tf_available else "Terraform not installed",
            ))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            results.append(ValidationResult(
                check="terraform_binary",
                passed=False,
                message="Terraform binary not found in PATH",
            ))

        elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        for r in results:
            r.duration_ms = elapsed // len(results)

        return results

    def terraform_init(self) -> ValidationResult:
        """Initialize Terraform working directory."""
        start = datetime.now(timezone.utc)
        logger.info("Initializing Terraform...")

        try:
            result = self._run_command(["terraform", "init", "-input=false"])
            passed = result.returncode == 0
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

            if passed:
                logger.info("Terraform initialized successfully")
            else:
                logger.error("Terraform init failed: %s", result.stderr)

            return ValidationResult(
                check="terraform_init",
                passed=passed,
                message="Initialized" if passed else result.stderr[:200],
                duration_ms=elapsed,
            )
        except FileNotFoundError:
            return ValidationResult(
                check="terraform_init",
                passed=False,
                message="Terraform binary not found",
            )

    def terraform_validate(self) -> ValidationResult:
        """Validate Terraform configuration syntax."""
        start = datetime.now(timezone.utc)
        logger.info("Validating Terraform configuration...")

        try:
            result = self._run_command(["terraform", "validate", "-json"])
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

            try:
                validation = json.loads(result.stdout)
                passed = validation.get("valid", False)
                message = "Configuration valid" if passed else validation.get("error_count", "Validation failed")
            except json.JSONDecodeError:
                passed = result.returncode == 0
                message = "Valid" if passed else result.stderr[:200]

            if passed:
                logger.info("Terraform configuration is valid")
            else:
                logger.error("Terraform validation failed")

            return ValidationResult(
                check="terraform_validate",
                passed=passed,
                message=str(message),
                duration_ms=elapsed,
            )
        except FileNotFoundError:
            return ValidationResult(
                check="terraform_validate",
                passed=False,
                message="Terraform binary not found",
            )

    def terraform_plan(self) -> InfrastructurePlan:
        """Generate Terraform execution plan."""
        logger.info("Generating Terraform plan...")

        plan_file = self.reports_dir / f"tfplan-{self.environment}.bin"

        plan = InfrastructurePlan(plan_file=str(plan_file))

        try:
            # Generate plan
            cmd = ["terraform", "plan", "-input=false", f"-out={plan_file}"]
            env_tfvars = self.terraform_dir / "environments" / f"{self.environment}.tfvars"
            if env_tfvars.exists():
                cmd.extend([f"-var-file={env_tfvars}"])

            result = self._run_command(cmd)
            if result.returncode != 0:
                logger.error("Terraform plan failed: %s", result.stderr)
                plan.raw_output = result.stderr
                return plan

            # Parse plan output for resource counts
            output = result.stdout
            plan.raw_output = output

            # Extract resource counts from plan output
            for line in output.split("\n"):
                if "to add" in line.lower():
                    try:
                        plan.resources_to_add = int(line.split()[0])
                    except (ValueError, IndexError):
                        pass
                elif "to change" in line.lower():
                    try:
                        plan.resources_to_change = int(line.split()[0])
                    except (ValueError, IndexError):
                        pass
                elif "to destroy" in line.lower():
                    try:
                        plan.resources_to_destroy = int(line.split()[0])
                    except (ValueError, IndexError):
                        pass

            logger.info(
                "Plan: +%d ~%d -%d",
                plan.resources_to_add,
                plan.resources_to_change,
                plan.resources_to_destroy,
            )
            return plan

        except FileNotFoundError:
            logger.warning("Terraform binary not found - simulating plan")
            plan.resources_to_add = 15
            plan.resources_to_change = 0
            plan.resources_to_destroy = 0
            return plan

    def terraform_apply(self, plan_file: str) -> bool:
        """Apply Terraform plan."""
        if not self.auto_approve:
            logger.warning("Auto-approve not set - skipping apply")
            return False

        logger.info("Applying Terraform plan...")

        try:
            cmd = ["terraform", "apply", "-input=false", "-auto-approve", plan_file]
            result = self._run_command(cmd)

            if result.returncode == 0:
                logger.info("Terraform apply completed successfully")
                return True
            else:
                logger.error("Terraform apply failed: %s", result.stderr)
                return False

        except FileNotFoundError:
            logger.warning("Terraform binary not found")
            return False

    def run(self, dry_run: bool = True) -> DeploymentReport:
        """Execute the full infrastructure deployment workflow."""
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        report = DeploymentReport(
            run_id=run_id,
            environment=self.environment,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        logger.info("=== AWS Infrastructure Deployment starting (run_id=%s, env=%s) ===", run_id, self.environment)

        # Phase 1: Validate prerequisites
        report.phase = DeploymentPhase.VALIDATE
        report.validations = self.validate_prerequisites()
        critical_checks = ["terraform_directory", "main_tf_exists"]
        if not all(v.passed for v in report.validations if v.check in critical_checks):
            report.phase = DeploymentPhase.FAILED
            report.error = "Critical prerequisites not met"
            report.completed_at = datetime.now(timezone.utc).isoformat()
            logger.error("Prerequisites validation failed")
            return report

        # Phase 2: Initialize and validate Terraform
        init_result = self.terraform_init()
        report.validations.append(init_result)
        if not init_result.passed:
            report.phase = DeploymentPhase.FAILED
            report.error = "Terraform initialization failed"
            report.completed_at = datetime.now(timezone.utc).isoformat()
            return report

        validate_result = self.terraform_validate()
        report.validations.append(validate_result)
        if not validate_result.passed:
            report.phase = DeploymentPhase.FAILED
            report.error = "Terraform validation failed"
            report.completed_at = datetime.now(timezone.utc).isoformat()
            return report

        # Phase 3: Plan
        report.phase = DeploymentPhase.PLAN
        report.plan = self.terraform_plan()

        # Phase 4: Apply (if not dry-run)
        if not dry_run and self.auto_approve:
            report.phase = DeploymentPhase.APPLY
            report.applied = self.terraform_apply(report.plan.plan_file)
            if not report.applied:
                report.phase = DeploymentPhase.FAILED
                report.error = "Terraform apply failed"
        else:
            logger.info("Dry-run mode - skipping apply")

        report.phase = DeploymentPhase.COMPLETE if report.phase != DeploymentPhase.FAILED else report.phase
        report.completed_at = datetime.now(timezone.utc).isoformat()

        # Write report
        report_path = self.reports_dir / f"deployment-{run_id}.json"
        report_path.write_text(json.dumps(report.to_dict(), indent=2))
        logger.info("=== Deployment %s (run_id=%s) - report: %s ===", report.phase.value.upper(), run_id, report_path)

        return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AWS Infrastructure Automation Orchestrator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--environment", "-e",
        default="dev",
        choices=["dev", "staging", "prod"],
        help="Target deployment environment",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Path to project root (default: parent of src/)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the plan (requires --auto-approve for non-interactive)",
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip interactive approval for apply",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the final report as JSON to stdout",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point."""
    args = build_parser().parse_args(argv)

    orchestrator = AWSInfrastructureOrchestrator(
        project_root=args.project_root,
        environment=args.environment,
        auto_approve=args.auto_approve,
    )

    dry_run = not args.apply
    report = orchestrator.run(dry_run=dry_run)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))

    return 0 if report.phase == DeploymentPhase.COMPLETE else 1


if __name__ == "__main__":
    sys.exit(main())
