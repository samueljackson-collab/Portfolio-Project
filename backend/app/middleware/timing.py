import time
from typing import Callable
from starlette.requests import Request
from starlette.responses import Response

async def timing_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware that measures request processing time using a monotonic clock.

    Sets X-Process-Time-Ms header on the response.
    """
    request.state._start_time = time.monotonic()
    response: Response = await call_next(request)
    elapsed_ms = (time.monotonic() - request.state._start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
    return response
