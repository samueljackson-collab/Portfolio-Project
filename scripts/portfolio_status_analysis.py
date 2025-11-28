#!/usr/bin/env python3
"""Portfolio status analysis utility.

This script compares a local Master Portfolio Index with live GitHub repository
metadata so you can quickly identify misalignments (missing repos, outdated
branches, stale activity, etc.). It is intentionally verbose and includes
inline logging to make it easy to follow in CI jobs or ad-hoc shell sessions.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import requests


@dataclass
class PortfolioEntry:
    """Represents a single project in the Master Portfolio Index."""

    identifier: str
    name: str
    repo: str
    status: str
    owner: Optional[str] = None


@dataclass
class RepoStatus:
    """Evaluation result for a single GitHub repository."""

    entry: PortfolioEntry
    exists: bool
    archived: bool
    pushed_at: Optional[datetime]
    default_branch: Optional[str]
    description: Optional[str]
    error: Optional[str] = None

    @property
    def age_days(self) -> Optional[int]:
        if not self.pushed_at:
            return None
        return (datetime.now(timezone.utc) - self.pushed_at).days

    @property
    def stale(self) -> bool:
        """Flag repositories older than 90 days without pushes."""

        if self.pushed_at is None:
            return True
        return self.age_days is not None and self.age_days > 90


class PortfolioStatusAnalyzer:
    """Load portfolio expectations and compare them against GitHub metadata."""

    def __init__(self, token: Optional[str], default_owner: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/vnd.github+json"})
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.default_owner = default_owner

    def _parse_markdown_table(self, path: Path) -> List[PortfolioEntry]:
        """Parse a Markdown table into portfolio entries.

        This handles tables with headers like `| ID | Name | Repo | Status |`.
        Additional columns are ignored, but the first four are expected.
        """

        rows: List[PortfolioEntry] = []
        with path.open("r", encoding="utf-8") as handle:
            lines = [line.strip() for line in handle if line.strip().startswith("|")]
        # Filter out the separator row consisting of dashes.
        content_lines = [line for line in lines if not re.match(r"\|[- ]+\|", line)]
        reader = csv.reader(content_lines, delimiter="|")
        parsed_rows = [
            [cell.strip() for cell in row if cell.strip()]
            for row in reader
            if any(cell.strip() for cell in row)
        ]
        if not parsed_rows:
            raise ValueError(f"No Markdown table rows detected in {path}")

        for idx, row in enumerate(parsed_rows[1:]):  # skip header
            try:
                identifier, name, repo, status, *rest = row
            except ValueError as exc:
                raise ValueError(
                    f"Row {idx + 2} in {path} does not have the expected columns"
                ) from exc
            owner = rest[0] if rest else self.default_owner
            rows.append(PortfolioEntry(identifier=identifier, name=name, repo=repo, status=status, owner=owner))
        return rows

    def load_portfolio_index(self, index_path: Path) -> List[PortfolioEntry]:
        """Load Master Portfolio Index data.

        Supports JSON (list of objects), CSV, and Markdown table formats so the
        script can adapt to however the index is maintained.
        """

        if not index_path.exists():
            raise FileNotFoundError(f"Portfolio index not found: {index_path}")

        if index_path.suffix.lower() == ".json":
            data = json.loads(index_path.read_text(encoding="utf-8"))
            return [
                PortfolioEntry(
                    identifier=str(item.get("id") or item.get("identifier") or ""),
                    name=item.get("name") or "",
                    repo=item.get("repo") or item.get("repository") or "",
                    status=item.get("status") or "unknown",
                    owner=item.get("owner") or self.default_owner,
                )
                for item in data
            ]

        if index_path.suffix.lower() == ".csv":
            with index_path.open("r", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                return [
                    PortfolioEntry(
                        identifier=row.get("id") or row.get("identifier") or "",
                        name=row.get("name") or "",
                        repo=row.get("repo") or row.get("repository") or "",
                        status=row.get("status") or "unknown",
                        owner=row.get("owner") or self.default_owner,
                    )
                    for row in reader
                ]

        # Fallback to Markdown table parsing
        return self._parse_markdown_table(index_path)

    def fetch_repo(self, repo: str, owner: Optional[str]) -> Dict:
        """Fetch GitHub repo metadata with graceful error handling."""

        target_owner = owner or self.default_owner
        if not target_owner:
            raise ValueError(f"No owner specified for repository '{repo}'")

        url = f"https://api.github.com/repos/{target_owner}/{repo}"
        response = self.session.get(url, timeout=15)
        if response.status_code == 404:
            return {"error": "Repository not found"}
        response.raise_for_status()
        return response.json()

    def evaluate(self, entries: Iterable[PortfolioEntry]) -> List[RepoStatus]:
        """Evaluate each portfolio entry against GitHub."""

        results: List[RepoStatus] = []
        for entry in entries:
            try:
                payload = self.fetch_repo(entry.repo, entry.owner)
                if payload.get("error"):
                    results.append(
                        RepoStatus(
                            entry=entry,
                            exists=False,
                            archived=False,
                            pushed_at=None,
                            default_branch=None,
                            description=None,
                            error=payload.get("error"),
                        )
                    )
                    continue
                pushed_at = (
                    datetime.fromisoformat(payload["pushed_at"].replace("Z", "+00:00"))
                    if payload.get("pushed_at")
                    else None
                )
                results.append(
                    RepoStatus(
                        entry=entry,
                        exists=True,
                        archived=payload.get("archived", False),
                        pushed_at=pushed_at,
                        default_branch=payload.get("default_branch"),
                        description=payload.get("description"),
                        error=None,
                    )
                )
            except requests.HTTPError as exc:
                results.append(
                    RepoStatus(
                        entry=entry,
                        exists=False,
                        archived=False,
                        pushed_at=None,
                        default_branch=None,
                        description=None,
                        error=f"HTTP error: {exc}",
                    )
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    RepoStatus(
                        entry=entry,
                        exists=False,
                        archived=False,
                        pushed_at=None,
                        default_branch=None,
                        description=None,
                        error=str(exc),
                    )
                )
        return results

    @staticmethod
    def to_json(results: Sequence[RepoStatus]) -> str:
        """Serialize results into JSON."""

        serializable = [
            {
                "identifier": result.entry.identifier,
                "name": result.entry.name,
                "repo": result.entry.repo,
                "status": result.entry.status,
                "owner": result.entry.owner,
                "exists": result.exists,
                "archived": result.archived,
                "pushed_at": result.pushed_at.isoformat() if result.pushed_at else None,
                "default_branch": result.default_branch,
                "stale": result.stale,
                "age_days": result.age_days,
                "error": result.error,
            }
            for result in results
        ]
        return json.dumps(serializable, indent=2)

    @staticmethod
    def to_markdown(results: Sequence[RepoStatus]) -> str:
        """Render results as a Markdown table."""

        header = "| ID | Name | Repo | Owner | Exists | Archived | Last Push | Age (days) | Stale | Status | Error |\n"
        separator = "|---|---|---|---|:---:|:---:|---|---|:---:|---|---|\n"
        rows = []
        for result in results:
            pushed = result.pushed_at.isoformat() if result.pushed_at else "N/A"
            rows.append(
                f"| {result.entry.identifier} | {result.entry.name} | {result.entry.repo} | "
                f"{result.entry.owner or '-'} | {'✅' if result.exists else '❌'} | "
                f"{'✅' if result.archived else '❌'} | {pushed} | {result.age_days or 'N/A'} | "
                f"{'⚠️' if result.stale else '✅'} | {result.entry.status} | {result.error or ''} |"
            )
        return "".join([header, separator, "\n".join(rows), "\n"])


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare a Master Portfolio Index against GitHub repositories",
    )
    parser.add_argument("index", type=Path, help="Path to the Master Portfolio Index (json/csv/md)")
    parser.add_argument(
        "--owner",
        dest="owner",
        default=None,
        help="Default GitHub owner or organization for repositories",
    )
    parser.add_argument(
        "--token-env",
        dest="token_env",
        default="GITHUB_TOKEN",
        help="Environment variable containing a GitHub token (default: GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the report instead of stdout",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    token = os.getenv(args.token_env)
    analyzer = PortfolioStatusAnalyzer(token=token, default_owner=args.owner)

    try:
        entries = analyzer.load_portfolio_index(args.index)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Failed to load portfolio index: {exc}\n")
        return 1

    results = analyzer.evaluate(entries)

    if args.format == "markdown":
        report = analyzer.to_markdown(results)
    else:
        report = analyzer.to_json(results)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
