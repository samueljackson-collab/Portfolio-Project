"""
Shared rate limiter instance.

Defined here (not in main.py) to avoid circular imports: routers need to
import the limiter, but main.py imports the routers.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
