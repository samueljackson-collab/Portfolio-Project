#!/usr/bin/env python3
"""
Portfolio Metrics Tracking System
Analyzes and reports on portfolio completion and progress
"""

import json
import logging
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Optional
import re

import requests


logger = logging.getLogger(__name__)


class PortfolioMetrics:
    """Track and report portfolio project metrics"""

    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.projects_dir = self.base_dir / "projects"
        self.metrics = self._initialize_metrics()

    def _initialize_metrics(self):
        """Initialize metrics structure"""
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_completion": 0,
            "projects": {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "planned": 0,
                "with_code": 0,
                "with_docs": 0,
                "with_tests": 0,
                "with_demos": 0,
            },
            "github": {
                "total_commits": 0,
                "total_files": 0,
                "total_lines": 0,
                "languages": {},
            },
            "documentation": {
                "readme_files": 0,
                "markdown_files": 0,
                "total_words": 0,
            },
            "infrastructure": {
                "docker_compose_files": 0,
                "terraform_files": 0,
                "kubernetes_manifests": 0,
                "config_files": 0,
            },
            "project_details": [],
        }

    def analyze_github_activity(self, repo: Optional[str] = None, token: Optional[str] = None) -> None:
        """Populate GitHub metrics using the REST API."""

        repository = repo or os.getenv("GITHUB_REPO", "samueljackson-collab/Portfolio-Project")
        github_token = token or os.getenv("GITHUB_TOKEN")

        try:
            total_commits = self._analyze_via_rest_api(repository, github_token)
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response else "unknown"
            if status_code == 403:
                rate_remaining = exc.response.headers.get("X-RateLimit-Remaining") if exc.response else None
                if rate_remaining == "0":
                    print("⚠️  GitHub API rate limit exceeded. Set GITHUB_TOKEN or wait for reset.")
                else:
                    print("⚠️  GitHub API access forbidden. Verify token scopes or repository visibility.")
            elif status_code == 401:
                print("⚠️  GitHub API authentication failed. Check your GITHUB_TOKEN.")
            else:
                print(f"⚠️  GitHub API error ({status_code}): {exc}")
            logger.warning("GitHub API HTTP error when analyzing commits", exc_info=exc)
            return
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  Unexpected error analyzing GitHub commits: {exc}")
            logger.exception("Unexpected error analyzing GitHub commits")
            return

        self.metrics["github"]["total_commits"] = total_commits
        print(f"✅ GitHub commits analyzed for {repository}: {total_commits}")

    def _analyze_via_rest_api(self, repository: str, token: Optional[str] = None) -> int:
        """Return total commits using GitHub REST API with paging safeguards."""

        url = f"https://api.github.com/repos/{repository}/commits"
        headers = {"Accept": "application/vnd.github+json"}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(url, headers=headers, params={"per_page": 1}, timeout=20)
        self._raise_for_github_errors(response)

        total_commits = self._extract_total_from_headers(response)
        if total_commits is not None:
            return total_commits

        print("ℹ️  Link header missing; scanning commit pages until exhausted.")
        return self._count_commits_by_iteration(url, headers)

    def _raise_for_github_errors(self, response: requests.Response) -> None:
        """Raise for status with clearer logging for auth or rate limits."""

        if response.status_code in (401, 403):
            rate_remaining = response.headers.get("X-RateLimit-Remaining")
            rate_reset = response.headers.get("X-RateLimit-Reset")
            logger.error(
                "GitHub API returned %s (remaining=%s, reset=%s)",
                response.status_code,
                rate_remaining,
                rate_reset,
            )
        response.raise_for_status()

    def _extract_total_from_headers(self, response: requests.Response) -> Optional[int]:
        """Extract commit total from Link or X-Total-Count headers."""

        if "X-Total-Count" in response.headers:
            try:
                return int(response.headers["X-Total-Count"])
            except ValueError:
                logger.warning("Invalid X-Total-Count header: %s", response.headers["X-Total-Count"])

        link_header = response.headers.get("Link", "")
        if "rel=\"last\"" in link_header:
            match = re.search(r"[?&]page=(\d+)>; rel=\"last\"", link_header)
            if match:
                return int(match.group(1))

        return None

    def _count_commits_by_iteration(self, url: str, headers: dict) -> int:
        """Fallback pagination when Link headers are absent."""

        total_commits = 0
        page = 1
        per_page = 100

        while True:
            page_response = requests.get(
                url,
                headers=headers,
                params={"per_page": per_page, "page": page},
                timeout=20,
            )
            self._raise_for_github_errors(page_response)

            commits = page_response.json()
            if not isinstance(commits, list):
                raise ValueError("Unexpected response format from GitHub commits API")

            if not commits:
                break

            total_commits += len(commits)
            if len(commits) < per_page:
                break

            page += 1

        return total_commits

    def scan_projects(self):
        """Scan projects directory and collect metrics"""
        print("🔍 Scanning portfolio projects...")

        if not self.projects_dir.exists():
            print(f"❌ Projects directory not found: {self.projects_dir}")
            return

        # Get all project directories
        project_dirs = [d for d in self.projects_dir.iterdir() if d.is_dir()]
        self.metrics["projects"]["total"] = len(project_dirs)

        for project_dir in project_dirs:
            project_metrics = self._analyze_project(project_dir)
            self.metrics["project_details"].append(project_metrics)

            # Update aggregate metrics
            if project_metrics["has_code"]:
                self.metrics["projects"]["with_code"] += 1
            if project_metrics["has_docs"]:
                self.metrics["projects"]["with_docs"] += 1
            if project_metrics["has_tests"]:
                self.metrics["projects"]["with_tests"] += 1
            if project_metrics["has_demo"]:
                self.metrics["projects"]["with_demos"] += 1

            # Count by status
            status = project_metrics["status"]
            if status == "complete":
                self.metrics["projects"]["completed"] += 1
            elif status == "in_progress":
                self.metrics["projects"]["in_progress"] += 1
            elif status == "planned":
                self.metrics["projects"]["planned"] += 1

        print(f"✅ Scanned {len(project_dirs)} projects")

    def _analyze_project(self, project_dir):
        """Analyze individual project metrics"""
        project_name = project_dir.name
        readme_path = project_dir / "README.md"

        metrics = {
            "name": project_name,
            "path": str(project_dir.relative_to(self.base_dir)),
            "has_code": False,
            "has_docs": False,
            "has_tests": False,
            "has_demo": False,
            "status": "planned",
            "completion": 0,
            "file_count": 0,
            "languages": [],
        }

        # Check for README
        if readme_path.exists():
            metrics["has_docs"] = True
            self.metrics["documentation"]["readme_files"] += 1

            # Try to extract status and completion from README
            try:
                content = readme_path.read_text(encoding='utf-8')
                metrics["status"], metrics["completion"] = self._extract_status(content)
            except Exception as e:
                print(f"⚠️  Error reading {readme_path}: {e}")

        # Check for source code
        code_indicators = ["src", "lib", "app", "scripts", "terraform", "k8s"]
        for indicator in code_indicators:
            if (project_dir / indicator).exists():
                metrics["has_code"] = True
                break

        # Check for tests
        test_indicators = ["test", "tests", "__tests__", "spec"]
        for indicator in test_indicators:
            if (project_dir / indicator).exists():
                metrics["has_tests"] = True
                break

        # Check for demos
        demo_indicators = ["demo", "demos", "examples", "screenshots"]
        for indicator in demo_indicators:
            if (project_dir / indicator).exists():
                metrics["has_demo"] = True
                break

        # Count files
        try:
            metrics["file_count"] = len(list(project_dir.rglob("*")))
        except Exception:
            metrics["file_count"] = 0

        # Detect languages
        metrics["languages"] = self._detect_languages(project_dir)

        return metrics

    def _extract_status(self, readme_content):
        """Extract project status and completion percentage from README"""
        status = "planned"
        completion = 0

        # Look for status indicators
        status_patterns = {
            "complete": r"(?i)(status|completion).*complete",
            "in_progress": r"(?i)(status|completion).*(in progress|progress)",
            "planned": r"(?i)(status|completion).*planned",
        }

        for s, pattern in status_patterns.items():
            if re.search(pattern, readme_content):
                status = s
                break

        # Look for completion percentage
        completion_match = re.search(r"(\d{1,3})\s*%", readme_content)
        if completion_match:
            completion = int(completion_match.group(1))
        elif status == "complete":
            completion = 100
        elif status == "in_progress":
            completion = 50
        elif status == "planned":
            completion = 10

        return status, completion

    def _detect_languages(self, project_dir):
        """Detect programming languages used in project"""
        language_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tf": "Terraform",
            ".yml": "YAML",
            ".yaml": "YAML",
            ".go": "Go",
            ".sh": "Shell",
            ".java": "Java",
            ".rs": "Rust",
        }

        languages = set()
        try:
            for ext, lang in language_extensions.items():
                if list(project_dir.rglob(f"*{ext}")):
                    languages.add(lang)
        except Exception:
            pass

        return sorted(list(languages))

    def scan_documentation(self):
        """Scan documentation files"""
        print("📚 Scanning documentation...")

        md_files = list(self.base_dir.rglob("*.md"))
        self.metrics["documentation"]["markdown_files"] = len(md_files)

        total_words = 0
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                words = len(content.split())
                total_words += words
            except Exception:
                continue

        self.metrics["documentation"]["total_words"] = total_words
        print(f"✅ Found {len(md_files)} markdown files ({total_words:,} words)")

    def scan_infrastructure(self):
        """Scan infrastructure as code files"""
        print("🏗️  Scanning infrastructure files...")

        # Docker Compose
        compose_files = list(self.base_dir.rglob("*compose*.yml")) + \
                       list(self.base_dir.rglob("docker-compose*.yml"))
        self.metrics["infrastructure"]["docker_compose_files"] = len(compose_files)

        # Terraform
        tf_files = list(self.base_dir.rglob("*.tf"))
        self.metrics["infrastructure"]["terraform_files"] = len(tf_files)

        # Kubernetes
        k8s_files = list(self.base_dir.rglob("k8s/**/*.yml")) + \
                   list(self.base_dir.rglob("k8s/**/*.yaml"))
        self.metrics["infrastructure"]["kubernetes_manifests"] = len(k8s_files)

        # Config files
        config_patterns = ["*.json", "*.toml", "*.ini", "*.conf"]
        config_count = 0
        for pattern in config_patterns:
            config_count += len(list(self.base_dir.rglob(pattern)))
        self.metrics["infrastructure"]["config_files"] = config_count

        print(f"✅ Found {len(compose_files)} Docker Compose, {len(tf_files)} Terraform files")

    def calculate_overall_completion(self):
        """Calculate overall portfolio completion percentage"""
        if not self.metrics["project_details"]:
            return 0

        total_completion = sum(p["completion"] for p in self.metrics["project_details"])
        avg_completion = total_completion / len(self.metrics["project_details"])

        self.metrics["overall_completion"] = round(avg_completion, 1)
        return self.metrics["overall_completion"]

    def generate_report(self):
        """Generate and display metrics report"""
        completion = self.calculate_overall_completion()

        print("\n" + "=" * 70)
        print("📊 PORTFOLIO METRICS DASHBOARD")
        print("=" * 70)

        # Overall Stats
        print(f"\n🎯 Overall Completion: {completion}%")
        self._print_progress_bar(completion)

        # Project Breakdown
        print(f"\n📁 Projects:")
        print(f"   Total:        {self.metrics['projects']['total']}")
        print(f"   Completed:    {self.metrics['projects']['completed']} 🟢")
        print(f"   In Progress:  {self.metrics['projects']['in_progress']} 🟡")
        print(f"   Planned:      {self.metrics['projects']['planned']} 🔵")

        # Implementation Status
        print(f"\n💻 Implementation:")
        print(f"   With Code:    {self.metrics['projects']['with_code']}/{self.metrics['projects']['total']}")
        print(f"   With Docs:    {self.metrics['projects']['with_docs']}/{self.metrics['projects']['total']}")
        print(f"   With Tests:   {self.metrics['projects']['with_tests']}/{self.metrics['projects']['total']}")
        print(f"   With Demos:   {self.metrics['projects']['with_demos']}/{self.metrics['projects']['total']}")

        # Documentation
        print(f"\n📚 Documentation:")
        print(f"   README files: {self.metrics['documentation']['readme_files']}")
        print(f"   Markdown:     {self.metrics['documentation']['markdown_files']}")
        print(f"   Total words:  {self.metrics['documentation']['total_words']:,}")

        # Infrastructure
        print(f"\n🏗️  Infrastructure:")
        print(f"   Docker Compose: {self.metrics['infrastructure']['docker_compose_files']}")
        print(f"   Terraform:      {self.metrics['infrastructure']['terraform_files']}")
        print(f"   Kubernetes:     {self.metrics['infrastructure']['kubernetes_manifests']}")

        # Top Projects
        print(f"\n⭐ Top Projects by Completion:")
        sorted_projects = sorted(
            self.metrics["project_details"],
            key=lambda p: p["completion"],
            reverse=True
        )
        for i, project in enumerate(sorted_projects[:5], 1):
            status_emoji = {"complete": "🟢", "in_progress": "🟡", "planned": "🔵"}.get(
                project["status"], "⚪"
            )
            print(f"   {i}. {project['name']}: {project['completion']}% {status_emoji}")

        print("\n" + "=" * 70)

    def _print_progress_bar(self, percentage, length=40):
        """Print a visual progress bar"""
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        print(f"   [{bar}] {percentage}%")

    def save_metrics(self, output_file="portfolio-metrics.json"):
        """Save metrics to JSON file"""
        output_path = self.base_dir / output_file

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2)

        print(f"\n💾 Metrics saved to: {output_path}")

    def generate_badge_data(self):
        """Generate data for GitHub badges"""
        completion = self.metrics["overall_completion"]
        color = "green" if completion >= 80 else "yellow" if completion >= 50 else "red"

        badge_data = {
            "schemaVersion": 1,
            "label": "portfolio completion",
            "message": f"{completion}%",
            "color": color
        }

        badge_path = self.base_dir / "portfolio-badge.json"
        with open(badge_path, 'w', encoding='utf-8') as f:
            json.dump(badge_data, f, indent=2)

        print(f"🏆 Badge data saved to: {badge_path}")

    def run_full_analysis(self):
        """Run complete portfolio analysis"""
        print("🚀 Starting Portfolio Metrics Analysis\n")

        self.scan_projects()
        self.scan_documentation()
        self.scan_infrastructure()
        self.analyze_github_activity()
        self.generate_report()
        self.save_metrics()
        self.generate_badge_data()

        print("\n✨ Analysis complete!")


def main():
    """Main entry point"""
    metrics = PortfolioMetrics()
    metrics.run_full_analysis()


if __name__ == "__main__":
    main()
