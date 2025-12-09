"""Collect project data from portfolio for report generation."""
from __future__ import annotations

import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ProjectData:
    """Data structure for a single project."""

    def __init__(
        self,
        id: str,
        name: str,
        path: Path,
        status: str = "unknown",
        completion: int = 0,
        description: str = "",
        tech_stack: List[str] = None,
        has_tests: bool = False,
        has_ci_cd: bool = False,
        has_docker: bool = False,
        has_k8s: bool = False,
        line_count: int = 0,
        file_count: int = 0,
        last_modified: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.path = path
        self.status = status
        self.completion = completion
        self.description = description
        self.tech_stack = tech_stack or []
        self.has_tests = has_tests
        self.has_ci_cd = has_ci_cd
        self.has_docker = has_docker
        self.has_k8s = has_k8s
        self.line_count = line_count
        self.file_count = file_count
        self.last_modified = last_modified

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering."""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'completion': self.completion,
            'description': self.description,
            'tech_stack': self.tech_stack,
            'has_tests': self.has_tests,
            'has_ci_cd': self.has_ci_cd,
            'has_docker': self.has_docker,
            'has_k8s': self.has_k8s,
            'line_count': self.line_count,
            'file_count': self.file_count,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'status_color': self._get_status_color(),
            'completion_class': self._get_completion_class()
        }

    def _get_status_color(self) -> str:
        """Get color for status indicator."""
        if self.completion >= 90:
            return 'green'
        elif self.completion >= 70:
            return 'yellow'
        elif self.completion >= 50:
            return 'orange'
        else:
            return 'red'

    def _get_completion_class(self) -> str:
        """Get CSS class for completion percentage."""
        if self.completion >= 90:
            return 'high'
        elif self.completion >= 50:
            return 'medium'
        else:
            return 'low'


class PortfolioDataCollector:
    """Collects data from portfolio projects for report generation."""

    def __init__(self, portfolio_root: Path):
        self.portfolio_root = portfolio_root
        self.projects_dir = portfolio_root / "projects"

    def collect_all_projects(self) -> List[ProjectData]:
        """Scan all projects and collect data."""
        projects = []

        if not self.projects_dir.exists():
            return projects

        # Scan numbered project directories
        for project_dir in sorted(self.projects_dir.iterdir()):
            if project_dir.is_dir() and not project_dir.name.startswith('.'):
                project_data = self._collect_project_data(project_dir)
                if project_data:
                    projects.append(project_data)

        return projects

    def _collect_project_data(self, project_path: Path) -> Optional[ProjectData]:
        """Collect data for a single project."""
        try:
            # Extract project ID from directory name (e.g., "1-aws-infrastructure" -> "1")
            match = re.match(r'^(\d+|p-\d+)-(.+)$', project_path.name)
            if not match:
                return None

            project_id = match.group(1)
            project_slug = match.group(2)

            # Read README for project info
            readme_path = project_path / "README.md"
            name, description = self._parse_readme(readme_path, project_slug)

            # Detect tech stack
            tech_stack = self._detect_tech_stack(project_path)

            # Check for various files
            has_tests = self._has_tests(project_path)
            has_ci_cd = self._has_ci_cd(project_path)
            has_docker = (project_path / "Dockerfile").exists() or (project_path / "docker-compose.yml").exists()
            has_k8s = (project_path / "k8s").exists() or (project_path / "kubernetes").exists()

            # Count lines and files
            line_count, file_count = self._count_code(project_path)

            # Get last modified time
            last_modified = self._get_last_modified(project_path)

            # Estimate completion based on artifacts
            completion = self._estimate_completion(
                has_readme=(readme_path.exists()),
                has_tests=has_tests,
                has_ci_cd=has_ci_cd,
                has_docker=has_docker,
                line_count=line_count
            )

            # Determine status
            status = self._determine_status(completion)

            return ProjectData(
                id=project_id,
                name=name,
                path=project_path,
                status=status,
                completion=completion,
                description=description,
                tech_stack=tech_stack,
                has_tests=has_tests,
                has_ci_cd=has_ci_cd,
                has_docker=has_docker,
                has_k8s=has_k8s,
                line_count=line_count,
                file_count=file_count,
                last_modified=last_modified
            )

        except Exception as e:
            print(f"Error collecting data for {project_path}: {e}")
            return None

    def _parse_readme(self, readme_path: Path, fallback_name: str) -> tuple[str, str]:
        """Parse README to extract project name and description."""
        if not readme_path.exists():
            return fallback_name.replace('-', ' ').title(), ""

        try:
            content = readme_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            # Find first h1 heading
            name = None
            description = ""

            for i, line in enumerate(lines):
                if line.startswith('# '):
                    name = line[2:].strip()
                    # Look for description in next few lines
                    for j in range(i + 1, min(i + 10, len(lines))):
                        desc_line = lines[j].strip()
                        if desc_line and not desc_line.startswith('#'):
                            description = desc_line
                            break
                    break

            if not name:
                name = fallback_name.replace('-', ' ').title()

            return name, description

        except Exception:
            return fallback_name.replace('-', ' ').title(), ""

    def _detect_tech_stack(self, project_path: Path) -> List[str]:
        """Detect technologies used in the project."""
        tech_stack = []

        # Check for various technology indicators
        if (project_path / "package.json").exists():
            tech_stack.append("Node.js")
        if (project_path / "requirements.txt").exists() or (project_path / "setup.py").exists():
            tech_stack.append("Python")
        if (project_path / "go.mod").exists():
            tech_stack.append("Go")
        if (project_path / "pom.xml").exists() or (project_path / "build.gradle").exists():
            tech_stack.append("Java")
        if (project_path / "Cargo.toml").exists():
            tech_stack.append("Rust")

        # Infrastructure tools
        if (project_path / "terraform").exists() or list(project_path.glob("**/*.tf")):
            tech_stack.append("Terraform")
        if (project_path / "Dockerfile").exists():
            tech_stack.append("Docker")
        if (project_path / "k8s").exists() or (project_path / "kubernetes").exists():
            tech_stack.append("Kubernetes")
        if (project_path / "template.yaml").exists() or (project_path / "samconfig.toml").exists():
            tech_stack.append("AWS SAM")
        if (project_path / "serverless.yml").exists():
            tech_stack.append("Serverless Framework")

        # Specific tools
        if (project_path / "prometheus").exists():
            tech_stack.append("Prometheus")
        if (project_path / "grafana").exists():
            tech_stack.append("Grafana")
        if list(project_path.glob("**/argocd/**")):
            tech_stack.append("ArgoCD")

        return tech_stack

    def _has_tests(self, project_path: Path) -> bool:
        """Check if project has tests."""
        test_dirs = ["tests", "test", "spec"]
        for test_dir in test_dirs:
            if (project_path / test_dir).exists():
                return True

        # Check for test files
        test_files = list(project_path.glob("**/*test*.py"))
        test_files.extend(list(project_path.glob("**/*spec*.js")))
        return len(test_files) > 0

    def _has_ci_cd(self, project_path: Path) -> bool:
        """Check if project has CI/CD configuration."""
        ci_paths = [
            ".github/workflows",
            ".gitlab-ci.yml",
            ".circleci",
            "Jenkinsfile",
            "azure-pipelines.yml"
        ]

        for ci_path in ci_paths:
            if (project_path / ci_path).exists():
                return True

        return False

    def _count_code(self, project_path: Path) -> tuple[int, int]:
        """Count lines of code and number of files."""
        extensions = {'.py', '.js', '.ts', '.go', '.java', '.rs', '.tf', '.yaml', '.yml', '.sh'}
        exclude_dirs = {'.git', 'node_modules', 'venv', '__pycache__', 'target', 'dist', 'build'}

        total_lines = 0
        file_count = 0

        try:
            for file_path in project_path.rglob('*'):
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in exclude_dirs):
                    continue

                if file_path.is_file() and file_path.suffix in extensions:
                    try:
                        lines = len(file_path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                        total_lines += lines
                        file_count += 1
                    except Exception:
                        pass

        except Exception:
            pass

        return total_lines, file_count

    def _get_last_modified(self, project_path: Path) -> Optional[datetime]:
        """Get last modification time of project."""
        try:
            latest_time = None

            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if latest_time is None or mtime > latest_time:
                        latest_time = mtime

            return latest_time

        except Exception:
            return None

    def _estimate_completion(
        self,
        has_readme: bool,
        has_tests: bool,
        has_ci_cd: bool,
        has_docker: bool,
        line_count: int
    ) -> int:
        """Estimate project completion percentage."""
        score = 0

        # Basic criteria
        if has_readme:
            score += 20
        if line_count > 100:
            score += 20
        if line_count > 500:
            score += 10

        # Quality indicators
        if has_tests:
            score += 25
        if has_ci_cd:
            score += 15
        if has_docker:
            score += 10

        return min(score, 100)

    def _determine_status(self, completion: int) -> str:
        """Determine project status based on completion."""
        if completion >= 90:
            return "production-ready"
        elif completion >= 70:
            return "near-complete"
        elif completion >= 50:
            return "in-progress"
        elif completion >= 20:
            return "started"
        else:
            return "planning"

    def get_summary_stats(self, projects: List[ProjectData]) -> Dict[str, Any]:
        """Calculate summary statistics for all projects."""
        if not projects:
            return {
                'total_projects': 0,
                'avg_completion': 0,
                'total_lines': 0,
                'total_files': 0,
                'status_breakdown': {},
                'tech_stack_count': {}
            }

        total_completion = sum(p.completion for p in projects)
        total_lines = sum(p.line_count for p in projects)
        total_files = sum(p.file_count for p in projects)

        # Status breakdown
        status_breakdown = {}
        for project in projects:
            status_breakdown[project.status] = status_breakdown.get(project.status, 0) + 1

        # Tech stack popularity
        tech_stack_count = {}
        for project in projects:
            for tech in project.tech_stack:
                tech_stack_count[tech] = tech_stack_count.get(tech, 0) + 1

        return {
            'total_projects': len(projects),
            'avg_completion': total_completion // len(projects) if projects else 0,
            'total_lines': total_lines,
            'total_files': total_files,
            'status_breakdown': status_breakdown,
            'tech_stack_count': dict(sorted(tech_stack_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            'projects_with_tests': sum(1 for p in projects if p.has_tests),
            'projects_with_ci_cd': sum(1 for p in projects if p.has_ci_cd),
            'projects_with_docker': sum(1 for p in projects if p.has_docker),
            'projects_with_k8s': sum(1 for p in projects if p.has_k8s)
        }
