#!/usr/bin/env python3
"""
Security Dashboard Generator

Parses JSON output from security scanners and generates an HTML dashboard.
Supports: Semgrep, Bandit, Gitleaks, Trivy, Syft, Checkov, CodeQL

Usage:
    python scripts/generate-dashboard.py --output-dir ./reports
    python scripts/generate-dashboard.py --scan-dir ./scan-results --output dashboard.html

The script will look for scan results in common locations:
    - semgrep-results.json
    - bandit-report.json
    - gitleaks-report.json
    - trivy-results.json
    - syft-sbom.json
    - checkov-results.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import Counter
import html


@dataclass
class Finding:
    """Represents a security finding."""
    tool: str
    severity: str
    title: str
    description: str
    file: str = ""
    line: int = 0
    cwe: str = ""
    category: str = ""
    recommendation: str = ""


@dataclass
class ScanSummary:
    """Summary of scan results."""
    tool: str
    total_findings: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    scan_time: str = ""
    status: str = "unknown"


@dataclass
class DashboardData:
    """Complete dashboard data."""
    findings: List[Finding] = field(default_factory=list)
    summaries: List[ScanSummary] = field(default_factory=list)
    sbom_packages: List[Dict] = field(default_factory=list)
    scan_timestamp: str = ""
    commit_sha: str = ""
    branch: str = ""


def normalize_severity(severity: str) -> str:
    """Normalize severity levels across different tools."""
    severity = severity.upper()
    severity_map = {
        'CRITICAL': 'critical',
        'HIGH': 'high',
        'MEDIUM': 'medium',
        'MODERATE': 'medium',
        'LOW': 'low',
        'INFO': 'info',
        'INFORMATIONAL': 'info',
        'WARNING': 'medium',
        'ERROR': 'high',
        'NOTE': 'info',
        'UNKNOWN': 'info'
    }
    return severity_map.get(severity, 'info')


def parse_semgrep_results(filepath: Path) -> tuple[List[Finding], ScanSummary]:
    """Parse Semgrep JSON output."""
    findings = []
    summary = ScanSummary(tool="Semgrep")

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        results = data.get('results', [])

        for result in results:
            severity = normalize_severity(result.get('extra', {}).get('severity', 'info'))
            finding = Finding(
                tool="Semgrep",
                severity=severity,
                title=result.get('check_id', 'Unknown'),
                description=result.get('extra', {}).get('message', ''),
                file=result.get('path', ''),
                line=result.get('start', {}).get('line', 0),
                cwe=result.get('extra', {}).get('metadata', {}).get('cwe', ''),
                category=result.get('extra', {}).get('metadata', {}).get('category', ''),
                recommendation=result.get('extra', {}).get('fix', '')
            )
            findings.append(finding)

            # Update summary counts
            if severity == 'critical':
                summary.critical += 1
            elif severity == 'high':
                summary.high += 1
            elif severity == 'medium':
                summary.medium += 1
            elif severity == 'low':
                summary.low += 1
            else:
                summary.info += 1

        summary.total_findings = len(findings)
        summary.status = "completed"

    except FileNotFoundError:
        summary.status = "not_run"
    except json.JSONDecodeError:
        summary.status = "error"

    return findings, summary


def parse_bandit_results(filepath: Path) -> tuple[List[Finding], ScanSummary]:
    """Parse Bandit JSON output."""
    findings = []
    summary = ScanSummary(tool="Bandit")

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        results = data.get('results', [])

        for result in results:
            severity = normalize_severity(result.get('issue_severity', 'info'))
            finding = Finding(
                tool="Bandit",
                severity=severity,
                title=result.get('test_id', '') + ': ' + result.get('test_name', 'Unknown'),
                description=result.get('issue_text', ''),
                file=result.get('filename', ''),
                line=result.get('line_number', 0),
                cwe=result.get('issue_cwe', {}).get('id', '') if isinstance(result.get('issue_cwe'), dict) else '',
                category=result.get('test_name', ''),
                recommendation=f"Confidence: {result.get('issue_confidence', 'Unknown')}"
            )
            findings.append(finding)

            if severity == 'critical':
                summary.critical += 1
            elif severity == 'high':
                summary.high += 1
            elif severity == 'medium':
                summary.medium += 1
            elif severity == 'low':
                summary.low += 1
            else:
                summary.info += 1

        summary.total_findings = len(findings)
        summary.status = "completed"

        # Parse metrics if available
        metrics = data.get('metrics', {})
        if metrics:
            summary.scan_time = f"Files scanned: {metrics.get('_totals', {}).get('loc', 'N/A')} LOC"

    except FileNotFoundError:
        summary.status = "not_run"
    except json.JSONDecodeError:
        summary.status = "error"

    return findings, summary


def parse_gitleaks_results(filepath: Path) -> tuple[List[Finding], ScanSummary]:
    """Parse Gitleaks JSON output."""
    findings = []
    summary = ScanSummary(tool="Gitleaks")

    try:
        with open(filepath, 'r') as f:
            content = f.read().strip()
            if not content or content == "[]":
                summary.status = "completed"
                return findings, summary
            data = json.loads(content)

        if not isinstance(data, list):
            data = [data]

        for result in data:
            # All secret findings are critical
            finding = Finding(
                tool="Gitleaks",
                severity="critical",
                title=f"Secret Detected: {result.get('RuleID', 'Unknown')}",
                description=result.get('Description', 'Hardcoded secret detected'),
                file=result.get('File', ''),
                line=result.get('StartLine', 0),
                category="secrets",
                recommendation="Remove the secret and rotate credentials immediately"
            )
            findings.append(finding)
            summary.critical += 1

        summary.total_findings = len(findings)
        summary.status = "completed"

    except FileNotFoundError:
        summary.status = "not_run"
    except json.JSONDecodeError:
        summary.status = "error"

    return findings, summary


def parse_trivy_results(filepath: Path) -> tuple[List[Finding], ScanSummary]:
    """Parse Trivy JSON output."""
    findings = []
    summary = ScanSummary(tool="Trivy")

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        results = data.get('Results', [])

        for result in results:
            vulnerabilities = result.get('Vulnerabilities', [])
            misconfigurations = result.get('Misconfigurations', [])
            secrets = result.get('Secrets', [])

            # Process vulnerabilities
            for vuln in vulnerabilities or []:
                severity = normalize_severity(vuln.get('Severity', 'info'))
                finding = Finding(
                    tool="Trivy",
                    severity=severity,
                    title=f"{vuln.get('VulnerabilityID', 'Unknown')}: {vuln.get('PkgName', '')}",
                    description=vuln.get('Title', ''),
                    file=result.get('Target', ''),
                    cwe=', '.join(vuln.get('CweIDs', [])) if vuln.get('CweIDs') else '',
                    category="vulnerability",
                    recommendation=f"Fixed in: {vuln.get('FixedVersion', 'N/A')}"
                )
                findings.append(finding)

                if severity == 'critical':
                    summary.critical += 1
                elif severity == 'high':
                    summary.high += 1
                elif severity == 'medium':
                    summary.medium += 1
                elif severity == 'low':
                    summary.low += 1
                else:
                    summary.info += 1

            # Process misconfigurations
            for misconfig in misconfigurations or []:
                severity = normalize_severity(misconfig.get('Severity', 'info'))
                finding = Finding(
                    tool="Trivy",
                    severity=severity,
                    title=f"{misconfig.get('ID', 'Unknown')}: {misconfig.get('Title', '')}",
                    description=misconfig.get('Description', ''),
                    file=result.get('Target', ''),
                    category="misconfiguration",
                    recommendation=misconfig.get('Resolution', '')
                )
                findings.append(finding)

                if severity == 'critical':
                    summary.critical += 1
                elif severity == 'high':
                    summary.high += 1
                elif severity == 'medium':
                    summary.medium += 1
                elif severity == 'low':
                    summary.low += 1
                else:
                    summary.info += 1

            # Process secrets
            for secret in secrets or []:
                finding = Finding(
                    tool="Trivy",
                    severity="critical",
                    title=f"Secret: {secret.get('RuleID', 'Unknown')}",
                    description=secret.get('Title', ''),
                    file=result.get('Target', ''),
                    line=secret.get('StartLine', 0),
                    category="secrets"
                )
                findings.append(finding)
                summary.critical += 1

        summary.total_findings = len(findings)
        summary.status = "completed"

    except FileNotFoundError:
        summary.status = "not_run"
    except json.JSONDecodeError:
        summary.status = "error"

    return findings, summary


def parse_syft_sbom(filepath: Path) -> tuple[List[Dict], ScanSummary]:
    """Parse Syft SBOM output."""
    packages = []
    summary = ScanSummary(tool="Syft (SBOM)")

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Handle SPDX format
        if 'packages' in data:
            for pkg in data.get('packages', []):
                packages.append({
                    'name': pkg.get('name', ''),
                    'version': pkg.get('versionInfo', ''),
                    'type': pkg.get('externalRefs', [{}])[0].get('referenceType', 'unknown'),
                    'license': pkg.get('licenseConcluded', 'Unknown')
                })
        # Handle CycloneDX format
        elif 'components' in data:
            for comp in data.get('components', []):
                packages.append({
                    'name': comp.get('name', ''),
                    'version': comp.get('version', ''),
                    'type': comp.get('type', 'unknown'),
                    'license': comp.get('licenses', [{}])[0].get('license', {}).get('id', 'Unknown') if comp.get('licenses') else 'Unknown'
                })

        summary.total_findings = len(packages)
        summary.status = "completed"

    except FileNotFoundError:
        summary.status = "not_run"
    except json.JSONDecodeError:
        summary.status = "error"

    return packages, summary


def parse_checkov_results(filepath: Path) -> tuple[List[Finding], ScanSummary]:
    """Parse Checkov JSON output."""
    findings = []
    summary = ScanSummary(tool="Checkov")

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Checkov can return array or object
        if isinstance(data, list):
            results_list = data
        else:
            results_list = [data]

        for check_result in results_list:
            failed_checks = check_result.get('results', {}).get('failed_checks', [])
            passed_checks = check_result.get('results', {}).get('passed_checks', [])

            for check in failed_checks:
                # Map check severity
                guideline = check.get('guideline', '')
                if 'critical' in guideline.lower():
                    severity = 'critical'
                elif 'high' in guideline.lower():
                    severity = 'high'
                else:
                    severity = 'medium'

                finding = Finding(
                    tool="Checkov",
                    severity=severity,
                    title=f"{check.get('check_id', 'Unknown')}: {check.get('check_name', '')}",
                    description=check.get('check_name', ''),
                    file=check.get('file_path', ''),
                    line=check.get('file_line_range', [0])[0],
                    category=check.get('check_type', 'IaC'),
                    recommendation=check.get('guideline', '')
                )
                findings.append(finding)

                if severity == 'critical':
                    summary.critical += 1
                elif severity == 'high':
                    summary.high += 1
                elif severity == 'medium':
                    summary.medium += 1
                else:
                    summary.low += 1

            # Update summary with passed checks info
            summary.info = len(passed_checks)

        summary.total_findings = len(findings)
        summary.status = "completed"

    except FileNotFoundError:
        summary.status = "not_run"
    except json.JSONDecodeError:
        summary.status = "error"

    return findings, summary


def generate_html_dashboard(data: DashboardData, template_path: Optional[Path] = None) -> str:
    """Generate HTML dashboard from scan data."""

    # Calculate totals
    total_critical = sum(s.critical for s in data.summaries)
    total_high = sum(s.high for s in data.summaries)
    total_medium = sum(s.medium for s in data.summaries)
    total_low = sum(s.low for s in data.summaries)
    total_findings = sum(s.total_findings for s in data.summaries)

    # Determine overall status
    if total_critical > 0:
        overall_status = "critical"
        status_text = "Critical Issues Found"
        status_color = "#dc3545"
    elif total_high > 0:
        overall_status = "warning"
        status_text = "High Severity Issues"
        status_color = "#fd7e14"
    elif total_medium > 0:
        overall_status = "caution"
        status_text = "Medium Severity Issues"
        status_color = "#ffc107"
    else:
        overall_status = "success"
        status_text = "No Critical Issues"
        status_color = "#28a745"

    # Generate tool summaries HTML
    tool_cards = ""
    for summary in data.summaries:
        status_badge = {
            'completed': '<span class="badge bg-success">Completed</span>',
            'not_run': '<span class="badge bg-secondary">Not Run</span>',
            'error': '<span class="badge bg-danger">Error</span>',
            'unknown': '<span class="badge bg-warning">Unknown</span>'
        }.get(summary.status, '<span class="badge bg-secondary">Unknown</span>')

        tool_cards += f"""
        <div class="col-md-4 mb-3">
            <div class="card h-100">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <strong>{html.escape(summary.tool)}</strong>
                    {status_badge}
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col">
                            <div class="fs-4 text-danger">{summary.critical}</div>
                            <small>Critical</small>
                        </div>
                        <div class="col">
                            <div class="fs-4 text-warning">{summary.high}</div>
                            <small>High</small>
                        </div>
                        <div class="col">
                            <div class="fs-4 text-info">{summary.medium}</div>
                            <small>Medium</small>
                        </div>
                        <div class="col">
                            <div class="fs-4 text-secondary">{summary.low}</div>
                            <small>Low</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

    # Generate findings table
    findings_rows = ""
    for finding in sorted(data.findings, key=lambda x: ['critical', 'high', 'medium', 'low', 'info'].index(x.severity)):
        severity_class = {
            'critical': 'table-danger',
            'high': 'table-warning',
            'medium': 'table-info',
            'low': 'table-secondary',
            'info': ''
        }.get(finding.severity, '')

        findings_rows += f"""
        <tr class="{severity_class}">
            <td><span class="badge bg-{finding.severity if finding.severity != 'info' else 'secondary'}">{html.escape(finding.severity.upper())}</span></td>
            <td>{html.escape(finding.tool)}</td>
            <td>{html.escape(finding.title)}</td>
            <td><code>{html.escape(finding.file)}:{finding.line}</code></td>
            <td>{html.escape(finding.description[:100])}{'...' if len(finding.description) > 100 else ''}</td>
        </tr>
        """

    # Generate SBOM section
    sbom_rows = ""
    for pkg in data.sbom_packages[:50]:  # Limit to 50 packages
        sbom_rows += f"""
        <tr>
            <td>{html.escape(pkg.get('name', ''))}</td>
            <td>{html.escape(pkg.get('version', ''))}</td>
            <td>{html.escape(pkg.get('type', ''))}</td>
            <td>{html.escape(pkg.get('license', ''))}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {{
            --status-color: {status_color};
        }}
        .status-banner {{
            background-color: var(--status-color);
            color: white;
        }}
        .severity-critical {{ color: #dc3545; }}
        .severity-high {{ color: #fd7e14; }}
        .severity-medium {{ color: #ffc107; }}
        .severity-low {{ color: #6c757d; }}
        .bg-critical {{ background-color: #dc3545 !important; }}
        .bg-high {{ background-color: #fd7e14 !important; }}
        .bg-medium {{ background-color: #ffc107 !important; color: #000 !important; }}
        .bg-low {{ background-color: #6c757d !important; }}
        .findings-table {{ font-size: 0.9rem; }}
        .card {{ box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    </style>
</head>
<body class="bg-light">
    <div class="status-banner py-3 mb-4">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 mb-0"><i class="bi bi-shield-check me-2"></i>Security Dashboard</h1>
                    <small>Generated: {data.scan_timestamp}</small>
                </div>
                <div class="text-end">
                    <div class="fs-5">{status_text}</div>
                    <small>Commit: {data.commit_sha[:8] if data.commit_sha else 'N/A'} | Branch: {data.branch or 'N/A'}</small>
                </div>
            </div>
        </div>
    </div>

    <div class="container mb-5">
        <!-- Summary Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center border-danger">
                    <div class="card-body">
                        <div class="display-4 text-danger">{total_critical}</div>
                        <div class="text-muted">Critical</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center border-warning">
                    <div class="card-body">
                        <div class="display-4 text-warning">{total_high}</div>
                        <div class="text-muted">High</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center border-info">
                    <div class="card-body">
                        <div class="display-4 text-info">{total_medium}</div>
                        <div class="text-muted">Medium</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center border-secondary">
                    <div class="card-body">
                        <div class="display-4 text-secondary">{total_low}</div>
                        <div class="text-muted">Low</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tool Summaries -->
        <h2 class="h4 mb-3"><i class="bi bi-tools me-2"></i>Scan Results by Tool</h2>
        <div class="row mb-4">
            {tool_cards}
        </div>

        <!-- Findings Table -->
        <h2 class="h4 mb-3"><i class="bi bi-exclamation-triangle me-2"></i>All Findings ({total_findings})</h2>
        <div class="card mb-4">
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover findings-table mb-0">
                        <thead class="table-dark">
                            <tr>
                                <th>Severity</th>
                                <th>Tool</th>
                                <th>Finding</th>
                                <th>Location</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {findings_rows if findings_rows else '<tr><td colspan="5" class="text-center text-muted">No findings</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- SBOM Section -->
        <h2 class="h4 mb-3"><i class="bi bi-box-seam me-2"></i>Software Bill of Materials ({len(data.sbom_packages)} packages)</h2>
        <div class="card mb-4">
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-sm table-hover mb-0">
                        <thead class="table-dark">
                            <tr>
                                <th>Package</th>
                                <th>Version</th>
                                <th>Type</th>
                                <th>License</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sbom_rows if sbom_rows else '<tr><td colspan="4" class="text-center text-muted">No SBOM data</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
            {f'<div class="card-footer text-muted">Showing first 50 of {len(data.sbom_packages)} packages</div>' if len(data.sbom_packages) > 50 else ''}
        </div>

        <!-- Footer -->
        <div class="text-center text-muted mt-4">
            <p>DevSecOps Security Dashboard | Generated by generate-dashboard.py</p>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    return html_content


def find_scan_results(scan_dir: Path) -> Dict[str, Path]:
    """Find scan result files in the given directory."""
    result_files = {}

    # Common filenames for scan results
    patterns = {
        'semgrep': ['semgrep-results.json', 'semgrep.json', 'semgrep-report.json'],
        'bandit': ['bandit-report.json', 'bandit.json', 'bandit-results.json'],
        'gitleaks': ['gitleaks-report.json', 'gitleaks.json', 'gitleaks-results.json'],
        'trivy': ['trivy-results.json', 'trivy.json', 'trivy-report.json', 'trivy-fs-results.json'],
        'syft': ['syft-sbom.json', 'sbom.json', 'sbom.spdx.json', 'sbom.cyclonedx.json'],
        'checkov': ['checkov-results.json', 'checkov.json', 'checkov-report.json']
    }

    for tool, filenames in patterns.items():
        for filename in filenames:
            filepath = scan_dir / filename
            if filepath.exists():
                result_files[tool] = filepath
                break

    return result_files


def main():
    parser = argparse.ArgumentParser(description='Generate security dashboard from scan results')
    parser.add_argument('--scan-dir', type=Path, default=Path('.'),
                        help='Directory containing scan results (default: current directory)')
    parser.add_argument('--output', type=Path, default=Path('security-dashboard.html'),
                        help='Output HTML file (default: security-dashboard.html)')
    parser.add_argument('--output-dir', type=Path,
                        help='Output directory for all reports')
    parser.add_argument('--template', type=Path,
                        help='Custom HTML template file')
    parser.add_argument('--commit', type=str, default=os.environ.get('GITHUB_SHA', ''),
                        help='Git commit SHA')
    parser.add_argument('--branch', type=str, default=os.environ.get('GITHUB_REF_NAME', ''),
                        help='Git branch name')
    parser.add_argument('--json-output', type=Path,
                        help='Also output results as JSON')

    # Individual file overrides
    parser.add_argument('--semgrep', type=Path, help='Semgrep results file')
    parser.add_argument('--bandit', type=Path, help='Bandit results file')
    parser.add_argument('--gitleaks', type=Path, help='Gitleaks results file')
    parser.add_argument('--trivy', type=Path, help='Trivy results file')
    parser.add_argument('--syft', type=Path, help='Syft SBOM file')
    parser.add_argument('--checkov', type=Path, help='Checkov results file')

    args = parser.parse_args()

    # Set up output directory
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        args.output = args.output_dir / 'security-dashboard.html'

    # Find or use specified scan result files
    result_files = find_scan_results(args.scan_dir)

    # Override with explicit paths if provided
    if args.semgrep:
        result_files['semgrep'] = args.semgrep
    if args.bandit:
        result_files['bandit'] = args.bandit
    if args.gitleaks:
        result_files['gitleaks'] = args.gitleaks
    if args.trivy:
        result_files['trivy'] = args.trivy
    if args.syft:
        result_files['syft'] = args.syft
    if args.checkov:
        result_files['checkov'] = args.checkov

    print(f"[*] Security Dashboard Generator")
    print(f"[*] Scan directory: {args.scan_dir}")
    print(f"[*] Found {len(result_files)} scan result files")

    # Initialize dashboard data
    dashboard_data = DashboardData(
        scan_timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        commit_sha=args.commit,
        branch=args.branch
    )

    # Parse each scan result
    parsers = {
        'semgrep': parse_semgrep_results,
        'bandit': parse_bandit_results,
        'gitleaks': parse_gitleaks_results,
        'trivy': parse_trivy_results,
        'checkov': parse_checkov_results
    }

    for tool, filepath in result_files.items():
        print(f"[*] Parsing {tool}: {filepath}")

        if tool == 'syft':
            packages, summary = parse_syft_sbom(filepath)
            dashboard_data.sbom_packages = packages
            dashboard_data.summaries.append(summary)
        elif tool in parsers:
            findings, summary = parsers[tool](filepath)
            dashboard_data.findings.extend(findings)
            dashboard_data.summaries.append(summary)

    # Add placeholder summaries for tools that weren't run
    existing_tools = {s.tool for s in dashboard_data.summaries}
    for tool in ['Semgrep', 'Bandit', 'Gitleaks', 'Trivy', 'Checkov', 'Syft (SBOM)']:
        if tool not in existing_tools:
            dashboard_data.summaries.append(ScanSummary(tool=tool, status='not_run'))

    # Generate HTML dashboard
    print(f"[*] Generating dashboard...")
    html_content = generate_html_dashboard(dashboard_data, args.template)

    # Write output
    with open(args.output, 'w') as f:
        f.write(html_content)
    print(f"[+] Dashboard written to: {args.output}")

    # Write JSON output if requested
    if args.json_output:
        json_data = {
            'timestamp': dashboard_data.scan_timestamp,
            'commit': dashboard_data.commit_sha,
            'branch': dashboard_data.branch,
            'summaries': [
                {
                    'tool': s.tool,
                    'total': s.total_findings,
                    'critical': s.critical,
                    'high': s.high,
                    'medium': s.medium,
                    'low': s.low,
                    'status': s.status
                }
                for s in dashboard_data.summaries
            ],
            'findings': [
                {
                    'tool': f.tool,
                    'severity': f.severity,
                    'title': f.title,
                    'file': f.file,
                    'line': f.line,
                    'description': f.description
                }
                for f in dashboard_data.findings
            ],
            'sbom_package_count': len(dashboard_data.sbom_packages)
        }
        with open(args.json_output, 'w') as f:
            json.dump(json_data, f, indent=2)
        print(f"[+] JSON report written to: {args.json_output}")

    # Print summary
    total_critical = sum(s.critical for s in dashboard_data.summaries)
    total_high = sum(s.high for s in dashboard_data.summaries)

    print(f"\n[*] Summary:")
    print(f"    Critical: {total_critical}")
    print(f"    High: {total_high}")
    print(f"    Total Findings: {len(dashboard_data.findings)}")
    print(f"    SBOM Packages: {len(dashboard_data.sbom_packages)}")

    # Exit with error if critical findings
    if total_critical > 0:
        print(f"\n[!] CRITICAL: {total_critical} critical findings detected!")
        sys.exit(1)

    print(f"\n[+] Dashboard generation complete!")


if __name__ == '__main__':
    main()
