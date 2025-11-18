from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


engine = create_async_engine(str(settings.database_url), future=True, echo=False)
SessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    from app import models

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def drop_db() -> None:
    from app import models

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
