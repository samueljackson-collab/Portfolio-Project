#!/usr/bin/env python3
"""Inject metadata-driven status and roadmap tables into project README files."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SCOPE_HEADING = "## 📌 Scope & Status"
ROADMAP_HEADING = "## 🗺️ Roadmap"

SCOPE_BEGIN = "<!-- BEGIN AUTO STATUS TABLE -->"
SCOPE_END = "<!-- END AUTO STATUS TABLE -->"
ROADMAP_BEGIN = "<!-- BEGIN AUTO ROADMAP TABLE -->"
ROADMAP_END = "<!-- END AUTO ROADMAP TABLE -->"


@dataclass
class ProjectMetadata:
    phase_status: str
    next_milestone_date: str
    owner: str
    dependency_blocker: str
    roadmap: list[dict[str, str]]


def load_project_metadata(metadata_file: Path) -> dict[str, ProjectMetadata]:
    raw = json.loads(metadata_file.read_text(encoding="utf-8"))
    metadata: dict[str, ProjectMetadata] = {}
    for path, payload in raw.get("projects", {}).items():
        metadata[path] = ProjectMetadata(
            phase_status=str(payload.get("phase_status", "")).strip(),
            next_milestone_date=str(payload.get("next_milestone_date", "")).strip(),
            owner=str(payload.get("owner", "")).strip(),
            dependency_blocker=str(payload.get("dependency_blocker", "")).strip(),
            roadmap=[
                {
                    "milestone": str(item.get("milestone", "")).strip(),
                    "target_date": str(item.get("target_date", "")).strip(),
                    "owner": str(item.get("owner", "")).strip(),
                    "status": str(item.get("status", "")).strip(),
                    "notes": str(item.get("notes", "")).strip(),
                }
                for item in payload.get("roadmap", [])
            ],
        )
    return metadata


def build_scope_table(metadata: ProjectMetadata) -> str:
    return "\n".join(
        [
            SCOPE_BEGIN,
            "| Field | Value |",
            "| --- | --- |",
            f"| Current phase/status | {metadata.phase_status} |",
            f"| Next milestone date | {metadata.next_milestone_date} |",
            f"| Owner | {metadata.owner} |",
            f"| Dependency / blocker | {metadata.dependency_blocker} |",
            SCOPE_END,
        ]
    )


def build_roadmap_table(metadata: ProjectMetadata) -> str:
    rows = [
        ROADMAP_BEGIN,
        "| Milestone | Target date | Owner | Status | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in metadata.roadmap:
        rows.append(
            f"| {item['milestone']} | {item['target_date']} | {item['owner']} | {item['status']} | {item['notes']} |"
        )
    rows.append(ROADMAP_END)
    return "\n".join(rows)


def strip_managed_block(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    finish = text.find(end)
    if start == -1 or finish == -1 or finish < start:
        return text
    finish += len(end)
    before = text[:start].rstrip()
    after = text[finish:].lstrip("\n")
    if before and after:
        return f"{before}\n\n{after}"
    return f"{before}{after}"


def split_section(content: str, heading: str) -> tuple[str, str, str] | None:
    marker = f"\n{heading}\n"
    start = content.find(marker)
    if start == -1:
        if content.startswith(f"{heading}\n"):
            start = 0
            prefix = ""
            after_start = len(f"{heading}\n")
        else:
            return None
    else:
        prefix = content[: start + 1]
        after_start = start + len(marker)

    tail = content[after_start:]
    next_h2 = tail.find("\n## ")
    if next_h2 == -1:
        body = tail
        suffix = ""
    else:
        body = tail[:next_h2]
        suffix = tail[next_h2 + 1 :]

    return prefix, body, suffix


def upsert_section_block(content: str, heading: str, block: str, begin: str, end: str) -> str:
    section = split_section(content, heading)
    if section is None:
        return content.rstrip() + f"\n\n{heading}\n{block}\n"

    prefix, body, suffix = section
    cleaned_body = strip_managed_block(body.strip("\n"), begin, end)

    parts = [prefix]
    if not prefix.endswith("\n"):
        parts.append("\n")
    parts.append(f"{heading}\n")
    parts.append(f"{block}\n")
    if cleaned_body.strip():
        parts.append("\n")
        parts.append(cleaned_body.strip("\n") + "\n")
    if suffix:
        parts.append(suffix)

    return "".join(parts)


def inject_metadata(content: str, metadata: ProjectMetadata) -> str:
    updated = upsert_section_block(
        content=content,
        heading=SCOPE_HEADING,
        block=build_scope_table(metadata),
        begin=SCOPE_BEGIN,
        end=SCOPE_END,
    )
    updated = upsert_section_block(
        content=updated,
        heading=ROADMAP_HEADING,
        block=build_roadmap_table(metadata),
        begin=ROADMAP_BEGIN,
        end=ROADMAP_END,
    )
    return updated


def iter_readmes(repo_root: Path, path_glob: str) -> Iterable[Path]:
    for path in sorted(repo_root.glob(path_glob)):
        if ".git" in path.parts:
            continue
        yield path


def run(repo_root: Path, apply_changes: bool, target: str | None, metadata_file: Path, path_glob: str) -> int:
    project_metadata = load_project_metadata(metadata_file)
    readmes = list(iter_readmes(repo_root, path_glob))
    if target:
        readmes = [p for p in readmes if p.relative_to(repo_root).as_posix() == target]

    changed = 0
    for readme in readmes:
        key = readme.relative_to(repo_root).as_posix()
        metadata = project_metadata.get(key)
        if metadata is None:
            print(f"[skip-no-metadata] {key}")
            continue

        original = readme.read_text(encoding="utf-8")
        updated = inject_metadata(original, metadata)
        if updated != original:
            changed += 1
            if apply_changes:
                readme.write_text(updated, encoding="utf-8")
                print(f"[updated] {key}")
            else:
                print(f"[would-update] {key}")

    verb = "Updated" if apply_changes else "Would update"
    print(f"{verb} {changed} README file(s).")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root directory")
    parser.add_argument("--apply", action="store_true", help="Write metadata tables into README files")
    parser.add_argument("--target", help="Optional repository-relative README path")
    parser.add_argument(
        "--metadata-file",
        type=Path,
        default=Path("scripts/readme_migration/project_status_metadata.json"),
        help="Path to centralized project metadata JSON.",
    )
    parser.add_argument(
        "--path-glob",
        default="projects/*/README.md",
        help="Glob for README files to update (default: projects/*/README.md).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    metadata_file = (repo_root / args.metadata_file).resolve()
    return run(
        repo_root=repo_root,
        apply_changes=args.apply,
        target=args.target,
        metadata_file=metadata_file,
        path_glob=args.path_glob,
    )


if __name__ == "__main__":
    raise SystemExit(main())
