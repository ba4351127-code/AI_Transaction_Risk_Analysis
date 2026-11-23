from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from backend.app.config import settings

# Normalize database URL: seamlessly supports Neon/PostgreSQL asyncpg and local SQLite
def _get_async_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if "asyncpg" in url and "sslmode=" in url:
        url = url.replace("sslmode=", "ssl=")
    return url

_db_url = _get_async_database_url(settings.DATABASE_URL)

# Create async engine with connection pooling
engine = create_async_engine(
    _db_url,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False, "timeout": 30.0} if "sqlite" in _db_url else {}
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
