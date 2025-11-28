"""Phase-aware diagram inventory and validation helper.

This script groups projects into four phases for diagram-focused work. Use it to
list the diagram assets expected in each phase and to verify that both the
Mermaid sources and rendered artifacts are present alongside README references.

Example usage:

    python tools/generate_phase1_diagrams.py --list phase1
    python tools/generate_phase1_diagrams.py --check phase2 phase3

"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DiagramExpectation:
    """Represents the expected diagram artifacts for a project."""

    name: str
    relative_files: tuple[str, ...]

    def existing_files(self, base_dir: Path) -> list[Path]:
        return [base_dir / rel for rel in self.relative_files if (base_dir / rel).exists()]

    def missing_files(self, base_dir: Path) -> list[Path]:
        return [base_dir / rel for rel in self.relative_files if not (base_dir / rel).exists()]


@dataclass(frozen=True)
class PhaseProject:
    slug: str
    base_dir: Path
    readme: str
    diagrams: tuple[DiagramExpectation, ...]

    def diagram_summary(self) -> list[str]:
        summary: list[str] = []
        for diagram in self.diagrams:
            summary.append(f"- {diagram.name}: {', '.join(diagram.relative_files)}")
        return summary

    def validate(self) -> list[str]:
        errors: list[str] = []
        for diagram in self.diagrams:
            missing = diagram.missing_files(self.base_dir)
            if missing:
                errors.append(
                    f"{self.slug} missing files for {diagram.name}: "
                    + ", ".join(str(path.relative_to(REPO_ROOT)) for path in missing)
                )

        readme_path = self.base_dir / self.readme
        if not readme_path.exists():
            errors.append(f"{self.slug} missing README at {readme_path.relative_to(REPO_ROOT)}")
        else:
            content = readme_path.read_text(encoding="utf-8")
            for diagram in self.diagrams:
                if not any(rel in content for rel in diagram.relative_files):
                    errors.append(
                        f"{self.slug} README missing reference to {diagram.name} diagrams"
                    )
        return errors


PHASES: dict[str, list[PhaseProject]] = {
    "phase1": [
        PhaseProject(
            slug="PRJ-SDE-001",
            base_dir=REPO_ROOT / "projects/01-sde-devops/PRJ-SDE-001",
            readme="README.md",
            diagrams=(
                DiagramExpectation(
                    name="Database infrastructure",
                    relative_files=(
                        "assets/diagrams/database-infrastructure.mermaid",
                        "assets/diagrams/database-infrastructure.md",
                    ),
                ),
            ),
        ),
        PhaseProject(
            slug="PRJ-SDE-002",
            base_dir=REPO_ROOT / "projects/01-sde-devops/PRJ-SDE-002",
            readme="README.md",
            diagrams=(
                DiagramExpectation(
                    name="Observability architecture",
                    relative_files=(
                        "assets/diagrams/observability-architecture.mermaid",
                        "assets/diagrams/observability-architecture.md",
                    ),
                ),
            ),
        ),
    ],
    "phase2": [
        PhaseProject(
            slug="PRJ-HOME-001",
            base_dir=REPO_ROOT / "projects/06-homelab/PRJ-HOME-001",
            readme="README.md",
            diagrams=(
                DiagramExpectation(
                    name="Homelab logical VLAN map",
                    relative_files=(
                        "assets/diagrams/logical-vlan-map.mermaid",
                        "assets/diagrams/logical-vlan-map.md",
                    ),
                ),
                DiagramExpectation(
                    name="Physical topology",
                    relative_files=(
                        "assets/diagrams/physical-topology.mermaid",
                        "assets/diagrams/physical-topology.md",
                    ),
                ),
            ),
        ),
    ],
    "phase3": [
        PhaseProject(
            slug="PRJ-HOME-002",
            base_dir=REPO_ROOT / "projects/06-homelab/PRJ-HOME-002",
            readme="README.md",
            diagrams=(
                DiagramExpectation(
                    name="Network topology",
                    relative_files=(
                        "assets/diagrams/network-topology.mmd",
                        "assets/diagrams/network-topology.md",
                    ),
                ),
                DiagramExpectation(
                    name="Service architecture",
                    relative_files=(
                        "assets/diagrams/service-architecture.mmd",
                        "assets/diagrams/service-architecture.md",
                    ),
                ),
                DiagramExpectation(
                    name="Virtualization architecture",
                    relative_files=(
                        "assets/diagrams/virtualization-architecture.mermaid",
                        "assets/diagrams/virtualization-architecture.md",
                    ),
                ),
                DiagramExpectation(
                    name="Monitoring architecture",
                    relative_files=(
                        "assets/diagrams/monitoring-architecture.mmd",
                        "assets/diagrams/monitoring-architecture.md",
                    ),
                ),
                DiagramExpectation(
                    name="Disaster recovery flow",
                    relative_files=(
                        "assets/diagrams/disaster-recovery-flow.mmd",
                        "assets/diagrams/disaster-recovery-flow.md",
                    ),
                ),
                DiagramExpectation(
                    name="Backup & recovery",
                    relative_files=(
                        "assets/diagrams/backup-recovery.mmd",
                        "assets/diagrams/backup-recovery.md",
                    ),
                ),
                DiagramExpectation(
                    name="Data flow",
                    relative_files=(
                        "assets/diagrams/data-flow.mmd",
                        "assets/diagrams/data-flow.md",
                    ),
                ),
            ),
        ),
    ],
    "phase4": [
        PhaseProject(
            slug="PRJ-HOME-004",
            base_dir=REPO_ROOT / "projects/06-homelab/PRJ-HOME-004",
            readme="README.md",
            diagrams=(
                DiagramExpectation(
                    name="Architecture overview",
                    relative_files=("assets/diagrams/architecture-overview.mermaid",),
                ),
                DiagramExpectation(
                    name="Firewall policy",
                    relative_files=("assets/diagrams/firewall-policy.mermaid",),
                ),
                DiagramExpectation(
                    name="Implementation timeline",
                    relative_files=("assets/diagrams/implementation-timeline.mermaid",),
                ),
                DiagramExpectation(
                    name="Backup strategy",
                    relative_files=("assets/diagrams/backup-strategy.mermaid",),
                ),
                DiagramExpectation(
                    name="Risk assessment matrix",
                    relative_files=("assets/diagrams/risk-assessment-matrix.mermaid",),
                ),
            ),
        ),
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list",
        nargs="*",
        metavar="PHASE",
        help="List expected diagrams for the given phases (default: all phases)",
    )
    parser.add_argument(
        "--check",
        nargs="*",
        metavar="PHASE",
        help="Validate files and README references for the given phases (default: all phases)",
    )
    return parser.parse_args()


def _phases_from_args(selected: Iterable[str] | None) -> list[str]:
    if selected:
        unknown = sorted(set(selected) - set(PHASES))
        if unknown:
            raise SystemExit(f"Unknown phase(s): {', '.join(unknown)}")
        return list(dict.fromkeys(selected))
    return list(PHASES)


def list_phase(phase: str) -> None:
    print(f"\n{phase.upper()} — {len(PHASES[phase])} project(s)")
    for project in PHASES[phase]:
        print(f"  {project.slug} ({project.base_dir.relative_to(REPO_ROOT)})")
        for line in project.diagram_summary():
            print(f"    {line}")


def check_phase(phase: str) -> int:
    failures = 0
    for project in PHASES[phase]:
        for error in project.validate():
            failures += 1
            print(f"[FAIL] {error}")
    if failures == 0:
        print(f"[OK] {phase} diagrams and README references validated")
    return failures


def main() -> None:
    args = parse_args()
    list_phases = _phases_from_args(args.list)
    check_phases = _phases_from_args(args.check)

    if args.list is not None:
        for phase in list_phases:
            list_phase(phase)

    if args.check is not None:
        failures = 0
        for phase in check_phases:
            failures += check_phase(phase)
        if failures:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
