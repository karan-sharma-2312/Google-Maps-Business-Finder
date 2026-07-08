"""Statistics API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication import require_api_key
from app.database.session import get_db_session
from app.repositories import HistoryRepository

router = APIRouter(prefix="/statistics", tags=["statistics"], dependencies=[Depends(require_api_key)])


@router.get("/summary")
async def get_summary(session: AsyncSession = Depends(get_db_session)) -> dict[str, int]:
    """Return summary statistics from persisted history records."""
    repo = HistoryRepository(session)
    return await repo.get_statistics()
