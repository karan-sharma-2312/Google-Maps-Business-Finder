"""Database initialization helpers."""

from __future__ import annotations

from app.database.session import engine
from app.models import Base


async def init_db() -> None:
    """Create database tables for local development."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
