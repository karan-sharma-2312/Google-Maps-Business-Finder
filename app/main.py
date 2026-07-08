"""FastAPI application entrypoint.

This module builds the ASGI application instance using a factory pattern,
initializes cross-cutting concerns, and exposes baseline operational routes.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config.settings import Settings, get_settings
from app.core.logging import configure_logging, get_logger
from app.database import init_db
from app.middleware import RateLimitMiddleware


def _configure_cors(application: FastAPI, settings: Settings) -> None:
    """Attach CORS middleware using configured allowed origins."""
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown events."""
    configure_logging()
    settings = get_settings()
    logger = get_logger({"component": "api-lifespan"})

    logger.info(
        "Starting API service: name={}, version={}, env={}",
        settings.app.name,
        settings.app.version,
        settings.app.environment.value,
    )

    settings.paths.data_dir.mkdir(parents=True, exist_ok=True)
    settings.paths.log_dir.mkdir(parents=True, exist_ok=True)
    settings.paths.export_dir.mkdir(parents=True, exist_ok=True)
    await init_db()

    yield

    logger.info("Shutting down API service")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application instance.

    Args:
        settings: Optional settings object for tests and explicit wiring.

    Returns:
        Configured FastAPI application.
    """
    settings = settings or get_settings()

    docs_enabled = settings.app.environment.value != "production"

    application = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
        debug=settings.app.debug,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
        lifespan=lifespan,
    )

    _configure_cors(application, settings)
    application.add_middleware(RateLimitMiddleware, requests_per_minute=settings.security.rate_limit_per_minute)
    application.include_router(api_router)

    return application


app = create_app()
