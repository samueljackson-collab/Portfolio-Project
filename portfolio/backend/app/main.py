from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .db import Base, engine, get_session
from .models import User
from .schemas import UserCreate, Token
from .auth import hash_pw, verify_pw, make_token
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="Portfolio API")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/register", status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    user = User(email=payload.email, password_hash=hash_pw(payload.password))
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        return {"id": user.id, "email": user.email}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email exists")


@app.post("/api/auth/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(User).where(User.email == form.username))
    user = res.scalar_one_or_none()
    if not user or not verify_pw(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Bad credentials")
    return {"access_token": make_token(str(user.id))}
