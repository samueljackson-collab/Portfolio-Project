#!/usr/bin/env python3
"""Migrate README.md files to a standardized portfolio template."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REQUIRED_SECTIONS = [
    "## 🎯 Overview",
    "## 📌 Scope & Status",
    "## 🏗️ Architecture",
    "## 🚀 Setup & Runbook",
    "## ✅ Testing & Quality Evidence",
    "## 🔐 Security, Risk & Reliability",
    "## 🔄 Delivery & Observability",
    "## 🗺️ Roadmap",
    "## 📎 Evidence Index",
    "## 🧾 Documentation Freshness",
]

CHECKLIST_BLOCK = """## Final checklist\n- [ ] Scope boundaries documented and aligned to current directory ownership.\n- [ ] Setup and runbook steps validated against current scripts/tools.\n- [ ] Testing evidence linked (commands, outputs, or artifacts).\n- [ ] Security and reliability controls captured with current status markers.\n- [ ] Delivery/observability signals linked to dashboards, logs, or runbooks.\n- [ ] Roadmap reflects next milestones with status key (🟢/🟠/🔵/🔄/📝).\n"""

STATUS_KEY = "🟢 Delivered · 🟠 In Progress · 🔵 Planned · 🔄 Recovery/Rebuild · 📝 Documentation Pending"

SECTION_MAPPING = {
    "overview": "## 🎯 Overview",
    "introduction": "## 🎯 Overview",
    "purpose": "## 🎯 Overview",
    "about": "## 🎯 Overview",
    "scope": "## 📌 Scope & Status",
    "status": "## 📌 Scope & Status",
    "current state": "## 📌 Scope & Status",
    "architecture": "## 🏗️ Architecture",
    "design": "## 🏗️ Architecture",
    "system": "## 🏗️ Architecture",
    "usage": "## 🚀 Setup & Runbook",
    "setup": "## 🚀 Setup & Runbook",
    "getting started": "## 🚀 Setup & Runbook",
    "installation": "## 🚀 Setup & Runbook",
    "runbook": "## 🚀 Setup & Runbook",
    "deploy": "## 🚀 Setup & Runbook",
    "test": "## ✅ Testing & Quality Evidence",
    "quality": "## ✅ Testing & Quality Evidence",
    "validation": "## ✅ Testing & Quality Evidence",
    "security": "## 🔐 Security, Risk & Reliability",
    "risk": "## 🔐 Security, Risk & Reliability",
    "reliability": "## 🔐 Security, Risk & Reliability",
    "observability": "## 🔄 Delivery & Observability",
    "monitoring": "## 🔄 Delivery & Observability",
    "delivery": "## 🔄 Delivery & Observability",
    "ci": "## 🔄 Delivery & Observability",
    "cd": "## 🔄 Delivery & Observability",
    "roadmap": "## 🗺️ Roadmap",
    "future": "## 🗺️ Roadmap",
    "backlog": "## 🗺️ Roadmap",
    "evidence": "## 📎 Evidence Index",
    "references": "## 📎 Evidence Index",
    "links": "## 📎 Evidence Index",
    "documentation": "## 🧾 Documentation Freshness",
    "changelog": "## 🧾 Documentation Freshness",
    "maintenance": "## 🧾 Documentation Freshness",
}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class ReadmeDocument:
    title: str
    sections: dict[str, str]


def normalize_heading_key(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]+", " ", text.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def parse_markdown_sections(content: str) -> ReadmeDocument:
    matches = list(HEADING_RE.finditer(content))
    title = ""
    sections: dict[str, str] = {}

    if not matches:
        return ReadmeDocument(title="", sections={"preface": content.strip()})

    first = matches[0]
    preface = content[: first.start()].strip()
    if preface:
        sections["preface"] = preface

    for index, match in enumerate(matches):
        level = len(match.group(1))
        heading = match.group(2).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        body = content[start:end].strip()

        if level == 1 and not title:
            title = heading
            continue

        sections[heading] = body

    return ReadmeDocument(title=title, sections=sections)


def map_section_heading(old_heading: str) -> str | None:
    normalized = normalize_heading_key(old_heading)
    for token, mapped in SECTION_MAPPING.items():
        if token in normalized:
            return mapped
    return None


def merge_into_target_sections(parsed: ReadmeDocument) -> dict[str, list[str]]:
    target: dict[str, list[str]] = {name: [] for name in REQUIRED_SECTIONS}

    for heading, body in parsed.sections.items():
        if heading == "preface":
            target["## 🎯 Overview"].append(body)
            continue

        mapped = map_section_heading(heading)
        if mapped:
            fragment = f"### {heading}\n{body}".strip()
            target[mapped].append(fragment)
        else:
            fallback = f"### {heading}\n{body}".strip()
            target["## 📎 Evidence Index"].append(fallback)

    return target


def infer_scope_context(readme_path: Path, repo_root: Path) -> str:
    rel_dir = readme_path.parent.relative_to(repo_root)
    if str(rel_dir) == ".":
        return (
            "- **Scope:** Repository-wide portfolio orchestration and cross-project navigation.\n"
            "- **Status key:** " + STATUS_KEY
        )

    display = rel_dir.as_posix()
    return (
        f"- **Scope:** `{display}/` subdirectory documentation boundary and local deliverables.\n"
        "- **Status key:** " + STATUS_KEY + "\n"
        "- **Status:** 📝 Planned-state placeholder — confirm active owner, maturity, and latest evidence links."
    )


def placeholder_for(section_heading: str, readme_path: Path, repo_root: Path) -> str:
    rel_path = readme_path.relative_to(repo_root).as_posix()
    placeholders = {
        "## 🎯 Overview": (
            f"📝 Planned-state placeholder: summarize the purpose and intended audience for `{rel_path}`."
        ),
        "## 📌 Scope & Status": infer_scope_context(readme_path, repo_root),
        "## 🏗️ Architecture": "🔵 Planned-state placeholder: capture component boundaries, dependencies, and diagram links.",
        "## 🚀 Setup & Runbook": "🔵 Planned-state placeholder: document setup prerequisites, execution commands, and rollback steps.",
        "## ✅ Testing & Quality Evidence": "🟠 Planned-state placeholder: link validated test commands, quality gates, and latest results.",
        "## 🔐 Security, Risk & Reliability": "🔄 Planned-state placeholder: enumerate controls, known risks, and reliability safeguards.",
        "## 🔄 Delivery & Observability": "🔵 Planned-state placeholder: provide CI/CD workflow, monitoring, alerting, and SLO evidence.",
        "## 🗺️ Roadmap": "🔵 Planned-state placeholder: list upcoming milestones with owners and target dates.",
        "## 📎 Evidence Index": "📝 Planned-state placeholder: index ADRs, runbooks, screenshots, reports, and ticket references.",
        "## 🧾 Documentation Freshness": "📝 Planned-state placeholder: note last review date, reviewer, and next scheduled refresh.",
    }
    return placeholders[section_heading]


def normalize_markdown_tables(content: str) -> str:
    lines = content.splitlines()
    fixed: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if "|" in line and i + 1 < len(lines) and re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*", lines[i + 1]):
            header_cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            sep_cells = [cell.strip() for cell in lines[i + 1].strip().strip("|").split("|")]
            column_count = max(len(header_cells), len(sep_cells))
            header_cells += [""] * (column_count - len(header_cells))
            sep_cells += ["---"] * (column_count - len(sep_cells))
            fixed.append("| " + " | ".join(header_cells) + " |")
            fixed.append("| " + " | ".join(cell if cell else "---" for cell in sep_cells) + " |")
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                row_cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                row_cells += [""] * (column_count - len(row_cells))
                fixed.append("| " + " | ".join(row_cells[:column_count]) + " |")
                i += 1
            continue
        fixed.append(line)
        i += 1

    return "\n".join(fixed)


def normalize_mermaid_blocks(content: str) -> str:
    lines = content.splitlines()
    normalized: list[str] = []
    in_mermaid = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            label = stripped[3:].strip().lower()
            if in_mermaid:
                normalized.append("```")
                in_mermaid = False
                continue
            if label in {"mermaid", "mmd"}:
                normalized.append("```mermaid")
                in_mermaid = True
                continue
        normalized.append(line)

    if in_mermaid:
        normalized.append("```")

    return "\n".join(normalized)


def build_migrated_content(original: str, readme_path: Path, repo_root: Path) -> str:
    parsed = parse_markdown_sections(original)
    merged = merge_into_target_sections(parsed)

    title = parsed.title or readme_path.parent.name.replace("-", " ").title()
    output: list[str] = [f"# {title}", ""]

    for section in REQUIRED_SECTIONS:
        output.append(section)
        body_blocks = [block for block in merged.get(section, []) if block.strip()]
        if body_blocks:
            output.append("\n\n".join(body_blocks))
        else:
            output.append(placeholder_for(section, readme_path, repo_root))
        output.append("")

    output.append(CHECKLIST_BLOCK.rstrip())
    output.append("")

    migrated = "\n".join(output).strip() + "\n"
    migrated = normalize_markdown_tables(migrated)
    migrated = normalize_mermaid_blocks(migrated)
    return migrated


def iter_readmes(repo_root: Path) -> Iterable[Path]:
    for path in repo_root.rglob("README.md"):
        if ".git" in path.parts:
            continue
        yield path


def run(repo_root: Path, apply_changes: bool, target: str | None) -> int:
    readmes = list(iter_readmes(repo_root))
    if target:
        readmes = [p for p in readmes if p.relative_to(repo_root).as_posix() == target]

    changed = 0
    for readme in sorted(readmes):
        original = readme.read_text(encoding="utf-8")
        migrated = build_migrated_content(original, readme, repo_root)
        if original != migrated:
            changed += 1
            if apply_changes:
                readme.write_text(migrated, encoding="utf-8")
                print(f"[updated] {readme.relative_to(repo_root)}")
            else:
                print(f"[would-update] {readme.relative_to(repo_root)}")

    verb = "Updated" if apply_changes else "Would update"
    print(f"{verb} {changed} README file(s).")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root directory")
    parser.add_argument("--apply", action="store_true", help="Write migrated content back to disk")
    parser.add_argument(
        "--target",
        help="Optional repository-relative README path (for focused testing), e.g. docs/README.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    return run(repo_root=repo_root, apply_changes=args.apply, target=args.target)


if __name__ == "__main__":
    raise SystemExit(main())
