"""API key authentication dependency."""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from app.config import get_settings


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Require API key when configured in environment."""
    settings = get_settings()
    configured = settings.security.api_key
    if configured is None:
        return

    expected = configured.get_secret_value()
    if not expected:
        return

    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
