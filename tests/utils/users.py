from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from tests.utils.utils import random_lower_string
from app.crud.user_crud import create_user
from app.core.security import hash_password
from app.schemas.user_schema import UserCreate
from app.models import User

@dataclass
class UserFactory:
    """
    Class for tests purposes only, saves User object and his plain password,
    in real User model, password saved only in hash
    """
    user: User
    password: str

async def create_random_user_factory(db_session: AsyncSession) -> UserFactory:
    user_body = UserCreate(username=random_lower_string(),
                           email=f"{random_lower_string()}@{random_lower_string()}.com",
                           password=random_lower_string())
    random_password_hash = hash_password(user_body.password)
    random_user = await create_user(db_session, user_body, random_password_hash)
    return UserFactory(user=random_user, password=user_body.password)

async def user_token(db_session: AsyncSession,
                     client: AsyncClient,
                     username: str | None = None,
                     password: str | None = None) -> dict:
    if username is None or password is None:
        factory = await create_random_user_factory(db_session)

    response = await client.post(
        "/auth/login",
        data={"username": username or factory.user.username, "password": password or factory.password}
    )
    access_token = response.json()["access_token"]
    headers = {"access_token": access_token,
               "token_type": "bearer",
               "headers": {"Authorization": f"Bearer {access_token}"}}
    return headers