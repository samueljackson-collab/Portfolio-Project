from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.auth import require_admin
from app.database import get_db

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[schemas.ProjectRead])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Project).order_by(models.Project.id))
    return result.scalars().all()


@router.get("/{slug}", response_model=schemas.ProjectRead)
async def get_project(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Project).where(models.Project.slug == slug))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=schemas.ProjectRead)
async def create_project(
    project_in: schemas.ProjectCreate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    existing = await db.execute(select(models.Project).where(models.Project.slug == project_in.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Slug already exists")

    project = models.Project(
        title=project_in.title,
        slug=project_in.slug,
        description=project_in.description,
        category=project_in.category,
        tags=",".join(project_in.tags),
        repo_url=project_in.repo_url,
        live_url=project_in.live_url,
        featured=project_in.featured,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.put("/{slug}", response_model=schemas.ProjectRead)
async def update_project(
    slug: str,
    project_in: schemas.ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    result = await db.execute(select(models.Project).where(models.Project.slug == slug))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in project_in.model_dump(exclude_unset=True).items():
        if field == "tags" and value is not None:
            setattr(project, field, ",".join(value))
        else:
            setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{slug}", status_code=204)
async def delete_project(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    result = await db.execute(select(models.Project).where(models.Project.slug == slug))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)
    await db.commit()
    return None
