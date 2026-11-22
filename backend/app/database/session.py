from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from backend.app.config import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False, "timeout": 30.0} if "sqlite" in settings.DATABASE_URL else {}
)

# Create sessionmaker
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing database sessions per request."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initializes database schema tables."""
    from backend.app.database.base import Base
    # Import all models to register them on Base.metadata
    import backend.app.database.models  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
