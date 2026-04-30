import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils import create_random_user_factory, UserFactory, random_lower_string
from app.crud.user_crud import (
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    change_password,
    check_user_exists,
)

@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    return await create_random_user_factory(db_session)

async def test_get_user_by_id(db_session: AsyncSession, test_user: UserFactory):
    user = await get_user_by_id(db_session, test_user.user.id)
    assert user is not None
    assert user.username == test_user.user.username
    assert user.id == test_user.user.id
    assert user.email == test_user.user.email

async def test_get_user_by_id_not_found(db_session: AsyncSession):
    user = await get_user_by_id(db_session, "-1")
    assert user is None

async def test_get_user_by_username(db_session: AsyncSession, test_user: UserFactory):
    user = await get_user_by_username(db_session, test_user.user.username)
    assert user is not None
    assert user.username == test_user.user.username
    assert user.id == test_user.user.id
    assert user.email == test_user.user.email

async def test_get_user_by_username_not_found(db_session: AsyncSession):
    user = await get_user_by_username(db_session, "-1")
    assert user is None

async def test_get_user_by_email(db_session: AsyncSession, test_user: UserFactory):
    user = await get_user_by_email(db_session, test_user.user.email)
    assert user is not None
    assert user.username == test_user.user.username
    assert user.id == test_user.user.id
    assert user.email == test_user.user.email

async def test_get_user_by_email_not_found(db_session: AsyncSession):
    user = await get_user_by_email(db_session, "-1")
    assert user is None

async def test_change_password(db_session: AsyncSession, test_user: UserFactory):
    new_password = random_lower_string()
    message = await change_password(db_session, test_user.user, new_password)
    assert message == {"message": "Password changed successfully"}
    assert test_user.user.hashed_password == new_password

async def test_check_user_exists_username(db_session: AsyncSession, test_user: UserFactory):
    check = await check_user_exists(db_session, test_user.user.username, test_user.user.email)
    assert check["username_taken"] is True

async def test_check_user_exists_email(db_session: AsyncSession, test_user: UserFactory):
    check = await check_user_exists(db_session, test_user.user.username, test_user.user.email)
    assert check["email_taken"] is True

async def test_check_user_exists_username_and_email(db_session: AsyncSession, test_user: UserFactory):
    check = await check_user_exists(db_session, test_user.user.username, test_user.user.email)
    assert check["username_taken"] is True
    assert check["email_taken"] is True
