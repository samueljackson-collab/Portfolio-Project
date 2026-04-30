"""FastAPI application entrypoint."""
from __future__ import annotations

import os
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import auth, models, schemas
from .auth import get_current_user, get_password_hash
from .db import SessionLocal, get_session, init_db

DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "changeme")

app = FastAPI(title="Portfolio API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
    async with SessionLocal() as session:
        result = await session.execute(
            select(models.User).where(models.User.username == DEFAULT_ADMIN_USERNAME)
        )
        user = result.scalars().first()
        if user is None:
            session.add(
                models.User(
                    username=DEFAULT_ADMIN_USERNAME,
                    hashed_password=get_password_hash(DEFAULT_ADMIN_PASSWORD),
                )
            )
            await session.commit()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/token", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> schemas.Token:
    return await auth.issue_token(form_data, session)


@app.get("/projects", response_model=List[schemas.ProjectRead])
async def list_projects(
    session: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
) -> List[schemas.ProjectRead]:
    result = await session.execute(
        select(models.Project).where(models.Project.owner_id == current_user.id)
    )
    projects = result.scalars().all()
    return [schemas.ProjectRead.model_validate(project) for project in projects]


@app.post("/projects", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: schemas.ProjectCreate,
    session: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.ProjectRead:
    new_project = models.Project(
        title=project.title, description=project.description, owner_id=current_user.id
    )
    session.add(new_project)
    await session.commit()
    await session.refresh(new_project)
    return schemas.ProjectRead.model_validate(new_project)


@app.get("/projects/{project_id}", response_model=schemas.ProjectRead)
async def read_project(
    project_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.ProjectRead:
    result = await session.execute(
        select(models.Project).where(
            models.Project.id == project_id, models.Project.owner_id == current_user.id
        )
    )
    project = result.scalars().first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return schemas.ProjectRead.model_validate(project)
