"""Security helpers and dependencies."""

from fastapi import Header, HTTPException, status

from src.config import get_settings


def verify_api_key(x_api_key: str | None = Header(default=None, alias="x-api-key")) -> str:
    """Validate API keys provided with each request."""

    settings = get_settings()
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key.",
            headers={"WWW-Authenticate": "API-Key"},
        )
    if x_api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key provided.",
            headers={"WWW-Authenticate": "API-Key"},
        )
    return x_api_key


def apply_security_headers(headers: dict[str, str]) -> dict[str, str]:
    """Return hardened HTTP response headers."""

    hardened = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "no-referrer",
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
        "Content-Security-Policy": "default-src 'none'",
    }
    hardened.update(headers)
    return hardened
