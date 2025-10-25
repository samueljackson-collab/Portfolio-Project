"""Utility script to display current seed projects."""
from __future__ import annotations

from app.services.projects import list_projects


def main() -> None:
    for project in list_projects():
        print(f"- {project.name} ({', '.join(project.tags)}) -> {project.url}")


if __name__ == "__main__":
    main()
