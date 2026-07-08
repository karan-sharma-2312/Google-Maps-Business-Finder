"""Local API launcher.

This script starts the FastAPI application with Uvicorn using typed settings.
It is the simplest way to run the service during localhost development.
"""

from __future__ import annotations

import uvicorn

from app.config import get_settings


def main() -> None:
    """Run the FastAPI application with environment-driven runtime options."""
    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.environment.value == "development",
        log_level=settings.logging.level.lower(),
    )


if __name__ == "__main__":
    main()
