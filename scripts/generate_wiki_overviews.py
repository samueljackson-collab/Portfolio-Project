#!/usr/bin/env python3
"""Generate Wiki overview pages for projects 1-25."""
import re
import textwrap
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = REPO_ROOT / "projects"
DOCS_ROOT = PROJECTS_DIR / "25-portfolio-website" / "docs" / "projects"
MASTER_PLAYBOOK = REPO_ROOT / "docs" / "PRJ-MASTER-PLAYBOOK" / "README.md"
HOMELAB_MOCKUPS = PROJECTS_DIR / "06-homelab" / "PRJ-HOME-002" / "assets" / "mockups"

CATEGORY_SCREENSHOT = {
    "Infrastructure & DevOps": "grafana-dashboard.html",
    "Data Engineering": "grafana-dashboard.html",
    "Machine Learning & AI": "grafana-dashboard.html",
    "Automation & Documentation": "wikijs-documentation.html",
    "Web Applications": "wikijs-documentation.html",
    "Security & Compliance": "nginx-proxy-manager.html",
    "Blockchain & Web3": "nginx-proxy-manager.html",
    "IoT & Edge Computing": "homeassistant-dashboard.html",
    "Quantum Computing": "proxmox-datacenter.html",
    "High-Performance Computing": "proxmox-datacenter.html",
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def parse_sections(text: str) -> dict:
    sections = {}
    current = None
    buffer = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current:
                sections[current] = "\n".join(buffer).strip()
            current = line[3:].strip()
            buffer = []
            continue
        if current:
            buffer.append(line.rstrip())
    if current:
        sections[current] = "\n".join(buffer).strip()
    return sections


def extract_bullets(text: str) -> list:
    bullets = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("- "):
            bullets.append(line[2:].strip())
    return bullets


def parse_technologies(text: str) -> list:
    entries = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("- "):
            continue
        line = line[2:].strip()
        match = re.match(r"\*\*(.+?)\*\*(.*)", line)
        if match:
            name = match.group(1).strip()
            rest = match.group(2).strip()
        else:
            parts = line.split("-", 1)
            name = parts[0].strip()
            rest = parts[1].strip() if len(parts) > 1 else ""
        desc = rest.lstrip("- ")
        entries.append((name, desc))
    return entries


def parse_doc_map() -> dict:
    mapping = {}
    for md_path in DOCS_ROOT.glob("*.md"):
        content = md_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        title_match = re.match(r"# (.+)", lines[0]) if lines else None
        title = title_match.group(1).strip() if title_match else md_path.stem
        category = ""
        status = ""
        source_line = ""
        for line in lines:
            if line.startswith("**Category:**"):
                category = line.split("**Category:**", 1)[1].strip()
            if line.startswith("**Status:**"):
                status = line.split("**Status:**", 1)[1].strip()
            if line.startswith("**Source:**"):
                source_line = line
                break
        number_match = re.search(r"Project\s+(\d+)", title)
        if not number_match:
            continue
        project_number = int(number_match.group(1))
        sections = parse_sections(content)
        mapping[project_number] = {
            "title": title,
            "category": category,
            "status": status,
            "sections": sections,
            "path": md_path,
            "content": content,
        }
    return mapping


def extract_master_checklist() -> str:
    text = MASTER_PLAYBOOK.read_text(encoding="utf-8")
    pattern = re.compile(r"#### 5.1 Pre-Deployment Checklist(.*?)#### 5.2", re.S)
    match = pattern.search(text)
    if match:
        snippet = match.group(1).strip()
        return snippet
    return ""


def extract_runbook_slo(runbook_path: Path) -> str:
    lines = runbook_path.read_text(encoding="utf-8").splitlines()
    start = None
    end = None
    for idx, line in enumerate(lines):
        if line.strip().lower().startswith("## slos/slis"):
            start = idx + 1
            continue
        if start is not None and line.strip().startswith("---"):
            end = idx
            break
    if start is None:
        return ""
    table_lines = []
    for line in lines[start : end if end is not None else len(lines)]:
        if line.strip().startswith("|"):
            table_lines.append(line.rstrip())
    return "\n".join(table_lines).strip()


def select_screen_mockup(category: str) -> Path:
    filename = CATEGORY_SCREENSHOT.get(category, "grafana-dashboard.html")
    return HOMELAB_MOCKUPS / filename


def gather_doc_links(project_dir: Path, extra_doc: Path) -> list:
    links = []
    for candidate in sorted(project_dir.glob("*.md")):
        rel = candidate.relative_to(project_dir)
        links.append((rel.as_posix(), f"../{rel.as_posix()}"))
    extra_rel = extra_doc.relative_to(REPO_ROOT)
    links.append((extra_rel.as_posix(), f"../../../{extra_rel.as_posix()}"))
    return links


def build_components_table(technologies: list) -> str:
    rows = [
        "| Component | Technology | Purpose |",
        "|-----------|-----------|---------|",
    ]
    for name, desc in technologies[:3]:
        tech = name
        purpose = desc or "Documented in project overview"
        rows.append(f"| {name} | {tech} | {purpose} |")
    return "\n".join(rows)


def render_objectives(bullets: list) -> str:
    if not bullets:
        return "- Establish foundational capabilities\n- Implement automation\n- Validate runbooks"
    return "\n".join(f"- {item}" for item in bullets[:5])


def render_results(business: list, status: str) -> str:
    if business:
        return "\n".join(f"- {item}" for item in business[:4])
    return f"- Status snapshot: {status}"


def clean_paragraph(text: str) -> str:
    lines = [
        ln.rstrip() for ln in textwrap.dedent(text).strip().splitlines() if ln.strip()
    ]
    return "\n\n".join(lines)


def render_implementation(sections: dict) -> str:
    parts = []
    for key in ("Quick Start", "Project Structure", "Getting Started"):
        if key in sections:
            parts.append(sections[key])
    if not parts:
        return "Refer to project README for implementation details."
    return "\n\n".join(parts)


def render_diagram_note(doc_rel: Path) -> str:
    return f"- **Architecture excerpt** — Copied from `../../../{doc_rel.as_posix()}` (Architecture section)."


def render_checklist(project_dir: Path, master_snippet: str) -> tuple[str, str]:
    checklist_file = next(project_dir.glob("*CHECKLIST*.md"), None)
    if checklist_file:
        lines = []
        for line in checklist_file.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("- [ ]"):
                lines.append(line.rstrip())
            if len(lines) >= 8:
                break
        snippet = "\n".join(lines)
        return snippet, f"../{checklist_file.name}"
    return (
        master_snippet,
        "../../../docs/PRJ-MASTER-PLAYBOOK/README.md#5-deployment--release",
    )


def render_skills(technologies: list) -> str:
    tech_list = ", ".join(name for name, _ in technologies[:5])
    soft = "Communication, Incident response leadership, Documentation rigor"
    return f"**Technical Skills:** {tech_list}\n\n**Soft Skills:** {soft}"


def main() -> None:
    doc_map = parse_doc_map()
    master_checklist = extract_master_checklist()
    today = date.today().isoformat()
    project_dirs = []
    for path in PROJECTS_DIR.iterdir():
        if not path.is_dir():
            continue
        name = path.name
        if not re.match(r"^[0-9]+-", name):
            continue
        if name.startswith("0"):
            continue
        idx = int(name.split("-", 1)[0])
        if 1 <= idx <= 25:
            project_dirs.append((idx, path))
    project_dirs.sort(key=lambda item: item[0])

    for idx, project_dir in project_dirs:
        doc = doc_map.get(idx)
        if not doc:
            print(f"Skipping {project_dir.name}: no supporting doc found")
            continue
        sections = doc["sections"]
        overview = clean_paragraph(sections.get("Overview", ""))
        objectives = render_objectives(
            extract_bullets(sections.get("Key Features", ""))
            or extract_bullets(sections.get("Goals", ""))
        )
        architecture = sections.get("Architecture", "Architecture details pending.")
        technologies = parse_technologies(sections.get("Technologies", ""))
        components_table = build_components_table(technologies)
        business = extract_bullets(sections.get("Business Impact", ""))
        implementation = render_implementation(sections)
        results = render_results(business, doc["status"])
        slo_table = extract_runbook_slo(project_dir / "RUNBOOK.md")
        checklist_snippet, checklist_source = render_checklist(
            project_dir, master_checklist
        )
        screenshot_path = select_screen_mockup(doc["category"])
        doc_links = gather_doc_links(project_dir, doc["path"])
        slug = project_dir.name.split("-", 1)[1]
        front_description = (
            overview.split(". ")[0].strip() if overview else doc["title"]
        )
        front_description = re.sub(r"[`*]", "", front_description)
        tags = [
            "portfolio",
            slugify(doc["category"] or slug),
            slugify(technologies[0][0]) if technologies else slug,
        ]
        doc_rel = doc["path"].relative_to(REPO_ROOT)

        wiki_lines = []
        wiki_lines.append("---")
        wiki_lines.append(f"title: {doc['title']}")
        wiki_lines.append(f"description: {front_description}")
        wiki_lines.append(f"tags: [{', '.join(tags)}]")
        wiki_lines.append(
            "repository: https://github.com/samueljackson-collab/Portfolio-Project"
        )
        wiki_lines.append(f"path: /projects/{slug}")
        wiki_lines.append("---\n")
        wiki_lines.append(f"# {doc['title']}")
        wiki_lines.append(
            f"> **Category:** {doc['category']} | **Status:** {doc['status']}"
        )
        wiki_lines.append(
            "> **Source:** projects/25-portfolio-website/docs/projects/" + doc_rel.name
        )
        wiki_lines.append("\n## 📋 Executive Summary\n")
        wiki_lines.append(overview or "Documentation in progress.")
        wiki_lines.append("\n## 🎯 Project Objectives\n")
        wiki_lines.append(objectives)
        wiki_lines.append("\n## 🏗️ Architecture\n")
        wiki_lines.append(f"> Source: ../../../{doc_rel.as_posix()}#architecture")
        wiki_lines.append(architecture)
        wiki_lines.append("\n### Components\n")
        wiki_lines.append(components_table)
        wiki_lines.append("\n## 💡 Key Technical Decisions\n")
        for idx, (name, desc) in enumerate(technologies[:3], start=1):
            wiki_lines.append(f"### Decision {idx}: Adopt {name}")
            wiki_lines.append(
                f"**Context:** {doc['title']} requires a resilient delivery path."
            )
            wiki_lines.append(
                f"**Decision:** {desc or 'Implementation documented in README.md.'}"
            )
            wiki_lines.append(
                "**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.\n"
            )
        wiki_lines.append("## 🔧 Implementation Details\n")
        wiki_lines.append(implementation)
        wiki_lines.append("\n## ✅ Results & Outcomes\n")
        wiki_lines.append(results)
        wiki_lines.append("\n## 📚 Documentation\n")
        for label, rel_link in doc_links:
            wiki_lines.append(f"- [{label}]({rel_link})")
        wiki_lines.append("\n## 🎓 Skills Demonstrated\n")
        wiki_lines.append(render_skills(technologies))
        wiki_lines.append("\n## 📦 Wiki Deliverables\n")
        wiki_lines.append("### Diagrams\n")
        wiki_lines.append(render_diagram_note(doc_rel))
        wiki_lines.append("\n### Checklists\n")
        wiki_lines.append(f"> Source: {checklist_source}")
        wiki_lines.append("\n" + checklist_snippet.strip())
        wiki_lines.append("\n### Metrics\n")
        wiki_lines.append(f"> Source: ../RUNBOOK.md#sloslis\n")
        if slo_table:
            wiki_lines.append(slo_table)
        else:
            wiki_lines.append("Metrics pending.")
        wiki_lines.append("\n### Screenshots\n")
        mockup_rel = screenshot_path.relative_to(REPO_ROOT)
        wiki_lines.append(
            "- **Operational dashboard mockup** — `../../../"
            + mockup_rel.as_posix()
            + "` (captures golden signals per PRJ-MASTER playbook)."
        )
        wiki_lines.append("\n---\n")
        wiki_lines.append(f"*Created: {today} | Last Updated: {today}*")

        wiki_dir = project_dir / "wiki"
        wiki_dir.mkdir(parents=True, exist_ok=True)
        (wiki_dir / "overview.md").write_text(
            "\n".join(wiki_lines) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
