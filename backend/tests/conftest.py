import asyncio
import os
from importlib import reload

import pytest
from httpx import ASGITransport, AsyncClient

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

import app.config as config
import app.database as database

# Reload settings and database after setting env
reload(config)
reload(database)

from app.database import init_db, drop_db, get_db
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    await init_db()
    yield
    await drop_db()


@pytest.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
