from fastapi import APIRouter
from config import APP_VERSION

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "version": APP_VERSION}
