"""
Author: Senthie seemoon2077@gmail.com
Date: 2025-12-24 16:24:52
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-12 11:29:10
FilePath: /api/app/core/pg_database.py
Description:PostgreSQL database connection and session management.

Copyright (c) 2026 by Senthie email: seemoon2077@gmail.com, All Rights Reserved.
"""

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

# Lazily-created engine and session factory to avoid binding to a closed event loop
engine: Optional[AsyncEngine] = None
# internal sessionmaker; exported `AsyncSessionLocal` below is a callable wrapper
_sessionmaker: Optional[async_sessionmaker] = None


def _create_engine_and_sessionmaker() -> None:
    """Create the async engine and sessionmaker if not already created.

    This function is synchronous because create_async_engine does not
    require an active event loop to construct. Deferring creation until the
    application or task is running avoids tying internal resources to a
    possibly-closed loop created earlier.
    """
    global engine, _sessionmaker
    if engine is None:
        engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
        )
        _sessionmaker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )


class _SessionFactory:
    """Callable wrapper that returns a new AsyncSession context manager.

    This object is safe to import at module import time; when called it
    ensures the engine and sessionmaker are created under the current
    runtime context and returns the sessionmaker instance's call result.
    """

    def __call__(self):
        _create_engine_and_sessionmaker()
        assert _sessionmaker is not None
        return _sessionmaker()


# Backwards-compatible exported name used across the codebase. Modules that
# did `from app.core.pg_database import AsyncSessionLocal` will get this
# callable object and can continue to use `async with AsyncSessionLocal() ...`.
AsyncSessionLocal = _SessionFactory()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session.

    Yields:
        AsyncSession: Database session
    """
    _create_engine_and_sessionmaker()
    assert _sessionmaker is not None
    async with _sessionmaker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    _create_engine_and_sessionmaker()
    assert engine is not None
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    if engine is not None:
        await engine.dispose()
