#!/usr/bin/env python3
"""
Security Dashboard Generator

Aggregates results from multiple security scanning tools and generates
an HTML dashboard with visualizations and summaries.

Supports:
- Semgrep (SAST)
- Bandit (Python security)
- Trivy (Container/IaC scanning)
- Gitleaks (Secret detection)
- OWASP Dependency-Check (SCA)
- Checkov (IaC security)
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader


@dataclass
class Finding:
    """Represents a security finding."""
    id: str
    title: str
    severity: str  # critical, high, medium, low, info
    tool: str
    file: str
    line: int
    description: str
    cwe: Optional[str] = None
    fix: Optional[str] = None


@dataclass
class ScanResults:
    """Aggregated scan results."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    findings: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    tools_run: list = field(default_factory=list)

    def add_finding(self, finding: Finding):
        self.findings.append(finding)

    def calculate_summary(self):
        """Calculate summary statistics."""
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        tool_counts = {}
        cwe_counts = {}

        for finding in self.findings:
            severity = finding.severity.lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

            tool_counts[finding.tool] = tool_counts.get(finding.tool, 0) + 1

            if finding.cwe:
                cwe_counts[finding.cwe] = cwe_counts.get(finding.cwe, 0) + 1

        self.summary = {
            "total": len(self.findings),
            "by_severity": severity_counts,
            "by_tool": tool_counts,
            "by_cwe": dict(sorted(cwe_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "risk_score": self._calculate_risk_score(severity_counts)
        }

    def _calculate_risk_score(self, severity_counts: dict) -> int:
        """Calculate overall risk score (0-100)."""
        weights = {"critical": 40, "high": 20, "medium": 5, "low": 1, "info": 0}
        score = sum(severity_counts[s] * weights[s] for s in severity_counts)
        return min(100, score)


def parse_semgrep(file_path: str) -> list:
    """Parse Semgrep JSON output."""
    findings = []
    try:
        with open(file_path) as f:
            data = json.load(f)

        for result in data.get("results", []):
            severity_map = {
                "ERROR": "high",
                "WARNING": "medium",
                "INFO": "low"
            }
            finding = Finding(
                id=result.get("check_id", "unknown"),
                title=result.get("check_id", "").split(".")[-1].replace("-", " ").title(),
                severity=severity_map.get(result.get("extra", {}).get("severity", "INFO"), "low"),
                tool="Semgrep",
                file=result.get("path", ""),
                line=result.get("start", {}).get("line", 0),
                description=result.get("extra", {}).get("message", ""),
                cwe=result.get("extra", {}).get("metadata", {}).get("cwe", None)
            )
            findings.append(finding)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse Semgrep results: {e}")

    return findings


def parse_bandit(file_path: str) -> list:
    """Parse Bandit JSON output."""
    findings = []
    try:
        with open(file_path) as f:
            data = json.load(f)

        severity_map = {"HIGH": "high", "MEDIUM": "medium", "LOW": "low"}

        for result in data.get("results", []):
            finding = Finding(
                id=result.get("test_id", "unknown"),
                title=result.get("test_name", "Unknown"),
                severity=severity_map.get(result.get("issue_severity", "LOW"), "low"),
                tool="Bandit",
                file=result.get("filename", ""),
                line=result.get("line_number", 0),
                description=result.get("issue_text", ""),
                cwe=result.get("issue_cwe", {}).get("id") if result.get("issue_cwe") else None
            )
            findings.append(finding)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse Bandit results: {e}")

    return findings


def parse_trivy(file_path: str) -> list:
    """Parse Trivy JSON output."""
    findings = []
    try:
        with open(file_path) as f:
            data = json.load(f)

        for result in data.get("Results", []):
            for vuln in result.get("Vulnerabilities", []):
                finding = Finding(
                    id=vuln.get("VulnerabilityID", "unknown"),
                    title=vuln.get("Title", vuln.get("VulnerabilityID", "Unknown")),
                    severity=vuln.get("Severity", "UNKNOWN").lower(),
                    tool="Trivy",
                    file=result.get("Target", ""),
                    line=0,
                    description=vuln.get("Description", ""),
                    fix=vuln.get("FixedVersion")
                )
                findings.append(finding)

            for misconfig in result.get("Misconfigurations", []):
                finding = Finding(
                    id=misconfig.get("ID", "unknown"),
                    title=misconfig.get("Title", "Unknown"),
                    severity=misconfig.get("Severity", "UNKNOWN").lower(),
                    tool="Trivy",
                    file=result.get("Target", ""),
                    line=0,
                    description=misconfig.get("Description", ""),
                    fix=misconfig.get("Resolution")
                )
                findings.append(finding)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse Trivy results: {e}")

    return findings


def parse_gitleaks(file_path: str) -> list:
    """Parse Gitleaks JSON output."""
    findings = []
    try:
        with open(file_path) as f:
            data = json.load(f)

        for result in data if isinstance(data, list) else []:
            finding = Finding(
                id=result.get("RuleID", "unknown"),
                title=f"Secret Detected: {result.get('RuleID', 'Unknown')}",
                severity="critical",  # Secrets are always critical
                tool="Gitleaks",
                file=result.get("File", ""),
                line=result.get("StartLine", 0),
                description=f"Secret of type '{result.get('RuleID')}' found in code"
            )
            findings.append(finding)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse Gitleaks results: {e}")

    return findings


def parse_checkov(file_path: str) -> list:
    """Parse Checkov JSON output."""
    findings = []
    try:
        with open(file_path) as f:
            data = json.load(f)

        for check_type in data.get("results", {}).get("failed_checks", []):
            severity_map = {
                "CRITICAL": "critical",
                "HIGH": "high",
                "MEDIUM": "medium",
                "LOW": "low"
            }
            finding = Finding(
                id=check_type.get("check_id", "unknown"),
                title=check_type.get("check_name", "Unknown"),
                severity=severity_map.get(check_type.get("severity", "MEDIUM"), "medium"),
                tool="Checkov",
                file=check_type.get("file_path", ""),
                line=check_type.get("file_line_range", [0])[0],
                description=check_type.get("guideline", "")
            )
            findings.append(finding)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse Checkov results: {e}")

    return findings


def generate_dashboard(results: ScanResults, template_dir: str, output_path: str):
    """Generate HTML dashboard from scan results."""
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("dashboard.html")

    # Sort findings by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    results.findings.sort(key=lambda x: severity_order.get(x.severity.lower(), 5))

    html = template.render(
        results=results,
        timestamp=results.timestamp,
        summary=results.summary,
        findings=results.findings,
        tools_run=results.tools_run
    )

    with open(output_path, "w") as f:
        f.write(html)

    print(f"Dashboard generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate security scan dashboard")
    parser.add_argument("--semgrep", help="Path to Semgrep JSON results")
    parser.add_argument("--bandit", help="Path to Bandit JSON results")
    parser.add_argument("--trivy", help="Path to Trivy JSON results")
    parser.add_argument("--gitleaks", help="Path to Gitleaks JSON results")
    parser.add_argument("--checkov", help="Path to Checkov JSON results")
    parser.add_argument("--template-dir", default="templates", help="Template directory")
    parser.add_argument("--output", default="security-dashboard.html", help="Output HTML file")

    args = parser.parse_args()

    results = ScanResults()

    # Parse all available scan results
    parsers = {
        "Semgrep": (args.semgrep, parse_semgrep),
        "Bandit": (args.bandit, parse_bandit),
        "Trivy": (args.trivy, parse_trivy),
        "Gitleaks": (args.gitleaks, parse_gitleaks),
        "Checkov": (args.checkov, parse_checkov),
    }

    for tool, (file_path, parser_func) in parsers.items():
        if file_path and os.path.exists(file_path):
            findings = parser_func(file_path)
            for finding in findings:
                results.add_finding(finding)
            results.tools_run.append(tool)
            print(f"Parsed {len(findings)} findings from {tool}")

    results.calculate_summary()

    # Generate dashboard
    script_dir = Path(__file__).parent.parent
    template_dir = script_dir / args.template_dir

    generate_dashboard(results, str(template_dir), args.output)

    # Print summary
    print("\n=== Security Scan Summary ===")
    print(f"Total findings: {results.summary['total']}")
    print(f"Risk score: {results.summary['risk_score']}/100")
    print("\nBy severity:")
    for severity, count in results.summary["by_severity"].items():
        if count > 0:
            print(f"  {severity.upper()}: {count}")


if __name__ == "__main__":
    main()
