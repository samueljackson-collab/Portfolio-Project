#!/usr/bin/env python3
"""
Portfolio Master Export Orchestrator
======================================
Runs the full export pipeline:
  1. Creates/refreshes the SQLite portfolio database
  2. Updates portfolio-metrics.json with fresh filesystem scan
  3. Prepares wiki-export/ directory for Wiki.js import
  4. Generates PORTFOLIO_INDEX.md linking all projects
  5. Generates missing per-project SUMMARY.md files

Usage:
    python scripts/export_portfolio.py [--root .] [--db portfolio.db]
    python scripts/export_portfolio.py --skip-db --skip-metrics
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def read_file_safe(path: Path) -> str:
    for enc in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, PermissionError):
            continue
    return ""


def count_words(text: str) -> int:
    return len(re.findall(r'\S+', text))


def extract_md_title(content: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


CODE_EXTENSIONS = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".go": "Go", ".rs": "Rust", ".java": "Java",
    ".sh": "Shell", ".bash": "Shell", ".tf": "Terraform",
    ".hcl": "Terraform", ".yaml": "YAML", ".yml": "YAML",
    ".json": "JSON", ".sql": "SQL", ".toml": "TOML",
    ".html": "HTML", ".css": "CSS", ".tsx": "TypeScript",
    ".jsx": "JavaScript", ".sol": "Solidity",
}

PROJECTS_DIR_NAMES = ["projects", "projects-new"]


# ---------------------------------------------------------------------------
# Step 1: Run SQLite DB creation
# ---------------------------------------------------------------------------

def run_db_creation(root: Path, db_path: Path) -> bool:
    script = root / "scripts" / "create_portfolio_db.py"
    if not script.exists():
        print(f"  WARNING: {script} not found — skipping DB creation")
        return False

    print(f"  Running: python {script} --root {root} --db {db_path}")
    result = subprocess.run(
        [sys.executable, str(script), "--root", str(root), "--db", str(db_path)],
        capture_output=False,
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Step 2: Refresh portfolio-metrics.json
# ---------------------------------------------------------------------------

def refresh_metrics(root: Path) -> dict:
    """Scan the filesystem and produce an updated metrics dict."""
    print("  Scanning filesystem for fresh metrics...")

    metrics = {
        "timestamp": now_iso(),
        "overall_completion": 0.0,
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

    # Count infrastructure files globally
    for fpath in root.rglob("*"):
        if not fpath.is_file():
            continue
        if any(p.startswith(".") for p in fpath.parts):
            continue
        name = fpath.name.lower()
        suffix = fpath.suffix.lower()
        if "docker-compose" in name:
            metrics["infrastructure"]["docker_compose_files"] += 1
        if suffix == ".tf":
            metrics["infrastructure"]["terraform_files"] += 1
        if suffix in (".yaml", ".yml") and any(
            k in str(fpath).lower() for k in ("k8s", "kubernetes", "manifest")
        ):
            metrics["infrastructure"]["kubernetes_manifests"] += 1
        if suffix in (".md", ".markdown"):
            metrics["documentation"]["markdown_files"] += 1
            content = read_file_safe(fpath)
            metrics["documentation"]["total_words"] += count_words(content)
            if fpath.name.lower() == "readme.md":
                metrics["documentation"]["readme_files"] += 1

    # Scan project directories
    seen_names: set[str] = set()
    project_details = []

    for parent_name in PROJECTS_DIR_NAMES:
        parent = root / parent_name
        if not parent.is_dir():
            continue

        for proj_dir in sorted(parent.iterdir()):
            if not proj_dir.is_dir():
                continue
            if proj_dir.name.startswith("."):
                continue

            proj_name = proj_dir.name
            if proj_name in seen_names:
                continue
            seen_names.add(proj_name)

            rel_path = f"{parent_name}/{proj_name}"
            files = [f for f in proj_dir.rglob("*") if f.is_file()
                     and not any(p.startswith(".") for p in f.parts)
                     and "__pycache__" not in str(f)
                     and "node_modules" not in str(f)]

            has_code = any(f.suffix.lower() in CODE_EXTENSIONS for f in files)
            has_docs = any(f.suffix.lower() in (".md", ".rst") for f in files)
            has_tests = any("test" in f.name.lower() for f in files)

            # Detect languages
            lang_set: set[str] = set()
            for f in files:
                lang = CODE_EXTENSIONS.get(f.suffix.lower())
                if lang:
                    lang_set.add(lang)

            # Estimate completion
            score = 0
            if has_code:
                score += 40
            if has_docs:
                score += 30
            if has_tests:
                score += 20
            if len(files) > 20:
                score += 10

            detail = {
                "name": proj_name,
                "path": rel_path,
                "has_code": has_code,
                "has_docs": has_docs,
                "has_tests": has_tests,
                "has_demo": False,
                "status": "planned",
                "completion": min(score, 100),
                "file_count": len(files),
                "languages": sorted(lang_set),
            }
            project_details.append(detail)

            # Aggregate
            metrics["projects"]["total"] += 1
            metrics["projects"]["planned"] += 1
            if has_code:
                metrics["projects"]["with_code"] += 1
            if has_docs:
                metrics["projects"]["with_docs"] += 1
            if has_tests:
                metrics["projects"]["with_tests"] += 1

    metrics["project_details"] = project_details

    # Overall completion
    if project_details:
        avg = sum(p["completion"] for p in project_details) / len(project_details)
        metrics["overall_completion"] = round(avg, 1)

    # Write back
    out_file = root / "portfolio-metrics.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"  Updated {out_file} ({metrics['projects']['total']} projects, "
          f"{metrics['documentation']['markdown_files']} docs)")
    return metrics


# ---------------------------------------------------------------------------
# Step 3: Prepare wiki-export/ directory
# ---------------------------------------------------------------------------

WIKIJS_FRONTMATTER_TEMPLATE = """\
---
title: {title}
description: {description}
tags: [{tags}]
created: {created}
updated: {updated}
wiki_path: {wiki_path}
---

"""


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9\-]', '-', text.lower()).strip('-')


def prepare_wikijs_export(root: Path, metrics: dict):
    """Copy all markdown docs into wiki-export/ with proper frontmatter."""
    export_dir = root / "wiki-export"
    export_dir.mkdir(exist_ok=True)

    manifest = {
        "generated_at": now_iso(),
        "pages": [],
    }

    ts = now_iso()
    total = 0

    for proj_detail in metrics.get("project_details", []):
        proj_name = proj_detail["name"]
        proj_path_str = proj_detail["path"]
        proj_dir = root / proj_path_str

        if not proj_dir.is_dir():
            continue

        proj_slug = slugify(proj_name)
        proj_export_dir = export_dir / "portfolio" / proj_slug
        proj_export_dir.mkdir(parents=True, exist_ok=True)

        for md_file in proj_dir.rglob("*.md"):
            if not md_file.is_file():
                continue
            if any(p.startswith(".") for p in md_file.parts):
                continue

            content = read_file_safe(md_file)
            title = extract_md_title(content) or md_file.stem.replace("-", " ").replace("_", " ").title()

            # Strip existing frontmatter
            if content.startswith("---"):
                end = content.find("---", 3)
                if end != -1:
                    content = content[end + 3:].lstrip()

            file_slug = slugify(md_file.stem)
            wiki_path = f"portfolio/{proj_slug}/{file_slug}"
            out_file = proj_export_dir / f"{file_slug}.md"

            frontmatter = WIKIJS_FRONTMATTER_TEMPLATE.format(
                title=title,
                description=f"Documentation for {proj_name}",
                tags=f"{proj_slug}, portfolio, documentation",
                created=ts,
                updated=ts,
                wiki_path=wiki_path,
            )

            out_file.write_text(frontmatter + content, encoding="utf-8")
            total += 1

            manifest["pages"].append({
                "title": title,
                "wiki_path": wiki_path,
                "source": str(md_file.relative_to(root)),
                "export": str(out_file.relative_to(root)),
                "project": proj_name,
            })

    # Also export root-level docs
    root_export_dir = export_dir / "portfolio" / "general"
    root_export_dir.mkdir(parents=True, exist_ok=True)

    for md_file in root.glob("*.md"):
        if not md_file.is_file():
            continue
        content = read_file_safe(md_file)
        title = extract_md_title(content) or md_file.stem.replace("-", " ").replace("_", " ").title()

        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                content = content[end + 3:].lstrip()

        file_slug = slugify(md_file.stem)
        wiki_path = f"portfolio/general/{file_slug}"
        out_file = root_export_dir / f"{file_slug}.md"

        frontmatter = WIKIJS_FRONTMATTER_TEMPLATE.format(
            title=title,
            description="Portfolio general documentation",
            tags="portfolio, general, documentation",
            created=ts,
            updated=ts,
            wiki_path=wiki_path,
        )
        out_file.write_text(frontmatter + content, encoding="utf-8")
        total += 1
        manifest["pages"].append({
            "title": title,
            "wiki_path": wiki_path,
            "source": str(md_file.relative_to(root)),
            "export": str(out_file.relative_to(root)),
            "project": "general",
        })

    manifest["total_pages"] = total

    manifest_path = export_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Write import helper script
    import_helper = export_dir / "run-import.sh"
    import_helper.write_text(
        "#!/bin/bash\n"
        "# Run this to import all pages into Wiki.js\n"
        "# Set WIKIJS_URL and WIKIJS_TOKEN environment variables first\n\n"
        "set -e\n"
        'WIKIJS_URL="${WIKIJS_URL:-http://localhost:3000}"\n'
        'WIKIJS_TOKEN="${WIKIJS_TOKEN:?WIKIJS_TOKEN must be set}"\n\n'
        "cd \"$(dirname \"$0\")/..\"\n"
        "WIKIJS_URL=\"$WIKIJS_URL\" WIKIJS_TOKEN=\"$WIKIJS_TOKEN\" \\\n"
        "  node wiki-js-scaffold/scripts/import-to-wikijs.js\n",
        encoding="utf-8",
    )
    import_helper.chmod(0o755)

    print(f"  Prepared {total} wiki pages in wiki-export/")
    print(f"  Manifest: {manifest_path}")
    return manifest


# ---------------------------------------------------------------------------
# Step 4: Generate PORTFOLIO_INDEX.md
# ---------------------------------------------------------------------------

def generate_portfolio_index(root: Path, metrics: dict):
    """Generate a comprehensive PORTFOLIO_INDEX.md."""
    projects = metrics.get("project_details", [])
    summary = metrics.get("projects", {})

    lines = [
        "# Portfolio Index",
        "",
        f"> Generated: {now_str()}",
        "",
        "## Overview",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Projects | {summary.get('total', len(projects))} |",
        f"| Overall Completion | {metrics.get('overall_completion', 0):.1f}% |",
        f"| Projects with Code | {summary.get('with_code', 0)} |",
        f"| Projects with Docs | {summary.get('with_docs', 0)} |",
        f"| Projects with Tests | {summary.get('with_tests', 0)} |",
        f"| Markdown Files | {metrics.get('documentation', {}).get('markdown_files', 0)} |",
        f"| Total Words | {metrics.get('documentation', {}).get('total_words', 0):,} |",
        f"| Terraform Files | {metrics.get('infrastructure', {}).get('terraform_files', 0)} |",
        f"| Docker Compose Files | {metrics.get('infrastructure', {}).get('docker_compose_files', 0)} |",
        "",
        "## Projects",
        "",
        "| # | Project | Status | Completion | Code | Docs | Tests | Languages |",
        "|---|---------|--------|-----------|------|------|-------|-----------|",
    ]

    for i, proj in enumerate(sorted(projects, key=lambda p: p.get("name", "")), 1):
        name = proj.get("name", "unknown")
        status = proj.get("status", "planned")
        pct = proj.get("completion", 0)
        code = "✅" if proj.get("has_code") else "❌"
        docs = "✅" if proj.get("has_docs") else "❌"
        tests = "✅" if proj.get("has_tests") else "❌"
        langs = ", ".join(proj.get("languages", [])[:3])
        path = proj.get("path", "")

        lines.append(
            f"| {i} | [{name}]({path}/README.md) | {status} | {pct}% | {code} | {docs} | {tests} | {langs} |"
        )

    lines += [
        "",
        "## Quick Links",
        "",
        "- [Portfolio Metrics](portfolio-metrics.json)",
        "- [Portfolio DB](portfolio.db)",
        "- [Wiki Export](wiki-export/manifest.json)",
        "- [Completion Tracker](Portfolio_Completion_Tracker/)",
        "- [Documentation Index](DOCUMENTATION_INDEX.md)",
        "- [Executive Summary](EXECUTIVE_SUMMARY.md)",
        "",
        "## Database",
        "",
        "The portfolio database (`portfolio.db`) contains:",
        "",
        "```sql",
        "-- Query all projects",
        "SELECT name, completion_pct, has_code, has_docs FROM projects ORDER BY completion_pct DESC;",
        "",
        "-- Query top documented projects",
        "SELECT p.name, COUNT(d.id) as doc_count, SUM(d.word_count) as words",
        "FROM projects p LEFT JOIN documentation d ON d.project_id = p.id",
        "GROUP BY p.id ORDER BY words DESC LIMIT 10;",
        "",
        "-- Infrastructure summary",
        "SELECT p.name, i.has_docker, i.has_terraform, i.has_kubernetes",
        "FROM projects p JOIN infrastructure i ON i.project_id = p.id",
        "WHERE i.has_docker=1 OR i.has_terraform=1;",
        "```",
        "",
    ]

    out_path = root / "PORTFOLIO_INDEX.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Generated {out_path} ({len(projects)} projects listed)")


# ---------------------------------------------------------------------------
# Step 5: Generate missing per-project SUMMARY.md files
# ---------------------------------------------------------------------------

SUMMARY_TEMPLATE = """\
# {name} — Project Summary

> Status: {status} | Completion: {completion}% | Generated: {date}

## Overview

{name} is part of the enterprise portfolio, covering {categories}.

## Technologies

{languages_list}

## Files

| Type | Count |
|------|-------|
| Total Files | {file_count} |
| Has Code | {has_code} |
| Has Tests | {has_tests} |

## Documentation

See [README.md](README.md) for full project documentation.

## Infrastructure

{infra_notes}

---
*This file is auto-generated by the portfolio export pipeline.*
"""


def generate_missing_summaries(root: Path, metrics: dict):
    """Create SUMMARY.md for projects that don't have one."""
    projects = metrics.get("project_details", [])
    generated = 0

    for proj in projects:
        proj_path = root / proj.get("path", "")
        if not proj_path.is_dir():
            continue

        summary_file = proj_path / "SUMMARY.md"
        if summary_file.exists():
            continue

        name = proj.get("name", "unknown")
        langs = proj.get("languages", [])
        languages_list = "\n".join(f"- {l}" for l in langs) if langs else "- (not yet detected)"

        # Determine category from name
        categories = "cloud infrastructure, DevOps, and security"
        if any(k in name.lower() for k in ("k8s", "kubernetes", "kube")):
            categories = "Kubernetes and container orchestration"
        elif any(k in name.lower() for k in ("aws", "azure", "gcp", "cloud")):
            categories = "cloud infrastructure and IaC"
        elif any(k in name.lower() for k in ("security", "soc", "zero-trust", "cyber")):
            categories = "cybersecurity and threat detection"
        elif any(k in name.lower() for k in ("ml", "ai", "mlops", "quantum")):
            categories = "machine learning and AI operations"
        elif any(k in name.lower() for k in ("data", "pipeline", "lake", "stream")):
            categories = "data engineering and pipelines"
        elif any(k in name.lower() for k in ("blockchain", "crypto", "oracle")):
            categories = "blockchain and distributed ledger technology"

        infra = []
        if proj_path.joinpath("docker-compose.yml").exists() or list(proj_path.glob("docker-compose*")):
            infra.append("Docker Compose")
        if list(proj_path.rglob("*.tf")):
            infra.append("Terraform")
        if any(proj_path.joinpath(d).is_dir() for d in ("k8s", "kubernetes")):
            infra.append("Kubernetes")
        infra_notes = "\n".join(f"- {i}" for i in infra) if infra else "- Standard project structure"

        content = SUMMARY_TEMPLATE.format(
            name=name,
            status=proj.get("status", "planned"),
            completion=proj.get("completion", 0),
            date=datetime.now().strftime("%Y-%m-%d"),
            categories=categories,
            languages_list=languages_list,
            file_count=proj.get("file_count", 0),
            has_code="Yes" if proj.get("has_code") else "No",
            has_tests="Yes" if proj.get("has_tests") else "No",
            infra_notes=infra_notes,
        )

        summary_file.write_text(content, encoding="utf-8")
        generated += 1

    print(f"  Generated {generated} missing SUMMARY.md files")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Portfolio Master Export Orchestrator")
    parser.add_argument("--root", default=".", help="Portfolio root directory")
    parser.add_argument("--db", default="portfolio.db", help="SQLite DB output path")
    parser.add_argument("--skip-db", action="store_true", help="Skip DB creation")
    parser.add_argument("--skip-metrics", action="store_true", help="Skip metrics refresh")
    parser.add_argument("--skip-wiki", action="store_true", help="Skip wiki export")
    parser.add_argument("--skip-index", action="store_true", help="Skip index generation")
    parser.add_argument("--skip-summaries", action="store_true", help="Skip summary generation")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = root / db_path

    print(f"\n{'='*60}")
    print(f"  Portfolio Export Orchestrator")
    print(f"  Root: {root}")
    print(f"  DB:   {db_path}")
    print(f"  Time: {now_str()}")
    print(f"{'='*60}\n")

    # Step 1: Create/refresh SQLite DB
    if not args.skip_db:
        print("[STEP 1/5] Creating SQLite portfolio database...")
        success = run_db_creation(root, db_path)
        if not success:
            print("  WARNING: DB creation had errors — continuing with other steps")
    else:
        print("[STEP 1/5] Skipping DB creation (--skip-db)")

    # Step 2: Refresh metrics
    if not args.skip_metrics:
        print("\n[STEP 2/5] Refreshing portfolio-metrics.json...")
        metrics = refresh_metrics(root)
    else:
        print("\n[STEP 2/5] Loading existing portfolio-metrics.json...")
        metrics_file = root / "portfolio-metrics.json"
        if metrics_file.exists():
            with open(metrics_file, encoding="utf-8") as f:
                metrics = json.load(f)
        else:
            print("  WARNING: No metrics file found, using empty metrics")
            metrics = {"project_details": [], "projects": {}}

    # Step 3: Prepare Wiki.js export
    if not args.skip_wiki:
        print("\n[STEP 3/5] Preparing Wiki.js export directory...")
        prepare_wikijs_export(root, metrics)
    else:
        print("\n[STEP 3/5] Skipping wiki export (--skip-wiki)")

    # Step 4: Generate PORTFOLIO_INDEX.md
    if not args.skip_index:
        print("\n[STEP 4/5] Generating PORTFOLIO_INDEX.md...")
        generate_portfolio_index(root, metrics)
    else:
        print("\n[STEP 4/5] Skipping index generation (--skip-index)")

    # Step 5: Generate missing SUMMARY.md files
    if not args.skip_summaries:
        print("\n[STEP 5/5] Generating missing per-project SUMMARY.md files...")
        generate_missing_summaries(root, metrics)
    else:
        print("\n[STEP 5/5] Skipping summary generation (--skip-summaries)")

    print(f"\n{'='*60}")
    print("  Export pipeline complete!")
    print(f"  Portfolio DB:     {db_path}")
    print(f"  Wiki Export:      {root / 'wiki-export'}")
    print(f"  Portfolio Index:  {root / 'PORTFOLIO_INDEX.md'}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
