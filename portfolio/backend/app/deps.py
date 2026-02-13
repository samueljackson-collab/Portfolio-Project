"""Dependency shortcuts."""
from __future__ import annotations

from .auth import get_current_user
from .db import get_session

__all__ = ["get_session", "get_current_user"]
