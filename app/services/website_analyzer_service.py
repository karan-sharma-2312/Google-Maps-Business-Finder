"""Service layer for website analysis."""

from __future__ import annotations

import json
from pathlib import Path

from app.config import Settings
from app.core import get_logger
from app.extractors.website_extractor import WebsiteExtractor
from app.schemas.website_analysis import WebsiteAnalysisResult


class WebsiteAnalyzerService:
    """Coordinates website extraction and report persistence."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = get_logger({"component": "website-analyzer-service"})
        self._extractor = WebsiteExtractor(settings.scraper)

    def analyze(self, website_url: str) -> WebsiteAnalysisResult:
        """Analyze one website and return normalized result payload."""
        self._logger.info("Analyzing website {}", website_url)
        result = self._extractor.analyze(website_url)
        self._logger.info(
            "Website analysis complete url={} emails={} phones={} socials={}",
            result.final_url,
            len(result.emails),
            len(result.phone_numbers),
            len(result.social_links.facebook)
            + len(result.social_links.instagram)
            + len(result.social_links.linkedin)
            + len(result.social_links.twitter_x)
            + len(result.social_links.youtube),
        )
        return result

    def save_json_report(self, result: WebsiteAnalysisResult, output_file: Path) -> Path:
        """Persist website analysis output to JSON."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(
            json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        self._logger.info("Website analysis report written to {}", output_file)
        return output_file
