"""SEO analysis schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class SeoIssue(BaseModel):
    """Single SEO issue entry with severity and suggestion."""

    key: str
    severity: str
    message: str
    suggestion: str


class SeoAnalysisResult(BaseModel):
    """Normalized SEO checks for one website."""

    source_url: HttpUrl
    final_url: HttpUrl
    title: str | None = None
    description: str | None = None
    h1: list[str] = Field(default_factory=list)
    h2: list[str] = Field(default_factory=list)
    canonical: HttpUrl | None = None
    robots_meta: str | None = None
    sitemap_url: HttpUrl | None = None
    structured_data_types: list[str] = Field(default_factory=list)
    broken_links: list[HttpUrl] = Field(default_factory=list)
    missing_alt_images: int = 0
    open_graph_tags: dict[str, str] = Field(default_factory=dict)
    twitter_card_tags: dict[str, str] = Field(default_factory=dict)
    page_speed_note: str = "Local simplified check: full page speed requires external API integration."
    score: int = 0
    issues: list[SeoIssue] = Field(default_factory=list)
