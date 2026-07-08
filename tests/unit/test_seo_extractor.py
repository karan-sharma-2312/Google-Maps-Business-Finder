"""Unit tests for SEO extractor helper behavior."""

from app.config import ScraperSettings
from app.extractors.seo_extractor import SeoExtractor


def _extractor() -> SeoExtractor:
    return SeoExtractor(ScraperSettings())


def test_collect_meta_by_prefix() -> None:
    extractor = _extractor()
    html = """
    <html>
      <head>
        <meta property='og:title' content='Hello'>
        <meta property='og:description' content='World'>
      </head>
    </html>
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    tags = extractor._collect_meta_by_prefix(soup, "property", "og:")

    assert tags["og:title"] == "Hello"
    assert tags["og:description"] == "World"


def test_build_issues_for_empty_result() -> None:
    extractor = _extractor()
    from app.schemas.seo_analysis import SeoAnalysisResult

    result = SeoAnalysisResult(source_url="https://example.com", final_url="https://example.com")
    issues = extractor._build_issues(result)

    assert len(issues) >= 4
