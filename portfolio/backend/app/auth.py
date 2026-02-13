from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.hash import bcrypt

SECRET = "CHANGE_ME"
ALGO = "HS256"
ACCESS_MIN = 30


def hash_pw(pw: str) -> str:
    return bcrypt.hash(pw)


def verify_pw(pw: str, hashed: str) -> bool:
    return bcrypt.verify(pw, hashed)


def make_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=ACCESS_MIN)).timestamp())}
    return jwt.encode(payload, SECRET, algorithm=ALGO)
