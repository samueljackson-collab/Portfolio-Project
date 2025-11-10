"""
Authentication and authorization utilities.

This module provides:
- Password hashing and verification using bcrypt
- JWT token generation and validation
- User authentication helpers
- Token decoding with expiration handling

Security Considerations:
- Passwords are never stored in plain text
- bcrypt automatically handles salt generation
- JWT tokens expire after 30 minutes by default
- Token signature prevents tampering
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.config import settings


# Password hashing context using bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    bcrypt automatically generates a unique salt for each password,
    so two users with the same password will have different hashes.

    Args:
        password: Plain text password from user input

    Returns:
        str: Hashed password safe for database storage
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches a stored hashed password.
    
    Performs a constant-time comparison to prevent timing attacks.
    
    Parameters:
        plain_password (str): Password provided by the user.
        hashed_password (str): Stored hashed password to verify against.
    
    Returns:
        bool: True if the password matches the hashed password, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with expiration.

    The token contains:
    - sub: Subject (usually user ID)
    - exp: Expiration timestamp
    - iat: Issued at timestamp
    - Any additional claims passed in data

    Args:
        data: Dictionary of claims to encode in token
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token

    Security Note:
        The token is signed but NOT encrypted. Don't put sensitive
        data like passwords or credit cards in the payload!
    """
    to_encode = data.copy()

    # Calculate expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    # Add standard claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
    })

    # Encode and sign the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.
    
    Verifies the token signature and expiration, and ensures the payload contains a non-null "sub" (subject) claim.
    
    Parameters:
        token (str): JWT token string (typically from the Authorization header).
    
    Returns:
        dict: Decoded token payload.
    
    Raises:
        HTTPException: HTTP 401 when the token is invalid, expired, or missing the "sub" claim.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token with signature verification
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        # Extract subject (user identifier)
        user_identifier: str = payload.get("sub")
        if user_identifier is None:
            raise credentials_exception

        return payload

    except JWTError as e:
        raise credentials_exception from e