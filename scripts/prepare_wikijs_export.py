#!/usr/bin/env python3
"""
Wiki.js Batch Export Preparation Script
=========================================
Reads all markdown files from every project directory, adds/normalizes
YAML frontmatter, structures content into wiki-export/ directory, and
generates a manifest for the existing import-to-wikijs.js script.

Usage:
    python scripts/prepare_wikijs_export.py [--root .] [--out wiki-export]
    python scripts/prepare_wikijs_export.py --dry-run
    python scripts/prepare_wikijs_export.py --show-manifest

After running, import with:
    WIKIJS_URL=http://localhost:3000 WIKIJS_TOKEN=<token> \\
      node wiki-js-scaffold/scripts/import-to-wikijs.js

Dependencies: stdlib only
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECTS_DIR_NAMES = ["projects", "projects-new"]

# Directories to skip during scanning
SKIP_DIRS = {
    ".git", ".github", "node_modules", "__pycache__", ".pytest_cache",
    "venv", ".venv", "env", ".env", "dist", "build", ".tox",
    "wiki-export",  # avoid re-processing exports
}

# Default tags per project name keyword
CATEGORY_TAGS = {
    "aws": ["aws", "cloud", "infrastructure"],
    "k8s": ["kubernetes", "containers", "orchestration"],
    "kubernetes": ["kubernetes", "containers", "orchestration"],
    "security": ["security", "devsecops", "compliance"],
    "soc": ["security", "soc", "monitoring"],
    "zero-trust": ["security", "zero-trust", "network"],
    "ml": ["machine-learning", "ai", "mlops"],
    "mlops": ["machine-learning", "mlops", "python"],
    "data": ["data-engineering", "pipeline", "analytics"],
    "blockchain": ["blockchain", "web3", "solidity"],
    "quantum": ["quantum-computing", "cryptography"],
    "terraform": ["terraform", "iac", "cloud"],
    "cicd": ["cicd", "devops", "automation"],
    "monitoring": ["monitoring", "observability", "grafana"],
    "iot": ["iot", "edge", "streaming"],
    "gpu": ["gpu", "cuda", "high-performance"],
}


# ---------------------------------------------------------------------------
# Frontmatter handling
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9\-]', '-', text.lower()).strip('-')


def strip_frontmatter(content: str) -> tuple[dict, str]:
    """Strip YAML frontmatter from markdown content. Returns (meta_dict, body)."""
    meta = {}
    if not content.startswith("---"):
        return meta, content

    end = content.find("\n---", 3)
    if end == -1:
        end = content.find("---", 3)
        if end == -1:
            return meta, content

    frontmatter_text = content[3:end].strip()
    body = content[end + 3:].lstrip("\n")

    # Simple YAML key:value parsing (no full YAML parser needed)
    for line in frontmatter_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            meta[key] = val

    return meta, body


def build_frontmatter(title: str, description: str, tags: list[str],
                      wiki_path: str, created: str, updated: str) -> str:
    tags_yaml = ", ".join(tags)
    return (
        "---\n"
        f"title: {title}\n"
        f"description: {description}\n"
        f"tags: [{tags_yaml}]\n"
        f"path: {wiki_path}\n"
        f"created: {created}\n"
        f"updated: {updated}\n"
        "---\n\n"
    )


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def get_description(content: str, max_chars: int = 200) -> str:
    """Extract first meaningful paragraph as description."""
    in_frontmatter = False
    lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if stripped.startswith("#"):
            continue
        if stripped and not stripped.startswith("```") and not stripped.startswith("|"):
            lines.append(stripped)
            if len(" ".join(lines)) >= max_chars:
                break
    desc = " ".join(lines)[:max_chars]
    return desc.replace('"', "'") if desc else "Portfolio documentation page"


def get_tags_for_project(project_name: str, base_tags: list[str] = None) -> list[str]:
    tags = set(base_tags or [])
    tags.add("portfolio")
    tags.add("documentation")
    proj_lower = project_name.lower()
    for keyword, keyword_tags in CATEGORY_TAGS.items():
        if keyword in proj_lower:
            tags.update(keyword_tags)
    return sorted(tags)


# ---------------------------------------------------------------------------
# File reading
# ---------------------------------------------------------------------------

def read_file_safe(path: Path) -> str:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, PermissionError):
            continue
    return ""


# ---------------------------------------------------------------------------
# Wiki page builder
# ---------------------------------------------------------------------------

class WikiPage:
    def __init__(self, source_path: Path, root: Path, project_name: str, wiki_path: str):
        self.source_path = source_path
        self.root = root
        self.project_name = project_name
        self.wiki_path = wiki_path
        self.title = ""
        self.description = ""
        self.tags: list[str] = []
        self.content = ""
        self.created = datetime.now(timezone.utc).isoformat()
        self.updated = self.created

    def load(self) -> bool:
        raw = read_file_safe(self.source_path)
        if not raw.strip():
            return False

        meta, body = strip_frontmatter(raw)

        # Try to get file modification time
        try:
            mtime = self.source_path.stat().st_mtime
            self.updated = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        except OSError:
            pass

        fallback_title = (
            self.source_path.stem.replace("-", " ").replace("_", " ").title()
        )
        self.title = meta.get("title") or extract_title(body, fallback_title)
        self.description = meta.get("description") or get_description(body)
        self.tags = get_tags_for_project(
            self.project_name,
            base_tags=[t.strip() for t in meta.get("tags", "").strip("[]").split(",") if t.strip()],
        )
        self.content = body
        return True

    def to_markdown(self) -> str:
        frontmatter = build_frontmatter(
            title=self.title,
            description=self.description,
            tags=self.tags,
            wiki_path=self.wiki_path,
            created=self.created,
            updated=self.updated,
        )
        return frontmatter + self.content

    def to_manifest_entry(self, export_path: str) -> dict:
        return {
            "title": self.title,
            "path": self.wiki_path,
            "description": self.description,
            "tags": self.tags,
            "source": str(self.source_path.relative_to(self.root)),
            "export": export_path,
            "project": self.project_name,
            "created": self.created,
            "updated": self.updated,
        }


# ---------------------------------------------------------------------------
# Main exporter
# ---------------------------------------------------------------------------

class WikiJsExportPreparer:
    def __init__(self, root: Path, output_dir: Path, dry_run: bool = False):
        self.root = root
        self.output_dir = output_dir
        self.dry_run = dry_run
        self.pages: list[WikiPage] = []
        self.skipped = 0
        self.errors = 0

    def _should_skip_dir(self, path: Path) -> bool:
        return path.name in SKIP_DIRS or path.name.startswith(".")

    def _scan_project(self, proj_dir: Path, project_name: str):
        for md_file in proj_dir.rglob("*.md"):
            if not md_file.is_file():
                continue
            # Skip if inside a skip dir
            if any(self._should_skip_dir(Path(p)) for p in md_file.parts):
                continue

            proj_slug = slugify(project_name)
            file_slug = slugify(md_file.stem)
            wiki_path = f"portfolio/{proj_slug}/{file_slug}"

            page = WikiPage(
                source_path=md_file,
                root=self.root,
                project_name=project_name,
                wiki_path=wiki_path,
            )
            if page.load():
                self.pages.append(page)
            else:
                self.skipped += 1

    def _scan_root_docs(self):
        """Scan top-level markdown files."""
        for md_file in self.root.glob("*.md"):
            if not md_file.is_file():
                continue
            file_slug = slugify(md_file.stem)
            wiki_path = f"portfolio/general/{file_slug}"
            page = WikiPage(
                source_path=md_file,
                root=self.root,
                project_name="general",
                wiki_path=wiki_path,
            )
            if page.load():
                self.pages.append(page)
            else:
                self.skipped += 1

        # Also scan docs/ directory
        docs_dir = self.root / "docs"
        if docs_dir.is_dir():
            for md_file in docs_dir.rglob("*.md"):
                if not md_file.is_file():
                    continue
                rel = md_file.relative_to(docs_dir)
                parts = [slugify(p) for p in rel.parts[:-1]]
                file_slug = slugify(md_file.stem)
                path_parts = ["portfolio", "docs"] + parts + [file_slug]
                wiki_path = "/".join(path_parts)
                page = WikiPage(
                    source_path=md_file,
                    root=self.root,
                    project_name="docs",
                    wiki_path=wiki_path,
                )
                if page.load():
                    self.pages.append(page)
                else:
                    self.skipped += 1

    def scan(self):
        print(f"  Scanning {self.root} for markdown files...")

        # Scan project directories
        for parent_name in PROJECTS_DIR_NAMES:
            parent = self.root / parent_name
            if not parent.is_dir():
                continue
            for proj_dir in sorted(parent.iterdir()):
                if not proj_dir.is_dir() or self._should_skip_dir(proj_dir):
                    continue
                self._scan_project(proj_dir, proj_dir.name)

        # Scan root docs
        self._scan_root_docs()

        # Deduplicate by wiki_path (keep last encountered)
        seen: dict[str, WikiPage] = {}
        for page in self.pages:
            seen[page.wiki_path] = page
        self.pages = list(seen.values())

        print(f"  Found {len(self.pages)} pages ({self.skipped} skipped, {self.errors} errors)")

    def export(self) -> dict:
        if not self.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_pages": len(self.pages),
            "wikijs_import_command": (
                "WIKIJS_URL=http://localhost:3000 WIKIJS_TOKEN=<token> "
                "node wiki-js-scaffold/scripts/import-to-wikijs.js"
            ),
            "pages": [],
        }

        written = 0
        for page in self.pages:
            # Determine output file path
            parts = page.wiki_path.split("/")
            out_path = self.output_dir.joinpath(*parts).with_suffix(".md")

            if not self.dry_run:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    out_path.write_text(page.to_markdown(), encoding="utf-8")
                    written += 1
                except OSError as e:
                    print(f"  ERROR writing {out_path}: {e}")
                    self.errors += 1
                    continue
            else:
                written += 1

            rel_export = str(out_path.relative_to(self.root)) if not self.dry_run else str(out_path)
            manifest["pages"].append(page.to_manifest_entry(rel_export))

        if not self.dry_run:
            # Write manifest
            manifest_path = self.output_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            print(f"  Written {written} pages to {self.output_dir}")
            print(f"  Manifest: {manifest_path}")

            # Write import helper shell script
            self._write_import_helper()
        else:
            print(f"  [DRY RUN] Would write {written} pages to {self.output_dir}")

        return manifest

    def _write_import_helper(self):
        helper = self.output_dir / "import-to-wikijs.sh"
        helper.write_text(
            "#!/bin/bash\n"
            "# Auto-generated Wiki.js import helper\n"
            "# Usage: WIKIJS_URL=http://localhost:3000 WIKIJS_TOKEN=<token> ./import-to-wikijs.sh\n\n"
            "set -euo pipefail\n\n"
            'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\n'
            'REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"\n\n'
            'WIKIJS_URL="${WIKIJS_URL:-http://localhost:3000}"\n'
            'WIKIJS_TOKEN="${WIKIJS_TOKEN:?Error: WIKIJS_TOKEN must be set}"\n\n'
            "echo \"Importing to Wiki.js at $WIKIJS_URL ...\"\n\n"
            "cd \"$REPO_ROOT\"\n\n"
            "# Check for node\n"
            'if ! command -v node &>/dev/null; then\n'
            '  echo "Error: node is required"\n'
            '  exit 1\n'
            'fi\n\n'
            "# Install deps if needed\n"
            'if [ ! -d "wiki-js-scaffold/node_modules" ]; then\n'
            '  echo "Installing wiki-js-scaffold dependencies..."\n'
            '  cd wiki-js-scaffold && npm install && cd ..\n'
            'fi\n\n'
            "WIKIJS_URL=\"$WIKIJS_URL\" WIKIJS_TOKEN=\"$WIKIJS_TOKEN\" \\\n"
            "  node wiki-js-scaffold/scripts/import-to-wikijs.js\n\n"
            'echo "Import complete!"\n',
            encoding="utf-8",
        )
        helper.chmod(0o755)
        print(f"  Import helper: {helper}")

    def show_manifest(self):
        """Print a summary of what would be exported."""
        print(f"\n  Total pages: {len(self.pages)}")
        print(f"\n  {'Wiki Path':<60} {'Project':<30} {'Title'}")
        print(f"  {'-'*60} {'-'*30} {'-'*40}")
        for page in sorted(self.pages, key=lambda p: p.wiki_path):
            print(f"  {page.wiki_path:<60} {page.project_name:<30} {page.title[:40]}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Prepare Wiki.js export from portfolio")
    parser.add_argument("--root", default=".", help="Portfolio root directory")
    parser.add_argument("--out", default="wiki-export", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--show-manifest", action="store_true",
                        help="Show manifest table after export")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_dir = Path(args.out)
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    if not root.exists():
        print(f"ERROR: Root not found: {root}", file=sys.stderr)
        sys.exit(1)

    print(f"\n=== Wiki.js Export Preparer ===")
    print(f"  Root:   {root}")
    print(f"  Output: {output_dir}")
    if args.dry_run:
        print("  Mode:   DRY RUN")
    print()

    preparer = WikiJsExportPreparer(root=root, output_dir=output_dir, dry_run=args.dry_run)
    preparer.scan()
    manifest = preparer.export()

    if args.show_manifest:
        preparer.show_manifest()

    print(f"\nDone! {manifest['total_pages']} pages prepared.")
    if not args.dry_run:
        print(f"\nTo import into Wiki.js:")
        print(f"  WIKIJS_URL=http://localhost:3000 WIKIJS_TOKEN=<your-token> \\")
        print(f"  bash {output_dir}/import-to-wikijs.sh")


if __name__ == "__main__":
    main()
