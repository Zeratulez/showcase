from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils.users import create_random_user_factory, user_token
from app.crud.user_crud import get_user_by_email
from app.core.security import verify_password

async def test_user_register(client: AsyncClient):
    data = {"username": "foo",
            "email": "foo@example.com",
            "password": "123"}
    response = await client.post(
        "/auth/register",
        json=data
    )
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == "foo"
    assert user["email"] == "foo@example.com"
    assert "password" not in user

async def test_user_already_exists_username(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    data = {"username": factory.user.username,
            "email": "test@example.com",
            "password": factory.password,}
    response = await client.post(
        "/auth/register",
        json=data
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this nickname already exists"

async def test_user_already_exists_email(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    data = {"username": "foo",
            "email": factory.user.email,
            "password": factory.password,}
    response = await client.post(
        "/auth/register",
        json=data
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"

async def test_register_not_valid_email(db_session: AsyncSession, client: AsyncClient):
    data = {"username": "foo",
            "email": "foofoofoo",
            "password": "123"}
    response = await client.post(
        "/auth/register",
        json=data
    )
    assert response.status_code == 422
    user = await get_user_by_email(db_session, data["email"])
    assert user is None

async def test_login_successful(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    response = await client.post(
        "/auth/login",
        data={"username": factory.user.username, "password": factory.password}
    )
    assert response.status_code == 200
    token = await user_token(db_session, client, factory.user.username, factory.password)
    assert token["access_token"] == response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"

async def test_login_unsuccessful_wrong_username(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    response = await client.post(
        "/auth/login",
        data={"username": "foo", "password": factory.password}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

async def test_login_unsuccessful_wrong_password(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    response = await client.post(
        "/auth/login",
        data={"username": factory.user.username, "password": "123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

async def test_change_password(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    user_headers = await user_token(db_session, client, factory.user.username, factory.password)
    new_password = "123"
    response = await client.post(
        "/me/change_password",
        headers=user_headers["headers"],
        json={"current_password": factory.password, "new_password": new_password}
    )
    assert response.status_code == 200
    verified = verify_password(new_password, factory.user.hashed_password)
    assert verified is True

async def test_change_password_same_password(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    user_headers = await user_token(db_session, client, factory.user.username, factory.password)
    response = await client.post(
        "/me/change_password",
        headers=user_headers["headers"],
        json={"current_password": factory.password, "new_password": factory.password}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "New password cannot be same as current password"

async def test_change_password_wrong_password(db_session: AsyncSession, client: AsyncClient):
    factory = await create_random_user_factory(db_session)
    user_headers = await user_token(db_session, client, factory.user.username, factory.password)
    new_password = "wow"
    response = await client.post(
        "/me/change_password",
        headers=user_headers["headers"],
        json={"current_password": "wrong_password_123", "new_password": new_password}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Incorrect current password"