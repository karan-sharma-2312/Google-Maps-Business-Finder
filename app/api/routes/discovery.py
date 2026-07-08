"""Business discovery API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication import require_api_key
from app.config import get_settings
from app.database.session import get_db_session
from app.repositories import BusinessRepository, HistoryRepository
from app.schemas.business import BusinessSearchResult
from app.services import GoogleMapsDiscoveryService

router = APIRouter(prefix="/discovery", tags=["discovery"], dependencies=[Depends(require_api_key)])


class GoogleMapsDiscoveryRequest(BaseModel):
    """Request payload for Google Maps discovery endpoint."""

    query: str = Field(min_length=2)
    location: str | None = None
    max_results: int = Field(default=20, ge=1, le=200)
    save_json: bool = True


@router.post("/google-maps", response_model=BusinessSearchResult)
async def discover_google_maps(
    payload: GoogleMapsDiscoveryRequest,
    session: AsyncSession = Depends(get_db_session),
) -> BusinessSearchResult:
    """Discover businesses from Google Maps and persist key metadata."""
    settings = get_settings()
    service = GoogleMapsDiscoveryService(settings)

    result = await service.discover(
        query=payload.query,
        location=payload.location,
        max_results=payload.max_results,
    )

    business_repo = BusinessRepository(session)
    history_repo = HistoryRepository(session)

    await business_repo.upsert_many(result.businesses)

    output_file: str | None = None
    if payload.save_json:
        safe_query = payload.query.replace(" ", "_").lower()
        out_path = settings.paths.export_dir / f"api_google_maps_{safe_query}.json"
        saved_path = service.save_json_report(result, Path(out_path))
        output_file = str(saved_path)

    await history_repo.add_search_history(
        source="google_maps",
        query=payload.query,
        location=payload.location,
        requested_count=payload.max_results,
        discovered_count=result.discovered_count,
        output_file=output_file,
    )

    return result
