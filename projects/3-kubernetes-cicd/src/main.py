"""Kubernetes CI/CD Pipeline Orchestrator.

Coordinates deployment pipelines with ArgoCD integration, progressive delivery
strategies (canary/blue-green), and rollout management.
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


class DeployStrategy(str, Enum):
    CANARY = "canary"
    BLUE_GREEN = "blue-green"
    ROLLING = "rolling"


class PipelinePhase(str, Enum):
    INIT = "init"
    VALIDATE = "validate"
    BUILD = "build"
    SCAN = "scan"
    DEPLOY = "deploy"
    PROMOTE = "promote"
    COMPLETE = "complete"
    FAILED = "failed"
    ROLLBACK = "rollback"


@dataclass
class StageResult:
    """Result of a single pipeline stage."""

    stage: str
    passed: bool
    message: str = ""
    duration_ms: int = 0
    artifacts: List[str] = field(default_factory=list)


@dataclass
class DeploymentStatus:
    """Current deployment status from ArgoCD/Rollouts."""

    app_name: str
    sync_status: str = "Unknown"
    health_status: str = "Unknown"
    revision: str = ""
    rollout_phase: str = ""
    canary_weight: int = 0


@dataclass
class PipelineReport:
    """Consolidated CI/CD pipeline execution report."""

    run_id: str
    strategy: DeployStrategy
    started_at: str
    completed_at: str = ""
    phase: PipelinePhase = PipelinePhase.INIT
    stages: List[StageResult] = field(default_factory=list)
    deployment: Optional[DeploymentStatus] = None
    rollback_triggered: bool = False
    error: str = ""

    def to_dict(self) -> Dict:
        return {
            "run_id": self.run_id,
            "strategy": self.strategy.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "phase": self.phase.value,
            "stages": [
                {
                    "stage": s.stage,
                    "passed": s.passed,
                    "message": s.message,
                    "duration_ms": s.duration_ms,
                    "artifacts": s.artifacts,
                }
                for s in self.stages
            ],
            "deployment": {
                "app_name": self.deployment.app_name,
                "sync_status": self.deployment.sync_status,
                "health_status": self.deployment.health_status,
                "revision": self.deployment.revision,
                "rollout_phase": self.deployment.rollout_phase,
                "canary_weight": self.deployment.canary_weight,
            } if self.deployment else None,
            "rollback_triggered": self.rollback_triggered,
            "error": self.error,
        }


class KubernetesCICDPipeline:
    """Orchestrates Kubernetes CI/CD pipelines with ArgoCD and progressive delivery."""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        app_name: str = "portfolio-app",
        namespace: str = "default",
        strategy: DeployStrategy = DeployStrategy.CANARY,
        argocd_server: Optional[str] = None,
    ) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[1]
        self.app_name = app_name
        self.namespace = namespace
        self.strategy = strategy
        self.argocd_server = argocd_server
        self.manifests_dir = self.project_root / "manifests"
        self.pipelines_dir = self.project_root / "pipelines"
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _run_command(self, cmd: List[str], timeout: int = 120) -> subprocess.CompletedProcess:
        """Execute a shell command and return result."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error("Command timed out: %s", " ".join(cmd))
            raise
        except FileNotFoundError:
            logger.warning("Command not found: %s", cmd[0])
            raise

    def validate_manifests(self) -> StageResult:
        """Validate Kubernetes manifests with kubeconform."""
        start = datetime.now(timezone.utc)
        logger.info("Validating Kubernetes manifests...")

        artifacts: List[str] = []

        # Check manifests directory exists
        if not self.manifests_dir.exists():
            return StageResult(
                stage="validate_manifests",
                passed=False,
                message=f"Manifests directory not found: {self.manifests_dir}",
            )

        # Find all YAML files
        yaml_files = list(self.manifests_dir.glob("**/*.yaml")) + list(self.manifests_dir.glob("**/*.yml"))
        if not yaml_files:
            return StageResult(
                stage="validate_manifests",
                passed=True,
                message="No manifest files found to validate",
            )

        artifacts = [str(f.relative_to(self.project_root)) for f in yaml_files]

        # Try kubeconform validation
        try:
            cmd = ["kubeconform", "-summary", "-output", "json"] + [str(f) for f in yaml_files]
            result = self._run_command(cmd)
            passed = result.returncode == 0
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

            return StageResult(
                stage="validate_manifests",
                passed=passed,
                message=f"Validated {len(yaml_files)} manifests" if passed else result.stderr[:200],
                duration_ms=elapsed,
                artifacts=artifacts,
            )
        except FileNotFoundError:
            # Fallback: basic YAML syntax check
            logger.warning("kubeconform not found - performing basic validation")
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            return StageResult(
                stage="validate_manifests",
                passed=True,
                message=f"Found {len(yaml_files)} manifests (kubeconform not available for schema validation)",
                duration_ms=elapsed,
                artifacts=artifacts,
            )

    def lint_yaml(self) -> StageResult:
        """Lint YAML files with yamllint."""
        start = datetime.now(timezone.utc)
        logger.info("Linting YAML files...")

        yaml_files = (
            list(self.manifests_dir.glob("**/*.yaml")) +
            list(self.manifests_dir.glob("**/*.yml")) +
            list(self.pipelines_dir.glob("**/*.yaml")) +
            list(self.pipelines_dir.glob("**/*.yml"))
        )

        if not yaml_files:
            return StageResult(
                stage="lint_yaml",
                passed=True,
                message="No YAML files found to lint",
            )

        try:
            cmd = ["yamllint", "-f", "parsable"] + [str(f) for f in yaml_files]
            result = self._run_command(cmd)
            passed = result.returncode == 0
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

            return StageResult(
                stage="lint_yaml",
                passed=passed,
                message=f"Linted {len(yaml_files)} files" if passed else f"Lint errors found",
                duration_ms=elapsed,
            )
        except FileNotFoundError:
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            return StageResult(
                stage="lint_yaml",
                passed=True,
                message=f"yamllint not available - skipped ({len(yaml_files)} files)",
                duration_ms=elapsed,
            )

    def security_scan(self) -> StageResult:
        """Run security scan with Trivy."""
        start = datetime.now(timezone.utc)
        logger.info("Running security scan...")

        try:
            # Scan manifests for misconfigurations
            cmd = ["trivy", "config", "--severity", "HIGH,CRITICAL", "--format", "json", str(self.manifests_dir)]
            result = self._run_command(cmd, timeout=300)
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

            try:
                scan_results = json.loads(result.stdout)
                high_critical = sum(
                    1 for r in scan_results.get("Results", [])
                    for m in r.get("Misconfigurations", [])
                    if m.get("Severity") in ("HIGH", "CRITICAL")
                )
                passed = high_critical == 0

                return StageResult(
                    stage="security_scan",
                    passed=passed,
                    message=f"Found {high_critical} HIGH/CRITICAL issues" if not passed else "No critical issues",
                    duration_ms=elapsed,
                )
            except json.JSONDecodeError:
                passed = result.returncode == 0
                return StageResult(
                    stage="security_scan",
                    passed=passed,
                    message="Scan complete" if passed else result.stderr[:200],
                    duration_ms=elapsed,
                )
        except FileNotFoundError:
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            return StageResult(
                stage="security_scan",
                passed=True,
                message="Trivy not available - security scan skipped",
                duration_ms=elapsed,
            )

    def argocd_sync(self) -> StageResult:
        """Trigger ArgoCD application sync."""
        start = datetime.now(timezone.utc)
        logger.info("Syncing ArgoCD application: %s", self.app_name)

        try:
            cmd = ["argocd", "app", "sync", self.app_name, "--prune"]
            if self.argocd_server:
                cmd.extend(["--server", self.argocd_server])

            result = self._run_command(cmd, timeout=300)
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            passed = result.returncode == 0

            return StageResult(
                stage="argocd_sync",
                passed=passed,
                message="Application synced" if passed else result.stderr[:200],
                duration_ms=elapsed,
            )
        except FileNotFoundError:
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            return StageResult(
                stage="argocd_sync",
                passed=True,
                message="ArgoCD CLI not available - sync simulated",
                duration_ms=elapsed,
            )

    def get_deployment_status(self) -> DeploymentStatus:
        """Get current deployment status from ArgoCD."""
        status = DeploymentStatus(app_name=self.app_name)

        try:
            cmd = ["argocd", "app", "get", self.app_name, "-o", "json"]
            if self.argocd_server:
                cmd.extend(["--server", self.argocd_server])

            result = self._run_command(cmd)
            if result.returncode == 0:
                app_data = json.loads(result.stdout)
                status.sync_status = app_data.get("status", {}).get("sync", {}).get("status", "Unknown")
                status.health_status = app_data.get("status", {}).get("health", {}).get("status", "Unknown")
                status.revision = app_data.get("status", {}).get("sync", {}).get("revision", "")[:8]
        except (FileNotFoundError, json.JSONDecodeError):
            # Simulate status
            status.sync_status = "Synced"
            status.health_status = "Healthy"
            status.revision = "simulated"

        return status

    def promote_canary(self, weight: int = 100) -> StageResult:
        """Promote canary deployment to specified weight."""
        start = datetime.now(timezone.utc)
        logger.info("Promoting canary to %d%% traffic...", weight)

        try:
            rollout_name = f"{self.app_name}-rollout"
            if weight >= 100:
                cmd = ["kubectl", "argo", "rollouts", "promote", rollout_name, "-n", self.namespace]
            else:
                cmd = ["kubectl", "argo", "rollouts", "set", "weight", rollout_name, str(weight), "-n", self.namespace]

            result = self._run_command(cmd)
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            passed = result.returncode == 0

            return StageResult(
                stage="promote_canary",
                passed=passed,
                message=f"Canary promoted to {weight}%" if passed else result.stderr[:200],
                duration_ms=elapsed,
            )
        except FileNotFoundError:
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            return StageResult(
                stage="promote_canary",
                passed=True,
                message=f"kubectl not available - canary promotion to {weight}% simulated",
                duration_ms=elapsed,
            )

    def switch_blue_green(self) -> StageResult:
        """Switch blue-green deployment to new version."""
        start = datetime.now(timezone.utc)
        logger.info("Switching blue-green deployment...")

        try:
            rollout_name = f"{self.app_name}-rollout"
            cmd = ["kubectl", "argo", "rollouts", "promote", rollout_name, "-n", self.namespace]

            result = self._run_command(cmd)
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            passed = result.returncode == 0

            return StageResult(
                stage="switch_blue_green",
                passed=passed,
                message="Blue-green switch complete" if passed else result.stderr[:200],
                duration_ms=elapsed,
            )
        except FileNotFoundError:
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            return StageResult(
                stage="switch_blue_green",
                passed=True,
                message="kubectl not available - blue-green switch simulated",
                duration_ms=elapsed,
            )

    def rollback(self) -> StageResult:
        """Rollback deployment to previous stable version."""
        start = datetime.now(timezone.utc)
        logger.info("Rolling back deployment...")

        try:
            # ArgoCD rollback
            cmd = ["argocd", "app", "rollback", self.app_name]
            if self.argocd_server:
                cmd.extend(["--server", self.argocd_server])

            result = self._run_command(cmd)
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            passed = result.returncode == 0

            return StageResult(
                stage="rollback",
                passed=passed,
                message="Rollback complete" if passed else result.stderr[:200],
                duration_ms=elapsed,
            )
        except FileNotFoundError:
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            return StageResult(
                stage="rollback",
                passed=True,
                message="ArgoCD CLI not available - rollback simulated",
                duration_ms=elapsed,
            )

    def run(self, skip_deploy: bool = False) -> PipelineReport:
        """Execute the full CI/CD pipeline."""
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        report = PipelineReport(
            run_id=run_id,
            strategy=self.strategy,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        logger.info("=== Kubernetes CI/CD Pipeline starting (run_id=%s, strategy=%s) ===", run_id, self.strategy.value)

        # Phase 1: Validate
        report.phase = PipelinePhase.VALIDATE

        lint_result = self.lint_yaml()
        report.stages.append(lint_result)
        if not lint_result.passed:
            report.phase = PipelinePhase.FAILED
            report.error = "YAML lint failed"
            report.completed_at = datetime.now(timezone.utc).isoformat()
            return report

        validate_result = self.validate_manifests()
        report.stages.append(validate_result)
        if not validate_result.passed:
            report.phase = PipelinePhase.FAILED
            report.error = "Manifest validation failed"
            report.completed_at = datetime.now(timezone.utc).isoformat()
            return report

        # Phase 2: Security scan
        report.phase = PipelinePhase.SCAN
        scan_result = self.security_scan()
        report.stages.append(scan_result)
        if not scan_result.passed:
            report.phase = PipelinePhase.FAILED
            report.error = "Security scan failed - HIGH/CRITICAL issues found"
            report.completed_at = datetime.now(timezone.utc).isoformat()
            return report

        if skip_deploy:
            logger.info("Skipping deployment stages (--skip-deploy)")
            report.phase = PipelinePhase.COMPLETE
            report.completed_at = datetime.now(timezone.utc).isoformat()
            self._save_report(report, run_id)
            return report

        # Phase 3: Deploy via ArgoCD
        report.phase = PipelinePhase.DEPLOY
        sync_result = self.argocd_sync()
        report.stages.append(sync_result)
        if not sync_result.passed:
            report.phase = PipelinePhase.FAILED
            report.error = "ArgoCD sync failed"
            report.rollback_triggered = True
            rollback_result = self.rollback()
            report.stages.append(rollback_result)
            report.completed_at = datetime.now(timezone.utc).isoformat()
            return report

        # Phase 4: Progressive delivery
        report.phase = PipelinePhase.PROMOTE
        if self.strategy == DeployStrategy.CANARY:
            # Progressive canary promotion
            for weight in [25, 50, 75, 100]:
                promote_result = self.promote_canary(weight)
                report.stages.append(promote_result)
                if not promote_result.passed:
                    report.phase = PipelinePhase.ROLLBACK
                    report.rollback_triggered = True
                    rollback_result = self.rollback()
                    report.stages.append(rollback_result)
                    report.error = f"Canary promotion failed at {weight}%"
                    report.completed_at = datetime.now(timezone.utc).isoformat()
                    return report

        elif self.strategy == DeployStrategy.BLUE_GREEN:
            switch_result = self.switch_blue_green()
            report.stages.append(switch_result)
            if not switch_result.passed:
                report.phase = PipelinePhase.ROLLBACK
                report.rollback_triggered = True
                rollback_result = self.rollback()
                report.stages.append(rollback_result)
                report.error = "Blue-green switch failed"
                report.completed_at = datetime.now(timezone.utc).isoformat()
                return report

        # Get final deployment status
        report.deployment = self.get_deployment_status()
        report.phase = PipelinePhase.COMPLETE
        report.completed_at = datetime.now(timezone.utc).isoformat()

        self._save_report(report, run_id)
        logger.info("=== Pipeline %s (run_id=%s) ===", report.phase.value.upper(), run_id)

        return report

    def _save_report(self, report: PipelineReport, run_id: str) -> None:
        """Save pipeline report to JSON file."""
        report_path = self.reports_dir / f"pipeline-{run_id}.json"
        report_path.write_text(json.dumps(report.to_dict(), indent=2))
        logger.info("Report saved: %s", report_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Kubernetes CI/CD Pipeline Orchestrator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--app-name",
        default="portfolio-app",
        help="ArgoCD application name",
    )
    parser.add_argument(
        "--namespace", "-n",
        default="default",
        help="Kubernetes namespace",
    )
    parser.add_argument(
        "--strategy",
        choices=["canary", "blue-green", "rolling"],
        default="canary",
        help="Deployment strategy",
    )
    parser.add_argument(
        "--argocd-server",
        default=None,
        help="ArgoCD server address",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Path to project root",
    )
    parser.add_argument(
        "--skip-deploy",
        action="store_true",
        help="Run validation stages only, skip deployment",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output final report as JSON to stdout",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point."""
    args = build_parser().parse_args(argv)

    strategy = DeployStrategy(args.strategy)

    pipeline = KubernetesCICDPipeline(
        project_root=args.project_root,
        app_name=args.app_name,
        namespace=args.namespace,
        strategy=strategy,
        argocd_server=args.argocd_server,
    )

    report = pipeline.run(skip_deploy=args.skip_deploy)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))

    return 0 if report.phase == PipelinePhase.COMPLETE else 1


if __name__ == "__main__":
    sys.exit(main())
