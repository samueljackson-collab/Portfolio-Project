from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS, APP_VERSION
from database import init_db
from routers import health as health_router
from routers import scan as scan_router
from routers import reports as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Bug Hunter API",
    version=APP_VERSION,
    description="Cross-platform static code analysis and vulnerability reporting engine",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router.router)
app.include_router(scan_router.router)
app.include_router(reports_router.router)
