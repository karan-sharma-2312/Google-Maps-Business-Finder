"""Website and SEO analysis API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication import require_api_key
from app.config import get_settings
from app.database.session import get_db_session
from app.repositories import HistoryRepository
from app.schemas.seo_analysis import SeoAnalysisResult
from app.schemas.website_analysis import WebsiteAnalysisResult
from app.services import SeoAnalyzerService, WebsiteAnalyzerService

router = APIRouter(prefix="/analysis", tags=["analysis"], dependencies=[Depends(require_api_key)])


class WebsiteAnalysisRequest(BaseModel):
    """Request payload for website analysis endpoint."""

    url: HttpUrl
    save_json: bool = True


class SeoAnalysisRequest(BaseModel):
    """Request payload for SEO analysis endpoint."""

    url: HttpUrl
    save_json: bool = True


@router.post("/website", response_model=WebsiteAnalysisResult)
async def analyze_website(
    payload: WebsiteAnalysisRequest,
    session: AsyncSession = Depends(get_db_session),
) -> WebsiteAnalysisResult:
    """Extract website contact and social footprint."""
    settings = get_settings()
    service = WebsiteAnalyzerService(settings)
    result = await run_in_threadpool(service.analyze, str(payload.url))

    history_repo = HistoryRepository(session)
    if payload.save_json:
        domain = str(payload.url).replace("https://", "").replace("http://", "").replace("/", "_")
        out_path = settings.paths.export_dir / f"api_website_{domain}.json"
        saved = await run_in_threadpool(service.save_json_report, result, Path(out_path))
        await history_repo.add_export_history("website_analysis_json", str(saved), {"url": str(payload.url)})

    return result


@router.post("/seo", response_model=SeoAnalysisResult)
async def analyze_seo(
    payload: SeoAnalysisRequest,
    session: AsyncSession = Depends(get_db_session),
) -> SeoAnalysisResult:
    """Analyze on-page SEO and return score plus improvements."""
    settings = get_settings()
    service = SeoAnalyzerService(settings)
    result = await run_in_threadpool(service.analyze, str(payload.url))

    history_repo = HistoryRepository(session)
    if payload.save_json:
        domain = str(payload.url).replace("https://", "").replace("http://", "").replace("/", "_")
        out_path = settings.paths.export_dir / f"api_seo_{domain}.json"
        saved = await run_in_threadpool(service.save_json_report, result, Path(out_path))
        await history_repo.add_export_history("seo_analysis_json", str(saved), {"url": str(payload.url)})

    return result
