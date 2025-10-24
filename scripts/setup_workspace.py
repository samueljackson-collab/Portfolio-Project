"""Utility for assembling portfolio workspace bundles.

This script mirrors the environment used to prepare the repository's
content when multiple ZIP archives are provided.  It safely extracts the
archives, performs light-weight linting/auto-fixing on common text-based
assets, and emits CSV/Markdown reports summarising everything that was
touched.

The implementation intentionally avoids destructive edits: only easily
recoverable or mechanically safe fixes (JSON comments/trailing commas,
missing colons in simple Python blocks, and empty package.json metadata)
are applied automatically.  Anything else is documented for manual
follow-up in the generated reports.
"""
from __future__ import annotations

import argparse
import ast
import datetime as _dt
import json
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Sequence, Tuple

try:
    import pandas as pd
except ImportError:  # pragma: no cover - helper dependency
    pd = None  # type: ignore

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore

ROOT = Path("/mnt/data")
DEFAULT_ARCHIVES = (
    "blitzy_export_v0.13.0.zip",
    "homelab_rack_update_2025-10.zip",
    "portfolio_templates_v3_enterprise_addons.zip",
    "portfolio_bootstrap_kit.zip",
)

CODE_EXTS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".json",
    ".yaml",
    ".yml",
    ".sh",
    ".ps1",
    ".tf",
    ".tfvars",
    ".md",
    ".toml",
    ".ini",
    ".cfg",
    ".dockerfile",
    ".env",
    ".conf",
    ".sql",
    ".rb",
    ".go",
    ".java",
    ".cs",
    ".rs",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".vue",
    ".svelte",
    ".pyi",
}

PACKAGE_FILES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "Dockerfile",
    "dockerfile",
}

PY_BLOCK_PREFIX = re.compile(
    r"^(?P<indent>\s*)(?:def|class|if|for|while|elif|else|try|except(?:\s+[^:]+)?|with\s+[^:]+)(?P<body>\s*(?:#.*)?)$"
)


@dataclass
class Issue:
    file: Path
    type: str
    message: str
    fixed: bool = False
    fix_note: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "file": str(self.file),
            "type": self.type,
            "message": self.message,
            "fixed": "yes" if self.fixed else "no",
            "fix_note": self.fix_note,
        }


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Root directory containing source ZIP archives (default: /mnt/data)",
    )
    parser.add_argument(
        "--archives",
        type=Path,
        nargs="*",
        default=None,
        help="Explicit list of ZIP archives to process.  If omitted the default list is searched.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Directory where the assembled workspace should be written.  Defaults to /mnt/data/fixed_<timestamp>.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Staging workspace.  Defaults to /mnt/data/workspace_<timestamp>.",
    )
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Skip the final copy of the staged files into the output directory.",
    )
    parser.add_argument(
        "--report-csv",
        type=Path,
        default=None,
        help="Optional path to write the CSV issue report.  Defaults to <out>/reports/scan_issues.csv.",
    )
    parser.add_argument(
        "--report-md",
        type=Path,
        default=None,
        help="Optional path to write the Markdown summary report.  Defaults to <out>/reports/SUMMARY.md.",
    )
    parser.add_argument(
        "--zip-output",
        action="store_true",
        help="Zip the output directory (mirrors the original environment packaging).",
    )
    return parser.parse_args(argv)


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def existing_archives(root: Path, requested: Iterable[Path] | None) -> List[Path]:
    if requested:
        archives = [p if p.is_absolute() else root / p for p in requested]
    else:
        archives = [root / name for name in DEFAULT_ARCHIVES]
    return [p for p in archives if p.exists()]


def safe_extract(archive: Path, destination: Path) -> None:
    """Safely extract *archive* to *destination* (guarding against Zip Slip)."""

    with zipfile.ZipFile(archive, "r") as zf:
        for member in zf.infolist():
            resolved = (destination / member.filename).resolve()
            if not str(resolved).startswith(str(destination.resolve())):
                continue
            if member.is_dir():
                resolved.mkdir(parents=True, exist_ok=True)
            else:
                resolved.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member, "r") as src, open(resolved, "wb") as dst:
                    shutil.copyfileobj(src, dst)


def sanitize_json(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(?m)//.*$", "", text)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text


def try_fix_json(path: Path) -> Tuple[bool, str]:
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - IO issues
        return False, f"Could not read file: {exc}"
    try:
        json.loads(raw)
        return False, "Valid JSON (no fix needed)"
    except Exception:
        cleaned = sanitize_json(raw)
        try:
            json.loads(cleaned)
        except Exception as exc:  # pragma: no cover - complex JSON errors
            return False, f"Unfixable JSON: {exc}"
        path.write_text(cleaned, encoding="utf-8")
        return True, "Removed comments/trailing commas"


def try_fix_yaml(path: Path) -> Tuple[bool, str]:
    if yaml is None:
        return False, "PyYAML unavailable"
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - IO issues
        return False, f"Could not read file: {exc}"
    try:
        yaml.safe_load(raw)
        return False, "Valid YAML (no fix needed)"
    except Exception as exc:
        return False, f"YAML parse error: {exc}"


def try_fix_python(path: Path) -> Tuple[bool, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - IO issues
        return False, f"Could not read file: {exc}"
    try:
        ast.parse(text)
        return False, "Valid Python (no fix needed)"
    except SyntaxError:
        lines = text.splitlines()
        changed = False
        for idx, line in enumerate(lines):
            if PY_BLOCK_PREFIX.match(line.rstrip()) and not line.rstrip().endswith(":"):
                lines[idx] = f"{line.rstrip()}:"
                changed = True
        if not changed:
            return False, "Syntax error (manual review required)"
        new_text = "\n".join(lines)
        try:
            ast.parse(new_text)
        except SyntaxError as exc:  # pragma: no cover - still invalid
            return False, f"Syntax still invalid: {exc}"
        path.write_text(new_text, encoding="utf-8")
        return True, "Added missing ':' to block headers"


def ensure_package_json(path: Path) -> Tuple[bool, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - invalid JSON already reported
        return False, f"Invalid JSON: {exc}"
    changed = False
    if not data.get("name"):
        data["name"] = path.parent.name.lower().replace(" ", "-")
        changed = True
    if not data.get("version"):
        data["version"] = "0.1.0"
        changed = True
    if "license" not in data:
        data["license"] = "MIT"
        changed = True
    if "private" not in data:
        data["private"] = True
        changed = True
    scripts = data.get("scripts")
    if not isinstance(scripts, dict) or not scripts:
        data["scripts"] = {
            "build": "echo \"No build configured\"",
            "start": "node index.js || echo 'No start script'",
        }
        changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return True, "Filled minimal fields in package.json"
    return False, "package.json ok"


def discover_files(base: Path) -> Iterator[Path]:
    for path in base.rglob("*"):
        if path.is_file():
            yield path


def relative_to_workspace(path: Path, workspace: Path) -> Path:
    try:
        return path.relative_to(workspace)
    except ValueError:  # pragma: no cover - fallback guard
        return path


def scan_files(files: Iterable[Path], workspace: Path) -> List[Issue]:
    issues: List[Issue] = []
    for file_path in files:
        ext = file_path.suffix.lower()
        name = file_path.name.lower()
        rel = relative_to_workspace(file_path, workspace)
        try:
            if ext == ".json":
                fixed, note = try_fix_json(file_path)
                issues.append(Issue(rel, "json", note, fixed, note if fixed else ""))
                if name == "package.json":
                    fixed2, note2 = ensure_package_json(file_path)
                    issues.append(Issue(rel, "node", note2, fixed2, note2 if fixed2 else ""))
            elif ext in {".yaml", ".yml"}:
                fixed, note = try_fix_yaml(file_path)
                issues.append(Issue(rel, "yaml", note, fixed, note if fixed else ""))
            elif ext == ".py":
                fixed, note = try_fix_python(file_path)
                issues.append(Issue(rel, "python", note, fixed, note if fixed else ""))
            elif name in {"dockerfile"} or ext == ".dockerfile":
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                msg = "Dockerfile missing FROM" if "FROM" not in text.upper() else "Dockerfile ok"
                issues.append(Issue(rel, "docker", msg))
            else:
                if ext in CODE_EXTS or file_path.stat().st_size < 2_000_000:
                    text = file_path.read_text(encoding="utf-8", errors="ignore")
                    matches = re.findall(r"\b(TODO|FIXME|XXX|TBD)\b", text, re.I)
                    if matches:
                        issues.append(
                            Issue(
                                rel,
                                "todo",
                                f"Found {len(matches)} TODO-like markers",
                            )
                        )
        except Exception as exc:  # pragma: no cover - defensive guard
            issues.append(Issue(rel, "error", f"Scan failed: {exc}"))
    return issues


def write_reports(
    issues: Sequence[Issue],
    out_dir: Path,
    csv_path: Path | None = None,
    md_path: Path | None = None,
) -> Tuple[Path | None, Path | None]:
    report_dir = out_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    csv_target = csv_path or report_dir / "scan_issues.csv"
    md_target = md_path or report_dir / "SUMMARY.md"

    if pd is not None:
        df = pd.DataFrame([issue.to_dict() for issue in issues])
        df.to_csv(csv_target, index=False)
    else:  # pragma: no cover - fallback when pandas missing
        lines = ["file,type,message,fixed,fix_note"]
        for issue in issues:
            lines.append(",".join(issue.to_dict().values()))
        csv_target.write_text("\n".join(lines), encoding="utf-8")

    summary = [
        f"# Auto-Debug Report ({timestamp()})",
        "",
        f"- Files scanned: {len(issues)}",
        f"- Issues found: {len(issues)}",
        "",
        "## Notes",
        "- JSON files were auto-sanitized (comments and trailing commas removed) where possible.",
        "- Python files were parsed; trivial missing ':' on block headers were auto-fixed when safe.",
        "- YAML files were validated; no automatic edits applied.",
        "- package.json files received minimal defaults if critical fields were missing.",
    ]
    md_target.write_text("\n".join(summary) + "\n", encoding="utf-8")
    return csv_target, md_target


def copy_workspace(staging_dirs: Sequence[Path], output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for staged in staging_dirs:
        dest = output_dir / staged.name
        shutil.copytree(staged, dest, dirs_exist_ok=True)


def build_zip(source_dir: Path) -> Path:
    zip_path = source_dir.with_suffix(".zip")
    shutil.make_archive(str(zip_path.with_suffix("")), "zip", source_dir)
    return zip_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    ts = timestamp()

    workspace = args.workspace or Path(ROOT, f"workspace_{ts}")
    outdir = args.out or Path(ROOT, f"fixed_{ts}")
    workspace.mkdir(parents=True, exist_ok=True)

    archives = existing_archives(args.root, args.archives)
    if not archives:
        print("No archives found; nothing to do.")
        return 0

    staged_dirs: List[Path] = []
    for archive in archives:
        dest = workspace / archive.stem
        dest.mkdir(parents=True, exist_ok=True)
        safe_extract(archive, dest)
        staged_dirs.append(dest)

    all_files: List[Path] = []
    for staged in staged_dirs:
        all_files.extend(list(discover_files(staged)))

    issues = scan_files(all_files, workspace)

    if not args.no_copy:
        copy_workspace(staged_dirs, outdir)

    csv_path, md_path = write_reports(issues, outdir, args.report_csv, args.report_md)

    if args.zip_output:
        zip_path = build_zip(outdir)
        print(f"Packaged output: {zip_path}")

    print("Scan complete.")
    print(f"Workspace: {workspace}")
    if not args.no_copy:
        print(f"Output: {outdir}")
    if csv_path:
        print(f"CSV report: {csv_path}")
    if md_path:
        print(f"Markdown summary: {md_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
