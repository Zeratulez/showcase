from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas import user_schema

async def get_user_by_id(session: AsyncSession, user_id: int):
    return await session.get(User, user_id)

async def get_user_by_username(session: AsyncSession, username: str):
    query = select(User).filter(User.username == username)
    return await session.scalar(query)

async def get_user_by_email(session: AsyncSession, email: str):
    query = select(User).filter(User.email == email)
    return await session.scalar(query)

async def create_user(session: AsyncSession, user: user_schema.UserCreate, hashed_password: str):
    new_user = User(**user.model_dump(exclude={"password"}), hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def change_password(session: AsyncSession, user: User, hashed_password: str):
    user.hashed_password = hashed_password
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"message": "Password changed successfully"}

async def check_user_exists(session: AsyncSession, username: str, email: str):
    query = select(
        exists().where(User.username == username).label("username_taken"),
        exists().where(User.email == email).label("email_taken"),
    )
    result = await session.execute(query)
    row = result.one()
    return {"username_taken": row.username_taken, "email_taken": row.email_taken}