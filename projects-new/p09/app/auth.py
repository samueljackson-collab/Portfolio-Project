"""Authentication and authorization module."""

import os
from datetime import datetime, timezone, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, Header

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token for user."""
    if expires_delta is None:
        expires_delta = timedelta(hours=24)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": user_id, "exp": expire, "iat": datetime.now(timezone.utc)}

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(authorization: str = Header(None)) -> str:
    """Verify JWT token from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
