"""Bootstrap generator for the portfolio starter tree."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STARTER_FILES = {
    "README.md": "# Portfolio Monorepo (Starter)\n\nThis file is managed by tools/bootstrap.py.\n",
    "Makefile": "SHELL := /bin/bash\n\n.PHONY: dev\n\ndev:\n\t@echo 'Starter makefile placeholder'\n",
    "backend/app/main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/health')\ndef health():\n    return {'status': 'ok'}\n",
    "frontend/src/main.tsx": "import React from 'react'\nimport ReactDOM from 'react-dom/client'\n\nReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(<React.StrictMode>Starter</React.StrictMode>)\n",
    "compose/docker-compose.yml": "version: '3.9'\nservices:\n  web:\n    image: nginx:alpine\n"
}


def write(path: Path, content: str, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def generate(check_only: bool = False, overwrite: bool = False) -> list[Path]:
    created: list[Path] = []
    for relative, content in STARTER_FILES.items():
        target = ROOT / relative
        if check_only and target.exists():
            continue
        write(target, content, overwrite=overwrite)
        created.append(target)
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate starter project files.")
    parser.add_argument("--check", action="store_true", help="Only report missing files")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    created = generate(check_only=args.check, overwrite=args.force)
    if args.check:
        missing = [path for path in (ROOT / rel for rel in STARTER_FILES) if not path.exists()]
        if missing:
            print("Missing starter files:")
            for path in missing:
                print(f" - {path.relative_to(ROOT)}")
        else:
            print("All starter files are present.")
    else:
        for path in created:
            print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
