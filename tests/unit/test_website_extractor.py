"""Unit tests for website extractor helpers."""

from app.config import ScraperSettings
from app.extractors.website_extractor import WebsiteExtractor


def _build_extractor() -> WebsiteExtractor:
    return WebsiteExtractor(ScraperSettings())


def test_detect_cms_wordpress() -> None:
    extractor = _build_extractor()
    assert extractor._detect_cms("<html><script src='/wp-content/theme.js'></script></html>") == "WordPress"


def test_detect_technologies() -> None:
    extractor = _build_extractor()
    html = "<html><script>window.__NEXT_DATA__={};</script><script src='jquery.js'></script></html>"
    technologies = extractor._detect_technologies(html)

    assert "Next.js" in technologies
    assert "jQuery" in technologies


def test_extract_meta_pixel_ids() -> None:
    extractor = _build_extractor()
    html = "<script>fbq('init', '123456789012345');</script>"
    assert extractor._extract_meta_pixel_ids(html) == ["123456789012345"]
