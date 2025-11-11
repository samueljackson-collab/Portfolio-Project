import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings
from app.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()


def get_url() -> str:
    return settings.database_url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_async_engine(get_url(), poolclass=pool.NullPool)

    async def do_run_migrations(connection: Connection) -> None:
        await connection.run_sync(Base.metadata.create_all)
        context.configure(connection=connection, target_metadata=Base.metadata)

        with context.begin_transaction():
            context.run_migrations()

    async def run_async_migrations() -> None:
        async with connectable.connect() as connection:
            await do_run_migrations(connection)

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
