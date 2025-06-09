from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import registry, sessionmaker

from app.settings import settings

table_registry = registry()

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db() as session:
        yield session
