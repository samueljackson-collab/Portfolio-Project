import importlib
from typing import Any

import pytest_asyncio
from httpx import AsyncClient


def _load_application() -> Any:
    module_candidates = (
        "backend.main",
        "backend.app",
        "app.main",
        "app",
    )
    last_error: Exception | None = None
    for module_name in module_candidates:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            last_error = exc
            continue

        if hasattr(module, "create_app"):
            app = module.create_app()  # type: ignore[attr-defined]
            if app is not None:
                return app

        app = getattr(module, "app", None)
        if app is not None:
            return app

    raise RuntimeError(
        "Unable to locate an ASGI application. Ensure the backend exposes "
        "an 'app' instance or 'create_app' factory in backend.main."
    ) from last_error


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    app = _load_application()
    await app.router.startup()
    try:
        async with AsyncClient(app=app, base_url="http://testserver") as async_client:
            yield async_client
    finally:
        await app.router.shutdown()
