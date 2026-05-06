import pytest

from fakeredis import FakeAsyncRedis
from unittest.mock import patch

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from httpx import ASGITransport, AsyncClient

from app.database import Base, get_async_session
from app.main import app



TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    url=TEST_DATABASE_URL,
    poolclass=StaticPool
)
TestSession = async_sessionmaker(bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False)

@pytest.fixture
async def db_session():
    async with test_engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSession() as session:
        yield session
    async with test_engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_async_session():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
async def mock_redis():
    fake = FakeAsyncRedis(decode_responses=True)
    with patch("app.core.redis_client.redis_client", fake):
        yield fake