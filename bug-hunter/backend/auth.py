from fastapi import Header, HTTPException
import config


async def require_api_key(x_api_key: str = Header(default="")) -> None:
    """Dependency that enforces X-API-Key auth when API_KEY env var is configured.

    If API_KEY is not set the application runs in open/local mode and all
    requests are allowed through — this is intentional for developer installs.
    """
    if not config.API_KEY:
        return
    if x_api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
