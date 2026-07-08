"""Business discovery schemas.

These Pydantic models are the canonical data contracts for discovered businesses.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field, HttpUrl


class Coordinates(BaseModel):
    """Latitude/longitude pair for a business location."""

    latitude: float | None = None
    longitude: float | None = None


class BusinessRecord(BaseModel):
    """Structured business information discovered from public sources."""

    business_name: str
    category: str | None = None
    rating: float | None = None
    reviews_count: int | None = None
    address: str | None = None
    phone: str | None = None
    website: HttpUrl | None = None
    google_maps_url: HttpUrl | None = None
    coordinates: Coordinates = Field(default_factory=Coordinates)
    opening_hours: list[str] = Field(default_factory=list)
    business_status: str | None = None
    business_description: str | None = None
    business_images: list[HttpUrl] = Field(default_factory=list)
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class BusinessSearchResult(BaseModel):
    """Container for one Google Maps search execution."""

    query: str
    location: str | None = None
    max_results: int
    discovered_count: int
    businesses: list[BusinessRecord] = Field(default_factory=list)
