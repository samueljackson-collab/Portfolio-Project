#!/usr/bin/env python3
"""
Portfolio SQLite Database Creator
==================================
Creates a comprehensive SQLite database from all portfolio project data.

Usage:
    python scripts/create_portfolio_db.py [--db portfolio.db] [--root /path/to/portfolio]

Dependencies: stdlib only (sqlite3, pathlib, json, csv, os, re, datetime)
"""

import argparse
import csv
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECTS_DIR_NAMES = ["projects", "projects-new"]

CODE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".sh": "Shell",
    ".bash": "Shell",
    ".tf": "Terraform",
    ".hcl": "Terraform",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".sql": "SQL",
    ".toml": "TOML",
    ".html": "HTML",
    ".css": "CSS",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".sol": "Solidity",
    ".dockerfile": "Docker",
}

DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc"}

INFRA_PATTERNS = {
    "docker": re.compile(r"docker-compose|Dockerfile", re.IGNORECASE),
    "terraform": re.compile(r"\.tf$", re.IGNORECASE),
    "kubernetes": re.compile(r"k8s|kubernetes|\.yaml$|\.yml$", re.IGNORECASE),
    "ansible": re.compile(r"playbook|ansible", re.IGNORECASE),
}


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS projects (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    path            TEXT NOT NULL UNIQUE,
    status          TEXT NOT NULL DEFAULT 'planned',
    completion_pct  REAL NOT NULL DEFAULT 0,
    has_code        INTEGER NOT NULL DEFAULT 0,
    has_docs        INTEGER NOT NULL DEFAULT 0,
    has_tests       INTEGER NOT NULL DEFAULT 0,
    has_demo        INTEGER NOT NULL DEFAULT 0,
    file_count      INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS project_languages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    language    TEXT NOT NULL,
    file_count  INTEGER NOT NULL DEFAULT 1
);
CREATE UNIQUE INDEX IF NOT EXISTS uix_proj_lang ON project_languages(project_id, language);

CREATE TABLE IF NOT EXISTS project_files (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    filename        TEXT NOT NULL,
    file_type       TEXT NOT NULL DEFAULT 'other',
    language        TEXT,
    size_bytes      INTEGER NOT NULL DEFAULT 0,
    relative_path   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_project_files_project ON project_files(project_id);

CREATE TABLE IF NOT EXISTS documentation (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    doc_type    TEXT NOT NULL DEFAULT 'markdown',
    filename    TEXT NOT NULL,
    word_count  INTEGER NOT NULL DEFAULT 0,
    char_count  INTEGER NOT NULL DEFAULT 0,
    path        TEXT NOT NULL UNIQUE,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_docs_project ON documentation(project_id);

CREATE TABLE IF NOT EXISTS wiki_pages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    title           TEXT NOT NULL,
    wiki_path       TEXT NOT NULL UNIQUE,
    tags            TEXT,
    content_preview TEXT,
    source_path     TEXT NOT NULL,
    export_path     TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS github_metadata (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
    repo_url        TEXT,
    branch          TEXT DEFAULT 'main',
    last_commit     TEXT,
    files_pushed    INTEGER DEFAULT 0,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS infrastructure (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
    has_docker      INTEGER NOT NULL DEFAULT 0,
    has_terraform   INTEGER NOT NULL DEFAULT 0,
    has_kubernetes  INTEGER NOT NULL DEFAULT 0,
    has_ansible     INTEGER NOT NULL DEFAULT 0,
    docker_files    INTEGER NOT NULL DEFAULT 0,
    tf_files        INTEGER NOT NULL DEFAULT 0,
    k8s_manifests   INTEGER NOT NULL DEFAULT 0,
    ansible_files   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS completion_tracker (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    week        TEXT,
    action_item TEXT,
    status      TEXT DEFAULT 'pending',
    notes       TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolio_summary (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def count_words(text: str) -> int:
    return len(re.findall(r'\S+', text))


def detect_language(filepath: Path) -> str | None:
    suffix = filepath.suffix.lower()
    if filepath.name.lower() == "dockerfile":
        return "Docker"
    return CODE_EXTENSIONS.get(suffix)


def read_file_safe(path: Path) -> str:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, PermissionError):
            continue
    return ""


def extract_md_title(content: str) -> str:
    """Extract first H1 heading from markdown content."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def make_wiki_path(project_name: str, filename: str) -> str:
    """Generate a clean Wiki.js-compatible path."""
    proj = re.sub(r'[^a-z0-9\-]', '-', project_name.lower()).strip('-')
    name = re.sub(r'[^a-z0-9\-]', '-', filename.lower().replace('.md', '')).strip('-')
    return f"portfolio/{proj}/{name}"


# ---------------------------------------------------------------------------
# Database Builder
# ---------------------------------------------------------------------------

class PortfolioDBBuilder:
    def __init__(self, root: Path, db_path: Path):
        self.root = root
        self.db_path = db_path
        self.conn: sqlite3.Connection = None
        self.stats = {
            "projects": 0,
            "files": 0,
            "docs": 0,
            "wiki_pages": 0,
            "tracker_rows": 0,
        }

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()
        print(f"  Database: {self.db_path}")

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    # ------------------------------------------------------------------
    # Projects from portfolio-metrics.json
    # ------------------------------------------------------------------

    def load_metrics_json(self):
        metrics_file = self.root / "portfolio-metrics.json"
        if not metrics_file.exists():
            print("  WARNING: portfolio-metrics.json not found — skipping metrics load")
            return []

        with open(metrics_file, encoding="utf-8") as f:
            data = json.load(f)

        projects = data.get("project_details", [])
        print(f"  Loaded {len(projects)} projects from portfolio-metrics.json")
        return projects

    def insert_projects(self, projects: list) -> dict[str, int]:
        """Insert projects, return mapping of project name -> db id."""
        cur = self.conn.cursor()
        name_to_id: dict[str, int] = {}
        ts = now_iso()

        for proj in projects:
            name = proj.get("name", "unknown")
            path = proj.get("path", "")
            cur.execute(
                """
                INSERT INTO projects
                    (name, path, status, completion_pct, has_code, has_docs,
                     has_tests, has_demo, file_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    completion_pct=excluded.completion_pct,
                    has_code=excluded.has_code,
                    has_docs=excluded.has_docs,
                    has_tests=excluded.has_tests,
                    has_demo=excluded.has_demo,
                    file_count=excluded.file_count,
                    updated_at=excluded.updated_at
                """,
                (
                    name,
                    path,
                    proj.get("status", "planned"),
                    proj.get("completion", 0),
                    int(proj.get("has_code", False)),
                    int(proj.get("has_docs", False)),
                    int(proj.get("has_tests", False)),
                    int(proj.get("has_demo", False)),
                    proj.get("file_count", 0),
                    ts,
                    ts,
                ),
            )
            proj_id = cur.lastrowid or cur.execute(
                "SELECT id FROM projects WHERE path=?", (path,)
            ).fetchone()[0]
            name_to_id[name] = proj_id
            name_to_id[path] = proj_id

            # Insert languages
            for lang in proj.get("languages", []):
                cur.execute(
                    """
                    INSERT INTO project_languages (project_id, language)
                    VALUES (?, ?)
                    ON CONFLICT(project_id, language) DO UPDATE SET file_count=file_count+1
                    """,
                    (proj_id, lang),
                )

            # Insert github_metadata placeholder
            cur.execute(
                """
                INSERT INTO github_metadata (project_id, updated_at)
                VALUES (?, ?)
                ON CONFLICT(project_id) DO NOTHING
                """,
                (proj_id, ts),
            )

            self.stats["projects"] += 1

        self.conn.commit()
        print(f"  Inserted {self.stats['projects']} projects")
        return name_to_id

    # ------------------------------------------------------------------
    # File scanning
    # ------------------------------------------------------------------

    def _find_project_dir(self, proj_path: str) -> Path | None:
        """Resolve a project path string to an absolute directory."""
        candidate = self.root / proj_path
        if candidate.is_dir():
            return candidate
        # Try stripping leading "projects/" prefix variations
        for parent in PROJECTS_DIR_NAMES:
            candidate = self.root / parent / Path(proj_path).name
            if candidate.is_dir():
                return candidate
        return None

    def scan_project_files(self, projects: list, name_to_id: dict[str, int]):
        """Walk each project directory and record files."""
        cur = self.conn.cursor()
        ts = now_iso()
        total_files = 0

        for proj in projects:
            path_str = proj.get("path", "")
            proj_id = name_to_id.get(proj.get("name")) or name_to_id.get(path_str)
            if not proj_id:
                continue

            proj_dir = self._find_project_dir(path_str)
            if not proj_dir:
                continue

            infra = {
                "has_docker": 0, "has_terraform": 0,
                "has_kubernetes": 0, "has_ansible": 0,
                "docker_files": 0, "tf_files": 0,
                "k8s_manifests": 0, "ansible_files": 0,
            }

            for fpath in proj_dir.rglob("*"):
                if not fpath.is_file():
                    continue
                # Skip hidden dirs
                if any(part.startswith(".") for part in fpath.parts):
                    continue
                if "__pycache__" in str(fpath) or "node_modules" in str(fpath):
                    continue

                rel = fpath.relative_to(proj_dir)
                lang = detect_language(fpath)
                suffix = fpath.suffix.lower()

                # Determine file type
                if suffix in DOC_EXTENSIONS:
                    file_type = "documentation"
                elif lang:
                    file_type = "code"
                else:
                    file_type = "other"

                try:
                    size = fpath.stat().st_size
                except OSError:
                    size = 0

                cur.execute(
                    """
                    INSERT INTO project_files
                        (project_id, filename, file_type, language, size_bytes, relative_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (proj_id, fpath.name, file_type, lang, size, str(rel)),
                )
                total_files += 1

                # Update language counts
                if lang:
                    cur.execute(
                        """
                        INSERT INTO project_languages (project_id, language, file_count)
                        VALUES (?, ?, 1)
                        ON CONFLICT(project_id, language) DO UPDATE SET file_count=file_count+1
                        """,
                        (proj_id, lang),
                    )

                # Infrastructure detection
                fname_lower = fpath.name.lower()
                rel_lower = str(rel).lower()
                if re.search(r'docker', fname_lower):
                    infra["has_docker"] = 1
                    infra["docker_files"] += 1
                if suffix == ".tf":
                    infra["has_terraform"] = 1
                    infra["tf_files"] += 1
                if "k8s" in rel_lower or "kubernetes" in rel_lower:
                    infra["has_kubernetes"] = 1
                    infra["k8s_manifests"] += 1
                if "playbook" in fname_lower or "ansible" in fname_lower:
                    infra["has_ansible"] = 1
                    infra["ansible_files"] += 1

            # Insert infrastructure record
            cur.execute(
                """
                INSERT INTO infrastructure
                    (project_id, has_docker, has_terraform, has_kubernetes, has_ansible,
                     docker_files, tf_files, k8s_manifests, ansible_files)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    has_docker=excluded.has_docker,
                    has_terraform=excluded.has_terraform,
                    has_kubernetes=excluded.has_kubernetes,
                    has_ansible=excluded.has_ansible,
                    docker_files=excluded.docker_files,
                    tf_files=excluded.tf_files,
                    k8s_manifests=excluded.k8s_manifests,
                    ansible_files=excluded.ansible_files
                """,
                (
                    proj_id,
                    infra["has_docker"], infra["has_terraform"],
                    infra["has_kubernetes"], infra["has_ansible"],
                    infra["docker_files"], infra["tf_files"],
                    infra["k8s_manifests"], infra["ansible_files"],
                ),
            )

        self.conn.commit()
        self.stats["files"] = total_files
        print(f"  Scanned {total_files} project files")

    # ------------------------------------------------------------------
    # Documentation indexing
    # ------------------------------------------------------------------

    def index_documentation(self, projects: list, name_to_id: dict[str, int]):
        """Index all markdown/documentation files."""
        cur = self.conn.cursor()
        ts = now_iso()
        total_docs = 0
        total_wiki = 0

        # Also index root-level docs
        all_search_roots: list[tuple[Path, int | None]] = []

        for proj in projects:
            path_str = proj.get("path", "")
            proj_id = name_to_id.get(proj.get("name")) or name_to_id.get(path_str)
            proj_dir = self._find_project_dir(path_str)
            if proj_dir:
                all_search_roots.append((proj_dir, proj_id))

        # Root-level docs (no project association)
        all_search_roots.append((self.root, None))

        seen_paths: set[str] = set()

        for search_dir, proj_id in all_search_roots:
            for fpath in search_dir.rglob("*.md"):
                if not fpath.is_file():
                    continue
                if any(part.startswith(".") for part in fpath.parts):
                    continue
                if "__pycache__" in str(fpath) or "node_modules" in str(fpath):
                    continue

                str_path = str(fpath)
                if str_path in seen_paths:
                    continue
                seen_paths.add(str_path)

                content = read_file_safe(fpath)
                words = count_words(content)
                chars = len(content)

                try:
                    cur.execute(
                        """
                        INSERT INTO documentation
                            (project_id, doc_type, filename, word_count, char_count, path, created_at)
                        VALUES (?, 'markdown', ?, ?, ?, ?, ?)
                        ON CONFLICT(path) DO UPDATE SET
                            word_count=excluded.word_count,
                            char_count=excluded.char_count
                        """,
                        (proj_id, fpath.name, words, chars, str_path, ts),
                    )
                    total_docs += 1
                except sqlite3.Error:
                    pass

                # Create wiki_pages entry
                title = extract_md_title(content) or fpath.stem.replace("-", " ").replace("_", " ").title()
                preview = content[:500].replace("\n", " ")

                if proj_id is not None:
                    proj_name = next(
                        (p["name"] for p in projects if name_to_id.get(p.get("name")) == proj_id),
                        "general"
                    )
                else:
                    proj_name = "general"

                wiki_path = make_wiki_path(proj_name, fpath.stem)

                try:
                    cur.execute(
                        """
                        INSERT INTO wiki_pages
                            (project_id, title, wiki_path, tags, content_preview, source_path, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(wiki_path) DO UPDATE SET
                            title=excluded.title,
                            content_preview=excluded.content_preview
                        """,
                        (proj_id, title, wiki_path, proj_name, preview, str_path, ts),
                    )
                    total_wiki += 1
                except sqlite3.Error:
                    pass

        self.conn.commit()
        self.stats["docs"] = total_docs
        self.stats["wiki_pages"] = total_wiki
        print(f"  Indexed {total_docs} documentation files")
        print(f"  Generated {total_wiki} wiki page entries")

    # ------------------------------------------------------------------
    # CSV completion tracker
    # ------------------------------------------------------------------

    def load_completion_tracker(self, name_to_id: dict[str, int]):
        """Load Portfolio_Completion_Tracker CSV files."""
        tracker_dir = self.root / "Portfolio_Completion_Tracker"
        if not tracker_dir.exists():
            print("  WARNING: Portfolio_Completion_Tracker directory not found")
            return

        cur = self.conn.cursor()
        ts = now_iso()
        total = 0

        for csv_file in tracker_dir.glob("*.csv"):
            try:
                with open(csv_file, encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Normalize field names (handle varying column headers)
                        action = (
                            row.get("Action Item")
                            or row.get("action_item")
                            or row.get("Task")
                            or row.get("Item")
                            or str(row)[:200]
                        )
                        status = (
                            row.get("Status")
                            or row.get("status")
                            or "pending"
                        )
                        week = (
                            row.get("Week")
                            or row.get("week")
                            or row.get("Date")
                            or ""
                        )
                        notes = (
                            row.get("Notes")
                            or row.get("notes")
                            or row.get("Comments")
                            or ""
                        )

                        cur.execute(
                            """
                            INSERT INTO completion_tracker
                                (week, action_item, status, notes, created_at)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (week, action, status, notes, ts),
                        )
                        total += 1
            except Exception as e:
                print(f"  WARNING: Could not parse {csv_file.name}: {e}")

        self.conn.commit()
        self.stats["tracker_rows"] = total
        print(f"  Loaded {total} completion tracker rows from CSVs")

    # ------------------------------------------------------------------
    # Portfolio summary
    # ------------------------------------------------------------------

    def write_portfolio_summary(self, metrics_data: dict):
        cur = self.conn.cursor()
        ts = now_iso()

        summary = {
            "generated_at": ts,
            "total_projects": str(metrics_data.get("projects", {}).get("total", self.stats["projects"])),
            "overall_completion_pct": str(metrics_data.get("overall_completion", 0)),
            "projects_with_code": str(metrics_data.get("projects", {}).get("with_code", 0)),
            "projects_with_docs": str(metrics_data.get("projects", {}).get("with_docs", 0)),
            "projects_with_tests": str(metrics_data.get("projects", {}).get("with_tests", 0)),
            "total_markdown_files": str(self.stats["docs"]),
            "total_wiki_pages": str(self.stats["wiki_pages"]),
            "total_project_files": str(self.stats["files"]),
            "total_tracker_rows": str(self.stats["tracker_rows"]),
            "docker_compose_files": str(metrics_data.get("infrastructure", {}).get("docker_compose_files", 0)),
            "terraform_files": str(metrics_data.get("infrastructure", {}).get("terraform_files", 0)),
            "kubernetes_manifests": str(metrics_data.get("infrastructure", {}).get("kubernetes_manifests", 0)),
            "readme_files": str(metrics_data.get("documentation", {}).get("readme_files", 0)),
            "total_words": str(metrics_data.get("documentation", {}).get("total_words", 0)),
        }

        for key, value in summary.items():
            cur.execute(
                """
                INSERT INTO portfolio_summary (key, value, updated_at) VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """,
                (key, value, ts),
            )

        self.conn.commit()
        print(f"  Wrote {len(summary)} portfolio summary entries")

    # ------------------------------------------------------------------
    # Main build
    # ------------------------------------------------------------------

    def build(self):
        print("\n=== Portfolio SQLite DB Builder ===\n")
        self.connect()

        # Load metrics JSON
        metrics_data = {}
        metrics_file = self.root / "portfolio-metrics.json"
        if metrics_file.exists():
            with open(metrics_file, encoding="utf-8") as f:
                metrics_data = json.load(f)

        projects = metrics_data.get("project_details", [])

        # Also discover any project dirs not in metrics
        discovered = self._discover_extra_projects(projects)
        if discovered:
            print(f"  Discovered {len(discovered)} additional projects not in metrics")
            projects = projects + discovered

        print(f"\n[1/5] Inserting {len(projects)} projects...")
        name_to_id = self.insert_projects(projects)

        print("\n[2/5] Scanning project files...")
        self.scan_project_files(projects, name_to_id)

        print("\n[3/5] Indexing documentation...")
        self.index_documentation(projects, name_to_id)

        print("\n[4/5] Loading completion tracker CSVs...")
        self.load_completion_tracker(name_to_id)

        print("\n[5/5] Writing portfolio summary...")
        self.write_portfolio_summary(metrics_data)

        self.close()
        self._print_summary()

    def _discover_extra_projects(self, existing: list) -> list:
        """Find project directories not already in the metrics."""
        existing_paths = {p.get("path", "") for p in existing}
        extras = []
        ts = now_iso()

        for parent_name in PROJECTS_DIR_NAMES:
            parent = self.root / parent_name
            if not parent.is_dir():
                continue
            for child in sorted(parent.iterdir()):
                if not child.is_dir():
                    continue
                rel = f"{parent_name}/{child.name}"
                if rel in existing_paths:
                    continue
                extras.append({
                    "name": child.name,
                    "path": rel,
                    "status": "planned",
                    "completion": 0,
                    "has_code": any(
                        f.suffix.lower() in CODE_EXTENSIONS
                        for f in child.rglob("*") if f.is_file()
                    ),
                    "has_docs": any(
                        f.suffix.lower() in DOC_EXTENSIONS
                        for f in child.rglob("*") if f.is_file()
                    ),
                    "has_tests": any(
                        "test" in f.name.lower()
                        for f in child.rglob("*") if f.is_file()
                    ),
                    "has_demo": False,
                    "file_count": sum(1 for _ in child.rglob("*") if _.is_file()),
                    "languages": [],
                })
        return extras

    def _print_summary(self):
        print("\n=== Build Complete ===")
        print(f"  DB Path:       {self.db_path}")
        print(f"  DB Size:       {self.db_path.stat().st_size / 1024:.1f} KB")
        print(f"  Projects:      {self.stats['projects']}")
        print(f"  Files:         {self.stats['files']}")
        print(f"  Docs:          {self.stats['docs']}")
        print(f"  Wiki Pages:    {self.stats['wiki_pages']}")
        print(f"  Tracker Rows:  {self.stats['tracker_rows']}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Create Portfolio SQLite Database")
    parser.add_argument(
        "--db",
        default="portfolio.db",
        help="Output SQLite database path (default: portfolio.db)",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Portfolio root directory (default: current directory)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = root / db_path

    if not root.exists():
        print(f"ERROR: Root directory not found: {root}", file=sys.stderr)
        sys.exit(1)

    builder = PortfolioDBBuilder(root=root, db_path=db_path)
    builder.build()


if __name__ == "__main__":
    main()
