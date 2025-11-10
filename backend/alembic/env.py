"""
Alembic environment configuration with async SQLAlchemy support.

This module configures Alembic to work with async SQLAlchemy engines
and provides both online (connected to DB) and offline (SQL script generation) modes.
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings
from app.database import Base
from app.models import User, Content  # Import all models for autogenerate

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with value from settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Configure the Alembic context to emit SQL migration scripts without connecting to a database.
    
    Sets the context using the configured database URL and target metadata, enables literal binds and comparison options, then runs migrations within a transaction so SQL is written to the script output rather than executed against a live DB.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Run Alembic migrations using the provided SQLAlchemy Connection.
    
    Parameters:
        connection (Connection): Active SQLAlchemy Connection in which migrations will be executed.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in online mode using an async SQLAlchemy engine.
    
    Creates an async engine from the Alembic config overridden with the application's database URL, opens an async connection, executes migrations within that connection, and disposes the engine when finished.
    """
    # Get configuration for async engine
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url

    # Create async engine
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Run migrations synchronously within async context
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Execute the asynchronous migration workflow to apply migrations using the application's database configuration.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()