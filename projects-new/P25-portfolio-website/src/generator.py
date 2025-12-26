#!/usr/bin/env python3
"""
Portfolio Website Generator

Generates static HTML pages from project metadata.
"""

import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from typing import List, Dict


class PortfolioGenerator:
    """Generate static portfolio website."""

    def __init__(self, projects_dir: str = "../../", output_dir: str = "dist"):
        """Initialize generator."""
        self.projects_dir = Path(projects_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Setup Jinja2
        self.env = Environment(
            loader=FileSystemLoader('templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def scan_projects(self) -> List[Dict]:
        """Scan repository for projects."""
        projects = []

        # Scan projects/ directory
        projects_path = self.projects_dir / "projects"
        if projects_path.exists():
            for project_dir in sorted(projects_path.iterdir()):
                if project_dir.is_dir() and not project_dir.name.startswith('.'):
                    project_info = self._extract_project_info(project_dir)
                    if project_info:
                        projects.append(project_info)

        # Scan projects-new/ directory
        projects_new_path = self.projects_dir / "projects-new"
        if projects_new_path.exists():
            for project_dir in sorted(projects_new_path.iterdir()):
                if project_dir.is_dir() and not project_dir.name.startswith('.'):
                    project_info = self._extract_project_info(project_dir)
                    if project_info:
                        projects.append(project_info)

        return projects

    def _extract_project_info(self, project_dir: Path) -> Dict:
        """Extract project information from directory."""
        readme_path = project_dir / "README.md"
        if not readme_path.exists():
            return None

        # Parse README
        with open(readme_path, 'r') as f:
            content = f.read()

        # Extract title (first # heading)
        title = "Unknown Project"
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break

        # Extract description (first paragraph after title)
        description = ""
        lines = content.split('\n')
        in_description = False
        for line in lines:
            if in_description and line.strip():
                description = line.strip()
                break
            if line.startswith('# '):
                in_description = True

        # Determine project status
        status = self._determine_status(project_dir)

        # Get technologies
        technologies = self._extract_technologies(content)

        return {
            'id': project_dir.name,
            'title': title,
            'description': description,
            'status': status,
            'technologies': technologies,
            'path': str(project_dir.relative_to(self.projects_dir))
        }

    def _determine_status(self, project_dir: Path) -> str:
        """Determine project completion status."""
        # Check for key indicators
        has_tests = (project_dir / "tests").exists()
        has_src = (project_dir / "src").exists()
        has_infra = (project_dir / "infra").exists()

        # Check CHANGELOG for completion indicators
        changelog_path = project_dir / "CHANGELOG.md"
        if changelog_path.exists():
            with open(changelog_path, 'r') as f:
                content = f.read()
                if "[1.0.0]" in content or "production" in content.lower():
                    return "complete"

        if has_tests and has_src:
            return "in-progress"

        if has_src or has_infra:
            return "started"

        return "planned"

    def _extract_technologies(self, readme_content: str) -> List[str]:
        """Extract technologies from README."""
        technologies = []
        tech_keywords = {
            'Python': ['python', 'pytest', 'flask', 'django', 'fastapi'],
            'Terraform': ['terraform', 'hcl'],
            'Kubernetes': ['kubernetes', 'k8s', 'kubectl', 'helm'],
            'AWS': ['aws', 'cloudformation', 's3', 'ec2', 'rds', 'lambda'],
            'Docker': ['docker', 'dockerfile', 'container'],
            'TypeScript': ['typescript', 'ts'],
            'React': ['react', 'jsx'],
            'Prometheus': ['prometheus'],
            'Grafana': ['grafana']
        }

        content_lower = readme_content.lower()
        for tech, keywords in tech_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                technologies.append(tech)

        return technologies[:5]  # Limit to 5 technologies

    def generate_index(self, projects: List[Dict]):
        """Generate index.html."""
        template = self.env.get_template('index.html')

        # Group projects by status
        complete = [p for p in projects if p['status'] == 'complete']
        in_progress = [p for p in projects if p['status'] == 'in-progress']
        planned = [p for p in projects if p['status'] in ['started', 'planned']]

        html = template.render(
            projects=projects,
            complete_projects=complete,
            in_progress_projects=in_progress,
            planned_projects=planned,
            total_projects=len(projects),
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        output_path = self.output_dir / "index.html"
        with open(output_path, 'w') as f:
            f.write(html)

        print(f"✓ Generated index.html ({len(projects)} projects)")

    def generate_project_pages(self, projects: List[Dict]):
        """Generate individual project pages."""
        template = self.env.get_template('project.html')

        for project in projects:
            html = template.render(
                project=project,
                generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            project_dir = self.output_dir / "projects"
            project_dir.mkdir(exist_ok=True)

            output_path = project_dir / f"{project['id']}.html"
            with open(output_path, 'w') as f:
                f.write(html)

        print(f"✓ Generated {len(projects)} project pages")

    def copy_assets(self):
        """Copy static assets."""
        import shutil

        assets_src = Path("assets")
        if assets_src.exists():
            assets_dst = self.output_dir / "assets"
            if assets_dst.exists():
                shutil.rmtree(assets_dst)
            shutil.copytree(assets_src, assets_dst)
            print("✓ Copied assets")

    def generate(self):
        """Generate complete website."""
        print("Generating portfolio website...")
        print("=" * 60)

        # Scan projects
        projects = self.scan_projects()
        print(f"Found {len(projects)} projects")

        # Generate pages
        self.generate_index(projects)
        self.generate_project_pages(projects)
        self.copy_assets()

        print("=" * 60)
        print(f"✓ Website generated in: {self.output_dir}")
        print(f"  Open {self.output_dir}/index.html in your browser")


def main():
    """Main entry point."""
    generator = PortfolioGenerator()
    generator.generate()


if __name__ == '__main__':
    main()
