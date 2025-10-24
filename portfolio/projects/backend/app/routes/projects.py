from typing import Iterable

from fastapi import APIRouter

from app.models import Project
from app.services.projects import list_projects

router = APIRouter(prefix="/api", tags=["projects"])


@router.get("/projects", response_model=list[Project])
def get_projects() -> Iterable[Project]:
    return list_projects()
