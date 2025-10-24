"""Generate the starter Portfolio monorepo tree."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, content: str) -> None:
    """Create ``path`` and populate it with ``content``."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip("\n") + "\n", encoding="utf-8")


def main() -> None:
    readme = """# Portfolio Monorepo Starter\n\nGenerated project skeleton with FastAPI backend, React frontend, and infrastructure helpers."""
    write(ROOT / "README.md", readme)

    write(
        ROOT / "portfolio/Makefile",
        """SHELL := /bin/bash\n\n.PHONY: dev up down test fmt build\n\ndev: up\nup:\n\tdocker compose -f compose/docker-compose.yml --env-file compose/.env.example up -d --build\ndown:\n\tdocker compose -f compose/docker-compose.yml --env-file compose/.env.example down -v\ntest:\n\tcd backend && pytest -q --maxfail=1 --disable-warnings --cov=app\nfmt:\n\truff check --fix backend || true; black backend || true; isort backend || true\n\tprettier -w frontend || true; eslint -c frontend/.eslintrc.cjs \"frontend/src/**/*.{ts,tsx}\" || true\nbuild:\n\tcd frontend && npm ci && npm run build\n\tdocker build -t portfolio-frontend:local ./frontend\n\tdocker build -t portfolio-backend:local ./backend""",
    )

    write(
        ROOT / "portfolio/backend/app/main.py",
        """from fastapi import FastAPI, Depends, HTTPException\nfrom sqlalchemy import select\nfrom sqlalchemy.exc import IntegrityError\nfrom .db import Base, engine, get_session\nfrom .models import User\nfrom .schemas import UserCreate, Token\nfrom .auth import hash_pw, verify_pw, make_token\nfrom fastapi.security import OAuth2PasswordRequestForm\nfrom sqlalchemy.ext.asyncio import AsyncSession\n\napp = FastAPI(title=\"Portfolio API\")\n\n\n@app.on_event(\"startup\")\nasync def on_startup():\n    async with engine.begin() as conn:\n        await conn.run_sync(Base.metadata.create_all)\n\n\n@app.get(\"/health\")\ndef health():\n    return {\"status\": \"ok\"}\n\n\n@app.post(\"/api/auth/register\", status_code=201)\nasync def register(payload: UserCreate, db: AsyncSession = Depends(get_session)):\n    user = User(email=payload.email, password_hash=hash_pw(payload.password))\n    db.add(user)\n    try:\n        await db.commit()\n        await db.refresh(user)\n        return {\"id\": user.id, \"email\": user.email}\n    except IntegrityError:\n        await db.rollback()\n        raise HTTPException(status_code=409, detail=\"Email exists\")\n\n\n@app.post(\"/api/auth/login\", response_model=Token)\nasync def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):\n    res = await db.execute(select(User).where(User.email == form.username))\n    user = res.scalar_one_or_none()\n    if not user or not verify_pw(form.password, user.password_hash):\n        raise HTTPException(status_code=401, detail=\"Bad credentials\")\n    return {\"access_token\": make_token(str(user.id))}""",
    )

    write(
        ROOT / "portfolio/backend/app/db.py",
        """from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker\nfrom sqlalchemy.orm import declarative_base\n\nDATABASE_URL = \"postgresql+asyncpg://postgres:postgres@postgres:5432/app\"\nengine = create_async_engine(DATABASE_URL, future=True, echo=False)\nSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)\nBase = declarative_base()\n\n\nasync def get_session() -> AsyncSession:\n    async with SessionLocal() as session:\n        yield session""",
    )

    write(
        ROOT / "portfolio/frontend/src/App.tsx",
        """import { useEffect, useState } from 'react'\nimport axios from './lib/api'\nexport default function App(){\n  const [status,setStatus]=useState('loading')\n  useEffect(()=>{ axios.get('/health').then(res=>setStatus(res.data.status)).catch(()=>setStatus('down')) },[])\n  return <main style={{padding:24}}><h1>Portfolio Frontend</h1><p>API status: {status}</p></main>\n}""",
    )

    write(
        ROOT / "portfolio/frontend/src/main.tsx",
        """import React from 'react'\nimport { createRoot } from 'react-dom/client'\nimport { BrowserRouter } from 'react-router-dom'\nimport App from './App'\ncreateRoot(document.getElementById('root')!).render(<BrowserRouter><App/></BrowserRouter>)""",
    )

    write(
        ROOT / "portfolio/frontend/src/lib/api.ts",
        """import axios from 'axios'\nconst api = axios.create({ baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000' })\nexport default api""",
    )

    write(
        ROOT / "portfolio/frontend/index.html",
        """<!doctype html>\n<html>\n  <head><meta charset=\"UTF-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" /><title>Portfolio</title></head>\n  <body><div id=\"root\"></div><script type=\"module\" src=\"/src/main.tsx\"></script></body>\n</html>""",
    )

    write(
        ROOT / "portfolio/compose/docker-compose.yml",
        """services:\n  backend:\n    image: portfolio-backend:local\n    build: ../backend\n    ports: [\"8000:8000\"]\n    environment:\n      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/app\n    depends_on: [postgres]\n    command: uvicorn app.main:app --host 0.0.0.0 --port 8000\n  frontend:\n    image: portfolio-frontend:local\n    build: ../frontend\n    ports: [\"5173:80\"]\n    environment:\n      - VITE_API_BASE=http://localhost:8000\n    depends_on: [backend]\n  postgres:\n    image: postgres:16\n    ports: [\"5432:5432\"]\n    environment:\n      POSTGRES_USER: postgres\n      POSTGRES_PASSWORD: postgres\n      POSTGRES_DB: app""",
    )

    write(ROOT / "portfolio/compose/.env.example", "VITE_API_BASE=http://localhost:8000")


def __main__() -> None:  # pragma: no cover - backward compat shim
    main()


if __name__ == "__main__":
    main()
