"""Website analysis schemas for business enrichment."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class SocialLinks(BaseModel):
    """Detected social profile URLs."""

    facebook: list[HttpUrl] = Field(default_factory=list)
    instagram: list[HttpUrl] = Field(default_factory=list)
    linkedin: list[HttpUrl] = Field(default_factory=list)
    twitter_x: list[HttpUrl] = Field(default_factory=list)
    youtube: list[HttpUrl] = Field(default_factory=list)
    telegram: list[HttpUrl] = Field(default_factory=list)
    pinterest: list[HttpUrl] = Field(default_factory=list)


class WebsiteAnalysisResult(BaseModel):
    """Normalized website footprint for one business domain."""

    source_url: HttpUrl
    final_url: HttpUrl
    title: str | None = None
    description: str | None = None
    emails: list[str] = Field(default_factory=list)
    phone_numbers: list[str] = Field(default_factory=list)
    whatsapp_links: list[HttpUrl] = Field(default_factory=list)
    contact_page: HttpUrl | None = None
    social_links: SocialLinks = Field(default_factory=SocialLinks)
    logo_url: HttpUrl | None = None
    favicon_url: HttpUrl | None = None
    about_page: HttpUrl | None = None
    services_page: HttpUrl | None = None
    products_page: HttpUrl | None = None
    careers_page: HttpUrl | None = None
    blog_page: HttpUrl | None = None
    technologies: list[str] = Field(default_factory=list)
    cms: str | None = None
    hosting: str | None = None
    analytics_ids: list[str] = Field(default_factory=list)
    meta_pixel_ids: list[str] = Field(default_factory=list)
    schema_types: list[str] = Field(default_factory=list)
