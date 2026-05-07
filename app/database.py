from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

async_engine = create_async_engine(
    url=settings.ASYNC_DATABASE_URL,
)

AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session