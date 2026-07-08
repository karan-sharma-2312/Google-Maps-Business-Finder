"""Route modules package."""

from app.api.routes.analysis import router as analysis_router
from app.api.routes.discovery import router as discovery_router
from app.api.routes.statistics import router as statistics_router
from app.api.routes.system import router as system_router

__all__ = ["system_router", "discovery_router", "analysis_router", "statistics_router"]
