"""System and operational API routes.

This module contains endpoints used for service health and runtime checks.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Return basic service health metadata for monitoring checks."""
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app.name,
        "environment": settings.app.environment.value,
        "version": settings.app.version,
    }


@router.get("/ready")
async def ready() -> dict[str, str]:
    """Return readiness status for orchestrators and startup probes."""
    settings = get_settings()
    return {
        "status": "ready",
        "service": settings.app.name,
        "environment": settings.app.environment.value,
    }
