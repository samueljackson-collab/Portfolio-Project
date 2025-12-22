from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set

DEFAULT_REQUIRED_DOCS: Sequence[str] = (
    "README.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "LICENSE",
    "SECURITY.md",
    "ARCHITECTURE.md",
)


@dataclass
class RepositoryMetrics:
    """Aggregated metrics describing a repository analysis run."""

    name: str
    path: Optional[str] = None
    has_documentation: bool = False
    documentation_files: List[str] = field(default_factory=list)
    required_documentation: List[str] = field(
        default_factory=lambda: list(DEFAULT_REQUIRED_DOCS)
    )
    missing_documentation: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def record_documentation(self, doc_path: str) -> None:
        """Track a discovered documentation file."""
        normalized = str(doc_path)
        if normalized not in self.documentation_files:
            self.documentation_files.append(normalized)
            self.has_documentation = True


class _AnalyzerBase:
    """Shared utilities for repository analysis."""

    def _normalize_doc_identifiers(self, documentation_files: Iterable[str]) -> Set[str]:
        """Normalize documentation identifiers for matching."""
        identifiers: Set[str] = set()
        for doc in documentation_files:
            path = Path(doc)
            identifiers.add(path.name.lower())
            identifiers.add(str(path.as_posix()).lower())
        return identifiers

    def _analyze_gaps(self, metrics: RepositoryMetrics) -> None:
        """Populate missing documentation using discovered files."""
        doc_identifiers = self._normalize_doc_identifiers(metrics.documentation_files)
        metrics.missing_documentation = [
            doc
            for doc in metrics.required_documentation
            if doc.lower() not in doc_identifiers
        ]
        self._apply_documentation_recommendations(metrics)

    def _apply_documentation_recommendations(self, metrics: RepositoryMetrics) -> None:
        """Attach recommendations based on missing documentation."""
        if metrics.missing_documentation:
            missing_list = ", ".join(metrics.missing_documentation)
            metrics.recommendations.append(
                f"Add required documentation files: {missing_list}."
            )
        elif not metrics.documentation_files:
            metrics.recommendations.append(
                "Add baseline documentation (README, architecture, security)."
            )


class PortfolioAnalyzer(_AnalyzerBase):
    """Analyze local repositories for portfolio completeness."""

    def __init__(self, required_documentation: Optional[Sequence[str]] = None) -> None:
        self.required_documentation: Sequence[str] = (
            required_documentation or DEFAULT_REQUIRED_DOCS
        )

    def analyze_repository(self, repo_path: Path | str) -> RepositoryMetrics:
        """Analyze a local repository directory."""
        repo_path = Path(repo_path)
        metrics = RepositoryMetrics(
            name=repo_path.name,
            path=str(repo_path),
            required_documentation=list(self.required_documentation),
        )

        for doc in self._collect_documentation_files(repo_path):
            metrics.record_documentation(doc)

        self._analyze_gaps(metrics)
        return metrics

    def _collect_documentation_files(self, repo_path: Path) -> List[str]:
        """Collect documentation files within a repository."""
        doc_paths: Set[str] = set()
        for pattern in ("*.md", "*.rst", "*.adoc"):
            for path in repo_path.rglob(pattern):
                try:
                    relative = path.relative_to(repo_path)
                except ValueError:
                    relative = path
                doc_paths.add(str(relative.as_posix()))
        return sorted(doc_paths)


class GitHubAnalyzer(_AnalyzerBase):
    """Analyze repositories using GitHub tree metadata."""

    def __init__(self, required_documentation: Optional[Sequence[str]] = None) -> None:
        self.required_documentation: Sequence[str] = (
            required_documentation or DEFAULT_REQUIRED_DOCS
        )

    def analyze_repository(
        self,
        repo_full_name: str,
        tree: Optional[Sequence[str | dict]] = None,
    ) -> RepositoryMetrics:
        """Analyze a repository using a supplied GitHub tree payload."""
        metrics = RepositoryMetrics(
            name=repo_full_name,
            path=repo_full_name,
            required_documentation=list(self.required_documentation),
        )

        for doc in self._collect_documentation_from_tree(tree or []):
            metrics.record_documentation(doc)

        self._analyze_gaps(metrics)
        return metrics

    def _collect_documentation_from_tree(
        self, tree: Sequence[str | dict]
    ) -> List[str]:
        """Extract documentation file paths from a GitHub tree."""
        doc_paths: Set[str] = set()
        for entry in tree:
            if isinstance(entry, str):
                path_str = entry
            elif isinstance(entry, dict):
                path_str = entry.get("path") or entry.get("name")
            else:
                continue

            if not path_str:
                continue

            path = Path(path_str)
            if path.suffix.lower() in {".md", ".rst", ".adoc"}:
                doc_paths.add(str(path.as_posix()))
        return sorted(doc_paths)
