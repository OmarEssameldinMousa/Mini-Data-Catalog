from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import get_settings

engine = None 
AsyncSessionFactory = None 

async def init_db():
    global engine, AsyncSessionFactory
    settings = get_settings()
    database_url = settings.database_url
    engine = create_async_engine(database_url, echo=settings.debug)
    AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)

async def close_db():
    global engine
    if engine:
        await engine.dispose()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if AsyncSessionFactory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with AsyncSessionFactory() as session:
        yield session
