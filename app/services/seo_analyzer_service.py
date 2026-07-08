"""Service layer for SEO analysis."""

from __future__ import annotations

import json
from pathlib import Path

from app.config import Settings
from app.core import get_logger
from app.extractors.seo_extractor import SeoExtractor
from app.schemas.seo_analysis import SeoAnalysisResult


class SeoAnalyzerService:
    """Coordinates SEO extraction and report output."""

    def __init__(self, settings: Settings) -> None:
        self._logger = get_logger({"component": "seo-analyzer-service"})
        self._extractor = SeoExtractor(settings.scraper)

    def analyze(self, website_url: str) -> SeoAnalysisResult:
        """Analyze one website for on-page SEO quality."""
        self._logger.info("Starting SEO analysis for {}", website_url)
        result = self._extractor.analyze(website_url)
        self._logger.info("SEO analysis complete url={} score={}", result.final_url, result.score)
        return result

    def save_json_report(self, result: SeoAnalysisResult, output_file: Path) -> Path:
        """Persist SEO analysis output to JSON."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(
            json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        self._logger.info("SEO analysis report written to {}", output_file)
        return output_file
