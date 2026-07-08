"""Repository for search and export history."""

from __future__ import annotations

import json

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import ExportHistoryEntity, SearchHistoryEntity


class HistoryRepository:
    """Data access methods for audit and analytics history."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_search_history(
        self,
        source: str,
        query: str,
        location: str | None,
        requested_count: int,
        discovered_count: int,
        output_file: str | None,
    ) -> SearchHistoryEntity:
        """Persist search execution record."""
        entity = SearchHistoryEntity(
            source=source,
            query=query,
            location=location,
            requested_count=requested_count,
            discovered_count=discovered_count,
            output_file=output_file,
        )
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def add_export_history(self, export_type: str, target: str, metadata: dict[str, str] | None = None) -> None:
        """Persist export history record."""
        entity = ExportHistoryEntity(
            export_type=export_type,
            target=target,
            metadata_json=json.dumps(metadata or {}, ensure_ascii=True),
        )
        self._session.add(entity)
        await self._session.commit()

    async def get_statistics(self) -> dict[str, int]:
        """Return simple aggregate statistics for dashboard/API."""
        total_searches = await self._session.scalar(select(func.count()).select_from(SearchHistoryEntity))
        total_exports = await self._session.scalar(select(func.count()).select_from(ExportHistoryEntity))
        total_discovered = await self._session.scalar(select(func.coalesce(func.sum(SearchHistoryEntity.discovered_count), 0)))

        return {
            "total_searches": int(total_searches or 0),
            "total_exports": int(total_exports or 0),
            "total_discovered": int(total_discovered or 0),
        }
