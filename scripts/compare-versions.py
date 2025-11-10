#!/usr/bin/env python3
"""
Compare Multiple Versions of the Same Project
Purpose: Score and rank different versions of duplicate projects to determine which to keep
"""

import os
import sys
import hashlib
import difflib
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json

# ANSI colors
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color

def print_header(text):
    print(f"{Colors.BLUE}=== {text} ==={Colors.NC}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

class ProjectVersion:
    """Represents a single version of a project"""

    def __init__(self, path):
        self.path = Path(path)
        self.name = self.path.name
        self.score = 0
        self.metrics = {}

    def analyze(self):
        """Analyze project and calculate quality metrics"""
        print(f"  Analyzing: {self.name}")

        # Count files by type
        self.metrics['total_files'] = len(list(self.path.rglob('*'))) if self.path.exists() else 0
        self.metrics['markdown_files'] = len(list(self.path.rglob('*.md')))
        self.metrics['python_files'] = len(list(self.path.rglob('*.py')))
        self.metrics['terraform_files'] = len(list(self.path.rglob('*.tf')))
        self.metrics['yaml_files'] = len(list(self.path.rglob('*.yaml'))) + len(list(self.path.rglob('*.yml')))
        self.metrics['shell_scripts'] = len(list(self.path.rglob('*.sh')))

        # Check for key documentation files
        self.metrics['has_readme'] = (self.path / 'README.md').exists()
        self.metrics['has_changelog'] = (self.path / 'CHANGELOG.md').exists()
        self.metrics['has_handbook'] = (self.path / 'HANDBOOK.md').exists()
        self.metrics['has_runbook'] = (self.path / 'RUNBOOK.md').exists()

        # Check for standard directories
        self.metrics['has_docs'] = (self.path / 'docs').exists()
        self.metrics['has_tests'] = (self.path / 'tests').exists()
        self.metrics['has_src'] = (self.path / 'src').exists()
        self.metrics['has_scripts'] = (self.path / 'scripts').exists()
        self.metrics['has_infrastructure'] = (
            (self.path / 'infrastructure').exists() or
            (self.path / 'terraform').exists() or
            (self.path / 'infra').exists()
        )

        # README quality analysis
        if self.metrics['has_readme']:
            readme_path = self.path / 'README.md'
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                readme_content = f.read()
                self.metrics['readme_length'] = len(readme_content)
                self.metrics['readme_lines'] = len(readme_content.split('\n'))

                # Check for key sections
                readme_lower = readme_content.lower()
                self.metrics['has_description'] = 'description' in readme_lower or '## ' in readme_content
                self.metrics['has_setup'] = 'setup' in readme_lower or 'installation' in readme_lower
                self.metrics['has_usage'] = 'usage' in readme_lower or 'how to' in readme_lower
                self.metrics['has_architecture'] = 'architecture' in readme_lower or 'design' in readme_lower
        else:
            self.metrics['readme_length'] = 0
            self.metrics['readme_lines'] = 0
            self.metrics['has_description'] = False
            self.metrics['has_setup'] = False
            self.metrics['has_usage'] = False
            self.metrics['has_architecture'] = False

        # Check for placeholders (indicators of incomplete work)
        self.metrics['placeholder_count'] = self._count_placeholders()

        # Get last modified time
        try:
            self.metrics['last_modified'] = max(
                f.stat().st_mtime for f in self.path.rglob('*') if f.is_file()
            )
            self.metrics['last_modified_str'] = datetime.fromtimestamp(
                self.metrics['last_modified']
            ).strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, OSError):
            self.metrics['last_modified'] = 0
            self.metrics['last_modified_str'] = 'Unknown'

        # Calculate quality score
        self._calculate_score()

    def _count_placeholders(self):
        """Count placeholder indicators in code and docs"""
        placeholder_patterns = [
            'TODO', 'FIXME', 'PLACEHOLDER', 'XXX', 'HACK',
            'Coming soon', 'To be implemented', 'TBD'
        ]
        count = 0

        for file_path in self.path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.py', '.md', '.sh', '.tf']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern in placeholder_patterns:
                            count += content.upper().count(pattern.upper())
                except:
                    pass

        return count

    def _calculate_score(self):
        """Calculate overall quality score (0-100)"""
        score = 0

        # Documentation completeness (40 points max)
        if self.metrics['has_readme']:
            score += 15
            # README quality
            if self.metrics['readme_length'] > 500:
                score += 5
            if self.metrics['readme_length'] > 2000:
                score += 5
            if self.metrics['has_description']:
                score += 3
            if self.metrics['has_setup']:
                score += 3
            if self.metrics['has_usage']:
                score += 3
            if self.metrics['has_architecture']:
                score += 3
        if self.metrics['has_changelog']:
            score += 3
        if self.metrics['has_handbook']:
            score += 2
        if self.metrics['has_runbook']:
            score += 3

        # Code completeness (30 points max)
        if self.metrics['python_files'] > 0:
            score += min(self.metrics['python_files'] * 2, 10)
        if self.metrics['terraform_files'] > 0:
            score += min(self.metrics['terraform_files'] * 2, 10)
        if self.metrics['shell_scripts'] > 0:
            score += min(self.metrics['shell_scripts'], 5)
        if self.metrics['yaml_files'] > 0:
            score += min(self.metrics['yaml_files'], 5)

        # Structure (20 points max)
        if self.metrics['has_docs']:
            score += 5
        if self.metrics['has_tests']:
            score += 5
        if self.metrics['has_src']:
            score += 3
        if self.metrics['has_scripts']:
            score += 3
        if self.metrics['has_infrastructure']:
            score += 4

        # Recency (10 points max)
        if self.metrics['last_modified'] > 0:
            days_old = (datetime.now().timestamp() - self.metrics['last_modified']) / 86400
            if days_old < 30:
                score += 10
            elif days_old < 90:
                score += 7
            elif days_old < 180:
                score += 5
            elif days_old < 365:
                score += 3

        # Penalize for placeholders
        score -= min(self.metrics['placeholder_count'], 20)

        self.score = max(0, min(100, score))

    def get_summary(self):
        """Return a summary string of metrics"""
        return (
            f"Score: {self.score}/100 | "
            f"Files: {self.metrics['total_files']} | "
            f"Docs: {self.metrics['markdown_files']} | "
            f"Code: {self.metrics['python_files']}py/{self.metrics['terraform_files']}tf | "
            f"Placeholders: {self.metrics['placeholder_count']} | "
            f"Modified: {self.metrics['last_modified_str']}"
        )


class ProjectComparator:
    """Compare multiple versions of the same project"""

    def __init__(self, project_paths):
        self.versions = [ProjectVersion(p) for p in project_paths]
        self.analyzed = False

    def analyze_all(self):
        """Analyze all versions"""
        print_header("Analyzing Project Versions")
        for version in self.versions:
            version.analyze()
        self.analyzed = True

    def rank_versions(self):
        """Rank versions by score"""
        if not self.analyzed:
            self.analyze_all()
        return sorted(self.versions, key=lambda v: v.score, reverse=True)

    def generate_report(self, output_path=None):
        """Generate comparison report"""
        if not self.analyzed:
            self.analyze_all()

        ranked = self.rank_versions()
        best = ranked[0]

        report = []
        report.append("# Project Version Comparison Report\n")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Versions Compared:** {len(self.versions)}\n\n")

        report.append("---\n\n")
        report.append("## Recommendation\n\n")
        report.append(f"**✅ KEEP:** `{best.name}` (Score: {best.score}/100)\n\n")

        if best.score < 50:
            report.append("⚠️ **Warning:** Even the best version has a low score. Consider significant improvements.\n\n")

        report.append("**Reasoning:**\n")
        if best.metrics['has_readme'] and best.metrics['readme_length'] > 1000:
            report.append("- ✅ Comprehensive documentation\n")
        if best.metrics['has_tests']:
            report.append("- ✅ Has test suite\n")
        if best.metrics['python_files'] > 5 or best.metrics['terraform_files'] > 3:
            report.append("- ✅ Substantial code implementation\n")
        if best.metrics['placeholder_count'] < 5:
            report.append("- ✅ Minimal placeholders (mostly complete)\n")

        report.append("\n---\n\n")
        report.append("## Version Rankings\n\n")

        for rank, version in enumerate(ranked, 1):
            medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else ""))
            report.append(f"### {medal} Rank #{rank}: `{version.name}` (Score: {version.score}/100)\n\n")

            report.append("**Metrics:**\n")
            report.append(f"- Total files: {version.metrics['total_files']}\n")
            report.append(f"- Documentation: {version.metrics['markdown_files']} markdown files\n")
            report.append(f"- Code files: {version.metrics['python_files']} Python, ")
            report.append(f"{version.metrics['terraform_files']} Terraform, ")
            report.append(f"{version.metrics['shell_scripts']} Shell\n")
            report.append(f"- Last modified: {version.metrics['last_modified_str']}\n")
            report.append(f"- Placeholders found: {version.metrics['placeholder_count']}\n\n")

            report.append("**Features:**\n")
            features = []
            if version.metrics['has_readme']:
                features.append("✅ README")
            else:
                features.append("❌ README")
            if version.metrics['has_changelog']:
                features.append("✅ CHANGELOG")
            if version.metrics['has_tests']:
                features.append("✅ Tests")
            if version.metrics['has_docs']:
                features.append("✅ Docs directory")
            if version.metrics['has_infrastructure']:
                features.append("✅ Infrastructure code")

            report.append(f"- {' | '.join(features)}\n\n")

            if rank == 1:
                report.append("**Verdict:** ✅ **KEEP THIS VERSION**\n\n")
            else:
                report.append("**Verdict:** ⚠️  Review for unique content, then archive\n\n")

        report.append("---\n\n")
        report.append("## Detailed Comparison Table\n\n")
        report.append("| Metric | " + " | ".join([f"`{v.name}`" for v in ranked]) + " |\n")
        report.append("|--------|" + "|".join(["--------"] * len(ranked)) + "|\n")

        metrics_to_compare = [
            ('Overall Score', lambda v: f"{v.score}/100"),
            ('Total Files', lambda v: v.metrics['total_files']),
            ('README', lambda v: '✅' if v.metrics['has_readme'] else '❌'),
            ('README Length', lambda v: v.metrics.get('readme_length', 0)),
            ('CHANGELOG', lambda v: '✅' if v.metrics['has_changelog'] else '❌'),
            ('Tests', lambda v: '✅' if v.metrics['has_tests'] else '❌'),
            ('Python Files', lambda v: v.metrics['python_files']),
            ('Terraform Files', lambda v: v.metrics['terraform_files']),
            ('Placeholders', lambda v: v.metrics['placeholder_count']),
            ('Last Modified', lambda v: v.metrics['last_modified_str']),
        ]

        for metric_name, metric_getter in metrics_to_compare:
            row = f"| {metric_name} | "
            row += " | ".join([str(metric_getter(v)) for v in ranked])
            row += " |\n"
            report.append(row)

        report.append("\n---\n\n")
        report.append("## Next Steps\n\n")
        report.append("1. **Extract unique content** from lower-ranked versions\n")
        report.append("2. **Merge into best version** if any unique value found\n")
        report.append("3. **Archive old versions** to `archive/` directory\n")
        report.append("4. **Update documentation** with merged content\n")
        report.append("5. **Verify all links** still work after merge\n\n")

        report_text = "".join(report)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)
            print_success(f"Report saved to: {output_path}")

        return report_text


def main():
    if len(sys.argv) < 3:
        print("Usage: ./compare-versions.py <project_path_1> <project_path_2> [project_path_3 ...]")
        print("\nExample:")
        print("  ./compare-versions.py projects/p01-aws-infra projects/1-aws-infrastructure-automation")
        sys.exit(1)

    project_paths = sys.argv[1:]

    # Validate paths
    valid_paths = []
    for path in project_paths:
        if Path(path).exists():
            valid_paths.append(path)
        else:
            print_error(f"Path not found: {path}")

    if len(valid_paths) < 2:
        print_error("Need at least 2 valid project paths to compare")
        sys.exit(1)

    print_header(f"Comparing {len(valid_paths)} Project Versions")
    print()

    # Compare
    comparator = ProjectComparator(valid_paths)
    comparator.analyze_all()

    # Show results
    print()
    print_header("Results")
    print()

    ranked = comparator.rank_versions()
    for rank, version in enumerate(ranked, 1):
        prefix = f"{Colors.GREEN}✓ KEEP:{Colors.NC} " if rank == 1 else f"{Colors.YELLOW}  #{rank}:{Colors.NC} "
        print(f"{prefix}{version.name}")
        print(f"       {version.get_summary()}")
        print()

    # Generate report
    repo_root = Path(__file__).parent.parent
    report_path = repo_root / "docs" / "VERSION_COMPARISON_REPORT.md"
    report_text = comparator.generate_report(report_path)

    print_success(f"Detailed report: {report_path}")

    # Return exit code based on analysis
    if ranked[0].score < 30:
        print_warning("Best version has low quality score - significant work needed")
        sys.exit(2)
    else:
        print_success("Analysis complete")
        sys.exit(0)


if __name__ == '__main__':
    main()
