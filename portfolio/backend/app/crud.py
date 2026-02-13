from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_password_hash, verify_password
from .models import Content, User


async def create_user(session: AsyncSession, email: str, password: str) -> User:
    user = User(email=email, password_hash=get_password_hash(password))
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError("Email already registered")
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.password_hash):
        return user
    return None


async def create_content(session: AsyncSession, *, owner_id: int, title: str, slug: str, body: str) -> Content:
    content = Content(owner_id=owner_id, title=title, slug=slug, body=body)
    session.add(content)
    await session.commit()
    await session.refresh(content)
    return content


async def list_content(session: AsyncSession, owner_id: int) -> list[Content]:
    result = await session.execute(select(Content).where(Content.owner_id == owner_id))
    return list(result.scalars())


async def get_content(session: AsyncSession, content_id: int, owner_id: int) -> Content | None:
    result = await session.execute(
        select(Content).where(Content.id == content_id, Content.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def update_content(
    session: AsyncSession,
    *,
    db_obj: Content,
    title: str | None = None,
    slug: str | None = None,
    body: str | None = None,
) -> Content:
    if title is not None:
        db_obj.title = title
    if slug is not None:
        db_obj.slug = slug
    if body is not None:
        db_obj.body = body
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def delete_content(session: AsyncSession, db_obj: Content) -> None:
    await session.delete(db_obj)
    await session.commit()
