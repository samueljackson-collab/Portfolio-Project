from __future__ import annotations
from pathlib import Path
import json

ARTIFACT = Path("artifacts/site_snapshot.json")
ARTIFACT.parent.mkdir(exist_ok=True)


def generate_pages() -> list[dict]:
    return [
        {"path": "/", "title": "Home", "content": "Welcome to the portfolio."},
        {"path": "/projects", "title": "Projects", "content": "Project listing placeholder."},
    ]


def main():
    pages = generate_pages()
    snapshot = {"pages": pages, "deployed": True}
    ARTIFACT.write_text(json.dumps(snapshot, indent=2))
    print("Portfolio website demo complete. See artifacts/site_snapshot.json")


if __name__ == "__main__":
    main()
