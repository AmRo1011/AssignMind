"""
AssignMind Backend — Database Configuration

Async SQLAlchemy engine and session factory using asyncpg.
All queries use parameterized statements via ORM (Constitution §III).
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# Async engine — connection pool with sensible defaults
engine = create_async_engine(
    settings.database_url,
    echo=(not settings.is_production),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session factory — produces async sessions
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session.

    Yields a session and ensures it is closed after the request,
    even if an exception occurs.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """
    Verify database connectivity for health checks.

    Returns True if the database is reachable, False otherwise.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        return True
    except Exception:
        return False
