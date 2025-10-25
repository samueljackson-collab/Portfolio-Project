from fastapi import FastAPI

from .config import get_settings
from .database import Base, engine
from .routers import auth, content, health

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(content.router)


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
