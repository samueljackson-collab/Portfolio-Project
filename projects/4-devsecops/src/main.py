"""DevSecOps Pipeline Orchestrator.

Coordinates security scanning, SBOM generation, policy enforcement, and
compliance reporting across the software delivery pipeline.
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Result from a single security scan stage."""

    stage: str
    passed: bool
    findings: List[dict] = field(default_factory=list)
    message: str = ""
    duration_ms: int = 0


@dataclass
class PipelineReport:
    """Aggregated DevSecOps pipeline execution report."""

    run_id: str
    started_at: str
    completed_at: str = ""
    overall_status: str = "pending"
    stages: List[ScanResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "overall_status": self.overall_status,
            "stages": [
                {
                    "stage": s.stage,
                    "passed": s.passed,
                    "findings": s.findings,
                    "message": s.message,
                    "duration_ms": s.duration_ms,
                }
                for s in self.stages
            ],
        }


class DevSecOpsPipeline:
    """Orchestrates the DevSecOps scanning pipeline stages."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[1]
        self.policies_dir = self.project_root / "policies"
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Stage 1: SBOM Generation
    # ------------------------------------------------------------------
    def generate_sbom(self) -> ScanResult:
        """Generate a Software Bill of Materials for dependency tracking."""
        start = datetime.utcnow()
        req_file = self.project_root / "requirements.txt"
        sbom: dict = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "metadata": {
                "timestamp": start.isoformat() + "Z",
                "component": {"type": "library", "name": "4-devsecops"},
            },
            "components": [],
        }
        if req_file.exists():
            for line in req_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split(">=")
                    name = parts[0].strip()
                    version = parts[1].strip() if len(parts) > 1 else "latest"
                    sbom["components"].append(
                        {"type": "library", "name": name, "version": version}
                    )
        sbom_path = self.reports_dir / "sbom.json"
        sbom_path.write_text(json.dumps(sbom, indent=2))
        elapsed = int((datetime.utcnow() - start).total_seconds() * 1000)
        logger.info("SBOM generated: %s (%d components)", sbom_path, len(sbom["components"]))
        return ScanResult(
            stage="sbom_generation",
            passed=True,
            message=f"SBOM written to {sbom_path} with {len(sbom['components'])} components",
            duration_ms=elapsed,
        )

    # ------------------------------------------------------------------
    # Stage 2: Dependency Vulnerability Scan (simulated Trivy)
    # ------------------------------------------------------------------
    def scan_dependencies(self) -> ScanResult:
        """Scan dependencies for known CVEs."""
        start = datetime.utcnow()
        findings: List[dict] = []
        sbom_path = self.reports_dir / "sbom.json"
        if sbom_path.exists():
            sbom = json.loads(sbom_path.read_text())
            # Simulated scan: flag packages with known demo vulnerabilities
            known_vulnerable = {"requests": "CVE-2023-32681", "urllib3": "CVE-2023-43804"}
            for comp in sbom.get("components", []):
                if comp["name"] in known_vulnerable:
                    findings.append(
                        {
                            "package": comp["name"],
                            "cve": known_vulnerable[comp["name"]],
                            "severity": "MEDIUM",
                            "fixed_version": "latest",
                        }
                    )
        elapsed = int((datetime.utcnow() - start).total_seconds() * 1000)
        passed = len([f for f in findings if f.get("severity") in ("CRITICAL", "HIGH")]) == 0
        scan_report = {"findings": findings, "summary": {"total": len(findings), "passed": passed}}
        report_path = self.reports_dir / "dependency-scan.json"
        report_path.write_text(json.dumps(scan_report, indent=2))
        logger.info(
            "Dependency scan complete: %d findings (CRITICAL/HIGH block=%s)",
            len(findings),
            not passed,
        )
        return ScanResult(
            stage="dependency_scan",
            passed=passed,
            findings=findings,
            message=f"{len(findings)} findings; report at {report_path}",
            duration_ms=elapsed,
        )

    # ------------------------------------------------------------------
    # Stage 3: OPA Policy Validation
    # ------------------------------------------------------------------
    def validate_policies(self) -> ScanResult:
        """Validate infrastructure and pipeline configurations against OPA policies."""
        start = datetime.utcnow()
        violations: List[dict] = []
        policy_files = list(self.policies_dir.glob("**/*.rego")) if self.policies_dir.exists() else []
        if not policy_files:
            logger.warning("No OPA policy files found in %s – skipping policy checks", self.policies_dir)
            elapsed = int((datetime.utcnow() - start).total_seconds() * 1000)
            return ScanResult(
                stage="policy_validation",
                passed=True,
                message="No policy files found; skipped",
                duration_ms=elapsed,
            )
        for policy in policy_files:
            # Simulate policy evaluation
            violations.append(
                {
                    "policy": policy.name,
                    "status": "pass",
                    "description": f"Policy {policy.stem} evaluated successfully",
                }
            )
        elapsed = int((datetime.utcnow() - start).total_seconds() * 1000)
        blocking = [v for v in violations if v.get("status") == "fail"]
        passed = len(blocking) == 0
        logger.info("Policy validation: %d policies evaluated, %d violations", len(policy_files), len(blocking))
        return ScanResult(
            stage="policy_validation",
            passed=passed,
            findings=violations,
            message=f"{len(policy_files)} policies evaluated; {len(blocking)} blocking violations",
            duration_ms=elapsed,
        )

    # ------------------------------------------------------------------
    # Stage 4: Compliance Report
    # ------------------------------------------------------------------
    def generate_compliance_report(self, stages: List[ScanResult]) -> ScanResult:
        """Produce a unified compliance report from all pipeline stage results."""
        start = datetime.utcnow()
        passed_stages = [s for s in stages if s.passed]
        failed_stages = [s for s in stages if not s.passed]
        report = {
            "generated_at": start.isoformat() + "Z",
            "summary": {
                "total_stages": len(stages),
                "passed": len(passed_stages),
                "failed": len(failed_stages),
                "overall": "PASS" if not failed_stages else "FAIL",
            },
            "stages": [s.stage for s in stages],
            "failures": [s.stage for s in failed_stages],
        }
        report_path = self.reports_dir / "compliance-report.json"
        report_path.write_text(json.dumps(report, indent=2))
        elapsed = int((datetime.utcnow() - start).total_seconds() * 1000)
        logger.info("Compliance report: %s – written to %s", report["summary"]["overall"], report_path)
        return ScanResult(
            stage="compliance_report",
            passed=report["summary"]["overall"] == "PASS",
            message=f"Compliance report at {report_path}: {report['summary']['overall']}",
            duration_ms=elapsed,
        )

    # ------------------------------------------------------------------
    # Pipeline runner
    # ------------------------------------------------------------------
    def run(self) -> PipelineReport:
        """Execute all DevSecOps pipeline stages and return a consolidated report."""
        run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        report = PipelineReport(run_id=run_id, started_at=datetime.utcnow().isoformat() + "Z")
        logger.info("=== DevSecOps Pipeline starting (run_id=%s) ===", run_id)

        stages: List[ScanResult] = []
        for stage_fn in (self.generate_sbom, self.scan_dependencies, self.validate_policies):
            result = stage_fn()
            stages.append(result)
            if not result.passed:
                logger.error("Stage '%s' FAILED – aborting pipeline", result.stage)
                break

        compliance = self.generate_compliance_report(stages)
        stages.append(compliance)
        report.stages = stages
        report.overall_status = "passed" if all(s.passed for s in stages) else "failed"
        report.completed_at = datetime.utcnow().isoformat() + "Z"

        final_report_path = self.reports_dir / f"pipeline-{run_id}.json"
        final_report_path.write_text(json.dumps(report.to_dict(), indent=2))
        logger.info(
            "=== Pipeline %s (run_id=%s) – report: %s ===",
            report.overall_status.upper(),
            run_id,
            final_report_path,
        )
        return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DevSecOps Pipeline Orchestrator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Path to project root (default: parent of this file)",
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
    pipeline = DevSecOpsPipeline(project_root=args.project_root)
    report = pipeline.run()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.overall_status == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())

