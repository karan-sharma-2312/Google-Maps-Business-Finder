"""Central API router composition.

This module aggregates versioned and domain-specific routers into a single
router object that can be mounted by the FastAPI application.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes.analysis import router as analysis_router
from app.api.routes.discovery import router as discovery_router
from app.api.routes.statistics import router as statistics_router
from app.api.routes.system import router as system_router

api_router = APIRouter()
api_router.include_router(system_router)
api_router.include_router(discovery_router)
api_router.include_router(analysis_router)
api_router.include_router(statistics_router)
