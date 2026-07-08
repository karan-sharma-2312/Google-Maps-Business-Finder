"""Service layer for Google Maps business discovery."""

from __future__ import annotations

import json
from pathlib import Path

from app.config import Settings
from app.core import get_logger
from app.schemas.business import BusinessSearchResult
from app.scrapers.google_maps.scraper import GoogleMapsQuery, GoogleMapsScraper


class GoogleMapsDiscoveryService:
    """Orchestrates Google Maps scraping and output persistence."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = get_logger({"component": "google-maps-service"})
        self._scraper = GoogleMapsScraper(settings.scraper)

    async def discover(
        self,
        query: str,
        location: str | None,
        max_results: int,
    ) -> BusinessSearchResult:
        """Run business discovery workflow and return normalized results."""
        search_request = GoogleMapsQuery(query=query, location=location, max_results=max_results)

        businesses = await self._scraper.search_businesses(search_request)

        result = BusinessSearchResult(
            query=query,
            location=location,
            max_results=max_results,
            discovered_count=len(businesses),
            businesses=businesses,
        )

        self._logger.info(
            "Discovery complete query='{}' location='{}' discovered_count={}",
            query,
            location,
            result.discovered_count,
        )
        return result

    def save_json_report(self, result: BusinessSearchResult, output_file: Path) -> Path:
        """Persist search result payload as UTF-8 JSON file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        output_file.write_text(
            json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        self._logger.info("Discovery JSON report written to {}", output_file)
        return output_file
