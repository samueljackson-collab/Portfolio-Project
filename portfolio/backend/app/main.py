from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import api_router
from .db import Base, get_engine


@asynccontextmanager
def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Portfolio API", lifespan=lifespan)
app.include_router(api_router)
