from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plaintext password with the stored hash."""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash that can be persisted with the user record."""

    return pwd_context.hash(password)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    """Build a short-lived JWT that callers include on API requests."""

    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    """Create a long-lived JWT that clients can swap for a fresh access token."""

    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes or settings.refresh_token_expire_minutes)
    to_encode = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """Return the decoded JWT payload or ``None`` when validation fails."""

    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
